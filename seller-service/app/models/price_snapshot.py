"""Local cache of price service data."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class PriceSnapshot(TimestampMixin, Base):
    __tablename__ = "price_snapshots_cache"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    modal_price: Mapped[float] = mapped_column(Float, nullable=False)
    floor_price: Mapped[float] = mapped_column(Float, nullable=False)
    min_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="price_service")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
