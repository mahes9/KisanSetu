"""Delivery location endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_buyer
from app.controllers.location_controller import LocationController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.location_schema import CreateLocationRequest, UpdateLocationRequest

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("", summary="Add a delivery location")
async def create_location(
    body: CreateLocationRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await LocationController.create_location(buyer, body.model_dump(), db)


@router.get("", summary="List my delivery locations")
async def list_locations(
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await LocationController.list_locations(buyer, db)


@router.patch("/{loc_id}", summary="Update a delivery location")
async def update_location(
    loc_id: UUID,
    body: UpdateLocationRequest,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await LocationController.update_location(loc_id, buyer, body.model_dump(exclude_unset=True), db)


@router.delete("/{loc_id}", summary="Delete a delivery location")
async def delete_location(
    loc_id: UUID,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await LocationController.delete_location(loc_id, buyer, db)


@router.post("/{loc_id}/default", summary="Set as default location")
async def set_default(
    loc_id: UUID,
    buyer: Buyer = Depends(get_current_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await LocationController.set_default(loc_id, buyer, db)
