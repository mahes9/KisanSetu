"""Order management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_kyc_verified
from app.controllers.order_controller import OrderController
from app.db.database import get_db
from app.models.buyer import Buyer

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", summary="List my orders")
async def list_orders(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OrderController.list_orders(buyer, status, page, db)


@router.get("/{order_id}", summary="Get order detail")
async def get_order(
    order_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OrderController.get_order(order_id, buyer, db)


@router.post("/{order_id}/confirm-delivery", summary="Confirm delivery received")
async def confirm_delivery(
    order_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OrderController.confirm_delivery(order_id, buyer, {}, db)


@router.post("/{order_id}/dispute", summary="Raise a dispute")
async def raise_dispute(
    order_id: UUID,
    reason: str = Query(...),
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OrderController.raise_dispute(order_id, buyer, reason, db)


@router.post("/{order_id}/rate", summary="Rate an order")
async def rate_order(
    order_id: UUID,
    rating: int = Query(..., ge=1, le=5),
    review: str | None = Query(None),
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OrderController.rate_order(order_id, buyer, rating, review, db)
