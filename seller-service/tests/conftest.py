"""Shared pytest fixtures."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4


@pytest.fixture
def sample_seller_id():
    return str(uuid4())


@pytest.fixture
def verified_seller_data():
    return {
        "id": str(uuid4()),
        "phone": "9876543210",
        "full_name": "Test Farmer",
        "kyc_status": "verified",
        "bank_verified": True,
        "upi_verified": True,
        "suspension_until": None,
        "cancellation_count": 0,
        "trust_score": 50,
        "language": "te",
    }


@pytest.fixture
def complete_draft_data():
    return {
        "step1_data": {
            "crop": "tomato",
            "quantity_kg": 800,
            "harvest_status": "harvested_today",
            "days_since_harvest": 0,
        },
        "step2_data": {
            "photo_urls": ["url1.jpg", "url2.jpg", "url3.jpg"],
            "grade": "A",
            "grading_status": "completed",
            "ai_confidence": 85,
        },
        "step3_data": {
            "ask_price_per_q": 1200,
            "floor_price_snapshot": 1054.0,
            "modal_price_snapshot": 1240.0,
            "price_fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        "step4_data": {
            "transport_type": "seller_delivers",
            "pickup_window": "morning_6_10",
            "pickup_date": (datetime.now(timezone.utc) + timedelta(days=2)).date().isoformat(),
            "pickup_address": "Farm Gate, Kurnool",
        },
        "step5_data": {
            "consent_quality": True,
            "consent_price": True,
            "consent_terms": True,
            "notes": "",
        },
    }


@pytest.fixture
def partial_draft_data():
    return {
        "step1_data": {
            "crop": "tomato",
            "quantity_kg": 800,
            "harvest_status": "harvested_today",
        },
        "step2_data": None,
        "step3_data": None,
        "step4_data": None,
        "step5_data": None,
    }


@pytest.fixture
def mock_price_response():
    return {
        "modal_price": 1240.0,
        "floor_price": 1054.0,
        "min_price": 900.0,
        "max_price": 1500.0,
    }
