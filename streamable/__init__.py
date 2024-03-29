import abc
import asyncio
import json
import uuid
from typing import Dict

import cachetools
from prometheus_client import Counter

import clients
from loggers import logger
from mab import Context
from observable import Observable


class Streamable(abc.ABC):
    kafka_counter_metric = Counter(
        "kafka_messages_total", "Count of total kafka messages."
    )

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

    def start(self):
        """Publishing 을 시작한다."""

        async def implementation():
            def to_context(x: Dict) -> Context:
                item_id_ = x["item_id"]
                value = -1
                updated_at = x["created_ts"]
                return Context(item_id_, value, updated_at)

            async for message in clients.kafka.v1.json.consume(
                topic=clients.configs.settings.item_topic, group_id=str(uuid.uuid4())
            ):
                try:
                    message = message.value.decode("utf-8")
                    message = json.loads(message)
                    if message["event"] in ["update", "create"]:
                        context = to_context(message["item"])
                        await self._updatable.publish(context)
                    elif message["event"] in ["delete", "remove"]:
                        item_id = message["item_id"]
                        await self._deletable.publish([item_id])
                except Exception as e:
                    logger.error(e)
                finally:
                    self.kafka_counter_metric.inc()

        asyncio.create_task(implementation())


class TraceStream(Streamable, abc.ABC):
    def __init__(self, updatable: Observable):
        super().__init__()
        self._updatable = updatable
        self.cache = cachetools.TTLCache(maxsize=200000, ttl=600)

    def start(self):
        """Publishing 을 시작한다."""

        async def implementation():
            def to_context(x: Dict) -> Context:
                item_id_ = x["item_id"]
                value = 1 if x["exposed_by"] == "detail" else 0
                updated_at = x["created_ts"]
                return Context(item_id_, value, updated_at)

            async for message in clients.kafka.v1.json.consume(
                topic=clients.configs.settings.trace_topic, group_id=str(uuid.uuid4())
            ):
                try:
                    message = message.value.decode("utf-8")
                    message = json.loads(message)
                    message_hash = (
                        message["session_id"] + message["item_id"] + message["exposed_by"]
                    )
                    if message_hash in self.cache:
                        continue

                    self.cache[message_hash] = True

                    context = to_context(message)
                    await self._updatable.publish(context)
                except Exception as e:
                    logger.error(e)
                finally:
                    self.kafka_counter_metric.inc()

        asyncio.create_task(implementation())


__all__ = [
    "ItemStream",
    "TraceStream",
]
