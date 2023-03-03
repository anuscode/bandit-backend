import asyncio

import numpy as np
import pytest
from pytest_mock import MockerFixture

from backends.grpc.interceptors.ttl import TTLInterceptor
from backends.grpc.servicers import MasterBanditServicer
from mab import Context
from observable import Observable
from protos import bandit_pb2
from protos import bandit_pb2_grpc


@pytest.mark.asyncio
async def test_master_bandit_stub_rank_with_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000 + 600)

    # When
    request = bandit_pb2.RankRequest(
        count=10,
        explorable=False,
    )
    response = await master.rank(request)

    # Then
    assert len(response.predictions) == 10
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
async def test_master_bandit_stub_rank_without_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
) -> None:
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000 + 600)

    # When
    request = bandit_pb2.RankRequest(
        count=10,
        explorable=True,
    )
    response = await master.rank(request)

    # Then
    assert len(response.predictions) == 10
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.70128924,
        alpha=4,
        beta=3,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_9",
        score=0.6799314,
        alpha=3,
        beta=1,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_8",
        score=0.5982641,
        alpha=2,
        beta=2,
    )
    assert response.predictions[3] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_1",
        score=0.53992087,
        alpha=1,
        beta=2,
    )


@pytest.mark.asyncio
async def test_master_bandit_stub_get_with_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
):
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000 + 600)

    # When
    request = bandit_pb2.GetRequest(
        item_id="test_thompson_bandits_2",
        explorable=False,
    )
    response = await master.get(request)

    # Then
    assert response.success
    assert response.prediction == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.7498241662979126,
        alpha=3,
        beta=2,
    )


@pytest.mark.asyncio
async def test_master_bandit_stub_get_without_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
):
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000 + 600)

    # When
    request = bandit_pb2.GetRequest(
        item_id="test_thompson_bandits_2",
        explorable=True,
    )
    response = await master.get(request)

    # Then
    assert response.success
    assert response.prediction == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.9165671467781067,
        alpha=3,
        beta=2,
    )


@pytest.mark.asyncio
async def test_master_bandit_stub_sample_without_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
):
    """explorable=False 이면 exploit 만 대상이 된다."""

    # Given
    np.random.seed(0)
    # '+ 600' 이 붙으므로 원래 explore 의 대상이지만 explorable 이 False 이므로 무시한다.
    mocker.patch("time.time", return_value=1666180000 + 600)

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
        ],
        explorable=False,
    )
    response = await master.samples(request)

    await asyncio.sleep(0.01)

    # Then
    assert len(response.predictions) == 3
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


@pytest.mark.asyncio
async def test_master_bandit_stub_sample_with_explorable(
    mocker: MockerFixture, master: bandit_pb2_grpc.BanditStub
):
    """explorable=True 이면 explore 가 포함 된다."""

    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=(1666180000 + 600))

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
        ],
        explorable=True,
    )
    response = await master.samples(request)

    await asyncio.sleep(0.01)

    # Then
    assert len(response.predictions) == 3
    assert response.predictions[0] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_2",
        score=0.48902976,
        alpha=2,
        beta=1,
    )
    assert response.predictions[1] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_7",
        score=0.70128924,
        alpha=4,
        beta=3,
    )
    assert response.predictions[2] == bandit_pb2.Prediction(
        item_id="test_thompson_bandits_6",
        score=0.53660476,
        alpha=2,
        beta=3,
    )


@pytest.mark.asyncio
async def test_master_bandit_stub_sample_with_invalid_ttl(
    mocker: MockerFixture,
    master: bandit_pb2_grpc.BanditStub,
    ttl_interceptor: TTLInterceptor,
):
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)
    ttl_interceptor.ttl.update("test_thompson_bandits_2", -1)

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
        ]
    )
    response = await master.samples(request)

    await asyncio.sleep(0.01)

    # Then
    assert len(response.predictions) == 3
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


@pytest.mark.asyncio
async def test_master_bandit_stub_sample_with_not_existing_id(
    mocker: MockerFixture,
    master: bandit_pb2_grpc.BanditStub,
    ttl_interceptor: TTLInterceptor,
):
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)
    ttl_interceptor.ttl.update("test_thompson_bandits_2", -1)

    # When
    request = bandit_pb2.SamplesRequest(
        item_ids=[
            "test_thompson_bandits_2",
            "test_thompson_bandits_7",
            "test_thompson_bandits_6",
            "test_thompson_bandits_NOT_EXISTING",
        ]
    )
    response = await master.samples(request)

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
        score=0.720552,
        alpha=0,
        beta=0,
    )


@pytest.mark.asyncio
async def test_master_bandit_stub_update(
    master: bandit_pb2_grpc.BanditStub,
    master_bandit_servicer: MasterBanditServicer,
):
    # Given
    np.random.seed(0)

    # When
    request = bandit_pb2.UpdateRequest(
        item_id="test_thompson_bandits_9999",
        value=1.0,
    )
    response = await master.update(request)

    # Then
    assert response.success
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits[
            "test_thompson_bandits_9999"
        ].alpha
        == 1.0
    )


@pytest.mark.asyncio
async def test_master_bandit_ttl_intercept(
    mocker: MockerFixture,
    master: bandit_pb2_grpc.BanditStub,
    master_bandit_servicer: MasterBanditServicer,
    ttl_interceptor: TTLInterceptor,
):
    # Given
    np.random.seed(0)
    mocker.patch("time.time", return_value=1666180000)

    # When
    request = bandit_pb2.UpdateRequest(
        item_id="test_thompson_bandits_9999",
        value=1.0,
    )
    assert ttl_interceptor.ttl.get("test_thompson_bandits_9999") is None
    response = await master.update(request)

    # Then
    assert response.success
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits[
            "test_thompson_bandits_9999"
        ].alpha
        == 1.0
    )
    ttl_to_verify = ttl_interceptor.ttl.get("test_thompson_bandits_9999")
    assert ttl_to_verify == 1666180000 + ttl_interceptor.ttl.default_ttl


@pytest.mark.asyncio
async def test_master_bandit_stub_delete(
    master: bandit_pb2_grpc.BanditStub,
    master_bandit_servicer: MasterBanditServicer,
):
    # Given
    np.random.seed(0)

    # When
    request = bandit_pb2.DeleteRequest(item_id="test_thompson_bandits_9999")
    response = await master.delete(request)

    # Then
    assert response.success is False
    assert (
        "test_thompson_bandits_9999"
        not in master_bandit_servicer.multi_armed_bandit.bandits
    )

    # When
    request = bandit_pb2.UpdateRequest(
        item_id="test_thompson_bandits_9999",
        value=1.0,
    )
    _ = await master.update(request)
    response = await master.delete(request)

    # Then
    assert response.success is True
    assert (
        "test_thompson_bandits_9999"
        not in master_bandit_servicer.multi_armed_bandit.bandits
    )


@pytest.mark.asyncio
async def test_deletable_publish_with_mab(
    master_bandit_servicer: MasterBanditServicer,
    deletable: Observable,
):
    # Given
    assert "test_thompson_bandits_1" in master_bandit_servicer.multi_armed_bandit.bandits

    # When
    await deletable.publish(["test_thompson_bandits_1"])
    await deletable.join()

    # Then
    assert (
        "test_thompson_bandits_1" not in master_bandit_servicer.multi_armed_bandit.bandits
    )


@pytest.mark.asyncio
async def test_deletable_publish_with_ttl(
    ttl_interceptor: TTLInterceptor,
    deletable: Observable,
):
    # Given
    assert ttl_interceptor.ttl.get("test_thompson_bandits_1") is not None

    # When
    await deletable.publish(["test_thompson_bandits_1"])
    await deletable.join()
    await asyncio.sleep(0.1)

    # Then
    assert ttl_interceptor.ttl.get("test_thompson_bandits_1") is None


@pytest.mark.asyncio
async def test_updatable_publish_with_mab(
    master_bandit_servicer: MasterBanditServicer,
    updatable: Observable,
):
    # Given
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits["test_thompson_bandits_1"].alpha
        == 1
    )
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits["test_thompson_bandits_1"].beta
        == 2
    )

    # When
    await updatable.publish(Context(item_id="test_thompson_bandits_1", value=1.0, updated_at=1666180000))
    await updatable.join()
    await asyncio.sleep(0.01)

    # Then
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits["test_thompson_bandits_1"].alpha
        == 2
    )
    assert (
        master_bandit_servicer.multi_armed_bandit.bandits["test_thompson_bandits_1"].beta
        == 1
    )


@pytest.mark.asyncio
async def test_updatable_publish_with_mab2(
    ttl_interceptor: TTLInterceptor,
    updatable: Observable,
):
    # Given
    assert ttl_interceptor.ttl.get("test_thompson_bandits_1") is not None

    # When
    await updatable.publish(
        Context(item_id="test_thompson_bandits_1", value=1.0, updated_at=1666180000 + 100)
    )
    await updatable.join()

    # Then
    assert ttl_interceptor.ttl.get("test_thompson_bandits_1") == 1668772000
