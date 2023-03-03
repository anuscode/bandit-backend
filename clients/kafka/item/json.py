from clients.kafka import shared
from clients.configs import settings

DEFAULT_ITEM_TOPIC = settings.item_topic


async def consume(topic: str = DEFAULT_ITEM_TOPIC):
    async for message in shared.consume(topic):
        yield message
