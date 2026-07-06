"""Buyer enquiry model — stores interest from buyers on listings."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Enquiry(TimestampMixin, Base):
    __tablename__ = "enquiries"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    buyer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    buyer_phone: Mapped[str | None] = mapped_column(String(15), nullable=True)
    buyer_district: Mapped[str | None] = mapped_column(String(50), nullable=True)

    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    offered_price_per_q: Mapped[float | None] = mapped_column(Float, nullable=True)
    delivery_district: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delivery_pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)
    required_by_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False, index=True)
    seller_quoted_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    seller_available_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    seller_delivery_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seller_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    seller_responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    counter_count: Mapped[int] = mapped_column(Integer, default=0)
    viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    listing = relationship("Listing", backref="enquiries")
