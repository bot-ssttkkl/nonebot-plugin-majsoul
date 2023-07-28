from typing import Optional

from nonebot import get_driver, logger
from tensoul import MajsoulPaipuDownloader
from websockets.exceptions import ConnectionClosedError

from ..config import conf
from ..network.auto_retry import auto_retry

_downloader: Optional[MajsoulPaipuDownloader] = None


def get_downloader():
    if _downloader is None:
        raise RuntimeError("downloader is not ready")
    return _downloader


@get_driver().on_startup
async def restart_downloader():
    global _downloader

    if _downloader is not None:
        await _downloader.close()
        _downloader = None

    if conf.majsoul_username:
        _downloader = MajsoulPaipuDownloader()
        await _downloader.start()
        await _downloader.login(conf.majsoul_username, conf.majsoul_password)
        logger.opt(colors=True).success(f"Logged in as <y>{conf.majsoul_username}</y>")


@auto_retry(ConnectionClosedError, restart_downloader)
async def download_paipu(uuid: str):
    return await get_downloader().download(uuid)


@get_driver().on_shutdown
async def _destroy_downloader():
    global _downloader

    if _downloader is not None:
        await _downloader.close()
        _downloader = None


__all__ = ("get_downloader", "restart_downloader", "download_paipu")
