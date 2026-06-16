"""Integration tests for the Listing Publish flow — mocked repos and clients."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.core.exceptions import (
    AlreadyPublishedError,
    FloorPriceViolationError,
    InvalidStatusTransitionError,
    KYCNotVerifiedError,
    MaxListingsReachedError,
    MaxPriceEditsError,
)
from app.services.listing_service import ListingService


def _mock_listing(seller_id=None, status="active", price_edit_count=0, **overrides):
    listing = MagicMock()
    listing.id = uuid4()
    listing.seller_id = seller_id or uuid4()
    listing.listing_number = "KGP-20260601-1234"
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
    listing.price_edit_count = price_edit_count
    listing.price_edit_history = []
    listing.expires_at = datetime.now(timezone.utc) + timedelta(days=5)
    listing.views_count = 0
    listing.enquiries_count = 0
    listing.created_at = datetime.now(timezone.utc)
    listing.paused_at = None
    listing.cancelled_at = None
    listing.matched_at = None
    listing.sold_at = None
    for k, v in overrides.items():
        setattr(listing, k, v)
    return listing


def _mock_draft(seller_id=None, status="complete"):
    draft = MagicMock()
    draft.id = uuid4()
    draft.seller_id = seller_id or uuid4()
    draft.draft_status = status
    draft.step1_data = {"crop": "tomato", "quantity_kg": 800}
    draft.step2_data = {"grade": "A", "ai_confidence": 85, "photo_urls": ["a", "b", "c"]}
    draft.step3_data = {"ask_price_per_q": 1200}
    draft.step4_data = {"transport_type": "seller_delivers"}
    draft.step5_data = {"consent_quality": True, "consent_price": True, "consent_terms": True}
    draft.completeness_score = 100
    return draft


def _mock_seller(seller_id=None, kyc="verified", cancellation_count=0):
    seller = MagicMock()
    seller.id = seller_id or uuid4()
    seller.kyc_status = kyc
    seller.bank_verified = True
    seller.suspension_until = None
    seller.cancellation_count = cancellation_count
    return seller


@pytest.fixture
def mock_session():
    return AsyncMock()


class TestPublishFromDraft:
    @pytest.mark.asyncio
    async def test_happy_path(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id)
        listing = _mock_listing(seller_id=seller_id)

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

            result = await svc.publish_from_draft(
                draft.id, seller_id, {"ask_price_per_q": 1200}
            )

            assert result["listing_number"] == listing.listing_number
            assert result["ai_grade_locked"] is True
            svc.draft_repo.mark_published.assert_called_once()
            svc.event_bus.emit_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_floor_price_blocks_publish(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.draft_repo = AsyncMock()
            svc.seller_repo = AsyncMock()
            svc.listing_repo = AsyncMock()
            svc.photo_repo = AsyncMock()
            svc.price_client = AsyncMock()

            svc.draft_repo.get_draft_for_update.return_value = draft
            svc.seller_repo.get_for_update.return_value = seller
            svc.listing_repo.count_active_listings.return_value = 0
            svc.price_client.get_floor_price.return_value = {"floor_price": 1054.0, "modal_price": 1240.0}

            with pytest.raises(FloorPriceViolationError):
                await svc.publish_from_draft(draft.id, seller_id, {"ask_price_per_q": 900})

    @pytest.mark.asyncio
    async def test_missing_kyc_blocks_publish(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id, kyc="pending")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.draft_repo = AsyncMock()
            svc.seller_repo = AsyncMock()

            svc.draft_repo.get_draft_for_update.return_value = draft
            svc.seller_repo.get_for_update.return_value = seller

            with pytest.raises(KYCNotVerifiedError):
                await svc.publish_from_draft(draft.id, seller_id, {"ask_price_per_q": 1200})

    @pytest.mark.asyncio
    async def test_max_listings_blocks_publish(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.draft_repo = AsyncMock()
            svc.seller_repo = AsyncMock()
            svc.listing_repo = AsyncMock()

            svc.draft_repo.get_draft_for_update.return_value = draft
            svc.seller_repo.get_for_update.return_value = seller
            svc.listing_repo.count_active_listings.return_value = 5

            with pytest.raises(MaxListingsReachedError):
                await svc.publish_from_draft(draft.id, seller_id, {"ask_price_per_q": 1200})

    @pytest.mark.asyncio
    async def test_already_published_raises(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id, status="published")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.draft_repo = AsyncMock()
            svc.draft_repo.get_draft_for_update.return_value = draft

            with pytest.raises(AlreadyPublishedError):
                await svc.publish_from_draft(draft.id, seller_id, {"ask_price_per_q": 1200})


class TestEditPrice:
    @pytest.mark.asyncio
    async def test_within_limit_succeeds(self, mock_session):
        seller_id = uuid4()
        listing = _mock_listing(seller_id=seller_id, price_edit_count=2)
        updated = _mock_listing(seller_id=seller_id, price_edit_count=3)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.price_client = AsyncMock()
            svc.event_bus = AsyncMock()

            svc.listing_repo.get_listing_by_id.return_value = listing
            svc.price_client.get_floor_price.return_value = {"floor_price": 1054.0, "modal_price": 1240.0}
            svc.listing_repo.update_listing_price.return_value = updated

            result = await svc.edit_price(listing.id, seller_id, 1150.0)
            assert result is not None

    @pytest.mark.asyncio
    async def test_max_edits_enforced(self, mock_session):
        seller_id = uuid4()
        listing = _mock_listing(seller_id=seller_id, price_edit_count=3)

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.listing_repo.get_listing_by_id.return_value = listing

            with pytest.raises(MaxPriceEditsError):
                await svc.edit_price(listing.id, seller_id, 1150.0)


class TestCancelListing:
    @pytest.mark.asyncio
    async def test_cancel_increments_count(self, mock_session):
        seller_id = uuid4()
        listing = _mock_listing(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id, cancellation_count=0)
        cancelled = _mock_listing(seller_id=seller_id, status="cancelled")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.seller_repo = AsyncMock()
            svc.event_bus = AsyncMock()

            svc.listing_repo.get_listing_by_id.return_value = listing
            svc.listing_repo.update_listing_status.return_value = cancelled
            svc.seller_repo.get_for_update.return_value = seller

            await svc.cancel_listing(listing.id, seller_id, "Changed mind")
            svc.seller_repo.update_cancellation_count.assert_called_once_with(seller_id, 1)

    @pytest.mark.asyncio
    async def test_3_cancellations_suspends(self, mock_session):
        seller_id = uuid4()
        listing = _mock_listing(seller_id=seller_id)
        seller = _mock_seller(seller_id=seller_id, cancellation_count=2)
        cancelled = _mock_listing(seller_id=seller_id, status="cancelled")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.seller_repo = AsyncMock()
            svc.event_bus = AsyncMock()

            svc.listing_repo.get_listing_by_id.return_value = listing
            svc.listing_repo.update_listing_status.return_value = cancelled
            svc.seller_repo.get_for_update.return_value = seller

            await svc.cancel_listing(listing.id, seller_id, "Too many")
            svc.seller_repo.suspend_seller.assert_called_once()


class TestPauseResume:
    @pytest.mark.asyncio
    async def test_pause_and_resume(self, mock_session):
        seller_id = uuid4()
        active = _mock_listing(seller_id=seller_id, status="active")
        paused = _mock_listing(seller_id=seller_id, status="paused")
        resumed = _mock_listing(seller_id=seller_id, status="active")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()

            svc.listing_repo.get_listing_by_id.return_value = active
            svc.listing_repo.update_listing_status.return_value = paused
            result = await svc.pause_listing(active.id, seller_id)
            assert result["status"] == "paused"

            svc.listing_repo.get_listing_by_id.return_value = paused
            svc.listing_repo.update_listing_status.return_value = resumed
            result = await svc.resume_listing(active.id, seller_id)
            assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_expired_cannot_resume(self, mock_session):
        seller_id = uuid4()
        expired = _mock_listing(seller_id=seller_id, status="expired")

        with patch.object(ListingService, "__init__", lambda self, s: None):
            svc = ListingService(mock_session)
            svc.listing_repo = AsyncMock()
            svc.listing_repo.get_listing_by_id.return_value = expired

            with pytest.raises(InvalidStatusTransitionError):
                await svc.resume_listing(expired.id, seller_id)
