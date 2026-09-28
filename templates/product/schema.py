"""Product database is independent of the platform; no credentials are inherited."""

import json
import os
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
)

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "approved-spec.json").read_text(encoding="utf-8"))
DATA = Path(os.environ.get("PRODUCT_DATA_DIR", ROOT / ".data")).resolve()
DATA.mkdir(parents=True, exist_ok=True)
url = os.environ.get("PRODUCT_DATABASE_URL") or f"sqlite:///{(DATA / 'product.db').as_posix()}"
args = {"check_same_thread": False, "autocommit": False} if url.startswith("sqlite:") else {}
engine = create_engine(url, connect_args=args, pool_pre_ping=True)
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def configure(connection, _):
        old = connection.autocommit
        connection.autocommit = True
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
        finally:
            connection.autocommit = old


metadata = MetaData()
Table(
    "users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("username", String(100), nullable=False, unique=True),
    Column("password", String(400), nullable=False),
)
Table(
    "tokens",
    metadata,
    Column("token", String(64), primary_key=True),
    Column("user_id", String(36), ForeignKey("users.id"), nullable=False),
    Column("expires_at", Integer, nullable=False),
)
for entity in SPEC["entities"]:
    columns = [
        Column("id", String(36), primary_key=True),
        Column("owner_id", String(36), ForeignKey("users.id"), nullable=False),
    ]
    for field in entity["fields"]:
        kind = {"text": String(field["max_length"]), "integer": Integer(), "boolean": Boolean()}[
            field["kind"]
        ]
        columns.append(Column(field["name"], kind, nullable=not field["required"]))
    Table(entity["name"], metadata, *columns)
