"""Organization buyer user management service."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.core.security import hash_password
from app.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def invite_user(self, buyer_id: UUID, data: dict) -> dict:
        existing = await self.repo.get_by_email_and_buyer(data["email"], buyer_id)
        if existing:
            raise UserAlreadyExistsError()

        token = secrets.token_urlsafe(32)
        user = await self.repo.create_user({
            "buyer_id": buyer_id,
            "email": data["email"],
            "full_name": data["full_name"],
            "phone": data.get("phone"),
            "role": data.get("role", "viewer"),
            "invitation_token": token,
        })
        return self._build_response(user)

    async def list_users(self, buyer_id: UUID) -> dict:
        users = await self.repo.list_by_buyer(buyer_id)
        return {
            "users": [self._build_response(u) for u in users],
            "total": len(users),
        }

    async def accept_invitation(self, token: str, password: str) -> dict:
        user = await self.repo.get_by_invitation_token(token)
        if not user:
            raise UserNotFoundError()
        user = await self.repo.update_user(user.id, {
            "password_hash": hash_password(password),
            "invitation_accepted": True,
            "invitation_accepted_at": datetime.now(timezone.utc),
            "invitation_token": None,
            "is_active": True,
        })
        return self._build_response(user)

    async def update_role(self, user_id: UUID, buyer_id: UUID, role: str) -> dict:
        user = await self.repo.get_by_id(user_id)
        if not user or user.buyer_id != buyer_id:
            raise UserNotFoundError()
        user = await self.repo.update_user(user_id, {"role": role})
        return self._build_response(user)

    async def remove_user(self, user_id: UUID, buyer_id: UUID) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user or user.buyer_id != buyer_id:
            raise UserNotFoundError()
        await self.repo.delete_user(user_id)

    def _build_response(self, user) -> dict:
        return {
            "id": str(user.id),
            "buyer_id": str(user.buyer_id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "invitation_accepted": user.invitation_accepted,
            "last_login_at": str(user.last_login_at) if user.last_login_at else None,
            "created_at": str(user.created_at) if user.created_at else None,
        }
