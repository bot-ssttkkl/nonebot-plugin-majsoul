from asyncio import wait_for
from datetime import datetime, timezone
from io import StringIO
from typing import Optional, AbstractSet, cast

from httpx import HTTPStatusError
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.internal.matcher import current_matcher, current_event, current_bot

from nonebot_plugin_majsoul.errors import BadRequestError
from .data.api import paifuya_api as api
from .data.models.player_num import PlayerNum
from .data.models.room_rank import RoomRank, all_four_player_room_rank, all_three_player_room_rank
from .mappers.game_record import map_game_record
from .mappers.room_rank import map_room_rank
from .parsers.room_rank import try_parse_room_rank
from ..config import conf
from ..interceptors.handle_error import handle_error
from ..utils.send_message import send_forward_msg


def make_handler(player_num: PlayerNum):
    async def query_majsoul_records(event: MessageEvent):
        args = event.get_message().extract_plain_text().split()[1:]

        nickname = args[0]
        if len(nickname) > 15:
            raise BadRequestError("昵称长度超过雀魂最大限制")

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

        coro = handle_query_majsoul_records(nickname, player_num, **kwargs)
        if conf.majsoul_query_timeout:
            await wait_for(coro, timeout=conf.majsoul_query_timeout)
        else:
            await coro

    return query_majsoul_records


query_four_player_majsoul_records_matcher = on_command("雀魂牌谱", aliases={'雀魂对局'})
query_four_player_majsoul_records = make_handler(PlayerNum.four)
query_four_player_majsoul_records = handle_error(query_four_player_majsoul_records_matcher)(
    query_four_player_majsoul_records)
query_four_player_majsoul_records_matcher.append_handler(query_four_player_majsoul_records)

query_three_player_majsoul_records_matcher = on_command("雀魂三麻牌谱", aliases={'雀魂三麻对局'})
query_three_player_majsoul_records = make_handler(PlayerNum.three)
query_three_player_majsoul_records = handle_error(query_three_player_majsoul_records_matcher)(
    query_three_player_majsoul_records)
query_three_player_majsoul_records_matcher.append_handler(query_three_player_majsoul_records)


async def handle_query_majsoul_records(nickname: str, player_num: PlayerNum, *,
                                       room_rank: Optional[AbstractSet[RoomRank]] = None):
    if room_rank is None:
        if player_num == PlayerNum.four:
            room_rank = all_four_player_room_rank
        elif player_num == PlayerNum.three:
            room_rank = all_three_player_room_rank

    start_time = datetime.fromisoformat("2010-01-01T00:00:00")
    end_time = datetime.now(timezone.utc)

    msgs = []

    players = await api[player_num].search_player(nickname)
    if len(players) == 0:
        msgs.append(Message(MessageSegment.text("没有查询到该角色在金之间以上的对局数据呢~")))
    else:
        try:
            records = await api[player_num].player_records(
                players[0].id,
                start_time,
                end_time,
                room_rank,
                5,
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

        msgs.append(Message(MessageSegment.text(msg.strip())))

        if records:
            for i, r in enumerate(records):
                with StringIO() as sio:
                    map_game_record(sio, r, players[0].id)
                    msgs.append(Message(MessageSegment.text(sio.getvalue().strip())))

        with StringIO() as url:
            url.write(f"https://amae-koromo.sapk.ch/player/{players[0].id}/")
            url.write(".".join(map(lambda x: str(x.value), room_rank)))

            msgs.append(Message(MessageSegment.text(f"更多信息：{url.getvalue()}")))

    if len(msgs) == 1:
        await current_matcher.get().send(msgs[0])
    else:
        e = cast(MessageEvent, current_event.get())
        await send_forward_msg(current_bot.get(), e, msgs)
