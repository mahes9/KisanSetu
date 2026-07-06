"""FastAPI dependency injection for authentication and authorization."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BuyerSuspendedError,
    IndividualBuyerOrgActionError,
    KYCNotVerifiedError,
    UnauthorizedError,
)
from app.core.security import decode_jwt
from app.db.database import get_db
from app.models.buyer import Buyer

bearer_scheme = HTTPBearer()


async def get_current_buyer(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Buyer:
    payload = decode_jwt(credentials.credentials)
    buyer_id = payload.get("buyer_id")
    if not buyer_id:
        raise UnauthorizedError()

    result = await db.execute(select(Buyer).where(Buyer.id == UUID(buyer_id)))
    buyer = result.scalar_one_or_none()
    if buyer is None:
        raise UnauthorizedError(message_en="Buyer account not found.")
    return buyer


async def require_kyc_verified(
    buyer: Buyer = Depends(get_current_buyer),
) -> Buyer:
    if buyer.suspension_until and buyer.suspension_until > datetime.now(timezone.utc):
        raise BuyerSuspendedError()
    if buyer.kyc_status != "fully_verified":
        raise KYCNotVerifiedError()
    return buyer


async def require_org_buyer(
    buyer: Buyer = Depends(get_current_buyer),
) -> Buyer:
    if buyer.buyer_type != "organization":
        raise IndividualBuyerOrgActionError()
    return buyer


async def require_verified_org_buyer(
    buyer: Buyer = Depends(require_kyc_verified),
) -> Buyer:
    if buyer.buyer_type != "organization":
        raise IndividualBuyerOrgActionError()
    return buyer
