"""Enquiry repository — DB operations for buyer enquiries."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enquiry import Enquiry
from app.models.listing import Listing


class EnquiryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict) -> Enquiry:
        now = datetime.now(timezone.utc)
        enquiry = Enquiry(
            listing_id=data["listing_id"],
            buyer_id=data["buyer_id"],
            buyer_name=data.get("buyer_name"),
            buyer_phone=data.get("buyer_phone"),
            buyer_district=data.get("buyer_district"),
            quantity_kg=data["quantity_kg"],
            offered_price_per_q=data.get("offered_price_per_q"),
            delivery_district=data.get("delivery_district"),
            delivery_pincode=data.get("delivery_pincode"),
            required_by_date=data.get("required_by_date"),
            payment_mode=data.get("payment_mode"),
            message=data.get("message"),
            status="pending",
            expires_at=now + timedelta(hours=48),
        )
        self.session.add(enquiry)
        await self.session.flush()
        return enquiry

    async def get_by_id(self, enquiry_id: UUID) -> Enquiry | None:
        result = await self.session.execute(
            select(Enquiry).where(Enquiry.id == enquiry_id)
        )
        return result.scalar_one_or_none()

    async def get_for_listing(self, listing_id: UUID, page: int = 1, per_page: int = 20) -> tuple[list[Enquiry], int]:
        query = select(Enquiry).where(Enquiry.listing_id == listing_id)
        count_query = select(func.count(Enquiry.id)).where(Enquiry.listing_id == listing_id)

        query = query.order_by(Enquiry.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)
        return list(result.scalars().all()), total_result.scalar() or 0

    async def get_for_seller(self, seller_id: UUID, status: str | None = None, page: int = 1, per_page: int = 20) -> tuple[list[Enquiry], int]:
        query = (
            select(Enquiry)
            .join(Listing, Enquiry.listing_id == Listing.id)
            .where(Listing.seller_id == seller_id)
        )
        count_query = (
            select(func.count(Enquiry.id))
            .join(Listing, Enquiry.listing_id == Listing.id)
            .where(Listing.seller_id == seller_id)
        )
        if status:
            query = query.where(Enquiry.status == status)
            count_query = count_query.where(Enquiry.status == status)

        query = query.order_by(Enquiry.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)
        return list(result.scalars().all()), total_result.scalar() or 0

    async def get_for_buyer(self, buyer_id: str, page: int = 1, per_page: int = 20) -> tuple[list[Enquiry], int]:
        query = select(Enquiry).where(Enquiry.buyer_id == buyer_id)
        count_query = select(func.count(Enquiry.id)).where(Enquiry.buyer_id == buyer_id)

        query = query.order_by(Enquiry.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        total_result = await self.session.execute(count_query)
        return list(result.scalars().all()), total_result.scalar() or 0

    async def check_duplicate(self, listing_id: UUID, buyer_id: str, max_active: int = 10) -> bool:
        result = await self.session.execute(
            select(func.count(Enquiry.id)).where(
                Enquiry.listing_id == listing_id,
                Enquiry.buyer_id == buyer_id,
                Enquiry.status.in_(["pending", "viewed", "responded", "negotiating"]),
            )
        )
        return (result.scalar() or 0) >= max_active

    async def count_buyer_today(self, buyer_id: str) -> int:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(Enquiry.id)).where(
                Enquiry.buyer_id == buyer_id,
                Enquiry.created_at >= today_start,
            )
        )
        return result.scalar() or 0

    async def update_status(self, enquiry_id: UUID, **kwargs) -> Enquiry:
        await self.session.execute(
            update(Enquiry).where(Enquiry.id == enquiry_id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(enquiry_id)

    async def increment_listing_enquiry_count(self, listing_id: UUID) -> None:
        await self.session.execute(
            update(Listing)
            .where(Listing.id == listing_id)
            .values(enquiries_count=Listing.enquiries_count + 1)
        )
