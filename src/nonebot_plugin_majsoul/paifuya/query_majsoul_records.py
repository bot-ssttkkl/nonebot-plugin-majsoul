from asyncio import wait_for
from datetime import datetime, timezone
from io import StringIO, BytesIO
from typing import Optional, AbstractSet, Sequence, Text, List

import matplotlib.pyplot as plt
from httpx import HTTPStatusError
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from nonebot import on_command
from nonebot.internal.adapter import Event
from nonebot.internal.matcher import current_bot
from nonebot_plugin_saa import MessageFactory, AggregatedMessageFactory, Image
from ssttkkl_nonebot_utils.errors.errors import BadRequestError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
from ssttkkl_nonebot_utils.nonebot import default_command_start

from nonebot_plugin_majsoul.config import conf
from .data.api import paifuya_api as api
from .data.models.game_record import GameRecord
from .data.models.player_num import PlayerNum
from .data.models.room_rank import RoomRank, all_four_player_room_rank, all_three_player_room_rank
from .mappers.game_record import map_game_record
from .mappers.room_rank import map_room_rank
from .parsers.name import try_parse_name, get_name_in_unconsumed_args
from .parsers.room_rank import try_parse_room_rank
from ..errors import error_handlers
from ..utils.my_executor import run_in_my_executor
from ..utils.rank import ranked


def make_handler(player_num: PlayerNum):
    async def majsoul_records(event: Event):
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

        coro = handle_majsoul_records(player_num=player_num, **kwargs)
        if conf.majsoul_query_timeout:
            await wait_for(coro, timeout=conf.majsoul_query_timeout)
        else:
            await coro

    return majsoul_records


four_player_majsoul_records_matcher = on_command("雀魂最近对局", aliases={'雀魂对局', '雀魂牌谱'})
four_player_majsoul_records_matcher.__help_info__ = f"{default_command_start}雀魂最近对局 <雀魂账号> [<房间类型>]"
four_player_majsoul_records = make_handler(PlayerNum.four)
four_player_majsoul_records = with_handling_reaction()(four_player_majsoul_records)
four_player_majsoul_records = handle_error(error_handlers)(four_player_majsoul_records)
four_player_majsoul_records_matcher.append_handler(four_player_majsoul_records)

three_player_majsoul_records_matcher = on_command("雀魂三麻最近对局", aliases={'雀魂三麻对局', '雀魂三麻牌谱'})
three_player_majsoul_records_matcher.__help_info__ = f"{default_command_start}雀魂三麻最近对局 <雀魂账号> [<房间类型>]"
three_player_majsoul_records = make_handler(PlayerNum.three)
three_player_majsoul_records = with_handling_reaction()(three_player_majsoul_records)
three_player_majsoul_records = handle_error(error_handlers)(three_player_majsoul_records)
three_player_majsoul_records_matcher.append_handler(three_player_majsoul_records)


def draw_records_plot(bio: BytesIO, records: Sequence[GameRecord], player_id: int):
    fig: Figure = plt.figure(facecolor='w', figsize=(12, 2))
    ax: Axes = fig.add_subplot(1, 1, 1)

    rank = []
    for r in records:
        for i, p in ranked(r.players, key=lambda x: x.pt, reverse=True):
            if p.id != player_id:
                continue

            rank.append(i)
    rank.reverse()
    ax.plot(range(1, len(records) + 1), rank, marker='o')

    # 设置X轴与Y轴范围
    ax.set_yticks([1, 2, 3, 4], labels=[1, 2, 3, 4])
    ax.set_xlim(0.5, len(records) + 0.5)
    ax.set_ylim(0.75, 4.25)

    # 反转Y轴
    ax.invert_yaxis()

    # 移除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # 显示网格
    ax.grid(axis='y')

    # 隐藏X轴
    ax.get_xaxis().set_visible(False)

    fig.savefig(bio, format='png')


async def handle_majsoul_records(nickname: str, player_num: PlayerNum, *,
                                 room_rank: Optional[AbstractSet[RoomRank]] = None):
    if room_rank is None:
        if player_num == PlayerNum.four:
            room_rank = all_four_player_room_rank
        elif player_num == PlayerNum.three:
            room_rank = all_three_player_room_rank

    start_time = datetime.fromisoformat("2010-01-01T00:00:00")
    end_time = datetime.now(timezone.utc)

    msgs: List[MessageFactory] = []

    players = await api[player_num].search_player(nickname)
    if len(players) == 0:
        msgs.append(MessageFactory(Text("没有查询到该角色在金之间以上的对局数据呢~")))
    else:
        try:
            records = await api[player_num].player_records(
                players[0].id,
                start_time,
                end_time,
                room_rank,
                limit=10,
                descending=True)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                records = None
            else:
                raise e

        msg = ""
        if len(players) > 1:
            msg += "查询到多条角色昵称呢~，若输出不是您想查找的昵称，请补全查询昵称。\n"
        msg += f"昵称：{players[0].nickname}"

        room_rank_text = map_room_rank(room_rank)
        if not records:
            msg += f"\n\n没有查询到{room_rank_text}的对局数据呢~"

        msgs.append(MessageFactory(Text(msg.strip())))

        if records:
            with BytesIO() as bio:
                await run_in_my_executor(draw_records_plot, bio, records, players[0].id)
                msgs.append(MessageFactory(Image(bio.getvalue())))

            for i, r in enumerate(records):
                with StringIO() as sio:
                    map_game_record(sio, r, players[0].id)
                    msgs.append(MessageFactory(Text(sio.getvalue().strip())))

            with StringIO() as url:
                if player_num == PlayerNum.four:
                    url.write(f"https://amae-koromo.sapk.ch/player/{players[0].id}/")
                else:
                    url.write(f"https://ikeda.sapk.ch/player/{players[0].id}/")
                url.write(".".join(map(lambda x: str(x.value), room_rank)))

                msgs.append(MessageFactory(Text(f"更多信息：{url.getvalue()}")))

    if len(msgs) == 1:
        await msgs[0].send(reply=True)
    else:
        adapter_name = current_bot.get().adapter.get_name()

        if conf.majsoul_send_aggregated_message and adapter_name in AggregatedMessageFactory.sender:
            await AggregatedMessageFactory(msgs).send()
        else:
            for msg in msgs:
                await msg.send(reply=True)
