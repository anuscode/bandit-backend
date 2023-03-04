import grpc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependency_injector.wiring import inject, Provide
from grpc_health.v1 import health_pb2
from grpc_health.v1._async import HealthServicer
from grpc_reflection.v1alpha import reflection
from prometheus_client import start_http_server

import clients.kafka
from caches import TTL
from configs import settings
from connectors import Connector
from container import Container
from loggers import logger
from mab import ThompsonMultiArmedBandit
from protos import bandit_pb2
from streamable import Streamable


@inject
async def master(
    master_server: grpc.aio.Server = Provide[Container.master_server],
    health_servicer: HealthServicer = Provide[Container.health_servicer],
    multi_armed_bandit: ThompsonMultiArmedBandit = Provide[Container.multi_armed_bandit],
    ttl: TTL = Provide[Container.ttl],
    item_stream: Streamable = Provide[Container.item_stream],
    trace_stream: Streamable = Provide[Container.trace_stream],
    _: Connector = Provide[Container.ttl_connector],
    __: Connector = Provide[Container.mab_connector],
    master_scheduler: AsyncIOScheduler = Provide[Container.master_scheduler],
) -> None:
    logger.info("Starting [MASTER] server..")

    logger.info("Initializing 'ttl' with retrieved contexts..")
    item_ids = multi_armed_bandit.bandits.keys()
    ttl.update(item_ids)

    service_names = (
        bandit_pb2.DESCRIPTOR.services_by_name["Bandit"].full_name,
        health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
        reflection.SERVICE_NAME,
    )
    for service_name in service_names:
        serving = health_pb2.HealthCheckResponse.SERVING
        await health_servicer.set(service_name, serving)

    logger.debug("Starting service on %s", "0.0.0.0:50051")

    item_stream.start()
    trace_stream.start()
    master_scheduler.start()

    await master_server.start()
    await master_server.wait_for_termination()

    master_scheduler.shutdown()


@inject
async def slave(
    slave_server: grpc.aio.Server = Provide[Container.slave_server],
    health_servicer: HealthServicer = Provide[Container.health_servicer],
    slave_scheduler: AsyncIOScheduler = Provide[Container.slave_scheduler],
) -> None:
    logger.info("Starting [SLAVE] server..")

    service_names = (
        bandit_pb2.DESCRIPTOR.services_by_name["Bandit"].full_name,
        health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
        reflection.SERVICE_NAME,
    )
    for service_name in service_names:
        serving = health_pb2.HealthCheckResponse.SERVING
        await health_servicer.set(service_name, serving)

    logger.debug("Starting service on %s", "0.0.0.0:50051")

    await slave_scheduler.get_job("synchronization").func()
    slave_scheduler.start()

    await slave_server.start()
    await slave_server.wait_for_termination()

    slave_scheduler.shutdown()


def prometheus():
    logger.info(f"Starting Prometheus HTTP server.. on {settings.metrics_port}")
    start_http_server(port=settings.metrics_port)
