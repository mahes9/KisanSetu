"""Org user management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_verified_org_buyer
from app.controllers.user_controller import UserController
from app.db.database import get_db
from app.models.buyer import Buyer
from app.schemas.user_schema import (
    AcceptInvitationRequest,
    InviteUserRequest,
    UpdateUserRoleRequest,
)

router = APIRouter(prefix="/users", tags=["Org Users"])


@router.post("", summary="Invite a user to the organization")
async def invite_user(
    body: InviteUserRequest,
    buyer: Buyer = Depends(require_verified_org_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.invite_user(buyer, body.model_dump(), db)


@router.get("", summary="List org users")
async def list_users(
    buyer: Buyer = Depends(require_verified_org_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.list_users(buyer, db)


@router.post("/accept-invitation", summary="Accept an invitation")
async def accept_invitation(
    body: AcceptInvitationRequest,
    db: AsyncSession = Depends(get_db),
):
    return await UserController.accept_invitation(body.invitation_token, body.password, db)


@router.patch("/{user_id}/role", summary="Update user role")
async def update_role(
    user_id: UUID,
    body: UpdateUserRoleRequest,
    buyer: Buyer = Depends(require_verified_org_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.update_role(user_id, buyer, body.role, db)


@router.delete("/{user_id}", summary="Remove a user")
async def remove_user(
    user_id: UUID,
    buyer: Buyer = Depends(require_verified_org_buyer),
    db: AsyncSession = Depends(get_db),
):
    return await UserController.remove_user(user_id, buyer, db)
