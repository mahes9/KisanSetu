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

    async def send_enquiry(self, listing_id: str, data: dict) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/listings/{listing_id}/enquiry",
                    json=data,
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Failed to send enquiry"), "status_code": resp.status_code}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def get_buyer_enquiries(self, buyer_id: str, page: int = 1, per_page: int = 20) -> dict:
        if not settings.ENABLE_SELLER_SERVICE:
            return {"enquiries": [], "total": 0}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/enquiries/buyer/{buyer_id}",
                    params={"page": page, "per_page": per_page},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        return data.get("data", {"enquiries": [], "total": 0})
                return {"enquiries": [], "total": 0}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return {"enquiries": [], "total": 0}

    async def counter_enquiry(self, enquiry_id: str, data: dict) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/enquiries/{enquiry_id}/counter",
                    json=data,
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Counter failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def withdraw_enquiry(self, enquiry_id: str, buyer_id: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/enquiries/{enquiry_id}/withdraw",
                    params={"buyer_id": buyer_id},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Withdraw failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    # ── Order proxy methods ──

    async def get_buyer_orders(self, buyer_id: str, page: int = 1, per_page: int = 20) -> dict:
        if not settings.ENABLE_SELLER_SERVICE:
            return {"orders": [], "total": 0}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/buyer/{buyer_id}",
                    params={"page": page, "per_page": per_page},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("success"):
                        return data.get("data", {"orders": [], "total": 0})
                return {"orders": [], "total": 0}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return {"orders": [], "total": 0}

    async def escrow_pay(self, order_id: str, buyer_id: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/{order_id}/escrow-pay",
                    params={"buyer_id": buyer_id},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Escrow payment failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def confirm_delivery(self, order_id: str, buyer_id: str, otp: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/{order_id}/confirm-delivery",
                    params={"buyer_id": buyer_id, "otp": otp},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Confirmation failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def cancel_order(self, order_id: str, buyer_id: str, reason: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/{order_id}/cancel",
                    json={"cancelled_by": "buyer", "canceller_id": buyer_id, "reason": reason},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Cancel failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def raise_dispute(self, order_id: str, buyer_id: str, reason: str, evidence_url: str | None = None) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/{order_id}/dispute",
                    json={"raised_by": "buyer", "raiser_id": buyer_id, "reason": reason, "evidence_url": evidence_url},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Dispute failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None

    async def get_invoice(self, order_id: str, buyer_id: str) -> dict | None:
        if not settings.ENABLE_SELLER_SERVICE:
            return None
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{settings.SELLER_SERVICE_URL}/api/v1/orders/{order_id}/invoice",
                    params={"requester_id": buyer_id},
                )
                result = resp.json()
                if resp.status_code == 200 and result.get("success"):
                    return result.get("data")
                return {"error": result.get("message_en", "Invoice fetch failed")}
        except Exception as e:
            logger.warning("Seller service unavailable: %s", e)
            return None
