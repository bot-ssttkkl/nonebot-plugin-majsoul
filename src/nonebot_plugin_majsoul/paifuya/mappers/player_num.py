from ..data.models.player_num import PlayerNum

_PLAYER_NUM_MAPPING = {
    PlayerNum.four: "四麻",
    PlayerNum.three: "三麻"
}


def map_player_num(player_num: PlayerNum):
    return _PLAYER_NUM_MAPPING[player_num]
