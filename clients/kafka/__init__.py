import asyncio
import itertools
import ssl
import time
import uuid
from multiprocessing.pool import ThreadPool
from typing import List, Dict, Tuple, AsyncGenerator

from aiokafka import AIOKafkaConsumer
from confluent_kafka import TopicPartition
from confluent_kafka.avro import (
    AvroConsumer,
    CachedSchemaRegistryClient,
    MessageSerializer,
)

from annotations import elapsed
from configs import settings
from loggers import logger
from mab import Context

GROUP_ID = f"bandit-backend-{uuid.uuid4()}"

CONSUMER_CONFIG = {
    "bootstrap.servers": settings.bootstrap_server,
    "group.id": GROUP_ID,
    "auto.offset.reset": settings.auto_offset_reset,
    "security.protocol": settings.security_protocol,
    "sasl.mechanism": settings.sasl_mechanism,
    "sasl.username": settings.sasl_username,
    "sasl.password": settings.sasl_password,
}

AIO_KAFKA_CONSUMER_CONFIG = {
    "bootstrap_servers": settings.bootstrap_server,
    "group_id": GROUP_ID,
    "auto_offset_reset": settings.auto_offset_reset,
    "sasl_mechanism": settings.sasl_mechanism,
    "sasl_plain_username": settings.sasl_username,
    "sasl_plain_password": settings.sasl_password,
    "security_protocol": settings.security_protocol,
    "ssl_context": ssl.SSLContext(),
    "fetch_max_wait_ms": 3000000,
    "request_timeout_ms": 3000000 * 3 + 3,
}

SCHEMA_REGISTRY_CONFIG = {
    "url": "https://psrc-epkz2.ap-southeast-2.aws.confluent.cloud",
    "basic.auth.user.info": "MC5V6C3ETOUZIP3D:5oSYFD6/f7BRcn/h2bf3QPGsvDQ9E1vnWga7Hk7YdAjwckxP8dHHKPfbLfwz0Cjl",
    "basic.auth.credentials.source": "USER_INFO",
}

SCHEMA_REGISTRY_CLIENT = CachedSchemaRegistryClient(SCHEMA_REGISTRY_CONFIG)


def to_context(x: Dict) -> Context:
    item_id = x["article_id"]
    value = 1 if x["type"] == "d" else 0
    updated_at = x["determined_at"]
    return Context(item_id, value, updated_at)


def avro_consumer():
    consumer = AvroConsumer(
        config=CONSUMER_CONFIG,
        schema_registry=SCHEMA_REGISTRY_CLIENT,
    )
    return consumer


def create_consume_params() -> List[Tuple[TopicPartition, int]]:
    consumer = avro_consumer()
    cluster_metadata = consumer.list_topics()

    params = []
    for topic_metadata in cluster_metadata.topics.values():
        topic = topic_metadata.topic
        for partition in topic_metadata.partitions:
            tp = TopicPartition(topic, partition=partition)
            first_offset, last_offset = consumer.get_watermark_offsets(tp)
            delta = int((last_offset - first_offset) * settings.kafka_offset_prorated)
            tp.offset = last_offset - delta
            params.append((tp, last_offset))

    consumer.close()

    return params


def consume(topic_partition: TopicPartition, last_offset: int) -> List[Dict]:
    consumer = avro_consumer()
    consumer.assign([topic_partition])

    threshold = time.time() - settings.kafka_retrieve_ttl

    result = []
    while True:
        message = consumer.poll(1)

        if not message:
            continue

        value, offset = message.value(), message.offset()
        value["data"]["determined_at"] = value["event_time"]["timestamp"]["second"]

        if offset >= last_offset - 1:
            logger.info(offset)
            break

        if value["data"]["determined_at"] < threshold:
            continue

        result.append(value["data"])

    consumer.close()
    return result


@elapsed
def fetch() -> List[Context]:
    consume_params = create_consume_params()
    partition_number = len(consume_params)
    logger.info(f"Found {partition_number} topic partitions..")

    logger.info(f"Pulling {partition_number} topics using {partition_number} threads..")
    with ThreadPool(partition_number) as p:
        messages = p.starmap(consume, consume_params)
        messages = itertools.chain.from_iterable(messages)

    logger.info("Done with retrieving messages from kafka..")
    logger.info("Start to convert messages to contexts..")

    contexts = map(to_context, messages)
    contexts = sorted(contexts, key=lambda x: x.updated_at)

    logger.info(f"Done with converting: {len(contexts)} contexts found..")
    return contexts


async def stream() -> AsyncGenerator[Dict, None]:
    while True:
        logger.info("Start to stream messages from kafka..")
        consumer = AIOKafkaConsumer(*settings.topics, **AIO_KAFKA_CONSUMER_CONFIG)
        await consumer.start()

        try:
            avro_deserializer = MessageSerializer(SCHEMA_REGISTRY_CLIENT)
            async for message in consumer:
                decoded_message = avro_deserializer.decode_message(message.value)
                decoded_message["data"]["determined_at"] = decoded_message["event_time"][
                    "timestamp"
                ]["second"]

                user_property = decoded_message["user_property"]
                data = decoded_message["data"]
                data.update(user_property)

                logger.info(f"Received message: {data}")

                yield data
        except Exception as e:
            logger.error(e)
        finally:
            logger.error(f"Stopping consumer..")
            await consumer.stop()

            logger.error(f"Sleeping 10 seconds.. stream will begin again in 10 seconds..")
            await asyncio.sleep(10)
