from typing import List

from nonebot.adapters.onebot.v11 import Message, Bot, MessageEvent, GroupMessageEvent


async def send_group_forward_msg(bot: Bot, group_id: int, messages: List[Message]):
    self_info = await bot.get_login_info()

    msg_li = []

    for msg in messages:
        msg_li.append({
            "type": "node",
            "data": {
                "uin": bot.self_id,
                "name": self_info["nickname"],
                "content": msg
            }
        })

    await bot.send_group_forward_msg(group_id=group_id, messages=msg_li)


async def send_private_forward_msg(bot: Bot, user_id: int, messages: List[Message]):
    self_info = await bot.get_login_info()

    msg_li = []

    for msg in messages:
        msg_li.append({
            "type": "node",
            "data": {
                "uin": bot.self_id,
                "name": self_info["nickname"],
                "content": msg
            }
        })

    await bot.send_private_forward_msg(user_id=user_id, messages=msg_li)


async def send_forward_msg(bot: Bot, event: MessageEvent, messages: List[Message]):
    if isinstance(event, GroupMessageEvent):
        await send_group_forward_msg(bot, event.group_id, messages)
    else:
        await send_private_forward_msg(bot, event.user_id, messages)
