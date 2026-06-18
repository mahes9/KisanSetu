"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import AuthController
from app.db.database import get_db
from app.schemas.auth_schema import IndividualLoginRequest, OrganizationLoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login/individual", summary="Login with phone + OTP")
async def login_individual(
    body: IndividualLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.login_individual(body.phone, body.otp, db)


@router.post("/login/organization", summary="Login with email + password")
async def login_organization(
    body: OrganizationLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await AuthController.login_organization(body.email, body.password, db)
