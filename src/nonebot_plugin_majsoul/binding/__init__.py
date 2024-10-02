from nonebot.internal.adapter import Event
from nonebot.plugin.on import on_command
from nonebot_plugin_saa import MessageFactory
from ssttkkl_nonebot_utils.errors.errors import BadRequestError
from ssttkkl_nonebot_utils.interceptor.handle_error import handle_error
from ssttkkl_nonebot_utils.nonebot import default_command_start

from nonebot_plugin_majsoul.data.account_binding import AccountBinding
from nonebot_plugin_majsoul.errors import error_handlers
from nonebot_plugin_majsoul.utils.user import get_uid

binding = on_command("雀魂账号绑定")
binding.__help_info__ = f"查询当前绑定：{default_command_start}雀魂账号绑定    绑定账号：{default_command_start}雀魂账号绑定 <雀魂账号>"
unset_binding = on_command("雀魂账号解绑")
unset_binding.__help_info__ = f"解除当前绑定：{default_command_start}雀魂账号解绑"


@binding.handle()
@handle_error(error_handlers)
async def handle_binding(event: Event):
    args = event.get_message().extract_plain_text().split()
    cmd, args = args[0], args[1:]

    if len(args) == 0:
        await query_binding(await get_uid())
    else:
        await set_binding(await get_uid(), args[0])


async def query_binding(uid: int):
    majsoul_name = await AccountBinding.get(uid)
    if majsoul_name is None:
        raise BadRequestError("当前用户尚未绑定雀魂账号")

    await MessageFactory(f"当前绑定雀魂账号：{majsoul_name}").send(reply=True)


async def set_binding(uid: int, majsoul_name: str):
    await AccountBinding.set(uid, majsoul_name)
    await MessageFactory(f"成功绑定雀魂账号：{majsoul_name}").send(reply=True)


@unset_binding.handle()
@handle_error(error_handlers)
async def unset_binding():
    await AccountBinding.unset(await get_uid())
    await MessageFactory(f"成功解绑雀魂账号").send(reply=True)
