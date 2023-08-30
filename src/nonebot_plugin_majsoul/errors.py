import asyncio

from httpx import HTTPError
from nonebot import logger
from ssttkkl_nonebot_utils.errors.error_handler import ErrorHandlers

error_handlers = ErrorHandlers()


@error_handlers.register(HTTPError)
def _(e):
    logger.exception(e)
    return "网络错误"


@error_handlers.register(asyncio.TimeoutError)
def _(e):
    logger.exception(e)
    return "查询超时"
