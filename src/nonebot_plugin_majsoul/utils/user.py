from nonebot.internal.matcher import current_bot, current_event
from nonebot_plugin_session import extract_session
from nonebot_plugin_user.params import get_user


async def get_uid() -> int:
    return (await get_user(extract_session(current_bot.get(), current_event.get()))).id
