import json
from datetime import UTC, datetime
from pathlib import Path

from app.core.base_model import MappedBase
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

CONFIG = json.loads(Path(__file__).with_name("business.json").read_text(encoding="utf-8"))


class BusinessEvent(MappedBase):
    __tablename__ = CONFIG["namespace"] + "_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity: Mapped[str] = mapped_column(String(40), index=True)
    record_id: Mapped[int] = mapped_column(Integer, index=True)
    actor: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id", ondelete="RESTRICT"))
    recipient: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sys_user.id", ondelete="RESTRICT"), index=True
    )
    event: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)
    source_key: Mapped[str | None] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
