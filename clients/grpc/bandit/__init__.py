"""The Python implementation of the GRPC Faizz client."""

from __future__ import print_function

import logging
from typing import List

from annotations import elapsed
from clients.configs import settings
from clients.grpc import shared
from protos import bandit_pb2, bandit_pb2_grpc

DEFAULT_ADDRESS = settings.bandit_slave_grpc_endpoint


@elapsed
async def rank(
    address: str = DEFAULT_ADDRESS,
    count: int = 1000,
    explorable: bool = False,
) -> bandit_pb2.RankResponse:
    logging.debug(f"Request grpc rank: {address}")

    request = bandit_pb2.RankRequest(
        count=count,
        explorable=explorable,
    )
    async with shared.channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.rank(request)
        logging.debug(f"Response grpc rank: {len(response.predictions)}")
        return response


@elapsed
async def get(
    address: str = DEFAULT_ADDRESS,
    item_id: str = None,
    explorable: bool = False,
) -> bandit_pb2.GetResponse:
    if item_id is None:
        raise ValueError("item_id is required")

    logging.debug(f"Request grpc get: {address}")

    request = bandit_pb2.GetRequest(
        item_id=item_id,
        explorable=explorable,
    )
    async with shared.channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.get(request)
        logging.debug(f"Response grpc get: {response.prediction}")
        return response


@elapsed
async def select(
    address: str = DEFAULT_ADDRESS,
    item_ids: List[str] = None,
    explorable: bool = False,
) -> bandit_pb2.SamplesResponse:
    if not item_ids:
        raise ValueError("item_ids is required")

    logging.debug(f"Request grpc select: {address}")

    request = bandit_pb2.SelectRequest(item_ids=item_ids, explorable=explorable)
    async with shared.channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.samples(request)
        logging.debug(f"Response grpc Sample: {len(response.predictions)}")
        return response


@elapsed
async def update(
    address: str = DEFAULT_ADDRESS,
    item_id: str = None,
    value: float = None,
) -> bandit_pb2.UpdateResponse:
    if item_id is None or value is None:
        raise ValueError("item_id and value are required")

    request = bandit_pb2.UpdateRequest(
        item_id=item_id,
        value=value,
    )
    async with shared.channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.update(request)
        return response


@elapsed
async def delete(
    address: str = DEFAULT_ADDRESS,
    item_id: str = None,
) -> bandit_pb2.DeleteResponse:
    if item_id is None:
        raise ValueError("item_id is required")

    request = bandit_pb2.DeleteRequest(item_id=item_id)
    async with shared.channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.delete(request)
        return response


if __name__ == "__main__":
    import asyncio

    async def main():
        response = await rank("bandit.slave.dev.trollsoft.io:443")
        print([x for x in response.predictions])

    asyncio.run(main())
