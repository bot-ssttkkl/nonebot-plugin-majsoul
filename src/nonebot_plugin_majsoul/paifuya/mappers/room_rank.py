from typing import AbstractSet

from ..data.models.room_rank import all_four_player_room_rank, \
    all_three_player_room_rank, \
    all_four_player_south_room_rank, all_four_player_east_room_rank, all_three_player_south_room_rank, \
    all_three_player_east_room_rank, RoomRank, all_three_player_golden_room_rank, all_four_player_golden_room_rank, \
    all_four_player_jade_room_rank, all_three_player_jade_room_rank, all_four_player_throne_room_rank, \
    all_three_player_throne_room_rank


def map_room_rank(room_rank: AbstractSet[RoomRank]) -> str:
    ans = []

    if room_rank & all_four_player_room_rank == all_four_player_room_rank:
        ans.append("四麻整体")
        room_rank = room_rank - all_four_player_room_rank

    if room_rank & all_three_player_room_rank == all_three_player_room_rank:
        ans.append("三麻整体")
        room_rank = room_rank - all_three_player_room_rank

    if room_rank & all_four_player_south_room_rank == all_four_player_south_room_rank:
        ans.append("四人南整体")
        room_rank = room_rank - all_four_player_south_room_rank

    if room_rank & all_four_player_east_room_rank == all_four_player_east_room_rank:
        ans.append("四人东整体")
        room_rank = room_rank - all_four_player_east_room_rank

    if room_rank & all_three_player_south_room_rank == all_three_player_south_room_rank:
        ans.append("三人南整体")
        room_rank = room_rank - all_three_player_south_room_rank

    if room_rank & all_three_player_east_room_rank == all_three_player_east_room_rank:
        ans.append("三人东整体")
        room_rank = room_rank - all_three_player_east_room_rank

    if room_rank & all_four_player_golden_room_rank == all_four_player_golden_room_rank:
        ans.append("四麻金之间整体")
        room_rank = room_rank - all_four_player_golden_room_rank

    if room_rank & all_three_player_golden_room_rank == all_three_player_golden_room_rank:
        ans.append("三麻金之间整体")
        room_rank = room_rank - all_three_player_golden_room_rank

    if room_rank & all_four_player_jade_room_rank == all_four_player_jade_room_rank:
        ans.append("四麻玉之间整体")
        room_rank = room_rank - all_four_player_jade_room_rank

    if room_rank & all_three_player_jade_room_rank == all_three_player_jade_room_rank:
        ans.append("三麻玉之间整体")
        room_rank = room_rank - all_three_player_jade_room_rank

    if room_rank & all_four_player_throne_room_rank == all_four_player_throne_room_rank:
        ans.append("四麻王座之间整体")
        room_rank = room_rank - all_four_player_throne_room_rank

    if room_rank & all_three_player_throne_room_rank == all_three_player_throne_room_rank:
        ans.append("三麻王座之间整体")
        room_rank = room_rank - all_three_player_throne_room_rank

    for rl in room_rank:
        if rl == RoomRank.four_player_golden_south:
            ans.append("四麻金南")
        elif rl == RoomRank.four_player_golden_east:
            ans.append("四麻金东")
        elif rl == RoomRank.four_player_jade_south:
            ans.append("四麻玉南")
        elif rl == RoomRank.four_player_jade_east:
            ans.append("四麻玉东")
        elif rl == RoomRank.four_player_throne_south:
            ans.append("四麻王座南")
        elif rl == RoomRank.four_player_throne_east:
            ans.append("四麻王座东")
        if rl == RoomRank.three_player_golden_south:
            ans.append("三麻金南")
        elif rl == RoomRank.three_player_golden_east:
            ans.append("三麻金东")
        elif rl == RoomRank.three_player_jade_south:
            ans.append("三麻玉南")
        elif rl == RoomRank.three_player_jade_east:
            ans.append("三麻玉东")
        elif rl == RoomRank.three_player_throne_south:
            ans.append("三麻王座南")
        elif rl == RoomRank.three_player_throne_east:
            ans.append("三麻王座东")

    return "&".join(ans)
