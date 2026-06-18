"""Browse and discovery endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.browse_controller import BrowseController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.browse_schema import PriceAlertRequest, PreferredSellerRequest, SavedSearchRequest

router = APIRouter(prefix="/browse", tags=["Browse & Discovery"])


@router.get("/listings", summary="Browse seller listings")
async def browse_listings(
    crop: str | None = Query(None),
    grade: str | None = Query(None),
    district: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    filters = {
        "crop": crop, "grade": grade, "district": district,
        "min_price": min_price, "max_price": max_price,
        "page": page, "per_page": per_page,
    }
    return await BrowseController.browse_listings(
        {k: v for k, v in filters.items() if v is not None}, db,
    )


@router.get("/listings/{listing_id}", summary="Get listing detail")
async def get_listing(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.get_listing(listing_id, db)


@router.post("/saved-searches", summary="Save a search")
async def save_search(
    body: SavedSearchRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.save_search(buyer, body.label, body.filters, db)


@router.post("/preferred-sellers/{seller_id}", summary="Add preferred seller")
async def add_preferred_seller(
    seller_id: UUID,
    body: PreferredSellerRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.add_preferred_seller(buyer, seller_id, body.notes, db)


@router.post("/price-alerts", summary="Create a price alert")
async def create_price_alert(
    body: PriceAlertRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await BrowseController.create_price_alert(buyer, body.model_dump(), db)
