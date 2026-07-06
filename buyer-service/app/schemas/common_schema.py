"""Shared Pydantic response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class StandardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    success: bool = True
    message: str = ""
    data: Any = None


class PaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Any] = []
    total: int = 0
    page: int = 1
    per_page: int = 20


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message_en: str
    message_te: str
