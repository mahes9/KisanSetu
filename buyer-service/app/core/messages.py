"""Bilingual message templates (English + Telugu)."""

from __future__ import annotations

SUCCESS_MESSAGES: dict[str, dict[str, str]] = {
    "buyer_registered": {
        "en": "Registration successful! Please complete KYC verification.",
        "te": "నమోదు విజయవంతమైంది! దయచేసి KYC ధృవీకరణ పూర్తి చేయండి.",
    },
    "phone_verified": {
        "en": "Phone number verified successfully.",
        "te": "ఫోన్ నంబర్ విజయవంతంగా ధృవీకరించబడింది.",
    },
    "aadhaar_verified": {
        "en": "Aadhaar verified successfully.",
        "te": "ఆధార్ విజయవంతంగా ధృవీకరించబడింది.",
    },
    "upi_verified": {
        "en": "UPI ID verified successfully.",
        "te": "UPI ID విజయవంతంగా ధృవీకరించబడింది.",
    },
    "gstin_verified": {
        "en": "GSTIN verified successfully.",
        "te": "GSTIN విజయవంతంగా ధృవీకరించబడింది.",
    },
    "bank_verified": {
        "en": "Bank account verified successfully.",
        "te": "బ్యాంక్ ఖాతా విజయవంతంగా ధృవీకరించబడింది.",
    },
    "kyc_complete": {
        "en": "KYC verification complete. You can now post requirements.",
        "te": "KYC ధృవీకరణ పూర్తయింది. ఇప్పుడు మీరు అవసరాలు పోస్ట్ చేయవచ్చు.",
    },
    "requirement_created": {
        "en": "Your requirement has been posted successfully.",
        "te": "మీ అవసరం విజయవంతంగా పోస్ట్ చేయబడింది.",
    },
    "requirement_cancelled": {
        "en": "Requirement has been cancelled.",
        "te": "అవసరం రద్దు చేయబడింది.",
    },
    "requirement_extended": {
        "en": "Requirement duration has been extended.",
        "te": "అవసరం వ్యవధి పొడిగించబడింది.",
    },
    "offer_accepted": {
        "en": "Offer accepted. Escrow payment will be initiated.",
        "te": "ఆఫర్ ఆమోదించబడింది. ఎస్క్రో చెల్లింపు ప్రారంభించబడుతుంది.",
    },
    "offer_rejected": {
        "en": "Offer has been rejected.",
        "te": "ఆఫర్ తిరస్కరించబడింది.",
    },
    "counter_offer_sent": {
        "en": "Counter offer sent successfully.",
        "te": "ప్రతి ఆఫర్ విజయవంతంగా పంపబడింది.",
    },
    "delivery_confirmed": {
        "en": "Delivery confirmed. Thank you!",
        "te": "డెలివరీ నిర్ధారించబడింది. ధన్యవాదాలు!",
    },
    "dispute_filed": {
        "en": "Dispute has been filed. Our team will review within 48 hours.",
        "te": "వివాదం దాఖలు చేయబడింది. మా బృందం 48 గంటల్లో సమీక్షిస్తుంది.",
    },
    "location_added": {
        "en": "Delivery location added successfully.",
        "te": "డెలివరీ స్థానం విజయవంతంగా జోడించబడింది.",
    },
    "location_deleted": {
        "en": "Delivery location deleted.",
        "te": "డెలివరీ స్థానం తొలగించబడింది.",
    },
    "user_invited": {
        "en": "User invitation sent successfully.",
        "te": "వినియోగదారు ఆహ్వానం విజయవంతంగా పంపబడింది.",
    },
    "user_removed": {
        "en": "User has been removed from the organization.",
        "te": "వినియోగదారు సంస్థ నుండి తొలగించబడ్డారు.",
    },
    "language_changed": {
        "en": "Language preference updated.",
        "te": "భాష ప్రాధాన్యత నవీకరించబడింది.",
    },
    "seller_rated": {
        "en": "Thank you for rating the seller.",
        "te": "విక్రేతను రేటింగ్ చేసినందుకు ధన్యవాదాలు.",
    },
}

ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "E101": {"en": "Buyer not found.", "te": "కొనుగోలుదారు కనుగొనబడలేదు."},
    "E102": {"en": "Buyer already exists.", "te": "కొనుగోలుదారు ఇప్పటికే ఉన్నారు."},
    "E103": {"en": "Invalid buyer type.", "te": "చెల్లని కొనుగోలుదారు రకం."},
    "E104": {"en": "Invalid language.", "te": "చెల్లని భాష."},
    "E105": {"en": "Crop not in Phase 1.", "te": "పంట ఫేజ్ 1లో లేదు."},
    "E106": {"en": "District not active.", "te": "జిల్లా చురుకుగా లేదు."},
    "E107": {"en": "Quantity too low.", "te": "పరిమాణం చాలా తక్కువ."},
    "E108": {"en": "Quantity too high.", "te": "పరిమాణం చాలా ఎక్కువ."},
    "E109": {"en": "Price below floor.", "te": "ధర కనిష్టం కంటే తక్కువ."},
    "E110": {"en": "Account suspended.", "te": "ఖాతా సస్పెండ్."},
    "E111": {"en": "KYC required.", "te": "KYC అవసరం."},
    "E112": {"en": "Invalid OTP.", "te": "చెల్లని OTP."},
    "E113": {"en": "OTP expired.", "te": "OTP గడువు ముగిసింది."},
    "E114": {"en": "Aadhaar verification failed.", "te": "ఆధార్ ధృవీకరణ విఫలమైంది."},
    "E115": {"en": "GSTIN verification failed.", "te": "GSTIN ధృవీకరణ విఫలమైంది."},
    "E116": {"en": "Bank verification failed.", "te": "బ్యాంక్ ధృవీకరణ విఫలమైంది."},
    "E117": {"en": "UPI verification failed.", "te": "UPI ధృవీకరణ విఫలమైంది."},
    "E118": {"en": "Invalid KYC transition.", "te": "చెల్లని KYC మార్పు."},
    "E119": {"en": "GSTIN required.", "te": "GSTIN అవసరం."},
    "E120": {"en": "Aadhaar required.", "te": "ఆధార్ అవసరం."},
    "E121": {"en": "Requirement not found.", "te": "అవసరం కనుగొనబడలేదు."},
    "E122": {"en": "Max RFQs reached.", "te": "గరిష్ట RFQలు చేరుకుంది."},
    "E123": {"en": "Invalid status transition.", "te": "చెల్లని స్థితి మార్పు."},
    "E124": {"en": "Not your requirement.", "te": "ఈ అవసరం మీది కాదు."},
    "E125": {"en": "Requirement expired.", "te": "అవసరం గడువు ముగిసింది."},
    "E126": {"en": "GST Invoice not available for individuals.", "te": "వ్యక్తులకు GST ఇన్‌వాయిస్ లేదు."},
    "E127": {"en": "Offer not found.", "te": "ఆఫర్ కనుగొనబడలేదు."},
    "E128": {"en": "Max negotiation rounds.", "te": "గరిష్ట చర్చల రౌండ్లు."},
    "E129": {"en": "Offer expired.", "te": "ఆఫర్ గడువు ముగిసింది."},
    "E130": {"en": "Offer already responded.", "te": "ఆఫర్‌కు ఇప్పటికే స్పందించబడింది."},
    "E131": {"en": "Location not found.", "te": "స్థానం కనుగొనబడలేదు."},
    "E132": {"en": "Max locations reached.", "te": "గరిష్ట స్థానాలు చేరుకుంది."},
    "E133": {"en": "Not your location.", "te": "ఈ స్థానం మీది కాదు."},
    "E134": {"en": "User not found.", "te": "వినియోగదారు కనుగొనబడలేదు."},
    "E135": {"en": "User already exists.", "te": "వినియోగదారు ఇప్పటికే ఉన్నారు."},
    "E136": {"en": "Insufficient permission.", "te": "అనుమతి లేదు."},
    "E137": {"en": "Org-only action.", "te": "సంస్థ మాత్రమే చర్య."},
    "E138": {"en": "Authentication required.", "te": "ప్రామాణీకరణ అవసరం."},
    "E139": {"en": "Order not found.", "te": "ఆర్డర్ కనుగొనబడలేదు."},
    "E140": {"en": "Dispute window expired.", "te": "వివాద విండో ముగిసింది."},
}


def get_message(key: str, language: str = "en") -> str:
    msgs = SUCCESS_MESSAGES.get(key) or ERROR_MESSAGES.get(key)
    if msgs is None:
        return key
    return msgs.get(language, msgs.get("en", key))
