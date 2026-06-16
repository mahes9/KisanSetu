"""Pydantic v2 schemas for the Photo Upload & AI Grading module."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# Photo upload schemas
# =====================================================================


class PhotoUploadResponse(BaseModel):
    """Metadata returned for a single successfully uploaded photo."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    photo_type: str = Field(..., description="lot_view | closeup | cut_section")
    storage_url: str = Field(..., description="Public CDN URL for the photo")
    file_size_bytes: int = Field(..., description="File size after compression (bytes)")


class PhotoListResponse(BaseModel):
    """Wrapper for a list of photos belonging to a draft."""

    model_config = ConfigDict(from_attributes=True)

    photos: list[PhotoUploadResponse]


# =====================================================================
# Grading request / result schemas
# =====================================================================


class GradingRequest(BaseModel):
    """Explicit request to trigger AI grading for a draft."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: uuid.UUID = Field(..., description="UUID of the listing draft to grade")


class GradingResult(BaseModel):
    """Full AI grading result returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    grade: Optional[str] = Field(None, description="Quality grade: A, B, or C")
    confidence: int = Field(..., ge=0, le=100, description="AI confidence 0-100")
    colour: Optional[str] = Field(None, description="Colour assessment")
    size_uniformity: Optional[str] = Field(None, description="Size uniformity assessment")
    visible_damage: Optional[str] = Field(None, description="Visible damage description")
    buyer_acceptance: Optional[str] = Field(
        None, description="Estimated buyer acceptance level"
    )
    estimated_shelf_life_days: Optional[int] = Field(
        None, description="Estimated remaining shelf life in days"
    )
    issues: Optional[list[str]] = Field(
        default=None, description="List of quality issues found"
    )
    tip: Optional[str] = Field(None, description="Improvement tip in English")
    tip_te: Optional[str] = Field(None, description="Improvement tip in Telugu")
    ai_provider: str = Field(..., description="claude | gemini | manual")
    low_confidence_warning: bool = Field(
        default=False,
        description="True when confidence is below the threshold",
    )


class GradingStatusResponse(BaseModel):
    """Current grading status and optional result for a draft."""

    model_config = ConfigDict(from_attributes=True)

    draft_id: uuid.UUID
    grading_status: str = Field(
        ..., description="pending | processing | completed | failed | manual"
    )
    result: Optional[GradingResult] = None
    message: Optional[str] = Field(
        None, description="Human-readable status message"
    )
