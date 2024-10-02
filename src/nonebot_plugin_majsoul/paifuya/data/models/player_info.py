from pydantic import BaseModel, validator

from .player_rank import PlayerRank


class PlayerLevel(BaseModel):
    id: PlayerRank
    score: int
    delta: int

    @validator("id", pre=True, allow_reuse=True)
    def parse_rank(cls, v):
        if isinstance(v, PlayerRank):
            return v
        elif isinstance(v, int):
            return PlayerRank.from_code(v)
        else:
            raise TypeError(f"value must be int or PlayerRank, got {type(v)}")


class PlayerInfo(BaseModel):
    id: int
    nickname: str
    level: PlayerLevel
    latest_timestamp: int
