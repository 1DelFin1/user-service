import logging
from urllib.parse import urlparse
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.exceptions import SELLER_NOT_FOUND_EXCEPTION, SELLER_ALREADY_EXIST_EXCEPTION
from app.models.sellers import SellerModel
from app.schemas import SellerCreateSchema, SellerUpdateSchema
from app.services.base_account_service import BaseAccountService
from app.services.minio_service import MinioService


logger = logging.getLogger(__name__)


class SellerService(BaseAccountService):
    model = SellerModel
    not_found_exception = SELLER_NOT_FOUND_EXCEPTION
    already_exists_exception = SELLER_ALREADY_EXIST_EXCEPTION

    @staticmethod
    def _resolve_image_extension(filename: str, content_type: str) -> str:
        if "." in filename:
            extension = filename.rsplit(".", 1)[-1].lower().strip()
            if extension:
                return extension

        content_type_to_extension = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/bmp": "bmp",
        }
        return content_type_to_extension.get(content_type, "bin")

    @staticmethod
    def _extract_object_key_from_public_url(
        photo_url: str,
        *,
        bucket_name: str,
    ) -> str | None:
        parsed = urlparse(photo_url)
        path = parsed.path.lstrip("/")
        bucket_prefix = f"{bucket_name}/"
        if not path.startswith(bucket_prefix):
            return None
        object_key = path[len(bucket_prefix):]
        return object_key or None

    @classmethod
    async def get_seller_by_id(
        cls,
        session: AsyncSession,
        seller_id: UUID,
        refresh_metrics: bool = True,
    ) -> SellerModel | None:
        seller = await cls.get_by_id(session, seller_id)
        if seller is None:
            return None
        if refresh_metrics:
            await cls.sync_metrics(session, seller)
        return seller

    @classmethod
    async def get_seller_by_email(
        cls,
        session: AsyncSession,
        email: str,
        refresh_metrics: bool = False,
    ) -> SellerModel | None:
        seller = await cls.get_by_email(session, email)
        if seller is None:
            return None
        if refresh_metrics:
            await cls.sync_metrics(session, seller)
        return seller

    @staticmethod
    async def _fetch_seller_product_ratings(seller_id: UUID) -> list[float] | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.NGINX_URL}/products",
                    params={"seller_id": str(seller_id)},
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                response.raise_for_status()
                payload = response.json()
        except Exception:
            logger.exception("Failed to fetch seller products for rating: seller_id=%s", seller_id)
            return None

        if not isinstance(payload, list):
            return []

        ratings: list[float] = []
        for item in payload:
            if not isinstance(item, dict):
                continue

            total_reviews_value = item.get("total_reviews")
            if total_reviews_value is None:
                total_reviews_value = item.get("totalReviews")

            total_reviews: int | None = None
            if isinstance(total_reviews_value, int):
                total_reviews = total_reviews_value
            elif isinstance(total_reviews_value, str):
                try:
                    total_reviews = int(total_reviews_value)
                except ValueError:
                    total_reviews = None

            # Seller rating should include only products that already have reviews.
            if total_reviews is None or total_reviews <= 0:
                continue

            rating_value = item.get("rating")
            if isinstance(rating_value, (int, float)):
                ratings.append(float(rating_value))
            elif isinstance(rating_value, str):
                try:
                    ratings.append(float(rating_value))
                except ValueError:
                    continue
        return ratings

    @staticmethod
    async def _fetch_seller_orders_count(seller_id: UUID) -> int | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.NGINX_URL}/orders/sellers/{seller_id}/count",
                    headers={"Content-Type": "application/json"},
                    timeout=10,
                )
                response.raise_for_status()
                payload = response.json()
        except Exception:
            logger.exception("Failed to fetch seller orders count: seller_id=%s", seller_id)
            return None

        if not isinstance(payload, dict):
            return 0

        orders_count = payload.get("orders_count")
        if isinstance(orders_count, int):
            return max(orders_count, 0)
        if isinstance(orders_count, str) and orders_count.isdigit():
            return int(orders_count)
        return 0

    @classmethod
    async def sync_metrics(cls, session: AsyncSession, seller: SellerModel) -> SellerModel:
        ratings = await cls._fetch_seller_product_ratings(seller.id)
        orders_count = await cls._fetch_seller_orders_count(seller.id)

        next_rating = seller.rating
        next_orders_count = seller.orders_count

        if ratings is not None:
            normalized_ratings = [
                1.0 if abs(rating) < 1e-9 else rating
                for rating in ratings
            ]
            next_rating = (
                round(sum(normalized_ratings) / len(normalized_ratings), 2)
                if normalized_ratings
                else 0.0
            )
        if orders_count is not None:
            next_orders_count = orders_count

        rating_changed = abs((seller.rating or 0.0) - next_rating) > 1e-9
        orders_count_changed = (seller.orders_count or 0) != next_orders_count

        if rating_changed or orders_count_changed:
            seller.rating = next_rating
            seller.orders_count = next_orders_count
            session.add(seller)
            await session.commit()
            await session.refresh(seller)

        return seller

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

    @classmethod
    async def upload_seller_photo(
        cls,
        session: AsyncSession,
        seller_id: UUID,
        file: UploadFile,
    ) -> SellerModel:
        seller = await cls.get_seller_by_id(session, seller_id)
        if seller is None:
            raise SELLER_NOT_FOUND_EXCEPTION

        content_type = file.content_type or "application/octet-stream"
        if not content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed",
            )

        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty",
            )

        minio_service = MinioService()
        file_extension = cls._resolve_image_extension(file.filename or "", content_type)
        object_key = f"sellers/{seller_id}/avatar_{uuid4()}.{file_extension}"
        photo_url = minio_service.upload_file(
            file_data=file_data,
            filename=object_key,
            content_type=content_type,
        )

        previous_photo_url = seller.photo_url.strip() if isinstance(seller.photo_url, str) else None
        seller.photo_url = photo_url
        session.add(seller)
        await session.commit()
        await session.refresh(seller)

        if previous_photo_url:
            previous_object_key = cls._extract_object_key_from_public_url(
                previous_photo_url,
                bucket_name=minio_service.bucket_name,
            )
            if previous_object_key and previous_object_key != object_key:
                try:
                    minio_service.delete_file(previous_object_key)
                except HTTPException:
                    pass

        return seller
