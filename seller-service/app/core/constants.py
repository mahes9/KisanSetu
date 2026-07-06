"""Domain constants for the Seller Service."""

from __future__ import annotations

# ── Phase 1 scope ────────────────────────────────────────

PHASE1_CROPS: list[str] = ["tomato", "chilli_dry", "chilli_green", "groundnut"]
PHASE1_DISTRICTS: list[str] = ["kurnool", "nandyal"]


class ListingConfig:
    """Constraints for listings."""

    MIN_QTY_KG: int = 100
    MAX_QTY_KG: int = 25000
    MAX_ACTIVE_LISTINGS: int = 5
    MAX_DRAFTS_PER_SELLER: int = 10
    LISTING_DURATION_DAYS: int = 7
    MAX_PRICE_EDITS: int = 3


class FloorPriceConfig:
    """Floor price calculation parameters."""

    FLOOR_PERCENT: float = 0.85


class CommissionConfig:
    """Commission tier structure."""

    TIER1_PERCENT: float = 0.03
    TIER1_MAX_KG: int = 500
    TIER2_PERCENT: float = 0.05
    TIER2_MAX_KG: int = 2000
    TIER3_PERCENT: float = 0.08


class AIConfig:
    """AI grading parameters."""

    CONFIDENCE_THRESHOLD: int = 60
    GRADING_TIMEOUT_SECONDS: int = 10
    MAX_RETRIES: int = 1


class DraftConfig:
    """Draft lifecycle parameters."""

    MAX_DRAFTS: int = 10
    STALENESS_MINUTES: int = 30
    WARN_INACTIVE_DAYS: int = 7
    ABANDON_INACTIVE_DAYS: int = 14
    DELETE_INACTIVE_DAYS: int = 30


class PhotoConfig:
    """Photo upload constraints."""

    MAX_PHOTOS: int = 3
    MIN_PHOTOS: int = 3
    MAX_SIZE_MB: int = 2
    MIN_RESOLUTION: int = 640
