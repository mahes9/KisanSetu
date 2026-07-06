"""Enquiry controller — thin layer between router and service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.enquiry_service import EnquiryService


class EnquiryController:
    @staticmethod
    async def create_enquiry(listing_id: UUID, data: dict, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.create_enquiry(listing_id, data)
        return StandardResponse(success=True, message="Enquiry sent!", data=result)

    @staticmethod
    async def get_listing_enquiries(listing_id: UUID, seller, db: AsyncSession, page: int = 1, per_page: int = 20) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.get_enquiries_for_listing(listing_id, seller.id, page, per_page)
        return StandardResponse(success=True, data=result)

    @staticmethod
    async def get_seller_enquiries(seller, db: AsyncSession, status: str | None = None, page: int = 1, per_page: int = 20) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.get_enquiries_for_seller(seller.id, status, page, per_page)
        return StandardResponse(success=True, data=result)

    @staticmethod
    async def get_buyer_enquiries(buyer_id: str, db: AsyncSession, page: int = 1, per_page: int = 20) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.get_enquiries_for_buyer(buyer_id, page, per_page)
        return StandardResponse(success=True, data=result)

    @staticmethod
    async def seller_respond(enquiry_id: UUID, seller, data: dict, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.seller_respond(enquiry_id, seller.id, data)
        return StandardResponse(success=True, message="Response sent.", data=result)

    @staticmethod
    async def buyer_counter(enquiry_id: UUID, buyer_id: str, data: dict, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.buyer_counter(enquiry_id, buyer_id, data)
        return StandardResponse(success=True, message="Counter offer sent.", data=result)

    @staticmethod
    async def seller_accept(enquiry_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.seller_accept(enquiry_id, seller.id)
        return StandardResponse(success=True, message="Enquiry accepted!", data=result)

    @staticmethod
    async def seller_reject(enquiry_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.seller_reject(enquiry_id, seller.id)
        return StandardResponse(success=True, message="Enquiry rejected.", data=result)

    @staticmethod
    async def buyer_withdraw(enquiry_id: UUID, buyer_id: str, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.buyer_withdraw(enquiry_id, buyer_id)
        return StandardResponse(success=True, message="Enquiry withdrawn.", data=result)

    @staticmethod
    async def mark_viewed(enquiry_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = EnquiryService(db)
        result = await svc.mark_viewed(enquiry_id, seller.id)
        return StandardResponse(success=True, data=result)
