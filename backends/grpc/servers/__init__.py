from typing import List

import grpc
from grpc_health.v1 import _async as async_health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from loggers import logger
from protos import bandit_pb2_grpc
from protos.bandit_pb2_grpc import BanditServicer

_LISTEN_SERVICE_ADDR = "[::]:{0}"

_HEALTH_SERVICE_FULLNAME = health_pb2.DESCRIPTOR.services_by_name["Health"].full_name


async def build(
    bandit_servicer: BanditServicer,
    health_servicer: async_health.HealthServicer,
    interceptors: List[grpc.aio.ServerInterceptor],
    service_port: int = 50051,
) -> grpc.aio.Server:
    """Build a gRPC server with the given servicers and interceptors."""

    logger.info("Configuring BanditServicer into rpc servers..")

    server = grpc.aio.server(interceptors=interceptors, compression=grpc.Compression.Gzip)
    service_address = _LISTEN_SERVICE_ADDR.format(service_port)
    server.add_insecure_port(service_address)

    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    bandit_pb2_grpc.add_BanditServicer_to_server(bandit_servicer, server)

    return server
