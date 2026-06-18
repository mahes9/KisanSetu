"""KYC verification endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.kyc_controller import KYCController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.buyer_schema import (
    VerifyAadhaarRequest,
    VerifyBankRequest,
    VerifyGSTINRequest,
    VerifyPhoneRequest,
    VerifyUPIRequest,
)

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.post("/verify/phone", summary="Verify phone with OTP")
async def verify_phone(
    body: VerifyPhoneRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await KYCController.verify_phone(buyer, body.model_dump(), db)


@router.post("/verify/aadhaar", summary="Verify Aadhaar")
async def verify_aadhaar(
    body: VerifyAadhaarRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await KYCController.verify_aadhaar(buyer, body.model_dump(), db)


@router.post("/verify/gstin", summary="Verify GSTIN")
async def verify_gstin(
    body: VerifyGSTINRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await KYCController.verify_gstin(buyer, body.model_dump(), db)


@router.post("/verify/bank", summary="Verify bank account")
async def verify_bank(
    body: VerifyBankRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await KYCController.verify_bank(
        buyer,
        {"account": body.bank_account, "ifsc": body.bank_ifsc, "holder_name": body.bank_holder_name},
        db,
    )


@router.post("/verify/upi", summary="Verify UPI VPA")
async def verify_upi(
    body: VerifyUPIRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await KYCController.verify_upi(buyer, body.model_dump(), db)
