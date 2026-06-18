"""Browse and discovery service — searches seller listings."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.seller_service_client import SellerServiceClient
from app.repositories.preference_repo import PreferenceRepository


class BrowseService:
    def __init__(self, session: AsyncSession) -> None:
        self.seller_client = SellerServiceClient()
        self.pref_repo = PreferenceRepository(session)

    async def browse_listings(self, filters: dict) -> dict:
        return await self.seller_client.browse_listings(filters)

    async def get_listing(self, listing_id: str) -> dict | None:
        return await self.seller_client.get_listing(listing_id)

    async def save_search(self, buyer_id: UUID, label: str, filters: dict) -> dict:
        pref = await self.pref_repo.create_preference({
            "buyer_id": buyer_id,
            "preference_type": "saved_search",
            "label": label,
            "filter_data": filters,
        })
        return {"id": str(pref.id), "label": pref.label, "filters": pref.filter_data}

    async def add_preferred_seller(self, buyer_id: UUID, seller_id: UUID, notes: str | None = None) -> dict:
        pref = await self.pref_repo.create_preference({
            "buyer_id": buyer_id,
            "preference_type": "preferred_seller",
            "target_seller_id": seller_id,
            "notes": notes,
        })
        return {"id": str(pref.id), "seller_id": str(seller_id)}

    async def create_price_alert(self, buyer_id: UUID, data: dict) -> dict:
        pref = await self.pref_repo.create_preference({
            "buyer_id": buyer_id,
            "preference_type": "price_alert",
            "label": f"{data['crop']} price alert",
            "filter_data": data,
        })
        return {"id": str(pref.id), "crop": data["crop"], "target_price": data.get("target_price_per_q")}
