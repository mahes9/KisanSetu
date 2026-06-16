"""Auth schemas — Module 1 (stub)."""

from pydantic import BaseModel


class SendOtpRequest(BaseModel):
    phone: str


class VerifyOtpRequest(BaseModel):
    otp_session_id: str
    otp: str


class RegisterSellerRequest(BaseModel):
    phone: str
    full_name: str
    aadhaar_number: str


class LoginResponse(BaseModel):
    token: str
    seller_id: str
    full_name: str
