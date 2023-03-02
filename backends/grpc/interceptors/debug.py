"""Base class for server-side interceptors."""
import time
from typing import Callable, Tuple, Awaitable, List, Iterable

import grpc
from grpc._utilities import RpcMethodHandler

import clients
from protos import bandit_pb2


class DebugInterceptor(grpc.aio.ServerInterceptor):
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
            response = await next_handler_method(request, context)

            if method not in [
                "/grpc.bandit.v1.Bandit/select",
                "/grpc.bandit.v1.Bandit/samples",
                "/grpc.bandit.v1.Bandit/betas",
            ]:
                return response

            if not request.debug:
                return response

            if not request.user_id:
                return response

            clients.http.stack_debug_distribution(request.user_id, "ctr_sample", [])

            return response

        return handler_factory(
            invoke_intercept_method,
            request_deserializer=getattr(rpc_method_handler, "request_deserializer"),
            response_serializer=getattr(rpc_method_handler, "response_serializer"),
        )

    def to_zero_if_expired(
        self, prediction: bandit_pb2.Prediction, expired_ids: Iterable[str]
    ):
        if prediction.item_id in expired_ids:
            prediction.score = 0.0
        return prediction

    def list_expired_ids(self, predictions: List[bandit_pb2.Prediction]):
        now = time.time()
        return [x.item_id for x in predictions if self.ttl.get(x.item_id, 0) < now]


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
