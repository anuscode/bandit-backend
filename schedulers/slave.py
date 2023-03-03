from apscheduler.schedulers.asyncio import AsyncIOScheduler

import clients
from backends.grpc.servicers import SlaveBanditServicer
from configs import settings


def scheduler(
    slave_bandit_servicer: SlaveBanditServicer,
    seconds: int = 10,
):
    async def synchronization():
        # rank with explorable false
        response = await clients.grpc.bandit.rank(
            settings.master_grpc_address,
            settings.max_slave_cache_size,
            explorable=False,
        )
        slave_bandit_servicer._samples[False] = {
            x.item_id: x for x in response.predictions
        }

        # rank with explorable true
        response = await clients.grpc.bandit.rank(
            settings.master_grpc_address,
            settings.max_slave_cache_size,
            explorable=True,
        )
        slave_bandit_servicer._samples[True] = {
            x.item_id: x for x in response.predictions
        }

    asyncio_scheduler = AsyncIOScheduler()
    asyncio_scheduler.add_job(
        synchronization, "interval", id="synchronization", seconds=seconds
    )

    return asyncio_scheduler
