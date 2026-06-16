"""Thin controller for the Draft module."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.draft_service import DraftService


class DraftController:
    @staticmethod
    async def create_draft(step1_data: dict, seller, db: AsyncSession) -> StandardResponse:
        svc = DraftService(db)
        data = await svc.create_draft(seller.id, step1_data)
        return StandardResponse(success=True, message="Draft created.", data=data)

    @staticmethod
    async def save_step(
        draft_id: UUID,
        step_number: int,
        step_data: dict,
        seller,
        db: AsyncSession,
        save_trigger: str = "manual",
        device: str | None = None,
        session_id: str | None = None,
        network_type: str | None = None,
    ) -> StandardResponse:
        svc = DraftService(db)
        data = await svc.save_step(
            draft_id, seller.id, step_number, step_data,
            save_trigger=save_trigger, device=device,
            session_id=session_id, network_type=network_type,
        )
        return StandardResponse(success=True, message="Step saved.", data=data)

    @staticmethod
    async def get_draft(draft_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = DraftService(db)
        data = await svc.get_draft(draft_id, seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def list_drafts(seller, db: AsyncSession) -> StandardResponse:
        svc = DraftService(db)
        data = await svc.list_drafts(seller.id)
        return StandardResponse(success=True, data=data)

    @staticmethod
    async def delete_draft(draft_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = DraftService(db)
        await svc.delete_draft(draft_id, seller.id)
        return StandardResponse(success=True, message="Draft deleted.")

    @staticmethod
    async def clone_draft(draft_id: UUID, seller, db: AsyncSession) -> StandardResponse:
        svc = DraftService(db)
        data = await svc.clone_draft(draft_id, seller.id)
        return StandardResponse(success=True, message="Draft cloned.", data=data)
