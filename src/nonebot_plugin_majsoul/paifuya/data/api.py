from datetime import datetime, timedelta
from functools import partial
from typing import List, AbstractSet, AsyncGenerator

from httpx import AsyncClient, URL, HTTPError
from nonebot import get_driver, logger

from nonebot_plugin_majsoul.network.auto_retry import auto_retry
from nonebot_plugin_majsoul.network.host_prober import HostProber
from .models.game_record import GameRecord
from .models.player_extended_stats import PlayerExtendedStats
from .models.player_info import PlayerInfo
from .models.player_num import PlayerNum
from .models.player_stats import PlayerStats
from .models.room_rank import RoomRank

prober = HostProber([
    "1.data.amae-koromo.com",
    "2.data.amae-koromo.com",
    "3.data.amae-koromo.com",
    "4.data.amae-koromo.com",
    "5-data.amae-koromo.com",
])


class PaifuyaApi:
    def __init__(self, baseurl):
        self._baseurl = baseurl

        async def req_hook(request):
            logger.trace(f"Request: {request.method} {request.url} - Waiting for response")

        async def resp_hook(response):
            request = response.request
            logger.trace(f"Response: {request.method} {request.url} - Status {response.status_code}")
            response.raise_for_status()

        self.client: AsyncClient = AsyncClient(
            follow_redirects=True,
            event_hooks={'request': [req_hook], 'response': [resp_hook]}
        )

        get_driver().on_shutdown(self.close)

    async def close(self):
        await self.client.aclose()

    @auto_retry(HTTPError, before_retry=partial(prober.select_host, exclude_current=True))
    async def search_player(
            self, nickname: str,
            *, limit: int = 10
    ) -> List[PlayerInfo]:
        resp = await self.client.get(
            URL(f"https://{prober.host}/{self._baseurl}/search_player/{nickname}"),
            params={"limit": limit}
        )
        return [PlayerInfo.parse_obj(x) for x in resp.json()]

    @auto_retry(HTTPError, before_retry=partial(prober.select_host, exclude_current=True))
    async def player_stats(
            self, player_id: int, start_time: datetime, end_time: datetime, room_rank: AbstractSet[RoomRank]
    ) -> PlayerStats:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{prober.host}/{self._baseurl}/player_stats/{player_id}/{start_timestamp}/{end_timestamp}"),
            params={"mode": mode}
        )
        return PlayerStats.parse_obj(resp.json())

    @auto_retry(HTTPError, before_retry=partial(prober.select_host, exclude_current=True))
    async def player_extended_stats(
            self, player_id: int, start_time: datetime, end_time: datetime, room_rank: AbstractSet[RoomRank]
    ) -> PlayerExtendedStats:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{prober.host}/{self._baseurl}/player_extended_stats/{player_id}/{start_timestamp}/{end_timestamp}"),
            params={"mode": mode}
        )
        return PlayerExtendedStats.parse_obj(resp.json())

    @auto_retry(HTTPError, before_retry=partial(prober.select_host, exclude_current=True))
    async def player_records(
            self, player_id: int, start_time: datetime, end_time: datetime, room_rank: AbstractSet[RoomRank],
            *, limit: int, descending: bool = True
    ) -> List[GameRecord]:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{prober.host}/{self._baseurl}/player_records/{player_id}/{end_timestamp}/{start_timestamp}"),
            params={"mode": mode, "limit": str(limit), "descending": str(descending).lower()}
        )
        return [GameRecord.parse_obj(x) for x in resp.json()]

    async def player_records_stream(
            self, player_id: int, start_time: datetime, end_time: datetime, room_rank: AbstractSet[RoomRank],
            *, batch: int = 200, descending: bool = True
    ) -> AsyncGenerator[GameRecord, None]:
        while start_time <= end_time:
            records = await self.player_records(
                player_id, start_time, end_time, room_rank, limit=batch, descending=descending
            )
            for r in records:
                yield r

            if len(records) < batch:
                break

            end_time = records[-1].start_time - timedelta(seconds=1)


four_player_api = PaifuyaApi(f"api/v2/pl4")
three_player_api = PaifuyaApi(f"api/v2/pl3")

paifuya_api = {
    PlayerNum.four: four_player_api,
    PlayerNum.three: three_player_api,
}

__all__ = ("PaifuyaApi", "four_player_api", "three_player_api", "paifuya_api")
