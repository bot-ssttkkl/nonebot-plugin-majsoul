import re
from typing import Optional

from ssttkkl_nonebot_utils.errors.errors import BadRequestError
from ssttkkl_nonebot_utils.integer import decode_integer


def try_parse_limit_of_games(raw: str) -> Optional[int]:
    result = re.match(r"^最近(.*)场$$", raw)
    if result is not None:
        num = result.group(1)
        try:
            num = decode_integer(num)
        except ValueError:
            return None

        if num <= 0:
            raise BadRequestError("场数不合法")

        return num

    return None
