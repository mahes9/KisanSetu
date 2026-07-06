"""Thin controller for authentication."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.auth_service import AuthService


class AuthController:
    @staticmethod
    async def login_individual(phone: str, otp: str, db: AsyncSession) -> StandardResponse:
        svc = AuthService(db)
        data = await svc.login_individual(phone, otp)
        return StandardResponse(success=True, message="Login successful.", data=data)

    @staticmethod
    async def login_organization(email: str, password: str, db: AsyncSession) -> StandardResponse:
        svc = AuthService(db)
        data = await svc.login_organization(email, password)
        return StandardResponse(success=True, message="Login successful.", data=data)
