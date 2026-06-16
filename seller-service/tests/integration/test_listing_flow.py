"""End-to-end style integration tests for the full listing lifecycle."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from app.services.listing_service import ListingService


def _build_listing(seller_id, status="active", **overrides):
    listing = MagicMock()
    listing.id = uuid4()
    listing.seller_id = seller_id
    listing.listing_number = f"KGP-20260601-{1000 + hash(listing.id) % 9000}"
    listing.crop = "tomato"
    listing.quantity_kg = 800.0
    listing.harvest_status = "harvested_today"
    listing.grade = "A"
    listing.ai_grade_locked = True
    listing.ai_confidence = 85
    listing.ai_provider = "claude"
    listing.ask_price_per_q = 1200.0
    listing.floor_price_at_publish = 1054.0
    listing.modal_price_at_publish = 1240.0
    listing.transport_type = "seller_delivers"
    listing.pickup_window = "morning_6_10"
    listing.status = status
    listing.price_edit_count = 0
    listing.price_edit_history = []
    listing.expires_at = datetime.now(timezone.utc) + timedelta(days=5)
    listing.views_count = 10
    listing.enquiries_count = 2
    listing.created_at = datetime.now(timezone.utc)
    listing.paused_at = None
    listing.cancelled_at = None
    listing.matched_at = None
    listing.sold_at = None
    for k, v in overrides.items():
        setattr(listing, k, v)
    return listing


@pytest.fixture
def mock_session():
    return AsyncMock()


class TestPublicListingNoPII:
    @pytest.mark.asyncio
    async def test_no_seller_id_in_public_view(self, mock_session):
        seller_id = uuid4()
        listing = _build_listing(seller_id)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.listing_repo.get_listing_by_id.return_value = listing

            result = await svc.get_public_listing(listing.id)

            assert "seller_id" not in result
            assert "listing_number" in result
            assert "crop" in result
            assert "grade" in result
            assert "ask_price_per_q" in result


class TestListingPagination:
    @pytest.mark.asyncio
    async def test_pagination(self, mock_session):
        seller_id = uuid4()
        listings = [_build_listing(seller_id) for _ in range(5)]

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.listing_repo.get_listings_paginated.return_value = (listings[:2], 5)

            result = await svc.list_my_listings(seller_id, page=1, per_page=2)
            assert len(result["listings"]) == 2
            assert result["total"] == 5
            assert result["page"] == 1
            assert result["per_page"] == 2


class TestListingStatusFilter:
    @pytest.mark.asyncio
    async def test_filter_by_active(self, mock_session):
        seller_id = uuid4()
        active_listings = [_build_listing(seller_id, status="active") for _ in range(3)]

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.listing_repo.get_listings_paginated.return_value = (active_listings, 3)

            result = await svc.list_my_listings(seller_id, page=1, per_page=20, status_filter="active")
            assert all(l["status"] == "active" for l in result["listings"])
            svc.listing_repo.get_listings_paginated.assert_called_once_with(
                seller_id, 1, 20, "active"
            )


class TestEventEmission:
    @pytest.mark.asyncio
    async def test_publish_emits_event(self, mock_session):
        seller_id = uuid4()
        draft = MagicMock()
        draft.id = uuid4()
        draft.seller_id = seller_id
        draft.draft_status = "complete"
        draft.step1_data = {"crop": "tomato", "quantity_kg": 800}
        draft.step2_data = {"grade": "A", "ai_confidence": 85}
        draft.step4_data = {"transport_type": "seller_delivers"}

        seller = MagicMock()
        seller.id = seller_id
        seller.kyc_status = "verified"
        seller.suspension_until = None

        listing = _build_listing(seller_id)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.session = mock_session
            svc.draft_repo = AsyncMock()
            svc.seller_repo = AsyncMock()
            svc.listing_repo = AsyncMock()
            svc.photo_repo = AsyncMock()
            svc.price_client = AsyncMock()
            svc.event_bus = AsyncMock()
            svc.notification = AsyncMock()

            svc.draft_repo.get_draft_for_update.return_value = draft
            svc.seller_repo.get_for_update.return_value = seller
            svc.listing_repo.count_active_listings.return_value = 0
            svc.price_client.get_floor_price.return_value = {"floor_price": 1054.0, "modal_price": 1240.0}
            svc.listing_repo.create_from_draft.return_value = listing

            await svc.publish_from_draft(draft.id, seller_id, {"ask_price_per_q": 1200})

            svc.event_bus.emit_event.assert_called_once()
            event_call = svc.event_bus.emit_event.call_args
            assert event_call[0][0] == "listing.published"
