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


# ── Listing validation (E001-E010) ──────────────────────


class FloorPriceViolationError(KisanGPTException):
    error_code = "E001"
    message_en = "Ask price is below the floor price."
    message_te = "అడిగిన ధర కనిష్ట ధర కంటే తక్కువగా ఉంది."
    http_status = 400


class CropNotInPhase1Error(KisanGPTException):
    error_code = "E002"
    message_en = "This crop is not available in Phase 1."
    message_te = "ఈ పంట ఫేజ్ 1లో అందుబాటులో లేదు."
    http_status = 400


class DistrictNotActiveError(KisanGPTException):
    error_code = "E003"
    message_en = "This district is not active in Phase 1."
    message_te = "ఈ జిల్లా ఫేజ్ 1లో చురుకుగా లేదు."
    http_status = 400


class QuantityTooLowError(KisanGPTException):
    error_code = "E004"
    message_en = "Quantity is below the minimum of 100 kg."
    message_te = "పరిమాణం కనీసం 100 కేజీల కంటే తక్కువగా ఉంది."
    http_status = 400


class QuantityTooHighError(KisanGPTException):
    error_code = "E005"
    message_en = "Quantity exceeds the maximum of 25,000 kg."
    message_te = "పరిమాణం గరిష్టంగా 25,000 కేజీలను మించిపోయింది."
    http_status = 400


class KYCNotVerifiedError(KisanGPTException):
    error_code = "E006"
    message_en = "KYC verification is required before this action."
    message_te = "ఈ చర్యకు ముందు KYC ధృవీకరణ అవసరం."
    http_status = 403


class PhotosRequiredError(KisanGPTException):
    error_code = "E007"
    message_en = "At least 3 photos are required to publish a listing."
    message_te = "లిస్టింగ్ ప్రచురించడానికి కనీసం 3 ఫోటోలు అవసరం."
    http_status = 400


class GradeNotSetError(KisanGPTException):
    error_code = "E008"
    message_en = "Quality grade must be set before publishing."
    message_te = "ప్రచురించడానికి ముందు నాణ్యత గ్రేడ్ సెట్ చేయాలి."
    http_status = 400


class ConsentRequiredError(KisanGPTException):
    error_code = "E009"
    message_en = "Consent for quality grading and pricing is required."
    message_te = "నాణ్యత గ్రేడింగ్ మరియు ధరల కోసం అంగీకారం అవసరం."
    http_status = 400


class InvalidStatusTransitionError(KisanGPTException):
    error_code = "E010"
    message_en = "This status transition is not allowed."
    message_te = "ఈ స్థితి మార్పు అనుమతించబడదు."
    http_status = 400


# ── Lookup / limit errors (E011-E016) ───────────────────


class ListingNotFoundError(KisanGPTException):
    error_code = "E011"
    message_en = "Listing not found."
    message_te = "లిస్టింగ్ కనుగొనబడలేదు."
    http_status = 404


class MaxListingsReachedError(KisanGPTException):
    error_code = "E012"
    message_en = "Maximum number of active listings reached."
    message_te = "గరిష్ట చురుకు లిస్టింగ్‌ల సంఖ్యకు చేరుకుంది."
    http_status = 400


class DraftNotFoundError(KisanGPTException):
    error_code = "E013"
    message_en = "Draft not found."
    message_te = "డ్రాఫ్ట్ కనుగొనబడలేదు."
    http_status = 404


class MaxDraftsReachedError(KisanGPTException):
    error_code = "E014"
    message_en = "Maximum number of drafts reached."
    message_te = "గరిష్ట డ్రాఫ్ట్‌ల సంఖ్యకు చేరుకుంది."
    http_status = 400


class AlreadyPublishedError(KisanGPTException):
    error_code = "E015"
    message_en = "This draft has already been published."
    message_te = "ఈ డ్రాఫ్ట్ ఇప్పటికే ప్రచురించబడింది."
    http_status = 409


class SellerNotFoundError(KisanGPTException):
    error_code = "E016"
    message_en = "Seller not found."
    message_te = "విక్రేత కనుగొనబడలేదు."
    http_status = 404


# ── Auth / verification errors (E017-E020) ──────────────


class InvalidOTPError(KisanGPTException):
    error_code = "E017"
    message_en = "Invalid OTP. Please try again."
    message_te = "చెల్లని OTP. దయచేసి మళ్ళీ ప్రయత్నించండి."
    http_status = 401


class OTPExpiredError(KisanGPTException):
    error_code = "E018"
    message_en = "OTP has expired. Please request a new one."
    message_te = "OTP గడువు ముగిసింది. దయచేసి కొత్తది అభ్యర్థించండి."
    http_status = 401


class AadhaarVerificationError(KisanGPTException):
    error_code = "E019"
    message_en = "Aadhaar verification failed."
    message_te = "ఆధార్ ధృవీకరణ విఫలమైంది."
    http_status = 400


class BankVerificationError(KisanGPTException):
    error_code = "E020"
    message_en = "Bank account verification failed."
    message_te = "బ్యాంక్ ఖాతా ధృవీకరణ విఫలమైంది."
    http_status = 400


# ── Operational errors (E021-E026) ──────────────────────


class PhotoUploadError(KisanGPTException):
    error_code = "E021"
    message_en = "Photo upload failed. Please try again."
    message_te = "ఫోటో అప్‌లోడ్ విఫలమైంది. దయచేసి మళ్ళీ ప్రయత్నించండి."
    http_status = 500


class AIGradingError(KisanGPTException):
    error_code = "E022"
    message_en = "AI grading failed. Manual grading will be used."
    message_te = "AI గ్రేడింగ్ విఫలమైంది. మాన్యువల్ గ్రేడింగ్ ఉపయోగించబడుతుంది."
    http_status = 500


class PriceStaleError(KisanGPTException):
    error_code = "E023"
    message_en = "Market price data is stale. Please refresh."
    message_te = "మార్కెట్ ధర డేటా పాతది. దయచేసి రిఫ్రెష్ చేయండి."
    http_status = 400


class DuplicatePhotoError(KisanGPTException):
    error_code = "E024"
    message_en = "This photo has already been uploaded."
    message_te = "ఈ ఫోటో ఇప్పటికే అప్‌లోడ్ చేయబడింది."
    http_status = 400


class SellerSuspendedError(KisanGPTException):
    error_code = "E025"
    message_en = "Your account is currently suspended."
    message_te = "మీ ఖాతా ప్రస్తుతం సస్పెండ్ చేయబడింది."
    http_status = 403


class MaxPriceEditsError(KisanGPTException):
    error_code = "E026"
    message_en = "Maximum number of price edits reached."
    message_te = "గరిష్ట ధర సవరణల సంఖ్యకు చేరుకుంది."
    http_status = 400


# ── Auth / ownership (E027-E030) ────────────────────────


class UnauthorizedError(KisanGPTException):
    error_code = "E027"
    message_en = "Authentication required."
    message_te = "ప్రామాణీకరణ అవసరం."
    http_status = 401


class FarmNotFoundError(KisanGPTException):
    error_code = "E028"
    message_en = "Farm not found."
    message_te = "వ్యవసాయ క్షేత్రం కనుగొనబడలేదు."
    http_status = 404


class InvalidCropError(KisanGPTException):
    error_code = "E029"
    message_en = "Invalid crop type."
    message_te = "చెల్లని పంట రకం."
    http_status = 400


class DraftNotOwnedError(KisanGPTException):
    error_code = "E030"
    message_en = "You do not own this draft."
    message_te = "ఈ డ్రాఫ్ట్ మీది కాదు."
    http_status = 403
