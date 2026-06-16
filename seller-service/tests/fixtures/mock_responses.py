"""Mock response data for tests."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

MOCK_CLAUDE_GRADING_RESPONSE = {
    "grade": "A",
    "confidence": 85,
    "colour": "Deep red, uniform across lot",
    "size_uniformity": "High - >70% similar size",
    "visible_damage": "none",
    "buyer_acceptance": "high",
    "estimated_shelf_life_days": 6,
    "issues": [],
    "tip": "Maintain cold chain during transport for best shelf life.",
    "tip_te": "ఉత్తమ షెల్ఫ్ లైఫ్ కోసం రవాణా సమయంలో కోల్డ్ చైన్ నిర్వహించండి.",
}

MOCK_GEMINI_GRADING_RESPONSE = {
    "grade": "B",
    "confidence": 72,
    "colour": "Mixed red and orange",
    "size_uniformity": "Moderate - 50-70% uniform",
    "visible_damage": "minimal",
    "buyer_acceptance": "medium",
    "estimated_shelf_life_days": 4,
    "issues": ["Some orange patches", "Minor size variation"],
    "tip": "Sort by color before packing for better buyer acceptance.",
    "tip_te": "మెరుగైన కొనుగోలుదారు ఆమోదం కోసం ప్యాకింగ్ ముందు రంగు ద్వారా క్రమబద్ధీకరించండి.",
}

MOCK_PRICE_RESPONSE = {
    "modal_price": 1240.0,
    "floor_price": 1054.0,
    "min_price": 900.0,
    "max_price": 1500.0,
}

MOCK_SELLER_VERIFIED = {
    "id": str(uuid4()),
    "phone": "9876543210",
    "full_name": "Test Farmer",
    "kyc_status": "verified",
    "bank_verified": True,
    "upi_verified": True,
    "suspension_until": None,
    "cancellation_count": 0,
    "trust_score": 50,
}

MOCK_SELLER_PENDING = {
    "id": str(uuid4()),
    "phone": "9876543211",
    "full_name": "Pending Farmer",
    "kyc_status": "pending",
    "bank_verified": False,
    "trust_score": 0,
}

MOCK_COMPLETE_DRAFT = {
    "step1_data": {"crop": "tomato", "quantity_kg": 800, "harvest_status": "harvested_today"},
    "step2_data": {"photo_urls": ["a.jpg", "b.jpg", "c.jpg"], "grade": "A", "grading_status": "completed", "ai_confidence": 85},
    "step3_data": {"ask_price_per_q": 1200, "floor_price_snapshot": 1054.0, "modal_price_snapshot": 1240.0, "price_fetched_at": datetime.now(timezone.utc).isoformat()},
    "step4_data": {"transport_type": "seller_delivers", "pickup_window": "morning_6_10"},
    "step5_data": {"consent_quality": True, "consent_price": True, "consent_terms": True},
}

MOCK_EMPTY_DRAFT = {
    "step1_data": {"crop": "tomato", "quantity_kg": 500},
    "step2_data": None,
    "step3_data": None,
    "step4_data": None,
    "step5_data": None,
}

MOCK_LISTING_ACTIVE = {
    "id": str(uuid4()),
    "listing_number": "KGP-20260601-1234",
    "crop": "tomato",
    "quantity_kg": 800,
    "grade": "A",
    "ask_price_per_q": 1200,
    "status": "active",
    "price_edit_count": 0,
    "expires_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
}

MOCK_NOTIFICATION_SUCCESS = {
    "sent": True,
    "message_id": "msg_test_12345",
}
