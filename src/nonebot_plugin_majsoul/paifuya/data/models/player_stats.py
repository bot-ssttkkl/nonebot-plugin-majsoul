from typing import List, Optional

from pydantic import BaseModel, Extra

from .player_info import PlayerLevel
from .room_rank import RoomRank


class PlayerStats(BaseModel):
    id: int
    nickname: str
    count: int
    played_modes: List[RoomRank]
    level: PlayerLevel
    max_level: PlayerLevel
    rank_rates: List[float]
    rank_avg_score: List[Optional[float]]
    avg_rank: float
    # negative_rate: float

    class Config:
        extra = Extra.ignore
