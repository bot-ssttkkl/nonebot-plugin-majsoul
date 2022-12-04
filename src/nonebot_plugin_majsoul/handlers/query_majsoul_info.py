from asyncio import create_task
from datetime import datetime, timezone
from io import StringIO
from typing import AbstractSet, Optional

from httpx import HTTPStatusError
from nonebot import on_command
from nonebot.internal.adapter import Event
from nonebot.internal.matcher import Matcher

from nonebot_plugin_majsoul.data.api import four_player_api, three_player_api
from nonebot_plugin_majsoul.data.models.player_num import PlayerNum
from nonebot_plugin_majsoul.data.models.room_rank import all_four_player_room_rank, all_three_player_room_rank, RoomRank
from nonebot_plugin_majsoul.mappers.player_stats import map_player_stats
from .interceptors.handle_error import handle_error
from ..errors import BadRequestError
from ..parsers.room_rank import try_parse_room_rank
from ..parsers.time_span import try_parse_time_span

query_majsoul_info_matcher = on_command('雀魂信息', aliases={'雀魂查询'})


@query_majsoul_info_matcher.handle()
@handle_error(query_majsoul_info_matcher)
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

    await handle_query_majsoul_info(matcher, nickname, **kwargs)


api = {
    PlayerNum.four: four_player_api,
    PlayerNum.three: three_player_api,
}


async def handle_query_majsoul_info(matcher: Matcher, nickname: str, *,
                                    four_men_room_rank: AbstractSet[RoomRank] = all_four_player_room_rank,
                                    three_men_room_rank: AbstractSet[RoomRank] = all_three_player_room_rank,
                                    start_time: Optional[datetime] = None,
                                    end_time: Optional[datetime] = None):
    if start_time is None:
        start_time = datetime.fromisoformat("2010-01-01T00:00:00")

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    with StringIO() as sio:
        players = await api[PlayerNum.four].search_player(nickname)
        if len(players) == 0:
            sio.write("没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(players) > 1:
                sio.write("查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称。\n")

            sio.write(f"昵称：{players[0].nickname}\n")

            args_by_game_men_num = []

            if len(four_men_room_rank):
                args_by_game_men_num.append((create_task(
                    api[PlayerNum.four].player_stats(
                        players[0].id,
                        start_time,
                        end_time,
                        four_men_room_rank
                    )
                ), four_men_room_rank, PlayerNum.four))
            else:
                args_by_game_men_num.append(None)

            if len(three_men_room_rank):
                args_by_game_men_num.append((create_task(
                    api[PlayerNum.three].player_stats(
                        players[0].id,
                        start_time,
                        end_time,
                        three_men_room_rank
                    )
                ), three_men_room_rank, PlayerNum.three))
            else:
                args_by_game_men_num.append(None)

            for args in args_by_game_men_num:
                if args is None:
                    continue

                player_stats, room_rank, game_men_num = args

                try:
                    player_stats = await player_stats
                except HTTPStatusError as e:
                    if e.response.status_code == 404:
                        player_stats = None
                    else:
                        raise e

                sio.write('\n')
                map_player_stats(sio, player_stats, room_rank, game_men_num)

            sio.write("\n")
            sio.write("PS：本数据不包含金之间以下对局以及2019.11.29之前的对局")

        await matcher.send(sio.getvalue())
