"""FastAPI dependency injection for authentication and authorization."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import KYCNotVerifiedError, SellerSuspendedError, UnauthorizedError
from app.core.security import decode_jwt
from app.db.database import get_db
from app.models.seller import Seller

from datetime import datetime, timezone

bearer_scheme = HTTPBearer()


async def get_current_seller(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Seller:
    payload = decode_jwt(credentials.credentials)
    seller_id = payload.get("seller_id")
    if not seller_id:
        raise UnauthorizedError()

    result = await db.execute(select(Seller).where(Seller.id == UUID(seller_id)))
    seller = result.scalar_one_or_none()
    if seller is None:
        raise UnauthorizedError(message_en="Seller account not found.")
    return seller


async def require_kyc_verified(
    seller: Seller = Depends(get_current_seller),
) -> Seller:
    if seller.suspension_until and seller.suspension_until > datetime.now(timezone.utc):
        raise SellerSuspendedError()
    if seller.kyc_status != "verified":
        raise KYCNotVerifiedError()
    return seller
