"""Org buyer user repository."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.buyer_user import BuyerUser


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, data: dict) -> BuyerUser:
        user = BuyerUser(id=uuid.uuid4(), **data)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> BuyerUser | None:
        result = await self._session.execute(
            select(BuyerUser).where(BuyerUser.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email_and_buyer(self, email: str, buyer_id: uuid.UUID) -> BuyerUser | None:
        result = await self._session.execute(
            select(BuyerUser)
            .where(BuyerUser.email == email)
            .where(BuyerUser.buyer_id == buyer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_invitation_token(self, token: str) -> BuyerUser | None:
        result = await self._session.execute(
            select(BuyerUser).where(BuyerUser.invitation_token == token)
        )
        return result.scalar_one_or_none()

    async def list_by_buyer(self, buyer_id: uuid.UUID) -> list[BuyerUser]:
        stmt = (
            select(BuyerUser)
            .where(BuyerUser.buyer_id == buyer_id)
            .order_by(BuyerUser.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_user(self, user_id: uuid.UUID, updates: dict) -> BuyerUser:
        stmt = update(BuyerUser).where(BuyerUser.id == user_id).values(**updates)
        await self._session.execute(stmt)
        await self._session.flush()
        user = await self.get_by_id(user_id)
        if user is not None:
            await self._session.refresh(user)
        return user  # type: ignore[return-value]

    async def delete_user(self, user_id: uuid.UUID) -> None:
        stmt = delete(BuyerUser).where(BuyerUser.id == user_id)
        await self._session.execute(stmt)
        await self._session.flush()
