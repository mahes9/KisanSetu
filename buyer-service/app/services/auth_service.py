"""Authentication service."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BuyerNotFoundError, InvalidOTPError, UnauthorizedError
from app.core.security import create_jwt, verify_password
from app.repositories.buyer_repo import BuyerRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = BuyerRepository(session)

    async def login_individual(self, phone: str, otp: str) -> dict:
        buyer = await self.repo.get_by_phone(phone)
        if not buyer:
            raise BuyerNotFoundError()
        if buyer.buyer_type != "individual":
            raise UnauthorizedError(message_en="Use organization login.")

        # OTP validation is mocked in Phase 1
        if not otp:
            raise InvalidOTPError()

        token = create_jwt(str(buyer.id), {"buyer_type": "individual"})
        await self.repo.update_buyer(buyer.id, {"last_active_at": datetime.now(timezone.utc)})
        return {
            "access_token": token,
            "token_type": "bearer",
            "buyer_id": str(buyer.id),
            "buyer_type": "individual",
        }

    async def login_organization(self, email: str, password: str) -> dict:
        from sqlalchemy import select
        from app.models.buyer import Buyer

        result = await self.repo._session.execute(
            select(Buyer).where(Buyer.primary_email == email).where(Buyer.buyer_type == "organization")
        )
        buyer = result.scalar_one_or_none()
        if not buyer:
            raise BuyerNotFoundError()
        if not buyer.password_hash or not verify_password(password, buyer.password_hash):
            raise UnauthorizedError(message_en="Invalid email or password.")

        token = create_jwt(str(buyer.id), {"buyer_type": "organization"})
        await self.repo.update_buyer(buyer.id, {"last_active_at": datetime.now(timezone.utc)})
        return {
            "access_token": token,
            "token_type": "bearer",
            "buyer_id": str(buyer.id),
            "buyer_type": "organization",
        }
