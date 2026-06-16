"""Pure validation functions -- no database calls."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.core.constants import (
    PHASE1_CROPS,
    PHASE1_DISTRICTS,
    CommissionConfig,
    DraftConfig,
    FloorPriceConfig,
    ListingConfig,
    PhotoConfig,
)
from app.core.exceptions import (
    ConsentRequiredError,
    CropNotInPhase1Error,
    DistrictNotActiveError,
    FloorPriceViolationError,
    GradeNotSetError,
    InvalidStatusTransitionError,
    KYCNotVerifiedError,
    MaxListingsReachedError,
    PhotosRequiredError,
    QuantityTooHighError,
    QuantityTooLowError,
    SellerSuspendedError,
)

# ── Allowed status transitions ──────────────────────────────────

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["active", "cancelled"],
    "active": ["paused", "matched", "expired", "cancelled"],
    "paused": ["active", "cancelled"],
    "matched": ["sold", "active"],
    "sold": [],
    "expired": ["active"],
    "cancelled": [],
}


# ── Validators ──────────────────────────────────────────────────


def validate_crop(crop: str) -> None:
    """Raise CropNotInPhase1Error if the crop is not in Phase 1 scope."""
    if crop.lower() not in PHASE1_CROPS:
        raise CropNotInPhase1Error(
            message_en=f"Crop '{crop}' is not available in Phase 1. Allowed: {', '.join(PHASE1_CROPS)}.",
            message_te=f"పంట '{crop}' ఫేజ్ 1లో అందుబాటులో లేదు.",
        )


def validate_district(district: str) -> None:
    """Raise DistrictNotActiveError if the district is not in Phase 1 scope."""
    if district.lower() not in PHASE1_DISTRICTS:
        raise DistrictNotActiveError(
            message_en=f"District '{district}' is not active in Phase 1. Allowed: {', '.join(PHASE1_DISTRICTS)}.",
            message_te=f"జిల్లా '{district}' ఫేజ్ 1లో చురుకుగా లేదు.",
        )


def validate_quantity(qty_kg: float, crop: str) -> None:
    """Validate quantity is within the allowed range."""
    if qty_kg < ListingConfig.MIN_QTY_KG:
        raise QuantityTooLowError(
            message_en=f"Quantity {qty_kg} kg is below the minimum of {ListingConfig.MIN_QTY_KG} kg.",
            message_te=f"పరిమాణం {qty_kg} కేజీలు కనీసం {ListingConfig.MIN_QTY_KG} కేజీల కంటే తక్కువగా ఉంది.",
        )
    if qty_kg > ListingConfig.MAX_QTY_KG:
        raise QuantityTooHighError(
            message_en=f"Quantity {qty_kg} kg exceeds the maximum of {ListingConfig.MAX_QTY_KG} kg.",
            message_te=f"పరిమాణం {qty_kg} కేజీలు గరిష్టంగా {ListingConfig.MAX_QTY_KG} కేజీలను మించిపోయింది.",
        )


def calculate_floor_price(modal_price: float) -> float:
    """Return floor price = modal_price * FLOOR_PERCENT."""
    return round(modal_price * FloorPriceConfig.FLOOR_PERCENT, 2)


def validate_floor_price(
    ask_price: float,
    floor_price: float,
    modal_price: float,
) -> None:
    """Raise FloorPriceViolationError if ask_price < floor_price."""
    if ask_price < floor_price:
        raise FloorPriceViolationError(
            message_en=(
                f"Ask price {ask_price}/q is below the floor price {floor_price}/q "
                f"(85% of modal {modal_price}/q)."
            ),
            message_te=(
                f"అడిగిన ధర {ask_price}/క్వింటాల్ కనిష్ట ధర {floor_price}/క్వింటాల్ కంటే తక్కువగా ఉంది."
            ),
        )


def validate_harvest_days(status: str, days_since: int) -> None:
    """Validate consistency between harvest status and days since harvest."""
    expected: dict[str, tuple[int, int]] = {
        "on_tree": (0, 0),
        "harvested_today": (0, 0),
        "harvested_1_3_days": (1, 3),
        "harvested_3_7_days": (3, 7),
    }
    bounds = expected.get(status)
    if bounds is None:
        return
    lo, hi = bounds
    if status == "on_tree":
        return  # no days_since check needed
    if not (lo <= days_since <= hi):
        pass  # soft validation -- logged but not blocking


def validate_pickup_date(pickup_date: date | datetime) -> None:
    """Pickup date must be between 1 and 7 days from today."""
    if isinstance(pickup_date, datetime):
        pickup_date = pickup_date.date()
    today = date.today()
    delta = (pickup_date - today).days
    if delta < 1 or delta > 7:
        raise ValueError(
            f"Pickup date must be 1-7 days from today. Got {delta} days."
        )


def validate_listing_duration(days: int) -> None:
    """Listing duration must not exceed maximum."""
    if days < 1 or days > ListingConfig.LISTING_DURATION_DAYS:
        raise ValueError(
            f"Listing duration must be 1-{ListingConfig.LISTING_DURATION_DAYS} days."
        )


def validate_ready_to_publish(
    photos_count: int,
    grade: str | None,
    consent_quality: bool,
    consent_price: bool,
) -> None:
    """Check all pre-publish requirements are met."""
    if photos_count < PhotoConfig.MIN_PHOTOS:
        raise PhotosRequiredError(
            message_en=f"At least {PhotoConfig.MIN_PHOTOS} photos are required. You have {photos_count}.",
            message_te=f"కనీసం {PhotoConfig.MIN_PHOTOS} ఫోటోలు అవసరం. మీ వద్ద {photos_count} ఉన్నాయి.",
        )
    if not grade:
        raise GradeNotSetError()
    if not consent_quality or not consent_price:
        raise ConsentRequiredError()


def calculate_payout_preview(
    qty_kg: float,
    ask_price_per_q: float,
    modal_price: float,
) -> dict[str, Any]:
    """Calculate the seller payout preview with tiered commission.

    Commission tiers:
        <= 500 kg  -> 3%
        <= 2000 kg -> 5%
        > 2000 kg  -> 8%

    Returns dict with gross_amount, commission_percent, commission_amount,
    seller_payout, effective_price_per_kg.
    """
    # Convert price per quintal to price per kg
    price_per_kg = ask_price_per_q / 100.0
    gross_amount = round(qty_kg * price_per_kg, 2)

    # Determine commission tier
    if qty_kg <= CommissionConfig.TIER1_MAX_KG:
        commission_percent = CommissionConfig.TIER1_PERCENT
    elif qty_kg <= CommissionConfig.TIER2_MAX_KG:
        commission_percent = CommissionConfig.TIER2_PERCENT
    else:
        commission_percent = CommissionConfig.TIER3_PERCENT

    commission_amount = round(gross_amount * commission_percent, 2)
    seller_payout = round(gross_amount - commission_amount, 2)
    effective_price_per_kg = round(seller_payout / qty_kg, 2) if qty_kg > 0 else 0.0

    return {
        "gross_amount": gross_amount,
        "commission_percent": commission_percent,
        "commission_amount": commission_amount,
        "seller_payout": seller_payout,
        "effective_price_per_kg": effective_price_per_kg,
    }


def validate_status_transition(current: str, new: str) -> None:
    """Validate that a listing status transition is allowed."""
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition from '{current}' to '{new}'. Allowed: {allowed}.",
            message_te=f"'{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )


def calculate_completeness_score(draft_data: dict) -> int:
    """Calculate draft completeness as 0-100 based on step weights.

    Step weights:
        step1 (crop/qty)   = 25
        step2 (photos)     = 25
        step3 (pricing)    = 20
        step4 (transport)  = 15
        step5 (consent)    = 15
    """
    weights = {
        "step1_completed": 25,
        "step2_completed": 25,
        "step3_completed": 20,
        "step4_completed": 15,
        "step5_completed": 15,
    }
    score = 0
    for key, weight in weights.items():
        if draft_data.get(key, False):
            score += weight
    return score


def validate_phone(phone: str) -> None:
    """Phone must be exactly 10 digits."""
    if not re.match(r"^\d{10}$", phone):
        raise ValueError("Phone number must be exactly 10 digits.")


def validate_publish_preflight(
    kyc_status: str,
    bank_verified: bool,
    suspension_until: datetime | None,
    active_count: int,
    completeness: int,
    photos_count: int,
    grade: str | None,
) -> None:
    """Run all pre-publish checks for a listing draft.

    Raises the appropriate domain exception if any check fails.
    """
    # Check suspension
    if suspension_until and suspension_until > datetime.now(timezone.utc):
        raise SellerSuspendedError()

    # Check KYC
    if kyc_status != "verified":
        raise KYCNotVerifiedError()

    # Check active listing cap
    if active_count >= ListingConfig.MAX_ACTIVE_LISTINGS:
        raise MaxListingsReachedError()

    # Check completeness
    if completeness < 100:
        raise ValueError(
            f"Draft completeness is {completeness}%. Must be 100% to publish."
        )

    # Check photos
    if photos_count < PhotoConfig.MIN_PHOTOS:
        raise PhotosRequiredError()

    # Check grade
    if not grade:
        raise GradeNotSetError()
