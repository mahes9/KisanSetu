"""Order model — created when an enquiry is accepted."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Order(TimestampMixin, Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    listing_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("listings.id"), nullable=False, index=True)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("enquiries.id"), nullable=False, unique=True)
    seller_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False, index=True)
    buyer_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    buyer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    crop: Mapped[str] = mapped_column(String(50), nullable=False)
    variety: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_q: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

    commission_rate: Mapped[float] = mapped_column(Float, nullable=False)
    commission_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tds_rate: Mapped[float] = mapped_column(Float, default=0.01)
    tds_amount: Mapped[float] = mapped_column(Float, default=0)
    net_seller_payout: Mapped[float] = mapped_column(Float, nullable=False)

    payment_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_district: Mapped[str | None] = mapped_column(String(50), nullable=True)
    delivery_pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Layer 2: Escrow
    escrow_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    escrow_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escrow_released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    escrow_refunded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Layer 3: OTP delivery verification
    delivery_otp: Mapped[str | None] = mapped_column(String(6), nullable=True)
    delivery_otp_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Layer 5: Invoice
    invoice_number: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    invoice_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Layer 6: Dispute resolution
    dispute_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    dispute_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispute_raised_by: Mapped[str | None] = mapped_column(String(10), nullable=True)
    dispute_raised_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dispute_resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dispute_resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispute_evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="awaiting_payment", nullable=False, index=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payment_released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    seller_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buyer_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    listing = relationship("Listing")
    enquiry = relationship("Enquiry")
    seller = relationship("Seller")
