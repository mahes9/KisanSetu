"""Farm profile controller — Module 2."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.farm_service import FarmService


class FarmController:
    @staticmethod
    async def get_farmer_profile(seller, db: AsyncSession) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.get_farmer_profile(seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_farms(seller, db: AsyncSession) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.get_farms(seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_farm_detail(
        farm_id: str, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.get_farm_detail(seller.id, farm_id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def get_bank_status(seller, db: AsyncSession) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.get_bank_status(seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def sync_farm(
        farm_id: str, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.sync_farm_to_local(seller.id, farm_id)
        return StandardResponse(
            success=True,
            message="Farm synced to seller service.",
            data=data,
        )

    @staticmethod
    async def get_publish_readiness(seller, db: AsyncSession) -> StandardResponse:
        svc = FarmService(db)
        data = await svc.get_publish_readiness(seller.id)
        return StandardResponse(success=True, data=data)
