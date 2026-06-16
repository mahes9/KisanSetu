"""Season summary repository — Module 6."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.season_summary import SeasonSummary
from app.models.seller import Seller


class SeasonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_season_summary(
        self, seller_id: UUID, season: str, year: int
    ) -> SeasonSummary | None:
        result = await self.session.execute(
            select(SeasonSummary).where(
                SeasonSummary.seller_id == seller_id,
                SeasonSummary.season == season,
                SeasonSummary.year == year,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_season_summary(self, data: dict) -> SeasonSummary:
        existing = await self.get_season_summary(
            data["seller_id"], data["season"], data["year"]
        )
        if existing:
            for key, val in data.items():
                if key not in ("seller_id", "season", "year"):
                    setattr(existing, key, val)
            await self.session.flush()
            return existing
        else:
            summary = SeasonSummary(**data)
            self.session.add(summary)
            await self.session.flush()
            return summary

    async def get_all_seasons(self, seller_id: UUID) -> list[SeasonSummary]:
        result = await self.session.execute(
            select(SeasonSummary)
            .where(SeasonSummary.seller_id == seller_id)
            .order_by(SeasonSummary.year.desc(), SeasonSummary.season)
        )
        return list(result.scalars().all())

    async def get_seller_total_earnings(self, seller_id: UUID) -> float:
        result = await self.session.execute(
            select(func.coalesce(func.sum(SeasonSummary.total_earnings), 0.0)).where(
                SeasonSummary.seller_id == seller_id
            )
        )
        return float(result.scalar() or 0.0)

    async def get_sellers_for_summary_refresh(self) -> list[UUID]:
        result = await self.session.execute(
            select(Seller.id).where(Seller.kyc_status.in_(["verified", "aadhaar_verified"]))
        )
        return [row[0] for row in result.all()]
