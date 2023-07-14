import asyncio
import concurrent.futures
import functools
import logging
import os
import time
from typing import Callable, Awaitable, Any

from prometheus_client import Histogram

logger = logging.getLogger(__name__)


function_duration_seconds = Histogram(
    "function_duration_seconds",
    "Duration of function execution in seconds.",
    ["function"],
)


def elapsed(f):
    """Decorator that logs the elapsed time and result of a function.

    Usage:
    @elapsed
    def my_func(arg1, arg2):
        ...

    Args:
        f: Function to be decorated.

    Returns:
        Decorated function that logs elapsed time and result.
    """

    @functools.wraps(f)
    def sync_wrapper(*args, **kwargs):
        with function_duration_seconds.labels(f.__name__).time():
            start = time.perf_counter()
            result = f(*args, **kwargs)
            end = time.perf_counter()
            elapsed_time = round(end - start, 2)

            log_msg = f"{f.__name__}: took {elapsed_time} sec"
            if isinstance(result, list):
                log_msg += f" with {len(result)} results."
            else:
                log_msg += "."
            logging.debug(log_msg)

            return result

    @functools.wraps(f)
    async def async_wrapper(*args, **kwargs):
        with function_duration_seconds.labels(f.__name__).time():
            start = time.perf_counter()
            result = await f(*args, **kwargs)
            end = time.perf_counter()
            elapsed_time = round(end - start, 2)

            log_msg = f"{f.__name__}: took {elapsed_time} sec"
            if isinstance(result, list):
                log_msg += f" with {len(result)} results."
            else:
                log_msg += "."
            logging.debug(log_msg)

            return result

    return async_wrapper if asyncio.iscoroutinefunction(f) else sync_wrapper


def awaitable(
    max_worker: int = 0,
    executor: concurrent.futures.ThreadPoolExecutor = None,
) -> Callable[..., Any]:
    if executor:
        thread_pool = executor
    elif max_worker:
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_worker)
    else:
        core_count = os.cpu_count()
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=core_count)

    def decorator(f) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> Awaitable:
            if asyncio.iscoroutinefunction(f):
                raise TypeError(
                    "async function is not allowed with a awaitable annotation."
                )

            loop = asyncio.get_running_loop()
            partial = functools.partial(f, *args, **kwargs)
            future = loop.run_in_executor(thread_pool, partial)
            return future

        return wrapper

    return decorator
