"""Requirement (RFQ) endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_kyc_verified
from app.controllers.requirement_controller import RequirementController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.requirement_schema import (
    CreateRequirementRequest,
    ExtendRequirementRequest,
    UpdateRequirementRequest,
)

router = APIRouter(prefix="/requirements", tags=["Requirements"])


@router.post("", summary="Create a new requirement")
async def create_requirement(
    body: CreateRequirementRequest,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.create_requirement(buyer, body.model_dump(), db)


@router.get("", summary="List my requirements")
async def list_requirements(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.list_requirements(buyer, status, page, per_page, db)


@router.get("/{req_id}", summary="Get requirement detail")
async def get_requirement(
    req_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.get_requirement(req_id, buyer, db)


@router.patch("/{req_id}", summary="Update a requirement")
async def update_requirement(
    req_id: UUID,
    body: UpdateRequirementRequest,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.update_requirement(req_id, buyer, body.model_dump(exclude_unset=True), db)


@router.post("/{req_id}/cancel", summary="Cancel a requirement")
async def cancel_requirement(
    req_id: UUID,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.cancel_requirement(req_id, buyer, db)


@router.post("/{req_id}/extend", summary="Extend requirement expiry")
async def extend_requirement(
    req_id: UUID,
    body: ExtendRequirementRequest,
    buyer: Buyer = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await RequirementController.extend_requirement(req_id, buyer, body.extend_days, db)
