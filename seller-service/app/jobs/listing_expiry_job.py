"""Background job: expire overdue listings."""

from __future__ import annotations

import logging

from app.db.database import SessionLocal
from app.services.listing_service import ListingService
from app.repositories.listing_repo import ListingRepository

logger = logging.getLogger(__name__)


async def run_listing_expiry() -> None:
    async with SessionLocal() as session:
        repo = ListingRepository(session)
        svc = ListingService(session)

        expired = await repo.get_expired_listings()
        count = 0
        for listing in expired:
            try:
                await svc.expire_listing(listing.id)
                count += 1
            except Exception:
                logger.exception("Failed to expire listing %s", listing.id)

        await session.commit()
        logger.info("Listing expiry job completed: %d listings expired", count)
