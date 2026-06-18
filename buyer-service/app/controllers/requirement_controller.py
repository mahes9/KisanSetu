"""Thin controller for requirements (RFQs)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.requirement_service import RequirementService


class RequirementController:
    @staticmethod
    async def create_requirement(buyer, data: dict, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        result = await svc.create_requirement(
            buyer.id, buyer.buyer_type, buyer.kyc_status,
            buyer.suspension_until, getattr(buyer, "org_tier", None), data,
        )
        return StandardResponse(success=True, message="Requirement created.", data=result)

    @staticmethod
    async def get_requirement(req_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        data = await svc.get_requirement(req_id, buyer.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def list_requirements(buyer, status: str | None, page: int, per_page: int, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        data = await svc.list_requirements(buyer.id, status, page, per_page)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def update_requirement(req_id: UUID, buyer, updates: dict, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        data = await svc.update_requirement(req_id, buyer.id, updates)
        return StandardResponse(success=True, message="Requirement updated.", data=data)

    @staticmethod
    async def cancel_requirement(req_id: UUID, buyer, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        data = await svc.cancel_requirement(req_id, buyer.id)
        return StandardResponse(success=True, message="Requirement cancelled.", data=data)

    @staticmethod
    async def extend_requirement(req_id: UUID, buyer, days: int, db: AsyncSession) -> StandardResponse:
        svc = RequirementService(db)
        data = await svc.extend_requirement(req_id, buyer.id, days)
        return StandardResponse(success=True, message="Requirement extended.", data=data)
