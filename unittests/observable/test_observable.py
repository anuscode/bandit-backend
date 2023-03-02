import pytest

from observable import Observable


@pytest.mark.asyncio
async def test_subscribe_and_publish():
    # Create an observable object
    observable = Observable()

    # Define a test function that will be used as a subscriber
    async def test_function(data: str) -> None:
        assert data == "hello"

    # Subscribe to the observable object
    observable.subscribe(test_function)

    # Publish some data to the observable object
    await observable.publish("hello")
    await observable.close()


@pytest.mark.asyncio
async def test_close():
    # Create an observable object
    observable = Observable()

    # Publish some data to the observable object
    await observable.publish("hello")

    # Close the observable object
    await observable.close()

    assert observable._queue.empty() is True
