"""Listing publish & management controller — Module 5."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.listing_service import ListingService


class ListingController:
    @staticmethod
    async def publish_listing(
        draft_id: UUID, publish_data: dict, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.publish_from_draft(draft_id, seller.id, publish_data)
        return StandardResponse(success=True, message="Listing published!", data=data)

    @staticmethod
    async def get_listing(
        listing_id: UUID, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.get_listing(listing_id, seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def list_my_listings(
        seller, db: AsyncSession, page: int = 1, per_page: int = 20, status_filter: str | None = None
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.list_my_listings(seller.id, page, per_page, status_filter)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def edit_price(
        listing_id: UUID, new_price: float, seller, db: AsyncSession, reason: str | None = None
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.edit_price(listing_id, seller.id, new_price, reason)
        return StandardResponse(success=True, message="Price updated.", data=data)

    @staticmethod
    async def pause_listing(listing_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.pause_listing(listing_id, seller.id)
        return StandardResponse(success=True, message="Listing paused.", data=data)

    @staticmethod
    async def resume_listing(listing_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.resume_listing(listing_id, seller.id)
        return StandardResponse(success=True, message="Listing resumed.", data=data)

    @staticmethod
    async def cancel_listing(
        listing_id: UUID, reason: str, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.cancel_listing(listing_id, seller.id, reason)
        return StandardResponse(success=True, message="Listing cancelled.", data=data)

    @staticmethod
    async def browse_public_listings(
        db: AsyncSession,
        crop: str | None = None,
        district: str | None = None,
        min_qty: float | None = None,
        max_price: float | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.browse_public_listings(crop, district, min_qty, max_price, page, per_page)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_public_listing(listing_id: UUID, db: AsyncSession) -> StandardResponse:
        svc = ListingService(db)
        data = await svc.get_public_listing(listing_id)
        return StandardResponse(success=True, data=data)
