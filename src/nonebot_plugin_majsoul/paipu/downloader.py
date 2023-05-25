from typing import Optional

from nonebot import get_driver, logger
from tensoul import MajsoulPaipuDownloader

from ..config import conf

_downloader: Optional[MajsoulPaipuDownloader] = None


def get_downloader():
    if _downloader is None:
        raise RuntimeError("downloader is not ready")
    return _downloader


@get_driver().on_startup
async def init_downloader():
    global _downloader
    if conf.majsoul_username:
        _downloader = MajsoulPaipuDownloader()
        await _downloader.start()
        await _downloader.login(conf.majsoul_username, conf.majsoul_password)
        logger.opt(colors=True).success(f"Logged in as <y>{conf.majsoul_username}</y>")


@get_driver().on_shutdown
async def destroy_downloader():
    global _downloader

    if _downloader is not None:
        await _downloader.close()
        _downloader = None
