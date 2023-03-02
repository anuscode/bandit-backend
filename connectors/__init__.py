import abc
import threading
from typing import NoReturn, TypeVar, List

import annotations
from caches import TTL
from loggers import logger
from mab import Context, ThompsonMultiArmedBandit
from observable import Observable

T1 = TypeVar("T1")
T2 = TypeVar("T2")

awaitable = annotations.awaitable(max_worker=1)


class Connector(abc.ABC):
    def update(self, data: T1) -> NoReturn:
        pass

    def delete(self, data: T2) -> NoReturn:
        pass


class MABConnector(Connector):
    def __init__(
        self, mab: ThompsonMultiArmedBandit, updatable: Observable, deletable: Observable
    ):
        self.mab = mab
        self.updatable = updatable
        self.deletable = deletable

        self.updatable.subscribe(callback=self.update)
        self.deletable.subscribe(callback=self.delete)

    @awaitable
    def update(self, context: Context) -> NoReturn:
        logger.info(f"MABConnector.Update, {threading.current_thread()}: {context}")
        self.mab.update(context)

    @awaitable
    def delete(self, item_ids: List[str]) -> NoReturn:
        logger.info(f"MABConnector.Update, {threading.current_thread()}: {item_ids}")
        self.mab.delete(item_ids)


class TTLConnector(Connector):
    def __init__(
        self, ttl: TTL, updatable: Observable[Context], deletable: Observable[List[str]]
    ):
        self.ttl = ttl
        self.updatable = updatable
        self.deletable = deletable

        self.updatable.subscribe(callback=self.update)
        self.deletable.subscribe(callback=self.delete)

    @awaitable
    def update(self, context: Context) -> NoReturn:
        logger.info(f"TTLConnector.Update, {threading.current_thread()}: {context}")
        self.ttl.update(context.item_id)

    @awaitable
    def delete(self, item_ids: List[str]) -> NoReturn:
        logger.info(f"TTLConnector.Delete, {threading.current_thread()}: {item_ids}")
        self.ttl.delete(item_ids)
