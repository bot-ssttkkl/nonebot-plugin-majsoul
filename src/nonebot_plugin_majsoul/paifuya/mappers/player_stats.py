from typing import TextIO, AbstractSet, Union

from .player_rank import map_player_rank
from .room_rank import map_room_rank
from ..data.models.player_info import PlayerLevel
from ..data.models.player_num import PlayerNum
from ..data.models.player_rank import PlayerRank, PlayerMajorRank
from ..data.models.player_stats import PlayerStats
from ..data.models.room_rank import RoomRank
from ...utils.percentile import percentile_str


def map_player_stats(sio: TextIO, stats: PlayerStats,
                     room_rank: Union[AbstractSet[RoomRank], str],
                     player_num: PlayerNum):
    if not isinstance(room_rank, str):
        room_rank = map_room_rank(room_rank)

    sio.write(f"【{room_rank} 基础数据】\n")

    level = fix_level(stats.level)
    sio.write(f"记录段位：{map_player_rank(level.id)}    ")
    sio.write(f"记录PT：{level.score}\n")

    sio.write(f"总场次：{stats.count}    ")
    sio.write(f"平均顺位：{round(stats.avg_rank, 2)}\n")

    sio.write(f"一位率：{percentile_str(stats.rank_rates[0])}    ")
    sio.write(f"二位率：{percentile_str(stats.rank_rates[1])}\n")

    sio.write(f"三位率：{percentile_str(stats.rank_rates[2])}")
    if player_num == PlayerNum.four:
        sio.write("    ")
        sio.write(f"四位率：{percentile_str(stats.rank_rates[3])}")
    sio.write("\n")


def fix_level(level: PlayerLevel) -> PlayerLevel:
    pt = level.score + level.delta
    if pt < 0:
        # 已掉段
        if level.id.minor_rank == 1:
            rank = PlayerRank(level.id.player_num,
                              PlayerMajorRank(level.id.major_rank.value - 1),
                              3)
        else:
            rank = PlayerRank(level.id.player_num,
                              level.id.major_rank,
                              level.id.minor_rank - 1)
        pt = rank.max_pt // 2
    elif pt > level.id.max_pt:
        # 已升段
        if level.id.major_rank != PlayerMajorRank.celestial and level.id.minor_rank == 3:
            rank = PlayerRank(level.id.player_num,
                              PlayerMajorRank(level.id.major_rank.value + 1),
                              1)
        else:
            rank = PlayerRank(level.id.player_num,
                              level.id.major_rank,
                              level.id.minor_rank + 1)
        pt = rank.max_pt // 2
    else:
        rank = level.id

    return PlayerLevel(id=rank, score=pt, delta=0)
