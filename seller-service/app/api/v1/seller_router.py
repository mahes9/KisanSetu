"""Seller profile endpoints — Module 2 (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/sellers", tags=["Sellers"])


@router.get("/me")
async def get_profile():
    raise NotImplementedError("Module 2 — Seller profile not yet implemented")


@router.patch("/me")
async def update_profile():
    raise NotImplementedError("Module 2 — Seller profile not yet implemented")
