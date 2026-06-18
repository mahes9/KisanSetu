"""Thin controller for order management."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.order_service import OrderService


class OrderController:
    @staticmethod
    async def get_order(order_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = OrderService(db)
        data = await svc.get_order(order_id, buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def list_orders(buyer, status: str | None, page: int, db: AsyncSession) -> StandardResponse:
        svc = OrderService(db)
        data = await svc.list_orders(buyer.id, status, page)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def confirm_delivery(order_id: UUID, buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = OrderService(db)
        result = await svc.confirm_delivery(order_id, buyer.id, data)
        return StandardResponse(success=True, message="Delivery confirmed.", data=result)

    @staticmethod
    async def raise_dispute(order_id: UUID, buyer, reason: str, db: AsyncSession) -> StandardResponse:
        svc = OrderService(db)
        data = await svc.raise_dispute(order_id, buyer.id, reason)
        return StandardResponse(success=True, message="Dispute raised.", data=data)

    @staticmethod
    async def rate_order(order_id: UUID, buyer, rating: int, review: str | None, db: AsyncSession) -> StandardResponse:
        svc = OrderService(db)
        data = await svc.rate_order(order_id, buyer.id, rating, review)
        return StandardResponse(success=True, message="Rating submitted.", data=data)
