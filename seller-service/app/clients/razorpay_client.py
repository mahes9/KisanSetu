"""Razorpay bank verification client — Module 2 (stub/mock)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class RazorpayClient:
    async def send_penny_drop(self, bank_account: str, ifsc: str, name: str) -> str:
        logger.info("MOCK penny drop: %s %s %s", bank_account, ifsc, name)
        return "mock_verification_id"

    async def check_penny_drop_status(self, verification_id: str) -> dict:
        return {"status": "success", "verified": True}
