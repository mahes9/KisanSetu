"""AI grading orchestrator: Claude -> Gemini -> Manual fallback."""

from __future__ import annotations

import logging

from app.core.constants import AIConfig
from app.core.exceptions import AIGradingError
from app.services.ai_service.claude_service import ClaudeGradingService
from app.services.ai_service.gemini_service import GeminiGradingService

logger = logging.getLogger(__name__)


class AIGradingRouter:
    def __init__(self) -> None:
        self.claude = ClaudeGradingService()
        self.gemini = GeminiGradingService()

    async def grade(self, photo_urls: list[str], crop: str) -> dict:
        # Try Claude first
        try:
            result = await self.claude.grade_photos(photo_urls, crop)
            logger.info("Claude grading succeeded: grade=%s", result.get("grade"))
        except AIGradingError:
            logger.warning("Claude failed, falling back to Gemini")
            # Try Gemini fallback
            try:
                result = await self.gemini.grade_photos(photo_urls, crop)
                logger.info("Gemini grading succeeded: grade=%s", result.get("grade"))
            except AIGradingError:
                logger.warning("Gemini also failed, returning manual fallback")
                return {
                    "grade": None,
                    "confidence": 0,
                    "details": {},
                    "ai_provider": "manual",
                    "model_used": None,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "duration_ms": 0,
                    "raw_response": None,
                    "requires_manual_grading": True,
                    "low_confidence_warning": False,
                }

        confidence = result.get("confidence", 0)
        result["low_confidence_warning"] = confidence < AIConfig.CONFIDENCE_THRESHOLD
        result["requires_manual_grading"] = False
        return result
