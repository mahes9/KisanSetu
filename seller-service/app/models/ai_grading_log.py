"""SQLAlchemy 2.0 model for AI grading audit logs."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AIGradingLog(TimestampMixin, Base):
    """Immutable audit record of every AI grading attempt.

    Captures the full request/response cycle — prompt, raw output, parsed
    result, token counts, latency, and estimated cost — so the grading
    pipeline can be debugged, audited, and cost-tracked.
    """

    __tablename__ = "ai_grading_log"

    # ── Primary key ──────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Draft reference ──────────────────────────────────────────────
    listing_draft_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("listing_drafts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── AI provider info ─────────────────────────────────────────────
    ai_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="claude | gemini | manual",
    )
    model_used: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    crop: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ── Request data ─────────────────────────────────────────────────
    photo_urls: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="List of photo URLs sent to the AI model",
    )
    prompt_used: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Response data ────────────────────────────────────────────────
    raw_response: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    parsed_grade: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
        comment="A, B, or C",
    )
    confidence_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="0-100 confidence from AI",
    )
    grading_details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Full parsed grading result",
    )

    # ── Outcome ──────────────────────────────────────────────────────
    success: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Performance / cost tracking ──────────────────────────────────
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    input_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    output_tokens: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    estimated_cost_usd: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────────
    draft = relationship("ListingDraft", backref="grading_logs", lazy="selectin")

    def __repr__(self) -> str:
        return (
            f"<AIGradingLog id={self.id} provider={self.ai_provider} "
            f"grade={self.parsed_grade} confidence={self.confidence_score} "
            f"success={self.success}>"
        )
