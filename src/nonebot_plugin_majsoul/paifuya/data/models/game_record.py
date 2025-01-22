from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from ssttkkl_nonebot_utils.pyc import field_validator
from .player_rank import PlayerRank
from .room_rank import RoomRank


class GamePlayer(BaseModel):
    id: int = Field(alias="accountId")
    nickname: str
    rank: PlayerRank = Field(alias="level")
    score: int
    pt: int = Field(alias="gradingScore")

    @field_validator("rank", mode="before")
    def parse_rank(cls, v):
        if isinstance(v, PlayerRank):
            return v
        elif isinstance(v, int):
            return PlayerRank.from_code(v)
        else:
            raise TypeError(f"value must be int or PlayerRank, got {type(v)}")


class GameRecord(BaseModel):
    room_rank: RoomRank = Field(alias="modeId")
    uuid: str
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")
    players: List[GamePlayer]

    @field_validator("start_time", "end_time", mode="before")
    def parse_timestamp(cls, v):
        if isinstance(v, int) or isinstance(v, float):
            return datetime.fromtimestamp(v, timezone.utc)
        else:
            return v
