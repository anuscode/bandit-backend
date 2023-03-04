from clients.kafka import shared
from clients.configs import settings

DEFAULT_TOPIC = settings.item_topic


async def consume(topic: str = DEFAULT_TOPIC):
    async for message in shared.consume(topic):
        yield message


async def produce(topic: str = DEFAULT_TOPIC, message: str = None):
    if not message:
        raise ValueError("Message is empty")
    await shared.produce(topic, message)
