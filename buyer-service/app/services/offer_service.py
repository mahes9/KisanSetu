"""Offer / negotiation service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import OfferConfig
from app.core.exceptions import (
    MaxNegotiationRoundsError,
    OfferAlreadyRespondedError,
    OfferNotFoundError,
    RequirementNotFoundError,
)
from app.core.state_machine import transition_offer
from app.repositories.offer_repo import OfferRepository
from app.repositories.requirement_repo import RequirementRepository


class OfferService:
    def __init__(self, session: AsyncSession) -> None:
        self.offer_repo = OfferRepository(session)
        self.req_repo = RequirementRepository(session)

    async def list_offers(self, requirement_id: UUID, buyer_id: UUID) -> dict:
        req = await self.req_repo.get_by_id(requirement_id)
        if not req or req.buyer_id != buyer_id:
            raise RequirementNotFoundError()
        offers = await self.offer_repo.list_by_requirement(requirement_id)
        return {
            "offers": [self._build_response(o) for o in offers],
            "total": len(offers),
        }

    async def accept_offer(self, offer_id: UUID, buyer_id: UUID) -> dict:
        offer = await self._get_offer(offer_id)
        req = await self.req_repo.get_by_id(offer.requirement_id)
        if not req or req.buyer_id != buyer_id:
            raise RequirementNotFoundError()

        transition_offer(offer.status, "accepted")
        offer = await self.offer_repo.update_offer(offer_id, {
            "status": "accepted",
            "responded_at": datetime.now(timezone.utc),
        })
        await self.req_repo.update_requirement(req.id, {"status": "matched"})
        return self._build_response(offer)

    async def counter_offer(self, offer_id: UUID, buyer_id: UUID, data: dict) -> dict:
        offer = await self._get_offer(offer_id)
        req = await self.req_repo.get_by_id(offer.requirement_id)
        if not req or req.buyer_id != buyer_id:
            raise RequirementNotFoundError()

        if offer.round_number >= OfferConfig.MAX_COUNTER_OFFERS:
            raise MaxNegotiationRoundsError()

        transition_offer(offer.status, "countered")
        await self.offer_repo.update_offer(offer_id, {
            "status": "countered",
            "responded_at": datetime.now(timezone.utc),
        })

        counter = await self.offer_repo.create_offer({
            "requirement_id": offer.requirement_id,
            "seller_listing_id": offer.seller_listing_id,
            "seller_id": offer.seller_id,
            "offer_price_per_q": data["counter_price_per_q"],
            "quantity_kg": data.get("counter_quantity_kg", offer.quantity_kg),
            "quality_grade": offer.quality_grade,
            "round_number": offer.round_number + 1,
            "parent_offer_id": offer_id,
            "status": "pending",
            "notes": data.get("notes"),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=OfferConfig.RESPONSE_WINDOW_HOURS),
        })
        return self._build_response(counter)

    async def reject_offer(self, offer_id: UUID, buyer_id: UUID) -> dict:
        offer = await self._get_offer(offer_id)
        req = await self.req_repo.get_by_id(offer.requirement_id)
        if not req or req.buyer_id != buyer_id:
            raise RequirementNotFoundError()

        transition_offer(offer.status, "rejected")
        offer = await self.offer_repo.update_offer(offer_id, {
            "status": "rejected",
            "responded_at": datetime.now(timezone.utc),
        })
        return self._build_response(offer)

    async def _get_offer(self, offer_id: UUID):
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise OfferNotFoundError()
        return offer

    def _build_response(self, offer) -> dict:
        return {
            "id": str(offer.id),
            "requirement_id": str(offer.requirement_id),
            "seller_id": str(offer.seller_id) if offer.seller_id else None,
            "offer_price_per_q": float(offer.offer_price_per_q),
            "quantity_kg": float(offer.quantity_kg),
            "quality_grade": offer.quality_grade,
            "round_number": offer.round_number,
            "status": offer.status,
            "counter_price_per_q": float(offer.counter_price_per_q) if offer.counter_price_per_q else None,
            "counter_quantity_kg": float(offer.counter_quantity_kg) if offer.counter_quantity_kg else None,
            "notes": offer.notes,
            "ai_suggestion": offer.ai_suggestion,
            "expires_at": str(offer.expires_at) if offer.expires_at else None,
            "created_at": str(offer.created_at) if offer.created_at else None,
        }
