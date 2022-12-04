from typing import List

from pydantic import BaseModel

from nonebot_plugin_majsoul.data.models.player_info import PlayerLevel
from nonebot_plugin_majsoul.data.models.room_rank import RoomRank


class PlayerStats(BaseModel):
    id: int
    nickname: str
    count: int
    played_modes: List[RoomRank]
    level: PlayerLevel
    max_level: PlayerLevel
    rank_rates: List[float]
    rank_avg_score: List[float]
    avg_rank: float
    negative_rate: float
