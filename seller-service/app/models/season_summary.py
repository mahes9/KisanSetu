"""Materialised earnings per seller per season — Module 6."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class SeasonSummary(TimestampMixin, Base):
    __tablename__ = "season_summaries"
    __table_args__ = (
        UniqueConstraint("seller_id", "season", "year", name="uq_seller_season_year"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seller_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("sellers.id", ondelete="CASCADE"), nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(20), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_listings: Mapped[int] = mapped_column(Integer, default=0)
    successful_sales: Mapped[int] = mapped_column(Integer, default=0)
    total_quantity_kg: Mapped[float] = mapped_column(Float, default=0)
    total_earnings: Mapped[float] = mapped_column(Float, default=0)
    total_commission: Mapped[float] = mapped_column(Float, default=0)
    avg_price_per_q: Mapped[float | None] = mapped_column(Float, nullable=True)
    best_crop: Mapped[str | None] = mapped_column(String(50), nullable=True)
    best_price_per_q: Mapped[float | None] = mapped_column(Float, nullable=True)
    mandi_comparison_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    cancellation_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_time_to_match_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_grade: Mapped[str | None] = mapped_column(String(1), nullable=True)
