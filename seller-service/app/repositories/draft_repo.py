"""Async repository for ListingDraft and DraftSaveLog persistence."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.listing_draft import DraftSaveLog, ListingDraft

logger = logging.getLogger(__name__)


class DraftRepository:
    """Data-access layer for listing drafts.

    Every public method is a thin async wrapper around SQLAlchemy 2.0
    select / update / delete statements executed on the injected
    ``AsyncSession``.  The caller is responsible for committing or
    rolling back the session.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Create ───────────────────────────────────────────────────────

    async def create_draft(
        self,
        seller_id: uuid.UUID,
        initial_data: dict,
    ) -> ListingDraft:
        """Insert a new draft row with the supplied *initial_data* as step 1."""

        draft = ListingDraft(
            id=uuid.uuid4(),
            seller_id=seller_id,
            draft_status="in_progress",
            current_step=1,
            completeness_score=initial_data.get("completeness_score", 0),
            step1_data=initial_data.get("step1_data"),
            step1_completed=initial_data.get("step1_completed", False),
            last_active_at=datetime.now(timezone.utc),
        )
        self._session.add(draft)
        await self._session.flush()
        await self._session.refresh(draft)
        return draft

    # ── Read ─────────────────────────────────────────────────────────

    async def get_draft_by_id(
        self,
        draft_id: uuid.UUID,
    ) -> ListingDraft | None:
        """Return a draft by primary key or ``None``."""

        stmt = select(ListingDraft).where(ListingDraft.id == draft_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_draft_for_update(
        self,
        draft_id: uuid.UUID,
    ) -> ListingDraft | None:
        """Return a draft with a ``FOR UPDATE`` row lock for safe mutation."""

        stmt = (
            select(ListingDraft)
            .where(ListingDraft.id == draft_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Update ───────────────────────────────────────────────────────

    async def update_draft(
        self,
        draft_id: uuid.UUID,
        updates: dict,
    ) -> ListingDraft:
        """Apply arbitrary column updates to a draft and return the refreshed row."""

        stmt = (
            update(ListingDraft)
            .where(ListingDraft.id == draft_id)
            .values(**updates)
        )
        await self._session.execute(stmt)
        await self._session.flush()

        draft = await self.get_draft_by_id(draft_id)
        if draft is not None:
            await self._session.refresh(draft)
        return draft  # type: ignore[return-value]

    async def update_step_data(
        self,
        draft_id: uuid.UUID,
        step_num: int,
        step_data: dict,
        completeness: int,
    ) -> ListingDraft:
        """Persist data for a specific wizard step and update the score."""

        step_data_col = f"step{step_num}_data"
        step_completed_col = f"step{step_num}_completed"

        values: dict = {
            step_data_col: step_data,
            step_completed_col: True,
            "completeness_score": completeness,
            "last_active_at": datetime.now(timezone.utc),
        }

        # Advance `current_step` to the next incomplete step
        if step_num >= 1:
            values["current_step"] = min(step_num + 1, 5)

        return await self.update_draft(draft_id, values)

    # ── Soft delete ──────────────────────────────────────────────────

    async def delete_draft(self, draft_id: uuid.UUID) -> None:
        """Soft-delete by setting status to *abandoned*."""

        stmt = (
            update(ListingDraft)
            .where(ListingDraft.id == draft_id)
            .values(draft_status="abandoned")
        )
        await self._session.execute(stmt)
        await self._session.flush()

    # ── List / count ─────────────────────────────────────────────────

    async def list_drafts_by_seller(
        self,
        seller_id: uuid.UUID,
        status_filter: Optional[str] = None,
    ) -> list[ListingDraft]:
        """Return all drafts for a seller, optionally filtered by status."""

        stmt = (
            select(ListingDraft)
            .where(ListingDraft.seller_id == seller_id)
            .where(ListingDraft.draft_status.notin_(["abandoned", "published"]))
            .order_by(ListingDraft.last_active_at.desc())
        )
        if status_filter is not None:
            stmt = stmt.where(ListingDraft.draft_status == status_filter)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_drafts_by_seller(self, seller_id: uuid.UUID) -> int:
        """Count non-abandoned drafts for a seller (for max-drafts check)."""

        stmt = (
            select(func.count())
            .select_from(ListingDraft)
            .where(ListingDraft.seller_id == seller_id)
            .where(ListingDraft.draft_status.notin_(["abandoned", "published"]))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    # ── Save log ─────────────────────────────────────────────────────

    async def save_log_entry(
        self,
        draft_id: uuid.UUID,
        save_trigger: str,
        step_number: int,
        data: dict,
        device: Optional[str] = None,
        session_id: Optional[str] = None,
        network_type: Optional[str] = None,
    ) -> None:
        """Append an audit entry to the draft save log."""

        log = DraftSaveLog(
            id=uuid.uuid4(),
            draft_id=draft_id,
            save_trigger=save_trigger,
            step_number=step_number,
            data_snapshot=data,
            device=device,
            session_id=session_id,
            network_type=network_type,
        )
        self._session.add(log)
        await self._session.flush()

    # ── Publish ──────────────────────────────────────────────────────

    async def mark_published(
        self,
        draft_id: uuid.UUID,
        listing_id: uuid.UUID,
    ) -> None:
        """Mark a draft as published and record the listing FK."""

        stmt = (
            update(ListingDraft)
            .where(ListingDraft.id == draft_id)
            .values(
                draft_status="published",
                published_listing_id=listing_id,
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()

    # ── Cleanup helpers ──────────────────────────────────────────────

    async def get_stale_drafts(self, inactive_days: int) -> list[ListingDraft]:
        """Return in-progress drafts whose ``last_active_at`` exceeds *inactive_days*."""

        cutoff = datetime.now(timezone.utc) - timedelta(days=inactive_days)
        stmt = (
            select(ListingDraft)
            .where(ListingDraft.draft_status == "in_progress")
            .where(ListingDraft.last_active_at < cutoff)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_update_status(
        self,
        draft_ids: list[uuid.UUID],
        status: str,
    ) -> None:
        """Batch-update the status column for a list of draft ids."""

        if not draft_ids:
            return
        stmt = (
            update(ListingDraft)
            .where(ListingDraft.id.in_(draft_ids))
            .values(draft_status=status)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def hard_delete_drafts(self, draft_ids: list[uuid.UUID]) -> None:
        """Permanently remove drafts (used by the cleanup job for very old data)."""

        if not draft_ids:
            return
        # Delete save logs first (cascade should handle this, but be explicit)
        log_stmt = delete(DraftSaveLog).where(DraftSaveLog.draft_id.in_(draft_ids))
        await self._session.execute(log_stmt)

        draft_stmt = delete(ListingDraft).where(ListingDraft.id.in_(draft_ids))
        await self._session.execute(draft_stmt)
        await self._session.flush()
