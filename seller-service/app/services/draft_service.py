"""Draft lifecycle service — Module 3."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.price_client import PriceClient
from app.core.constants import DraftConfig, ListingConfig
from app.core.exceptions import (
    AlreadyPublishedError,
    CropNotInPhase1Error,
    DraftNotFoundError,
    DraftNotOwnedError,
    MaxDraftsReachedError,
)
from app.core.validators import validate_crop, validate_quantity
from app.repositories.draft_repo import DraftRepository
from app.services.completeness_service import CompletenessService


class DraftService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DraftRepository(session)
        self.completeness = CompletenessService
        self.price_client = PriceClient()

    async def create_draft(self, seller_id: UUID, step1_data: dict) -> dict:
        count = await self.repo.count_drafts_by_seller(seller_id)
        if count >= DraftConfig.MAX_DRAFTS:
            raise MaxDraftsReachedError()

        crop = step1_data.get("crop", "")
        validate_crop(crop)
        if "quantity_kg" in step1_data:
            validate_quantity(step1_data["quantity_kg"], crop)

        draft = await self.repo.create_draft(
            seller_id=seller_id,
            initial_data={"step1_data": step1_data},
        )

        draft_dict = self._draft_to_dict(draft)
        score = self.completeness.calculate_score(draft_dict)
        await self.repo.update_draft(draft.id, {
            "completeness_score": score,
            "step1_completed": self.completeness.get_step_completion(draft_dict).get("step1", False),
        })
        draft.completeness_score = score

        return self._build_response(draft)

    async def save_step(
        self,
        draft_id: UUID,
        seller_id: UUID,
        step_num: int,
        step_data: dict,
        save_trigger: str = "manual",
        device: str | None = None,
        session_id: str | None = None,
        network_type: str | None = None,
    ) -> dict:
        draft = await self._get_owned_draft(draft_id, seller_id)

        if draft.draft_status == "published":
            raise AlreadyPublishedError()

        if step_num == 1 and "crop" in step_data:
            validate_crop(step_data["crop"])
            if "quantity_kg" in step_data:
                validate_quantity(step_data["quantity_kg"], step_data["crop"])

        step_key = f"step{step_num}_data"
        existing = getattr(draft, step_key) or {}
        merged = {**existing, **step_data}

        draft_dict = self._draft_to_dict(draft)
        draft_dict[step_key] = merged
        score = self.completeness.calculate_score(draft_dict)
        step_complete = self.completeness.get_step_completion(draft_dict)

        updates = {
            step_key: merged,
            "completeness_score": score,
            f"step{step_num}_completed": step_complete.get(f"step{step_num}", False),
            "last_active_at": datetime.now(timezone.utc),
        }
        if step_num > draft.current_step:
            updates["current_step"] = step_num
        if score == 100:
            updates["draft_status"] = "complete"

        await self.repo.update_draft(draft_id, updates)
        await self.repo.save_log_entry(
            draft_id=draft_id,
            save_trigger=save_trigger,
            step_number=step_num,
            data=step_data,
            device=device,
            session_id=session_id,
            network_type=network_type,
        )

        draft = await self.repo.get_draft_by_id(draft_id)
        return self._build_response(draft)

    async def get_draft(self, draft_id: UUID, seller_id: UUID) -> dict:
        draft = await self._get_owned_draft(draft_id, seller_id)
        return self._build_response(draft)

    async def list_drafts(self, seller_id: UUID) -> dict:
        drafts = await self.repo.list_drafts_by_seller(seller_id)
        return {
            "drafts": [self._build_response(d) for d in drafts],
            "total": len(drafts),
        }

    async def delete_draft(self, draft_id: UUID, seller_id: UUID) -> None:
        await self._get_owned_draft(draft_id, seller_id)
        await self.repo.delete_draft(draft_id)

    async def clone_draft(self, draft_id: UUID, seller_id: UUID) -> dict:
        count = await self.repo.count_drafts_by_seller(seller_id)
        if count >= DraftConfig.MAX_DRAFTS:
            raise MaxDraftsReachedError()

        source = await self._get_owned_draft(draft_id, seller_id)

        clone_data: dict = {}
        if source.step1_data:
            clone_data["step1_data"] = dict(source.step1_data)
        if source.step3_data:
            clone_data["step3_data"] = dict(source.step3_data)
        if source.step4_data:
            clone_data["step4_data"] = dict(source.step4_data)

        new_draft = await self.repo.create_draft(
            seller_id=seller_id, initial_data=clone_data
        )

        draft_dict = self._draft_to_dict(new_draft)
        score = self.completeness.calculate_score(draft_dict)
        step_comp = self.completeness.get_step_completion(draft_dict)
        await self.repo.update_draft(new_draft.id, {
            "completeness_score": score,
            "step1_completed": step_comp.get("step1", False),
            "step3_completed": step_comp.get("step3", False),
            "step4_completed": step_comp.get("step4", False),
        })
        new_draft.completeness_score = score
        return self._build_response(new_draft)

    async def resume_draft(self, draft_id: UUID, seller_id: UUID) -> dict:
        draft = await self._get_owned_draft(draft_id, seller_id)
        await self.repo.update_draft(draft_id, {"last_active_at": datetime.now(timezone.utc)})
        return self._build_response(draft)

    async def _get_owned_draft(self, draft_id: UUID, seller_id: UUID):
        draft = await self.repo.get_draft_by_id(draft_id)
        if draft is None:
            raise DraftNotFoundError()
        if draft.seller_id != seller_id:
            raise DraftNotOwnedError()
        return draft

    def _check_price_staleness(self, step3_data: dict | None) -> bool:
        if not step3_data:
            return False
        fetched_at = step3_data.get("price_fetched_at")
        if not fetched_at:
            return False
        if isinstance(fetched_at, str):
            fetched_at = datetime.fromisoformat(fetched_at)
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        delta = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 60
        return delta > DraftConfig.STALENESS_MINUTES

    def _draft_to_dict(self, draft) -> dict:
        return {
            "step1_data": draft.step1_data,
            "step2_data": draft.step2_data,
            "step3_data": draft.step3_data,
            "step4_data": draft.step4_data,
            "step5_data": draft.step5_data,
        }

    def _build_response(self, draft) -> dict:
        draft_dict = self._draft_to_dict(draft)
        missing = self.completeness.get_missing_required(draft_dict)
        price_stale = self._check_price_staleness(draft.step3_data)
        return {
            "id": str(draft.id),
            "seller_id": str(draft.seller_id),
            "draft_status": draft.draft_status,
            "current_step": draft.current_step,
            "completeness_score": draft.completeness_score,
            "step1_data": draft.step1_data,
            "step2_data": draft.step2_data,
            "step3_data": draft.step3_data,
            "step4_data": draft.step4_data,
            "step5_data": draft.step5_data,
            "step1_completed": draft.step1_completed,
            "step2_completed": draft.step2_completed,
            "step3_completed": draft.step3_completed,
            "step4_completed": draft.step4_completed,
            "step5_completed": draft.step5_completed,
            "last_active_at": str(draft.last_active_at) if draft.last_active_at else None,
            "price_stale": price_stale,
            "missing_fields": missing,
            "created_at": str(draft.created_at) if draft.created_at else None,
            "updated_at": str(draft.updated_at) if draft.updated_at else None,
        }
