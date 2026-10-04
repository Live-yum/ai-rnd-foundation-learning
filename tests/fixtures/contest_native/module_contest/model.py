"""Authored reference fixture ORM, registered by the real native model loader."""

from datetime import datetime

from app.core.base_model import MappedBase
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class ContestTeam(MappedBase):
    __tablename__ = "rnd_contest_team"
    __table_args__ = (CheckConstraint("capacity >= 2 AND capacity <= 10", name="capacity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    captain_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id", ondelete="RESTRICT"))
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    submission_title: Mapped[str] = mapped_column(String(200), nullable=False)


class ContestMembership(MappedBase):
    __tablename__ = "rnd_contest_membership"
    __table_args__ = (UniqueConstraint("user_id", name="uq_contest_one_team_per_user"),)

    team_id: Mapped[int] = mapped_column(
        ForeignKey("rnd_contest_team.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id", ondelete="RESTRICT"), primary_key=True
    )


class ContestInvitation(MappedBase):
    __tablename__ = "rnd_contest_invitation"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'revoked', 'expired')", name="invitation_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("rnd_contest_team.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
