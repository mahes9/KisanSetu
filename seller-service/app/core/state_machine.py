"""Listing status transition machine."""

from __future__ import annotations

from app.core.exceptions import InvalidStatusTransitionError

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "active": ["paused", "matched", "cancelled", "expired"],
    "paused": ["active", "cancelled", "expired"],
    "matched": ["sold", "cancelled"],
    "sold": [],
    "expired": [],
    "cancelled": [],
}

TERMINAL_STATES = {"sold", "expired", "cancelled"}


def validate_transition(current: str, new: str) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, [])


def transition_listing(current: str, new: str) -> str:
    if not validate_transition(current, new):
        raise InvalidStatusTransitionError(
            message_en=f"Cannot transition from '{current}' to '{new}'. Allowed: {ALLOWED_TRANSITIONS.get(current, [])}.",
            message_te=f"'{current}' నుండి '{new}' కి మారడం సాధ్యం కాదు.",
        )
    return new


def get_allowed_transitions(current: str) -> list[str]:
    return ALLOWED_TRANSITIONS.get(current, [])


def is_terminal(status: str) -> bool:
    return status in TERMINAL_STATES
