"""Offer / negotiation endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_kyc_verified
from app.controllers.offer_controller import OfferController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.offer_schema import CounterOfferRequest

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.get("/requirement/{req_id}", summary="List offers for a requirement")
async def list_offers(
    req_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OfferController.list_offers(req_id, buyer, db)


@router.post("/{offer_id}/accept", summary="Accept an offer")
async def accept_offer(
    offer_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OfferController.accept_offer(offer_id, buyer, db)


@router.post("/{offer_id}/counter", summary="Counter an offer")
async def counter_offer(
    offer_id: UUID,
    body: CounterOfferRequest,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OfferController.counter_offer(offer_id, buyer, body.model_dump(), db)


@router.post("/{offer_id}/reject", summary="Reject an offer")
async def reject_offer(
    offer_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await OfferController.reject_offer(offer_id, buyer, db)
