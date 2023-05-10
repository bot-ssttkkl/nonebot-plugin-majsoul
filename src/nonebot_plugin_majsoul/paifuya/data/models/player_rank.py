from enum import Enum
from functools import total_ordering
from typing import NamedTuple

from .player_num import PlayerNum


class PlayerMajorRank(int, Enum):
    novice = 1
    adept = 2
    expert = 3
    master = 4
    saint = 5
    celestial_old = 6
    celestial = 7


_RANK_MAX_PT = {
    203: 1000,
    301: 1200,
    302: 1400,
    303: 2000,
    401: 2800,
    402: 3200,
    403: 3600,
    501: 4000,
    502: 6000,
    503: 9000,
}

_CELESTIAL_MAX_PT = 10000


@total_ordering
class PlayerRank(NamedTuple):
    player_num: PlayerNum
    major_rank: PlayerMajorRank
    minor_rank: int

    @property
    def code(self) -> int:
        return self.player_num.value * 10000 + self.major_rank * 100 + self.minor_rank

    @classmethod
    def from_code(cls, code: int):
        game_players = code // 10000
        major_rank = code % 1000 // 100
        minor_rank = code % 100
        return PlayerRank(PlayerNum(game_players), PlayerMajorRank(major_rank), minor_rank)

    @property
    def max_pt(self) -> int:
        if self.major_rank != PlayerMajorRank.celestial and self.major_rank != PlayerMajorRank.celestial_old:
            return _RANK_MAX_PT[self.major_rank * 100 + self.minor_rank]
        else:
            return _CELESTIAL_MAX_PT

    def __lt__(self, other):
        if isinstance(other, PlayerRank):
            return self.code < other.code
        else:
            raise TypeError(type(other))


__all__ = ("PlayerMajorRank", "PlayerRank")
