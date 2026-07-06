"""Buyer registration and profile schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RegisterIndividualRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")
    individual_name: str = Field(..., min_length=2, max_length=100)
    language: str = Field(default="te", pattern=r"^(en|te)$")


class RegisterOrganizationRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")
    primary_email: str
    company_name: str = Field(..., min_length=2, max_length=200)
    business_type: str | None = None
    buyer_segment: str | None = None
    gstin: str | None = None
    pan_number: str | None = None
    password: str = Field(..., min_length=8)
    language: str = Field(default="en", pattern=r"^(en|te)$")


class VerifyPhoneRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\d{10}$")
    otp: str = Field(..., min_length=4, max_length=6)


class VerifyAadhaarRequest(BaseModel):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    otp: str = Field(..., min_length=4, max_length=6)


class VerifyGSTINRequest(BaseModel):
    gstin: str = Field(..., min_length=15, max_length=15)


class VerifyBankRequest(BaseModel):
    bank_account: str = Field(..., min_length=9, max_length=18)
    bank_ifsc: str = Field(..., pattern=r"^[A-Z]{4}0[A-Z0-9]{6}$")
    bank_holder_name: str = Field(..., min_length=2, max_length=100)


class VerifyUPIRequest(BaseModel):
    upi_id: str


class UpdateProfileRequest(BaseModel):
    individual_name: str | None = None
    company_name: str | None = None
    primary_email: str | None = None
    preferred_crops: list[str] | None = None
    default_quality_grade: str | None = None
    min_order_kg: int | None = None
    device_token: str | None = None
    device_platform: str | None = None
    app_version: str | None = None


class ChangeLanguageRequest(BaseModel):
    language: str = Field(..., pattern=r"^(en|te)$")


class BuyerProfileResponse(BaseModel):
    id: str
    buyer_number: str
    buyer_type: str
    language: str
    primary_phone: str
    primary_email: str | None = None
    individual_name: str | None = None
    company_name: str | None = None
    business_type: str | None = None
    buyer_segment: str | None = None
    gstin: str | None = None
    kyc_status: str
    trust_score: int
    orders_completed: int
    avg_rating: float = 0
    preferred_crops: list[str] | None = None
    default_quality_grade: str | None = None


class KYCStatusResponse(BaseModel):
    buyer_type: str
    kyc_status: str
    phone_verified: bool
    email_verified: bool
    aadhaar_verified: bool = False
    upi_verified: bool = False
    gstin_verified: bool = False
    bank_verified: bool = False
    next_step: str | None = None
