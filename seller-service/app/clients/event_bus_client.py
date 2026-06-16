"""Redis pub/sub event bus for inter-service events."""

from __future__ import annotations

import json
import logging

from app.config import settings

logger = logging.getLogger(__name__)

CHANNEL = "seller-service-events"


class EventBusClient:
    async def emit_event(self, event_type: str, payload: dict) -> None:
        message = json.dumps({"event": event_type, "payload": payload})

        if not settings.REDIS_URL or settings.ENV == "test":
            logger.info("MOCK event: %s -> %s", event_type, message)
            return

        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        try:
            await r.publish(CHANNEL, message)
            logger.info("Event emitted: %s", event_type)
        finally:
            await r.aclose()
