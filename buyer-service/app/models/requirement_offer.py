"""RequirementOffer model — offer / counter-offer chain."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class RequirementOffer(TimestampMixin, Base):
    __tablename__ = "requirement_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyer_requirements.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    seller_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    seller_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # ── Offer details ──────────────────────────────────────
    offer_price_per_q: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quality_grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Negotiation ────────────────────────────────────────
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    parent_offer_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("requirement_offers.id"), nullable=True
    )
    counter_price_per_q: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    counter_quantity_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # ── Status & timing ────────────────────────────────────
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── AI suggestion ──────────────────────────────────────
    ai_suggestion: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Relationships ──────────────────────────────────────
    requirement = relationship("BuyerRequirement", back_populates="offers")
