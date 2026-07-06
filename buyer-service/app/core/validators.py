"""Pure validation functions -- no database calls."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.core.constants import (
    ALLOWED_LANGUAGES,
    PHASE1_CROPS,
    PHASE1_DISTRICTS,
    IndividualBuyerConfig,
    OrganizationBuyerConfig,
    RFQConfig,
)
from app.core.exceptions import (
    BuyerSuspendedError,
    CropNotInPhase1Error,
    DistrictNotActiveError,
    GSTINRequiredError,
    GSTInvoiceNotAvailableError,
    InvalidLanguageError,
    KYCNotVerifiedError,
    MaxLocationsReachedError,
    MaxRFQsReachedError,
    PriceFloorViolationError,
    QuantityTooHighError,
    QuantityTooLowError,
)


# ── Language ───────────────────────────────────────────────

def validate_language(language: str) -> None:
    if language not in ALLOWED_LANGUAGES:
        raise InvalidLanguageError(
            message_en=f"Language '{language}' is not supported. Allowed: {', '.join(ALLOWED_LANGUAGES)}.",
            message_te=f"భాష '{language}' మద్దతు లేదు. అనుమతించబడినవి: {', '.join(ALLOWED_LANGUAGES)}.",
        )


# ── Crop & District ────────────────────────────────────────

def validate_crop(crop: str) -> None:
    if crop.lower() not in PHASE1_CROPS:
        raise CropNotInPhase1Error(
            message_en=f"Crop '{crop}' is not available in Phase 1. Allowed: {', '.join(PHASE1_CROPS)}.",
            message_te=f"పంట '{crop}' ఫేజ్ 1లో అందుబాటులో లేదు.",
        )


def validate_district(district: str) -> None:
    if district.lower() not in PHASE1_DISTRICTS:
        raise DistrictNotActiveError(
            message_en=f"District '{district}' is not active in Phase 1. Allowed: {', '.join(PHASE1_DISTRICTS)}.",
            message_te=f"జిల్లా '{district}' ఫేజ్ 1లో చురుకుగా లేదు.",
        )


# ── Quantity validation (buyer-type aware) ─────────────────

def validate_quantity(qty_kg: float, buyer_type: str) -> None:
    if buyer_type == "individual":
        min_kg = IndividualBuyerConfig.MIN_ORDER_KG
        max_kg = IndividualBuyerConfig.MAX_ORDER_KG
    else:
        min_kg = OrganizationBuyerConfig.MIN_ORDER_KG
        max_kg = OrganizationBuyerConfig.MAX_ORDER_KG

    if qty_kg < min_kg:
        raise QuantityTooLowError(
            message_en=f"Quantity {qty_kg} kg is below the minimum of {min_kg} kg for {buyer_type} buyers.",
            message_te=f"పరిమాణం {qty_kg} కేజీలు కనీసం {min_kg} కేజీల కంటే తక్కువగా ఉంది.",
        )
    if qty_kg > max_kg:
        raise QuantityTooHighError(
            message_en=f"Quantity {qty_kg} kg exceeds the maximum of {max_kg} kg for {buyer_type} buyers.",
            message_te=f"పరిమాణం {qty_kg} కేజీలు గరిష్టంగా {max_kg} కేజీలను మించిపోయింది.",
        )


# ── Price validation ───────────────────────────────────────

def validate_offer_price(offer_price: float, modal_price: float) -> None:
    floor = modal_price * RFQConfig.PRICE_FLOOR_PERCENT
    if offer_price < floor:
        raise PriceFloorViolationError(
            message_en=(
                f"Offer price {offer_price}/q is below the floor "
                f"{floor:.2f}/q (70% of modal {modal_price}/q)."
            ),
            message_te=(
                f"ఆఫర్ ధర {offer_price}/క్వింటాల్ కనిష్ట ధర "
                f"{floor:.2f}/క్వింటాల్ కంటే తక్కువగా ఉంది."
            ),
        )


def calculate_price_floor(modal_price: float) -> float:
    return round(modal_price * RFQConfig.PRICE_FLOOR_PERCENT, 2)


# ── RFQ limits ─────────────────────────────────────────────

def validate_rfq_limit(active_count: int, buyer_type: str, org_tier: str | None = None) -> None:
    if buyer_type == "individual":
        max_rfqs = IndividualBuyerConfig.MAX_ACTIVE_RFQS
    else:
        tier_map = {
            "tier_1": OrganizationBuyerConfig.TIER1_MAX_RFQS,
            "tier_2": OrganizationBuyerConfig.TIER2_MAX_RFQS,
            "tier_3": OrganizationBuyerConfig.TIER3_MAX_RFQS,
        }
        max_rfqs = tier_map.get(org_tier or "tier_3", OrganizationBuyerConfig.TIER3_MAX_RFQS)

    if active_count >= max_rfqs:
        raise MaxRFQsReachedError(
            message_en=f"Maximum of {max_rfqs} active requirements reached.",
            message_te=f"గరిష్టంగా {max_rfqs} చురుకు అవసరాలు చేరుకుంది.",
        )


# ── Location limits ────────────────────────────────────────

def validate_location_limit(location_count: int, buyer_type: str) -> None:
    if buyer_type == "individual":
        max_locations = IndividualBuyerConfig.MAX_DELIVERY_LOCATIONS
    else:
        max_locations = OrganizationBuyerConfig.MAX_DELIVERY_LOCATIONS

    if location_count >= max_locations:
        raise MaxLocationsReachedError(
            message_en=f"Maximum of {max_locations} delivery locations reached for {buyer_type} buyer.",
            message_te=f"గరిష్టంగా {max_locations} డెలివరీ స్థానాలు చేరుకుంది.",
        )


# ── GST invoice validation ─────────────────────────────────

def validate_gst_invoice_eligibility(buyer_type: str) -> None:
    if buyer_type == "individual":
        raise GSTInvoiceNotAvailableError()


# ── Phone & GSTIN format ──────────────────────────────────

def validate_phone(phone: str) -> None:
    if not re.match(r"^\d{10}$", phone):
        raise ValueError("Phone number must be exactly 10 digits.")


def validate_gstin(gstin: str) -> None:
    if not re.match(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$", gstin):
        raise ValueError("Invalid GSTIN format.")


def validate_email(email: str) -> None:
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        raise ValueError("Invalid email format.")


def validate_upi_id(upi_id: str) -> None:
    if not re.match(r"^[a-zA-Z0-9._-]+@[a-zA-Z]{2,}$", upi_id):
        raise ValueError("Invalid UPI ID format.")


# ── Pre-RFQ checks ────────────────────────────────────────

def validate_rfq_preflight(
    kyc_status: str,
    suspension_until: datetime | None,
    active_count: int,
    buyer_type: str,
    org_tier: str | None = None,
) -> None:
    if suspension_until and suspension_until > datetime.now(timezone.utc):
        raise BuyerSuspendedError()
    if kyc_status != "fully_verified":
        raise KYCNotVerifiedError()
    validate_rfq_limit(active_count, buyer_type, org_tier)


# ── Commission calculation ─────────────────────────────────

def calculate_buyer_commission(amount: float, buyer_type: str, org_tier: str | None = None) -> float:
    if buyer_type == "individual":
        rate = IndividualBuyerConfig.COMMISSION_PERCENT
    else:
        tier_map = {
            "tier_1": OrganizationBuyerConfig.TIER1_COMMISSION,
            "tier_2": OrganizationBuyerConfig.TIER2_COMMISSION,
            "tier_3": OrganizationBuyerConfig.TIER3_COMMISSION,
        }
        rate = tier_map.get(org_tier or "tier_3", OrganizationBuyerConfig.TIER3_COMMISSION)
    return round(amount * rate, 2)
