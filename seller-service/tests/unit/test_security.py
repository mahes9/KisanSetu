"""Unit tests for app.core.security."""

import pytest
from app.core.security import (
    create_jwt,
    decode_jwt,
    hash_aadhaar,
    hash_password,
    verify_password,
)
from app.core.exceptions import UnauthorizedError


class TestPasswordHashing:
    def test_hash_returns_string(self):
        h = hash_password("test123")
        assert isinstance(h, str)

    def test_hash_not_plaintext(self):
        h = hash_password("test123")
        assert h != "test123"

    def test_verify_correct_password(self):
        h = hash_password("test123")
        assert verify_password("test123", h) is True

    def test_verify_wrong_password(self):
        h = hash_password("test123")
        assert verify_password("wrong", h) is False

    def test_different_inputs_different_hashes(self):
        h1 = hash_password("pass1")
        h2 = hash_password("pass2")
        assert h1 != h2


class TestJWT:
    def test_roundtrip(self):
        token = create_jwt(seller_id="abc-123")
        decoded = decode_jwt(token)
        assert decoded["seller_id"] == "abc-123"

    def test_custom_payload(self):
        token = create_jwt(seller_id="abc-123", payload={"role": "seller"})
        decoded = decode_jwt(token)
        assert decoded["seller_id"] == "abc-123"
        assert decoded["role"] == "seller"

    def test_expired_token_raises(self):
        token = create_jwt(seller_id="abc-123", expires_in=-1)
        with pytest.raises(UnauthorizedError):
            decode_jwt(token)

    def test_invalid_token_raises(self):
        with pytest.raises(UnauthorizedError):
            decode_jwt("garbage.token.here")

    def test_token_has_exp_and_iat(self):
        token = create_jwt(seller_id="abc-123")
        decoded = decode_jwt(token)
        assert "exp" in decoded
        assert "iat" in decoded


class TestAadhaarHashing:
    def test_consistent_hash(self):
        h1 = hash_aadhaar("123456789012")
        h2 = hash_aadhaar("123456789012")
        assert h1 == h2

    def test_different_input_different_hash(self):
        h1 = hash_aadhaar("123456789012")
        h2 = hash_aadhaar("987654321098")
        assert h1 != h2

    def test_hash_length_64(self):
        h = hash_aadhaar("123456789012")
        assert len(h) == 64

    def test_hash_not_plaintext(self):
        h = hash_aadhaar("123456789012")
        assert "123456789012" not in h

    def test_hash_is_hex(self):
        h = hash_aadhaar("123456789012")
        int(h, 16)  # Should not raise
