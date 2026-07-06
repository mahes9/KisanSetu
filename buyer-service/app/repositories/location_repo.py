"""Delivery location repository."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer_location import BuyerLocation


class LocationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_location(self, data: dict) -> BuyerLocation:
        location = BuyerLocation(id=uuid.uuid4(), **data)
        self._session.add(location)
        await self._session.flush()
        await self._session.refresh(location)
        return location

    async def get_by_id(self, location_id: uuid.UUID) -> BuyerLocation | None:
        result = await self._session.execute(
            select(BuyerLocation).where(BuyerLocation.id == location_id)
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(self, buyer_id: uuid.UUID) -> list[BuyerLocation]:
        stmt = (
            select(BuyerLocation)
            .where(BuyerLocation.buyer_id == buyer_id)
            .order_by(BuyerLocation.is_default.desc(), BuyerLocation.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_buyer(self, buyer_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(BuyerLocation)
            .where(BuyerLocation.buyer_id == buyer_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_location(self, location_id: uuid.UUID, updates: dict) -> BuyerLocation:
        stmt = update(BuyerLocation).where(BuyerLocation.id == location_id).values(**updates)
        await self._session.execute(stmt)
        await self._session.flush()
        location = await self.get_by_id(location_id)
        if location is not None:
            await self._session.refresh(location)
        return location  # type: ignore[return-value]

    async def delete_location(self, location_id: uuid.UUID) -> None:
        stmt = delete(BuyerLocation).where(BuyerLocation.id == location_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def clear_defaults(self, buyer_id: uuid.UUID) -> None:
        stmt = (
            update(BuyerLocation)
            .where(BuyerLocation.buyer_id == buyer_id)
            .values(is_default=False)
        )
        await self._session.execute(stmt)

    async def set_default(self, location_id: uuid.UUID, buyer_id: uuid.UUID) -> None:
        await self.clear_defaults(buyer_id)
        await self.update_location(location_id, {"is_default": True})
