"""Human-readable SQL generated from the same frozen product fields as the migration."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateIndex, CreateTable

from templates.product.fields import integer_bounds
from workbench.filesystem import atomic_text


def render(plan, destination):
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
    for entity in plan.entities:
        columns = [
            Column("id", String(36), primary_key=True),
            Column("owner_id", String(36), ForeignKey("users.id"), nullable=False),
        ]
        for field in entity.fields:
            kind = {
                "text": String(field.max_length),
                "enum": String(field.max_length),
                "date": String(10),
                "datetime": String(40),
                "integer": Integer(),
                "boolean": Boolean(),
            }[field.kind]
            columns.append(Column(field.name, kind, nullable=not field.required))
            if field.kind == "integer":
                low, high = integer_bounds(field.model_dump())
                columns.append(CheckConstraint(f'"{field.name}" BETWEEN {low} AND {high}'))
        table = Table(entity.name, metadata, *columns)
        Index("ix_" + entity.name + "_owner_id", table.c.owner_id)
    for name, dialect in [("sqlite", sqlite.dialect()), ("postgresql", postgresql.dialect())]:
        statements = [
            "-- Reference DDL. Normal startup uses the versioned Alembic migration; do not apply both.\n"
        ]
        for table in metadata.sorted_tables:
            statements.append(str(CreateTable(table).compile(dialect=dialect)) + ";")
            statements.extend(
                str(CreateIndex(index).compile(dialect=dialect)) + ";" for index in table.indexes
            )
        atomic_text(destination / "database" / f"schema.{name}.sql", "\n".join(statements) + "\n")
