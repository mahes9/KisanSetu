"""Unit tests for security utilities."""

import pytest

from app.core.security import (
    create_jwt,
    decode_jwt,
    hash_aadhaar,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("test_password_123")
        assert verify_password("test_password_123", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False


class TestJWT:
    def test_create_and_decode(self):
        token = create_jwt("buyer-123")
        payload = decode_jwt(token)
        assert payload["buyer_id"] == "buyer-123"

    def test_create_with_extra_claims(self):
        token = create_jwt("buyer-456", {"buyer_type": "individual"})
        payload = decode_jwt(token)
        assert payload["buyer_id"] == "buyer-456"
        assert payload["buyer_type"] == "individual"

    def test_invalid_token_raises(self):
        with pytest.raises(Exception):
            decode_jwt("invalid.token.here")


class TestAadhaarHash:
    def test_hash_is_deterministic(self):
        h1 = hash_aadhaar("123456789012")
        h2 = hash_aadhaar("123456789012")
        assert h1 == h2

    def test_different_numbers_different_hash(self):
        h1 = hash_aadhaar("123456789012")
        h2 = hash_aadhaar("987654321098")
        assert h1 != h2
