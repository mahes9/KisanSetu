"""Draft completeness scoring — pure logic, no DB."""

from __future__ import annotations


class CompletenessService:

    STEP1_REQUIRED = ["crop", "quantity_kg", "harvest_status"]
    STEP2_REQUIRED = ["photo_urls", "grade"]
    STEP3_REQUIRED = ["ask_price_per_q"]
    STEP4_REQUIRED = ["transport_type"]
    STEP5_REQUIRED = ["consent_quality", "consent_price", "consent_terms"]

    STEP_WEIGHTS = {
        "step1": 25,
        "step2": 25,
        "step3": 20,
        "step4": 15,
        "step5": 15,
    }

    STEP_FIELDS = {
        "step1": STEP1_REQUIRED,
        "step2": STEP2_REQUIRED,
        "step3": STEP3_REQUIRED,
        "step4": STEP4_REQUIRED,
        "step5": STEP5_REQUIRED,
    }

    @classmethod
    def calculate_score(cls, draft_data: dict) -> int:
        score = 0
        for step_key, weight in cls.STEP_WEIGHTS.items():
            data_key = f"{step_key}_data"
            step_data = draft_data.get(data_key)
            if not step_data or not isinstance(step_data, dict):
                continue

            required = cls.STEP_FIELDS[step_key]
            filled = 0
            for field in required:
                val = step_data.get(field)
                if val is None:
                    continue
                if isinstance(val, bool):
                    if val:
                        filled += 1
                elif isinstance(val, list):
                    if step_key == "step2" and field == "photo_urls" and len(val) >= 3:
                        filled += 1
                    elif step_key != "step2" and len(val) > 0:
                        filled += 1
                elif isinstance(val, str) and val:
                    filled += 1
                elif isinstance(val, (int, float)) and val > 0:
                    filled += 1

            if required:
                step_pct = filled / len(required)
                score += int(weight * step_pct)

        return min(score, 100)

    @classmethod
    def get_missing_required(cls, draft_data: dict) -> list[str]:
        missing: list[str] = []
        for step_key, required_fields in cls.STEP_FIELDS.items():
            data_key = f"{step_key}_data"
            step_data = draft_data.get(data_key) or {}
            for field in required_fields:
                val = step_data.get(field)
                if val is None:
                    missing.append(f"{step_key}.{field}")
                elif isinstance(val, bool) and not val:
                    missing.append(f"{step_key}.{field}")
                elif isinstance(val, list) and len(val) < (3 if field == "photo_urls" else 1):
                    missing.append(f"{step_key}.{field}")
                elif isinstance(val, str) and not val:
                    missing.append(f"{step_key}.{field}")
        return missing

    @classmethod
    def get_step_completion(cls, draft_data: dict) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for step_key, required_fields in cls.STEP_FIELDS.items():
            data_key = f"{step_key}_data"
            step_data = draft_data.get(data_key) or {}
            complete = True
            for field in required_fields:
                val = step_data.get(field)
                if val is None:
                    complete = False
                    break
                if isinstance(val, bool) and not val:
                    complete = False
                    break
                if isinstance(val, list) and field == "photo_urls" and len(val) < 3:
                    complete = False
                    break
                if isinstance(val, str) and not val:
                    complete = False
                    break
            result[step_key] = complete
        return result

    @classmethod
    def get_completion_message(cls, score: int) -> dict[str, str]:
        if score == 0:
            return {"en": "Just started", "te": "ఇప్పుడే ప్రారంభించారు"}
        if score <= 25:
            return {"en": "Just started", "te": "ఇప్పుడే ప్రారంభించారు"}
        if score <= 50:
            return {"en": "Making progress", "te": "పురోగతి సాధిస్తున్నారు"}
        if score <= 75:
            return {"en": "Almost there", "te": "దాదాపు పూర్తయింది"}
        if score < 100:
            return {"en": "Nearly complete", "te": "దాదాపు పూర్తి"}
        return {"en": "Ready to publish", "te": "ప్రచురించడానికి సిద్ధంగా ఉంది"}
