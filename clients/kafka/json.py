import uuid

from aiokafka import AIOKafkaConsumer

from clients.kafka.configs import settings


async def consume(
    topic: str,
    bootstrap_server: str = None,
    group_id: str = None,
    auto_offset_reset: str = "earliest",
):
    group_id = group_id or str(uuid.uuid4())
    bootstrap_server = bootstrap_server or settings.bootstrap_server

    while True:
        consumer = AIOKafkaConsumer(
            topic or settings.topic,
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
