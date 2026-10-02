"""Business references retain real native physical identity types and ordered DDL."""

import pytest
from sqlalchemy import BigInteger, DateTime, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from test_business_contracts import business_plan

from workbench.domain import Plan
from workbench.native_modules import native_metadata


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_business_native_schema_has_real_foreign_keys(template):
    plan = Plan.model_validate(business_plan())
    metadata, tables, names = native_metadata(
        template, plan, "postgresql+psycopg://native:lab@127.0.0.1/native_codegen", "business"
    )
    request = next(t for t in tables if t.name == names["requests"])
    assert isinstance(request.c.customer_id.type, Integer)
    assert isinstance(request.c.resolved_at.type, DateTime)
    assert (
        next(iter(request.c.customer_id.foreign_keys)).target_fullname == names["customers"] + ".id"
    )
    user = "sys_user" if template == "fastapiadmin" else "system_users"
    assert next(iter(request.c.assignee_id.foreign_keys)).target_fullname == user + ".id"
    ordered = [t.name for t in metadata.sorted_tables]
    assert ordered.index(names["customers"]) < ordered.index(names["requests"])
    ddl = str(CreateTable(request).compile(dialect=postgresql.dialect()))
    assert "ON DELETE RESTRICT" in ddl
    if template == "yudao-vben":
        assert isinstance(request.c.customer_id.type, BigInteger)


def test_fastapi_business_indexes_match_original_mixins():
    metadata, tables, _ = native_metadata(
        "fastapiadmin",
        Plan.model_validate(business_plan()),
        "postgresql+psycopg://native:lab@127.0.0.1/native_codegen",
        "indexed",
    )
    for table in tables:
        indexes = {
            tuple(column.name for column in index.columns): index.unique for index in table.indexes
        }
        assert indexes[("uuid",)] is True
        assert {
            ("id",),
            ("is_deleted",),
            ("created_time",),
            ("created_id",),
            ("updated_id",),
            ("deleted_id",),
        } <= indexes.keys()
        assert not any(
            getattr(constraint, "__visit_name__", "") == "unique_constraint"
            and [c.name for c in constraint.columns] == ["uuid"]
            for constraint in table.constraints
        )
