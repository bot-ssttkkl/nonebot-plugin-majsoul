from nonebot import logger, get_driver

from ..config import conf

if not conf.majsoul_username:
    logger.warning("majsoul_paipu is disabled because majsoul_username is not configured")
elif get_driver().type != "fastapi":
    logger.warning("majsoul_paipu is disabled because only FastAPI Driver is supported")
else:
    import json
    import re
    from asyncio import wait_for

    from nonebot import on_command, logger, require
    from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageEvent
    from nonebot.params import CommandArg
    from tensoul.downloader import MajsoulDownloadError

    from .downloader import get_downloader
    from ..errors import BadRequestError
    from ..interceptors.handle_error import handle_error
    from ..utils.nonebot import default_cmd_start

    uuid_reg = re.compile(r"\d{6}-[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}")

    require("nonebot_plugin_gocqhttp_cross_machine_upload_file")

    from nonebot_plugin_gocqhttp_cross_machine_upload_file import upload_group_file, upload_private_file

    query_majsoul_paipu_matcher = on_command("下载雀魂牌谱")


    @query_majsoul_paipu_matcher.handle()
    @handle_error(query_majsoul_paipu_matcher)
    async def majsoul_paipu(bot: Bot, event: MessageEvent, args=CommandArg()):
        plain_args = args.extract_plain_text()
        mat = uuid_reg.search(plain_args)
        if not mat:
            raise BadRequestError(f"使用方式：{default_cmd_start}下载雀魂牌谱 <牌谱网址>")

        uuid = mat.group(0)

        logger.opt(colors=True).info(f"Downloading paipu <y>{uuid}</y>")
        try:
            coro = get_downloader().download(uuid)
            if conf.majsoul_query_timeout:
                record = await wait_for(coro, timeout=conf.majsoul_query_timeout)
            else:
                record = await coro
        except MajsoulDownloadError as e:
            logger.opt(colors=True).warning(f"Failed to download paipu <y>{uuid}</y>, code: {e.code}")
            if e.code == 1203:
                raise BadRequestError("牌谱不存在") from e
            else:
                raise e

        time_str = record['title'][1]
        year = int(time_str[0:4])
        month = int(time_str[5:7])
        day = int(time_str[8:10])
        hour = int(time_str[11:13])
        minute = int(time_str[14:16])

        filename = f"{record['title'][0]}_{year}_{month}_{day}_{hour}_{minute}（{'、'.join(record['name'])}）.json"

        data = json.dumps(record, ensure_ascii=False).encode("utf-8")

        if isinstance(event, GroupMessageEvent):
            await upload_group_file(bot, event.group_id, filename, data)
        else:
            await upload_private_file(bot, event.user_id, filename, data)
