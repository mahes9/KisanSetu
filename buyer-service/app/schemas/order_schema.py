"""Order management request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ConfirmDeliveryRequest(BaseModel):
    confirmation_code: str | None = None
    notes: str | None = None


class DisputeRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500)
    evidence_description: str | None = None


class RateSellerRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review: str | None = None


class OrderResponse(BaseModel):
    id: str
    requirement_id: str
    buyer_id: str
    seller_id: str | None = None
    offer_id: str | None = None
    crop: str
    quantity_kg: float
    price_per_q: float
    total_amount: float
    commission_amount: float
    status: str
    escrow_status: str | None = None
    delivery_confirmed_at: str | None = None
    disputed_at: str | None = None
    seller_rating: int | None = None
    created_at: str | None = None


class InvoiceResponse(BaseModel):
    order_id: str
    invoice_type: str
    buyer_name: str
    buyer_gstin: str | None = None
    seller_name: str | None = None
    crop: str
    quantity_kg: float
    price_per_q: float
    total_amount: float
    commission_amount: float
    tax_amount: float = 0
    net_amount: float
    created_at: str | None = None
