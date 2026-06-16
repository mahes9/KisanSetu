"""Listing publish & management service — Module 5."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.event_bus_client import EventBusClient
from app.clients.notification_client import NotificationClient
from app.clients.price_client import PriceClient
from app.core.constants import ListingConfig
from app.core.exceptions import (
    AlreadyPublishedError,
    DraftNotFoundError,
    GradeNotSetError,
    KYCNotVerifiedError,
    ListingNotFoundError,
    MaxListingsReachedError,
    MaxPriceEditsError,
    SellerSuspendedError,
)
from app.core.state_machine import transition_listing
from app.core.validators import calculate_payout_preview, validate_floor_price
from app.repositories.draft_repo import DraftRepository
from app.repositories.listing_repo import ListingRepository
from app.repositories.photo_repo import PhotoRepository
from app.repositories.seller_repo import SellerRepository

logger = logging.getLogger(__name__)


class ListingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.listing_repo = ListingRepository(session)
        self.draft_repo = DraftRepository(session)
        self.seller_repo = SellerRepository(session)
        self.photo_repo = PhotoRepository(session)
        self.price_client = PriceClient()
        self.event_bus = EventBusClient()
        self.notification = NotificationClient()

    async def publish_from_draft(
        self, draft_id: UUID, seller_id: UUID, publish_data: dict
    ) -> dict:
        draft = await self.draft_repo.get_draft_for_update(draft_id)
        if not draft:
            raise DraftNotFoundError()
        if draft.draft_status == "published":
            raise AlreadyPublishedError()

        seller = await self.seller_repo.get_for_update(seller_id)
        if seller.kyc_status != "verified":
            raise KYCNotVerifiedError()
        if seller.suspension_until and seller.suspension_until > datetime.now(timezone.utc):
            raise SellerSuspendedError()

        active_count = await self.listing_repo.count_active_listings(seller_id)
        if active_count >= ListingConfig.MAX_ACTIVE_LISTINGS:
            raise MaxListingsReachedError()

        step1 = draft.step1_data or {}
        step2 = draft.step2_data or {}
        crop = step1.get("crop", "tomato")

        if not step2.get("grade"):
            raise GradeNotSetError()

        fresh_price = await self.price_client.get_floor_price(crop, "kurnool")
        ask_price = publish_data.get("ask_price_per_q", 0)
        validate_floor_price(ask_price, fresh_price["floor_price"], fresh_price["modal_price"])

        listing = await self.listing_repo.create_from_draft(
            draft=draft,
            publish_data=publish_data,
            locked_floor=fresh_price["floor_price"],
            locked_modal=fresh_price["modal_price"],
        )

        await self.draft_repo.mark_published(draft_id, listing.id)
        await self.photo_repo.update_listing_id(draft_id, listing.id)

        await self.event_bus.emit_event("listing.published", {
            "listing_id": str(listing.id),
            "listing_number": listing.listing_number,
            "seller_id": str(seller_id),
            "crop": listing.crop,
        })
        await self.notification.send_sms(
            str(seller_id), "listing_published",
            {"crop": listing.crop, "number": listing.listing_number},
        )

        return self._listing_to_dict(listing)

    async def edit_price(
        self, listing_id: UUID, seller_id: UUID, new_price: float, reason: str | None = None
    ) -> dict:
        listing = await self._get_owned_listing(listing_id, seller_id)
        if listing.status not in ("active", "paused"):
            from app.core.exceptions import InvalidStatusTransitionError
            raise InvalidStatusTransitionError(
                message_en="Can only edit price of active or paused listings."
            )
        if listing.price_edit_count >= ListingConfig.MAX_PRICE_EDITS:
            raise MaxPriceEditsError()

        fresh_price = await self.price_client.get_floor_price(listing.crop, "kurnool")
        validate_floor_price(new_price, fresh_price["floor_price"], fresh_price["modal_price"])

        old_price = listing.ask_price_per_q
        listing = await self.listing_repo.update_listing_price(listing_id, new_price, old_price)

        await self.event_bus.emit_event("listing.price_edited", {
            "listing_id": str(listing_id),
            "old_price": old_price,
            "new_price": new_price,
        })
        return self._listing_to_dict(listing)

    async def pause_listing(self, listing_id: UUID, seller_id: UUID) -> dict:
        listing = await self._get_owned_listing(listing_id, seller_id)
        transition_listing(listing.status, "paused")
        listing = await self.listing_repo.update_listing_status(
            listing_id, "paused", paused_at=datetime.now(timezone.utc)
        )
        return self._listing_to_dict(listing)

    async def resume_listing(self, listing_id: UUID, seller_id: UUID) -> dict:
        listing = await self._get_owned_listing(listing_id, seller_id)
        transition_listing(listing.status, "active")
        listing = await self.listing_repo.update_listing_status(
            listing_id, "active", paused_at=None
        )
        return self._listing_to_dict(listing)

    async def cancel_listing(
        self, listing_id: UUID, seller_id: UUID, reason: str
    ) -> dict:
        listing = await self._get_owned_listing(listing_id, seller_id)
        transition_listing(listing.status, "cancelled")
        listing = await self.listing_repo.update_listing_status(
            listing_id, "cancelled",
            cancelled_at=datetime.now(timezone.utc),
            cancellation_reason=reason,
        )

        seller = await self.seller_repo.get_for_update(seller_id)
        new_count = seller.cancellation_count + 1
        await self.seller_repo.update_cancellation_count(seller_id, new_count)
        if new_count >= 3:
            await self.seller_repo.suspend_seller(
                seller_id, datetime.now(timezone.utc) + timedelta(days=30)
            )

        await self.event_bus.emit_event("listing.cancelled", {
            "listing_id": str(listing_id),
            "reason": reason,
        })
        return self._listing_to_dict(listing)

    async def expire_listing(self, listing_id: UUID) -> dict:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing:
            raise ListingNotFoundError()
        transition_listing(listing.status, "expired")
        listing = await self.listing_repo.update_listing_status(listing_id, "expired")
        await self.event_bus.emit_event("listing.expired", {"listing_id": str(listing_id)})
        await self.notification.send_sms(
            str(listing.seller_id), "listing_expired",
            {"crop": listing.crop, "number": listing.listing_number},
        )
        return self._listing_to_dict(listing)

    async def get_listing(self, listing_id: UUID, seller_id: UUID) -> dict:
        listing = await self._get_owned_listing(listing_id, seller_id)
        return self._listing_to_dict(listing)

    async def get_public_listing(self, listing_id: UUID) -> dict:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing:
            raise ListingNotFoundError()
        await self.listing_repo.increment_views(listing_id)
        return {
            "listing_number": listing.listing_number,
            "crop": listing.crop,
            "quantity_kg": listing.quantity_kg,
            "grade": listing.grade,
            "ask_price_per_q": listing.ask_price_per_q,
            "harvest_status": listing.harvest_status,
            "transport_type": listing.transport_type,
            "pickup_window": listing.pickup_window,
            "status": listing.status,
            "expires_at": str(listing.expires_at),
            "views_count": listing.views_count + 1,
            "created_at": str(listing.created_at),
        }

    async def list_my_listings(
        self,
        seller_id: UUID,
        page: int = 1,
        per_page: int = 20,
        status_filter: str | None = None,
    ) -> dict:
        listings, total = await self.listing_repo.get_listings_paginated(
            seller_id, page, per_page, status_filter
        )
        return {
            "listings": [self._listing_to_dict(l) for l in listings],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def _get_owned_listing(self, listing_id: UUID, seller_id: UUID) -> Listing:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing:
            raise ListingNotFoundError()
        if listing.seller_id != seller_id:
            raise ListingNotFoundError(message_en="Listing not found or access denied.")
        return listing

    def _listing_to_dict(self, listing) -> dict:
        now = datetime.now(timezone.utc)
        days_remaining = max(0, (listing.expires_at - now).days) if listing.expires_at else 0
        payout = calculate_payout_preview(
            listing.quantity_kg, listing.ask_price_per_q, listing.modal_price_at_publish
        )
        return {
            "id": str(listing.id),
            "seller_id": str(listing.seller_id),
            "listing_number": listing.listing_number,
            "crop": listing.crop,
            "quantity_kg": listing.quantity_kg,
            "harvest_status": listing.harvest_status,
            "grade": listing.grade,
            "ai_grade_locked": listing.ai_grade_locked,
            "ai_confidence": listing.ai_confidence,
            "ask_price_per_q": listing.ask_price_per_q,
            "floor_price_at_publish": listing.floor_price_at_publish,
            "modal_price_at_publish": listing.modal_price_at_publish,
            "transport_type": listing.transport_type,
            "pickup_window": listing.pickup_window,
            "status": listing.status,
            "price_edit_count": listing.price_edit_count,
            "expires_at": str(listing.expires_at),
            "views_count": listing.views_count,
            "enquiries_count": listing.enquiries_count,
            "created_at": str(listing.created_at) if listing.created_at else None,
            "payout_preview": payout,
            "days_remaining": days_remaining,
            "can_edit_price": listing.price_edit_count < ListingConfig.MAX_PRICE_EDITS,
        }
