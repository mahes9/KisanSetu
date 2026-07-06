"""Pydantic v2 schemas for the Listing Draft module."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================================
# Step-level data schemas
# =====================================================================


class Step1Data(BaseModel):
    """Crop basics collected in wizard step 1."""

    model_config = ConfigDict(from_attributes=True)

    crop: str = Field(..., description="Crop type identifier, e.g. 'tomato'")
    quantity_kg: float = Field(
        ...,
        ge=100,
        le=25000,
        description="Quantity in kilograms (100-25 000 kg)",
    )
    harvest_status: str = Field(..., description="Harvest status enum value")
    days_since_harvest: Optional[int] = Field(
        None,
        ge=0,
        description="Days elapsed since harvest (0 = harvested today)",
    )


class Step2Data(BaseModel):
    """Photos and grading data collected in wizard step 2."""

    model_config = ConfigDict(from_attributes=True)

    photo_urls: Optional[list[str]] = Field(
        None,
        description="List of uploaded photo URLs (minimum 3 for completion)",
    )
    variety: Optional[str] = Field(None, description="Crop variety, e.g. 'Sona Masuri'")
    grade: Optional[str] = Field(None, description="Quality grade: A, B, or C")
    grading_status: Optional[str] = Field(
        None,
        description="AI grading pipeline status",
    )
    ai_confidence: Optional[int] = Field(
        None,
        description="AI grading confidence 0-100",
    )
    moisture_pct: Optional[float] = Field(None, description="Moisture percentage")
    foreign_matter_pct: Optional[float] = Field(None, description="Foreign matter percentage")


class Step3Data(BaseModel):
    """Pricing data collected in wizard step 3."""

    model_config = ConfigDict(from_attributes=True)

    ask_price_per_q: float = Field(
        ...,
        gt=0,
        description="Asking price per quintal in INR",
    )
    payment_terms: Optional[str] = Field(
        None,
        description="Payment terms: advance, on_delivery, credit_7, credit_15, credit_30",
    )
    negotiable: Optional[bool] = Field(
        None,
        description="Whether the price is negotiable",
    )
    price_validity_days: Optional[int] = Field(
        None,
        ge=1,
        le=30,
        description="Number of days the price is valid (1-30)",
    )
    floor_price_snapshot: Optional[float] = Field(
        None,
        description="Market floor price at time of entry",
    )
    modal_price_snapshot: Optional[float] = Field(
        None,
        description="Market modal price at time of entry",
    )
    price_fetched_at: Optional[datetime] = Field(
        None,
        description="Timestamp when market prices were fetched",
    )


class Step4Data(BaseModel):
    """Transport / pickup details collected in wizard step 4."""

    model_config = ConfigDict(from_attributes=True)

    transport_type: str = Field(
        ...,
        description="Transport arrangement type",
    )
    pickup_window: Optional[str] = Field(
        None,
        description="Preferred pickup time window",
    )
    pickup_date: Optional[date] = Field(
        None,
        description="Preferred pickup date",
    )
    pickup_address: Optional[str] = Field(
        None,
        description="Full pickup address text",
    )


class Step5Data(BaseModel):
    """Consents and notes collected in wizard step 5."""

    model_config = ConfigDict(from_attributes=True)

    consent_quality: bool = Field(
        ...,
        description="Seller confirms quality accuracy",
    )
    consent_price: bool = Field(
        ...,
        description="Seller confirms pricing accuracy",
    )
    consent_terms: bool = Field(
        ...,
        description="Seller accepts platform terms",
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional seller notes",
    )


# =====================================================================
# Request schemas
# =====================================================================


class CreateDraftRequest(BaseModel):
    """Payload to create a new listing draft (step 1 data required)."""

    model_config = ConfigDict(from_attributes=True)

    step1: Step1Data


class SaveDraftRequest(BaseModel):
    """Payload to save (or auto-save) a single step's data."""

    model_config = ConfigDict(from_attributes=True)

    step_number: int = Field(..., ge=1, le=5, description="Wizard step number")
    step_data: dict = Field(..., description="Arbitrary step data to persist")
    save_trigger: str = Field(
        "manual",
        description="What triggered this save: manual | auto_save | step_complete",
    )
    device: Optional[str] = Field(None, max_length=50, description="Client device identifier")
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Client session identifier",
    )
    network_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Network type: wifi | 4g | 3g | 2g",
    )


# =====================================================================
# Response schemas
# =====================================================================


class DraftResponse(BaseModel):
    """Full representation of a listing draft returned to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    seller_id: uuid.UUID
    draft_status: str
    current_step: int
    completeness_score: int

    step1_data: Optional[dict] = None
    step2_data: Optional[dict] = None
    step3_data: Optional[dict] = None
    step4_data: Optional[dict] = None
    step5_data: Optional[dict] = None

    step1_completed: bool = False
    step2_completed: bool = False
    step3_completed: bool = False
    step4_completed: bool = False
    step5_completed: bool = False

    last_active_at: Optional[datetime] = None

    # ── Computed / enriched fields ───────────────────────────────────
    price_stale: Optional[bool] = None
    missing_fields: Optional[list[str]] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DraftListResponse(BaseModel):
    """Paginated list of drafts for a seller."""

    model_config = ConfigDict(from_attributes=True)

    drafts: list[DraftResponse]
    total: int
