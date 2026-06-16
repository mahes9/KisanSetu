"""Integration tests for the Draft module — mocked DB via patching."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.core.exceptions import (
    AlreadyPublishedError,
    CropNotInPhase1Error,
    DraftNotFoundError,
    DraftNotOwnedError,
    MaxDraftsReachedError,
)
from app.services.draft_service import DraftService


def _mock_draft(
    seller_id=None, status="in_progress", step1=None, step2=None,
    step3=None, step4=None, step5=None, completeness=0, current_step=1,
):
    draft = MagicMock()
    draft.id = uuid4()
    draft.seller_id = seller_id or uuid4()
    draft.draft_status = status
    draft.current_step = current_step
    draft.completeness_score = completeness
    draft.step1_data = step1
    draft.step2_data = step2
    draft.step3_data = step3
    draft.step4_data = step4
    draft.step5_data = step5
    draft.step1_completed = False
    draft.step2_completed = False
    draft.step3_completed = False
    draft.step4_completed = False
    draft.step5_completed = False
    draft.last_active_at = datetime.now(timezone.utc)
    draft.created_at = datetime.now(timezone.utc)
    draft.updated_at = datetime.now(timezone.utc)
    draft.published_listing_id = None
    return draft


@pytest.fixture
def mock_session():
    return AsyncMock()


class TestCreateDraft:
    @pytest.mark.asyncio
    async def test_success(self, mock_session):
        seller_id = uuid4()
        step1 = {"crop": "tomato", "quantity_kg": 800, "harvest_status": "harvested_today"}
        draft = _mock_draft(seller_id=seller_id, step1=step1)

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.completeness = MagicMock()
            svc.price_client = AsyncMock()
            svc.repo.count_drafts_by_seller.return_value = 0
            svc.repo.create_draft.return_value = draft
            svc.repo.update_draft.return_value = draft
            svc.repo.get_draft_by_id.return_value = draft
            svc.completeness.calculate_score.return_value = 25
            svc.completeness.get_step_completion.return_value = {"step1": True}
            svc.completeness.get_missing_required.return_value = ["step2.photo_urls"]

            result = await svc.create_draft(seller_id, step1)
            assert result["step1_data"] == step1
            svc.repo.create_draft.assert_called_once()

    @pytest.mark.asyncio
    async def test_max_drafts_reached(self, mock_session):
        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.count_drafts_by_seller.return_value = 3

            with pytest.raises(MaxDraftsReachedError):
                await svc.create_draft(uuid4(), {"crop": "tomato", "quantity_kg": 500})

    @pytest.mark.asyncio
    async def test_invalid_crop(self, mock_session):
        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.count_drafts_by_seller.return_value = 0

            with pytest.raises(CropNotInPhase1Error):
                await svc.create_draft(uuid4(), {"crop": "cotton", "quantity_kg": 500})


class TestSaveStep:
    @pytest.mark.asyncio
    async def test_increments_completeness(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id, step1={"crop": "tomato", "quantity_kg": 800})
        updated_draft = _mock_draft(seller_id=seller_id, step1={"crop": "tomato", "quantity_kg": 800}, completeness=50)

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.completeness = MagicMock()
            svc.price_client = AsyncMock()
            svc.repo.get_draft_by_id.side_effect = [draft, updated_draft]
            svc.completeness.calculate_score.return_value = 50
            svc.completeness.get_step_completion.return_value = {"step2": True}
            svc.completeness.get_missing_required.return_value = []

            result = await svc.save_step(
                draft.id, seller_id, 2,
                {"photo_urls": ["a.jpg", "b.jpg", "c.jpg"], "grade": "A"},
            )
            svc.repo.update_draft.assert_called_once()
            svc.repo.save_log_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_wrong_owner_raises(self, mock_session):
        draft = _mock_draft(seller_id=uuid4())

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.get_draft_by_id.return_value = draft

            with pytest.raises(DraftNotOwnedError):
                await svc.save_step(draft.id, uuid4(), 1, {"crop": "tomato"})

    @pytest.mark.asyncio
    async def test_published_draft_raises(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id, status="published")

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.get_draft_by_id.return_value = draft

            with pytest.raises(AlreadyPublishedError):
                await svc.save_step(draft.id, seller_id, 1, {"crop": "tomato"})


class TestDeleteDraft:
    @pytest.mark.asyncio
    async def test_soft_deletes(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.get_draft_by_id.return_value = draft

            await svc.delete_draft(draft.id, seller_id)
            svc.repo.delete_draft.assert_called_once_with(draft.id)


class TestCloneDraft:
    @pytest.mark.asyncio
    async def test_copies_step_data(self, mock_session):
        seller_id = uuid4()
        source = _mock_draft(
            seller_id=seller_id,
            step1={"crop": "tomato", "quantity_kg": 800},
            step3={"ask_price_per_q": 1200},
            step4={"transport_type": "seller_delivers"},
            step5={"consent_quality": True},
        )
        clone = _mock_draft(seller_id=seller_id, step1={"crop": "tomato", "quantity_kg": 800})

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.completeness = MagicMock()
            svc.price_client = AsyncMock()
            svc.repo.count_drafts_by_seller.return_value = 1
            svc.repo.get_draft_by_id.return_value = source
            svc.repo.create_draft.return_value = clone
            svc.completeness.calculate_score.return_value = 25
            svc.completeness.get_step_completion.return_value = {"step1": True}
            svc.completeness.get_missing_required.return_value = []

            result = await svc.clone_draft(source.id, seller_id)
            call_args = svc.repo.create_draft.call_args
            initial_data = call_args.kwargs.get("initial_data") or call_args[1].get("initial_data")
            assert "step1_data" in initial_data
            assert "step5_data" not in initial_data

    @pytest.mark.asyncio
    async def test_max_drafts_reached(self, mock_session):
        seller_id = uuid4()
        draft = _mock_draft(seller_id=seller_id)

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.repo.count_drafts_by_seller.return_value = 3
            svc.repo.get_draft_by_id.return_value = draft

            with pytest.raises(MaxDraftsReachedError):
                await svc.clone_draft(draft.id, seller_id)


class TestPriceStaleness:
    @pytest.mark.asyncio
    async def test_stale_price_detected(self, mock_session):
        seller_id = uuid4()
        stale_time = (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat()
        draft = _mock_draft(
            seller_id=seller_id,
            step3={"ask_price_per_q": 1200, "price_fetched_at": stale_time},
        )

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.completeness = MagicMock()
            svc.price_client = AsyncMock()
            svc.repo.get_draft_by_id.return_value = draft
            svc.completeness.get_missing_required.return_value = []

            result = await svc.get_draft(draft.id, seller_id)
            assert result["price_stale"] is True

    @pytest.mark.asyncio
    async def test_fresh_price_not_stale(self, mock_session):
        seller_id = uuid4()
        fresh_time = datetime.now(timezone.utc).isoformat()
        draft = _mock_draft(
            seller_id=seller_id,
            step3={"ask_price_per_q": 1200, "price_fetched_at": fresh_time},
        )

        with patch.object(DraftService, "__init__", lambda self, s: None):
            svc = DraftService(mock_session)
            svc.repo = AsyncMock()
            svc.completeness = MagicMock()
            svc.price_client = AsyncMock()
            svc.repo.get_draft_by_id.return_value = draft
            svc.completeness.get_missing_required.return_value = []

            result = await svc.get_draft(draft.id, seller_id)
            assert result["price_stale"] is False
