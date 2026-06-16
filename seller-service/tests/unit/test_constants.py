"""Unit tests for app.core.constants."""

from app.core.constants import (
    PHASE1_CROPS,
    PHASE1_DISTRICTS,
    AIConfig,
    CommissionConfig,
    DraftConfig,
    FloorPriceConfig,
    ListingConfig,
    PhotoConfig,
)


class TestPhase1Scope:
    def test_phase1_crops_count(self):
        assert len(PHASE1_CROPS) == 4

    def test_phase1_crops_contains_tomato(self):
        assert "tomato" in PHASE1_CROPS

    def test_phase1_crops_contains_chilli_dry(self):
        assert "chilli_dry" in PHASE1_CROPS

    def test_phase1_crops_contains_chilli_green(self):
        assert "chilli_green" in PHASE1_CROPS

    def test_phase1_crops_contains_groundnut(self):
        assert "groundnut" in PHASE1_CROPS

    def test_phase1_districts_count(self):
        assert len(PHASE1_DISTRICTS) == 2

    def test_phase1_districts_contains_kurnool(self):
        assert "kurnool" in PHASE1_DISTRICTS

    def test_phase1_districts_contains_nandyal(self):
        assert "nandyal" in PHASE1_DISTRICTS


class TestListingConfig:
    def test_min_qty(self):
        assert ListingConfig.MIN_QTY_KG == 100

    def test_max_qty(self):
        assert ListingConfig.MAX_QTY_KG == 25000

    def test_max_active(self):
        assert ListingConfig.MAX_ACTIVE_LISTINGS == 5

    def test_max_drafts(self):
        assert ListingConfig.MAX_DRAFTS_PER_SELLER == 3

    def test_duration_days(self):
        assert ListingConfig.LISTING_DURATION_DAYS == 7

    def test_max_price_edits(self):
        assert ListingConfig.MAX_PRICE_EDITS == 3


class TestFloorPriceConfig:
    def test_floor_percent(self):
        assert FloorPriceConfig.FLOOR_PERCENT == 0.85


class TestCommissionConfig:
    def test_tier1(self):
        assert CommissionConfig.TIER1_PERCENT == 0.03

    def test_tier2(self):
        assert CommissionConfig.TIER2_PERCENT == 0.05

    def test_tier3(self):
        assert CommissionConfig.TIER3_PERCENT == 0.08

    def test_tier1_max_kg(self):
        assert CommissionConfig.TIER1_MAX_KG == 500

    def test_tier2_max_kg(self):
        assert CommissionConfig.TIER2_MAX_KG == 2000


class TestAIConfig:
    def test_confidence_threshold(self):
        assert AIConfig.CONFIDENCE_THRESHOLD == 60

    def test_timeout(self):
        assert AIConfig.GRADING_TIMEOUT_SECONDS == 10


class TestDraftConfig:
    def test_max_drafts(self):
        assert DraftConfig.MAX_DRAFTS == 3

    def test_staleness_minutes(self):
        assert DraftConfig.STALENESS_MINUTES == 30

    def test_warn_days(self):
        assert DraftConfig.WARN_INACTIVE_DAYS == 7

    def test_abandon_days(self):
        assert DraftConfig.ABANDON_INACTIVE_DAYS == 14

    def test_delete_days(self):
        assert DraftConfig.DELETE_INACTIVE_DAYS == 30


class TestPhotoConfig:
    def test_max_photos(self):
        assert PhotoConfig.MAX_PHOTOS == 3

    def test_min_photos(self):
        assert PhotoConfig.MIN_PHOTOS == 3

    def test_max_size_mb(self):
        assert PhotoConfig.MAX_SIZE_MB == 2
