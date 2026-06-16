"""Gemini Vision grading service (fallback AI provider)."""

from __future__ import annotations

import json
import logging
import time

from app.config import settings
from app.core.constants import AIConfig
from app.core.exceptions import AIGradingError
from app.services.ai_service.prompts import get_prompt_for_crop

logger = logging.getLogger(__name__)


class GeminiGradingService:
    def __init__(self) -> None:
        self.model_name = settings.GEMINI_MODEL

    async def grade_photos(self, photo_urls: list[str], crop: str) -> dict:
        import google.generativeai as genai

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel(self.model_name)
        prompt = get_prompt_for_crop(crop)

        full_prompt = f"{prompt}\n\nPhoto URLs:\n" + "\n".join(photo_urls)

        start = time.monotonic()
        retries = AIConfig.MAX_RETRIES + 1
        last_error = None

        for attempt in range(retries):
            try:
                response = model.generate_content(full_prompt)
                duration_ms = int((time.monotonic() - start) * 1000)

                raw_text = response.text
                clean = raw_text.strip()
                if clean.startswith("```"):
                    clean = clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                parsed = json.loads(clean)

                return {
                    "grade": parsed.get("grade"),
                    "confidence": parsed.get("confidence", 0),
                    "details": parsed,
                    "ai_provider": "gemini",
                    "model_used": self.model_name,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "duration_ms": duration_ms,
                    "raw_response": raw_text,
                }
            except json.JSONDecodeError as exc:
                last_error = exc
                logger.warning("Gemini returned invalid JSON, attempt %d", attempt + 1)
                continue
            except Exception as exc:
                last_error = exc
                logger.error("Gemini grading failed: %s", exc)
                break

        raise AIGradingError(
            message_en=f"Gemini grading failed: {last_error}"
        )
