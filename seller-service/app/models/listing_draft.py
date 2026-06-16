"""SQLAlchemy 2.0 models for the Listing Draft module."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ListingDraft(TimestampMixin, Base):
    """Represents a multi-step crop listing draft with auto-save support.

    Each draft tracks the seller's progress through a 5-step wizard,
    storing per-step JSON data, completion flags, and an overall
    completeness score.  Drafts can be resumed across devices and
    cloned for similar future listings.
    """

    __tablename__ = "listing_drafts"

    # ── Primary key ──────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Ownership ────────────────────────────────────────────────────
    seller_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sellers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Draft lifecycle ──────────────────────────────────────────────
    draft_status: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        nullable=False,
        index=True,
    )
    current_step: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    completeness_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ── Step data (JSONB for Postgres) ───────────────────────────────
    step1_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    step2_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    step3_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    step4_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    step5_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Step completion flags ────────────────────────────────────────
    step1_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    step2_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    step3_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    step4_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    step5_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ── Activity tracking ────────────────────────────────────────────
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Published reference ──────────────────────────────────────────
    published_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────────
    seller = relationship("Seller", back_populates="drafts", lazy="selectin")
    save_logs = relationship(
        "DraftSaveLog",
        back_populates="draft",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<ListingDraft id={self.id} seller={self.seller_id} "
            f"status={self.draft_status} step={self.current_step} "
            f"completeness={self.completeness_score}>"
        )


class DraftSaveLog(TimestampMixin, Base):
    """Audit log of every save event for a listing draft.

    Captures device, session, network metadata alongside the data
    snapshot so that cross-device resume behaviour can be debugged
    and save reliability measured.
    """

    __tablename__ = "draft_save_log"

    # ── Primary key ──────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Foreign key ──────────────────────────────────────────────────
    draft_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("listing_drafts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Save metadata ────────────────────────────────────────────────
    save_trigger: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    data_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Client metadata ──────────────────────────────────────────────
    device: Mapped[str | None] = mapped_column(String(50), nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    network_type: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ── Relationships ────────────────────────────────────────────────
    draft = relationship("ListingDraft", back_populates="save_logs")

    def __repr__(self) -> str:
        return (
            f"<DraftSaveLog id={self.id} draft={self.draft_id} "
            f"trigger={self.save_trigger} step={self.step_number}>"
        )
