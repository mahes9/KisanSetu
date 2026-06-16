"""Analytics controller — Module 6."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.analytics_service import AnalyticsService


class AnalyticsController:
    @staticmethod
    async def get_season_summary(
        seller, db: AsyncSession, season: str | None = None, year: int | None = None
    ) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_season_summary(seller.id, season, year)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_earnings_history(seller, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_earnings_history(seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def compare_with_mandi(
        seller, db: AsyncSession, crop: str | None = None
    ) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.compare_with_mandi(seller.id, crop)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_listing_analytics(
        listing_id: UUID, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_listing_analytics(listing_id, seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_dashboard(seller, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_dashboard(seller.id)
        return StandardResponse(success=True, data=data)
