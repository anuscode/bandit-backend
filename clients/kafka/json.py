import uuid

from aiokafka import AIOKafkaConsumer

from clients.configs import settings

DEFAULT_BOOTSTRAP_SERVER = settings.bootstrap_server
DEFAULT_TOPIC = settings.topic
DEFAULT_GROUP_ID = str(uuid.uuid4())


async def consume(
    topic: str,
    bootstrap_server: str = None,
    group_id: str = None,
    auto_offset_reset: str = "earliest",
):
    group_id = group_id or DEFAULT_GROUP_ID
    bootstrap_server = bootstrap_server or DEFAULT_BOOTSTRAP_SERVER
    topic = topic or DEFAULT_TOPIC,

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
