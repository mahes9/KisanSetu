"""APScheduler setup for background jobs."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def init_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    from app.jobs.listing_expiry_job import run_listing_expiry
    from app.jobs.draft_cleanup_job import run_draft_cleanup
    from app.jobs.season_summary_job import run_season_summary_refresh

    # Daily at 00:30 IST (19:00 UTC previous day)
    scheduler.add_job(
        run_listing_expiry,
        CronTrigger(hour=19, minute=0),
        id="listing_expiry",
        name="Expire overdue listings",
        replace_existing=True,
    )

    # Daily at 02:00 IST (20:30 UTC previous day)
    scheduler.add_job(
        run_draft_cleanup,
        CronTrigger(hour=20, minute=30),
        id="draft_cleanup",
        name="Clean up stale drafts",
        replace_existing=True,
    )

    # Weekly on Sunday at 03:00 IST (21:30 UTC Saturday)
    scheduler.add_job(
        run_season_summary_refresh,
        CronTrigger(day_of_week="sat", hour=21, minute=30),
        id="season_summary",
        name="Refresh season summaries",
        replace_existing=True,
    )

    return scheduler


def start_scheduler(scheduler: AsyncIOScheduler) -> None:
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler(scheduler: AsyncIOScheduler) -> None:
    scheduler.shutdown(wait=False)
    logger.info("Background scheduler stopped")
