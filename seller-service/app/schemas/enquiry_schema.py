"""Enquiry request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateEnquiryRequest(BaseModel):
    buyer_id: str
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_district: Optional[str] = None
    quantity_kg: float = Field(..., gt=0)
    offered_price_per_q: Optional[float] = Field(None, gt=0)
    delivery_district: Optional[str] = None
    delivery_pincode: Optional[str] = None
    required_by_date: Optional[datetime] = None
    payment_mode: Optional[str] = Field(None, description="cash, upi, credit, bank_transfer")
    message: Optional[str] = Field(None, max_length=500)


class SellerRespondRequest(BaseModel):
    quoted_price_per_q: float = Field(..., gt=0)
    available_quantity_kg: Optional[float] = Field(None, gt=0)
    delivery_within_days: Optional[int] = Field(None, ge=1)
    message: Optional[str] = Field(None, max_length=500)


class BuyerCounterRequest(BaseModel):
    buyer_id: str
    offered_price_per_q: float = Field(..., gt=0)
    quantity_kg: Optional[float] = Field(None, gt=0)
    message: Optional[str] = Field(None, max_length=500)
