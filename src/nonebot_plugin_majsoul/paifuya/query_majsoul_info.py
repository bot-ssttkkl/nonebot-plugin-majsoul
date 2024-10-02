from asyncio import create_task, wait_for
from datetime import datetime, timezone
from io import StringIO
from typing import AbstractSet, Optional, Text

from httpx import HTTPStatusError
from nonebot import on_command
from nonebot.internal.adapter import Event
from nonebot_plugin_saa import MessageFactory
from ssttkkl_nonebot_utils.errors.errors import BadRequestError, QueryError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
from ssttkkl_nonebot_utils.nonebot import default_command_start

from nonebot_plugin_majsoul.config import conf
from .data.api import paifuya_api as api
from .data.models.player_num import PlayerNum
from .data.models.room_rank import all_four_player_room_rank, all_three_player_room_rank, RoomRank
from .mappers.player_extended_stats import map_player_extended_stats
from .mappers.player_stats import map_player_stats
from .mappers.room_rank import map_room_rank
from .parsers.limit_of_games import try_parse_limit_of_games
from .parsers.name import try_parse_name, get_name_in_unconsumed_args
from .parsers.room_rank import try_parse_room_rank
from .parsers.time_span import try_parse_time_span
from ..errors import error_handlers


def make_handler(player_num: PlayerNum):
    async def majsoul_info(event: Event):
        args = event.get_message().extract_plain_text().split()
        cmd, args = args[0], args[1:]

        unconsumed_args = []
        kwargs = {}

        for arg in args:
            if "room_rank" not in kwargs:
                room_rank = try_parse_room_rank(arg)
                if room_rank is not None:
                    if player_num == PlayerNum.four:
                        kwargs["room_rank"] = room_rank[0]
                    elif player_num == PlayerNum.three:
                        kwargs["room_rank"] = room_rank[1]
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

            if "nickname" not in kwargs:
                name = try_parse_name(arg)
                if name is not None:
                    kwargs["nickname"] = name
                    continue

            unconsumed_args.append(arg)

        if "nickname" not in kwargs:
            nickname = await get_name_in_unconsumed_args(unconsumed_args)

            if not nickname:
                raise BadRequestError("请输入雀魂账号")

            kwargs["nickname"] = nickname

        coro = handle_majsoul_info(player_num=player_num, **kwargs)
        if conf.majsoul_query_timeout:
            await wait_for(coro, timeout=conf.majsoul_query_timeout)
        else:
            await coro

    return majsoul_info


four_player_majsoul_info_matcher = on_command('雀魂信息', aliases={'雀魂查询'})
four_player_majsoul_info_matcher.__help_info__ = (f"{default_command_start}雀魂信息 <雀魂账号> "
                                                  f"[<房间类型>] [最近<数量>场] [最近<数量>{{天|周|个月|年}}]")
four_player_majsoul_info = make_handler(PlayerNum.four)
four_player_majsoul_info = with_handling_reaction()(four_player_majsoul_info)
four_player_majsoul_info = handle_error(error_handlers)(four_player_majsoul_info)
four_player_majsoul_info_matcher.append_handler(four_player_majsoul_info)

three_player_majsoul_info_matcher = on_command('雀魂三麻信息', aliases={'雀魂三麻查询'})
three_player_majsoul_info_matcher.__help_info__ = (f"{default_command_start}雀魂三麻信息 <雀魂账号> "
                                                   f"[<房间类型>] [最近<数量>场] [最近<数量>{{天|周|个月|年}}]")
three_player_majsoul_info = make_handler(PlayerNum.three)
three_player_majsoul_info = with_handling_reaction()(three_player_majsoul_info)
three_player_majsoul_info = handle_error(error_handlers)(three_player_majsoul_info)
three_player_majsoul_info_matcher.append_handler(three_player_majsoul_info)


async def handle_majsoul_info(nickname: str, player_num: PlayerNum, *,
                              room_rank: Optional[AbstractSet[RoomRank]] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None,
                              limit: Optional[int] = None):
    default_start_time = start_time is None
    default_end_time = end_time is None
    default_limit = limit is None

    if room_rank is None:
        if player_num == PlayerNum.four:
            room_rank = all_four_player_room_rank
        elif player_num == PlayerNum.three:
            room_rank = all_three_player_room_rank

    if start_time is None:
        start_time = datetime.fromisoformat("2010-01-01T00:00:00").astimezone(timezone.utc)

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    with StringIO() as sio:
        players = await api[player_num].search_player(nickname)
        if len(players) == 0:
            raise QueryError("没有查询到该角色在金之间以上的对局数据呢~")
        else:
            if len(players) > 1:
                sio.write("查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称。\n")

            sio.write(f"昵称：{players[0].nickname}\n\n")

            try:
                if limit is not None:
                    records = await api[player_num].player_records(
                        players[0].id,
                        start_time,
                        end_time,
                        room_rank,
                        limit=limit,
                        descending=True)
                    start_time = records[-1].start_time

                player_stats = create_task(api[player_num].player_stats(
                    players[0].id,
                    start_time,
                    end_time,
                    room_rank))
                player_extended_stats = create_task(api[player_num].player_extended_stats(
                    players[0].id,
                    start_time,
                    end_time,
                    room_rank))

                player_stats = await player_stats
                player_extended_stats = await player_extended_stats
            except HTTPStatusError as e:
                if e.response.status_code == 404:
                    player_stats = None
                else:
                    raise e

            room_rank_text = map_room_rank(room_rank)
            if player_stats is None:
                raise QueryError(f"没有查询到{room_rank_text}的对局数据呢~")
            else:
                map_player_stats(sio, player_stats, room_rank_text, player_num)
                sio.write('\n')
                map_player_extended_stats(sio, player_extended_stats, room_rank_text)

            sio.write("\nPS：本数据不包含金之间以下对局以及2019.11.29之前的对局")

            with StringIO() as url:
                if player_num == PlayerNum.four:
                    url.write(f"https://amae-koromo.sapk.ch/player/{players[0].id}/")
                else:
                    url.write(f"https://ikeda.sapk.ch/player/{players[0].id}/")
                url.write(".".join(map(lambda x: str(x.value), room_rank)))
                if not default_start_time:
                    url.write("/")
                    url.write(start_time.strftime("%Y-%m-%d"))
                if not default_end_time:
                    url.write("/")
                    url.write(end_time.strftime("%Y-%m-%d"))
                if not default_limit:
                    url.write(f"?limit={limit}")

                sio.write("\n")
                sio.write("更多信息：")
                sio.write(url.getvalue())

        msg = sio.getvalue()
        await MessageFactory(Text(msg)).send(reply=True)
