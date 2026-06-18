"""Unit tests for buyer constants."""

from app.core.constants import (
    IndividualBuyerConfig,
    OrganizationBuyerConfig,
    RFQConfig,
    OfferConfig,
)


class TestIndividualBuyerConfig:
    def test_min_order(self):
        assert IndividualBuyerConfig.MIN_ORDER_KG == 100

    def test_max_order(self):
        assert IndividualBuyerConfig.MAX_ORDER_KG == 5000

    def test_max_rfqs(self):
        assert IndividualBuyerConfig.MAX_ACTIVE_RFQS == 3

    def test_max_locations(self):
        assert IndividualBuyerConfig.MAX_DELIVERY_LOCATIONS == 1

    def test_commission(self):
        assert IndividualBuyerConfig.COMMISSION_PERCENT == 0.05


class TestOrganizationBuyerConfig:
    def test_min_order(self):
        assert OrganizationBuyerConfig.MIN_ORDER_KG == 500

    def test_max_order(self):
        assert OrganizationBuyerConfig.MAX_ORDER_KG == 50000

    def test_tier1_rfqs(self):
        assert OrganizationBuyerConfig.TIER1_MAX_RFQS == 20

    def test_tier2_rfqs(self):
        assert OrganizationBuyerConfig.TIER2_MAX_RFQS == 10

    def test_tier3_rfqs(self):
        assert OrganizationBuyerConfig.TIER3_MAX_RFQS == 5


class TestRFQConfig:
    def test_price_floor_percent(self):
        assert RFQConfig.PRICE_FLOOR_PERCENT == 0.70

    def test_max_negotiation_rounds(self):
        assert RFQConfig.MAX_NEGOTIATION_ROUNDS == 3

    def test_offer_response_hours(self):
        assert RFQConfig.OFFER_RESPONSE_HOURS == 4


class TestOfferConfig:
    def test_max_counter_offers(self):
        assert OfferConfig.MAX_COUNTER_OFFERS == 3

    def test_response_window_hours(self):
        assert OfferConfig.RESPONSE_WINDOW_HOURS == 4
