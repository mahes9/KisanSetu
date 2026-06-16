"""Farm endpoints — Module 2 (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.post("")
async def create_farm():
    raise NotImplementedError("Module 2 — Farm not yet implemented")


@router.get("/me")
async def get_my_farm():
    raise NotImplementedError("Module 2 — Farm not yet implemented")
