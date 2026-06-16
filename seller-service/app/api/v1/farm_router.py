"""Farm profile endpoints — Module 2.

Farm data is fetched from the Farmer Service (separate microservice).
These endpoints proxy/enrich the data for seller-service consumers.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_seller, require_kyc_verified
from app.controllers.farm_controller import FarmController
from app.db.database import get_db
from app.models.seller import Seller

router = APIRouter(prefix="/farms", tags=["Farm Profile"])


@router.get("/profile", summary="Get my full farmer profile (from Farmer Service)")
async def get_farmer_profile(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.get_farmer_profile(seller, db)


@router.get("", summary="List all my farms (from Farmer Service)")
async def get_my_farms(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.get_farms(seller, db)


@router.get("/bank/status", summary="Get bank/UPI verification status")
async def get_bank_status(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.get_bank_status(seller, db)


@router.get("/publish/readiness", summary="Check if farm profile is ready for publishing")
async def get_publish_readiness(
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.get_publish_readiness(seller, db)


@router.post("/{farm_id}/sync", summary="Sync farm data to seller service (local cache)")
async def sync_farm(
    farm_id: str,
    seller: Seller = Depends(require_kyc_verified),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.sync_farm(farm_id, seller, db)


@router.get("/{farm_id}", summary="Get specific farm detail")
async def get_farm_detail(
    farm_id: str,
    seller: Seller = Depends(get_current_seller),
    db: AsyncSession = Depends(get_db),
):
    return await FarmController.get_farm_detail(farm_id, seller, db)
