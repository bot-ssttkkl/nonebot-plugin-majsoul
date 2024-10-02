"""
nonebot-plugin-majsoul

@Author         : ssttkkl
@License        : AGPLv3
@GitHub         : https://github.com/ssttkkl/nonebot-plugin-majsoul
"""
from nonebot import require

require("nonebot_plugin_saa")
require("nonebot_plugin_orm")
require("nonebot_plugin_user")
require("ssttkkl_nonebot_utils")

from . import paifuya  # noqa
from . import paipu  # noqa
from . import binding  # noqa

from ssttkkl_nonebot_utils.nonebot import default_command_start
from .config import Config
from .data import migrations

__usage__ = f"""
账号绑定：
- 查询当前绑定：{default_command_start}雀魂账号绑定
- 绑定账号：{default_command_start}雀魂账号绑定 <雀魂账号>
- 解除当前绑定：{default_command_start}雀魂账号解绑

牌谱屋：
- 账号数据查询：{default_command_start}雀魂(三麻)信息 <雀魂账号> [<房间类型>] [最近<数量>场] [最近<数量>{{天|周|个月|年}}]
- 账号对局查询：{default_command_start}雀魂(三麻)对局 <雀魂账号> [<房间类型>]
- 账号PT走势图：{default_command_start}雀魂(三麻)PT图 <雀魂账号> [最近<数量>场] [最近<数量>{{天|周|个月|年}}]

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
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa", "nonebot_plugin_user"),
    extra={"orm_version_location": migrations}
)
