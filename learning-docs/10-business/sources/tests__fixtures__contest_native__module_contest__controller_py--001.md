# tests/fixtures/contest_native/module_contest/controller.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `RequestBody`（L34–L35）：继承`BaseModel`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `CreateTeam`（L38–L41）：继承`RequestBody`。声明的数据项为`name`、`capacity`、`submission_title`；类型约束/数据库列参数以完整定义为准。
- `IssueInvitation`（L44–L45）：继承`RequestBody`。声明的数据项为`expires_in_seconds`；类型约束/数据库列参数以完整定义为准。
- `RedeemInvitation`（L48–L49）：继承`RequestBody`。声明的数据项为`code`；类型约束/数据库列参数以完整定义为准。
- `EmptyBody`（L52–L53）：继承`RequestBody`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `has_role`（L56–L73）：接收`db`、`user_id`、`code`。 调用`db.scalar`、`select(RoleModel.id) .join(UserRolesModel, UserRolesModel.role_id…`、`select(RoleModel.id) .join`、`select`、`UserModel.is_deleted.is_`、`RoleModel.is_deleted.is_`。 返回路径：L57的`await db.scalar( select(RoleModel.id) .join(UserRolesModel, UserRolesModel.role_id == Role…`。
- `require_role`（L76–L82）：接收`db`、`auth`、`code`。 控制顺序：L78按`db.get_bind().dialect.name != "postgresql"`分支；L79抛异常，停止当前正常路径；L80按`not auth.user.id or not await has_role(db, auth.user.id, code)`分支；L81抛异常，停止当前正常路径。 调用`db.get_bind`、`HTTPException`、`has_role`。 返回路径：L82的`auth.user.id`。
- `lock_team`（L85–L89）：接收`db`、`team_id`。 控制顺序：L87按`team is None`分支；L88抛异常，停止当前正常路径。 调用`db.scalar`、`select(ContestTeam).where(ContestTeam.id == team_id).with_for_upd…`、`select(ContestTeam).where`、`select`、`HTTPException`。 返回路径：L89的`team`。
- `create_team`（L93–L105）：接收`body`、`auth`、`db`。 控制顺序：L98按`await db.scalar(select(ContestMembership.user_id).where(ContestMembership.user_id == …`分支；L99抛异常，停止当前正常路径。 调用`require_role`、`db.scalar`、`select(UserModel.id).where(UserModel.id == actor).with_for_update`、`select(UserModel.id).where`、`select`、`select(ContestMembership.user_id).where`、`HTTPException`、`ContestTeam`、`body.model_dump`等。 返回路径：L105的`SuccessResponse(data={"id": team.id})`。
- `issue_invitation`（L109–L124）：接收`team_id`、`body`、`auth`、`db`。 控制顺序：L112按`team.captain_id != actor`分支；L113抛异常，停止当前正常路径。 调用`require_role`、`lock_team`、`HTTPException`、`token_urlsafe`、`ContestInvitation`、`sha256(code.encode()).hexdigest`、`sha256`、`code.encode`、`datetime.now`等。 返回路径：L124的`SuccessResponse(data={"id": invitation.id, "code": code})`。
- `redeem_invitation`（L128–L170）：接收`body`、`auth`、`db`。 控制顺序：L137按`invitation_ref is None`分支；L138抛异常，停止当前正常路径；L149按`invitation is None or invitation.team_id != team.id`分支；L150抛异常，停止当前正常路径；L151按`invitation.status != "active" or invitation.expires_at <= datetime.now(UTC)`分支；L152抛异常，停止当前正常路径；L156按`membership is not None`分支；L157按`membership.team_id != team.id`分支。后续分支沿下方源码相同行号继续阅读。 调用`require_role`、`( await db.execute( select(ContestInvitation.id, ContestInvitatio…`、`db.execute`、`select(ContestInvitation.id, ContestInvitation.team_id).where`、`select`、`sha256(body.code.encode()).hexdigest`、`sha256`、`body.code.encode`、`HTTPException`等。 返回路径：L160的`SuccessResponse(data={"id": invitation.id, "team_id": team.id})`；L170的`SuccessResponse(data={"id": invitation.id, "team_id": team.id})`。
- `revoke_invitation`（L174–L194）：接收`invitation_id`、`body`、`auth`、`db`。 控制顺序：L179按`team_id is None`分支；L180抛异常，停止当前正常路径；L182按`team.captain_id != actor`分支；L183抛异常，停止当前正常路径；L190按`invitation is None`分支；L191抛异常，停止当前正常路径。 调用`require_role`、`db.scalar`、`select(ContestInvitation.team_id).where`、`select`、`HTTPException`、`lock_team`、`select(ContestInvitation) .where(ContestInvitation.id == invitati…`、`select(ContestInvitation) .where`、`db.flush`等。 返回路径：L194的`SuccessResponse(data={"id": invitation.id})`。
- `team_detail`（L198–L214）：接收`team_id`、`auth`、`db`。 控制顺序：L201按`team is None`分支；L202抛异常，停止当前正常路径；L203按`team.captain_id != actor`分支；L204抛异常，停止当前正常路径。 调用`require_role`、`db.scalar`、`select(ContestTeam).where`、`select`、`HTTPException`、`list`、`( await db.scalars( select(ContestMembership.user_id) .where(Cont…`、`db.scalars`、`select(ContestMembership.user_id) .where(ContestMembership.team_i…`等。 返回路径：L214的`SuccessResponse(data={"id": team.id, "name": team.name, "member_ids": members})`。
- `blind_review`（L218–L229）：接收`team_id`、`auth`、`db`。 控制顺序：L227按`row is None`分支；L228抛异常，停止当前正常路径。 调用`require_role`、`( await db.execute( select(ContestTeam.id, ContestTeam.submission…`、`db.execute`、`select(ContestTeam.id, ContestTeam.submission_title).where`、`select`、`HTTPException`、`SuccessResponse`、`ContestRouter.get`。 返回路径：L229的`SuccessResponse(data={"id": row.id, "submission_title": row.submission_title})`。

</details>

**创建路径：** `tests/fixtures/contest_native/module_contest/controller.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L229。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9314`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/contest_native/module_contest/controller.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3e0fa07af5d2422c71ad125a26d6931405e35d05b394721d92879b5c866737ce"} -->
````python
# tests/fixtures/contest_native/module_contest/controller.py
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
````
