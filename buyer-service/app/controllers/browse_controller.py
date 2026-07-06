"""Thin controller for browse and discovery."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.browse_service import BrowseService


class BrowseController:
    @staticmethod
    async def browse_listings(filters: dict, db: AsyncSession) -> StandardResponse:
        svc = BrowseService(db)
        data = await svc.browse_listings(filters)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_listing(listing_id: str, db: AsyncSession) -> StandardResponse:
        svc = BrowseService(db)
        data = await svc.get_listing(listing_id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def save_search(buyer, label: str, filters: dict, db: AsyncSession) -> StandardResponse:
        svc = BrowseService(db)
        data = await svc.save_search(buyer.id, label, filters)
        return StandardResponse(success=True, message="Search saved.", data=data)

    @staticmethod
    async def add_preferred_seller(buyer, seller_id: UUID, notes: str | None, db: AsyncSession) -> StandardResponse:
        svc = BrowseService(db)
        data = await svc.add_preferred_seller(buyer.id, seller_id, notes)
        return StandardResponse(success=True, message="Seller added to preferred.", data=data)

    @staticmethod
    async def create_price_alert(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = BrowseService(db)
        result = await svc.create_price_alert(buyer.id, data)
        return StandardResponse(success=True, message="Price alert created.", data=result)
