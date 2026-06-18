"""Requirement (RFQ) request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateRequirementRequest(BaseModel):
    crop: str
    variety: str | None = None
    quantity_min_kg: float = Field(..., gt=0)
    quantity_max_kg: float = Field(..., gt=0)
    quality_grade: str | None = None
    quality_specs: dict | None = None
    price_type: str = "negotiable"
    offer_price_per_q: float | None = None
    delivery_location_id: str | None = None
    delivery_district: str | None = None
    delivery_by_date: datetime | None = None
    gst_invoice_required: bool = False
    allow_partial_match: bool = True
    urgency: str | None = None
    notes: str | None = None


class UpdateRequirementRequest(BaseModel):
    quantity_min_kg: float | None = None
    quantity_max_kg: float | None = None
    quality_grade: str | None = None
    quality_specs: dict | None = None
    offer_price_per_q: float | None = None
    delivery_by_date: datetime | None = None
    notes: str | None = None


class ExtendRequirementRequest(BaseModel):
    extend_days: int = Field(default=7, ge=1, le=14)


class RequirementResponse(BaseModel):
    id: str
    requirement_number: str
    buyer_id: str
    crop: str
    variety: str | None = None
    quantity_min_kg: float
    quantity_max_kg: float
    quality_grade: str | None = None
    price_type: str
    offer_price_per_q: float | None = None
    ai_suggested_price: float | None = None
    delivery_district: str | None = None
    gst_invoice_required: bool
    allow_partial_match: bool
    status: str
    offers_received: int = 0
    views_count: int = 0
    expires_at: str | None = None
    created_at: str | None = None
