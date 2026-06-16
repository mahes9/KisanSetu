"""Unit tests for CompletenessService — pure logic, no DB."""

import pytest
from app.services.completeness_service import CompletenessService


class TestCalculateScore:
    def test_empty_draft_zero_score(self):
        assert CompletenessService.calculate_score({}) == 0

    def test_step1_only_25(self):
        data = {
            "step1_data": {
                "crop": "tomato",
                "quantity_kg": 800,
                "harvest_status": "harvested_today",
            }
        }
        assert CompletenessService.calculate_score(data) == 25

    def test_step1_partial(self):
        data = {"step1_data": {"crop": "tomato"}}
        score = CompletenessService.calculate_score(data)
        assert 0 < score < 25

    def test_step1_and_step2_50(self):
        data = {
            "step1_data": {"crop": "tomato", "quantity_kg": 800, "harvest_status": "harvested_today"},
            "step2_data": {"photo_urls": ["a.jpg", "b.jpg", "c.jpg"], "grade": "A"},
        }
        assert CompletenessService.calculate_score(data) == 50

    def test_full_draft_100(self, complete_draft_data):
        assert CompletenessService.calculate_score(complete_draft_data) == 100

    def test_missing_photos_reduces_step2(self):
        data = {
            "step1_data": {"crop": "tomato", "quantity_kg": 800, "harvest_status": "harvested_today"},
            "step2_data": {"photo_urls": ["a.jpg"], "grade": "A"},
        }
        score = CompletenessService.calculate_score(data)
        assert score < 50

    def test_none_step_data_ignored(self):
        data = {"step1_data": None, "step2_data": None}
        assert CompletenessService.calculate_score(data) == 0


class TestGetMissingRequired:
    def test_empty_draft_all_missing(self):
        missing = CompletenessService.get_missing_required({})
        assert len(missing) > 0
        assert "step1.crop" in missing
        assert "step2.photo_urls" in missing
        assert "step5.consent_quality" in missing

    def test_complete_draft_none_missing(self, complete_draft_data):
        missing = CompletenessService.get_missing_required(complete_draft_data)
        assert len(missing) == 0

    def test_partial_returns_only_missing(self, partial_draft_data):
        missing = CompletenessService.get_missing_required(partial_draft_data)
        assert "step1.crop" not in missing
        assert "step2.photo_urls" in missing
        assert "step3.ask_price_per_q" in missing


class TestGetStepCompletion:
    def test_all_false_for_empty(self):
        result = CompletenessService.get_step_completion({})
        assert all(v is False for v in result.values())

    def test_step1_true_when_complete(self):
        data = {"step1_data": {"crop": "tomato", "quantity_kg": 800, "harvest_status": "ok"}}
        result = CompletenessService.get_step_completion(data)
        assert result["step1"] is True
        assert result["step2"] is False

    def test_mixed_completion(self, complete_draft_data):
        result = CompletenessService.get_step_completion(complete_draft_data)
        assert all(v is True for v in result.values())


class TestGetCompletionMessage:
    def test_zero_just_started(self):
        msg = CompletenessService.get_completion_message(0)
        assert msg["en"] == "Just started"

    def test_30_making_progress(self):
        msg = CompletenessService.get_completion_message(30)
        assert msg["en"] == "Making progress"

    def test_60_almost_there(self):
        msg = CompletenessService.get_completion_message(60)
        assert msg["en"] == "Almost there"

    def test_90_nearly_complete(self):
        msg = CompletenessService.get_completion_message(90)
        assert msg["en"] == "Nearly complete"

    def test_100_ready_to_publish(self):
        msg = CompletenessService.get_completion_message(100)
        assert msg["en"] == "Ready to publish"

    def test_all_messages_have_telugu(self):
        for score in [0, 25, 50, 75, 100]:
            msg = CompletenessService.get_completion_message(score)
            assert "te" in msg
            assert len(msg["te"]) > 0
