"""Price service client — fetches market prices."""

from __future__ import annotations

from app.config import settings

MOCK_PRICES: dict[str, dict] = {
    "tomato": {"modal_price": 1240.0, "floor_price": 868.0, "min_price": 800.0, "max_price": 1600.0},
    "chilli_dry": {"modal_price": 8500.0, "floor_price": 5950.0, "min_price": 5000.0, "max_price": 12000.0},
    "chilli_green": {"modal_price": 2800.0, "floor_price": 1960.0, "min_price": 1500.0, "max_price": 4000.0},
    "groundnut": {"modal_price": 5200.0, "floor_price": 3640.0, "min_price": 4000.0, "max_price": 6500.0},
}


class PriceClient:
    async def get_market_price(self, crop: str, district: str = "kurnool") -> dict:
        if not settings.ENABLE_REAL_PRICE_DATA:
            return MOCK_PRICES.get(crop.lower(), MOCK_PRICES["tomato"])

        # TODO: Call real price service
        return MOCK_PRICES.get(crop.lower(), MOCK_PRICES["tomato"])
