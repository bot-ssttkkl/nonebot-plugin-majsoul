from functools import wraps
from typing import TypeVar, Callable, Optional, Awaitable, Any, Union, Type, Sequence

from nonebot import logger
from typing_extensions import ParamSpec

T = TypeVar('T')
P = ParamSpec('P')


def auto_retry(error: Union[Type[Exception], Sequence[Type[Exception]]],
               before_retry: Optional[Callable[[], Awaitable[Any]]] = None):
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            err = None

            for i in range(10):
                try:
                    return await func(*args, **kwargs)
                except error as e:
                    if before_retry:
                        try:
                            await before_retry()
                        except error as e2:
                            logger.opt(exception=e2).error(f"Error occurred when retrying {i + 1}/10")
                    logger.opt(exception=e).error(f"Retrying... {i + 1}/10")
                    err = e
                except Exception as e:
                    raise e

            raise err

        return wrapper

    return decorator
