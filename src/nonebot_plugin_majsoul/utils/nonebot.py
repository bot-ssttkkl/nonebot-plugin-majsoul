from nonebot import get_driver

default_cmd_start = next(iter(get_driver().config.command_start))
