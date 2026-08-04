from asyncio import create_task, wait_for
from datetime import datetime, timezone
from io import StringIO
from typing import AbstractSet, Optional, Text

from httpx import HTTPError, HTTPStatusError
from nonebot import logger, on_command
from nonebot.internal.adapter import Event
from nonebot_plugin_saa import MessageFactory
from ssttkkl_nonebot_utils.errors.errors import BadRequestError, QueryError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
from ssttkkl_nonebot_utils.nonebot import default_command_start

from .ai_comment import generate_ai_comment

from .data.api import paifuya_api as api
from .data.models.player_num import PlayerNum
from .data.models.room_rank import (
    all_four_player_room_rank,
    all_three_player_room_rank,
    RoomRank
)

from .mappers.player_extended_stats import map_player_extended_stats
from .mappers.player_stats import map_player_stats
from .mappers.room_rank import map_room_rank

from .parsers.limit_of_games import try_parse_limit_of_games
from .parsers.name import try_parse_name, get_name_in_unconsumed_args
from .parsers.room_rank import try_parse_room_rank
from .parsers.time_span import try_parse_time_span

from ..ac import query_info_service
from ..config import conf
from ..errors import PaifuyaRateLimitError, error_handlers


_FOUR_PLAYER_INFO_COMMAND_NAMES = {
    "雀魂信息",
    "雀魂查询",
}
_THREE_PLAYER_INFO_COMMAND_NAMES = {
    "雀魂三麻信息",
    "雀魂三麻查询",
}
_PLAYER_RECORDS_PAGE_SIZE = 500


async def _try_authorized_records_start_time(
        player_num: PlayerNum,
        player_id: int,
        start_time: datetime,
        end_time: datetime,
        room_rank: AbstractSet[RoomRank],
        limit: int
) -> Optional[datetime]:
    api_key = conf.majsoul_paifuya_api_key.strip()
    if not api_key:
        return None

    found = 0
    oldest_time = start_time
    try:
        async for record in api[player_num].player_records_stream(
                player_id,
                start_time,
                end_time,
                room_rank,
                batch=min(limit, _PLAYER_RECORDS_PAGE_SIZE),
                descending=True,
                api_key=api_key,
        ):
            found += 1
            oldest_time = record.start_time
            if found >= limit:
                break
    except (HTTPError, PaifuyaRateLimitError) as e:
        logger.warning(
            "Paifuya API-key player_records failed for info; "
            f"falling back to player_stats ({type(e).__name__}: {e})"
        )
        return None

    return oldest_time


def _extract_command_args(plain_text: str, player_num: PlayerNum) -> list[str]:
    parts = plain_text.split()
    if not parts:
        return []

    command_token, args = parts[0], parts[1:]
    command_names = (
        _FOUR_PLAYER_INFO_COMMAND_NAMES
        if player_num == PlayerNum.four
        else _THREE_PLAYER_INFO_COMMAND_NAMES
    )

    for command_name in sorted(command_names, key=len, reverse=True):
        command_index = command_token.find(command_name)
        if command_index == -1:
            continue

        attached_arg = command_token[command_index + len(command_name):]
        if attached_arg:
            args.insert(0, attached_arg)
        break

    return args


def make_handler(player_num: PlayerNum):

    async def majsoul_info(event: Event):

        args = _extract_command_args(
            event.get_message().extract_plain_text(),
            player_num,
        )

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

            nickname = await get_name_in_unconsumed_args(
                unconsumed_args
            )

            if not nickname:
                raise BadRequestError("请输入雀魂账号")

            kwargs["nickname"] = nickname

        coro = handle_majsoul_info(
            player_num=player_num,
            **kwargs
        )

        if conf.majsoul_query_timeout:
            await wait_for(
                coro,
                timeout=conf.majsoul_query_timeout
            )
        else:
            await coro

    return majsoul_info


four_player_majsoul_info_matcher = on_command(
    '雀魂信息',
    aliases=_FOUR_PLAYER_INFO_COMMAND_NAMES - {'雀魂信息'},
    block=True,
    priority=1
)

query_info_service.patch_matcher(
    four_player_majsoul_info_matcher
)

four_player_majsoul_info_matcher.__help_info__ = (
    f"{default_command_start}雀魂信息 <雀魂账号> "
    f"[<房间类型>] [最近<数量>场] "
    f"[最近<数量>{{天|周|个月|年}}]"
)

four_player_majsoul_info = make_handler(
    PlayerNum.four
)

four_player_majsoul_info = with_handling_reaction()(
    four_player_majsoul_info
)

four_player_majsoul_info = handle_error(
    error_handlers
)(
    four_player_majsoul_info
)

four_player_majsoul_info_matcher.append_handler(
    four_player_majsoul_info
)


three_player_majsoul_info_matcher = on_command(
    '雀魂三麻信息',
    aliases=_THREE_PLAYER_INFO_COMMAND_NAMES - {'雀魂三麻信息'},
    block=True,
    priority=1
)

query_info_service.patch_matcher(
    three_player_majsoul_info_matcher
)

three_player_majsoul_info_matcher.__help_info__ = (
    f"{default_command_start}雀魂三麻信息 <雀魂账号> "
    f"[<房间类型>] [最近<数量>场] "
    f"[最近<数量>{{天|周|个月|年}}]"
)

three_player_majsoul_info = make_handler(
    PlayerNum.three
)

three_player_majsoul_info = with_handling_reaction()(
    three_player_majsoul_info
)

three_player_majsoul_info = handle_error(
    error_handlers
)(
    three_player_majsoul_info
)

three_player_majsoul_info_matcher.append_handler(
    three_player_majsoul_info
)


async def handle_majsoul_info(
        nickname: str,
        player_num: PlayerNum,
        *,
        room_rank: Optional[
            AbstractSet[RoomRank]
        ] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
):

    default_start_time = start_time is None
    default_end_time = end_time is None
    if room_rank is None:

        if player_num == PlayerNum.four:
            room_rank = all_four_player_room_rank

        elif player_num == PlayerNum.three:
            room_rank = all_three_player_room_rank

    if start_time is None:
        start_time = datetime.fromisoformat(
            "2010-01-01T00:00:00"
        ).astimezone(timezone.utc)

    if end_time is None:
        end_time = datetime.now(timezone.utc)

    # 查询玩家
    players = await api[player_num].search_player(
        nickname
    )

    # 优先完全匹配
    exact_players = [
        p for p in players
        if p.nickname == nickname
    ]

    if exact_players:
        players = exact_players

    if not players:
        raise QueryError(
            "没有查询到该角色在金之间以上的对局数据呢~"
        )

    room_rank_text = map_room_rank(room_rank)

    # 多账号逐个发送
    for idx, p in enumerate(players):

        sio = StringIO()

        sio.write(
            f"====== 昵称：{p.nickname} ======\n"
        )

        try:

            stats_loaded_by_fallback = False
            if limit is not None:
                start_time_used = await (
                    _try_authorized_records_start_time(
                        player_num,
                        p.id,
                        start_time,
                        end_time,
                        room_rank,
                        limit,
                    )
                )

                if start_time_used is None:
                    latest_timestamp = p.latest_timestamp
                    if latest_timestamp > 10_000_000_000:
                        latest_timestamp /= 1000
                    latest_time = datetime.fromtimestamp(
                        latest_timestamp,
                        tz=timezone.utc
                    )

                    try:
                        start_time_used, player_stats = await (
                            api[player_num].player_stats_for_recent_games(
                                p.id,
                                start_time,
                                end_time,
                                room_rank,
                                limit=limit,
                                latest_time=latest_time
                            )
                        )
                    except RuntimeError as e:
                        raise QueryError(
                            f"无法精确定位最近{limit}场，请改用时间范围查询"
                        ) from e

                    stats_loaded_by_fallback = True

            else:
                start_time_used = start_time

            if stats_loaded_by_fallback:
                if player_stats is None:
                    player_extended_stats = None
                else:
                    player_extended_stats = await (
                        api[player_num].player_extended_stats(
                            p.id,
                            start_time_used,
                            end_time,
                            room_rank
                        )
                    )
            else:
                stats_task = create_task(
                    api[player_num].player_stats(
                        p.id,
                        start_time_used,
                        end_time,
                        room_rank
                    )
                )

                ext_task = create_task(
                    api[player_num].player_extended_stats(
                        p.id,
                        start_time_used,
                        end_time,
                        room_rank
                    )
                )

                player_stats = await stats_task
                player_extended_stats = await ext_task

        except HTTPStatusError as e:

            if e.response.status_code == 404:

                sio.write(
                    "没有该账号的对局数据"
                )

                await MessageFactory(
                    Text(sio.getvalue().strip())
                ).send()

                continue

            else:
                raise e

        if player_stats is None:

            sio.write(
                f"没有查询到{room_rank_text}"
                f"的对局数据呢~"
            )

            await MessageFactory(
                Text(sio.getvalue().strip())
            ).send()

            continue

        # 统计文本

        single_sio = StringIO()

        map_player_stats(
            single_sio,
            player_stats,
            room_rank_text,
            player_num
        )

        single_sio.write("\n")

        map_player_extended_stats(
            single_sio,
            player_extended_stats,
            room_rank_text
        )

        stats_text = single_sio.getvalue().strip()

        sio.write(stats_text)

        # 链接

        if conf.majsoul_send_link:

            sio.write("\n\n更多信息：\n")

            if player_num == PlayerNum.four:

                url = (
                    f"https://amae-koromo.sapk.ch/"
                    f"player/{p.id}/"
                )

            else:

                url = (
                    f"https://ikeda.sapk.ch/"
                    f"player/{p.id}/"
                )

            url += ".".join(
                map(
                    lambda x: str(x.value),
                    room_rank
                )
            )

            if not default_start_time:
                url += "/" + start_time.strftime(
                    "%Y-%m-%d"
                )

            if not default_end_time:
                url += "/" + end_time.strftime(
                    "%Y-%m-%d"
                )

            sio.write(url)

        # 发送统计信息

        msg = sio.getvalue().strip()

        await MessageFactory(
            Text(msg)
        ).send()

        # AI锐评单独发送

        try:

            ai_comment = await generate_ai_comment(
                stats_text
            )

            if ai_comment:

                await MessageFactory(
                    Text(
                        f"AI锐评：\n{ai_comment.strip()}"
                    )
                ).send()

        except Exception as e:

            await MessageFactory(
                Text(
                    f"AI锐评生成失败：{e}"
                )
            ).send()
