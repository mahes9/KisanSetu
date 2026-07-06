"""Requirement (RFQ) service — core buyer module."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_client import PriceClient
from app.core.constants import RFQConfig
from app.core.exceptions import (
    RequirementExpiredError,
    RequirementNotFoundError,
    RequirementNotOwnedError,
)
from app.core.state_machine import transition_requirement
from app.core.validators import (
    validate_crop,
    validate_offer_price,
    validate_quantity,
    validate_rfq_preflight,
)
from app.repositories.requirement_repo import RequirementRepository


class RequirementService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = RequirementRepository(session)
        self.price_client = PriceClient()

    async def create_requirement(
        self, buyer_id: UUID, buyer_type: str, kyc_status: str,
        suspension_until, org_tier: str | None, data: dict,
    ) -> dict:
        active_count = await self.repo.count_active_by_buyer(buyer_id)
        validate_rfq_preflight(kyc_status, suspension_until, active_count, buyer_type, org_tier)
        validate_crop(data["crop"])
        validate_quantity(data["quantity_max_kg"], buyer_type)

        if data.get("offer_price_per_q"):
            price_data = await self.price_client.get_market_price(data["crop"])
            validate_offer_price(data["offer_price_per_q"], price_data["modal_price"])
            data["modal_price_at_create"] = price_data["modal_price"]

        if buyer_type == "individual":
            data["gst_invoice_required"] = False

        req_number = self._generate_req_number(data.get("delivery_district", "KNL"))
        expires_at = datetime.now(timezone.utc) + timedelta(days=RFQConfig.REQUIREMENT_DURATION_DAYS)

        req = await self.repo.create_requirement({
            "requirement_number": req_number,
            "buyer_id": buyer_id,
            "crop": data["crop"],
            "variety": data.get("variety"),
            "quantity_min_kg": data["quantity_min_kg"],
            "quantity_max_kg": data["quantity_max_kg"],
            "quality_grade": data.get("quality_grade"),
            "quality_specs": data.get("quality_specs"),
            "price_type": data.get("price_type", "negotiable"),
            "offer_price_per_q": data.get("offer_price_per_q"),
            "modal_price_at_create": data.get("modal_price_at_create"),
            "delivery_location_id": data.get("delivery_location_id"),
            "delivery_district": data.get("delivery_district"),
            "delivery_by_date": data.get("delivery_by_date"),
            "gst_invoice_required": data.get("gst_invoice_required", False),
            "allow_partial_match": data.get("allow_partial_match", True),
            "urgency": data.get("urgency"),
            "notes": data.get("notes"),
            "status": "active",
            "expires_at": expires_at,
        })
        return self._build_response(req)

    async def get_requirement(self, req_id: UUID, buyer_id: UUID) -> dict:
        req = await self._get_owned(req_id, buyer_id)
        return self._build_response(req)

    async def list_requirements(
        self, buyer_id: UUID, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> dict:
        reqs = await self.repo.list_by_buyer(buyer_id, status, page, per_page)
        return {
            "requirements": [self._build_response(r) for r in reqs],
            "total": len(reqs),
            "page": page,
            "per_page": per_page,
        }

    async def update_requirement(self, req_id: UUID, buyer_id: UUID, updates: dict) -> dict:
        req = await self._get_owned(req_id, buyer_id)
        allowed = {"quantity_min_kg", "quantity_max_kg", "quality_grade", "quality_specs",
                    "offer_price_per_q", "delivery_by_date", "notes"}
        filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
        if filtered:
            req = await self.repo.update_requirement(req_id, filtered)
        return self._build_response(req)

    async def cancel_requirement(self, req_id: UUID, buyer_id: UUID) -> dict:
        req = await self._get_owned(req_id, buyer_id)
        transition_requirement(req.status, "cancelled")
        req = await self.repo.update_requirement(req_id, {
            "status": "cancelled",
            "cancelled_at": datetime.now(timezone.utc),
        })
        return self._build_response(req)

    async def extend_requirement(self, req_id: UUID, buyer_id: UUID, days: int = 7) -> dict:
        req = await self._get_owned(req_id, buyer_id)
        if req.status != "active":
            raise RequirementExpiredError()
        new_expiry = (req.expires_at or datetime.now(timezone.utc)) + timedelta(days=days)
        req = await self.repo.update_requirement(req_id, {"expires_at": new_expiry})
        return self._build_response(req)

    async def _get_owned(self, req_id: UUID, buyer_id: UUID):
        req = await self.repo.get_by_id(req_id)
        if not req:
            raise RequirementNotFoundError()
        if req.buyer_id != buyer_id:
            raise RequirementNotOwnedError()
        return req

    def _generate_req_number(self, district_code: str | None) -> str:
        now = datetime.now(timezone.utc)
        random_part = secrets.token_hex(3).upper()
        code = (district_code or "GEN")[:3].upper()
        return f"REQ-{code}-{now.strftime('%Y%m')}-{random_part}"

    def _build_response(self, req) -> dict:
        return {
            "id": str(req.id),
            "requirement_number": req.requirement_number,
            "buyer_id": str(req.buyer_id),
            "crop": req.crop,
            "variety": req.variety,
            "quantity_min_kg": float(req.quantity_min_kg),
            "quantity_max_kg": float(req.quantity_max_kg),
            "quality_grade": req.quality_grade,
            "price_type": req.price_type,
            "offer_price_per_q": float(req.offer_price_per_q) if req.offer_price_per_q else None,
            "ai_suggested_price": float(req.ai_suggested_price) if req.ai_suggested_price else None,
            "delivery_district": req.delivery_district,
            "gst_invoice_required": req.gst_invoice_required,
            "allow_partial_match": req.allow_partial_match,
            "status": req.status,
            "offers_received": req.offers_received,
            "views_count": req.views_count,
            "expires_at": str(req.expires_at) if req.expires_at else None,
            "created_at": str(req.created_at) if req.created_at else None,
        }
