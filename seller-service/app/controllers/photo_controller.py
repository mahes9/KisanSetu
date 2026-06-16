"""Photo upload and AI grading controller — Module 4."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common_schema import StandardResponse
from app.services.photo_service import PhotoService


class PhotoController:
    @staticmethod
    async def upload_photos(
        draft_id: UUID, files: list, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = PhotoService(db)
        data = await svc.upload_photos(draft_id, seller.id, files)
        return StandardResponse(success=True, message="Photos uploaded.", data=data)

    @staticmethod
    async def trigger_grading(
        draft_id: UUID, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = PhotoService(db)
        data = await svc.trigger_grading(draft_id, seller.id)
        return StandardResponse(success=True, message="Grading initiated.", data=data)

    @staticmethod
    async def get_grading_status(
        draft_id: UUID, seller, db: AsyncSession
    ) -> StandardResponse:
        svc = PhotoService(db)
        data = await svc.get_grading_status(draft_id, seller.id)
        return StandardResponse(success=True, data=data)
