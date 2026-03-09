from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=50)
    birthday: date | None = None
    is_active: bool = True
    is_superuser: bool = False


class UserCreateSchema(UserBaseSchema):
    password: str = Field(max_length=40)


class UserUpdateSchema(BaseModel):
    email: str | None = None
    name: str | None = None
    birthday: date | None = None
    password: str | None = None


class UserOutSchema(UserBaseSchema):
    id: UUID
    photo_url: str | None = None

    class Config:
        from_attributes = True


class UserInDBSchema(UserBaseSchema):
    id: UUID
    photo_url: str | None = None
    hashed_password: str


class SellerBaseSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=50)
    birthday: date | None = None
    rating: float = 0.0
    orders_count: int = 0
    is_active: bool = True


class SellerCreateSchema(SellerBaseSchema):
    password: str = Field(max_length=40)


class SellerUpdateSchema(BaseModel):
    email: str | None = None
    name: str | None = None
    birthday: date | None = None
    rating: float | None = None
    orders_count: int | None = None
    password: str | None = None


class SellerOutSchema(SellerBaseSchema):
    id: UUID
    photo_url: str | None = None

    class Config:
        from_attributes = True


class SellerInDBSchema(SellerBaseSchema):
    id: UUID
    photo_url: str | None = None
    hashed_password: str
