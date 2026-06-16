"""Draft CRUD endpoints — Module 3."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_kyc_verified
from app.controllers.draft_controller import DraftController
from app.db.database import get_db
from app.models.seller import Seller
from app.schemas.draft_schema import CreateDraftRequest, SaveDraftRequest

router = APIRouter(prefix="/drafts", tags=["Drafts"])


@router.post("", summary="Create a new listing draft")
async def create_draft(
    body: CreateDraftRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.create_draft(body.step1.model_dump(), seller, db)


@router.post("/{draft_id}/step/{step_number}", summary="Save step data")
async def save_step(
    draft_id: UUID,
    step_number: int,
    body: SaveDraftRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.save_step(
        draft_id, step_number, body.step_data, seller, db,
        save_trigger=body.save_trigger, device=body.device,
        session_id=body.session_id, network_type=body.network_type,
    )


@router.post("/{draft_id}/save", summary="Auto-save partial draft data")
async def save_partial(
    draft_id: UUID,
    body: SaveDraftRequest,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.save_step(
        draft_id, body.step_number, body.step_data, seller, db,
        save_trigger="auto_save", device=body.device,
        session_id=body.session_id, network_type=body.network_type,
    )


@router.get("/{draft_id}", summary="Get draft detail")
async def get_draft(
    draft_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.get_draft(draft_id, seller, db)


@router.get("", summary="List all my drafts")
async def list_drafts(
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.list_drafts(seller, db)


@router.delete("/{draft_id}", summary="Delete a draft")
async def delete_draft(
    draft_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.delete_draft(draft_id, seller, db)


@router.post("/{draft_id}/clone", summary="Clone an existing draft")
async def clone_draft(
    draft_id: UUID,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await DraftController.clone_draft(draft_id, seller, db)
