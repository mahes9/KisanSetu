"""GSTN API client — GSTIN verification."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class GSTNClient:
    async def verify_gstin(self, gstin: str) -> dict:
        if not settings.ENABLE_GSTIN_VERIFICATION:
            logger.info("GSTIN verification skipped (disabled): %s", gstin)
            return {
                "success": True,
                "gstin": gstin,
                "legal_name": "Mock Business Pvt Ltd",
                "trade_name": "Mock Trade",
                "status": "Active",
                "state": "Andhra Pradesh",
            }
        # TODO: Call GSTN Public Search API
        return {"success": True, "gstin": gstin}
