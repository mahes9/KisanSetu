"""Seller profile schemas — Module 2 (stub)."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SellerProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    phone: str
    full_name: str
    kyc_status: str
    language: str
    trust_score: int


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    language: str | None = None
