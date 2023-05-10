from ..data.models.player_rank import PlayerRank, PlayerMajorRank

_MAJOR_RANK_MAPPING = {
    PlayerMajorRank.novice: "心",
    PlayerMajorRank.adept: "士",
    PlayerMajorRank.expert: "杰",
    PlayerMajorRank.master: "豪",
    PlayerMajorRank.saint: "圣",
    PlayerMajorRank.celestial_old: "魂",
    PlayerMajorRank.celestial: "魂",
}


def map_player_rank(rank: PlayerRank) -> str:
    return _MAJOR_RANK_MAPPING[rank.major_rank] + str(rank.minor_rank)
