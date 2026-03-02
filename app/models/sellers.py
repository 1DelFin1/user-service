from datetime import date
from uuid import uuid4, UUID

from sqlalchemy import String, Boolean, DateTime, Float, Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base
from app.models.mixins import TimestampMixin


class SellerModel(Base, TimestampMixin):
    __tablename__ = "sellers"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    birthday: Mapped[date] = mapped_column(DateTime)
    hashed_password: Mapped[str] = mapped_column(String)
    rating: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0")
    orders_count: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean)
