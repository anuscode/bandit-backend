import time

from caches import TTL


def test_ttl():
    ttl = TTL()

    # Test `update` method
    ttl.update("key1", 100)
    assert ttl.get("key1") == 100

    # Test `delete` method
    ttl.delete("key1")
    assert ttl.get("key1") is None

    # Test `expired` method
    ttl.update("key1", time.time() + 100)
    ttl.update("key2", time.time() - 100)
    expired_keys = ttl.expired()
    assert len(expired_keys) == 1
    assert expired_keys[0] == "key2"

    # Test `update` method with multiple keys
    keys = ["key1", "key2", "key3"]
    ttl.update(keys, 200)
    for key in keys:
        assert ttl.get(key) == 200

    # Test `delete` method with multiple keys
    deleted_keys = ttl.delete(keys)
    assert len(deleted_keys) == len(keys)
    for key in keys:
        assert ttl.get(key) is None

    # Test `items` method
    ttl.update("key1", 300)
    ttl.update("key2", 400)
    items = list(ttl.items())
    assert len(items) == 2
    assert items == [("key1", 300), ("key2", 400)]
