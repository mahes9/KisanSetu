"""BuyerPreference model — saved searches, alerts, preferred sellers."""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class BuyerPreference(TimestampMixin, Base):
    __tablename__ = "buyer_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    preference_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    filter_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    target_seller_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    buyer = relationship("Buyer", back_populates="preferences")
