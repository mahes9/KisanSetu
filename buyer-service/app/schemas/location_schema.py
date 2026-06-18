"""Delivery location request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CreateLocationRequest(BaseModel):
    label: str = Field(default="default", max_length=50)
    address_line1: str = Field(..., max_length=255)
    address_line2: str | None = None
    village: str | None = None
    mandal: str | None = None
    district: str
    state: str = "Andhra Pradesh"
    pincode: str = Field(..., pattern=r"^\d{6}$")
    gps_lat: float | None = None
    gps_lon: float | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    notes: str | None = None


class UpdateLocationRequest(BaseModel):
    label: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    village: str | None = None
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    gps_lat: float | None = None
    gps_lon: float | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    notes: str | None = None


class LocationResponse(BaseModel):
    id: str
    buyer_id: str
    label: str
    address_line1: str
    address_line2: str | None = None
    village: str | None = None
    mandal: str | None = None
    district: str
    state: str
    pincode: str
    gps_lat: float | None = None
    gps_lon: float | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    is_default: bool
    notes: str | None = None
