"""Listing publish & management endpoints — Module 5."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_seller, require_kyc_verified
from app.controllers.listing_controller import ListingController
from app.db.database import get_db
from app.models.seller import Seller
from app.schemas.listing_schema import CancelListingRequest, EditPriceRequest, PublishRequest

router = APIRouter(tags=["Listings"])


@router.post("/drafts/{draft_id}/publish", summary="Publish a draft as a live listing")
async def publish_listing(
    draft_id: UUID,
    body: PublishRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.publish_listing(draft_id, body.model_dump(), seller, db)


@router.get("/listings", summary="List my listings")
async def list_my_listings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.list_my_listings(seller, db, page, per_page, status)


@router.get("/listings/public", summary="Browse all active listings (no auth)")
async def browse_public_listings(
    crop: str | None = Query(None),
    district: str | None = Query(None),
    min_qty: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.browse_public_listings(
        db, crop, district, min_qty, max_price, page, per_page
    )


@router.get("/listings/{listing_id}", summary="Get listing detail")
async def get_listing(
    listing_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.get_listing(listing_id, seller, db)


@router.get("/listings/{listing_id}/public", summary="Public listing view (no auth)")
async def get_public_listing(
    listing_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.get_public_listing(listing_id, db)


@router.patch("/listings/{listing_id}/price", summary="Edit listing price")
async def edit_price(
    listing_id: UUID,
    body: EditPriceRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.edit_price(listing_id, body.new_price_per_q, seller, db, body.reason)


@router.post("/listings/{listing_id}/pause", summary="Pause a listing")
async def pause_listing(
    listing_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.pause_listing(listing_id, seller, db)


@router.post("/listings/{listing_id}/resume", summary="Resume a paused listing")
async def resume_listing(
    listing_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.resume_listing(listing_id, seller, db)


@router.post("/listings/{listing_id}/cancel", summary="Cancel a listing")
async def cancel_listing(
    listing_id: UUID,
    body: CancelListingRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await ListingController.cancel_listing(listing_id, body.reason, seller, db)
