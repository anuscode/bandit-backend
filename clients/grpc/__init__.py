"""The Python implementation of the GRPC Faizz client."""

from __future__ import print_function

import logging
from typing import List

import grpc

import tools
from annotations import elapsed
from protos import bandit_pb2, bandit_pb2_grpc


def _channel(address: str) -> grpc.aio.Channel:
    host, port = address.split(":")
    if port == "443":
        certificate = tools.get_ssl_certificate(host)
        creds = grpc.ssl_channel_credentials(certificate)
        return grpc.aio.secure_channel(address, creds)
    else:
        return grpc.aio.insecure_channel(address)


@elapsed
async def rank(
    address: str,
    count: int = 1000,
    explorable: bool = False,
) -> bandit_pb2.RankResponse:
    logging.debug(f"Request grpc rank: {address}")

    request = bandit_pb2.RankRequest(
        count=count,
        explorable=explorable,
    )
    async with _channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.rank(request)
        logging.debug(f"Response grpc rank: {len(response.predictions)}")
        return response


@elapsed
async def get(
    address: str,
    item_id: str,
    explorable: bool = False,
) -> bandit_pb2.GetResponse:
    logging.debug(f"Request grpc get: {address}")

    request = bandit_pb2.GetRequest(
        item_id=item_id,
        explorable=explorable,
    )
    async with _channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.get(request)
        logging.debug(f"Response grpc get: {response.prediction}")
        return response


@elapsed
async def select(
    address: str,
    item_ids: List[str],
    explorable: bool = False,
) -> bandit_pb2.SamplesResponse:
    logging.debug(f"Request grpc select: {address}")

    request = bandit_pb2.SelectRequest(item_ids=item_ids, explorable=explorable)
    async with _channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.samples(request)
        logging.debug(f"Response grpc Sample: {len(response.predictions)}")
        return response


async def update(
    address: str,
    item_id: str,
    value: float,
) -> bandit_pb2.UpdateResponse:
    request = bandit_pb2.UpdateRequest(
        item_id=item_id,
        value=value,
    )
    async with _channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.update(request)
        return response


async def delete(
    address: str,
    item_id: str,
) -> bandit_pb2.DeleteResponse:
    request = bandit_pb2.DeleteRequest(item_id=item_id)
    async with _channel(address) as channel:
        stub = bandit_pb2_grpc.BanditStub(channel)
        response = await stub.delete(request)
        return response


if __name__ == "__main__":
    import asyncio

    async def main():
        response = await rank("bandit.slave.dev.trollsoft.io:443")
        print([x for x in response.predictions])

    asyncio.run(main())
