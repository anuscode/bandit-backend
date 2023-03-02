import numpy as np
from pytest_mock import MockerFixture

from mab import Context
from mab import ThompsonMultiArmedBandit
from mab.thomson import Observation
from mab.thomson import Prediction


def test_multi_armed_bandit_create(multi_armed_bandit: ThompsonMultiArmedBandit):
    assert multi_armed_bandit.bandits["test_thompson_bandits_1"].alpha == 1
    assert multi_armed_bandit.bandits["test_thompson_bandits_1"].beta == 2

    assert multi_armed_bandit.bandits["test_thompson_bandits_2"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_2"].beta == 1

    assert multi_armed_bandit.bandits["test_thompson_bandits_3"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_3"].beta == 3

    assert multi_armed_bandit.bandits["test_thompson_bandits_4"].alpha == 0
    assert multi_armed_bandit.bandits["test_thompson_bandits_4"].beta == 5

    assert multi_armed_bandit.bandits["test_thompson_bandits_5"].alpha == 1
    assert multi_armed_bandit.bandits["test_thompson_bandits_5"].beta == 4

    assert multi_armed_bandit.bandits["test_thompson_bandits_6"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_6"].beta == 3

    assert multi_armed_bandit.bandits["test_thompson_bandits_7"].alpha == 4
    assert multi_armed_bandit.bandits["test_thompson_bandits_7"].beta == 3

    assert multi_armed_bandit.bandits["test_thompson_bandits_8"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_8"].beta == 2

    assert multi_armed_bandit.bandits["test_thompson_bandits_9"].alpha == 3
    assert multi_armed_bandit.bandits["test_thompson_bandits_9"].beta == 1

    assert multi_armed_bandit.bandits["test_thompson_bandits_10"].alpha == 1
    assert multi_armed_bandit.bandits["test_thompson_bandits_10"].beta == 4


def test_multi_armed_bandit_update(multi_armed_bandit: ThompsonMultiArmedBandit):
    context1 = Context(
        item_id="test_thompson_bandits_1", value=1, updated_at=1666180000 + 180
    )
    context2 = Context(
        item_id="test_thompson_bandits_5", value=1, updated_at=1666180000 + 180
    )
    context3 = Context(
        item_id="test_thompson_bandits_5", value=0, updated_at=1666180000 + 180
    )

    multi_armed_bandit.update(context1)
    assert multi_armed_bandit.bandits["test_thompson_bandits_1"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_1"].beta == 1

    multi_armed_bandit.update(context2)
    multi_armed_bandit.update(context3)
    assert multi_armed_bandit.bandits["test_thompson_bandits_5"].alpha == 2
    assert multi_armed_bandit.bandits["test_thompson_bandits_5"].beta == 4


def test_multi_armed_bandit_delete(multi_armed_bandit: ThompsonMultiArmedBandit):
    assert len(multi_armed_bandit.bandits) == 10

    deleted_bandits = multi_armed_bandit.delete("NOT_EXISTING_ID")
    assert deleted_bandits == [None]

    deleted_bandits = multi_armed_bandit.delete("test_thompson_bandits_1")
    assert len(deleted_bandits) == 1
    assert deleted_bandits[0].item_id == "test_thompson_bandits_1"
    assert deleted_bandits[0].alpha == 1
    assert deleted_bandits[0].beta == 2

    deleted_bandits = multi_armed_bandit.delete(
        ["test_thompson_bandits_2", "test_thompson_bandits_3"]
    )
    assert len(deleted_bandits) == 2
    assert deleted_bandits[0].item_id == "test_thompson_bandits_2"
    assert deleted_bandits[0].alpha == 2
    assert deleted_bandits[0].beta == 1
    assert deleted_bandits[1].item_id == "test_thompson_bandits_3"
    assert deleted_bandits[1].alpha == 2
    assert deleted_bandits[1].beta == 3


def test_multi_armed_bandit_pull(
    mocker: MockerFixture, multi_armed_bandit: ThompsonMultiArmedBandit
):
    # explores of bandits_3 and bandits_4 are not affected
    mocker.patch("time.time", return_value=1666180000 + 130)
    np.random.seed(0)

    predictions = multi_armed_bandit.pull()

    assert predictions == [
        Prediction(
            item_id="test_thompson_bandits_2", score=0.8256515349586602, alpha=2, beta=1
        ),
        Prediction(
            item_id="test_thompson_bandits_7", score=0.7963802474065867, alpha=4, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_6", score=0.7289961260182709, alpha=2, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_9", score=0.5995506617977753, alpha=3, beta=1
        ),
        Prediction(
            item_id="test_thompson_bandits_1", score=0.5908559698348175, alpha=1, beta=2
        ),
        Prediction(
            item_id="test_thompson_bandits_8", score=0.4606867469456969, alpha=2, beta=2
        ),
        Prediction(
            item_id="test_thompson_bandits_5", score=0.37138154319583183, alpha=1, beta=4
        ),
        Prediction(
            item_id="test_thompson_bandits_3", score=0.35676129423633407, alpha=2, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_10", score=0.1615247631082228, alpha=1, beta=4
        ),
        Prediction(
            item_id="test_thompson_bandits_4", score=0.10846861875944053, alpha=0, beta=5
        ),
    ]


def test_multi_armed_bandit_pull2(
    mocker: MockerFixture, multi_armed_bandit: ThompsonMultiArmedBandit
):
    """multi_armed_bandit explore test"""

    mocker.patch("time.time", return_value=1666184734 + 60 * 10)
    np.random.seed(0)

    predictions = multi_armed_bandit.pull()

    assert predictions == [
        Prediction(
            item_id="test_thompson_bandits_7", score=0.7012892439367917, alpha=4, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_9", score=0.679931428102942, alpha=3, beta=1
        ),
        Prediction(
            item_id="test_thompson_bandits_8", score=0.5982641104808608, alpha=2, beta=2
        ),
        Prediction(
            item_id="test_thompson_bandits_1", score=0.5399208552605227, alpha=1, beta=2
        ),
        Prediction(
            item_id="test_thompson_bandits_6", score=0.5366047537046931, alpha=2, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_5", score=0.489510502583612, alpha=1, beta=4
        ),
        Prediction(
            item_id="test_thompson_bandits_2", score=0.4890297625578933, alpha=2, beta=1
        ),
        Prediction(
            item_id="test_thompson_bandits_3", score=0.4696062480097461, alpha=2, beta=3
        ),
        Prediction(
            item_id="test_thompson_bandits_10", score=0.35652615980403785, alpha=1, beta=4
        ),
        Prediction(
            item_id="test_thompson_bandits_4", score=0.2953465232563696, alpha=0, beta=5
        ),
    ]


def test_multi_armed_bandit_means(
    mocker: MockerFixture, multi_armed_bandit: ThompsonMultiArmedBandit
):
    """multi_armed_bandit explore test"""

    mocker.patch("time.time", return_value=1666184734 + 60 * 10)
    np.random.seed(0)

    predictions = multi_armed_bandit.means()
    assert predictions == [
        ("test_thompson_bandits_1", 0.3333333333333333),
        ("test_thompson_bandits_2", 0.6666666666666666),
        ("test_thompson_bandits_3", 0.4),
        ("test_thompson_bandits_4", 0.0),
        ("test_thompson_bandits_5", 0.2),
        ("test_thompson_bandits_6", 0.4),
        ("test_thompson_bandits_7", 0.5714285714285714),
        ("test_thompson_bandits_8", 0.5),
        ("test_thompson_bandits_9", 0.75),
        ("test_thompson_bandits_10", 0.2),
    ]


def test_multi_armed_bandit_observations(
    mocker: MockerFixture, multi_armed_bandit: ThompsonMultiArmedBandit
):
    mocker.patch("time.time", return_value=1666184734 + 60 * 10)
    np.random.seed(0)

    observations = multi_armed_bandit.observations()
    assert observations == [
        Observation(item_id="test_thompson_bandits_1", alpha=1, beta=2),
        Observation(item_id="test_thompson_bandits_2", alpha=2, beta=1),
        Observation(item_id="test_thompson_bandits_3", alpha=2, beta=3),
        Observation(item_id="test_thompson_bandits_4", alpha=0, beta=5),
        Observation(item_id="test_thompson_bandits_5", alpha=1, beta=4),
        Observation(item_id="test_thompson_bandits_6", alpha=2, beta=3),
        Observation(item_id="test_thompson_bandits_7", alpha=4, beta=3),
        Observation(item_id="test_thompson_bandits_8", alpha=2, beta=2),
        Observation(item_id="test_thompson_bandits_9", alpha=3, beta=1),
        Observation(item_id="test_thompson_bandits_10", alpha=1, beta=4),
    ]
