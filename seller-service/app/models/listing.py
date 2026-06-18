"""Published listing model — Module 5."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Listing(TimestampMixin, Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True)
    listing_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    source_draft_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("listing_drafts.id"), nullable=True)

    crop: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    variety: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    harvest_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    days_since_harvest: Mapped[int | None] = mapped_column(Integer, nullable=True)

    grade: Mapped[str] = mapped_column(String(1), nullable=False)
    ai_grade_locked: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(20), nullable=True)

    ask_price_per_q: Mapped[float] = mapped_column(Float, nullable=False)
    floor_price_at_publish: Mapped[float] = mapped_column(Float, nullable=False)
    modal_price_at_publish: Mapped[float] = mapped_column(Float, nullable=False)

    transport_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pickup_window: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pickup_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pickup_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)
    price_edit_count: Mapped[int] = mapped_column(Integer, default=0)
    price_edit_history: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    consent_quality: Mapped[bool] = mapped_column(Boolean, default=True)
    consent_price: Mapped[bool] = mapped_column(Boolean, default=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    views_count: Mapped[int] = mapped_column(Integer, default=0)
    enquiries_count: Mapped[int] = mapped_column(Integer, default=0)

    seller = relationship("Seller", back_populates="listings")
    photos = relationship("ListingPhoto", back_populates="listing", lazy="selectin")
