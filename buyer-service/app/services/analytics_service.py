"""Buyer analytics service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.requirement_repo import RequirementRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.req_repo = RequirementRepository(session)

    async def get_dashboard(self, buyer_id: UUID, buyer_type: str) -> dict:
        active_count = await self.req_repo.count_active_by_buyer(buyer_id)
        return {
            "total_spent": 0,
            "orders_completed": 0,
            "active_requirements": active_count,
            "pending_deliveries": 0,
            "avg_price_paid": None,
            "top_crops": [],
            "recent_orders": [],
        }

    async def get_spend_trends(self, buyer_id: UUID, period: str = "monthly") -> dict:
        return {"period": period, "data": []}

    async def get_vendor_performance(self, buyer_id: UUID) -> dict:
        return {"vendors": [], "total_vendors": 0}

    async def get_gst_summary(self, buyer_id: UUID, period: str = "monthly") -> dict:
        return {"period": period, "total_gst_paid": 0, "invoices": []}
