"""PostgreSQL must match the native audit convention without changing business booleans."""

from sqlalchemy import Boolean, SmallInteger

from scripts.ci_native_generated import acceptance_spec
from workbench.native_modules import native_metadata


def test_native_deleted_uses_upstream_smallint_and_active_remains_boolean():
    _, tables, _ = native_metadata(
        "yudao-vben",
        acceptance_spec(),
        "postgresql+psycopg://lab:lab@127.0.0.1/native_codegen",
        "postgres-contract",
    )
    assert isinstance(tables[0].c.deleted.type, SmallInteger)
    assert isinstance(tables[0].c.active.type, Boolean)
    assert str(tables[0].c.deleted.server_default.arg) == "0"
    assert tables[0].c.tenant_id.nullable is False
