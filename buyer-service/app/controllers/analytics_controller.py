"""Thin controller for buyer analytics."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.analytics_service import AnalyticsService


class AnalyticsController:
    @staticmethod
    async def get_dashboard(buyer, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_dashboard(buyer.id, buyer.buyer_type)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_spend_trends(buyer, period: str, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_spend_trends(buyer.id, period)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_vendor_performance(buyer, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_vendor_performance(buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_gst_summary(buyer, db: AsyncSession) -> StandardResponse:
        svc = AnalyticsService(db)
        data = await svc.get_gst_summary(buyer.id)
        return StandardResponse(success=True, data=data)
