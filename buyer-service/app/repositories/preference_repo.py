"""Buyer preference repository — saved searches, alerts, preferred sellers."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer_preference import BuyerPreference


class PreferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_preference(self, data: dict) -> BuyerPreference:
        pref = BuyerPreference(id=uuid.uuid4(), **data)
        self._session.add(pref)
        await self._session.flush()
        await self._session.refresh(pref)
        return pref

    async def get_by_id(self, pref_id: uuid.UUID) -> BuyerPreference | None:
        result = await self._session.execute(
            select(BuyerPreference).where(BuyerPreference.id == pref_id)
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(
        self, buyer_id: uuid.UUID, preference_type: str | None = None
    ) -> list[BuyerPreference]:
        stmt = (
            select(BuyerPreference)
            .where(BuyerPreference.buyer_id == buyer_id)
            .where(BuyerPreference.is_active.is_(True))
            .order_by(BuyerPreference.created_at.desc())
        )
        if preference_type:
            stmt = stmt.where(BuyerPreference.preference_type == preference_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_preference(self, pref_id: uuid.UUID) -> None:
        stmt = delete(BuyerPreference).where(BuyerPreference.id == pref_id)
        await self._session.execute(stmt)
        await self._session.flush()
