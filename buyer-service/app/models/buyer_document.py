"""BuyerDocument model — Phase 1 stub only.

Full schema will be added in Phase 2 migration 002_buyer_documents_full.sql.
"""

from __future__ import annotations

import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BuyerDocument(Base):
    __tablename__ = "buyer_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
