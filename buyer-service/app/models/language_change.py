"""LanguageChange model — language preference change history."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LanguageChange(TimestampMixin, Base):
    __tablename__ = "language_changes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    from_language: Mapped[str] = mapped_column(String(5), nullable=False)
    to_language: Mapped[str] = mapped_column(String(5), nullable=False)
    changed_by: Mapped[str] = mapped_column(String(20), default="user")
