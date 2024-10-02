import sys
from asyncio import wait_for
from datetime import datetime, timezone
from io import BytesIO
from typing import Sequence, Optional, Text

import matplotlib.pyplot as plt
from httpx import HTTPStatusError
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from nonebot import on_command
from nonebot.internal.adapter import Event
from nonebot_plugin_saa import MessageFactory, Image
from ssttkkl_nonebot_utils.errors.errors import BadRequestError, QueryError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
from ssttkkl_nonebot_utils.nonebot import default_command_start

from nonebot_plugin_majsoul.config import conf
from .data.api import paifuya_api as api
from .data.models.game_record import GameRecord
from .data.models.player_info import PlayerInfo, PlayerLevel
from .data.models.player_num import PlayerNum
from .data.models.player_rank import PlayerMajorRank
from .data.models.room_rank import all_four_player_room_rank, all_three_player_room_rank, RoomRank
from .mappers.player_num import map_player_num
from .mappers.player_rank import map_player_rank
from .parsers.limit_of_games import try_parse_limit_of_games
from .parsers.name import get_name_in_unconsumed_args, try_parse_name
from .parsers.time_span import try_parse_time_span
from ..errors import error_handlers
from ..utils.my_executor import run_in_my_executor

if conf.majsoul_font:
    plt.rcParams['font.sans-serif'] = conf.majsoul_font
elif sys.platform == 'win32':
    plt.rcParams['font.sans-serif'] = "Microsoft YaHei"

if conf.majsoul_font_path:
    font_manager.fontManager.addfont(conf.majsoul_font_path)


def make_handler(player_num: PlayerNum):
    async def majsoul_pt_plot(event: Event):
        args = event.get_message().extract_plain_text().split()
        cmd, args = args[0], args[1:]

        unconsumed_args = []
        kwargs = {}

        for arg in args:
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

        coro = handle_majsoul_pt_plot(player_num=player_num, **kwargs)
        if conf.majsoul_query_timeout:
            await wait_for(coro, timeout=conf.majsoul_query_timeout)
        else:
            await coro

    return majsoul_pt_plot


four_player_majsoul_pt_plot_matcher = on_command("雀魂PT图", aliases={"雀魂PT推移图"})
four_player_majsoul_pt_plot_matcher.__help_info__ = (f"{default_command_start}雀魂PT图 <雀魂账号> "
                                                     f"[最近<数量>场] [最近<数量>{{天|周|个月|年}}]")
four_player_majsoul_pt_plot_records = make_handler(PlayerNum.four)
four_player_majsoul_pt_plot_records = with_handling_reaction()(four_player_majsoul_pt_plot_records)
four_player_majsoul_pt_plot_records = handle_error(error_handlers)(
    four_player_majsoul_pt_plot_records)
four_player_majsoul_pt_plot_matcher.append_handler(four_player_majsoul_pt_plot_records)

three_player_majsoul_pt_plot_matcher = on_command("雀魂三麻PT图", aliases={"雀魂三麻PT推移图"})
three_player_majsoul_pt_plot_matcher.__help_info__ = (f"{default_command_start}雀魂三麻PT图 <雀魂账号> "
                                                      f"[最近<数量>场] [最近<数量>{{天|周|个月|年}}]")
three_player_majsoul_pt_plot_records = make_handler(PlayerNum.three)
three_player_majsoul_pt_plot_records = with_handling_reaction()(three_player_majsoul_pt_plot_records)
three_player_majsoul_pt_plot_records = handle_error(error_handlers)(
    three_player_majsoul_pt_plot_records)
three_player_majsoul_pt_plot_matcher.append_handler(three_player_majsoul_pt_plot_records)

_color = {RoomRank.four_player_throne_south: 'r',
          RoomRank.four_player_throne_east: 'r',
          RoomRank.four_player_jade_south: 'g',
          RoomRank.four_player_jade_east: 'g',
          RoomRank.four_player_golden_south: 'y',
          RoomRank.four_player_golden_east: 'y',
          RoomRank.three_player_throne_south: 'r',
          RoomRank.three_player_throne_east: 'r',
          RoomRank.three_player_jade_south: 'g',
          RoomRank.three_player_jade_east: 'g',
          RoomRank.three_player_golden_south: 'y',
          RoomRank.three_player_golden_east: 'y'}


def draw(bio: BytesIO,
         player_num: PlayerNum,
         player: PlayerInfo,
         initial_level: PlayerLevel,
         records: Sequence[GameRecord]):
    fig: Figure = plt.figure(facecolor='w', figsize=(16, 10))
    ax: Axes = fig.add_subplot(1, 1, 1)

    pre_rank = max_rank = initial_level.id
    pre_pt = pt = initial_level.score + initial_level.delta
    base = pre_rank.max_pt // 2

    ax.text(3, 100, '\n'.join(map_player_rank(pre_rank)), fontsize=15)

    is_celestial = False

    for i, r in enumerate(records):
        for p in r.players:
            if p.id != player.id:
                continue

            rank = p.rank
            if max_rank is None or rank > max_rank:
                max_rank = rank

            if pre_rank != rank:
                ax.text(i + 3, 100, '\n'.join(map_player_rank(rank)), fontsize=15)
                ax.vlines(i, 0, max(rank.max_pt, pre_rank.max_pt if pre_rank else 0), color='k')

                base = rank.max_pt // 2
                pt = pre_pt = base

            if rank.major_rank == PlayerMajorRank.celestial:
                # 获取到的PT是魂珠*100（每20魂珠升一段），这里再缩放5倍
                pt += p.pt * 5
                is_celestial = True
            else:
                pt += p.pt

            ax.plot([i, i + 1], [pre_pt, pt], color='k', lw=1.5)
            ax.fill_between([i, i + 1], [pre_pt, pt], color=_color[r.room_rank], alpha=0.05)
            ax.plot([i, i + 1], [base, base], color='k', lw=1.5)
            ax.plot([i, i + 1], [base * 2, base * 2], color='k', lw=1.5)

            pre_rank, pre_pt = rank, pt

    ax.set_title(f'雀魂段位战PT推移图[{map_player_num(player_num)}]  '
                 f'@{player.nickname}'
                 f'（{records[0].start_time.strftime("%Y/%m/%d")}~{records[-1].start_time.strftime("%Y/%m/%d")}）',
                 fontsize=12, pad=5)
    ax.set_xlabel('对局数', fontsize=20)

    ax.set_ylabel('PT', fontsize=20)

    if not is_celestial:
        ax.set_yticks([i * 1000 for i in range(11)], labels=[i * 1000 for i in range(11)])
    else:
        ax.set_yticks([i * 1000 for i in range(11)], labels=[f'{i * 1000} 魂珠{float(i * 2)}' for i in range(11)])

    ax.set_xlim(0, len(records))
    ax.set_ylim(0, max_rank.max_pt + 100)

    fig.savefig(bio, format='png')


async def handle_majsoul_pt_plot(nickname: str, player_num: PlayerNum, *,
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None,
                                 limit: Optional[int] = None):
    if player_num == PlayerNum.four:
        room_rank = all_four_player_room_rank
    elif player_num == PlayerNum.three:
        room_rank = all_three_player_room_rank
    else:
        raise ValueError(f"invalid player_num: {player_num}")

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    players = await api[player_num].search_player(nickname)
    if len(players) == 0:
        raise QueryError("没有查询到该角色在金之间以上的对局数据呢~")

    player = players[0]

    msg = ""
    if len(players) > 1:
        msg += "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称。\n"
    msg += f"昵称：{player.nickname}\n"

    try:
        records = []

        api_start_time = datetime.fromisoformat("2010-01-01T00:00:00").astimezone(timezone.utc)
        async for r in api[player_num].player_records_stream(
                player.id, api_start_time, end_time, room_rank, descending=True):
            # 比limit多取一个，用于获取在此之前的段位及PT
            if limit is not None and len(records) > limit:
                break

            records.append(r)

            # 同样多取一个，用于获取在此之前的段位及PT
            if start_time is not None and r.start_time < start_time:
                limit = len(records) - 1
                break

        predecessor_record = None
        if limit:
            if len(records) > limit:
                predecessor_record = records[limit]
            records = records[:limit]

        records.reverse()

        if predecessor_record is not None:
            player_stats_at_start = await api[player_num].player_stats(
                player.id, predecessor_record.start_time, predecessor_record.end_time, room_rank)
            initial_level = player_stats_at_start.level
        else:
            initial_level = None
            for p in records[0].players:
                if p.id == player.id:
                    initial_level = PlayerLevel(id=p.rank, score=p.rank.max_pt // 2, delta=0)
                    break
    except HTTPStatusError as e:
        if e.response.status_code == 404:
            raise QueryError("没有查询到该角色在金之间以上的对局数据呢~")
        else:
            raise e

    if not records:
        await MessageFactory(
            Text(msg)
        ).send(reply=True)
    else:
        with BytesIO() as bio:
            await run_in_my_executor(draw, bio, player_num, player, initial_level, records)
            await MessageFactory(
                Image(bio)
            ).send()
