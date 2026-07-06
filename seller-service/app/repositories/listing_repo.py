"""Listing repository — Module 5."""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ListingConfig
from app.models.listing import Listing


class ListingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_from_draft(
        self,
        draft,
        publish_data: dict,
        locked_floor: float,
        locked_modal: float,
    ) -> Listing:
        now = datetime.now(timezone.utc)
        listing_number = f"KGP-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        step1 = draft.step1_data or {}
        step2 = draft.step2_data or {}
        step3 = draft.step3_data or {}
        step4 = draft.step4_data or {}

        listing = Listing(
            seller_id=draft.seller_id,
            listing_number=listing_number,
            source_draft_id=draft.id,
            crop=step1.get("crop", ""),
            variety=step2.get("variety"),
            quantity_kg=step1.get("quantity_kg", 0),
            harvest_status=step1.get("harvest_status"),
            days_since_harvest=step1.get("days_since_harvest"),
            grade=step2.get("grade", "C"),
            ai_grade_locked=True,
            ai_confidence=step2.get("ai_confidence"),
            ai_provider=step2.get("ai_provider"),
            ask_price_per_q=publish_data.get("ask_price_per_q", 0),
            floor_price_at_publish=locked_floor,
            modal_price_at_publish=locked_modal,
            payment_terms=step3.get("payment_terms"),
            negotiable=step3.get("negotiable") in (True, "yes", "true", "1"),
            price_validity_days=int(step3["price_validity_days"]) if step3.get("price_validity_days") else None,
            transport_type=step4.get("transport_type"),
            pickup_window=step4.get("pickup_window"),
            pickup_date=date.fromisoformat(step4["pickup_date"]) if step4.get("pickup_date") else None,
            pickup_address=step4.get("pickup_address"),
            status="active",
            expires_at=now + timedelta(days=ListingConfig.LISTING_DURATION_DAYS),
        )
        self.session.add(listing)
        await self.session.flush()
        return listing

    async def get_listing_by_id(self, listing_id: UUID) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(Listing.id == listing_id)
        )
        return result.scalar_one_or_none()

    async def get_listing_for_update(self, listing_id: UUID) -> Listing | None:
        result = await self.session.execute(
            select(Listing).where(Listing.id == listing_id).with_for_update()
        )
        return result.scalar_one_or_none()

    async def update_listing_status(
        self, listing_id: UUID, new_status: str, **kwargs
    ) -> Listing:
        values = {"status": new_status, **kwargs}
        await self.session.execute(
            update(Listing).where(Listing.id == listing_id).values(**values)
        )
        await self.session.flush()
        return await self.get_listing_by_id(listing_id)

    async def update_listing_price(
        self, listing_id: UUID, new_price: float, old_price: float
    ) -> Listing:
        listing = await self.get_listing_by_id(listing_id)
        history = list(listing.price_edit_history or [])
        history.append({
            "old_price": old_price,
            "new_price": new_price,
            "edited_at": datetime.now(timezone.utc).isoformat(),
        })
        await self.session.execute(
            update(Listing)
            .where(Listing.id == listing_id)
            .values(
                ask_price_per_q=new_price,
                price_edit_count=listing.price_edit_count + 1,
                price_edit_history=history,
            )
        )
        await self.session.flush()
        return await self.get_listing_by_id(listing_id)

    async def get_active_listings(self, seller_id: UUID) -> list[Listing]:
        result = await self.session.execute(
            select(Listing).where(
                Listing.seller_id == seller_id,
                Listing.status == "active",
            )
        )
        return list(result.scalars().all())

    async def count_active_listings(self, seller_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(Listing.id)).where(
                Listing.seller_id == seller_id,
                Listing.status.in_(["active", "paused", "matched"]),
            )
        )
        return result.scalar() or 0

    async def get_public_listing(self, listing_id: UUID) -> Listing | None:
        return await self.get_listing_by_id(listing_id)

    async def get_expired_listings(self) -> list[Listing]:
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(Listing).where(
                Listing.status == "active",
                Listing.expires_at < now,
            )
        )
        return list(result.scalars().all())

    async def get_listings_paginated(
        self,
        seller_id: UUID,
        page: int = 1,
        per_page: int = 20,
        status_filter: str | None = None,
    ) -> tuple[list[Listing], int]:
        query = select(Listing).where(Listing.seller_id == seller_id)
        count_query = select(func.count(Listing.id)).where(Listing.seller_id == seller_id)

        if status_filter:
            query = query.where(Listing.status == status_filter)
            count_query = count_query.where(Listing.status == status_filter)

        query = query.order_by(Listing.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)

        return list(result.scalars().all()), total_result.scalar() or 0

    async def increment_views(self, listing_id: UUID) -> None:
        await self.session.execute(
            update(Listing)
            .where(Listing.id == listing_id)
            .values(views_count=Listing.views_count + 1)
        )

    async def get_seller_listings_for_season(
        self, seller_id: UUID, start_date: datetime, end_date: datetime
    ) -> list[Listing]:
        result = await self.session.execute(
            select(Listing).where(
                Listing.seller_id == seller_id,
                Listing.created_at >= start_date,
                Listing.created_at <= end_date,
            )
        )
        return list(result.scalars().all())
