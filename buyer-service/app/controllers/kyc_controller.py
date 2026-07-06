"""Thin controller for KYC verification."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.kyc_service import KYCService


class KYCController:
    @staticmethod
    async def verify_phone(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = KYCService(db)
        result = await svc.verify_phone(buyer.id, data["phone"], data["otp"])
        return StandardResponse(success=True, message="Phone verified.", data=result)

    @staticmethod
    async def verify_aadhaar(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = KYCService(db)
        result = await svc.verify_aadhaar(buyer.id, data["aadhaar_number"], data["otp"])
        return StandardResponse(success=True, message="Aadhaar verified.", data=result)

    @staticmethod
    async def verify_gstin(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = KYCService(db)
        result = await svc.verify_gstin(buyer.id, data["gstin"])
        return StandardResponse(success=True, message="GSTIN verified.", data=result)

    @staticmethod
    async def verify_bank(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = KYCService(db)
        result = await svc.verify_bank(buyer.id, data["account"], data["ifsc"], data["holder_name"])
        return StandardResponse(success=True, message="Bank account verified.", data=result)

    @staticmethod
    async def verify_upi(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = KYCService(db)
        result = await svc.verify_upi(buyer.id, data["upi_id"])
        return StandardResponse(success=True, message="UPI verified.", data=result)
