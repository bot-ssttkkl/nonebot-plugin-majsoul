from typing import Optional

from ssttkkl_nonebot_utils.errors.errors import BadRequestError

from nonebot_plugin_majsoul.data.account_binding import AccountBinding
from nonebot_plugin_majsoul.utils.user import get_uid


def try_parse_name(raw: str) -> Optional[str]:
    if raw.startswith("id:") or raw.startswith("ID:"):
        return raw[len("id:"):]

    return None


async def get_name_in_unconsumed_args(unconsumed_args: list[str]) -> Optional[str]:
    if len(unconsumed_args) > 0 and unconsumed_args[0]:
        nickname = unconsumed_args[0]
        if len(nickname) > 15:
            raise BadRequestError("昵称长度超过雀魂最大限制")
    else:
        nickname = await AccountBinding.get(await get_uid())

    return nickname
