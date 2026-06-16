"""Async repository for AIGradingLog CRUD and analytics."""

from __future__ import annotations

import uuid

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_grading_log import AIGradingLog


class AILogRepository:
    """Data-access layer for AI grading audit logs."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_log(self, log_data: dict) -> AIGradingLog:
        """Insert a new grading log entry and return it."""
        log = AIGradingLog(**log_data)
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log

    async def get_logs_by_draft(self, draft_id: uuid.UUID) -> list[AIGradingLog]:
        """Return all grading attempts for a draft, newest first."""
        stmt = (
            select(AIGradingLog)
            .where(AIGradingLog.listing_draft_id == draft_id)
            .order_by(AIGradingLog.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_successful(
        self, draft_id: uuid.UUID
    ) -> AIGradingLog | None:
        """Return the most recent successful grading log for a draft, or None."""
        stmt = (
            select(AIGradingLog)
            .where(
                AIGradingLog.listing_draft_id == draft_id,
                AIGradingLog.success.is_(True),
            )
            .order_by(AIGradingLog.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_grading_stats(self) -> dict:
        """Return aggregate statistics across all grading attempts.

        Returns:
            dict with keys: total_grades, avg_confidence, success_rate
        """
        stmt = select(
            func.count(AIGradingLog.id).label("total_grades"),
            func.avg(
                case(
                    (AIGradingLog.success.is_(True), AIGradingLog.confidence_score),
                    else_=None,
                )
            ).label("avg_confidence"),
            func.count(
                case(
                    (AIGradingLog.success.is_(True), AIGradingLog.id),
                    else_=None,
                )
            ).label("success_count"),
        )
        result = await self._session.execute(stmt)
        row = result.one()

        total = row.total_grades or 0
        success_count = row.success_count or 0
        avg_conf = float(row.avg_confidence) if row.avg_confidence is not None else 0.0
        success_rate = (success_count / total * 100) if total > 0 else 0.0

        return {
            "total_grades": total,
            "avg_confidence": round(avg_conf, 1),
            "success_rate": round(success_rate, 1),
        }
