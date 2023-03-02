import functools
from typing import Tuple, Iterable, Any, List, Callable, TypeVar

import grpc
import numpy as np

from loggers import logger
from mab import ThompsonMultiArmedBandit, Context
from mab.thomson import Prediction
from protos import bandit_pb2, bandit_pb2_grpc

T = TypeVar("T")

DEFAULT_BETA_DIST = functools.partial(np.random.beta, 1, 1)


def to_proto_prediction(x: Prediction) -> bandit_pb2.Prediction:
    return bandit_pb2.Prediction(
        item_id=x[0],
        score=x[1],
        alpha=x[2],
        beta=x[3],
    )


def select(
    ids: List[str],
    tuples: Iterable[Tuple[str, T]],
    converter: Callable[[Tuple[str, T]], Any] = None,
    default: Callable[[], T] = None,
) -> List[Any]:
    dictionary = dict(tuples)
    default = default or (lambda: None)
    converter = converter or (lambda x: x)
    return [converter((id, dictionary.get(id, default()))) for id in ids]


class MasterBanditServicer(bandit_pb2_grpc.BanditServicer):
    def __init__(self, multi_armed_bandit: ThompsonMultiArmedBandit = None):
        self.multi_armed_bandit = multi_armed_bandit or ThompsonMultiArmedBandit()

    async def rank(
        self, request: bandit_pb2.RankRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.RankResponse:
        """List all predictions of the multi armed bandits."""

        count, explorable = request.count or 20, request.explorable
        predictions = self.multi_armed_bandit.pull(explorable=explorable)
        predictions = predictions[:count]
        predictions = map(to_proto_prediction, predictions)
        predictions = list(predictions)

        logger.debug(f"Found {len(predictions)} predictions..")

        response = bandit_pb2.RankResponse(
            success=True,
            predictions=predictions,
        )
        return response

    async def get(
        self, request: bandit_pb2.GetRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.GetResponse:
        explorable = request.explorable
        bandit = self.multi_armed_bandit.bandits.get(request.item_id, None)
        if bandit is None:
            return bandit_pb2.GetResponse(
                success=False,
                error=f"Item {request.item_id} not found.",
            )

        prediction = bandit.pull(explorable=explorable)
        return bandit_pb2.GetResponse(
            success=True,
            prediction=bandit_pb2.Prediction(
                item_id=prediction[0],
                score=prediction[1],
                alpha=prediction[2],
                beta=prediction[3],
            ),
        )

    async def samples(
        self, request: bandit_pb2.SamplesRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.SamplesResponse:
        item_ids, explorable = request.item_ids, request.explorable

        def default(item_id: str):
            return Prediction(item_id=item_id, score=DEFAULT_BETA_DIST(), alpha=0, beta=0)

        predictions = self.multi_armed_bandit.pull(explorable=explorable)
        predictions = map(lambda x: (x[0], x), predictions)
        predictions = dict(predictions)
        predictions = [predictions.get(x, default(x)) for x in request.item_ids]
        predictions = map(to_proto_prediction, predictions)
        predictions = list(predictions)

        response = bandit_pb2.SamplesResponse(
            success=True,
            predictions=predictions,
        )
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
        """Update the bandit with the new observation"""

        c = Context(
            item_id=request.item_id, value=request.value, updated_at=request.updated_at
        )
        self.multi_armed_bandit.update(c)

        response = bandit_pb2.UpdateResponse(success=True)
        return response

    async def delete(
        self, request: bandit_pb2.DeleteRequest, context: grpc.aio.ServicerContext
    ) -> bandit_pb2.DeleteResponse:
        """Delete the bandit"""

        deleted_bandits = self.multi_armed_bandit.delete(request.item_id)
        deleted_bandits = [x for x in deleted_bandits if x is not None]

        for bandit in deleted_bandits:
            del bandit.contexts

        success = True if deleted_bandits else False
        response = bandit_pb2.DeleteResponse(success=success)
        return response
