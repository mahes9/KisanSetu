"""Seller repository — Module 1/2 (stub)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seller import Seller


class SellerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_seller_by_id(self, seller_id: UUID) -> Seller | None:
        result = await self.session.execute(
            select(Seller).where(Seller.id == seller_id)
        )
        return result.scalar_one_or_none()

    async def get_seller_by_phone(self, phone: str) -> Seller | None:
        result = await self.session.execute(
            select(Seller).where(Seller.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, seller_id: UUID) -> Seller | None:
        result = await self.session.execute(
            select(Seller).where(Seller.id == seller_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def update_kyc_status(self, seller_id: UUID, status: str) -> None:
        await self.session.execute(
            update(Seller).where(Seller.id == seller_id).values(kyc_status=status)
        )

    async def update_cancellation_count(self, seller_id: UUID, count: int) -> None:
        await self.session.execute(
            update(Seller)
            .where(Seller.id == seller_id)
            .values(cancellation_count=count)
        )

    async def suspend_seller(self, seller_id: UUID, until) -> None:
        await self.session.execute(
            update(Seller)
            .where(Seller.id == seller_id)
            .values(suspension_until=until, kyc_status="suspended")
        )
