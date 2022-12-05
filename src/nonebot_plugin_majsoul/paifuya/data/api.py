from asyncio import create_task, sleep
from datetime import datetime
from functools import wraps
from typing import List, AbstractSet, Optional

from httpx import AsyncClient, URL, HTTPError
from icmplib import async_ping, NameLookupError, SocketAddressError, ICMPSocketError
from nonebot import get_driver, logger

from nonebot_plugin_majsoul.network.auto_retry import auto_retry
from .models.game_record import GameRecord
from .models.player_extended_stats import PlayerExtendedStats
from .models.player_info import PlayerInfo
from .models.player_num import PlayerNum
from .models.player_stats import PlayerStats
from .models.room_rank import RoomRank

_mirrors = [
    "1.data.amae-koromo.com",
    "2.data.amae-koromo.com",
    "3.data.amae-koromo.com",
    "4.data.amae-koromo.com",
    "5.data.amae-koromo.com",
]


class PaifuyaHostProber:
    def __init__(self):
        self._host = _mirrors[0]
        self._select_host_daemon_task = None

        get_driver().on_startup(self.start)
        get_driver().on_shutdown(self.close)

    async def start(self):
        self._select_host_daemon_task = create_task(self._select_host_daemon())

    async def close(self):
        self._select_host_daemon_task.cancel()

    @property
    def host(self) -> str:
        return self._host

    async def select_host(self, exclude: Optional[AbstractSet[str]] = None):
        logger.debug("paifuya host selecting...")

        ping_tasks = [create_task(async_ping(h))
                      if not exclude or h not in exclude
                      else None
                      for h in _mirrors]

        selected = None
        selected_rtt = None

        for i, ping_task in enumerate(ping_tasks):
            if ping_task is None:
                continue

            try:
                ping_result = await ping_task
            except (NameLookupError, SocketAddressError, ICMPSocketError) as e:
                logger.trace(f"failed to ping to {_mirrors[i]} ({str(type(e))})")
                continue

            logger.trace(f"ping to {_mirrors[i]}")
            logger.trace(ping_result)
            if selected is None or ping_result.avg_rtt < selected_rtt:
                selected = _mirrors[i]
                selected_rtt = ping_result.avg_rtt

        if selected is not None:
            self._host = selected
            logger.info(f"switched paifuya host to {selected}  (avg rtt: {selected_rtt}ms)")
            return True
        else:
            return False

    async def _select_host_daemon(self):
        try:
            while True:
                if await self.select_host():
                    await sleep(10 * 60)
                else:
                    logger.error(f"all ping to paifuya host has failed. will retry after 60s...")
                    await sleep(60)
        except Exception as e:
            logger.exception(e)

    def select_on_exception(self, exc_type):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except exc_type as e:
                    await self.select_host(exclude={self._host})
                    raise e

            return wrapper

        return decorator


_prober = PaifuyaHostProber()


class PaifuyaApi:
    def __init__(self, baseurl):
        self._host = _mirrors[0]
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

    @auto_retry
    @_prober.select_on_exception(HTTPError)
    async def search_player(self, nickname: str, *, limit: int = 10) -> List[PlayerInfo]:
        resp = await self.client.get(
            URL(f"https://{_prober.host}/{self._baseurl}/search_player/{nickname}"),
            params={"limit": limit}
        )
        return [PlayerInfo.parse_obj(x) for x in resp.json()]

    @auto_retry
    @_prober.select_on_exception(HTTPError)
    async def player_stats(self, player_id: int, start_time: datetime, end_time: datetime,
                           room_rank: AbstractSet[RoomRank]) -> PlayerStats:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{_prober.host}/{self._baseurl}/player_stats/{player_id}/{start_timestamp}/{end_timestamp}"),
            params={"mode": mode}
        )
        return PlayerStats.parse_obj(resp.json())

    @auto_retry
    @_prober.select_on_exception(HTTPError)
    async def player_extended_stats(self, player_id: int, start_time: datetime, end_time: datetime,
                                    room_rank: AbstractSet[RoomRank]) -> PlayerExtendedStats:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{_prober.host}/{self._baseurl}/player_extended_stats/{player_id}/{start_timestamp}/{end_timestamp}"),
            params={"mode": mode}
        )
        return PlayerExtendedStats.parse_obj(resp.json())

    @auto_retry
    @_prober.select_on_exception(HTTPError)
    async def player_records(self, player_id: int, start_time: datetime, end_time: datetime,
                             room_rank: AbstractSet[RoomRank], limit: int, descending: bool = True) -> List[GameRecord]:
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        mode = ".".join(map(lambda x: str(x.value), room_rank))
        resp = await self.client.get(
            URL(f"https://{_prober.host}/{self._baseurl}/player_records/{player_id}/{end_timestamp}/{start_timestamp}"),
            params={"mode": mode, "limit": str(limit), "descending": str(descending).lower()}
        )
        return [GameRecord.parse_obj(x) for x in resp.json()]


four_player_api = PaifuyaApi(f"api/v2/pl4")
three_player_api = PaifuyaApi(f"api/v2/pl3")

paifuya_api = {
    PlayerNum.four: four_player_api,
    PlayerNum.three: three_player_api,
}

__all__ = ("PaifuyaApi", "four_player_api", "three_player_api", "paifuya_api")
