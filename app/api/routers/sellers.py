from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.api.deps import SessionDep, get_current_active_auth_seller
from app.exceptions import SELLER_NOT_FOUND_EXCEPTION
from app.schemas import SellerCreateSchema, SellerUpdateSchema, SellerInDBSchema, SellerOutSchema
from app.services import SellerService


sellers_router = APIRouter(prefix="/sellers", tags=["sellers"])


@sellers_router.get("/me")
async def get_current_user(
    user_data: SellerInDBSchema = Depends(get_current_active_auth_seller),
):
    return user_data


@sellers_router.post("/me/photo", response_model=SellerOutSchema)
async def upload_current_seller_photo(
    session: SessionDep,
    file: UploadFile = File(...),
    user_data: SellerInDBSchema = Depends(get_current_active_auth_seller),
):
    return await SellerService.upload_seller_photo(session, user_data.id, file)


@sellers_router.post("")
async def create_seller(session: SessionDep, seller_data: SellerCreateSchema):
    return await SellerService.create_seller(session, seller_data)


@sellers_router.get("/{seller_id}")
async def get_seller_by_id(session: SessionDep, seller_id: UUID):
    seller = await SellerService.get_seller_by_id(session, seller_id)
    if seller is None:
        raise SELLER_NOT_FOUND_EXCEPTION
    return seller


@sellers_router.get("/{email}")
async def get_seller_by_email(session: SessionDep, email: str):
    return await SellerService.get_seller_by_email(session, email)


@sellers_router.patch("/{seller_id}")
async def update_seller(
    session: SessionDep, seller_data: SellerUpdateSchema, seller_id: UUID
):
    return await SellerService.update_seller(session, seller_data, seller_id)


@sellers_router.delete("/{seller_id}")
async def delete_seller(session: SessionDep, seller_id: UUID):
    return await SellerService.delete_seller(session, seller_id)
