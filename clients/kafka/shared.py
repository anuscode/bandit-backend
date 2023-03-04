import uuid

from aiokafka import AIOKafkaConsumer
from aiokafka import AIOKafkaProducer

from clients.configs import settings

DEFAULT_BOOTSTRAP_SERVER = settings.bootstrap_server
DEFAULT_AUTO_OFFSET_RESET = settings.auto_offset_reset
DEFAULT_GROUP_ID = str(uuid.uuid4())

producer: AIOKafkaProducer


async def consume(
    topic: str,
    bootstrap_server: str = DEFAULT_BOOTSTRAP_SERVER,
    group_id: str = DEFAULT_GROUP_ID,
    auto_offset_reset: str = DEFAULT_AUTO_OFFSET_RESET,
):
    while True:
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_server,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
        )
        try:
            await consumer.start()
            async for message in consumer:
                yield message
        finally:
            await consumer.stop()


async def init_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=DEFAULT_BOOTSTRAP_SERVER)
    await producer.start()


async def stop_producer():
    await producer.stop()


async def produce(topic: str, message: str):
    await producer.send_and_wait(topic, message.encode())