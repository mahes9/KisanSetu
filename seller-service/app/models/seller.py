"""Seller model — Module 1 & 2 (stub with full schema)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Seller(TimestampMixin, Base):
    __tablename__ = "sellers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    aadhaar_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    aadhaar_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    aadhaar_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    kyc_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)

    upi_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upi_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    bank_account: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_ifsc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    bank_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    language: Mapped[str] = mapped_column(String(5), default="te")

    trust_score: Mapped[int] = mapped_column(Integer, default=0)
    orders_completed: Mapped[int] = mapped_column(Integer, default=0)
    cancellation_count: Mapped[int] = mapped_column(Integer, default=0)
    suspension_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    farms = relationship("Farm", back_populates="seller", lazy="selectin")
    listings = relationship("Listing", back_populates="seller", lazy="selectin")
    drafts = relationship("ListingDraft", back_populates="seller", lazy="selectin")
