"""Farm repository — Module 2.

Local cache of farm data fetched from the Farmer Service.
The Farmer Service is the source of truth; this is a read-optimized copy.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.farm import Farm


class FarmRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_farm(self, seller_id: uuid.UUID, farm_data: dict) -> Farm:
        farm = Farm(seller_id=seller_id, **farm_data)
        self.session.add(farm)
        await self.session.flush()
        return farm

    async def get_farm_by_seller(self, seller_id: uuid.UUID) -> Farm | None:
        result = await self.session.execute(
            select(Farm).where(Farm.seller_id == seller_id)
        )
        return result.scalar_one_or_none()

    async def get_farms_by_seller(self, seller_id: uuid.UUID) -> list[Farm]:
        result = await self.session.execute(
            select(Farm).where(Farm.seller_id == seller_id)
        )
        return list(result.scalars().all())

    async def update_farm(self, farm_id: uuid.UUID, updates: dict) -> Farm:
        await self.session.execute(
            update(Farm).where(Farm.id == farm_id).values(**updates)
        )
        await self.session.flush()
        result = await self.session.execute(
            select(Farm).where(Farm.id == farm_id)
        )
        return result.scalar_one_or_none()
