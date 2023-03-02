"""Base class for servers-side interceptors."""

import grpc

from typing import Callable, Tuple, Awaitable

from grpc._utilities import RpcMethodHandler
from prometheus_client import Counter, Histogram


class Prometheus(object):
    requests_total = Counter(
        "grpc_requests_total",
        "Count of total requests.",
        ["method", "status"],
    )
    request_latency_seconds = Histogram(
        "grpc_request_duration_seconds",
        "Duration of HTTP requests in seconds.",
        ["method"],
    )


class RequestCounterInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ):
        rpc_method_handler = await continuation(handler_call_details)

        handler_factory, next_handler_method = _get_factory_and_method(rpc_method_handler)

        async def invoke_intercept_method(request, context):
            method = getattr(handler_call_details, "method")
            try:
                response = await next_handler_method(request, context)
                Prometheus.requests_total.labels(
                    method=method,
                    status=200,
                ).inc()
            except Exception as e:
                Prometheus.requests_total.labels(method=method, status=500).inc()
                raise e
            return response

        execute = handler_factory(
            invoke_intercept_method,
            request_deserializer=getattr(
                rpc_method_handler,
                "request_deserializer",
            ),
            response_serializer=getattr(
                rpc_method_handler,
                "response_serializer",
            ),
        )
        return execute


class RequestLatencyInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(
        self,
        continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ],
        handler_call_details: grpc.HandlerCallDetails,
    ):
        rpc_method_handler = await continuation(handler_call_details)

        handler_factory, next_handler_method = _get_factory_and_method(rpc_method_handler)

        async def invoke_intercept_method(request, context):
            method = getattr(handler_call_details, "method")
            with Prometheus.request_latency_seconds.labels(method=method).time():
                response = await next_handler_method(request, context)
            return response

        execute = handler_factory(
            invoke_intercept_method,
            request_deserializer=getattr(
                rpc_method_handler,
                "request_deserializer",
            ),
            response_serializer=getattr(
                rpc_method_handler,
                "response_serializer",
            ),
        )
        return execute


def _get_factory_and_method(
    rpc_handler: RpcMethodHandler,
) -> Tuple[Callable, Callable]:
    if rpc_handler.unary_unary:
        return grpc.unary_unary_rpc_method_handler, rpc_handler.unary_unary
    elif rpc_handler.unary_stream:
        return grpc.unary_stream_rpc_method_handler, rpc_handler.unary_stream
    elif rpc_handler.stream_unary:
        return grpc.stream_unary_rpc_method_handler, rpc_handler.stream_unary
    elif rpc_handler.stream_stream:
        return grpc.stream_stream_rpc_method_handler, rpc_handler.stream_stream
    else:  # pragma: no cover
        raise RuntimeError("RPC handler implementation does not exist")
