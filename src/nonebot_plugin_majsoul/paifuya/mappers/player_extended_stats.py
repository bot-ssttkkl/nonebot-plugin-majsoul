from typing import TextIO, Union, AbstractSet

from nonebot_plugin_majsoul.utils.percentile import percentile_str
from .room_rank import map_room_rank
from ..data.models.player_extended_stats import PlayerExtendedStats
from ..data.models.room_rank import RoomRank


def map_player_extended_stats(sio: TextIO, stats: PlayerExtendedStats,
                              room_rank: Union[AbstractSet[RoomRank], str]):
    if not isinstance(room_rank, str):
        room_rank = map_room_rank(room_rank)

    sio.write(f"【{room_rank} 详细数据】\n")

    sio.write(f"和牌率：{percentile_str(stats.和牌率)}    ")
    sio.write(f"放铳率：{percentile_str(stats.放铳率)}    ")
    sio.write(f"自摸率：{percentile_str(stats.自摸率)}    ")
    sio.write(f"默胡率：{percentile_str(stats.默听率)}\n")

    sio.write(f"副露率：{percentile_str(stats.副露率)}    ")
    sio.write(f"立直率：{percentile_str(stats.立直率)}    ")
    sio.write(f"流局率：{percentile_str(stats.流局率)}    ")
    sio.write(f"流听率：{percentile_str(stats.流听率)}\n")

    sio.write(f"先制率：{percentile_str(stats.先制率)}    ")
    sio.write(f"追立率：{percentile_str(stats.追立率)}    ")
    sio.write(f"立直巡目：{round(stats.立直巡目, 2)}    ")
    sio.write(f"和了巡目：{round(stats.和了巡数, 2)}\n")

    sio.write(f"平均打点：{stats.平均打点}    ")
    sio.write(f"平均铳点：{stats.平均铳点}    ")
    sio.write(f"打点效率：{stats.打点效率}    ")
    sio.write(f"净打点效率：{stats.净打点效率}\n")
