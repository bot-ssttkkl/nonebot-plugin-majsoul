import re
from datetime import datetime, timezone, timedelta
from monthdelta import monthdelta
from typing import Optional, Tuple

from nonebot_plugin_majsoul.errors import BadRequestError
from nonebot_plugin_majsoul.utils.decode_integer import decode_integer


def try_parse_time_span(raw: str) -> Optional[Tuple[datetime, datetime]]:
    result = re.match(r"^最近(.*)((天)|(周)|(个月)|(年))$", raw)
    if result is not None:
        num = result.group(1)
        try:
            num = decode_integer(num)
        except ValueError:
            return None

        if num <= 0:
            raise BadRequestError("时间不合法")

        end_time = datetime.now(timezone.utc)

        unit = result.group(2)
        if unit == '天':
            start_time = end_time - timedelta(days=num)
        elif unit == '周':
            start_time = end_time - timedelta(days=num * 7)
        elif unit == '个月':
            start_time = end_time - monthdelta(num)
        elif unit == '年':
            start_time = end_time - monthdelta(num * 12)
        else:
            return None

        return start_time, end_time

    return None
