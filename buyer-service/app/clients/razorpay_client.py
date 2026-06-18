"""Razorpay client — UPI verification and penny drop."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class RazorpayClient:
    async def verify_upi(self, upi_id: str) -> dict:
        if not settings.ENABLE_UPI_VERIFICATION:
            logger.info("UPI verification skipped (disabled): %s", upi_id)
            return {"success": True, "vpa": upi_id, "name": "Mock Name"}
        # TODO: Call Razorpay VPA validation API
        return {"success": True, "vpa": upi_id}

    async def penny_drop(self, account: str, ifsc: str, name: str) -> dict:
        if not settings.ENABLE_BANK_VERIFICATION:
            logger.info("Penny drop skipped (disabled): %s", account)
            return {"success": True, "account": account, "ifsc": ifsc, "name_match": True}
        # TODO: Call Razorpay penny drop API
        return {"success": True, "account": account, "ifsc": ifsc}
