"""Integration tests for the AI Grading module — mocked AI clients."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.core.constants import AIConfig
from app.core.exceptions import AIGradingError, DuplicatePhotoError
from app.services.ai_service.ai_router import AIGradingRouter
from tests.fixtures.mock_responses import MOCK_CLAUDE_GRADING_RESPONSE, MOCK_GEMINI_GRADING_RESPONSE


class TestAIGradingRouter:
    @pytest.mark.asyncio
    async def test_claude_returns_valid_grade(self):
        router = AIGradingRouter()
        router.claude = AsyncMock()
        router.claude.grade_photos.return_value = {
            "grade": "A",
            "confidence": 85,
            "details": MOCK_CLAUDE_GRADING_RESPONSE,
            "ai_provider": "claude",
            "model_used": "claude-sonnet-4-20250514",
            "input_tokens": 1500,
            "output_tokens": 200,
            "duration_ms": 3200,
            "raw_response": "{}",
        }

        result = await router.grade(["url1", "url2", "url3"], "tomato")
        assert result["grade"] == "A"
        assert result["confidence"] == 85
        assert result["ai_provider"] == "claude"
        assert result["low_confidence_warning"] is False

    @pytest.mark.asyncio
    async def test_gemini_fallback_when_claude_fails(self):
        router = AIGradingRouter()
        router.claude = AsyncMock()
        router.claude.grade_photos.side_effect = AIGradingError(message_en="Claude failed")
        router.gemini = AsyncMock()
        router.gemini.grade_photos.return_value = {
            "grade": "B",
            "confidence": 72,
            "details": MOCK_GEMINI_GRADING_RESPONSE,
            "ai_provider": "gemini",
            "model_used": "gemini-1.5-flash",
            "input_tokens": 0,
            "output_tokens": 0,
            "duration_ms": 2500,
            "raw_response": "{}",
        }

        result = await router.grade(["url1", "url2", "url3"], "tomato")
        assert result["grade"] == "B"
        assert result["ai_provider"] == "gemini"

    @pytest.mark.asyncio
    async def test_manual_fallback_when_both_fail(self):
        router = AIGradingRouter()
        router.claude = AsyncMock()
        router.claude.grade_photos.side_effect = AIGradingError(message_en="Claude failed")
        router.gemini = AsyncMock()
        router.gemini.grade_photos.side_effect = AIGradingError(message_en="Gemini failed")

        result = await router.grade(["url1", "url2", "url3"], "tomato")
        assert result["grade"] is None
        assert result["ai_provider"] == "manual"
        assert result["requires_manual_grading"] is True

    @pytest.mark.asyncio
    async def test_low_confidence_warning(self):
        router = AIGradingRouter()
        router.claude = AsyncMock()
        router.claude.grade_photos.return_value = {
            "grade": "B",
            "confidence": 40,
            "details": {},
            "ai_provider": "claude",
            "model_used": "test",
            "input_tokens": 0,
            "output_tokens": 0,
            "duration_ms": 0,
            "raw_response": "{}",
        }

        result = await router.grade(["url1", "url2", "url3"], "tomato")
        assert result["low_confidence_warning"] is True
        assert result["confidence"] == 40

    @pytest.mark.asyncio
    async def test_high_confidence_no_warning(self):
        router = AIGradingRouter()
        router.claude = AsyncMock()
        router.claude.grade_photos.return_value = {
            "grade": "A",
            "confidence": AIConfig.CONFIDENCE_THRESHOLD,
            "details": {},
            "ai_provider": "claude",
            "model_used": "test",
            "input_tokens": 0,
            "output_tokens": 0,
            "duration_ms": 0,
            "raw_response": "{}",
        }

        result = await router.grade(["url1", "url2", "url3"], "tomato")
        assert result["low_confidence_warning"] is False


class TestPhotoService:
    @pytest.mark.asyncio
    async def test_grading_result_logged(self):
        from app.services.photo_service import PhotoService

        with patch.object(PhotoService, "__init__", lambda self, s: None):
            svc = PhotoService(AsyncMock())
            svc.draft_repo = AsyncMock()
            svc.photo_repo = AsyncMock()
            svc.ai_log_repo = AsyncMock()
            svc.ai_router = AsyncMock()

            draft = MagicMock()
            draft.seller_id = uuid4()
            draft.step1_data = {"crop": "tomato"}
            draft.step2_data = {}
            svc.draft_repo.get_draft_by_id.return_value = draft

            photos = [MagicMock(storage_url=f"url{i}") for i in range(3)]
            svc.photo_repo.get_photos_by_draft.return_value = photos

            svc.ai_router.grade.return_value = {
                "grade": "A",
                "confidence": 85,
                "ai_provider": "claude",
                "model_used": "test",
                "details": {},
                "duration_ms": 1000,
                "input_tokens": 500,
                "output_tokens": 100,
                "raw_response": "{}",
            }

            seller_id = draft.seller_id
            await svc.trigger_grading(uuid4(), seller_id)

            svc.ai_log_repo.create_log.assert_called_once()
            log_data = svc.ai_log_repo.create_log.call_args[0][0]
            assert log_data["ai_provider"] == "claude"
            assert log_data["success"] is True

    @pytest.mark.asyncio
    async def test_duplicate_photo_rejected(self):
        from app.services.photo_service import PhotoService

        with patch.object(PhotoService, "__init__", lambda self, s: None):
            svc = PhotoService(AsyncMock())
            svc.draft_repo = AsyncMock()
            svc.photo_repo = AsyncMock()
            svc.storage = AsyncMock()

            draft = MagicMock()
            draft.seller_id = uuid4()
            draft.step2_data = {}
            svc.draft_repo.get_draft_by_id.return_value = draft

            svc.photo_repo.check_duplicate_hash.return_value = True

            mock_file = AsyncMock()
            mock_file.read.return_value = b"\x00" * 100
            mock_file.content_type = "image/jpeg"
            mock_file.filename = "test.jpg"

            with patch.object(svc, "_compress_photo", return_value=b"\x00" * 100):
                with patch.object(svc, "_calculate_perceptual_hash", return_value="abc123"):
                    with pytest.raises(DuplicatePhotoError):
                        await svc.upload_photos(uuid4(), draft.seller_id, [mock_file, mock_file, mock_file])
