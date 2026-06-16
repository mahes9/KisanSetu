"""Domain enumerations for the Seller Service."""

from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    """Base class for string enums (compatible with Python 3.11+)."""

    def __str__(self) -> str:
        return self.value


class ListingStatus(_StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    MATCHED = "matched"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class KycStatus(_StrEnum):
    PENDING = "pending"
    AADHAAR_VERIFIED = "aadhaar_verified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class HarvestStatus(_StrEnum):
    ON_TREE = "on_tree"
    HARVESTED_TODAY = "harvested_today"
    HARVESTED_1_3_DAYS = "harvested_1_3_days"
    HARVESTED_3_7_DAYS = "harvested_3_7_days"


class TransportType(_StrEnum):
    SELLER_DELIVERS = "seller_delivers"
    BUYER_PICKS_UP = "buyer_picks_up"
    PLATFORM_ARRANGED = "platform_arranged"


class PickupWindow(_StrEnum):
    MORNING_6_10 = "morning_6_10"
    MIDDAY_10_2 = "midday_10_2"
    AFTERNOON_2_6 = "afternoon_2_6"
    EVENING_6_9 = "evening_6_9"


class CropType(_StrEnum):
    TOMATO = "tomato"
    CHILLI_DRY = "chilli_dry"
    CHILLI_GREEN = "chilli_green"
    GROUNDNUT = "groundnut"


class Grade(_StrEnum):
    A = "A"
    B = "B"
    C = "C"


class DraftStatus(_StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    PUBLISHED = "published"
    ABANDONED = "abandoned"


class SaveTrigger(_StrEnum):
    MANUAL = "manual"
    AUTO_SAVE = "auto_save"
    STEP_COMPLETE = "step_complete"


class GradingStatus(_StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    MANUAL = "manual"
