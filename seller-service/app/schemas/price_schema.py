"""Price snapshot schema."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class PriceSnapshotSchema(BaseModel):
    crop: str
    district: str
    modal_price: float
    floor_price: float
    min_price: float | None = None
    max_price: float | None = None
    fetched_at: datetime | None = None
