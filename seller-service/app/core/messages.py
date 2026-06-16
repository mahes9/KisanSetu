"""Bilingual message templates (English + Telugu)."""

from __future__ import annotations

SUCCESS_MESSAGES: dict[str, dict[str, str]] = {
    "listing_published": {
        "en": "Your listing has been published successfully!",
        "te": "మీ లిస్టింగ్ విజయవంతంగా ప్రచురించబడింది!",
    },
    "draft_saved": {
        "en": "Draft saved successfully.",
        "te": "డ్రాఫ్ట్ విజయవంతంగా సేవ్ చేయబడింది.",
    },
    "draft_deleted": {
        "en": "Draft deleted.",
        "te": "డ్రాఫ్ట్ తొలగించబడింది.",
    },
    "draft_cloned": {
        "en": "Draft cloned successfully.",
        "te": "డ్రాఫ్ట్ విజయవంతంగా క్లోన్ చేయబడింది.",
    },
    "kyc_verified": {
        "en": "Your KYC has been verified.",
        "te": "మీ KYC ధృవీకరించబడింది.",
    },
    "bank_verified": {
        "en": "Bank account verified successfully.",
        "te": "బ్యాంక్ ఖాతా విజయవంతంగా ధృవీకరించబడింది.",
    },
    "photo_uploaded": {
        "en": "Photos uploaded successfully.",
        "te": "ఫోటోలు విజయవంతంగా అప్‌లోడ్ చేయబడ్డాయి.",
    },
    "grade_completed": {
        "en": "Quality grading completed.",
        "te": "నాణ్యత గ్రేడింగ్ పూర్తయింది.",
    },
    "listing_cancelled": {
        "en": "Listing has been cancelled.",
        "te": "లిస్టింగ్ రద్దు చేయబడింది.",
    },
    "listing_paused": {
        "en": "Listing has been paused.",
        "te": "లిస్టింగ్ పాజ్ చేయబడింది.",
    },
    "listing_resumed": {
        "en": "Listing has been resumed.",
        "te": "లిస్టింగ్ పునఃప్రారంభించబడింది.",
    },
    "listing_expired": {
        "en": "Your listing has expired.",
        "te": "మీ లిస్టింగ్ గడువు ముగిసింది.",
    },
    "price_updated": {
        "en": "Price updated successfully.",
        "te": "ధర విజయవంతంగా నవీకరించబడింది.",
    },
}

ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "E001": {"en": "Ask price is below the floor price.", "te": "అడిగిన ధర కనిష్ట ధర కంటే తక్కువగా ఉంది."},
    "E002": {"en": "This crop is not available in Phase 1.", "te": "ఈ పంట ఫేజ్ 1లో అందుబాటులో లేదు."},
    "E003": {"en": "This district is not active in Phase 1.", "te": "ఈ జిల్లా ఫేజ్ 1లో చురుకుగా లేదు."},
    "E004": {"en": "Quantity is below the minimum.", "te": "పరిమాణం కనీసం కంటే తక్కువగా ఉంది."},
    "E005": {"en": "Quantity exceeds the maximum.", "te": "పరిమాణం గరిష్టాన్ని మించిపోయింది."},
    "E006": {"en": "KYC verification is required.", "te": "KYC ధృవీకరణ అవసరం."},
    "E007": {"en": "At least 3 photos required.", "te": "కనీసం 3 ఫోటోలు అవసరం."},
    "E008": {"en": "Quality grade must be set.", "te": "నాణ్యత గ్రేడ్ సెట్ చేయాలి."},
    "E009": {"en": "Consent is required.", "te": "అంగీకారం అవసరం."},
    "E010": {"en": "Invalid status transition.", "te": "చెల్లని స్థితి మార్పు."},
    "E011": {"en": "Listing not found.", "te": "లిస్టింగ్ కనుగొనబడలేదు."},
    "E012": {"en": "Maximum active listings reached.", "te": "గరిష్ట చురుకు లిస్టింగ్‌లు చేరుకుంది."},
    "E013": {"en": "Draft not found.", "te": "డ్రాఫ్ట్ కనుగొనబడలేదు."},
    "E014": {"en": "Maximum drafts reached.", "te": "గరిష్ట డ్రాఫ్ట్‌లు చేరుకుంది."},
    "E015": {"en": "Already published.", "te": "ఇప్పటికే ప్రచురించబడింది."},
    "E016": {"en": "Seller not found.", "te": "విక్రేత కనుగొనబడలేదు."},
    "E017": {"en": "Invalid OTP.", "te": "చెల్లని OTP."},
    "E018": {"en": "OTP expired.", "te": "OTP గడువు ముగిసింది."},
    "E019": {"en": "Aadhaar verification failed.", "te": "ఆధార్ ధృవీకరణ విఫలమైంది."},
    "E020": {"en": "Bank verification failed.", "te": "బ్యాంక్ ధృవీకరణ విఫలమైంది."},
    "E021": {"en": "Photo upload failed.", "te": "ఫోటో అప్‌లోడ్ విఫలమైంది."},
    "E022": {"en": "AI grading failed.", "te": "AI గ్రేడింగ్ విఫలమైంది."},
    "E023": {"en": "Price data is stale.", "te": "ధర డేటా పాతది."},
    "E024": {"en": "Duplicate photo.", "te": "నకిలీ ఫోటో."},
    "E025": {"en": "Account suspended.", "te": "ఖాతా సస్పెండ్ చేయబడింది."},
    "E026": {"en": "Maximum price edits reached.", "te": "గరిష్ట ధర సవరణలు చేరుకుంది."},
    "E027": {"en": "Authentication required.", "te": "ప్రామాణీకరణ అవసరం."},
    "E028": {"en": "Farm not found.", "te": "వ్యవసాయ క్షేత్రం కనుగొనబడలేదు."},
    "E029": {"en": "Invalid crop type.", "te": "చెల్లని పంట రకం."},
    "E030": {"en": "You do not own this draft.", "te": "ఈ డ్రాఫ్ట్ మీది కాదు."},
}


def get_message(key: str, language: str = "en") -> str:
    msgs = SUCCESS_MESSAGES.get(key) or ERROR_MESSAGES.get(key)
    if msgs is None:
        return key
    return msgs.get(language, msgs.get("en", key))
