"""Auth request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CheckPhoneRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")


class CheckPhoneResponse(BaseModel):
    exists: bool
    buyer_type: str | None = None


class IndividualLoginRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")
    otp: str = Field(..., min_length=4, max_length=6)


class OrganizationLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    buyer_id: str
    buyer_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
