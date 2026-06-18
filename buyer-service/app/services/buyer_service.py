"""Buyer registration and profile service."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BuyerAlreadyExistsError, BuyerNotFoundError
from app.core.security import hash_aadhaar, hash_password
from app.core.validators import validate_language, validate_phone
from app.repositories.buyer_repo import BuyerRepository


class BuyerService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = BuyerRepository(session)

    async def register_individual(self, data: dict) -> dict:
        validate_phone(data["phone"])
        validate_language(data.get("language", "te"))

        existing = await self.repo.get_by_phone(data["phone"])
        if existing:
            raise BuyerAlreadyExistsError()

        buyer_number = self._generate_buyer_number("IND")
        buyer = await self.repo.create_buyer({
            "buyer_number": buyer_number,
            "buyer_type": "individual",
            "primary_phone": data["phone"],
            "individual_name": data["individual_name"],
            "language": data.get("language", "te"),
            "kyc_status": "pending",
        })
        return self._build_profile(buyer)

    async def register_organization(self, data: dict) -> dict:
        validate_phone(data["phone"])
        validate_language(data.get("language", "en"))

        existing = await self.repo.get_by_phone(data["phone"])
        if existing:
            raise BuyerAlreadyExistsError()

        buyer_number = self._generate_buyer_number("ORG")
        buyer = await self.repo.create_buyer({
            "buyer_number": buyer_number,
            "buyer_type": "organization",
            "primary_phone": data["phone"],
            "primary_email": data.get("primary_email"),
            "company_name": data["company_name"],
            "business_type": data.get("business_type"),
            "buyer_segment": data.get("buyer_segment"),
            "gstin": data.get("gstin"),
            "pan_number": data.get("pan_number"),
            "password_hash": hash_password(data["password"]),
            "language": data.get("language", "en"),
            "kyc_status": "pending",
            "org_tier": "tier_3",
        })
        return self._build_profile(buyer)

    async def get_profile(self, buyer_id: UUID) -> dict:
        buyer = await self.repo.get_by_id(buyer_id)
        if not buyer:
            raise BuyerNotFoundError()
        return self._build_profile(buyer)

    async def update_profile(self, buyer_id: UUID, updates: dict) -> dict:
        allowed = {
            "individual_name", "company_name", "primary_email",
            "preferred_crops", "default_quality_grade", "min_order_kg",
            "device_token", "device_platform", "app_version",
        }
        filtered = {k: v for k, v in updates.items() if k in allowed and v is not None}
        if filtered:
            filtered["last_active_at"] = datetime.now(timezone.utc)
            buyer = await self.repo.update_buyer(buyer_id, filtered)
        else:
            buyer = await self.repo.get_by_id(buyer_id)
        if not buyer:
            raise BuyerNotFoundError()
        return self._build_profile(buyer)

    async def change_language(self, buyer_id: UUID, language: str) -> dict:
        validate_language(language)
        buyer = await self.repo.update_buyer(buyer_id, {"language": language})
        if not buyer:
            raise BuyerNotFoundError()
        return self._build_profile(buyer)

    async def get_kyc_status(self, buyer_id: UUID) -> dict:
        buyer = await self.repo.get_by_id(buyer_id)
        if not buyer:
            raise BuyerNotFoundError()

        result = {
            "buyer_type": buyer.buyer_type,
            "kyc_status": buyer.kyc_status,
            "phone_verified": buyer.phone_verified,
            "email_verified": buyer.email_verified,
            "bank_verified": buyer.bank_verified,
        }
        if buyer.buyer_type == "individual":
            result["aadhaar_verified"] = buyer.aadhaar_verified
            result["upi_verified"] = buyer.upi_verified
            result["next_step"] = self._next_individual_step(buyer)
        else:
            result["gstin_verified"] = buyer.gstin_verified
            result["next_step"] = self._next_org_step(buyer)
        return result

    def _next_individual_step(self, buyer) -> str | None:
        if not buyer.phone_verified:
            return "verify_phone"
        if not buyer.aadhaar_verified:
            return "verify_aadhaar"
        if not buyer.upi_verified:
            return "verify_upi"
        if buyer.kyc_status != "fully_verified":
            return "complete"
        return None

    def _next_org_step(self, buyer) -> str | None:
        if not buyer.phone_verified or not buyer.email_verified:
            return "verify_contact"
        if not buyer.gstin_verified:
            return "verify_gstin"
        if not buyer.bank_verified:
            return "verify_bank"
        if buyer.kyc_status != "fully_verified":
            return "complete"
        return None

    def _generate_buyer_number(self, prefix: str) -> str:
        now = datetime.now(timezone.utc)
        random_part = secrets.token_hex(3).upper()
        return f"BYR-{prefix}-{now.strftime('%Y%m')}-{random_part}"

    def _build_profile(self, buyer) -> dict:
        return {
            "id": str(buyer.id),
            "buyer_number": buyer.buyer_number,
            "buyer_type": buyer.buyer_type,
            "language": buyer.language,
            "primary_phone": buyer.primary_phone,
            "primary_email": buyer.primary_email,
            "individual_name": buyer.individual_name,
            "company_name": buyer.company_name,
            "business_type": buyer.business_type,
            "buyer_segment": buyer.buyer_segment,
            "gstin": buyer.gstin,
            "kyc_status": buyer.kyc_status,
            "trust_score": buyer.trust_score,
            "orders_completed": buyer.orders_completed,
            "avg_rating": float(buyer.avg_rating) if buyer.avg_rating else 0,
            "preferred_crops": buyer.preferred_crops,
            "default_quality_grade": buyer.default_quality_grade,
            "created_at": str(buyer.created_at) if buyer.created_at else None,
        }
