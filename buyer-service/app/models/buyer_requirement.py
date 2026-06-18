"""BuyerRequirement model — RFQ / buyer requirements."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BuyerRequirement(TimestampMixin, Base):
    __tablename__ = "buyer_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    requirement_number: Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False, index=True
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyer_users.id"), nullable=True
    )

    # ── Crop & quantity ────────────────────────────────────
    crop: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    variety: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_min_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_max_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quality_grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    quality_specs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Pricing ────────────────────────────────────────────
    price_type: Mapped[str] = mapped_column(String(30), default="negotiable")
    offer_price_per_q: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    ai_suggested_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    modal_price_at_create: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # ── Delivery ───────────────────────────────────────────
    delivery_location_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyer_locations.id"), nullable=True
    )
    delivery_district: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delivery_by_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Options ────────────────────────────────────────────
    gst_invoice_required: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_partial_match: Mapped[bool] = mapped_column(Boolean, default=True)
    urgency: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status & lifecycle ─────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(30), default="active", index=True
    )
    escrow_deposited: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    fulfilled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Matching stats ─────────────────────────────────────
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    offers_received: Mapped[int] = mapped_column(Integer, default=0)
    matched_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # ── Relationships ──────────────────────────────────────
    buyer = relationship("Buyer", back_populates="requirements")
    offers = relationship("RequirementOffer", back_populates="requirement", lazy="selectin")
