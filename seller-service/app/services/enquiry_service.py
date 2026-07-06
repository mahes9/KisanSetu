"""Enquiry service — business logic for buyer-seller enquiries."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enquiry import Enquiry
from app.repositories.enquiry_repo import EnquiryRepository
from app.repositories.listing_repo import ListingRepository
from app.services.order_service import OrderService


MAX_ENQUIRIES_PER_DAY = 10
MAX_COUNTER_ROUNDS = 3

# Layer 4: phone/email patterns to mask in messages
_PHONE_RE = re.compile(r'\b(\+?\d[\d\s\-]{8,14}\d)\b')
_EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')


def _mask_contact_info(text: str | None) -> str | None:
    if not text:
        return text
    text = _PHONE_RE.sub('[phone hidden]', text)
    text = _EMAIL_RE.sub('[email hidden]', text)
    return text


def _mask_phone(phone: str | None) -> str | None:
    if not phone or len(phone) < 4:
        return "XXXX"
    return "XXXXX" + phone[-4:]


VALID_TRANSITIONS = {
    "pending": ["viewed", "responded", "rejected", "expired", "withdrawn"],
    "viewed": ["responded", "rejected", "expired", "withdrawn"],
    "responded": ["negotiating", "accepted", "rejected", "withdrawn"],
    "negotiating": ["accepted", "rejected", "withdrawn"],
}


class EnquiryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = EnquiryRepository(session)
        self.listing_repo = ListingRepository(session)

    async def create_enquiry(self, listing_id: UUID, data: dict) -> dict:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing:
            raise ValueError("Listing not found")
        if listing.status != "active":
            raise ValueError("Listing is not active")

        buyer_id = data["buyer_id"]

        if await self.repo.check_duplicate(listing_id, buyer_id):
            raise ValueError("You have reached the maximum of 10 active enquiries on this listing")

        if await self.repo.count_buyer_today(buyer_id) >= MAX_ENQUIRIES_PER_DAY:
            raise ValueError(f"Daily enquiry limit reached ({MAX_ENQUIRIES_PER_DAY})")

        data["listing_id"] = listing_id
        data["message"] = _mask_contact_info(data.get("message"))
        enquiry = await self.repo.create(data)
        await self.repo.increment_listing_enquiry_count(listing_id)
        await self.session.commit()

        return self._to_dict(enquiry, listing)

    async def get_enquiries_for_listing(self, listing_id: UUID, seller_id: UUID, page: int = 1, per_page: int = 20) -> dict:
        listing = await self.listing_repo.get_listing_by_id(listing_id)
        if not listing or listing.seller_id != seller_id:
            raise ValueError("Listing not found or access denied")

        enquiries, total = await self.repo.get_for_listing(listing_id, page, per_page)
        return {
            "enquiries": [self._to_dict(e, listing) for e in enquiries],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_enquiries_for_seller(self, seller_id: UUID, status: str | None = None, page: int = 1, per_page: int = 20) -> dict:
        enquiries, total = await self.repo.get_for_seller(seller_id, status, page, per_page)
        items = []
        for e in enquiries:
            listing = await self.listing_repo.get_listing_by_id(e.listing_id)
            items.append(self._to_dict(e, listing))
        return {
            "enquiries": items,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def get_enquiries_for_buyer(self, buyer_id: str, page: int = 1, per_page: int = 20) -> dict:
        enquiries, total = await self.repo.get_for_buyer(buyer_id, page, per_page)
        items = []
        for e in enquiries:
            listing = await self.listing_repo.get_listing_by_id(e.listing_id)
            items.append(self._to_dict(e, listing))
        return {
            "enquiries": items,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

    async def seller_respond(self, enquiry_id: UUID, seller_id: UUID, data: dict) -> dict:
        enquiry = await self._get_owned_enquiry(enquiry_id, seller_id)

        if enquiry.status not in ("pending", "viewed", "negotiating"):
            raise ValueError(f"Cannot respond to enquiry in '{enquiry.status}' status")

        now = datetime.now(timezone.utc)
        updated = await self.repo.update_status(
            enquiry_id,
            status="responded",
            seller_quoted_price=data["quoted_price_per_q"],
            seller_available_qty=data.get("available_quantity_kg"),
            seller_delivery_days=data.get("delivery_within_days"),
            seller_message=_mask_contact_info(data.get("message")),
            seller_responded_at=now,
            viewed_at=enquiry.viewed_at or now,
        )
        await self.session.commit()
        return self._to_dict(updated)

    async def buyer_counter(self, enquiry_id: UUID, buyer_id: str, data: dict) -> dict:
        enquiry = await self.repo.get_by_id(enquiry_id)
        if not enquiry or enquiry.buyer_id != buyer_id:
            raise ValueError("Enquiry not found")
        if enquiry.status != "responded":
            raise ValueError("Can only counter a responded enquiry")
        if enquiry.counter_count >= MAX_COUNTER_ROUNDS:
            raise ValueError(f"Maximum counter rounds ({MAX_COUNTER_ROUNDS}) reached")

        updated = await self.repo.update_status(
            enquiry_id,
            status="negotiating",
            offered_price_per_q=data["offered_price_per_q"],
            quantity_kg=data.get("quantity_kg", enquiry.quantity_kg),
            message=_mask_contact_info(data.get("message")),
            counter_count=enquiry.counter_count + 1,
        )
        await self.session.commit()
        return self._to_dict(updated)

    async def seller_accept(self, enquiry_id: UUID, seller_id: UUID) -> dict:
        enquiry = await self._get_owned_enquiry(enquiry_id, seller_id)
        if enquiry.status not in ("pending", "viewed", "responded", "negotiating"):
            raise ValueError(f"Cannot accept enquiry in '{enquiry.status}' status")

        listing = await self.listing_repo.get_listing_by_id(enquiry.listing_id)

        updated = await self.repo.update_status(
            enquiry_id,
            status="accepted",
            accepted_at=datetime.now(timezone.utc),
        )

        order_svc = OrderService(self.session)
        order = await order_svc.create_from_enquiry(updated, listing)
        await self.session.commit()

        result = self._to_dict(updated, listing)
        result["order"] = order_svc._to_dict(order)
        return result

    async def seller_reject(self, enquiry_id: UUID, seller_id: UUID) -> dict:
        enquiry = await self._get_owned_enquiry(enquiry_id, seller_id)
        if enquiry.status in ("accepted", "rejected", "withdrawn", "expired"):
            raise ValueError(f"Cannot reject enquiry in '{enquiry.status}' status")

        updated = await self.repo.update_status(
            enquiry_id,
            status="rejected",
            rejected_at=datetime.now(timezone.utc),
        )
        await self.session.commit()
        return self._to_dict(updated)

    async def buyer_withdraw(self, enquiry_id: UUID, buyer_id: str) -> dict:
        enquiry = await self.repo.get_by_id(enquiry_id)
        if not enquiry or enquiry.buyer_id != buyer_id:
            raise ValueError("Enquiry not found")
        if enquiry.status in ("accepted", "rejected", "withdrawn", "expired"):
            raise ValueError(f"Cannot withdraw enquiry in '{enquiry.status}' status")

        updated = await self.repo.update_status(
            enquiry_id,
            status="withdrawn",
            withdrawn_at=datetime.now(timezone.utc),
        )
        await self.session.commit()
        return self._to_dict(updated)

    async def mark_viewed(self, enquiry_id: UUID, seller_id: UUID) -> dict:
        enquiry = await self._get_owned_enquiry(enquiry_id, seller_id)
        if enquiry.status == "pending":
            updated = await self.repo.update_status(
                enquiry_id,
                status="viewed",
                viewed_at=datetime.now(timezone.utc),
            )
            await self.session.commit()
            return self._to_dict(updated)
        return self._to_dict(enquiry)

    async def _get_owned_enquiry(self, enquiry_id: UUID, seller_id: UUID) -> Enquiry:
        enquiry = await self.repo.get_by_id(enquiry_id)
        if not enquiry:
            raise ValueError("Enquiry not found")
        listing = await self.listing_repo.get_listing_by_id(enquiry.listing_id)
        if not listing or listing.seller_id != seller_id:
            raise ValueError("Access denied")
        return enquiry

    def _to_dict(self, e: Enquiry, listing=None) -> dict:
        is_accepted = e.status == "accepted"
        d = {
            "id": str(e.id),
            "listing_id": str(e.listing_id),
            "buyer_id": e.buyer_id,
            "buyer_name": e.buyer_name,
            "buyer_phone": e.buyer_phone if is_accepted else _mask_phone(e.buyer_phone),
            "buyer_district": e.buyer_district,
            "quantity_kg": e.quantity_kg,
            "offered_price_per_q": e.offered_price_per_q,
            "delivery_district": e.delivery_district,
            "delivery_pincode": e.delivery_pincode if is_accepted else None,
            "required_by_date": str(e.required_by_date) if e.required_by_date else None,
            "payment_mode": e.payment_mode,
            "message": e.message,
            "status": e.status,
            "seller_quoted_price": e.seller_quoted_price,
            "seller_available_qty": e.seller_available_qty,
            "seller_delivery_days": e.seller_delivery_days,
            "seller_message": e.seller_message,
            "seller_responded_at": str(e.seller_responded_at) if e.seller_responded_at else None,
            "counter_count": e.counter_count,
            "viewed_at": str(e.viewed_at) if e.viewed_at else None,
            "accepted_at": str(e.accepted_at) if e.accepted_at else None,
            "rejected_at": str(e.rejected_at) if e.rejected_at else None,
            "withdrawn_at": str(e.withdrawn_at) if e.withdrawn_at else None,
            "expires_at": str(e.expires_at) if e.expires_at else None,
            "created_at": str(e.created_at) if e.created_at else None,
        }
        if listing:
            d["listing_crop"] = listing.crop
            d["listing_variety"] = listing.variety
            d["listing_price"] = listing.ask_price_per_q
            d["listing_number"] = listing.listing_number
        return d
