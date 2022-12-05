from typing import TextIO, Optional

import tzlocal

from nonebot_plugin_majsoul.paifuya.data.models.game_record import GameRecord
from nonebot_plugin_majsoul.paifuya.mappers.player_rank import map_player_rank
from nonebot_plugin_majsoul.paifuya.mappers.room_rank import map_room_rank
from nonebot_plugin_majsoul.utils.rank import ranked

_local_timezone = tzlocal.get_localzone()


def _encode_account_id(account_id: int) -> int:
    return 1358437 + ((7 * account_id + 1117113) ^ 86216345)


def _get_record_link(record: GameRecord, player_id: int) -> str:
    # https://github.com/SAPikachu/amae-koromo/blob/7b99f10f0fce251641013c5571c4fbe5edaa20f1/src/data/types/record.ts#L56
    #
    # encodeAccountId: (t: number) => 1358437 + ((7 * t + 1117113) ^ 86216345),
    #
    # // ...
    #
    # getRecordLink(rec: GameRecord | string, player?: PlayerRecord | number | string) {
    #     const playerId = typeof player === "object" ? player.accountId : player;
    #     const trailer = playerId
    #       ? `_a${GameRecord.encodeAccountId(typeof playerId === "number" ? playerId : parseInt(playerId))}`
    #       : "";
    #     const uuid = typeof rec === "string" ? rec : rec.uuid;
    #     return `${i18n.t("https://game.maj-soul.net/1/")}?paipu=${uuid}${trailer}`;
    #   }

    trailer = f"_a{_encode_account_id(player_id)}"
    return f"https://game.maj-soul.net/1/?paipu={record.uuid}{trailer}"


def map_game_record(sio: TextIO, record: GameRecord, player_id: int, num: Optional[int] = None):
    if num is not None:
        sio.write(f"[{num}]  ")

    for rank, player in ranked(record.players, key=lambda x: x.pt, reverse=True):
        if player.id == player_id:
            sio.write(f"[#{rank}]")
        else:
            sio.write(f"#{rank}")
        sio.write(f'  [{map_player_rank(player.rank)}]{player.nickname}    {player.score}  ')

        sio.write('(')
        if player.pt > 0:
            sio.write('+')
        elif player.pt == 0:
            sio.write('±')
        sio.write(str(player.pt))
        sio.write(')\n')

    sio.write("\n")
    sio.write(f"房间：{map_room_rank({record.room_rank})}\n")
    sio.write(f"时间：{record.start_time.astimezone(_local_timezone).strftime('%Y/%m/%d %H:%M')}\n")
    sio.write(_get_record_link(record, player_id))
    sio.write("\n")
