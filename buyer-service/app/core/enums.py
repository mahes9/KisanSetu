"""Domain enumerations for the Buyer Service."""

from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    """Base class for string enums (compatible with Python 3.11+)."""

    def __str__(self) -> str:
        return self.value


# ── Buyer types ────────────────────────────────────────────

class BuyerType(_StrEnum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"


# ── KYC status per buyer type ──────────────────────────────

class IndividualKycStatus(_StrEnum):
    PENDING = "pending"
    PHONE_VERIFIED = "phone_verified"
    AADHAAR_VERIFIED = "aadhaar_verified"
    UPI_VERIFIED = "upi_verified"
    FULLY_VERIFIED = "fully_verified"


class OrganizationKycStatus(_StrEnum):
    PENDING = "pending"
    CONTACT_VERIFIED = "contact_verified"
    GSTIN_PENDING = "gstin_pending"
    GSTIN_VERIFIED = "gstin_verified"
    BANK_PENDING = "bank_pending"
    FULLY_VERIFIED = "fully_verified"


# ── Requirement / RFQ ─────────────────────────────────────

class RequirementStatus(_StrEnum):
    ACTIVE = "active"
    MATCHED = "matched"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PriceType(_StrEnum):
    FIXED = "fixed"
    NEGOTIABLE = "negotiable"
    BEST_OFFER = "best_offer"
    MARKET = "market"


# ── Offers & Negotiation ──────────────────────────────────

class OfferStatus(_StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COUNTERED = "countered"
    REJECTED = "rejected"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"


# ── Orders ─────────────────────────────────────────────────

class OrderStatus(_StrEnum):
    PENDING_ESCROW = "pending_escrow"
    ESCROW_LOCKED = "escrow_locked"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


# ── Crops & Quality ────────────────────────────────────────

class CropType(_StrEnum):
    TOMATO = "tomato"
    CHILLI_DRY = "chilli_dry"
    CHILLI_GREEN = "chilli_green"
    GROUNDNUT = "groundnut"


class Grade(_StrEnum):
    A = "A"
    B = "B"
    C = "C"


# ── Organization roles ─────────────────────────────────────

class OrgUserRole(_StrEnum):
    ADMIN = "admin"
    BUYER = "buyer"
    FINANCE = "finance"
    VIEWER = "viewer"


# ── Organization tiers ─────────────────────────────────────

class OrgTier(_StrEnum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


# ── Payment methods ────────────────────────────────────────

class PaymentMethod(_StrEnum):
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"


# ── Language ───────────────────────────────────────────────

class Language(_StrEnum):
    ENGLISH = "en"
    TELUGU = "te"


# ── Business type (org buyers) ─────────────────────────────

class BusinessType(_StrEnum):
    TRADER = "trader"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    PROCESSOR = "processor"
    EXPORTER = "exporter"
    RESTAURANT = "restaurant"
    OTHER = "other"


# ── Buyer segment (org buyers) ─────────────────────────────

class BuyerSegment(_StrEnum):
    MANDI_TRADER = "mandi_trader"
    WHOLESALE = "wholesale"
    RETAIL_CHAIN = "retail_chain"
    PROCESSOR = "processor"
    EXPORTER = "exporter"
    HORECA = "horeca"
    OTHER = "other"
