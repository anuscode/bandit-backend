import uuid

from clients.kafka import shared
from clients.configs import settings

DEFAULT_TOPIC = settings.trace_topic
DEFAULT_GROUP_ID = str(uuid.uuid4())


async def consume(topic: str = DEFAULT_TOPIC, group_id: str = DEFAULT_GROUP_ID):
    async for message in shared.consume(topic, group_id=group_id):
        yield message


async def produce(topic: str = DEFAULT_TOPIC, message: str = None):
    if not message:
        raise ValueError("Message is empty")
    await shared.produce(topic, message)
