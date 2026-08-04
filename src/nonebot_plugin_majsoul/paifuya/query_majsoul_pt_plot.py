import sys
from datetime import datetime, timezone
from io import BytesIO
from typing import AbstractSet, Sequence, Optional

from httpx import HTTPError, HTTPStatusError
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from nonebot import logger, on_command
from nonebot.internal.adapter import Event
from nonebot_plugin_saa import MessageFactory, Text, Image
from ssttkkl_nonebot_utils.errors.errors import BadRequestError, QueryError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
from ssttkkl_nonebot_utils.nonebot import default_command_start

from .data.api import paifuya_api as api
from .data.models.game_record import GameRecord
from .data.models.player_info import PlayerInfo, PlayerLevel
from .data.models.player_num import PlayerNum
from .data.models.player_rank import PlayerMajorRank
from .data.models.room_rank import (
    all_four_player_room_rank,
    all_three_player_room_rank,
    RoomRank
)
from .mappers.player_num import map_player_num
from .mappers.player_rank import map_player_rank
from .parsers.limit_of_games import try_parse_limit_of_games
from .parsers.name import get_name_in_unconsumed_args, try_parse_name
from .parsers.time_span import try_parse_time_span
from ..ac import pt_plot_service
from ..config import conf
from ..errors import PaifuyaRateLimitError, error_handlers
from ..utils.my_executor import run_in_my_executor

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

PLUGIN_DIR = Path(__file__).parent
font_path = str(PLUGIN_DIR / "NotoSansCJK-Regular.otf")

# 注册字体
font_manager.fontManager.addfont(font_path)

# 获取字体真实名字
font_name = font_manager.FontProperties(fname=font_path).get_name()

# 强制全局使用
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

_FOUR_PLAYER_PT_COMMAND_NAMES = {
    "雀魂PT图",
    "雀魂PT推移图",
    "雀魂pt推移图",
    "雀魂pt图",
}
_THREE_PLAYER_PT_COMMAND_NAMES = {
    "雀魂三麻PT图",
    "雀魂三麻PT推移图",
    "雀魂三麻pt推移图",
    "雀魂三麻pt图",
}
MAX_PT_PLOT_GAMES = 500
PLAYER_RECORDS_BATCH_SIZE = 200


async def _try_authorized_pt_records(
        player_num: PlayerNum,
        player_id: int,
        start_time: datetime,
        end_time: datetime,
        room_rank: AbstractSet[RoomRank]
) -> Optional[list[GameRecord]]:
    api_key = conf.majsoul_paifuya_api_key.strip()
    if not api_key:
        return None

    try:
        records = await api[player_num].player_records(
            player_id,
            start_time,
            end_time,
            room_rank,
            limit=MAX_PT_PLOT_GAMES,
            descending=True,
            api_key=api_key,
        )
    except (HTTPError, PaifuyaRateLimitError) as e:
        logger.warning(
            "Paifuya API-key player_records failed for PT plot; "
            f"falling back to full pagination ({type(e).__name__}: {e})"
        )
        return None

    return records[:MAX_PT_PLOT_GAMES]


def _extract_command_args(plain_text: str, player_num: PlayerNum) -> list[str]:
    parts = plain_text.split()
    if not parts:
        return []

    command_token, args = parts[0], parts[1:]
    command_names = (
        _FOUR_PLAYER_PT_COMMAND_NAMES
        if player_num == PlayerNum.four
        else _THREE_PLAYER_PT_COMMAND_NAMES
    )
    folded_token = command_token.casefold()

    for command_name in sorted(command_names, key=len, reverse=True):
        command_index = folded_token.find(command_name.casefold())
        if command_index == -1:
            continue

        attached_arg = command_token[command_index + len(command_name):]
        if attached_arg:
            args.insert(0, attached_arg)
        break

    return args


def make_handler(player_num: PlayerNum):
    async def majsoul_pt_plot(event: Event):
        args = _extract_command_args(
            event.get_message().extract_plain_text(),
            player_num,
        )

        unconsumed_args = []
        kwargs = {}

        for arg in args:

            if "time_span" not in kwargs:
                time_span = try_parse_time_span(arg)
                if time_span is not None:
                    kwargs["start_time"], kwargs["end_time"] = time_span
                    continue

            # PT 图已取消总场数限制。继续识别旧的“最近 N 场”
            # 参数，但不把它误当成玩家昵称。
            if try_parse_limit_of_games(arg) is not None:
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

        await handle_majsoul_pt_plot(
            player_num=player_num,
            **kwargs
        )

    return majsoul_pt_plot


four_player_majsoul_pt_plot_matcher = on_command(
    "雀魂PT图",
    aliases=_FOUR_PLAYER_PT_COMMAND_NAMES - {"雀魂PT图"},
    block=True,
    priority=1
)

pt_plot_service.patch_matcher(
    four_player_majsoul_pt_plot_matcher
)

four_player_majsoul_pt_plot_matcher.__help_info__ = (
    f"{default_command_start}雀魂PT图 <雀魂账号> "
    f"[最近<数量>{{天|周|个月|年}}]"
)

four_player_majsoul_pt_plot_records = make_handler(PlayerNum.four)
four_player_majsoul_pt_plot_records = with_handling_reaction()(
    four_player_majsoul_pt_plot_records
)

four_player_majsoul_pt_plot_records = handle_error(error_handlers)(
    four_player_majsoul_pt_plot_records
)

four_player_majsoul_pt_plot_matcher.append_handler(
    four_player_majsoul_pt_plot_records
)


three_player_majsoul_pt_plot_matcher = on_command(
    "雀魂三麻PT图",
    aliases=_THREE_PLAYER_PT_COMMAND_NAMES - {"雀魂三麻PT图"},
    block=True,
    priority=1
)

pt_plot_service.patch_matcher(
    three_player_majsoul_pt_plot_matcher
)

three_player_majsoul_pt_plot_matcher.__help_info__ = (
    f"{default_command_start}雀魂三麻PT图 <雀魂账号> "
    f"[最近<数量>{{天|周|个月|年}}]"
)

three_player_majsoul_pt_plot_records = make_handler(PlayerNum.three)

three_player_majsoul_pt_plot_records = with_handling_reaction()(
    three_player_majsoul_pt_plot_records
)

three_player_majsoul_pt_plot_records = handle_error(error_handlers)(
    three_player_majsoul_pt_plot_records
)

three_player_majsoul_pt_plot_matcher.append_handler(
    three_player_majsoul_pt_plot_records
)


_color = {
    RoomRank.four_player_throne_south: 'r',
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
    RoomRank.three_player_golden_east: 'y'
}


def draw(
        bio: BytesIO,
        player_num: PlayerNum,
        player: PlayerInfo,
        initial_level: PlayerLevel,
        records: Sequence[GameRecord]
):
    fig: Figure = plt.figure(
        facecolor='w',
        figsize=(16, 10)
    )

    ax: Axes = fig.add_subplot(1, 1, 1)

    pre_rank = max_rank = initial_level.id
    pre_pt = pt = initial_level.score + initial_level.delta

    base = pre_rank.max_pt // 2

    ax.text(
        3,
        100,
        '\n'.join(map_player_rank(pre_rank)),
        fontsize=15
    )

    is_celestial = False

    for i, r in enumerate(records):

        for p in r.players:

            if p.id != player.id:
                continue

            rank = p.rank

            if max_rank is None or rank > max_rank:
                max_rank = rank

            if pre_rank != rank:
                ax.text(
                    i + 3,
                    100,
                    '\n'.join(map_player_rank(rank)),
                    fontsize=15
                )

                ax.vlines(
                    i,
                    0,
                    max(
                        rank.max_pt,
                        pre_rank.max_pt if pre_rank else 0
                    ),
                    color='k'
                )

                base = rank.max_pt // 2
                pt = pre_pt = base

            if rank.major_rank == PlayerMajorRank.celestial:
                pt += p.pt * 5
                is_celestial = True
            else:
                pt += p.pt

            ax.plot(
                [i, i + 1],
                [pre_pt, pt],
                color='k',
                lw=1.5
            )

            ax.fill_between(
                [i, i + 1],
                [pre_pt, pt],
                color=_color[r.room_rank],
                alpha=0.05
            )

            ax.plot(
                [i, i + 1],
                [base, base],
                color='k',
                lw=1.5
            )

            ax.plot(
                [i, i + 1],
                [base * 2, base * 2],
                color='k',
                lw=1.5
            )

            pre_rank, pre_pt = rank, pt

    ax.set_title(
        f'雀魂段位战PT推移图[{map_player_num(player_num)}]  '
        f'@{player.nickname}'
        f'（{records[0].start_time.strftime("%Y/%m/%d")}~'
        f'{records[-1].start_time.strftime("%Y/%m/%d")}）',
        fontsize=12,
        pad=5
    )

    ax.set_xlabel('对局数', fontsize=20)
    ax.set_ylabel('PT', fontsize=20)

    if not is_celestial:
        ax.set_yticks(
            [i * 1000 for i in range(11)],
            labels=[i * 1000 for i in range(11)]
        )
    else:
        ax.set_yticks(
            [i * 1000 for i in range(11)],
            labels=[
                f'{i * 1000} 魂珠{float(i * 2)}'
                for i in range(11)
            ]
        )

    ax.set_xlim(0, len(records))
    ax.set_ylim(0, max_rank.max_pt + 100)

    fig.savefig(
        bio,
        format='png'
    )

    plt.close(fig)


async def handle_majsoul_pt_plot(
        nickname: str,
        player_num: PlayerNum,
        *,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
):
    if player_num == PlayerNum.four:
        room_rank = all_four_player_room_rank

    elif player_num == PlayerNum.three:
        room_rank = all_three_player_room_rank

    else:
        raise ValueError(
            f"invalid player_num: {player_num}"
        )

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    players = await api[player_num].search_player(
        nickname
    )

    # 强制区分大小写 + 精确匹配
    players = [
        p for p in players
        if p.nickname == nickname
    ]

    if len(players) == 0:
        raise QueryError(
            "没有查询到该角色在金之间以上的对局数据呢~"
        )

    if start_time is None:
        api_start_time = datetime.fromisoformat(
            "2010-01-01T00:00:00"
        ).astimezone(timezone.utc)
    else:
        api_start_time = start_time

    sent_any = False

    for player in players:

        async def fetch_records():
            result = []
            async for r in api[player_num].player_records_stream(
                    player.id,
                    api_start_time,
                    end_time,
                    room_rank,
                    batch=PLAYER_RECORDS_BATCH_SIZE,
                    descending=True
            ):
                # The API returns newest records first. Keep consuming every
                # page, but retain only the newest records used for plotting.
                if len(result) < MAX_PT_PLOT_GAMES:
                    result.append(r)

            return result

        try:
            records = await _try_authorized_pt_records(
                player_num,
                player.id,
                api_start_time,
                end_time,
                room_rank,
            )

            if records is None:
                records = await fetch_records()

            records.reverse()

        except HTTPStatusError as e:

            if e.response.status_code != 404:
                raise e

            continue

        if not records:
            continue

        # 获取初始段位
        initial_level = None

        for p in records[0].players:

            if p.id == player.id:
                initial_level = PlayerLevel(
                    id=p.rank,
                    score=p.rank.max_pt // 2,
                    delta=0
                )

                break

        if initial_level is None:
            continue

        msg = (
            f"昵称：{player.nickname} "
            f"(id={player.id})\n"
            f"对局数：{len(records)}"
        )

        with BytesIO() as bio:

            await run_in_my_executor(
                draw,
                bio,
                player_num,
                player,
                initial_level,
                records
            )

            await MessageFactory([
                Text(msg),
                Image(bio.getvalue())
            ]).send()

        sent_any = True

    if not sent_any:
        raise QueryError(
            "所有同名账号均没有有效对局数据"
        )
