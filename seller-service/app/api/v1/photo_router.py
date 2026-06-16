"""Photo upload and AI grading endpoints — Module 4."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_kyc_verified
from app.controllers.photo_controller import PhotoController
from app.db.database import get_db
from app.models.seller import Seller

router = APIRouter(prefix="/drafts", tags=["Photos & Grading"])


@router.post("/{draft_id}/photos", summary="Upload 3 listing photos")
async def upload_photos(
    draft_id: UUID,
    files: list[UploadFile] = File(...),
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await PhotoController.upload_photos(draft_id, files, seller, db)


@router.post("/{draft_id}/grade", summary="Trigger AI grading")
async def trigger_grading(
    draft_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await PhotoController.trigger_grading(draft_id, seller, db)


@router.get("/{draft_id}/grade", summary="Get grading status / result")
async def get_grading_status(
    draft_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await PhotoController.get_grading_status(draft_id, seller, db)
