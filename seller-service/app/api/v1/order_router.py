"""Order & commission endpoints — escrow, OTP, invoice, disputes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_seller
from app.db.database import get_db
from app.models.seller import Seller
from app.schemas.common_schema import StandardResponse
from app.services.order_service import OrderService

router = APIRouter(tags=["Orders"])


# ── Request schemas ──

class DisputeRequest(BaseModel):
    raised_by: str  # "buyer" or "seller"
    raiser_id: str
    reason: str
    evidence_url: str | None = None


class ResolveDisputeRequest(BaseModel):
    resolution: str
    action: str  # "release_to_seller", "refund_buyer", "partial_release"


class CancelRequest(BaseModel):
    cancelled_by: str  # "buyer" or "seller"
    canceller_id: str
    reason: str


# ── Seller endpoints ──

@router.get("/orders/my", summary="Get seller's orders")
async def get_seller_orders(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    data = await svc.get_orders_for_seller(seller.id, status, page, per_page)
    return StandardResponse(success=True, data=data)


@router.post("/orders/{order_id}/dispatch", summary="Mark order dispatched")
async def mark_dispatched(
    order_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.mark_dispatched(order_id, seller.id)
    return StandardResponse(success=True, message="Order dispatched.", data=svc._to_dict(order, viewer="seller"))


@router.post("/orders/{order_id}/deliver", summary="Mark order delivered")
async def mark_delivered(
    order_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.mark_delivered(order_id, seller.id)
    return StandardResponse(success=True, message="Order delivered.", data=svc._to_dict(order, viewer="seller"))


# ── Buyer endpoints (no seller auth) ──

@router.get("/orders/buyer/{buyer_id}", summary="Get orders for a buyer")
async def get_buyer_orders(
    buyer_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    data = await svc.get_orders_for_buyer(buyer_id, page, per_page)
    return StandardResponse(success=True, data=data)


@router.post("/orders/{order_id}/escrow-pay", summary="Buyer pays into escrow")
async def escrow_pay(
    order_id: UUID,
    buyer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.escrow_pay(order_id, buyer_id)
    return StandardResponse(
        success=True,
        message="Payment received. Escrow held. Delivery OTP generated.",
        data=svc._to_dict(order, viewer="buyer"),
    )


@router.post("/orders/{order_id}/confirm-delivery", summary="Buyer confirms with OTP")
async def confirm_delivery(
    order_id: UUID,
    buyer_id: str = Query(...),
    otp: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.confirm_delivery_with_otp(order_id, buyer_id, otp)
    return StandardResponse(
        success=True,
        message="Delivery confirmed! Payment released to seller. Invoice generated.",
        data=svc._to_dict(order, viewer="buyer"),
    )


@router.post("/orders/{order_id}/cancel", summary="Cancel order (before dispatch)")
async def cancel_order(
    order_id: UUID,
    body: CancelRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.cancel_order(order_id, body.cancelled_by, body.canceller_id, body.reason)
    return StandardResponse(success=True, message="Order cancelled. Escrow refunded if paid.", data=svc._to_dict(order, viewer=body.cancelled_by))


# ── Dispute endpoints ──

@router.post("/orders/{order_id}/dispute", summary="Raise a dispute")
async def raise_dispute(
    order_id: UUID,
    body: DisputeRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.raise_dispute(order_id, body.raised_by, body.raiser_id, body.reason, body.evidence_url)
    return StandardResponse(success=True, message="Dispute raised. Escrow frozen until resolved.", data=svc._to_dict(order, viewer=body.raised_by))


@router.post("/orders/{order_id}/resolve-dispute", summary="Platform resolves dispute")
async def resolve_dispute(
    order_id: UUID,
    body: ResolveDisputeRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    order = await svc.resolve_dispute(order_id, body.resolution, body.action)
    return StandardResponse(success=True, message=f"Dispute resolved: {body.action}.", data=svc._to_dict(order, viewer="platform"))


# ── Invoice ──

@router.get("/orders/{order_id}/invoice", summary="Get platform invoice")
async def get_invoice(
    order_id: UUID,
    requester_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    invoice = await svc.get_invoice(order_id, requester_id)
    return StandardResponse(success=True, data=invoice)


# ── Platform dashboard ──

@router.get("/platform/revenue", summary="Platform revenue dashboard")
async def platform_revenue(
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    data = await svc.get_platform_revenue()
    return StandardResponse(success=True, data=data)
