"""Season summary & analytics service — Module 6."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_client import PriceClient
from app.core.validators import calculate_payout_preview
from app.repositories.draft_repo import DraftRepository
from app.repositories.listing_repo import ListingRepository
from app.repositories.season_repo import SeasonRepository

logger = logging.getLogger(__name__)


def _determine_current_season() -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    month = now.month
    year = now.year
    if 6 <= month <= 10:
        return f"kharif_{year}", year
    elif month >= 11 or month <= 3:
        effective_year = year if month >= 11 else year - 1
        return f"rabi_{effective_year}", effective_year
    else:
        return f"zaid_{year}", year


def _season_date_range(season: str, year: int) -> tuple[datetime, datetime]:
    if season.startswith("kharif"):
        start = datetime(year, 6, 1, tzinfo=timezone.utc)
        end = datetime(year, 10, 31, 23, 59, 59, tzinfo=timezone.utc)
    elif season.startswith("rabi"):
        start = datetime(year, 11, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 3, 31, 23, 59, 59, tzinfo=timezone.utc)
    else:
        start = datetime(year, 4, 1, tzinfo=timezone.utc)
        end = datetime(year, 5, 31, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.season_repo = SeasonRepository(session)
        self.listing_repo = ListingRepository(session)
        self.draft_repo = DraftRepository(session)
        self.price_client = PriceClient()

    async def get_season_summary(
        self,
        seller_id: UUID,
        season: str | None = None,
        year: int | None = None,
    ) -> dict:
        if not season or not year:
            season, year = _determine_current_season()

        summary = await self.season_repo.get_season_summary(seller_id, season, year)
        if summary:
            return self._summary_to_dict(summary)

        return {
            "season": season,
            "year": year,
            "total_listings": 0,
            "successful_sales": 0,
            "total_quantity_kg": 0,
            "total_earnings": 0,
            "total_commission": 0,
            "avg_price_per_q": None,
            "best_crop": None,
            "mandi_comparison_percent": None,
        }

    async def get_earnings_history(self, seller_id: UUID) -> dict:
        seasons = await self.season_repo.get_all_seasons(seller_id)
        total_earnings = await self.season_repo.get_seller_total_earnings(seller_id)
        total_sales = sum(s.successful_sales for s in seasons)
        return {
            "seasons": [self._summary_to_dict(s) for s in seasons],
            "total_all_time_earnings": total_earnings,
            "total_all_time_sales": total_sales,
        }

    async def compare_with_mandi(
        self, seller_id: UUID, crop: str | None = None
    ) -> list[dict]:
        season, year = _determine_current_season()
        start, end = _season_date_range(season, year)
        listings = await self.listing_repo.get_seller_listings_for_season(
            seller_id, start, end
        )
        if not listings:
            return []

        crop_data: dict[str, list[float]] = defaultdict(list)
        for l in listings:
            if l.status in ("sold", "active", "matched"):
                if crop and l.crop != crop:
                    continue
                crop_data[l.crop].append(l.ask_price_per_q)

        comparisons: list[dict] = []
        for c, prices in crop_data.items():
            avg_price = sum(prices) / len(prices)
            mandi = await self.price_client.get_floor_price(c, "kurnool")
            mandi_modal = mandi["modal_price"]
            diff_pct = round(((avg_price - mandi_modal) / mandi_modal) * 100, 1)
            verdict = "above_mandi" if diff_pct > 0 else ("below_mandi" if diff_pct < 0 else "at_mandi")
            comparisons.append({
                "crop": c,
                "your_avg_price": round(avg_price, 2),
                "mandi_avg_price": mandi_modal,
                "difference_percent": diff_pct,
                "verdict": verdict,
            })
        return comparisons

    async def get_listing_analytics(
        self, listing_id: UUID, seller_id: UUID
    ) -> dict:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing or listing.seller_id != seller_id:
            from app.core.exceptions import ListingNotFoundError
            raise ListingNotFoundError()

        time_to_match = None
        if listing.matched_at and listing.created_at:
            time_to_match = (listing.matched_at - listing.created_at).total_seconds() / 3600

        mandi = await self.price_client.get_floor_price(listing.crop, "kurnool")
        competitiveness = "competitive" if listing.ask_price_per_q <= mandi["modal_price"] else "above_market"

        return {
            "listing_id": str(listing_id),
            "views_count": listing.views_count,
            "enquiries_count": listing.enquiries_count,
            "time_to_match_hours": round(time_to_match, 1) if time_to_match else None,
            "price_competitiveness": competitiveness,
        }

    async def get_dashboard(self, seller_id: UUID) -> dict:
        active = await self.listing_repo.count_active_listings(seller_id)
        season, year = _determine_current_season()
        summary = await self.season_repo.get_season_summary(seller_id, season, year)
        drafts = await self.draft_repo.list_drafts_by_seller(seller_id)
        pending = len([d for d in drafts if d.draft_status in ("in_progress", "complete")])

        return {
            "active_listings": active,
            "total_earnings_this_season": summary.total_earnings if summary else 0,
            "avg_grade": summary.avg_grade if summary else None,
            "pending_drafts": pending,
            "recent_activity": [],
        }

    async def refresh_season_summary(
        self, seller_id: UUID, season: str, year: int
    ) -> dict:
        start, end = _season_date_range(season, year)
        listings = await self.listing_repo.get_seller_listings_for_season(
            seller_id, start, end
        )

        total_listings = len(listings)
        sold = [l for l in listings if l.status == "sold"]
        cancelled = [l for l in listings if l.status == "cancelled"]

        total_qty = sum(l.quantity_kg for l in sold)
        total_earnings = 0.0
        total_commission = 0.0
        prices: list[float] = []
        grades: list[str] = []
        crop_earnings: dict[str, float] = defaultdict(float)

        for l in sold:
            payout = calculate_payout_preview(l.quantity_kg, l.ask_price_per_q, l.modal_price_at_publish)
            total_earnings += payout["seller_payout"]
            total_commission += payout["commission_amount"]
            prices.append(l.ask_price_per_q)
            grades.append(l.grade)
            crop_earnings[l.crop] += payout["seller_payout"]

        best_crop = max(crop_earnings, key=crop_earnings.get) if crop_earnings else None
        avg_price = round(sum(prices) / len(prices), 2) if prices else None

        data = {
            "seller_id": seller_id,
            "season": season,
            "year": year,
            "total_listings": total_listings,
            "successful_sales": len(sold),
            "total_quantity_kg": total_qty,
            "total_earnings": round(total_earnings, 2),
            "total_commission": round(total_commission, 2),
            "avg_price_per_q": avg_price,
            "best_crop": best_crop,
            "cancellation_count": len(cancelled),
            "avg_grade": max(set(grades), key=grades.count) if grades else None,
        }
        summary = await self.season_repo.upsert_season_summary(data)
        return self._summary_to_dict(summary)

    def _summary_to_dict(self, s) -> dict:
        return {
            "id": str(s.id),
            "seller_id": str(s.seller_id),
            "season": s.season,
            "year": s.year,
            "total_listings": s.total_listings,
            "successful_sales": s.successful_sales,
            "total_quantity_kg": s.total_quantity_kg,
            "total_earnings": s.total_earnings,
            "total_commission": s.total_commission,
            "avg_price_per_q": s.avg_price_per_q,
            "best_crop": s.best_crop,
            "best_price_per_q": s.best_price_per_q,
            "mandi_comparison_percent": s.mandi_comparison_percent,
            "cancellation_count": s.cancellation_count,
            "avg_time_to_match_hours": s.avg_time_to_match_hours,
            "avg_grade": s.avg_grade,
        }
