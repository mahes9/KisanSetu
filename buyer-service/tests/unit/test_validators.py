"""Unit tests for app.core.validators — pure functions, no DB."""

import pytest

from app.core.validators import (
    calculate_buyer_commission,
    calculate_price_floor,
    validate_crop,
    validate_district,
    validate_language,
    validate_location_limit,
    validate_offer_price,
    validate_phone,
    validate_quantity,
    validate_rfq_limit,
)
from app.core.exceptions import (
    CropNotInPhase1Error,
    DistrictNotActiveError,
    InvalidLanguageError,
    MaxLocationsReachedError,
    MaxRFQsReachedError,
    PriceFloorViolationError,
    QuantityTooHighError,
    QuantityTooLowError,
)


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

    def test_empty_string_rejected(self):
        with pytest.raises(CropNotInPhase1Error):
            validate_crop("")


class TestValidateDistrict:
    def test_kurnool_allowed(self):
        validate_district("kurnool")

    def test_nandyal_allowed(self):
        validate_district("nandyal")

    def test_hyderabad_rejected(self):
        with pytest.raises(DistrictNotActiveError):
            validate_district("hyderabad")


class TestValidateLanguage:
    def test_english_allowed(self):
        validate_language("en")

    def test_telugu_allowed(self):
        validate_language("te")

    def test_hindi_rejected(self):
        with pytest.raises(InvalidLanguageError):
            validate_language("hi")


class TestValidateQuantity:
    def test_individual_min_boundary(self):
        validate_quantity(100, "individual")

    def test_individual_max_boundary(self):
        validate_quantity(5000, "individual")

    def test_individual_below_min(self):
        with pytest.raises(QuantityTooLowError):
            validate_quantity(50, "individual")

    def test_individual_above_max(self):
        with pytest.raises(QuantityTooHighError):
            validate_quantity(6000, "individual")

    def test_org_min_boundary(self):
        validate_quantity(500, "organization")

    def test_org_max_boundary(self):
        validate_quantity(50000, "organization")

    def test_org_below_min(self):
        with pytest.raises(QuantityTooLowError):
            validate_quantity(100, "organization")

    def test_org_above_max(self):
        with pytest.raises(QuantityTooHighError):
            validate_quantity(60000, "organization")


class TestCalculatePriceFloor:
    def test_1240_gives_868(self):
        assert calculate_price_floor(1240) == 868.0

    def test_zero_modal(self):
        assert calculate_price_floor(0) == 0.0

    def test_1000_gives_700(self):
        assert calculate_price_floor(1000) == 700.0


class TestValidateOfferPrice:
    def test_above_floor_passes(self):
        validate_offer_price(900, 1240)

    def test_at_floor_passes(self):
        validate_offer_price(868, 1240)

    def test_below_floor_raises(self):
        with pytest.raises(PriceFloorViolationError):
            validate_offer_price(800, 1240)


class TestValidateRfqLimit:
    def test_individual_under_limit(self):
        validate_rfq_limit(2, "individual")

    def test_individual_at_limit(self):
        with pytest.raises(MaxRFQsReachedError):
            validate_rfq_limit(3, "individual")

    def test_org_tier1_under_limit(self):
        validate_rfq_limit(19, "organization", "tier_1")

    def test_org_tier1_at_limit(self):
        with pytest.raises(MaxRFQsReachedError):
            validate_rfq_limit(20, "organization", "tier_1")

    def test_org_tier3_at_limit(self):
        with pytest.raises(MaxRFQsReachedError):
            validate_rfq_limit(5, "organization", "tier_3")


class TestValidateLocationLimit:
    def test_individual_first_location(self):
        validate_location_limit(0, "individual")

    def test_individual_at_limit(self):
        with pytest.raises(MaxLocationsReachedError):
            validate_location_limit(1, "individual")

    def test_org_under_limit(self):
        validate_location_limit(5, "organization")


class TestCalculateBuyerCommission:
    def test_individual_commission(self):
        assert calculate_buyer_commission(10000, "individual") == 500.0

    def test_org_tier1_commission(self):
        assert calculate_buyer_commission(10000, "organization", "tier_1") == 300.0

    def test_org_tier3_commission(self):
        assert calculate_buyer_commission(10000, "organization", "tier_3") == 500.0


class TestValidatePhone:
    def test_valid_phone(self):
        validate_phone("9876543210")

    def test_short_phone_raises(self):
        with pytest.raises(ValueError):
            validate_phone("12345")

    def test_alpha_phone_raises(self):
        with pytest.raises(ValueError):
            validate_phone("abcdefghij")
