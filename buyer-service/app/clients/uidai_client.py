"""UIDAI client — Aadhaar OTP verification."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class UIDAIClient:
    async def send_otp(self, aadhaar_number: str) -> dict:
        if not settings.ENABLE_AADHAAR_VERIFICATION:
            logger.info("Aadhaar OTP skipped (disabled): %s****", aadhaar_number[:4])
            return {"success": True, "txn_id": "mock-txn-001"}
        # TODO: Call UIDAI Auth API
        return {"success": True}

    async def verify_otp(self, aadhaar_number: str, otp: str, txn_id: str = "") -> dict:
        if not settings.ENABLE_AADHAAR_VERIFICATION:
            logger.info("Aadhaar OTP verification skipped (disabled)")
            return {"success": True, "verified": True}
        # TODO: Call UIDAI Auth API
        return {"success": True, "verified": True}
