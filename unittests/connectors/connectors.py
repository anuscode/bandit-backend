import pytest
from unittest.mock import MagicMock

from observable import Observable
from connectors import MABConnector
from mab import ThompsonMultiArmedBandit, Context


@pytest.mark.asyncio
async def test_update():
    # Create a mock ThompsonMultiArmedBandit object
    mab = MagicMock(ThompsonMultiArmedBandit)

    # Create a mock Observable object
    updatable = Observable()

    # Create a mock MABConnector object
    _ = MABConnector(mab, updatable, MagicMock(Observable))

    # Create a mock Context object
    context = Context(item_id="mock_item_id_1", value=1.0, updated_at=1666184715.75547)

    # Publish the mock Context object to the observable
    await updatable.publish(context)
    await updatable.join()

    # Check that the update method was called on the mock MAB object
    mab.update.assert_called_once_with(context)
    await updatable.close()


@pytest.mark.asyncio
async def test_delete():
    # Create a mock ThompsonMultiArmedBandit object
    mab = MagicMock(ThompsonMultiArmedBandit)

    # Create a mock Observable object
    deletable = Observable()

    # Create a mock MABConnector object
    _ = MABConnector(mab, MagicMock(Observable), deletable)

    # Publish a list of item IDs to the observable
    await deletable.publish(["item1", "item2"])
    await deletable.join()

    # Check that the delete method was called on the mock MAB object
    mab.delete.assert_called_once_with(["item1", "item2"])
    await deletable.close()
