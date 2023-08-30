from nonebot import logger

from ..config import conf

if not conf.majsoul_username:
    logger.warning("majsoul_paipu is disabled because majsoul_username is not configured")
else:
    import json
    import re
    from asyncio import wait_for

    from nonebot import on_command, Bot
    from nonebot.internal.adapter import Event
    from nonebot.params import CommandArg
    from ssttkkl_nonebot_utils.errors.errors import BadRequestError, QueryError
    from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
    from ssttkkl_nonebot_utils.interceptor.with_handling_reaction import with_handling_reaction
    from ssttkkl_nonebot_utils.nonebot import default_command_start
    from ssttkkl_nonebot_utils.platform import platform_func
    from tensoul.downloader import MajsoulDownloadError

    from .downloader import download_paipu
    from ..errors import error_handlers

    uuid_reg = re.compile(r"\d{6}-[\da-fA-F]{8}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{12}")

    query_majsoul_paipu_matcher = on_command("下载雀魂牌谱")


    @query_majsoul_paipu_matcher.handle()
    @handle_error(error_handlers)
    @with_handling_reaction()
    async def majsoul_paipu(bot: Bot, event: Event, args=CommandArg()):
        plain_args = args.extract_plain_text()
        mat = uuid_reg.search(plain_args)
        if not mat:
            raise BadRequestError(f"使用方式：{default_command_start}下载雀魂牌谱 <牌谱网址>")

        uuid = mat.group(0)

        logger.opt(colors=True).info(f"Downloading paipu <y>{uuid}</y>")
        try:
            coro = download_paipu(uuid)
            if conf.majsoul_query_timeout:
                record = await wait_for(coro, timeout=conf.majsoul_query_timeout)
            else:
                record = await coro
        except MajsoulDownloadError as e:
            logger.opt(colors=True).warning(f"Failed to download paipu <y>{uuid}</y>, code: {e.code}")
            if e.code == 1203:
                raise QueryError("牌谱不存在") from e
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

        platform_func(bot).upload_file(bot, event, filename, data)
