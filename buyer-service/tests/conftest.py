"""Shared pytest fixtures."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4


@pytest.fixture
def sample_buyer_id():
    return str(uuid4())


@pytest.fixture
def individual_buyer_data():
    return {
        "id": str(uuid4()),
        "buyer_number": "BYR-IND-202601-A1B2C3",
        "buyer_type": "individual",
        "phone": "9876543210",
        "individual_name": "Ravi Kumar",
        "language": "te",
        "kyc_status": "fully_verified",
        "phone_verified": True,
        "aadhaar_verified": True,
        "upi_verified": True,
        "bank_verified": False,
        "email_verified": False,
        "trust_score": 50,
        "orders_completed": 0,
        "suspension_until": None,
    }


@pytest.fixture
def org_buyer_data():
    return {
        "id": str(uuid4()),
        "buyer_number": "BYR-ORG-202601-D4E5F6",
        "buyer_type": "organization",
        "phone": "9123456789",
        "company_name": "AgriTrade Ltd",
        "primary_email": "admin@agritrade.com",
        "language": "en",
        "kyc_status": "fully_verified",
        "phone_verified": True,
        "email_verified": True,
        "gstin_verified": True,
        "bank_verified": True,
        "aadhaar_verified": False,
        "upi_verified": False,
        "org_tier": "tier_1",
        "trust_score": 75,
        "orders_completed": 12,
        "suspension_until": None,
    }


@pytest.fixture
def sample_requirement_data():
    return {
        "crop": "tomato",
        "quantity_min_kg": 500,
        "quantity_max_kg": 2000,
        "quality_grade": "A",
        "price_type": "negotiable",
        "offer_price_per_q": 1200,
        "delivery_district": "kurnool",
        "gst_invoice_required": False,
        "allow_partial_match": True,
    }


@pytest.fixture
def mock_price_response():
    return {
        "modal_price": 1240.0,
        "floor_price": 868.0,
        "min_price": 900.0,
        "max_price": 1500.0,
    }
