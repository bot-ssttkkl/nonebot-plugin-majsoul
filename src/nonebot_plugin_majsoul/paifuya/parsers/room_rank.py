from typing import AbstractSet, Tuple, Optional

from ..data.models.room_rank import RoomRank, all_four_player_south_room_rank, \
    all_four_player_east_room_rank, all_three_player_east_room_rank, all_three_player_south_room_rank, \
    all_four_player_golden_room_rank, all_three_player_golden_room_rank, all_four_player_jade_room_rank, \
    all_three_player_jade_room_rank, all_four_player_throne_room_rank, all_three_player_throne_room_rank

_ROOM_RANK_REVERSED_MAPPING = {
    "南": (all_four_player_south_room_rank, all_three_player_south_room_rank),
    "东": (all_four_player_east_room_rank, all_three_player_east_room_rank),

    "金": (all_four_player_golden_room_rank, all_three_player_golden_room_rank),
    "玉": (all_four_player_jade_room_rank, all_three_player_jade_room_rank),
    "王座": (all_four_player_throne_room_rank, all_three_player_throne_room_rank),

    "金东": ({RoomRank.four_player_golden_east}, {RoomRank.three_player_golden_east}),
    "金南": ({RoomRank.four_player_golden_south}, {RoomRank.three_player_golden_south}),
    "玉东": ({RoomRank.four_player_jade_east}, {RoomRank.three_player_jade_east}),
    "玉南": ({RoomRank.four_player_jade_south}, {RoomRank.three_player_jade_south}),
    "王座东": ({RoomRank.four_player_throne_east}, {RoomRank.three_player_throne_east}),
    "王座南": ({RoomRank.four_player_throne_south}, {RoomRank.three_player_throne_south}),
}

_ROOM_RANK_REVERSED_MAPPING["南场"] = _ROOM_RANK_REVERSED_MAPPING["南"]
_ROOM_RANK_REVERSED_MAPPING["东场"] = _ROOM_RANK_REVERSED_MAPPING["东"]
_ROOM_RANK_REVERSED_MAPPING["金之间"] = _ROOM_RANK_REVERSED_MAPPING["金"]
_ROOM_RANK_REVERSED_MAPPING["玉之间"] = _ROOM_RANK_REVERSED_MAPPING["玉"]
_ROOM_RANK_REVERSED_MAPPING["王座之间"] = _ROOM_RANK_REVERSED_MAPPING["王座"]
_ROOM_RANK_REVERSED_MAPPING["金之间东场"] = _ROOM_RANK_REVERSED_MAPPING["金东"]
_ROOM_RANK_REVERSED_MAPPING["玉之间东场"] = _ROOM_RANK_REVERSED_MAPPING["玉东"]
_ROOM_RANK_REVERSED_MAPPING["王座之间东场"] = _ROOM_RANK_REVERSED_MAPPING["王座东"]
_ROOM_RANK_REVERSED_MAPPING["金之间南场"] = _ROOM_RANK_REVERSED_MAPPING["金南"]
_ROOM_RANK_REVERSED_MAPPING["玉之间南场"] = _ROOM_RANK_REVERSED_MAPPING["玉南"]
_ROOM_RANK_REVERSED_MAPPING["王座之间南场"] = _ROOM_RANK_REVERSED_MAPPING["王座南"]


def try_parse_room_rank(raw: str) -> Optional[Tuple[AbstractSet[RoomRank], AbstractSet[RoomRank]]]:
    return _ROOM_RANK_REVERSED_MAPPING.get(raw, None)
