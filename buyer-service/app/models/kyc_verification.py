"""KycVerification model — KYC audit trail."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class KycVerification(TimestampMixin, Base):
    __tablename__ = "kyc_verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    verification_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    provider: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
