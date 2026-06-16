"""Background job: clean up stale drafts."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update, delete

from app.core.constants import DraftConfig
from app.db.database import SessionLocal
from app.models.listing_draft import ListingDraft

logger = logging.getLogger(__name__)


async def run_draft_cleanup() -> None:
    now = datetime.now(timezone.utc)
    async with SessionLocal() as session:
        warn_cutoff = now - timedelta(days=DraftConfig.WARN_INACTIVE_DAYS)
        result = await session.execute(
            select(ListingDraft).where(
                ListingDraft.draft_status == "in_progress",
                ListingDraft.last_active_at < warn_cutoff,
                ListingDraft.last_active_at >= now - timedelta(days=DraftConfig.ABANDON_INACTIVE_DAYS),
            )
        )
        warn_drafts = result.scalars().all()
        if warn_drafts:
            logger.info("Would send SMS warning for %d stale drafts", len(warn_drafts))

        abandon_cutoff = now - timedelta(days=DraftConfig.ABANDON_INACTIVE_DAYS)
        await session.execute(
            update(ListingDraft)
            .where(
                ListingDraft.draft_status == "in_progress",
                ListingDraft.last_active_at < abandon_cutoff,
                ListingDraft.last_active_at >= now - timedelta(days=DraftConfig.DELETE_INACTIVE_DAYS),
            )
            .values(draft_status="abandoned")
        )

        delete_cutoff = now - timedelta(days=DraftConfig.DELETE_INACTIVE_DAYS)
        await session.execute(
            delete(ListingDraft).where(
                ListingDraft.draft_status == "abandoned",
                ListingDraft.last_active_at < delete_cutoff,
            )
        )

        await session.commit()
        logger.info("Draft cleanup job completed")
