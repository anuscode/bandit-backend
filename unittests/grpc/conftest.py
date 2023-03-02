import itertools
from typing import List

import grpc
import numpy as np
import pytest
import pytest_asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from grpc import aio
from grpc_health.v1 import health_pb2_grpc
from grpc_health.v1._async import HealthServicer
from pytest_mock import MockerFixture

import clients
from backends.grpc.interceptors import RequestCounterInterceptor
from backends.grpc.interceptors import RequestLatencyInterceptor
from backends.grpc.interceptors import WelcomeInterceptor
from backends.grpc.interceptors.ttl import TTLInterceptor
from backends.grpc.servicers import MasterBanditServicer, SlaveBanditServicer
from container import Container
from loggers import logger
from observable import Observable
from protos import bandit_pb2_grpc, bandit_pb2
from unittests import fixtures


@pytest_asyncio.fixture(autouse=True)
def container() -> Container:
    c = Container()
    c.init_resources()
    return c


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def updatable(container: Container) -> Observable:
    o = container.updatable()
    yield o
    await o.close()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def deletable(container: Container) -> Observable:
    o = container.deletable()
    yield o
    await o.close()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def ttl_connector(container: Container) -> Observable:
    o = container.ttl_connector()
    yield o


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def mab_connector(container: Container) -> Observable:
    o = container.mab_connector()
    yield o


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def master_bandit_servicer(container: Container) -> MasterBanditServicer:
    return container.master_bandit_servicer()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def slave_bandit_servicer(container: Container) -> SlaveBanditServicer:
    return container.slave_bandit_servicer()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def health_servicer(container: Container) -> HealthServicer:
    return container.health_servicer()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def ttl_interceptor(container: Container) -> List[grpc.aio.ServerInterceptor]:
    return container.ttl_interceptor()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def welcome_interceptor(container: Container) -> List[grpc.aio.ServerInterceptor]:
    return container.welcome_interceptor()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def request_counter_interceptor(
    container: Container,
) -> List[grpc.aio.ServerInterceptor]:
    return container.request_counter_interceptor()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def request_latency_interceptor(
    container: Container,
) -> List[grpc.aio.ServerInterceptor]:
    return container.request_latency_interceptor()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def master_interceptors(container: Container) -> List[grpc.aio.ServerInterceptor]:
    return container.master_interceptors()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def slave_interceptors(container: Container) -> List[grpc.aio.ServerInterceptor]:
    return container.slave_interceptors()


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def master(
    mocker: MockerFixture,
    master_interceptors: List[grpc.aio.ServerInterceptor],
    master_bandit_servicer: MasterBanditServicer,
    health_servicer: health_pb2_grpc.HealthServicer,
) -> bandit_pb2_grpc.BanditStub:
    np.random.seed(0)

    server = aio.server(interceptors=list(master_interceptors))
    port = server.add_insecure_port("[::]:0")
    channel = aio.insecure_channel("localhost:%d" % port)
    stub = bandit_pb2_grpc.BanditStub(channel)

    bandit_pb2_grpc.add_BanditServicer_to_server(master_bandit_servicer, server)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    await server.start()

    mocker.patch("time.time", return_value=1666180000)
    contexts = itertools.chain.from_iterable(fixtures.contexts)
    for c in contexts:
        request = bandit_pb2.UpdateRequest(
            item_id=c.item_id,
            value=c.value,
            updated_at=c.updated_at,
        )
        await stub.update(request)

    yield stub
    await server.stop(None)


@pytest.mark.asyncio
@pytest_asyncio.fixture(autouse=True)
async def slave(
    mocker: MockerFixture,
    master: bandit_pb2_grpc.BanditStub,
    slave_interceptors: List[grpc.aio.ServerInterceptor],
    slave_bandit_servicer: SlaveBanditServicer,
    health_servicer: health_pb2_grpc.HealthServicer,
) -> bandit_pb2_grpc.BanditStub:
    np.random.seed(0)

    server = aio.server(interceptors=list(slave_interceptors))
    port = server.add_insecure_port("[::]:0")
    channel = aio.insecure_channel("localhost:%d" % port)
    stub = bandit_pb2_grpc.BanditStub(channel)

    bandit_pb2_grpc.add_BanditServicer_to_server(slave_bandit_servicer, server)
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    # patch the stub for slave to master
    mocker.patch("protos.bandit_pb2_grpc.BanditStub", return_value=master)

    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

    async def synchronization():
        logger.debug("Updating predictions..")
        # total item_ids
        response = await clients.grpc.rank(
            "MOCK_MASTER_GRPC_ADDRESS:50051", 100000, explorable=False
        )
        slave_bandit_servicer._samples[False] = {
            x.item_id: x for x in response.predictions
        }

        # rank, explorable=True
        response = await clients.grpc.rank(
            "MOCK_MASTER_GRPC_ADDRESS:50051", 100000, explorable=True
        )
        slave_bandit_servicer._samples[True] = {
            x.item_id: x for x in response.predictions
        }

    async def start_schedule():
        scheduler.add_job(synchronization, "interval", seconds=2)
        scheduler.start()

    await synchronization()
    await start_schedule()

    await server.start()
    yield stub
    await server.stop(None)
