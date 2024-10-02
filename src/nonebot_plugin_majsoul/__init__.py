"""
nonebot-plugin-majsoul

@Author         : ssttkkl
@License        : AGPLv3
@GitHub         : https://github.com/ssttkkl/nonebot-plugin-majsoul
"""
from nonebot import require

require("nonebot_plugin_saa")
require("ssttkkl_nonebot_utils")

from ssttkkl_nonebot_utils.nonebot import default_command_start
from .config import Config

__usage__ = f"""
牌谱屋：
- {default_command_start}雀魂(三麻)信息 <雀魂账号> [<房间类型>] [最近<数量>场] [最近<数量>{{天|周|个月|年}}]
- {default_command_start}雀魂(三麻)对局 <雀魂账号> [<房间类型>]
- {default_command_start}雀魂(三麻)PT图 <雀魂账号> [最近<数量>场] [最近<数量>{{天|周|个月|年}}]

牌谱下载：
- {default_command_start}下载雀魂牌谱 <牌谱链接或UUID>

以上命令格式中，以<>包裹的表示一个参数，以[]包裹的表示一个可选项。

详细说明：参见https://github.com/bot-ssttkkl/nonebot-plugin-majsoul
""".strip()

from nonebot.plugin import PluginMetadata, inherit_supported_adapters

__plugin_meta__ = PluginMetadata(
    name='雀魂查询',
    description='根据牌谱屋的数据查询雀魂账号信息',
    usage=__usage__,
    type="application",
    config=Config,
    homepage="https://github.com/bot-ssttkkl/nonebot-plugin-majsoul",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
)

from . import paifuya  # noqa
from . import paipu  # noqa
