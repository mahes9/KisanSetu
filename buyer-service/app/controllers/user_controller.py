"""Thin controller for org user management."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.user_service import UserService


class UserController:
    @staticmethod
    async def invite_user(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = UserService(db)
        result = await svc.invite_user(buyer.id, data)
        return StandardResponse(success=True, message="User invited.", data=result)

    @staticmethod
    async def list_users(buyer, db: AsyncSession) -> StandardResponse:
        svc = UserService(db)
        data = await svc.list_users(buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def accept_invitation(token: str, password: str, db: AsyncSession) -> StandardResponse:
        svc = UserService(db)
        data = await svc.accept_invitation(token, password)
        return StandardResponse(success=True, message="Invitation accepted.", data=data)

    @staticmethod
    async def update_role(user_id: UUID, buyer, role: str, db: AsyncSession) -> StandardResponse:
        svc = UserService(db)
        data = await svc.update_role(user_id, buyer.id, role)
        return StandardResponse(success=True, message="Role updated.", data=data)

    @staticmethod
    async def remove_user(user_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = UserService(db)
        await svc.remove_user(user_id, buyer.id)
        return StandardResponse(success=True, message="User removed.")
