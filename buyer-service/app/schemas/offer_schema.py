"""Offer / negotiation request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CounterOfferRequest(BaseModel):
    counter_price_per_q: float = Field(..., gt=0)
    counter_quantity_kg: float | None = None
    notes: str | None = None


class OfferResponse(BaseModel):
    id: str
    requirement_id: str
    seller_id: str | None = None
    offer_price_per_q: float
    quantity_kg: float
    quality_grade: str | None = None
    round_number: int
    status: str
    counter_price_per_q: float | None = None
    counter_quantity_kg: float | None = None
    notes: str | None = None
    ai_suggestion: dict | None = None
    expires_at: str | None = None
    created_at: str | None = None


class AISuggestionResponse(BaseModel):
    suggested_price: float
    confidence: int
    reasoning: str | None = None
    market_context: dict | None = None
