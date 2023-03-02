from typing import List

import numpy as np
import pytest
from pytest_mock import MockerFixture

from mab import ThompsonBandit, Context
from mab.thomson import Prediction, Observation


@pytest.fixture
def contexts() -> List[Context]:
    contexts = [
        Context(item_id="test_thompson_bandits", value=0, updated_at=1666184712),
        Context(item_id="test_thompson_bandits", value=1, updated_at=1666184713),
        Context(item_id="test_thompson_bandits", value=0, updated_at=1666184714),
        Context(item_id="test_thompson_bandits", value=0, updated_at=1666184715),
    ]
    return contexts


@pytest.fixture
def bandit(contexts: List[Context]) -> ThompsonBandit:
    _bandit = ThompsonBandit(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e",
        created_at=1666184711,
        contexts=contexts,
    )
    return _bandit


def test_thompson_bandit_create(bandit):
    assert bandit.item_id == "bf30e7dc-ba5a-4452-8cc4-7a567937af3e"
    assert bandit.created_at == 1666184711
    assert bandit.alpha == 1
    assert bandit.beta == 2
    assert bandit.total == 3


def test_thompson_bandit_explore(mocker: MockerFixture, bandit):
    mocker.patch("time.time", return_value=1666184715.75547 + 60 * 1)
    assert bandit.explore == 0.2
    assert bandit.exploit == 0.8

    mocker.patch("time.time", return_value=1666184715.75547 + 60 * 2)
    assert bandit.explore == 0.4
    assert bandit.exploit == 0.6

    mocker.patch("time.time", return_value=1666184715.75547 + 60 * 3)
    assert bandit.explore == 0.6
    assert bandit.exploit == 0.4

    mocker.patch("time.time", return_value=1666184715.75547 + 60 * 4)
    assert bandit.explore == 0.8
    assert round(bandit.exploit, 2) == 0.2

    mocker.patch("time.time", return_value=1666184715.75547 + 60 * 5)
    assert bandit.explore == 1.0
    assert bandit.exploit == 0.0


def test_thompson_bandit_pull(mocker: MockerFixture, bandit):
    mocker.patch("time.time", return_value=1666184716)
    np.random.seed(0)

    assert bandit.pull() == Prediction(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e",
        score=0.6035897484783911,
        alpha=2,
        beta=3,
    )


def test_thompson_bandit_update(mocker: MockerFixture, bandit):
    context = Context(
        item_id="test_thompson_bandits",
        value=1,
        updated_at=1666184712 + 60,
    )
    bandit.update(context)

    assert bandit.item_id == "bf30e7dc-ba5a-4452-8cc4-7a567937af3e"
    assert bandit.created_at == 1666184711
    assert bandit.alpha == 2
    assert bandit.beta == 1
    assert bandit.total == 3

    mocker.patch("time.time", return_value=context.updated_at)
    np.random.seed(0)
    assert bandit.explore == 0.0
    assert bandit.pull() == Prediction(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e",
        score=0.7498241925935014,
        alpha=bandit.alpha + 1,  # 2 + 1
        beta=bandit.beta + 1,  # 2 + 1
    )


def test_thompson_bandit_mean(contexts):
    bandit = ThompsonBandit(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e",
        created_at=1666184711,
        contexts=contexts,
    )
    assert bandit.alpha == 1
    assert bandit.beta == 2
    assert bandit.mean() == 0.3333333333333333

    bandit.update(
        Context(item_id="test_thompson_bandits", value=0, updated_at=1666184712)
    )
    assert bandit.alpha == 1
    assert bandit.beta == 3
    assert bandit.mean() == 0.25

    bandit.update(
        Context(item_id="test_thompson_bandits", value=1, updated_at=1666184713)
    )
    assert bandit.alpha == 2
    assert bandit.beta == 2
    assert bandit.mean() == 0.5


def test_thompson_bandit_observation(contexts):
    # Given
    np.random.seed(0)

    # When
    bandit = ThompsonBandit(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e",
        created_at=1666184711,
        contexts=contexts,
    )

    # Then
    assert bandit.observation() == Observation(
        item_id="bf30e7dc-ba5a-4452-8cc4-7a567937af3e", alpha=1, beta=2
    )
