"""Farm profile service — Module 2.

Fetches farm data from the Farmer Service (your friend's microservice)
and syncs relevant fields to the local seller-service database.
The Farmer Service is the source of truth for all farm data.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.farmer_service_client import FarmerServiceClient
from app.core.constants import PHASE1_DISTRICTS
from app.core.exceptions import FarmNotFoundError, SellerNotFoundError
from app.repositories.farm_repo import FarmRepository
from app.repositories.seller_repo import SellerRepository

logger = logging.getLogger(__name__)


class FarmService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.farmer_client = FarmerServiceClient()
        self.farm_repo = FarmRepository(session)
        self.seller_repo = SellerRepository(session)

    async def get_farmer_profile(self, seller_id: UUID) -> dict:
        """Fetch complete farmer profile from Farmer Service."""
        profile = await self.farmer_client.get_farmer_profile(str(seller_id))
        if not profile:
            raise SellerNotFoundError(
                message_en="Farmer profile not found in Farmer Service.",
                message_te="రైతు ప్రొఫైల్ రైతు సేవలో కనుగొనబడలేదు.",
            )

        farms = profile.get("farms", [])
        bank_status = await self.farmer_client.get_bank_status(str(seller_id))

        has_phase1_district = any(
            f.get("district", "").lower() in PHASE1_DISTRICTS for f in farms
        )

        return {
            "farmer_id": str(seller_id),
            "full_name": profile.get("full_name", ""),
            "phone": profile.get("phone", ""),
            "farms": farms,
            "bank_status": bank_status,
            "farm_count": len(farms),
            "has_verified_bank": bank_status.get("bank_verified", False),
            "has_farm_in_phase1_district": has_phase1_district,
        }

    async def get_farms(self, seller_id: UUID) -> list[dict]:
        """Get all farms for a seller from Farmer Service."""
        farms = await self.farmer_client.get_farmer_farms(str(seller_id))
        for farm in farms:
            farm["is_phase1_district"] = farm.get("district", "").lower() in PHASE1_DISTRICTS
        return farms

    async def get_farm_detail(self, seller_id: UUID, farm_id: str) -> dict:
        """Get a specific farm by ID."""
        farm = await self.farmer_client.get_farm_by_id(str(seller_id), farm_id)
        if not farm:
            raise FarmNotFoundError()
        farm["is_phase1_district"] = farm.get("district", "").lower() in PHASE1_DISTRICTS
        return farm

    async def get_bank_status(self, seller_id: UUID) -> dict:
        """Get bank/UPI verification status from Farmer Service."""
        return await self.farmer_client.get_bank_status(str(seller_id))

    async def sync_farm_to_local(self, seller_id: UUID, farm_id: str) -> dict:
        """Sync a specific farm from Farmer Service to local DB.

        This is used when a seller selects a farm for a listing, so we have
        a local copy for queries and joins without calling the Farmer Service
        every time.
        """
        farm_data = await self.farmer_client.get_farm_by_id(str(seller_id), farm_id)
        if not farm_data:
            raise FarmNotFoundError(
                message_en="Farm not found in Farmer Service.",
                message_te="వ్యవసాయ క్షేత్రం రైతు సేవలో కనుగొనబడలేదు.",
            )

        existing = await self.farm_repo.get_farm_by_seller(seller_id)
        if existing:
            await self.farm_repo.update_farm(existing.id, {
                "gps_latitude": farm_data.get("gps_latitude"),
                "gps_longitude": farm_data.get("gps_longitude"),
                "district": farm_data.get("district"),
                "village": farm_data.get("village"),
                "acreage": farm_data.get("acreage"),
                "irrigation_type": farm_data.get("irrigation_type"),
                "soil_type": farm_data.get("soil_type"),
                "crops_grown": farm_data.get("crops_grown"),
            })
            logger.info("Updated local farm cache for seller %s", seller_id)
        else:
            await self.farm_repo.create_farm(seller_id, {
                "gps_latitude": farm_data.get("gps_latitude"),
                "gps_longitude": farm_data.get("gps_longitude"),
                "district": farm_data.get("district"),
                "village": farm_data.get("village"),
                "acreage": farm_data.get("acreage"),
                "irrigation_type": farm_data.get("irrigation_type"),
                "soil_type": farm_data.get("soil_type"),
                "crops_grown": farm_data.get("crops_grown"),
            })
            logger.info("Created local farm cache for seller %s", seller_id)

        return farm_data

    async def get_publish_readiness(self, seller_id: UUID) -> dict:
        """Check if seller's farm profile is ready for publishing a listing.

        Returns a dict with check results and any blocking issues.
        """
        profile = await self.farmer_client.get_farmer_profile(str(seller_id))
        if not profile:
            return {
                "ready": False,
                "issues": ["Farmer profile not found. Please register in the Farmer app."],
                "issues_te": ["రైతు ప్రొఫైల్ కనుగొనబడలేదు. దయచేసి రైతు యాప్‌లో నమోదు చేయండి."],
            }

        issues_en = []
        issues_te = []
        farms = profile.get("farms", [])
        bank_status = await self.farmer_client.get_bank_status(str(seller_id))

        if not farms:
            issues_en.append("No farm registered. Please add a farm in the Farmer app.")
            issues_te.append("వ్యవసాయ క్షేత్రం నమోదు కాలేదు. దయచేసి రైతు యాప్‌లో జోడించండి.")

        has_phase1 = any(f.get("district", "").lower() in PHASE1_DISTRICTS for f in farms)
        if farms and not has_phase1:
            issues_en.append(f"No farm in Phase 1 districts ({', '.join(PHASE1_DISTRICTS)}). KisanSetu currently operates in Kurnool and Nandyal only.")
            issues_te.append("ఫేజ్ 1 జిల్లాలలో వ్యవసాయ క్షేత్రం లేదు. KisanSetu ప్రస్తుతం కర్నూల్ మరియు నంద్యాల్‌లో మాత్రమే పనిచేస్తుంది.")

        has_gps = any(f.get("gps_latitude") and f.get("gps_longitude") for f in farms)
        if farms and not has_gps:
            issues_en.append("Farm GPS location not set. Please update in the Farmer app.")
            issues_te.append("వ్యవసాయ క్షేత్రం GPS స్థానం సెట్ కాలేదు. దయచేసి రైతు యాప్‌లో అప్‌డేట్ చేయండి.")

        if not bank_status.get("bank_verified") and not bank_status.get("upi_verified"):
            issues_en.append("Bank or UPI not verified. Please verify payment details in the Farmer app.")
            issues_te.append("బ్యాంక్ లేదా UPI ధృవీకరించబడలేదు. దయచేసి రైతు యాప్‌లో చెల్లింపు వివరాలను ధృవీకరించండి.")

        return {
            "ready": len(issues_en) == 0,
            "issues": issues_en,
            "issues_te": issues_te,
            "farm_count": len(farms),
            "has_phase1_farm": has_phase1,
            "bank_verified": bank_status.get("bank_verified", False),
            "upi_verified": bank_status.get("upi_verified", False),
        }
