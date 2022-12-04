from datetime import datetime, timezone
from io import StringIO
from typing import AbstractSet, Optional

from httpx import HTTPStatusError
from nonebot import on_command
from nonebot.internal.adapter import Event
from nonebot.internal.matcher import Matcher

from nonebot_plugin_majsoul.errors import BadRequestError
from nonebot_plugin_majsoul.interceptors.handle_error import handle_error
from .data.api import four_player_api, three_player_api
from .data.models.player_num import PlayerNum
from .data.models.room_rank import all_four_player_room_rank, all_three_player_room_rank, RoomRank
from .mappers.player_stats import map_player_stats
from .parsers.limit_of_games import try_parse_limit_of_games
from .parsers.room_rank import try_parse_room_rank
from .parsers.time_span import try_parse_time_span


def make_handler(player_num: PlayerNum):
    async def query_majsoul_info(matcher: Matcher, event: Event):
        args = event.get_message().extract_plain_text().split()[1:]

        nickname = args[0]
        if len(nickname) > 15:
            raise BadRequestError("昵称长度超过雀魂最大限制")

        kwargs = {}

        for arg in args:
            if "room_rank" not in kwargs:
                room_rank = try_parse_room_rank(arg)
                if room_rank is not None:
                    kwargs["room_rank"] = room_rank
                    continue

            if "time_span" not in kwargs:
                time_span = try_parse_time_span(arg)
                if time_span is not None:
                    kwargs["start_time"], kwargs["end_time"] = time_span
                    continue

            if "limit" not in kwargs:
                limit = try_parse_limit_of_games(arg)
                if limit is not None:
                    kwargs["limit"] = limit
                    continue

        await handle_query_majsoul_info(matcher, nickname, player_num, **kwargs)

    return query_majsoul_info


query_four_player_majsoul_info_matcher = on_command('雀魂信息', aliases={'雀魂查询'})
query_four_player_majsoul_info = make_handler(PlayerNum.four)
query_four_player_majsoul_info = handle_error(query_four_player_majsoul_info_matcher)(query_four_player_majsoul_info)
query_four_player_majsoul_info_matcher.append_handler(query_four_player_majsoul_info)

query_three_player_majsoul_info_matcher = on_command('雀魂三麻信息', aliases={'雀魂三麻查询'})
query_three_player_majsoul_info = make_handler(PlayerNum.three)
query_three_player_majsoul_info = handle_error(query_three_player_majsoul_info_matcher)(query_three_player_majsoul_info)
query_three_player_majsoul_info_matcher.append_handler(query_three_player_majsoul_info)

api = {
    PlayerNum.four: four_player_api,
    PlayerNum.three: three_player_api,
}


async def handle_query_majsoul_info(matcher: Matcher, nickname: str, player_num: PlayerNum, *,
                                    room_rank: Optional[AbstractSet[RoomRank]] = None,
                                    start_time: Optional[datetime] = None,
                                    end_time: Optional[datetime] = None,
                                    limit: Optional[int] = None):
    if room_rank is None:
        if player_num == PlayerNum.four:
            room_rank = all_four_player_room_rank
        elif player_num == PlayerNum.three:
            room_rank = all_three_player_room_rank

    if start_time is None:
        start_time = datetime.fromisoformat("2010-01-01T00:00:00")

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    with StringIO() as sio:
        players = await api[player_num].search_player(nickname)
        if len(players) == 0:
            sio.write("没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(players) > 1:
                sio.write("查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称。\n")

            sio.write(f"昵称：{players[0].nickname}\n\n")

            if limit is not None:
                records = await api[player_num].player_records(
                    players[0].id,
                    start_time,
                    end_time,
                    room_rank,
                    limit,
                    descending=True)
                start_time = datetime.fromtimestamp(records[-1]["startTime"], timezone.utc)

            try:
                player_stats = await api[player_num].player_stats(
                    players[0].id,
                    start_time,
                    end_time,
                    room_rank)
            except HTTPStatusError as e:
                if e.response.status_code == 404:
                    return None
                else:
                    raise e

            map_player_stats(sio, player_stats, room_rank, player_num)

            sio.write("\nPS：本数据不包含金之间以下对局以及2019.11.29之前的对局")

        await matcher.send(sio.getvalue())
