"""Seller service client — browse listings from seller service."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class SellerServiceClient:
    async def browse_listings(self, filters: dict) -> dict:
        if not settings.ENABLE_SELLER_SERVICE:
            return {"items": [], "total": 0}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/listings/public",
                    params={k: v for k, v in filters.items() if v is not None},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        listings = data.get("data", {}).get("listings", [])
                        return {"items": listings, "total": len(listings)}
                return {"items": [], "total": 0}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return {"items": [], "total": 0}

    async def get_listing(self, listing_id: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/listings/{listing_id}/public",
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        return data.get("data")
                return None
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None
