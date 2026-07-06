"""KYC verification repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kyc_verification import KycVerification


class KycRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_verification(self, data: dict) -> KycVerification:
        verification = KycVerification(id=uuid.uuid4(), **data)
        self._session.add(verification)
        await self._session.flush()
        await self._session.refresh(verification)
        return verification

    async def get_latest_by_type(
        self, buyer_id: uuid.UUID, verification_type: str
    ) -> KycVerification | None:
        stmt = (
            select(KycVerification)
            .where(KycVerification.buyer_id == buyer_id)
            .where(KycVerification.verification_type == verification_type)
            .order_by(KycVerification.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_buyer(self, buyer_id: uuid.UUID) -> list[KycVerification]:
        stmt = (
            select(KycVerification)
            .where(KycVerification.buyer_id == buyer_id)
            .order_by(KycVerification.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
