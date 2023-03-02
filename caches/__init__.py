import time
from collections.abc import Iterable
from typing import Optional, Union, Dict, List

from loggers import logger


class TTL:
    def __init__(self, default_ttl: float = 60 * 60 * 24 * 1):
        self._data: Dict[str, float] = {}
        self.default_ttl = default_ttl

    def get(self, key: str, default: float = None) -> Optional[float]:
        return self._data.get(key, default)

    def update(self, key_or_keys: Union[str, Iterable[str]], ttl: Optional[float] = None):
        if ttl is None:
            ttl = time.time() + (ttl or self.default_ttl)

        if isinstance(key_or_keys, str):
            self._data[key_or_keys] = ttl
            return

        if isinstance(key_or_keys, Iterable):
            for k in key_or_keys:
                self._data[k] = ttl
            return

        logger.warn(f"Invalid key_or_keys: {key_or_keys}")

    def delete(
        self, key_or_keys: Union[str, Iterable[str]]
    ) -> Union[Optional[float], List[float]]:
        if isinstance(key_or_keys, str):
            return self._data.pop(key_or_keys, None)

        if isinstance(key_or_keys, Iterable):
            getter = self._data.get
            deleted = [getter(k, None) for k in key_or_keys]
            self._data = {k: v for k, v in self._data.items() if k not in key_or_keys}
            return deleted

        logger.warn(f"Invalid key_or_keys: {key_or_keys}")

    def items(self):
        return self._data.items()

    def expired(self):
        current_timestamp = time.time()
        return [k for k, v in self._data.items() if v < current_timestamp]
