"""Thin controller for buyer registration and profile."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.buyer_service import BuyerService


class BuyerController:
    @staticmethod
    async def register_individual(data: dict, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        result = await svc.register_individual(data)
        return StandardResponse(success=True, message="Registration successful.", data=result)

    @staticmethod
    async def register_organization(data: dict, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        result = await svc.register_organization(data)
        return StandardResponse(success=True, message="Organization registered.", data=result)

    @staticmethod
    async def get_profile(buyer, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        data = await svc.get_profile(buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def update_profile(buyer, updates: dict, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        data = await svc.update_profile(buyer.id, updates)
        return StandardResponse(success=True, message="Profile updated.", data=data)

    @staticmethod
    async def change_language(buyer, language: str, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        data = await svc.change_language(buyer.id, language)
        return StandardResponse(success=True, message="Language updated.", data=data)

    @staticmethod
    async def get_kyc_status(buyer, db: AsyncSession) -> StandardResponse:
        svc = BuyerService(db)
        data = await svc.get_kyc_status(buyer.id)
        return StandardResponse(success=True, data=data)
