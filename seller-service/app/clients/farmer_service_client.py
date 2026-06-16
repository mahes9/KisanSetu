"""Client for the Farmer Service (port 8002).

Fetches farm profiles that farmers register in the Farmer app.
When ENABLE_FARMER_SERVICE is False, returns mock data for development.
"""

from __future__ import annotations

import logging
from uuid import UUID

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

MOCK_FARM_PROFILES: dict[str, dict] = {
    "11111111-1111-1111-1111-111111111111": {
        "farmer_id": "11111111-1111-1111-1111-111111111111",
        "full_name": "Ramesh Kumar",
        "phone": "9876543210",
        "farms": [
            {
                "farm_id": "aaaa1111-1111-1111-1111-111111111111",
                "farm_name": "Ramesh Farm - Kurnool",
                "gps_latitude": 15.8281,
                "gps_longitude": 78.0373,
                "district": "kurnool",
                "village": "Orvakal",
                "acreage": 5.5,
                "irrigation_type": "borewell",
                "soil_type": "red_soil",
                "crops_grown": ["tomato", "chilli_dry", "groundnut"],
            },
        ],
        "bank_verified": True,
        "upi_id": "ramesh@upi",
        "upi_verified": True,
        "bank_account": "1234567890",
        "bank_ifsc": "SBIN0001234",
    },
    "22222222-2222-2222-2222-222222222222": {
        "farmer_id": "22222222-2222-2222-2222-222222222222",
        "full_name": "Lakshmi Devi",
        "phone": "9876543211",
        "farms": [
            {
                "farm_id": "bbbb2222-2222-2222-2222-222222222222",
                "farm_name": "Lakshmi Farm - Nandyal",
                "gps_latitude": 15.4780,
                "gps_longitude": 78.4836,
                "district": "nandyal",
                "village": "Banaganapalle",
                "acreage": 3.0,
                "irrigation_type": "canal",
                "soil_type": "black_soil",
                "crops_grown": ["chilli_green", "groundnut"],
            },
        ],
        "bank_verified": False,
        "upi_id": None,
        "upi_verified": False,
        "bank_account": None,
        "bank_ifsc": None,
    },
    "33333333-3333-3333-3333-333333333333": {
        "farmer_id": "33333333-3333-3333-3333-333333333333",
        "full_name": "Suresh Reddy",
        "phone": "9876543212",
        "farms": [],
        "bank_verified": True,
        "upi_id": "suresh@upi",
        "upi_verified": True,
        "bank_account": "9876543210",
        "bank_ifsc": "HDFC0004567",
    },
}


class FarmerServiceClient:
    """Fetches farmer profile and farm data from the Farmer Service."""

    async def get_farmer_profile(self, farmer_id: str) -> dict | None:
        if not settings.ENABLE_FARMER_SERVICE:
            profile = MOCK_FARM_PROFILES.get(farmer_id)
            logger.info("MOCK farmer profile for %s: %s", farmer_id, "found" if profile else "not found")
            return profile

        url = f"{settings.FARMER_SERVICE_URL}/api/v1/farmers/{farmer_id}/profile"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json().get("data")
        except httpx.HTTPError:
            logger.exception("Failed to fetch farmer profile for %s", farmer_id)
            return None

    async def get_farmer_farms(self, farmer_id: str) -> list[dict]:
        profile = await self.get_farmer_profile(farmer_id)
        if not profile:
            return []
        return profile.get("farms", [])

    async def get_farm_by_id(self, farmer_id: str, farm_id: str) -> dict | None:
        farms = await self.get_farmer_farms(farmer_id)
        for farm in farms:
            if farm.get("farm_id") == farm_id:
                return farm
        return None

    async def get_bank_status(self, farmer_id: str) -> dict:
        if not settings.ENABLE_FARMER_SERVICE:
            profile = MOCK_FARM_PROFILES.get(farmer_id, {})
            return {
                "bank_verified": profile.get("bank_verified", False),
                "upi_id": profile.get("upi_id"),
                "upi_verified": profile.get("upi_verified", False),
                "bank_account": profile.get("bank_account"),
                "bank_ifsc": profile.get("bank_ifsc"),
            }

        url = f"{settings.FARMER_SERVICE_URL}/api/v1/farmers/{farmer_id}/bank-status"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json().get("data", {})
        except httpx.HTTPError:
            logger.exception("Failed to fetch bank status for %s", farmer_id)
            return {"bank_verified": False, "upi_verified": False}
