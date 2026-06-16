"""Background job: refresh season summaries for all active sellers."""

from __future__ import annotations

import logging

from app.db.database import SessionLocal
from app.repositories.season_repo import SeasonRepository
from app.services.analytics_service import AnalyticsService, _determine_current_season

logger = logging.getLogger(__name__)


async def run_season_summary_refresh() -> None:
    async with SessionLocal() as session:
        season_repo = SeasonRepository(session)
        seller_ids = await season_repo.get_sellers_for_summary_refresh()

        season, year = _determine_current_season()
        count = 0
        for seller_id in seller_ids:
            try:
                svc = AnalyticsService(session)
                await svc.refresh_season_summary(seller_id, season, year)
                count += 1
            except Exception:
                logger.exception("Failed to refresh summary for seller %s", seller_id)

        await session.commit()
        logger.info("Season summary refresh completed: %d sellers updated", count)
