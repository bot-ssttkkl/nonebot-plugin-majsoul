from typing import Optional

from nonebot import get_driver, logger
from tensoul import MajsoulPaipuDownloader
from websockets.exceptions import ConnectionClosedError

from ..config import conf
from ..network.auto_retry import auto_retry

_downloader: Optional[MajsoulPaipuDownloader] = None


class DownloaderNotReadyError(RuntimeError):
    def __init__(self):
        super().__init__("downloader is not ready yet.")


async def _destroy_downloader():
    global _downloader

    if _downloader is not None:
        await _downloader.close()
        _downloader = None


async def restart_downloader():
    global _downloader

    await _destroy_downloader()

    if conf.majsoul_username:
        _downloader = MajsoulPaipuDownloader()
        await _downloader.start()
        await _downloader.login(conf.majsoul_username, conf.majsoul_password)
        logger.opt(colors=True).success(f"Logged in as <y>{conf.majsoul_username}</y>")


@auto_retry(DownloaderNotReadyError, restart_downloader)
async def get_downloader():
    if _downloader is None:
        raise DownloaderNotReadyError()
    return _downloader


@auto_retry(ConnectionClosedError, restart_downloader)
async def download_paipu(uuid: str):
    return await (await get_downloader()).download(uuid)


@get_driver().on_startup
@logger.catch
async def _init_downloader_on_startup():
    await restart_downloader()


@get_driver().on_shutdown
@logger.catch
async def _destroy_downloader_on_shutdown():
    await _destroy_downloader()


__all__ = ("get_downloader", "restart_downloader", "download_paipu")
