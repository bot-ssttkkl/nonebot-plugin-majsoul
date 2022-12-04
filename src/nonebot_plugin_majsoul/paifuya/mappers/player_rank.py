from .general import map_digit
from ..data.models.player_rank import PlayerRank, PlayerMajorRank

_MAJOR_RANK_MAPPING = {
    PlayerMajorRank.novice: "初心",
    PlayerMajorRank.adept: "雀士",
    PlayerMajorRank.expert: "雀杰",
    PlayerMajorRank.master: "雀豪",
    PlayerMajorRank.saint: "雀圣",
    PlayerMajorRank.celestial: "魂天",
}


def map_player_rank(rank: PlayerRank) -> str:
    return _MAJOR_RANK_MAPPING[rank.major_rank] + map_digit(rank.minor_rank)
