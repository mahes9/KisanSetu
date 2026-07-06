"""Buyer analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.analytics_controller import AnalyticsController
from app.db.database import get_db
from app.models.buyer import Buyer

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", summary="Get buyer dashboard")
async def get_dashboard(
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_dashboard(buyer, db)


@router.get("/spend-trends", summary="Get spending trends")
async def get_spend_trends(
    period: str = Query("monthly", pattern=r"^(daily|weekly|monthly)$"),
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_spend_trends(buyer, period, db)


@router.get("/vendors", summary="Get vendor performance")
async def get_vendor_performance(
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_vendor_performance(buyer, db)


@router.get("/gst-summary", summary="Get GST summary")
async def get_gst_summary(
    period: str = Query("monthly"),
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await AnalyticsController.get_gst_summary(buyer, db)
