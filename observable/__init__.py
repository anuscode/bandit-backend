import asyncio
from enum import Enum
from typing import Callable, TypeVar, List, NoReturn, Generic

from loggers import logger

TERMINATE = Enum("TERMINATE", "0")

T = TypeVar("T")


class Observable(Generic[T]):
    def __init__(self, max_size: int = 10):
        self._callbacks: List[Callable[[T], NoReturn]] = []
        self._queue = asyncio.Queue(maxsize=max_size)
        logger.debug("Starting Observable.asyncio.queue..")
        asyncio.create_task(self._init())

    def subscribe(self, callback: Callable[[T], NoReturn]) -> NoReturn:
        self._callbacks.append(callback)

    async def publish(self, data: T) -> NoReturn:
        await self._queue.put(data)

    async def _init(self) -> NoReturn:
        while True:
            try:
                data = await self._queue.get()

                if data == TERMINATE:
                    break

                for subscriber in self._callbacks:
                    if asyncio.iscoroutinefunction(subscriber):
                        await subscriber(data)
                    else:
                        subscriber(data)

            except Exception as e:
                logger.error(e)
            finally:
                self._queue.task_done()

    async def close(self) -> NoReturn:
        logger.debug("Closing Observable.asyncio.queue..")
        await self._queue.put(TERMINATE)
        await self._queue.join()

    async def join(self) -> NoReturn:
        await self._queue.join()
