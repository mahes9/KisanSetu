"""Buyer requirement (RFQ) repository."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer_requirement import BuyerRequirement


class RequirementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_requirement(self, data: dict) -> BuyerRequirement:
        req = BuyerRequirement(id=uuid.uuid4(), **data)
        self._session.add(req)
        await self._session.flush()
        await self._session.refresh(req)
        return req

    async def get_by_id(self, req_id: uuid.UUID) -> BuyerRequirement | None:
        result = await self._session.execute(
            select(BuyerRequirement).where(BuyerRequirement.id == req_id)
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, req_id: uuid.UUID) -> BuyerRequirement | None:
        result = await self._session.execute(
            select(BuyerRequirement)
            .where(BuyerRequirement.id == req_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(
        self,
        buyer_id: uuid.UUID,
        status_filter: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> list[BuyerRequirement]:
        stmt = (
            select(BuyerRequirement)
            .where(BuyerRequirement.buyer_id == buyer_id)
            .order_by(BuyerRequirement.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        if status_filter:
            stmt = stmt.where(BuyerRequirement.status == status_filter)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_active_by_buyer(self, buyer_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(BuyerRequirement)
            .where(BuyerRequirement.buyer_id == buyer_id)
            .where(BuyerRequirement.status == "active")
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def update_requirement(self, req_id: uuid.UUID, updates: dict) -> BuyerRequirement:
        stmt = update(BuyerRequirement).where(BuyerRequirement.id == req_id).values(**updates)
        await self._session.execute(stmt)
        await self._session.flush()
        req = await self.get_by_id(req_id)
        if req is not None:
            await self._session.refresh(req)
        return req  # type: ignore[return-value]

    async def get_expired_requirements(self) -> list[BuyerRequirement]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(BuyerRequirement)
            .where(BuyerRequirement.status == "active")
            .where(BuyerRequirement.expires_at < now)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_update_status(self, req_ids: list[uuid.UUID], status: str) -> None:
        if not req_ids:
            return
        stmt = (
            update(BuyerRequirement)
            .where(BuyerRequirement.id.in_(req_ids))
            .values(status=status)
        )
        await self._session.execute(stmt)
        await self._session.flush()
