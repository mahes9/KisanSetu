"""Browse / discovery request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BrowseListingsParams(BaseModel):
    crop: str | None = None
    grade: str | None = None
    district: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_quantity: float | None = None
    max_quantity: float | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class ListingResponse(BaseModel):
    id: str
    listing_number: str | None = None
    seller_id: str | None = None
    crop: str
    quantity_kg: float
    grade: str | None = None
    ask_price_per_q: float
    district: str | None = None
    transport_type: str | None = None
    status: str
    expires_at: str | None = None
    created_at: str | None = None


class SavedSearchRequest(BaseModel):
    label: str = Field(..., max_length=100)
    filters: dict


class PriceAlertRequest(BaseModel):
    crop: str
    target_price_per_q: float
    district: str | None = None
    alert_type: str = "below"


class PreferredSellerRequest(BaseModel):
    notes: str | None = None
