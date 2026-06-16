"""Unit tests for app.core.state_machine."""

import pytest
from app.core.state_machine import (
    get_allowed_transitions,
    is_terminal,
    transition_listing,
    validate_transition,
)
from app.core.exceptions import InvalidStatusTransitionError


class TestValidateTransition:
    def test_active_to_paused(self):
        assert validate_transition("active", "paused") is True

    def test_active_to_matched(self):
        assert validate_transition("active", "matched") is True

    def test_active_to_cancelled(self):
        assert validate_transition("active", "cancelled") is True

    def test_active_to_expired(self):
        assert validate_transition("active", "expired") is True

    def test_paused_to_active(self):
        assert validate_transition("paused", "active") is True

    def test_matched_to_sold(self):
        assert validate_transition("matched", "sold") is True

    def test_sold_to_anything(self):
        assert validate_transition("sold", "active") is False
        assert validate_transition("sold", "paused") is False

    def test_expired_to_anything(self):
        assert validate_transition("expired", "active") is False
        assert validate_transition("expired", "paused") is False

    def test_cancelled_to_anything(self):
        assert validate_transition("cancelled", "active") is False

    def test_active_to_sold_invalid(self):
        assert validate_transition("active", "sold") is False

    def test_paused_to_matched_invalid(self):
        assert validate_transition("paused", "matched") is False


class TestTransitionListing:
    def test_valid_returns_new_status(self):
        assert transition_listing("active", "paused") == "paused"

    def test_invalid_raises(self):
        with pytest.raises(InvalidStatusTransitionError):
            transition_listing("sold", "active")

    def test_cancelled_to_active_raises(self):
        with pytest.raises(InvalidStatusTransitionError):
            transition_listing("cancelled", "active")


class TestIsTerminal:
    def test_sold_is_terminal(self):
        assert is_terminal("sold") is True

    def test_expired_is_terminal(self):
        assert is_terminal("expired") is True

    def test_cancelled_is_terminal(self):
        assert is_terminal("cancelled") is True

    def test_active_is_not_terminal(self):
        assert is_terminal("active") is False

    def test_paused_is_not_terminal(self):
        assert is_terminal("paused") is False

    def test_matched_is_not_terminal(self):
        assert is_terminal("matched") is False


class TestGetAllowedTransitions:
    def test_active(self):
        allowed = get_allowed_transitions("active")
        assert set(allowed) == {"paused", "matched", "cancelled", "expired"}

    def test_sold_empty(self):
        assert get_allowed_transitions("sold") == []

    def test_unknown_empty(self):
        assert get_allowed_transitions("unknown") == []
