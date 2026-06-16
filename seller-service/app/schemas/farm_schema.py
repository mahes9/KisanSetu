"""Farm schemas — Module 2.

Farm data is owned by the Farmer Service. These schemas represent
the data as fetched and returned by the seller-service endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FarmDetail(BaseModel):
    """Single farm as returned by the Farmer Service."""

    model_config = ConfigDict(from_attributes=True)

    farm_id: str
    farm_name: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    district: str | None = None
    village: str | None = None
    acreage: float | None = None
    irrigation_type: str | None = None
    soil_type: str | None = None
    crops_grown: list[str] = Field(default_factory=list)


class BankStatus(BaseModel):
    """Bank/UPI verification status from Farmer Service."""

    bank_verified: bool = False
    upi_id: str | None = None
    upi_verified: bool = False
    bank_account: str | None = None
    bank_ifsc: str | None = None


class FarmerProfileResponse(BaseModel):
    """Complete farmer profile with farms and bank status."""

    farmer_id: str
    full_name: str
    phone: str
    farms: list[FarmDetail] = Field(default_factory=list)
    bank_status: BankStatus
    farm_count: int = 0
    has_verified_bank: bool = False
    has_farm_in_phase1_district: bool = False
