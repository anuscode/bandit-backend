import abc
import asyncio

import cachetools
from prometheus_client import Counter

import clients.kafka
from loggers import logger
from observable import Observable


class Streamable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass


class KafkaStream(Streamable, abc.ABC):
    def __init__(self, updatable: Observable):
        super().__init__()
        self._updatable = updatable
        self.kafka_counter_metric = Counter(
            "kafka_messages_total",
            "Count of total kafka messages.",
        )
        self.cache = cachetools.TTLCache(maxsize=200000, ttl=600)

    def start(self):
        """Publishing 을 시작한다."""

        async def implementation():
            to_context = clients.kafka.to_context
            async for message in clients.kafka.stream():
                try:
                    message_type = message.get("type")
                    if message_type == "d":
                        enter_type = message.get("enter_type", "") or ""
                        if enter_type and "_list" not in enter_type:
                            continue

                    message_hash = (
                        message["user_id"] + message["article_id"] + message["type"]
                    )
                    if message_hash in self.cache:
                        continue

                    self.cache[message_hash] = True

                    context = to_context(message)
                    await self._updatable.publish(context)
                    self.kafka_counter_metric.inc()
                except Exception as e:
                    logger.error(e)

        asyncio.create_task(implementation())


__all__ = [
    "Streamable",
    "KafkaStream",
]
