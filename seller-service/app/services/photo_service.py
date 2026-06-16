"""Photo upload, compression, hashing, and AI grading trigger."""

from __future__ import annotations

import hashlib
import io
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.supabase_client import SupabaseStorageClient
from app.config import settings
from app.core.constants import PhotoConfig
from app.core.exceptions import DraftNotFoundError, DraftNotOwnedError, DuplicatePhotoError, PhotoUploadError
from app.repositories.ai_log_repo import AILogRepository
from app.repositories.draft_repo import DraftRepository
from app.repositories.photo_repo import PhotoRepository
from app.services.ai_service.ai_router import AIGradingRouter

logger = logging.getLogger(__name__)

PHOTO_TYPES = ["lot_view", "closeup", "cut_section"]


class PhotoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.photo_repo = PhotoRepository(session)
        self.draft_repo = DraftRepository(session)
        self.ai_log_repo = AILogRepository(session)
        self.storage = SupabaseStorageClient()
        self.ai_router = AIGradingRouter()

    async def upload_photos(
        self,
        draft_id: UUID,
        seller_id: UUID,
        files: list,
    ) -> list[dict]:
        draft = await self.draft_repo.get_draft_by_id(draft_id)
        if not draft:
            raise DraftNotFoundError()
        if draft.seller_id != seller_id:
            raise DraftNotOwnedError()

        if len(files) != PhotoConfig.MAX_PHOTOS:
            raise PhotoUploadError(
                message_en=f"Exactly {PhotoConfig.MAX_PHOTOS} photos required. Got {len(files)}."
            )

        results: list[dict] = []
        photo_urls: list[str] = []

        for idx, file in enumerate(files):
            content = await file.read()
            content_type = file.content_type or "image/jpeg"

            if content_type not in ("image/jpeg", "image/png"):
                raise PhotoUploadError(message_en="Only JPEG and PNG photos are allowed.")

            compressed = self._compress_photo(content)
            p_hash = self._calculate_perceptual_hash(compressed)

            is_dup = await self.photo_repo.check_duplicate_hash(p_hash, draft_id)
            if is_dup:
                raise DuplicatePhotoError()

            photo_type = PHOTO_TYPES[idx] if idx < len(PHOTO_TYPES) else f"photo_{idx}"
            path = f"sellers/{seller_id}/drafts/{draft_id}/{photo_type}.jpg"

            url = await self.storage.upload_file(
                settings.STORAGE_BUCKET, path, compressed, content_type
            )

            photo = await self.photo_repo.create_photo({
                "listing_draft_id": draft_id,
                "photo_type": photo_type,
                "storage_url": url,
                "storage_path": path,
                "file_size_bytes": len(compressed),
                "original_filename": file.filename or f"{photo_type}.jpg",
                "content_type": content_type,
                "perceptual_hash": p_hash,
                "sort_order": idx,
            })

            photo_urls.append(url)
            results.append({
                "id": str(photo.id),
                "photo_type": photo_type,
                "storage_url": url,
                "file_size_bytes": len(compressed),
            })

        step2_data = (draft.step2_data or {})
        step2_data["photo_urls"] = photo_urls
        await self.draft_repo.update_draft(draft_id, {"step2_data": step2_data})

        return results

    async def trigger_grading(self, draft_id: UUID, seller_id: UUID) -> dict:
        draft = await self.draft_repo.get_draft_by_id(draft_id)
        if not draft:
            raise DraftNotFoundError()
        if draft.seller_id != seller_id:
            raise DraftNotOwnedError()

        photos = await self.photo_repo.get_photos_by_draft(draft_id)
        if len(photos) < PhotoConfig.MIN_PHOTOS:
            from app.core.exceptions import PhotosRequiredError
            raise PhotosRequiredError()

        photo_urls = [p.storage_url for p in photos]
        crop = (draft.step1_data or {}).get("crop", "tomato")

        step2_data = dict(draft.step2_data or {})
        step2_data["grading_status"] = "processing"
        await self.draft_repo.update_draft(draft_id, {"step2_data": step2_data})

        result = await self.ai_router.grade(photo_urls, crop)

        await self.ai_log_repo.create_log({
            "listing_draft_id": draft_id,
            "ai_provider": result.get("ai_provider", "unknown"),
            "model_used": result.get("model_used", ""),
            "crop": crop,
            "photo_urls": photo_urls,
            "prompt_used": "",
            "raw_response": result.get("raw_response", ""),
            "parsed_grade": result.get("grade"),
            "confidence_score": result.get("confidence", 0),
            "grading_details": result.get("details"),
            "success": result.get("grade") is not None,
            "error_message": None,
            "duration_ms": result.get("duration_ms", 0),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
        })

        step2_data.update({
            "grade": result.get("grade"),
            "ai_confidence": result.get("confidence", 0),
            "grading_status": "completed" if result.get("grade") else "failed",
        })
        await self.draft_repo.update_draft(draft_id, {"step2_data": step2_data})

        return {
            "draft_id": str(draft_id),
            "grading_status": step2_data["grading_status"],
            "result": {
                "grade": result.get("grade"),
                "confidence": result.get("confidence", 0),
                "ai_provider": result.get("ai_provider"),
                "low_confidence_warning": result.get("low_confidence_warning", False),
                "details": result.get("details"),
            },
        }

    async def get_grading_status(self, draft_id: UUID, seller_id: UUID) -> dict:
        draft = await self.draft_repo.get_draft_by_id(draft_id)
        if not draft:
            raise DraftNotFoundError()
        if draft.seller_id != seller_id:
            raise DraftNotOwnedError()

        step2 = draft.step2_data or {}
        latest_log = await self.ai_log_repo.get_latest_successful(draft_id)
        result = None
        if latest_log:
            result = {
                "grade": latest_log.parsed_grade,
                "confidence": latest_log.confidence_score,
                "ai_provider": latest_log.ai_provider,
                "details": latest_log.grading_details,
            }

        return {
            "draft_id": str(draft_id),
            "grading_status": step2.get("grading_status", "pending"),
            "result": result,
        }

    def _compress_photo(self, file_bytes: bytes, max_size_mb: float = 2.0) -> bytes:
        try:
            from PIL import Image
        except ImportError:
            return file_bytes

        max_bytes = int(max_size_mb * 1024 * 1024)
        if len(file_bytes) <= max_bytes:
            return file_bytes

        img = Image.open(io.BytesIO(file_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        quality = 85
        while quality >= 20:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= max_bytes:
                return buf.getvalue()
            quality -= 10

        img.thumbnail((1280, 1280))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=70)
        return buf.getvalue()

    def _calculate_perceptual_hash(self, file_bytes: bytes) -> str:
        try:
            from PIL import Image
        except ImportError:
            return hashlib.md5(file_bytes).hexdigest()

        img = Image.open(io.BytesIO(file_bytes))
        img = img.resize((8, 8)).convert("L")
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        bits = "".join("1" if p >= avg else "0" for p in pixels)
        return hex(int(bits, 2))[2:].zfill(16)
