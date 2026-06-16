"""Unit tests for app.core.validators — pure functions, no DB."""

import pytest
from datetime import datetime, timedelta, timezone

from app.core.validators import (
    calculate_completeness_score,
    calculate_floor_price,
    calculate_payout_preview,
    validate_crop,
    validate_district,
    validate_floor_price,
    validate_phone,
    validate_publish_preflight,
    validate_quantity,
    validate_ready_to_publish,
    validate_status_transition,
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


# ── validate_crop ──────────────────────────────────────────

class TestValidateCrop:
    def test_tomato_allowed(self):
        validate_crop("tomato")

    def test_chilli_dry_allowed(self):
        validate_crop("chilli_dry")

    def test_chilli_green_allowed(self):
        validate_crop("chilli_green")

    def test_groundnut_allowed(self):
        validate_crop("groundnut")

    def test_cotton_rejected(self):
        with pytest.raises(CropNotInPhase1Error):
            validate_crop("cotton")

    def test_rice_rejected(self):
        with pytest.raises(CropNotInPhase1Error):
            validate_crop("rice")

    def test_empty_string_rejected(self):
        with pytest.raises(CropNotInPhase1Error):
            validate_crop("")


# ── validate_district ──────────────────────────────────────

class TestValidateDistrict:
    def test_kurnool_allowed(self):
        validate_district("kurnool")

    def test_nandyal_allowed(self):
        validate_district("nandyal")

    def test_hyderabad_rejected(self):
        with pytest.raises(DistrictNotActiveError):
            validate_district("hyderabad")


# ── validate_quantity ──────────────────────────────────────

class TestValidateQuantity:
    def test_min_boundary_100kg(self):
        validate_quantity(100, "tomato")

    def test_max_boundary_25000kg(self):
        validate_quantity(25000, "tomato")

    def test_normal_800kg(self):
        validate_quantity(800, "tomato")

    def test_below_min_50kg(self):
        with pytest.raises(QuantityTooLowError):
            validate_quantity(50, "tomato")

    def test_above_max_30000kg(self):
        with pytest.raises(QuantityTooHighError):
            validate_quantity(30000, "tomato")


# ── calculate_floor_price ──────────────────────────────────

class TestFloorPrice:
    def test_1240_gives_1054(self):
        assert calculate_floor_price(1240) == 1054.0

    def test_zero_modal(self):
        assert calculate_floor_price(0) == 0.0

    def test_1000_gives_850(self):
        assert calculate_floor_price(1000) == 850.0


# ── validate_floor_price ──────────────────────────────────

class TestValidateFloorPrice:
    def test_above_floor_passes(self):
        validate_floor_price(1100, 1054, 1240)

    def test_at_floor_passes(self):
        validate_floor_price(1054, 1054, 1240)

    def test_below_floor_raises(self):
        with pytest.raises(FloorPriceViolationError):
            validate_floor_price(900, 1054, 1240)


# ── validate_ready_to_publish ──────────────────────────────

class TestValidateReadyToPublish:
    def test_all_valid(self):
        validate_ready_to_publish(3, "A", True, True)

    def test_no_photos_raises(self):
        with pytest.raises(PhotosRequiredError):
            validate_ready_to_publish(0, "A", True, True)

    def test_insufficient_photos_raises(self):
        with pytest.raises(PhotosRequiredError):
            validate_ready_to_publish(2, "A", True, True)

    def test_no_grade_raises(self):
        with pytest.raises(GradeNotSetError):
            validate_ready_to_publish(3, None, True, True)

    def test_no_consent_quality_raises(self):
        with pytest.raises(ConsentRequiredError):
            validate_ready_to_publish(3, "A", False, True)

    def test_no_consent_price_raises(self):
        with pytest.raises(ConsentRequiredError):
            validate_ready_to_publish(3, "A", True, False)


# ── validate_status_transition ─────────────────────────────

class TestStatusTransition:
    def test_active_to_paused(self):
        validate_status_transition("active", "paused")

    def test_active_to_cancelled(self):
        validate_status_transition("active", "cancelled")

    def test_active_to_expired(self):
        validate_status_transition("active", "expired")

    def test_sold_to_active_invalid(self):
        with pytest.raises(InvalidStatusTransitionError):
            validate_status_transition("sold", "active")

    def test_expired_to_active(self):
        validate_status_transition("expired", "active")

    def test_cancelled_to_active_invalid(self):
        with pytest.raises(InvalidStatusTransitionError):
            validate_status_transition("cancelled", "active")


# ── validate_publish_preflight ─────────────────────────────

class TestPublishPreflight:
    def test_all_valid(self):
        validate_publish_preflight(
            kyc_status="verified",
            bank_verified=True,
            suspension_until=None,
            active_count=2,
            completeness=100,
            photos_count=3,
            grade="A",
        )

    def test_kyc_not_verified_raises(self):
        with pytest.raises(KYCNotVerifiedError):
            validate_publish_preflight(
                kyc_status="pending", bank_verified=True,
                suspension_until=None, active_count=0,
                completeness=100, photos_count=3, grade="A",
            )

    def test_max_listings_raises(self):
        with pytest.raises(MaxListingsReachedError):
            validate_publish_preflight(
                kyc_status="verified", bank_verified=True,
                suspension_until=None, active_count=5,
                completeness=100, photos_count=3, grade="A",
            )

    def test_suspended_raises(self):
        future = datetime.now(timezone.utc) + timedelta(days=10)
        with pytest.raises(SellerSuspendedError):
            validate_publish_preflight(
                kyc_status="verified", bank_verified=True,
                suspension_until=future, active_count=0,
                completeness=100, photos_count=3, grade="A",
            )

    def test_incomplete_draft_raises(self):
        with pytest.raises(ValueError, match="completeness"):
            validate_publish_preflight(
                kyc_status="verified", bank_verified=True,
                suspension_until=None, active_count=0,
                completeness=80, photos_count=3, grade="A",
            )


# ── validate_phone ─────────────────────────────────────────

class TestValidatePhone:
    def test_valid_phone(self):
        validate_phone("9876543210")

    def test_short_phone_raises(self):
        with pytest.raises(ValueError):
            validate_phone("12345")

    def test_alpha_phone_raises(self):
        with pytest.raises(ValueError):
            validate_phone("abcdefghij")
