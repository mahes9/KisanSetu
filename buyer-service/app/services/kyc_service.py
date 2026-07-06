"""KYC verification service — handles both individual and org flows."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.gstn_client import GSTNClient
from app.clients.razorpay_client import RazorpayClient
from app.clients.uidai_client import UIDAIClient
from app.core.exceptions import (
    AadhaarVerificationError,
    BankVerificationError,
    BuyerNotFoundError,
    GSTINVerificationError,
    InvalidKYCTransitionError,
    UPIVerificationError,
)
from app.core.security import hash_aadhaar
from app.core.state_machine import validate_kyc_transition
from app.repositories.buyer_repo import BuyerRepository
from app.repositories.kyc_repo import KycRepository


class KYCService:
    def __init__(self, session: AsyncSession) -> None:
        self.buyer_repo = BuyerRepository(session)
        self.kyc_repo = KycRepository(session)
        self.uidai = UIDAIClient()
        self.razorpay = RazorpayClient()
        self.gstn = GSTNClient()

    async def verify_phone(self, buyer_id: UUID, phone: str, otp: str) -> dict:
        buyer = await self._get_buyer(buyer_id)
        updates = {"phone_verified": True}
        if buyer.buyer_type == "individual":
            updates["kyc_status"] = "phone_verified"
        else:
            if buyer.email_verified:
                updates["kyc_status"] = "contact_verified"
        await self.buyer_repo.update_buyer(buyer_id, updates)
        await self._log_verification(buyer_id, "phone", True)
        return {"verified": True, "type": "phone"}

    async def verify_aadhaar(self, buyer_id: UUID, aadhaar_number: str, otp: str) -> dict:
        buyer = await self._get_buyer(buyer_id)
        result = await self.uidai.verify_otp(aadhaar_number, otp)
        if not result.get("verified"):
            await self._log_verification(buyer_id, "aadhaar", False, "OTP mismatch")
            raise AadhaarVerificationError()

        await self.buyer_repo.update_buyer(buyer_id, {
            "aadhaar_hash": hash_aadhaar(aadhaar_number),
            "aadhaar_verified": True,
            "aadhaar_verified_at": datetime.now(timezone.utc),
            "kyc_status": "aadhaar_verified",
        })
        await self._log_verification(buyer_id, "aadhaar", True)
        return {"verified": True, "type": "aadhaar"}

    async def verify_gstin(self, buyer_id: UUID, gstin: str) -> dict:
        buyer = await self._get_buyer(buyer_id)
        result = await self.gstn.verify_gstin(gstin)
        if not result.get("success"):
            await self._log_verification(buyer_id, "gstin", False, "GSTN API failure")
            raise GSTINVerificationError()

        await self.buyer_repo.update_buyer(buyer_id, {
            "gstin": gstin,
            "gstin_verified": True,
            "kyc_status": "gstin_verified",
        })
        await self._log_verification(buyer_id, "gstin", True)
        return {"verified": True, "type": "gstin", "details": result}

    async def verify_bank(self, buyer_id: UUID, account: str, ifsc: str, holder_name: str) -> dict:
        buyer = await self._get_buyer(buyer_id)
        result = await self.razorpay.penny_drop(account, ifsc, holder_name)
        if not result.get("success"):
            await self._log_verification(buyer_id, "bank", False, "Penny drop failed")
            raise BankVerificationError()

        updates: dict = {
            "bank_account": account,
            "bank_ifsc": ifsc,
            "bank_holder_name": holder_name,
            "bank_verified": True,
        }
        if buyer.buyer_type == "organization":
            updates["kyc_status"] = "fully_verified"

        await self.buyer_repo.update_buyer(buyer_id, updates)
        await self._log_verification(buyer_id, "bank", True)
        return {"verified": True, "type": "bank"}

    async def verify_upi(self, buyer_id: UUID, upi_id: str) -> dict:
        buyer = await self._get_buyer(buyer_id)
        result = await self.razorpay.verify_upi(upi_id)
        if not result.get("success"):
            await self._log_verification(buyer_id, "upi", False, "UPI VPA invalid")
            raise UPIVerificationError()

        await self.buyer_repo.update_buyer(buyer_id, {
            "upi_id": upi_id,
            "upi_verified": True,
            "kyc_status": "fully_verified",
        })
        await self._log_verification(buyer_id, "upi", True)
        return {"verified": True, "type": "upi"}

    async def _get_buyer(self, buyer_id: UUID):
        buyer = await self.buyer_repo.get_by_id(buyer_id)
        if not buyer:
            raise BuyerNotFoundError()
        return buyer

    async def _log_verification(
        self, buyer_id: UUID, v_type: str, success: bool, reason: str | None = None
    ) -> None:
        await self.kyc_repo.create_verification({
            "buyer_id": buyer_id,
            "verification_type": v_type,
            "status": "success" if success else "failed",
            "success": success,
            "failure_reason": reason,
        })
