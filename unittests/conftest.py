import logging.config
from typing import List

import pytest
import yaml

import directories
from mab import ThompsonBandit, Context, ThompsonMultiArmedBandit
from unittests import fixtures


@pytest.fixture(scope="session", autouse=True)
def setup_logging_configs(request):
    """Cleanup a testing directory once we are finished."""
    with open(directories.logging, "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
        logging.config.dictConfig(config)

    # request.addfinalizer(cleanup)


@pytest.fixture
def contexts() -> List[List[Context]]:
    return fixtures.contexts


@pytest.fixture
def bandits(contexts: List[List[Context]]) -> List[ThompsonBandit]:
    def to_bandit(context: List[Context]) -> ThompsonBandit:
        return ThompsonBandit(item_id=context[0].item_id, contexts=context)

    _bandits = map(to_bandit, contexts)
    _bandits = list(_bandits)
    return _bandits


@pytest.fixture
def multi_armed_bandit(bandits: List[ThompsonBandit]) -> ThompsonMultiArmedBandit:
    _multi_armed_bandit = ThompsonMultiArmedBandit(bandits=bandits)
    return _multi_armed_bandit
