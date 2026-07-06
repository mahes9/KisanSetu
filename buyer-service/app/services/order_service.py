"""Order management service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import RFQConfig
from app.core.exceptions import (
    DisputeWindowExpiredError,
    OrderNotFoundError,
)
from app.core.state_machine import transition_order


class OrderService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_order(self, order_id: UUID, buyer_id: UUID) -> dict:
        return {"id": str(order_id), "status": "stub"}

    async def list_orders(self, buyer_id: UUID, status: str | None = None, page: int = 1) -> dict:
        return {"orders": [], "total": 0, "page": page}

    async def confirm_delivery(self, order_id: UUID, buyer_id: UUID, data: dict) -> dict:
        return {"id": str(order_id), "status": "delivered"}

    async def raise_dispute(self, order_id: UUID, buyer_id: UUID, reason: str) -> dict:
        return {"id": str(order_id), "status": "disputed", "reason": reason}

    async def rate_order(self, order_id: UUID, buyer_id: UUID, rating: int, review: str | None = None) -> dict:
        return {"id": str(order_id), "rating": rating, "review": review}
