from typing import Optional

from nonebot_plugin_orm import Model, get_scoped_session
from sqlalchemy import select, delete
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class AccountBinding(MappedAsDataclass, Model):
    __tablename__ = "nonebot_plugin_majsoul_account_binding"
    __table_args__ = {"extend_existing": True}

    uid: Mapped[int] = mapped_column(primary_key=True)
    majsoul_name: Mapped[str]

    @staticmethod
    async def _get_binding(uid: int) -> "Optional[AccountBinding]":
        stmt = select(AccountBinding).where(AccountBinding.uid == uid).limit(1)
        binding = (await get_scoped_session().execute(stmt)).scalar_one_or_none()
        if binding is None:
            return None
        return binding

    @staticmethod
    async def get(uid: int) -> "Optional[str]":
        binding = await AccountBinding._get_binding(uid)
        if binding is None:
            return None
        return binding.majsoul_name

    @staticmethod
    async def set(uid: int, majsoul_name: str):
        binding = await AccountBinding._get_binding(uid)
        if binding is None:
            binding = AccountBinding(uid=uid, majsoul_name=majsoul_name)
        get_scoped_session().add(binding)
        await get_scoped_session().commit()

    @staticmethod
    async def unset(uid: int):
        stmt = delete(AccountBinding).where(AccountBinding.uid == uid)
        await get_scoped_session().execute(stmt)
        await get_scoped_session().commit()
