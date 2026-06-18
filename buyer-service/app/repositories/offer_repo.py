"""Offer / negotiation repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.requirement_offer import RequirementOffer


class OfferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_offer(self, data: dict) -> RequirementOffer:
        offer = RequirementOffer(id=uuid.uuid4(), **data)
        self._session.add(offer)
        await self._session.flush()
        await self._session.refresh(offer)
        return offer

    async def get_by_id(self, offer_id: uuid.UUID) -> RequirementOffer | None:
        result = await self._session.execute(
            select(RequirementOffer).where(RequirementOffer.id == offer_id)
        )
        return result.scalar_one_or_none()

    async def list_by_requirement(self, requirement_id: uuid.UUID) -> list[RequirementOffer]:
        stmt = (
            select(RequirementOffer)
            .where(RequirementOffer.requirement_id == requirement_id)
            .order_by(RequirementOffer.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_rounds(self, requirement_id: uuid.UUID, seller_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(RequirementOffer)
            .where(RequirementOffer.requirement_id == requirement_id)
            .where(RequirementOffer.seller_id == seller_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_offer(self, offer_id: uuid.UUID, updates: dict) -> RequirementOffer:
        stmt = update(RequirementOffer).where(RequirementOffer.id == offer_id).values(**updates)
        await self._session.execute(stmt)
        await self._session.flush()
        offer = await self.get_by_id(offer_id)
        if offer is not None:
            await self._session.refresh(offer)
        return offer  # type: ignore[return-value]
