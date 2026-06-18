"""Authentication helpers: password hashing, JWT, Aadhaar hashing."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.core.exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_jwt(
    buyer_id: str,
    payload: dict | None = None,
    expires_in: int | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire_delta = timedelta(
        days=expires_in if expires_in is not None else settings.JWT_EXPIRY_DAYS
    )
    data: dict = {
        "buyer_id": buyer_id,
        "iat": now,
        "exp": now + expire_delta,
    }
    if payload:
        data.update(payload)
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise UnauthorizedError(
            message_en="Invalid or expired authentication token."
        ) from exc


def hash_aadhaar(aadhaar_number: str) -> str:
    return hashlib.sha256(aadhaar_number.encode()).hexdigest()
