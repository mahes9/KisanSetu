"""Delivery location service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LocationNotFoundError, LocationNotOwnedError
from app.core.validators import validate_district, validate_location_limit
from app.repositories.location_repo import LocationRepository


class LocationService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = LocationRepository(session)

    async def create_location(self, buyer_id: UUID, buyer_type: str, data: dict) -> dict:
        count = await self.repo.count_by_buyer(buyer_id)
        validate_location_limit(count, buyer_type)
        validate_district(data["district"])

        is_first = count == 0
        location = await self.repo.create_location({
            "buyer_id": buyer_id,
            "label": data.get("label", "default"),
            "address_line1": data["address_line1"],
            "address_line2": data.get("address_line2"),
            "village": data.get("village"),
            "mandal": data.get("mandal"),
            "district": data["district"],
            "state": data.get("state", "Andhra Pradesh"),
            "pincode": data["pincode"],
            "gps_lat": data.get("gps_lat"),
            "gps_lon": data.get("gps_lon"),
            "contact_name": data.get("contact_name"),
            "contact_phone": data.get("contact_phone"),
            "is_default": is_first,
            "notes": data.get("notes"),
        })
        return self._build_response(location)

    async def list_locations(self, buyer_id: UUID) -> dict:
        locations = await self.repo.list_by_buyer(buyer_id)
        return {
            "locations": [self._build_response(l) for l in locations],
            "total": len(locations),
        }

    async def update_location(self, location_id: UUID, buyer_id: UUID, updates: dict) -> dict:
        location = await self._get_owned(location_id, buyer_id)
        if "district" in updates and updates["district"]:
            validate_district(updates["district"])
        filtered = {k: v for k, v in updates.items() if v is not None}
        if filtered:
            location = await self.repo.update_location(location_id, filtered)
        return self._build_response(location)

    async def delete_location(self, location_id: UUID, buyer_id: UUID) -> None:
        await self._get_owned(location_id, buyer_id)
        await self.repo.delete_location(location_id)

    async def set_default(self, location_id: UUID, buyer_id: UUID) -> dict:
        location = await self._get_owned(location_id, buyer_id)
        await self.repo.set_default(location_id, buyer_id)
        location = await self.repo.get_by_id(location_id)
        return self._build_response(location)

    async def _get_owned(self, location_id: UUID, buyer_id: UUID):
        location = await self.repo.get_by_id(location_id)
        if not location:
            raise LocationNotFoundError()
        if location.buyer_id != buyer_id:
            raise LocationNotOwnedError()
        return location

    def _build_response(self, location) -> dict:
        return {
            "id": str(location.id),
            "buyer_id": str(location.buyer_id),
            "label": location.label,
            "address_line1": location.address_line1,
            "address_line2": location.address_line2,
            "village": location.village,
            "mandal": location.mandal,
            "district": location.district,
            "state": location.state,
            "pincode": location.pincode,
            "gps_lat": float(location.gps_lat) if location.gps_lat else None,
            "gps_lon": float(location.gps_lon) if location.gps_lon else None,
            "contact_name": location.contact_name,
            "contact_phone": location.contact_phone,
            "is_default": location.is_default,
            "notes": location.notes,
        }
