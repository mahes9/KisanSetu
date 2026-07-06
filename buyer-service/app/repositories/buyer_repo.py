"""Buyer repository — data access layer."""

from __future__ import annotations

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer import Buyer


class BuyerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_buyer(self, data: dict) -> Buyer:
        buyer = Buyer(id=uuid.uuid4(), **data)
        self._session.add(buyer)
        await self._session.flush()
        await self._session.refresh(buyer)
        return buyer

    async def get_by_id(self, buyer_id: uuid.UUID) -> Buyer | None:
        result = await self._session.execute(
            select(Buyer).where(Buyer.id == buyer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Buyer | None:
        result = await self._session.execute(
            select(Buyer).where(Buyer.primary_phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_gstin(self, gstin: str) -> Buyer | None:
        result = await self._session.execute(
            select(Buyer).where(Buyer.gstin == gstin)
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, buyer_id: uuid.UUID) -> Buyer | None:
        result = await self._session.execute(
            select(Buyer).where(Buyer.id == buyer_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def update_buyer(self, buyer_id: uuid.UUID, updates: dict) -> Buyer:
        stmt = update(Buyer).where(Buyer.id == buyer_id).values(**updates)
        await self._session.execute(stmt)
        await self._session.flush()
        buyer = await self.get_by_id(buyer_id)
        if buyer is not None:
            await self._session.refresh(buyer)
        return buyer  # type: ignore[return-value]

    async def update_kyc_status(self, buyer_id: uuid.UUID, status: str) -> None:
        await self._session.execute(
            update(Buyer).where(Buyer.id == buyer_id).values(kyc_status=status)
        )

    async def suspend_buyer(self, buyer_id: uuid.UUID, until) -> None:
        await self._session.execute(
            update(Buyer)
            .where(Buyer.id == buyer_id)
            .values(suspension_until=until)
        )
