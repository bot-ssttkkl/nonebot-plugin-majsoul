from functools import wraps

from httpx import HTTPError
from nonebot import logger


def auto_retry(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
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
