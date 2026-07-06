"""Event bus client — async event publishing."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class EventBusClient:
    async def emit_event(self, event_name: str, payload: dict) -> None:
        logger.info("Event emitted: %s — %s", event_name, payload.get("id", ""))
