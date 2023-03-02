import asyncio

import numpy as np
import pytest
from pytest_mock import MockerFixture

from protos import bandit_pb2
from protos import bandit_pb2_grpc


@pytest.mark.asyncio
async def test_slave_bandit_stub_rank_with_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)

    # When
    request = bandit_pb2.RankRequest(count=4, explorable=True)
    response = await slave.rank(request)

    # Then
    assert len(response.predictions) == 4
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_9",
        score=0.79497486,
        alpha=3,
        beta=1,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.68658155,
        alpha=4,
        beta=3,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_8",
        score=0.57779235,
        alpha=2,
        beta=2,
    )
    assert response.predictions[3] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.5378794,
        alpha=2,
        beta=1,
    )


@pytest.mark.asyncio
async def test_slave_bandit_stub_rank_without_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)

    # When
    request = bandit_pb2.RankRequest(count=4)
    response = await slave.rank(request)

    # Then
    assert len(response.predictions) == 4
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.90980697,
        alpha=2,
        beta=1,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.7963802,
        alpha=4,
        beta=3,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_6",
        score=0.7289961,
        alpha=2,
        beta=3,
    )
    assert response.predictions[3] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_1",
        score=0.6035898,
        alpha=1,
        beta=2,
    )


@pytest.mark.asyncio
async def test_slave_bandit_stub_get_with_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
    master: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    mocker.patch("time.time", return_value=1666180000)
    mocker.patch("protos.bandit_pb2_grpc.BanditStub", return_value=master)
    np.random.seed(0)

    # When
    request = bandit_pb2.GetRequest(
        item_id="test_thompson_bandits_2",
        explorable=False,
    )
    response = await slave.get(request)

    # Then
    assert response.success
    assert response.prediction == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.9098069667816162,
        alpha=2,
        beta=1,
    )


@pytest.mark.asyncio
async def test_slave_bandit_stub_get_without_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
    master: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    mocker.patch("time.time", return_value=1666180000)
    mocker.patch("protos.bandit_pb2_grpc.BanditStub", return_value=master)
    np.random.seed(0)

    # When
    request = bandit_pb2.GetRequest(
        item_id="test_thompson_bandits_2",
        explorable=True,
    )
    response = await slave.get(request)

    # Then
    assert response.success
    assert response.prediction == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.5378794,
        alpha=2,
        beta=1,
    )


@pytest.mark.asyncio
async def test_slave_bandit_stub_sample_with_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
            "test_thompson_bandits_NOT_EXISTING",
        ],
        explorable=True,
    )
    response = await slave.samples(request)
    # HACK: wait for the master ttl progress done.
    await asyncio.sleep(0.01)

    # Then
    assert len(response.predictions) == 4
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.5378794,
        alpha=2,
        beta=1,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.68658155,
        alpha=4,
        beta=3,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_6",
        score=0.4810935,
        alpha=2,
        beta=3,
    )
    assert response.predictions[3] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_NOT_EXISTING",
        score=0.44912526,
        alpha=0,
        beta=0,
    )


@pytest.mark.asyncio
async def test_slave_bandit_stub_sample_without_explorable_mode(
    mocker: MockerFixture,
    slave: bandit_pb2_grpc.BanditStub,
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
            "test_thompson_bandits_NOT_EXISTING",
        ],
        explorable=False,
    )
    response = await slave.samples(request)
    # HACK: wait for the master ttl progress done.
    await asyncio.sleep(0.01)

    # Then
    assert len(response.predictions) == 4
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.90980697,
        alpha=2,
        beta=1,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.7963802,
        alpha=4,
        beta=3,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_6",
        score=0.7289961,
        alpha=2,
        beta=3,
    )
    assert response.predictions[3] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_NOT_EXISTING",
        score=0.44912526,
        alpha=0,
        beta=0,
    )
