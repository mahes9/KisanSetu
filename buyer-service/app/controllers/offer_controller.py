"""Thin controller for offers / negotiation."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.offer_service import OfferService


class OfferController:
    @staticmethod
    async def list_offers(req_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = OfferService(db)
        data = await svc.list_offers(req_id, buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def accept_offer(offer_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = OfferService(db)
        data = await svc.accept_offer(offer_id, buyer.id)
        return StandardResponse(success=True, message="Offer accepted.", data=data)

    @staticmethod
    async def counter_offer(offer_id: UUID, buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = OfferService(db)
        result = await svc.counter_offer(offer_id, buyer.id, data)
        return StandardResponse(success=True, message="Counter offer sent.", data=result)

    @staticmethod
    async def reject_offer(offer_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = OfferService(db)
        data = await svc.reject_offer(offer_id, buyer.id)
        return StandardResponse(success=True, message="Offer rejected.", data=data)
