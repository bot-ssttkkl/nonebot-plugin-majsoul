from enum import Enum


class RoomRank(int, Enum):
    four_player_golden_east = 8
    four_player_golden_south = 9
    four_player_jade_east = 11
    four_player_jade_south = 12
    four_player_throne_east = 15
    four_player_throne_south = 16
    three_player_golden_east = 21
    three_player_golden_south = 22
    three_player_jade_east = 23
    three_player_jade_south = 24
    three_player_throne_east = 25
    three_player_throne_south = 26


all_four_player_east_room_rank = frozenset([
    RoomRank.four_player_golden_east,
    RoomRank.four_player_jade_east,
    RoomRank.four_player_throne_east,
])

all_four_player_south_room_rank = frozenset([
    RoomRank.four_player_golden_south,
    RoomRank.four_player_jade_south,
    RoomRank.four_player_throne_south,
])

all_four_player_room_rank = frozenset([
    *all_four_player_east_room_rank,
    *all_four_player_south_room_rank
])

all_three_player_east_room_rank = frozenset([
    RoomRank.three_player_golden_east,
    RoomRank.three_player_jade_east,
    RoomRank.three_player_throne_east,
])

all_three_player_south_room_rank = frozenset([
    RoomRank.three_player_golden_south,
    RoomRank.three_player_jade_south,
    RoomRank.three_player_throne_south,
])

all_three_player_room_rank = frozenset([
    *all_three_player_east_room_rank,
    *all_three_player_south_room_rank
])

all_four_player_golden_room_rank = frozenset([
    RoomRank.four_player_golden_east, RoomRank.four_player_golden_south
])
all_three_player_golden_room_rank = frozenset([
    RoomRank.three_player_golden_east, RoomRank.three_player_golden_south
])

all_four_player_jade_room_rank = frozenset([
    RoomRank.four_player_jade_east, RoomRank.four_player_jade_south
])
all_three_player_jade_room_rank = frozenset([
    RoomRank.three_player_jade_east, RoomRank.three_player_jade_south
])

all_four_player_throne_room_rank = frozenset([
    RoomRank.four_player_throne_east, RoomRank.four_player_throne_south
])
all_three_player_throne_room_rank = frozenset([
    RoomRank.three_player_throne_east, RoomRank.three_player_throne_south
])
