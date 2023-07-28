from asyncio import create_task, sleep
from typing import TypeVar, Sequence

from icmplib import async_ping, NameLookupError, SocketAddressError, ICMPSocketError
from nonebot import get_driver, logger
from typing_extensions import ParamSpec

from ..utils.percentile import percentile_str

T = TypeVar('T')
P = ParamSpec('P')


class HostProber:
    def __init__(self, mirrors: Sequence[str]):
        self._mirrors = mirrors
        self._host = mirrors[0]
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

    async def select_host(self, exclude_current: bool = False) -> bool:
        logger.debug("paifuya host selecting...")

        ping_tasks = [create_task(async_ping(h))
                      if not exclude_current or h == self._host
                      else None
                      for h in self._mirrors]

        selected = None
        selected_result = None

        for i, ping_task in enumerate(ping_tasks):
            if ping_task is None:
                continue

            try:
                ping_result = await ping_task
            except (NameLookupError, SocketAddressError, ICMPSocketError) as e:
                logger.trace(f"failed to ping to {self._mirrors[i]} ({str(type(e))})")
                continue

            logger.trace(f"ping to {self._mirrors[i]}")
            logger.trace(ping_result)

            if ping_result.packet_loss == 1:
                logger.trace(f"{self._mirrors[i]} was ignored due to all packages loss")
                continue

            if (selected is None or
                    (ping_result.packet_loss, ping_result.avg_rtt) <
                    (ping_result.packet_loss, selected_result.avg_rtt)):
                selected = self._mirrors[i]
                selected_result = ping_result

        if selected is not None:
            self._host = selected
            logger.info(f"switched paifuya host to {selected}  "
                        f"(avg rtt: {selected_result.avg_rtt}ms, "
                        f"packet loss: {percentile_str(selected_result.packet_loss)})")
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
