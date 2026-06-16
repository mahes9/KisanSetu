"""Async repository for ListingPhoto CRUD operations."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing_photo import ListingPhoto


class PhotoRepository:
    """Data-access layer for listing photos."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_photo(self, photo_data: dict) -> ListingPhoto:
        """Insert a new photo record and return it."""
        photo = ListingPhoto(**photo_data)
        self._session.add(photo)
        await self._session.flush()
        await self._session.refresh(photo)
        return photo

    async def get_photos_by_draft(self, draft_id: uuid.UUID) -> list[ListingPhoto]:
        """Return all photos for a given draft, ordered by sort_order."""
        stmt = (
            select(ListingPhoto)
            .where(ListingPhoto.listing_draft_id == draft_id)
            .order_by(ListingPhoto.sort_order)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_photos_by_listing(self, listing_id: uuid.UUID) -> list[ListingPhoto]:
        """Return all photos for a published listing, ordered by sort_order."""
        stmt = (
            select(ListingPhoto)
            .where(ListingPhoto.listing_id == listing_id)
            .order_by(ListingPhoto.sort_order)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_photos_by_draft(self, draft_id: uuid.UUID) -> None:
        """Delete all photos belonging to a draft (cascade cleanup)."""
        stmt = delete(ListingPhoto).where(ListingPhoto.listing_draft_id == draft_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def check_duplicate_hash(
        self, perceptual_hash: str, draft_id: uuid.UUID
    ) -> bool:
        """Return True if a photo with the same perceptual hash already
        exists for this draft.
        """
        stmt = select(func.count()).where(
            ListingPhoto.listing_draft_id == draft_id,
            ListingPhoto.perceptual_hash == perceptual_hash,
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def update_listing_id(
        self, draft_id: uuid.UUID, listing_id: uuid.UUID
    ) -> None:
        """Link all draft photos to the published listing."""
        stmt = (
            update(ListingPhoto)
            .where(ListingPhoto.listing_draft_id == draft_id)
            .values(listing_id=listing_id)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def count_photos_by_draft(self, draft_id: uuid.UUID) -> int:
        """Return the number of photos uploaded for a draft."""
        stmt = select(func.count()).where(
            ListingPhoto.listing_draft_id == draft_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
