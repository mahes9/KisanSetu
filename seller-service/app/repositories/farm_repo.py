"""Farm repository — Module 2 (stub)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm


class FarmRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_farm(self, seller_id: UUID, farm_data: dict) -> Farm:
        farm = Farm(seller_id=seller_id, **farm_data)
        self.session.add(farm)
        await self.session.flush()
        return farm

    async def get_farm_by_seller(self, seller_id: UUID) -> Farm | None:
        result = await self.session.execute(
            select(Farm).where(Farm.seller_id == seller_id)
        )
        return result.scalar_one_or_none()
