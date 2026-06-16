"""UIDAI Aadhaar verification client — Module 1 (stub/mock)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class UIDAIClient:
    async def send_aadhaar_otp(self, aadhaar: str) -> str:
        logger.info("MOCK Aadhaar OTP sent for hash of %s...", aadhaar[:4])
        return "mock_otp_ref"

    async def verify_aadhaar_otp(self, otp_ref: str, otp: str) -> bool:
        return otp == "123456"
