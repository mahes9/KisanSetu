"""Enquiry endpoints — buyer-seller interest & negotiation."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_seller
from app.controllers.enquiry_controller import EnquiryController
from app.db.database import get_db
from app.models.seller import Seller
from app.schemas.enquiry_schema import (
    BuyerCounterRequest,
    CreateEnquiryRequest,
    SellerRespondRequest,
)

router = APIRouter(tags=["Enquiries"])


# ── Public endpoints (called by buyer service, no seller auth) ──

@router.post("/listings/{listing_id}/enquiry", summary="Send enquiry on a listing (buyer→seller)")
async def create_enquiry(
    listing_id: UUID,
    body: CreateEnquiryRequest,
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.create_enquiry(listing_id, body.model_dump(), db)


@router.get("/enquiries/buyer/{buyer_id}", summary="Get enquiries sent by a buyer")
async def get_buyer_enquiries(
    buyer_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.get_buyer_enquiries(buyer_id, db, page, per_page)


@router.post("/enquiries/{enquiry_id}/counter", summary="Buyer counter-offer")
async def buyer_counter(
    enquiry_id: UUID,
    body: BuyerCounterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.buyer_counter(enquiry_id, body.buyer_id, body.model_dump(), db)


@router.post("/enquiries/{enquiry_id}/withdraw", summary="Buyer withdraws enquiry")
async def buyer_withdraw(
    enquiry_id: UUID,
    buyer_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.buyer_withdraw(enquiry_id, buyer_id, db)


# ── Seller-authenticated endpoints ──

@router.get("/enquiries/my", summary="Get all enquiries received by seller")
async def get_seller_enquiries(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.get_seller_enquiries(seller, db, status, page, per_page)


@router.get("/listings/{listing_id}/enquiries", summary="Get enquiries for a listing (seller)")
async def get_listing_enquiries(
    listing_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.get_listing_enquiries(listing_id, seller, db, page, per_page)


@router.post("/enquiries/{enquiry_id}/respond", summary="Seller responds with quote")
async def seller_respond(
    enquiry_id: UUID,
    body: SellerRespondRequest,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.seller_respond(enquiry_id, seller, body.model_dump(), db)


@router.post("/enquiries/{enquiry_id}/accept", summary="Seller accepts enquiry")
async def seller_accept(
    enquiry_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.seller_accept(enquiry_id, seller, db)


@router.post("/enquiries/{enquiry_id}/reject", summary="Seller rejects enquiry")
async def seller_reject(
    enquiry_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.seller_reject(enquiry_id, seller, db)


@router.post("/enquiries/{enquiry_id}/viewed", summary="Mark enquiry as viewed")
async def mark_viewed(
    enquiry_id: UUID,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await EnquiryController.mark_viewed(enquiry_id, seller, db)
