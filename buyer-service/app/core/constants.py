"""Domain constants for the Buyer Service."""

from __future__ import annotations

# ── Phase 1 scope ────────────────────────────────────────

PHASE1_CROPS: list[str] = ["tomato", "chilli_dry", "chilli_green", "groundnut"]
PHASE1_DISTRICTS: list[str] = ["kurnool", "nandyal"]
ALLOWED_LANGUAGES: list[str] = ["en", "te"]


class IndividualBuyerConfig:
    """Constraints for individual buyers."""

    MIN_ORDER_KG: int = 100
    MAX_ORDER_KG: int = 5000
    MAX_ACTIVE_RFQS: int = 3
    MAX_DELIVERY_LOCATIONS: int = 1
    COMMISSION_PERCENT: float = 0.05


class OrganizationBuyerConfig:
    """Constraints for organization buyers."""

    MIN_ORDER_KG: int = 500
    MAX_ORDER_KG: int = 50000
    MAX_DELIVERY_LOCATIONS: int = 50

    TIER1_MAX_RFQS: int = 20
    TIER2_MAX_RFQS: int = 10
    TIER3_MAX_RFQS: int = 5

    TIER1_COMMISSION: float = 0.03
    TIER2_COMMISSION: float = 0.04
    TIER3_COMMISSION: float = 0.05


class RFQConfig:
    """Requirement / RFQ parameters."""

    REQUIREMENT_DURATION_DAYS: int = 7
    MAX_NEGOTIATION_ROUNDS: int = 3
    OFFER_RESPONSE_HOURS: int = 4
    DISPUTE_WINDOW_HOURS: int = 72
    PRICE_FLOOR_PERCENT: float = 0.70


class OfferConfig:
    """Offer / negotiation parameters."""

    MAX_COUNTER_OFFERS: int = 3
    RESPONSE_WINDOW_HOURS: int = 4
    AUTO_EXPIRE_HOURS: int = 24
