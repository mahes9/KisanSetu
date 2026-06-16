"""SQLAlchemy 2.0 model for listing photos (lot view, closeup, cut section)."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ListingPhoto(TimestampMixin, Base):
    """Stores metadata for each photo uploaded during the listing wizard.

    Exactly three photos (lot_view, closeup, cut_section) are required per
    listing.  Photos are initially linked to a draft; once the draft is
    published the ``listing_id`` column is populated so photos survive
    independently of the draft lifecycle.
    """

    __tablename__ = "listing_photos"

    # ── Primary key ──────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Parent references ────────────────────────────────────────────
    listing_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("listing_drafts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("listings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Photo metadata ───────────────────────────────────────────────
    photo_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="lot_view | closeup | cut_section",
    )
    storage_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    storage_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_size_bytes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    content_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # ── Image dimensions ─────────────────────────────────────────────
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Duplicate detection ──────────────────────────────────────────
    perceptual_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    # ── Ordering ─────────────────────────────────────────────────────
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────
    draft = relationship("ListingDraft", lazy="selectin")
    listing = relationship("Listing", back_populates="photos", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<ListingPhoto id={self.id} type={self.photo_type} "
            f"draft={self.listing_draft_id}>"
        )
