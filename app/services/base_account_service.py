from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash


class BaseAccountService:
    model = None
    not_found_exception: HTTPException
    already_exists_exception: HTTPException

    @classmethod
    async def get_by_id(cls, session: AsyncSession, account_id: UUID):
        stmt = select(cls.model).where(cls.model.id == account_id)
        return await session.scalar(stmt)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str):
        stmt = select(cls.model).where(cls.model.email == email)
        return await session.scalar(stmt)

    @classmethod
    async def create(cls, session: AsyncSession, account_data: Any):
        if await cls.get_by_email(session, account_data.email):
            raise cls.already_exists_exception

        data = account_data.model_dump(exclude={"password"})
        data["hashed_password"] = get_password_hash(account_data.password)
        new_account = cls.model(**data)
        session.add(new_account)

        await session.commit()
        return {"ok": True}

    @classmethod
    async def update(cls, session: AsyncSession, account_data: Any, account_id: UUID):
        account = await cls.get_by_id(session, account_id)
        if account is None:
            raise cls.not_found_exception

        update_data = account_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(account_data.password)
            del update_data["password"]
        for key, value in update_data.items():
            if value != "":
                setattr(account, key, value)

        session.add(account)
        await session.commit()
        await session.refresh(account)
        return {"ok": True}

    @classmethod
    async def delete(cls, session: AsyncSession, account_id: UUID):
        account = await cls.get_by_id(session, account_id)
        if account is None:
            raise cls.not_found_exception

        await session.delete(account)
        await session.commit()
        return {"ok": True}
