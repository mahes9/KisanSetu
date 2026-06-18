"""Domain exceptions with bilingual messages (English + Telugu)."""

from __future__ import annotations


class KisanGPTException(Exception):
    """Base exception for all KisanGPT domain errors."""

    error_code: str = "E000"
    message_en: str = "An unexpected error occurred."
    message_te: str = "ఊహించని లోపం సంభవించింది."
    http_status: int = 500

    def __init__(
        self,
        message_en: str | None = None,
        message_te: str | None = None,
        *,
        error_code: str | None = None,
        http_status: int | None = None,
    ) -> None:
        if message_en is not None:
            self.message_en = message_en
        if message_te is not None:
            self.message_te = message_te
        if error_code is not None:
            self.error_code = error_code
        if http_status is not None:
            self.http_status = http_status
        super().__init__(self.message_en)


# ── Buyer validation (E101-E110) ──────────────────────────

class BuyerNotFoundError(KisanGPTException):
    error_code = "E101"
    message_en = "Buyer not found."
    message_te = "కొనుగోలుదారు కనుగొనబడలేదు."
    http_status = 404


class BuyerAlreadyExistsError(KisanGPTException):
    error_code = "E102"
    message_en = "A buyer with this phone number already exists."
    message_te = "ఈ ఫోన్ నంబర్‌తో కొనుగోలుదారు ఇప్పటికే ఉన్నారు."
    http_status = 409


class InvalidBuyerTypeError(KisanGPTException):
    error_code = "E103"
    message_en = "Invalid buyer type. Must be 'individual' or 'organization'."
    message_te = "చెల్లని కొనుగోలుదారు రకం."
    http_status = 400


class InvalidLanguageError(KisanGPTException):
    error_code = "E104"
    message_en = "Invalid language. Only 'en' (English) and 'te' (Telugu) are supported."
    message_te = "చెల్లని భాష. 'en' (ఇంగ్లీష్) మరియు 'te' (తెలుగు) మాత్రమే."
    http_status = 400


class CropNotInPhase1Error(KisanGPTException):
    error_code = "E105"
    message_en = "This crop is not available in Phase 1."
    message_te = "ఈ పంట ఫేజ్ 1లో అందుబాటులో లేదు."
    http_status = 400


class DistrictNotActiveError(KisanGPTException):
    error_code = "E106"
    message_en = "This district is not active in Phase 1."
    message_te = "ఈ జిల్లా ఫేజ్ 1లో చురుకుగా లేదు."
    http_status = 400


class QuantityTooLowError(KisanGPTException):
    error_code = "E107"
    message_en = "Quantity is below the minimum."
    message_te = "పరిమాణం కనీసం కంటే తక్కువగా ఉంది."
    http_status = 400


class QuantityTooHighError(KisanGPTException):
    error_code = "E108"
    message_en = "Quantity exceeds the maximum."
    message_te = "పరిమాణం గరిష్టాన్ని మించిపోయింది."
    http_status = 400


class PriceFloorViolationError(KisanGPTException):
    error_code = "E109"
    message_en = "Offer price is below the minimum allowed (70% of modal price)."
    message_te = "ఆఫర్ ధర కనీస అనుమతి (మోడల్ ధరలో 70%) కంటే తక్కువగా ఉంది."
    http_status = 400


class BuyerSuspendedError(KisanGPTException):
    error_code = "E110"
    message_en = "Your account is currently suspended."
    message_te = "మీ ఖాతా ప్రస్తుతం సస్పెండ్ చేయబడింది."
    http_status = 403


# ── KYC errors (E111-E120) ────────────────────────────────

class KYCNotVerifiedError(KisanGPTException):
    error_code = "E111"
    message_en = "KYC verification is required before this action."
    message_te = "ఈ చర్యకు ముందు KYC ధృవీకరణ అవసరం."
    http_status = 403


class InvalidOTPError(KisanGPTException):
    error_code = "E112"
    message_en = "Invalid OTP. Please try again."
    message_te = "చెల్లని OTP. దయచేసి మళ్ళీ ప్రయత్నించండి."
    http_status = 401


class OTPExpiredError(KisanGPTException):
    error_code = "E113"
    message_en = "OTP has expired. Please request a new one."
    message_te = "OTP గడువు ముగిసింది. దయచేసి కొత్తది అభ్యర్థించండి."
    http_status = 401


class AadhaarVerificationError(KisanGPTException):
    error_code = "E114"
    message_en = "Aadhaar verification failed."
    message_te = "ఆధార్ ధృవీకరణ విఫలమైంది."
    http_status = 400


class GSTINVerificationError(KisanGPTException):
    error_code = "E115"
    message_en = "GSTIN verification failed."
    message_te = "GSTIN ధృవీకరణ విఫలమైంది."
    http_status = 400


class BankVerificationError(KisanGPTException):
    error_code = "E116"
    message_en = "Bank account verification failed."
    message_te = "బ్యాంక్ ఖాతా ధృవీకరణ విఫలమైంది."
    http_status = 400


class UPIVerificationError(KisanGPTException):
    error_code = "E117"
    message_en = "UPI ID verification failed."
    message_te = "UPI ID ధృవీకరణ విఫలమైంది."
    http_status = 400


class InvalidKYCTransitionError(KisanGPTException):
    error_code = "E118"
    message_en = "This KYC status transition is not allowed."
    message_te = "ఈ KYC స్థితి మార్పు అనుమతించబడదు."
    http_status = 400


class GSTINRequiredError(KisanGPTException):
    error_code = "E119"
    message_en = "GSTIN is required for organization buyers."
    message_te = "సంస్థ కొనుగోలుదారులకు GSTIN అవసరం."
    http_status = 400


class AadhaarRequiredError(KisanGPTException):
    error_code = "E120"
    message_en = "Aadhaar verification is required for individual buyers."
    message_te = "వ్యక్తిగత కొనుగోలుదారులకు ఆధార్ ధృవీకరణ అవసరం."
    http_status = 400


# ── RFQ / Requirement errors (E121-E126) ──────────────────

class RequirementNotFoundError(KisanGPTException):
    error_code = "E121"
    message_en = "Requirement not found."
    message_te = "అవసరం కనుగొనబడలేదు."
    http_status = 404


class MaxRFQsReachedError(KisanGPTException):
    error_code = "E122"
    message_en = "Maximum number of active requirements reached."
    message_te = "గరిష్ట చురుకు అవసరాల సంఖ్యకు చేరుకుంది."
    http_status = 400


class InvalidStatusTransitionError(KisanGPTException):
    error_code = "E123"
    message_en = "This status transition is not allowed."
    message_te = "ఈ స్థితి మార్పు అనుమతించబడదు."
    http_status = 400


class RequirementNotOwnedError(KisanGPTException):
    error_code = "E124"
    message_en = "You do not own this requirement."
    message_te = "ఈ అవసరం మీది కాదు."
    http_status = 403


class RequirementExpiredError(KisanGPTException):
    error_code = "E125"
    message_en = "This requirement has expired."
    message_te = "ఈ అవసరం గడువు ముగిసింది."
    http_status = 400


class GSTInvoiceNotAvailableError(KisanGPTException):
    error_code = "E126"
    message_en = "GST Invoice is not available for individual buyers."
    message_te = "వ్యక్తిగత కొనుగోలుదారులకు GST ఇన్‌వాయిస్ అందుబాటులో లేదు."
    http_status = 400


# ── Offer / Negotiation errors (E127-E130) ────────────────

class OfferNotFoundError(KisanGPTException):
    error_code = "E127"
    message_en = "Offer not found."
    message_te = "ఆఫర్ కనుగొనబడలేదు."
    http_status = 404


class MaxNegotiationRoundsError(KisanGPTException):
    error_code = "E128"
    message_en = "Maximum negotiation rounds reached."
    message_te = "గరిష్ట చర్చల రౌండ్లు చేరుకుంది."
    http_status = 400


class OfferExpiredError(KisanGPTException):
    error_code = "E129"
    message_en = "This offer has expired."
    message_te = "ఈ ఆఫర్ గడువు ముగిసింది."
    http_status = 400


class OfferAlreadyRespondedError(KisanGPTException):
    error_code = "E130"
    message_en = "This offer has already been responded to."
    message_te = "ఈ ఆఫర్‌కు ఇప్పటికే స్పందించబడింది."
    http_status = 409


# ── Location errors (E131-E133) ───────────────────────────

class LocationNotFoundError(KisanGPTException):
    error_code = "E131"
    message_en = "Delivery location not found."
    message_te = "డెలివరీ స్థానం కనుగొనబడలేదు."
    http_status = 404


class MaxLocationsReachedError(KisanGPTException):
    error_code = "E132"
    message_en = "Maximum number of delivery locations reached."
    message_te = "గరిష్ట డెలివరీ స్థానాల సంఖ్యకు చేరుకుంది."
    http_status = 400


class LocationNotOwnedError(KisanGPTException):
    error_code = "E133"
    message_en = "You do not own this delivery location."
    message_te = "ఈ డెలివరీ స్థానం మీది కాదు."
    http_status = 403


# ── Org user errors (E134-E137) ───────────────────────────

class UserNotFoundError(KisanGPTException):
    error_code = "E134"
    message_en = "User not found."
    message_te = "వినియోగదారు కనుగొనబడలేదు."
    http_status = 404


class UserAlreadyExistsError(KisanGPTException):
    error_code = "E135"
    message_en = "User with this email already exists in this organization."
    message_te = "ఈ ఇమెయిల్‌తో వినియోగదారు ఈ సంస్థలో ఇప్పటికే ఉన్నారు."
    http_status = 409


class InsufficientPermissionError(KisanGPTException):
    error_code = "E136"
    message_en = "You do not have permission to perform this action."
    message_te = "ఈ చర్య చేయడానికి మీకు అనుమతి లేదు."
    http_status = 403


class IndividualBuyerOrgActionError(KisanGPTException):
    error_code = "E137"
    message_en = "This action is only available for organization buyers."
    message_te = "ఈ చర్య సంస్థ కొనుగోలుదారులకు మాత్రమే అందుబాటులో ఉంది."
    http_status = 403


# ── Auth errors (E138-E140) ───────────────────────────────

class UnauthorizedError(KisanGPTException):
    error_code = "E138"
    message_en = "Authentication required."
    message_te = "ప్రామాణీకరణ అవసరం."
    http_status = 401


class OrderNotFoundError(KisanGPTException):
    error_code = "E139"
    message_en = "Order not found."
    message_te = "ఆర్డర్ కనుగొనబడలేదు."
    http_status = 404


class DisputeWindowExpiredError(KisanGPTException):
    error_code = "E140"
    message_en = "Dispute window has expired (72 hours)."
    message_te = "వివాద విండో గడువు ముగిసింది (72 గంటలు)."
    http_status = 400
