"""Human-authored contest CI vertical using native sessions and PostgreSQL locks.

Mounted as app/plugin/module_rnd/contest/controller.py. The native registry adds
/rnd; this router adds /contest. No standalone app, alternate auth or SQLite.
"""

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from typing import Annotated

from app.common.response import SuccessResponse
from app.core.base_schema import AuthSchema
from app.core.dependencies import db_getter, get_current_user
from app.modules.system.role.model import RoleModel
from app.modules.system.user.model import UserModel, UserRolesModel
from fastapi import APIRouter, Depends, HTTPException, Path, Security
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import ContestInvitation, ContestMembership, ContestTeam

ContestRouter = APIRouter(prefix="/contest", tags=["Authored contest reference fixture"])
STUDENT_ROLE = "rnd_contest_student"
REVIEWER_ROLE = "rnd_contest_reviewer"
Identifier = Annotated[int, Path(gt=0)]
# Commit/rollback finishes before a successful response is published. The
# authentication dependency remains the pinned framework implementation.
Database = Annotated[AsyncSession, Depends(db_getter, scope="function")]
Actor = Annotated[AuthSchema, Security(get_current_user)]


class RequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CreateTeam(RequestBody):
    name: str = Field(min_length=1, max_length=120)
    capacity: StrictInt = Field(ge=2, le=10)
    submission_title: str = Field(min_length=1, max_length=200)


class IssueInvitation(RequestBody):
    expires_in_seconds: StrictInt = Field(ge=1, le=604800)


class RedeemInvitation(RequestBody):
    code: str = Field(min_length=1, max_length=256)


class EmptyBody(RequestBody):
    pass


async def has_role(db, user_id, code):
    return (
        await db.scalar(
            select(RoleModel.id)
            .join(UserRolesModel, UserRolesModel.role_id == RoleModel.id)
            .join(UserModel, UserModel.id == UserRolesModel.user_id)
            .where(
                UserModel.id == user_id,
                UserModel.status == 0,
                UserModel.is_deleted.is_(False),
                RoleModel.code == code,
                RoleModel.status == 0,
                RoleModel.is_deleted.is_(False),
            )
            .limit(1)
        )
        is not None
    )


async def require_role(db, auth, code):
    # SQLite ignores SELECT FOR UPDATE; it cannot certify this concurrency slice.
    if db.get_bind().dialect.name != "postgresql":
        raise HTTPException(503, "Contest reference fixture requires PostgreSQL")
    if not auth.user.id or not await has_role(db, auth.user.id, code):
        raise HTTPException(403, "Contest permission denied")
    return auth.user.id


async def lock_team(db, team_id):
    team = await db.scalar(select(ContestTeam).where(ContestTeam.id == team_id).with_for_update())
    if team is None:
        raise HTTPException(404, "Team not found")
    return team


@ContestRouter.post("/teams")
async def create_team(body: CreateTeam, auth: Actor, db: Database):
    actor = await require_role(db, auth, STUDENT_ROLE)
    # All membership writers lock the native user first, then the team. This
    # serializes cross-team attempts and keeps a consistent lock ordering.
    await db.scalar(select(UserModel.id).where(UserModel.id == actor).with_for_update())
    if await db.scalar(select(ContestMembership.user_id).where(ContestMembership.user_id == actor)):
        raise HTTPException(409, "Already belongs to a team")
    team = ContestTeam(captain_id=actor, **body.model_dump())
    db.add(team)
    await db.flush()
    db.add(ContestMembership(team_id=team.id, user_id=actor))
    await db.flush()
    return SuccessResponse(data={"id": team.id})


@ContestRouter.post("/teams/{team_id}/invitations")
async def issue_invitation(team_id: Identifier, body: IssueInvitation, auth: Actor, db: Database):
    actor = await require_role(db, auth, STUDENT_ROLE)
    team = await lock_team(db, team_id)
    if team.captain_id != actor:
        raise HTTPException(403, "Only the captain may issue invitation codes")
    code = token_urlsafe(32)
    invitation = ContestInvitation(
        team_id=team_id,
        code_hash=sha256(code.encode()).hexdigest(),
        expires_at=datetime.now(UTC) + timedelta(seconds=body.expires_in_seconds),
        status="active",
    )
    db.add(invitation)
    await db.flush()
    # The opaque code is returned once, never stored in the business table.
    return SuccessResponse(data={"id": invitation.id, "code": code})


@ContestRouter.post("/invitations/redeem")
async def redeem_invitation(body: RedeemInvitation, auth: Actor, db: Database):
    actor = await require_role(db, auth, STUDENT_ROLE)
    invitation_ref = (
        await db.execute(
            select(ContestInvitation.id, ContestInvitation.team_id).where(
                ContestInvitation.code_hash == sha256(body.code.encode()).hexdigest()
            )
        )
    ).one_or_none()
    if invitation_ref is None:
        raise HTTPException(404, "Invitation not found")
    # The lock order is user -> team -> invitation. The team lock serializes
    # different users and different codes competing for the same last slot.
    await db.scalar(select(UserModel.id).where(UserModel.id == actor).with_for_update())
    team = await lock_team(db, invitation_ref.team_id)
    invitation = await db.scalar(
        select(ContestInvitation)
        .where(ContestInvitation.id == invitation_ref.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if invitation is None or invitation.team_id != team.id:
        raise HTTPException(404, "Invitation not found")
    if invitation.status != "active" or invitation.expires_at <= datetime.now(UTC):
        raise HTTPException(410, "Invitation expired or revoked")
    membership = await db.scalar(
        select(ContestMembership).where(ContestMembership.user_id == actor)
    )
    if membership is not None:
        if membership.team_id != team.id:
            raise HTTPException(409, "Already belongs to another team")
        # Exact member replay succeeds even if the team's last slot is full.
        return SuccessResponse(data={"id": invitation.id, "team_id": team.id})
    count = await db.scalar(
        select(func.count())
        .select_from(ContestMembership)
        .where(ContestMembership.team_id == team.id)
    )
    if count >= team.capacity:
        raise HTTPException(409, "Team is full")
    db.add(ContestMembership(team_id=team.id, user_id=actor))
    await db.flush()
    return SuccessResponse(data={"id": invitation.id, "team_id": team.id})


@ContestRouter.post("/invitations/{invitation_id}/revoke")
async def revoke_invitation(invitation_id: Identifier, body: EmptyBody, auth: Actor, db: Database):
    actor = await require_role(db, auth, STUDENT_ROLE)
    team_id = await db.scalar(
        select(ContestInvitation.team_id).where(ContestInvitation.id == invitation_id)
    )
    if team_id is None:
        raise HTTPException(404, "Invitation not found")
    team = await lock_team(db, team_id)
    if team.captain_id != actor:
        raise HTTPException(403, "Only the captain may revoke invitation codes")
    invitation = await db.scalar(
        select(ContestInvitation)
        .where(ContestInvitation.id == invitation_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    if invitation is None:
        raise HTTPException(404, "Invitation not found")
    invitation.status = "revoked"
    await db.flush()
    return SuccessResponse(data={"id": invitation.id})


@ContestRouter.get("/teams/{team_id}")
async def team_detail(team_id: Identifier, auth: Actor, db: Database):
    actor = await require_role(db, auth, STUDENT_ROLE)
    team = await db.scalar(select(ContestTeam).where(ContestTeam.id == team_id))
    if team is None:
        raise HTTPException(404, "Team not found")
    if team.captain_id != actor:
        raise HTTPException(403, "Only the captain may read team membership")
    members = list(
        (
            await db.scalars(
                select(ContestMembership.user_id)
                .where(ContestMembership.team_id == team.id)
                .order_by(ContestMembership.user_id)
            )
        ).all()
    )
    return SuccessResponse(data={"id": team.id, "name": team.name, "member_ids": members})


@ContestRouter.get("/review/teams/{team_id}")
async def blind_review(team_id: Identifier, auth: Actor, db: Database):
    await require_role(db, auth, REVIEWER_ROLE)
    # Explicit projection: never serialize an ORM __dict__, a native user,
    # membership, invitation, attachment filename, or generic audit metadata.
    row = (
        await db.execute(
            select(ContestTeam.id, ContestTeam.submission_title).where(ContestTeam.id == team_id)
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(404, "Submission not found")
    return SuccessResponse(data={"id": row.id, "submission_title": row.submission_title})
