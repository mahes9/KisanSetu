"""Farm schemas — Module 2 (stub)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FarmCreate(BaseModel):
    gps_latitude: float
    gps_longitude: float
    district: str
    village: str | None = None
    acreage: float | None = None
    irrigation_type: str | None = None
    soil_type: str | None = None


class FarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    district: str
    village: str | None = None
    acreage: float | None = None


class BankVerifyRequest(BaseModel):
    bank_account: str
    bank_ifsc: str
    account_holder_name: str
