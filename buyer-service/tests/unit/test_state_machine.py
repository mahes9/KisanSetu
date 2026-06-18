"""Unit tests for state machine transitions."""

import pytest

from app.core.state_machine import (
    is_offer_terminal,
    is_order_terminal,
    is_requirement_terminal,
    transition_offer,
    transition_order,
    transition_requirement,
    validate_kyc_transition,
)
from app.core.exceptions import InvalidStatusTransitionError


class TestRequirementTransitions:
    def test_active_to_matched(self):
        transition_requirement("active", "matched")

    def test_active_to_cancelled(self):
        transition_requirement("active", "cancelled")

    def test_active_to_expired(self):
        transition_requirement("active", "expired")

    def test_matched_to_active_invalid(self):
        with pytest.raises(InvalidStatusTransitionError):
            transition_requirement("matched", "active")

    def test_cancelled_is_terminal(self):
        assert is_requirement_terminal("cancelled") is True

    def test_active_is_not_terminal(self):
        assert is_requirement_terminal("active") is False


class TestOfferTransitions:
    def test_pending_to_accepted(self):
        transition_offer("pending", "accepted")

    def test_pending_to_rejected(self):
        transition_offer("pending", "rejected")

    def test_pending_to_countered(self):
        transition_offer("pending", "countered")

    def test_accepted_to_pending_invalid(self):
        with pytest.raises(InvalidStatusTransitionError):
            transition_offer("accepted", "pending")

    def test_accepted_is_terminal(self):
        assert is_offer_terminal("accepted") is True


class TestOrderTransitions:
    def test_escrow_locked_to_dispatched(self):
        transition_order("escrow_locked", "dispatched")

    def test_delivered_to_confirmed(self):
        transition_order("delivered", "confirmed")

    def test_confirmed_is_terminal(self):
        assert is_order_terminal("confirmed") is True

    def test_cancelled_is_terminal(self):
        assert is_order_terminal("cancelled") is True


class TestKYCTransitions:
    def test_individual_pending_to_phone_verified(self):
        validate_kyc_transition("individual", "pending", "phone_verified")

    def test_org_pending_to_contact_verified(self):
        validate_kyc_transition("organization", "pending", "contact_verified")

    def test_individual_invalid_transition(self):
        with pytest.raises(InvalidStatusTransitionError):
            validate_kyc_transition("individual", "pending", "fully_verified")
