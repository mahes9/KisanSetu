"""Notification service client — SMS and push notifications."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationClient:
    async def send_sms(self, phone: str, template: str, context: dict, language: str = "en") -> None:
        if not settings.ENABLE_NOTIFICATIONS:
            logger.info("Notification skipped (disabled): %s -> %s", template, phone)
            return
        # TODO: Call notification service
        logger.info("SMS sent: %s -> %s", template, phone)

    async def send_push(self, device_token: str, title: str, body: str, data: dict | None = None) -> None:
        if not settings.ENABLE_NOTIFICATIONS:
            logger.info("Push notification skipped (disabled): %s", title)
            return
        # TODO: Call FCM via notification service
        logger.info("Push sent: %s", title)
