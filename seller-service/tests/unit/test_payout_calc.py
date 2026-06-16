"""Unit tests for payout calculation logic."""

import pytest
from app.core.validators import calculate_payout_preview


class TestPayoutCalculation:
    def test_500kg_tier1_3_percent(self):
        result = calculate_payout_preview(500, 1000, 1100)
        assert result["gross_amount"] == 5000.0
        assert result["commission_percent"] == 0.03
        assert result["commission_amount"] == 150.0
        assert result["seller_payout"] == 4850.0

    def test_800kg_tier2_5_percent(self):
        result = calculate_payout_preview(800, 1200, 1240)
        assert result["gross_amount"] == 9600.0
        assert result["commission_percent"] == 0.05
        assert result["commission_amount"] == 480.0
        assert result["seller_payout"] == 9120.0

    def test_2000kg_tier2_boundary(self):
        result = calculate_payout_preview(2000, 1500, 1600)
        assert result["gross_amount"] == 30000.0
        assert result["commission_percent"] == 0.05
        assert result["commission_amount"] == 1500.0
        assert result["seller_payout"] == 28500.0

    def test_5000kg_tier3_8_percent(self):
        result = calculate_payout_preview(5000, 800, 900)
        assert result["gross_amount"] == 40000.0
        assert result["commission_percent"] == 0.08
        assert result["commission_amount"] == 3200.0
        assert result["seller_payout"] == 36800.0

    def test_100kg_min_tier1(self):
        result = calculate_payout_preview(100, 1000, 1100)
        assert result["commission_percent"] == 0.03

    def test_returns_all_keys(self):
        result = calculate_payout_preview(500, 1000, 1100)
        expected_keys = {"gross_amount", "commission_percent", "commission_amount", "seller_payout", "effective_price_per_kg"}
        assert set(result.keys()) == expected_keys

    def test_effective_price_per_kg(self):
        result = calculate_payout_preview(500, 1000, 1100)
        assert result["effective_price_per_kg"] == round(4850.0 / 500, 2)

    def test_2001kg_tier3(self):
        result = calculate_payout_preview(2001, 1000, 1100)
        assert result["commission_percent"] == 0.08
