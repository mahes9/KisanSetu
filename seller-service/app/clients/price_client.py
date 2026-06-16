"""Client for the Price Intelligence Service (port 8006)."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

MOCK_PRICES: dict[str, float] = {
    "tomato": 1240.0,
    "chilli_dry": 8500.0,
    "chilli_green": 3200.0,
    "groundnut": 5500.0,
}


class PriceClient:
    async def get_floor_price(self, crop: str, district: str) -> dict:
        if not settings.ENABLE_REAL_PRICE_DATA:
            modal = MOCK_PRICES.get(crop, 1000.0)
            floor = round(modal * 0.85, 2)
            return {
                "modal_price": modal,
                "floor_price": floor,
                "min_price": round(modal * 0.70, 2),
                "max_price": round(modal * 1.20, 2),
            }

        url = f"{settings.PRICE_SERVICE_URL}/api/v1/prices/{crop}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, params={"district": district})
            resp.raise_for_status()
            data = resp.json()
            return {
                "modal_price": data["modal_price"],
                "floor_price": data["floor_price"],
                "min_price": data.get("min_price"),
                "max_price": data.get("max_price"),
            }
