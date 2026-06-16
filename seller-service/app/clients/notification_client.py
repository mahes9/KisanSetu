"""Client for the Notification Service (port 8007)."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationClient:
    async def send_sms(
        self, seller_id: str, template: str, data: dict | None = None
    ) -> bool:
        if not settings.ENABLE_NOTIFICATIONS:
            logger.info("MOCK SMS to %s: template=%s data=%s", seller_id, template, data)
            return True

        url = f"{settings.NOTIFICATION_SERVICE_URL}/api/v1/sms/send"
        payload = {"seller_id": seller_id, "template": template, "data": data or {}}
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return True
