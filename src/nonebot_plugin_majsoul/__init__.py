"""
nonebot-plugin-majsoul

@Author         : ssttkkl
@License        : AGPLv3
@GitHub         : https://github.com/ssttkkl/nonebot-plugin-majsoul
"""
from nonebot import require

require("nonebot_plugin_saa")

from .utils.nonebot import default_cmd_start

help_text = f"""
牌谱屋：
- {default_cmd_start}雀魂(三麻)信息 <雀魂账号> [<房间类型>] [最近<数量>场] [最近<数量>{{天|周|个月|年}}]
- {default_cmd_start}雀魂(三麻)对局 <雀魂账号> [<房间类型>]
- {default_cmd_start}雀魂(三麻)PT图 <雀魂账号> [最近<数量>场] [最近<数量>{{天|周|个月|年}}]

牌谱下载：
- {default_cmd_start}下载雀魂牌谱 <牌谱链接或UUID>

以上命令格式中，以<>包裹的表示一个参数，以[]包裹的表示一个可选项。

详细说明：参见https://github.com/ssttkkl/nonebot-plugin-majsoul
""".strip()

from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='雀魂查询',
    description='根据牌谱屋的数据查询雀魂账号信息',
    usage=help_text
)

from . import paifuya
from . import paipu
