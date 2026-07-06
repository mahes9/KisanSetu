"""Thin controller for delivery locations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.location_service import LocationService


class LocationController:
    @staticmethod
    async def create_location(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = LocationService(db)
        result = await svc.create_location(buyer.id, buyer.buyer_type, data)
        return StandardResponse(success=True, message="Location added.", data=result)

    @staticmethod
    async def list_locations(buyer, db: AsyncSession) -> StandardResponse:
        svc = LocationService(db)
        data = await svc.list_locations(buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def update_location(loc_id: UUID, buyer, updates: dict, db: AsyncSession) -> StandardResponse:
        svc = LocationService(db)
        data = await svc.update_location(loc_id, buyer.id, updates)
        return StandardResponse(success=True, message="Location updated.", data=data)

    @staticmethod
    async def delete_location(loc_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = LocationService(db)
        await svc.delete_location(loc_id, buyer.id)
        return StandardResponse(success=True, message="Location deleted.")

    @staticmethod
    async def set_default(loc_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = LocationService(db)
        data = await svc.set_default(loc_id, buyer.id)
        return StandardResponse(success=True, message="Default location set.", data=data)
