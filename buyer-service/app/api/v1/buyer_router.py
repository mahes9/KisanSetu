"""Buyer registration and profile endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.buyer_controller import BuyerController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_schema import (
    ChangeLanguageRequest,
    RegisterIndividualRequest,
    RegisterOrganizationRequest,
    UpdateProfileRequest,
)

router = APIRouter(prefix="/buyers", tags=["Buyers"])


@router.post("/register/individual", summary="Register individual buyer")
async def register_individual(
    body: RegisterIndividualRequest,
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.register_individual(body.model_dump(), db)


@router.post("/register/organization", summary="Register organization buyer")
async def register_organization(
    body: RegisterOrganizationRequest,
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.register_organization(body.model_dump(), db)


@router.get("/me", summary="Get my profile")
async def get_profile(
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.get_profile(buyer, db)


@router.patch("/me", summary="Update my profile")
async def update_profile(
    body: UpdateProfileRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.update_profile(buyer, body.model_dump(exclude_unset=True), db)


@router.put("/me/language", summary="Change language preference")
async def change_language(
    body: ChangeLanguageRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.change_language(buyer, body.language, db)


@router.get("/me/kyc", summary="Get KYC status")
async def get_kyc_status(
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BuyerController.get_kyc_status(buyer, db)
