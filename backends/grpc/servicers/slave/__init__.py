import grpc
import numpy as np

import clients
from configs import settings
from protos import bandit_pb2
from protos import bandit_pb2_grpc


class SlaveBanditServicer(bandit_pb2_grpc.BanditServicer):
    def __init__(self):
        self._samples = {}

    async def rank(
        self, request: bandit_pb2.RankRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.RankResponse:
        """List all predictions of the multi armed bandits"""

        predictions = self._samples[request.explorable].values()
        predictions = list(predictions)
        predictions = predictions[: request.count]
        response = bandit_pb2.RankResponse(success=True, predictions=predictions)
        return response

    async def get(
        self, request: bandit_pb2.GetRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.GetResponse:
        prediction = self._samples[request.explorable].get(request.item_id, None)
        if not prediction:
            prediction = bandit_pb2.Prediction(
                item_id=request.item_id, score=np.random.beta(1, 1)
            )

        response = bandit_pb2.GetResponse(success=True, prediction=prediction)
        return response

    async def samples(
        self, request: bandit_pb2.SamplesRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.SamplesResponse:
        def to_prediction(item_id: str) -> bandit_pb2.Prediction:
            prediction = getter(item_id, None)
            prediction = prediction or bandit_pb2.Prediction(
                item_id=item_id,
                score=np.random.beta(1, 1),
                alpha=0,
                beta=0,
            )
            return prediction

        getter = self._samples[request.explorable].get
        predictions = map(to_prediction, request.item_ids)
        predictions = list(predictions)

        response = bandit_pb2.SamplesResponse(success=True, predictions=predictions)
        return response

    async def betas(
        self, request: bandit_pb2.BetasRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.BetasResponse:
        return await self.samples(request, context)

    async def select(
        self, request: bandit_pb2.SelectRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.SelectResponse:
        return await self.samples(request, context)

    async def update(
        self, request: bandit_pb2.UpdateRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.UpdateResponse:
        """Update the bandit with the new observation."""

        response = await clients.grpc.bandit.update(
            settings.bandit_master_grpc_endpoint,
            request.item_id,
            request.value,
        )
        return response

    async def delete(
        self, request: bandit_pb2.DeleteRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.DeleteResponse:
        """Delete the bandit."""

        response = await clients.grpc.bandit.delete(
            settings.bandit_master_grpc_endpoint,
            request.item_id,
        )
        return response
