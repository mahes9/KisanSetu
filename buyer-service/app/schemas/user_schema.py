"""Org user management request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InviteUserRequest(BaseModel):
    email: str
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str | None = None
    role: str = Field(default="viewer", pattern=r"^(admin|buyer|finance|viewer)$")


class AcceptInvitationRequest(BaseModel):
    invitation_token: str
    password: str = Field(..., min_length=8)


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern=r"^(admin|buyer|finance|viewer)$")


class BuyerUserResponse(BaseModel):
    id: str
    buyer_id: str
    email: str
    full_name: str
    phone: str | None = None
    role: str
    is_active: bool
    invitation_accepted: bool
    last_login_at: str | None = None
    created_at: str | None = None
