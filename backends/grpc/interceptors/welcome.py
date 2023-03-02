import grpc

from typing import Callable, Awaitable

from loggers import logger


class WelcomeInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        method = getattr(handler_call_details, "method")
        handler = await continuation(handler_call_details)

        if "health" in method:
            return handler

        if "update" in method:
            return handler

        logger.debug(f"grpc: {method}")
        return handler
