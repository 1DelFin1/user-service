from typing import Annotated, AsyncGenerator
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import JWTAuthenticator
from app.core.database import async_session_factory
from app.exceptions import (
    USER_NOT_FOUND_EXCEPTION,
    SELLER_NOT_FOUND_EXCEPTION,
    USER_UNAUTHORIZED_EXCEPTION,
    INVALID_TOKEN_EXCEPTION,
)
from app.services import UserService, SellerService


async def get_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def _get_current_active_auth_account(
    request: Request,
    session: SessionDep,
    expected_account_type: str,
):
    token = request.cookies.get("token")
    if not token:
        raise USER_UNAUTHORIZED_EXCEPTION

    try:
        payload = JWTAuthenticator.decode_jwt_token(token)
    except InvalidTokenError:
        raise INVALID_TOKEN_EXCEPTION

    account_type = payload.get("account_type")
    email = payload.get("email")
    if not email:
        raise INVALID_TOKEN_EXCEPTION

    if account_type and account_type != expected_account_type:
        raise USER_UNAUTHORIZED_EXCEPTION

    if expected_account_type == "user":
        account = await UserService.get_user_by_email(session, email)
        if not account:
            raise USER_NOT_FOUND_EXCEPTION
        return account

    account = await SellerService.get_seller_by_email(session, email)
    if not account:
        raise SELLER_NOT_FOUND_EXCEPTION

    return account


async def get_current_active_auth_user(request: Request, session: SessionDep):
    return await _get_current_active_auth_account(request, session, "user")


async def get_current_active_auth_seller(request: Request, session: SessionDep):
    return await _get_current_active_auth_account(request, session, "seller")
