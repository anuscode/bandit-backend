from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from caches import TTL
from observable import Observable


def scheduler(
    ttl: TTL,
    deletable: Observable[List[str]],
    seconds: int = 60 * 10,
):
    async def cleanup():
        expired_ids = ttl.expired()
        await deletable.publish(expired_ids)

    asyncio_scheduler = AsyncIOScheduler()
    asyncio_scheduler.add_job(cleanup, "interval", seconds=seconds)
    return asyncio_scheduler
