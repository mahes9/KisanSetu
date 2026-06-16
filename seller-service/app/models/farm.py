"""Farm model — Module 2 (stub with full schema)."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Farm(TimestampMixin, Base):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sellers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gps_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)
    acreage: Mapped[float | None] = mapped_column(Float, nullable=True)
    irrigation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    crops_grown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    seller = relationship("Seller", back_populates="farms")
