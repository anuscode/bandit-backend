import abc
import asyncio
import json
from typing import Dict

import cachetools
from prometheus_client import Counter

import clients.kafka
from loggers import logger
from mab import Context
from observable import Observable


class Streamable(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def start(self):
        pass


class ItemStream(Streamable, abc.ABC):
    def __init__(self, updatable: Observable, deletable: Observable):
        super().__init__()
        self._updatable = updatable
        self._deletable = deletable
        self.kafka_counter_metric = Counter(
            "kafka_messages_total",
            "Count of total kafka messages.",
        )
        self.cache = cachetools.TTLCache(maxsize=200000, ttl=600)

    def start(self):
        """Publishing 을 시작한다."""

        async def implementation():

            def to_context(x: Dict) -> Context:
                item_id_ = x["item_id"]
                value = -1
                updated_at = x["created_ts"]
                return Context(item_id_, value, updated_at)

            async for message in clients.kafka.item.json.consume(topic="item.dev.v1"):
                try:
                    message = message.value.decode("utf-8")
                    message = json.loads(message)
                    if message["event"] in ["update", "create"]:
                        context = to_context(message["data"])
                        await self._updatable.publish(context)
                    elif message["event"] == "delete":
                        item_id = message["data"]["item_id"]
                        await self._deletable.publish([item_id])
                except Exception as e:
                    logger.error(e)
                finally:
                    self.kafka_counter_metric.inc()

        asyncio.create_task(implementation())


__all__ = [
    "Streamable",
    "ItemStream",
]
