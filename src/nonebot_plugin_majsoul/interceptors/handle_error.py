from functools import wraps
from typing import Type

from httpx import HTTPError
from nonebot import logger
from nonebot.exception import MatcherException, ActionFailed
from nonebot.internal.matcher import Matcher

from nonebot_plugin_majsoul.errors import BadRequestError


def handle_error(matcher: Type[Matcher], silently: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapped_func(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MatcherException as e:
                raise e
            except BadRequestError as e:
                if not silently:
                    await matcher.finish(e.message)
            except ActionFailed as e:
                # 避免当发送消息错误时再尝试发送
                logger.exception(e)
            except HTTPError as e:
                logger.exception(e)
                if not silently:
                    await matcher.finish(f"网络错误：{type(e)}{str(e)}")
            except Exception as e:
                logger.exception(e)
                if not silently:
                    await matcher.finish(f"内部错误：{type(e)}{str(e)}")

        return wrapped_func

    return decorator
