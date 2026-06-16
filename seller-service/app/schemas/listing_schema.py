"""Pydantic schemas for the Listing module — Module 5."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PublishRequest(BaseModel):
    ask_price_per_q: float
    confirm_floor_check: bool = True
    confirm_grade: bool = True


class EditPriceRequest(BaseModel):
    new_price_per_q: float
    reason: str | None = None


class CancelListingRequest(BaseModel):
    reason: str


class ListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    seller_id: UUID
    listing_number: str
    crop: str
    quantity_kg: float
    harvest_status: str | None = None
    grade: str
    ai_grade_locked: bool = True
    ai_confidence: int | None = None
    ask_price_per_q: float
    floor_price_at_publish: float
    modal_price_at_publish: float
    transport_type: str | None = None
    pickup_window: str | None = None
    pickup_date: date | None = None
    status: str
    price_edit_count: int = 0
    expires_at: datetime
    views_count: int = 0
    enquiries_count: int = 0
    created_at: datetime | None = None
    payout_preview: dict | None = None
    days_remaining: int | None = None
    can_edit_price: bool = True


class PublicListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    listing_number: str
    crop: str
    quantity_kg: float
    grade: str
    ask_price_per_q: float
    harvest_status: str | None = None
    transport_type: str | None = None
    pickup_window: str | None = None
    status: str
    expires_at: datetime
    views_count: int = 0
    created_at: datetime | None = None


class ListingListResponse(BaseModel):
    listings: list[ListingResponse] = []
    total: int = 0
    page: int = 1
    per_page: int = 20
