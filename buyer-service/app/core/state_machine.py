"""Status transition machines for buyer domain entities."""

from __future__ import annotations

from app.core.exceptions import InvalidStatusTransitionError

# ── Requirement (RFQ) transitions ──────────────────────────

REQUIREMENT_TRANSITIONS: dict[str, list[str]] = {
    "active": ["matched", "cancelled", "expired"],
    "matched": ["fulfilled", "cancelled"],
    "fulfilled": [],
    "cancelled": [],
    "expired": [],
}

REQUIREMENT_TERMINAL_STATES = {"fulfilled", "cancelled", "expired"}


def validate_requirement_transition(current: str, new: str) -> bool:
    return new in REQUIREMENT_TRANSITIONS.get(current, [])


def transition_requirement(current: str, new: str) -> str:
    if not validate_requirement_transition(current, new):
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition requirement from '{current}' to '{new}'. Allowed: {REQUIREMENT_TRANSITIONS.get(current, [])}.",
            message_te=f"అవసరాన్ని '{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )
    return new


def is_requirement_terminal(status: str) -> bool:
    return status in REQUIREMENT_TERMINAL_STATES


# ── Offer transitions ─────────────────────────────────────

OFFER_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["accepted", "countered", "rejected", "expired", "withdrawn"],
    "countered": ["accepted", "countered", "rejected", "expired", "withdrawn"],
    "accepted": [],
    "rejected": [],
    "expired": [],
    "withdrawn": [],
}

OFFER_TERMINAL_STATES = {"accepted", "rejected", "expired", "withdrawn"}


def validate_offer_transition(current: str, new: str) -> bool:
    return new in OFFER_TRANSITIONS.get(current, [])


def transition_offer(current: str, new: str) -> str:
    if not validate_offer_transition(current, new):
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition offer from '{current}' to '{new}'. Allowed: {OFFER_TRANSITIONS.get(current, [])}.",
            message_te=f"ఆఫర్‌ను '{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )
    return new


def is_offer_terminal(status: str) -> bool:
    return status in OFFER_TERMINAL_STATES


# ── Order transitions ──────────────────────────────────────

ORDER_TRANSITIONS: dict[str, list[str]] = {
    "pending_escrow": ["escrow_locked", "cancelled"],
    "escrow_locked": ["dispatched", "cancelled"],
    "dispatched": ["delivered", "cancelled"],
    "delivered": ["confirmed", "disputed"],
    "confirmed": [],
    "disputed": ["resolved"],
    "resolved": [],
    "cancelled": [],
}

ORDER_TERMINAL_STATES = {"confirmed", "resolved", "cancelled"}


def validate_order_transition(current: str, new: str) -> bool:
    return new in ORDER_TRANSITIONS.get(current, [])


def transition_order(current: str, new: str) -> str:
    if not validate_order_transition(current, new):
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition order from '{current}' to '{new}'. Allowed: {ORDER_TRANSITIONS.get(current, [])}.",
            message_te=f"ఆర్డర్‌ను '{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )
    return new


def is_order_terminal(status: str) -> bool:
    return status in ORDER_TERMINAL_STATES


# ── Individual KYC transitions ─────────────────────────────

INDIVIDUAL_KYC_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["phone_verified"],
    "phone_verified": ["aadhaar_verified"],
    "aadhaar_verified": ["upi_verified"],
    "upi_verified": ["fully_verified"],
    "fully_verified": [],
}


# ── Organization KYC transitions ──────────────────────────

ORGANIZATION_KYC_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["contact_verified"],
    "contact_verified": ["gstin_pending"],
    "gstin_pending": ["gstin_verified"],
    "gstin_verified": ["bank_pending"],
    "bank_pending": ["fully_verified"],
    "fully_verified": [],
}


def validate_kyc_transition(buyer_type: str, current: str, new: str) -> bool:
    transitions = (
        INDIVIDUAL_KYC_TRANSITIONS
        if buyer_type == "individual"
        else ORGANIZATION_KYC_TRANSITIONS
    )
    if new not in transitions.get(current, []):
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition KYC from '{current}' to '{new}' for {buyer_type}.",
            message_te=f"KYC ను '{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )
    return True
