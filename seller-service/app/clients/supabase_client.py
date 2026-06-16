"""Supabase Storage client for photo uploads."""

from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageClient:
    async def upload_file(
        self,
        bucket: str,
        path: str,
        file_bytes: bytes,
        content_type: str = "image/jpeg",
    ) -> str:
        if not settings.SUPABASE_URL:
            mock_url = f"https://mock-storage.supabase.co/{bucket}/{path}"
            logger.info("MOCK upload: %s", mock_url)
            return mock_url

        from supabase import create_client

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        client.storage.from_(bucket).upload(
            path, file_bytes, {"content-type": content_type}
        )
        return self.get_public_url(bucket, path)

    async def delete_file(self, bucket: str, path: str) -> bool:
        if not settings.SUPABASE_URL:
            logger.info("MOCK delete: %s/%s", bucket, path)
            return True

        from supabase import create_client

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        client.storage.from_(bucket).remove([path])
        return True

    def get_public_url(self, bucket: str, path: str) -> str:
        if not settings.SUPABASE_URL:
            return f"https://mock-storage.supabase.co/{bucket}/{path}"
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
