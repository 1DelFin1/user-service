from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import SELLER_NOT_FOUND_EXCEPTION, SELLER_ALREADY_EXIST_EXCEPTION
from app.models.sellers import SellerModel
from app.schemas import SellerCreateSchema, SellerUpdateSchema
from app.services.base_account_service import BaseAccountService


class SellerService(BaseAccountService):
    model = SellerModel
    not_found_exception = SELLER_NOT_FOUND_EXCEPTION
    already_exists_exception = SELLER_ALREADY_EXIST_EXCEPTION

    @classmethod
    async def get_seller_by_id(
        cls, session: AsyncSession, seller_id: UUID
    ) -> SellerModel | None:
        return await cls.get_by_id(session, seller_id)

    @classmethod
    async def get_seller_by_email(
        cls, session: AsyncSession, email: str
    ) -> SellerModel | None:
        return await cls.get_by_email(session, email)

    @classmethod
    async def create_seller(
        cls, session: AsyncSession, seller_data: SellerCreateSchema
    ):
        return await cls.create(session, seller_data)

    @classmethod
    async def update_seller(
        cls, session: AsyncSession, seller_data: SellerUpdateSchema, seller_id: UUID
    ):
        return await cls.update(session, seller_data, seller_id)

    @classmethod
    async def delete_seller(cls, session: AsyncSession, seller_id: UUID):
        return await cls.delete(session, seller_id)
