"""Buyer model — supports both individual and organization buyer types."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Buyer(TimestampMixin, Base):
    __tablename__ = "buyers"

    # ── Identity ───────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_number: Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False, index=True
    )
    buyer_type: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(5), default="te", nullable=False)

    # ── Common contact ─────────────────────────────────────
    primary_phone: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False, index=True
    )
    primary_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Individual-only fields ─────────────────────────────
    individual_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    aadhaar_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    aadhaar_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    aadhaar_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    upi_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    upi_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Organization-only fields ───────────────────────────
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    business_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    buyer_segment: Mapped[str | None] = mapped_column(String(30), nullable=True)
    gstin: Mapped[str | None] = mapped_column(String(15), unique=True, nullable=True)
    gstin_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    pan_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    pan_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    cin_number: Mapped[str | None] = mapped_column(String(21), nullable=True)
    org_tier: Mapped[str] = mapped_column(String(10), default="tier_3")

    # ── Bank (both types) ──────────────────────────────────
    bank_account: Mapped[str | None] = mapped_column(String(20), nullable=True)
    bank_ifsc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    bank_holder_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── KYC state ──────────────────────────────────────────
    kyc_status: Mapped[str] = mapped_column(
        String(30), default="pending", index=True
    )

    # ── Trust & history ────────────────────────────────────
    trust_score: Mapped[int] = mapped_column(Integer, default=0)
    orders_completed: Mapped[int] = mapped_column(Integer, default=0)
    dispute_loss_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), default=0
    )
    avg_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    total_gmv: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    suspension_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Preferences ────────────────────────────────────────
    preferred_crops: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    default_quality_grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    min_order_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Device / app ───────────────────────────────────────
    device_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_platform: Mapped[str | None] = mapped_column(String(10), nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Org password (org buyers login with email + password) ──
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # ── Relationships ──────────────────────────────────────
    users = relationship("BuyerUser", back_populates="buyer", lazy="selectin")
    locations = relationship("BuyerLocation", back_populates="buyer", lazy="selectin")
    requirements = relationship("BuyerRequirement", back_populates="buyer", lazy="selectin")
    preferences = relationship("BuyerPreference", back_populates="buyer", lazy="selectin")
