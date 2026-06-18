"""UserActivityLog model — org user activity audit trail."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserActivityLog(TimestampMixin, Base):
    __tablename__ = "user_activity_log"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("buyer_users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
