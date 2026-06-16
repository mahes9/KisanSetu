"""Auth endpoints — Module 1 (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-otp")
async def send_otp():
    raise NotImplementedError("Module 1 — Auth not yet implemented")


@router.post("/verify-otp")
async def verify_otp():
    raise NotImplementedError("Module 1 — Auth not yet implemented")


@router.post("/register")
async def register():
    raise NotImplementedError("Module 1 — Auth not yet implemented")


@router.post("/login")
async def login():
    raise NotImplementedError("Module 1 — Auth not yet implemented")
