"""Claude Vision grading service (primary AI provider)."""

from __future__ import annotations

import json
import logging
import time

import anthropic

from app.config import settings
from app.core.constants import AIConfig
from app.core.exceptions import AIGradingError
from app.services.ai_service.prompts import get_prompt_for_crop

logger = logging.getLogger(__name__)


class ClaudeGradingService:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL

    async def grade_photos(self, photo_urls: list[str], crop: str) -> dict:
        prompt = get_prompt_for_crop(crop)
        image_content = []
        for url in photo_urls:
            image_content.append({
                "type": "image",
                "source": {"type": "url", "url": url},
            })
        image_content.append({"type": "text", "text": prompt})

        start = time.monotonic()
        retries = AIConfig.MAX_RETRIES + 1
        last_error = None

        for attempt in range(retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": image_content}],
                    timeout=AIConfig.GRADING_TIMEOUT_SECONDS,
                )

                duration_ms = int((time.monotonic() - start) * 1000)
                raw_text = response.content[0].text
                parsed = json.loads(raw_text)

                return {
                    "grade": parsed.get("grade"),
                    "confidence": parsed.get("confidence", 0),
                    "details": parsed,
                    "ai_provider": "claude",
                    "model_used": self.model,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "duration_ms": duration_ms,
                    "raw_response": raw_text,
                }
            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning("Claude returned invalid JSON, attempt %d", attempt + 1)
                continue
            except Exception as exc:
                last_error = exc
                logger.error("Claude grading failed: %s", exc)
                break

        raise AIGradingError(
            message_en=f"Claude grading failed: {last_error}"
        )
