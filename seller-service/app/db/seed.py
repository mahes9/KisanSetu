"""Seed data for development and testing."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.base import Base
from app.models.seller import Seller
from app.models.farm import Farm


SELLERS = [
    {
        "id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "phone": "9876543210",
        "full_name": "Ramesh Kumar",
        "kyc_status": "verified",
        "aadhaar_verified": True,
        "bank_verified": True,
        "upi_verified": True,
        "trust_score": 80,
        "language": "te",
    },
    {
        "id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "phone": "9876543211",
        "full_name": "Suresh Reddy",
        "kyc_status": "pending",
        "trust_score": 0,
        "language": "te",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "phone": "9876543212",
        "full_name": "Lakshmi Devi",
        "kyc_status": "suspended",
        "cancellation_count": 3,
        "trust_score": 20,
        "language": "te",
    },
]

FARMS = [
    {
        "seller_id": uuid.UUID("11111111-1111-1111-1111-111111111111"),
        "gps_latitude": 15.8281,
        "gps_longitude": 78.0373,
        "district": "kurnool",
        "village": "Adoni",
        "acreage": 5.0,
        "irrigation_type": "borewell",
        "soil_type": "black_cotton",
    },
    {
        "seller_id": uuid.UUID("22222222-2222-2222-2222-222222222222"),
        "gps_latitude": 15.4777,
        "gps_longitude": 78.4836,
        "district": "nandyal",
        "village": "Atmakur",
        "acreage": 3.5,
    },
    {
        "seller_id": uuid.UUID("33333333-3333-3333-3333-333333333333"),
        "gps_latitude": 15.8300,
        "gps_longitude": 78.0400,
        "district": "kurnool",
        "village": "Mantralayam",
        "acreage": 8.0,
    },
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        for data in SELLERS:
            session.add(Seller(**data))
        for data in FARMS:
            session.add(Farm(**data))
        await session.commit()

    await engine.dispose()
    print(f"Seeded {len(SELLERS)} sellers and {len(FARMS)} farms.")


if __name__ == "__main__":
    asyncio.run(seed())
