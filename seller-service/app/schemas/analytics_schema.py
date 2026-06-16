"""Analytics & season summary schemas — Module 6."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SeasonSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    seller_id: UUID | None = None
    season: str
    year: int
    total_listings: int = 0
    successful_sales: int = 0
    total_quantity_kg: float = 0
    total_earnings: float = 0
    total_commission: float = 0
    avg_price_per_q: float | None = None
    best_crop: str | None = None
    best_price_per_q: float | None = None
    mandi_comparison_percent: float | None = None
    cancellation_count: int = 0
    avg_time_to_match_hours: float | None = None
    avg_grade: str | None = None


class EarningsHistoryResponse(BaseModel):
    seasons: list[SeasonSummaryResponse] = []
    total_all_time_earnings: float = 0
    total_all_time_sales: int = 0


class MandiComparisonResponse(BaseModel):
    crop: str
    your_avg_price: float
    mandi_avg_price: float
    difference_percent: float
    verdict: str


class ListingAnalyticsResponse(BaseModel):
    listing_id: UUID
    views_count: int = 0
    enquiries_count: int = 0
    time_to_match_hours: float | None = None
    price_competitiveness: str | None = None


class DashboardResponse(BaseModel):
    active_listings: int = 0
    total_earnings_this_season: float = 0
    avg_grade: str | None = None
    pending_drafts: int = 0
    recent_activity: list[dict] = []
