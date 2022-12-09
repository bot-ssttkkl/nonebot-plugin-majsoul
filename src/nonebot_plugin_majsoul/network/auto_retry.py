from functools import wraps
from typing import TypeVar, Callable

from httpx import HTTPError
from nonebot import logger
from typing_extensions import ParamSpec

T = TypeVar('T')
P = ParamSpec('P')


def auto_retry(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        err = None

        for i in range(10):
            try:
                return await func(*args, **kwargs)
            except HTTPError as e:
                logger.error(f"Retrying... {i + 1}/10")
                logger.exception(e)
                err = e
            except Exception as e:
                raise e

        raise err

    return wrapper
