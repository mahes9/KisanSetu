"""Analytics endpoints — Module 6."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_seller
from app.controllers.analytics_controller import AnalyticsController
from app.db.database import get_db
from app.models.seller import Seller

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/season-summary", summary="Get season summary")
async def get_season_summary(
    season: str | None = Query(None),
    year: int | None = Query(None),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_season_summary(seller, db, season, year)


@router.get("/earnings-history", summary="Get earnings history across all seasons")
async def get_earnings_history(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_earnings_history(seller, db)


@router.get("/mandi-comparison", summary="Compare your prices with mandi rates")
async def compare_with_mandi(
    crop: str | None = Query(None),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.compare_with_mandi(seller, db, crop)


@router.get("/listings/{listing_id}/stats", summary="Get analytics for a specific listing")
async def get_listing_analytics(
    listing_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_listing_analytics(listing_id, seller, db)


@router.get("/dashboard", summary="Get seller dashboard overview")
async def get_dashboard(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_dashboard(seller, db)
