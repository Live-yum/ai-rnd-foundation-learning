"""Controller resets only its attested ephemeral cluster; never user databases."""

import json
import os
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine

from workbench import capability_sandbox
from workbench import capability_stack as stack
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection


def identity(oid=100):
    return dict(
        database="rnd_product",
        database_oid=oid,
        cluster="987654321",
        directory=stack.PG_ROOT + "/data",
        sandbox_id="owned-sandbox",
    )


def plan():
    return SimpleNamespace(
        selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(port=8000)
    )


def test_reset_drains_before_identity_check_and_fixed_owned_ddl(monkeypatch):
    events = []
    replies = iter([identity(), identity(101)])
    monkeypatch.setattr(
        capability_sandbox, "restart_application_identity", lambda *a, **kw: events.append("drain")
    )

    def owned(*args):
        events.append("identity")
        return next(replies)

    monkeypatch.setattr(stack, "owned_database_identity", owned)

    def execute(sandbox, argv, timeout):
        events.append(argv)
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(stack, "control_exec", execute)
    result = stack.recreate_owned_native_database(
        SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
    )
    assert events[:2] == ["drain", "identity"]
    assert len([row for row in events if isinstance(row, list)]) == 3
    assert result["database_oid"] == 101
    assert all(stack.PG_SOCKET in row for row in events if isinstance(row, list))
    assert "dropdb" in " ".join(events[2]) and events[2][-1] == "rnd_product"
    assert "--force" not in events[2]


@pytest.mark.parametrize(
    "field,value",
    [
        ("cluster", "other"),
        ("sandbox_id", "other"),
        ("database", "userdb"),
        ("directory", "/other/data"),
        ("database_oid", 999),
    ],
)
def test_identity_drift_prevents_any_drop(monkeypatch, field, value):
    monkeypatch.setattr(capability_sandbox, "restart_application_identity", lambda *a, **kw: None)
    monkeypatch.setattr(
        stack, "owned_database_identity", lambda *args: {**identity(), field: value}
    )
    monkeypatch.setattr(stack, "control_exec", lambda *args: pytest.fail("No destructive command"))
    with pytest.raises(CheckFailure, match="身份"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


def test_live_thread_blocks_before_identity_or_ddl(monkeypatch):
    def fail(*args, **kwargs):
        raise CheckFailure("live thread")

    monkeypatch.setattr(capability_sandbox, "restart_application_identity", fail)
    monkeypatch.setattr(stack, "control_exec", lambda *args: pytest.fail("No command"))
    with pytest.raises(CheckFailure, match="live thread"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


@pytest.mark.parametrize(
    "field,value",
    [("cluster", "other"), ("sandbox_id", "other"), ("database_oid", 100)],
)
def test_reset_rejects_cluster_sandbox_drift_or_unchanged_oid(monkeypatch, field, value):
    replies = iter([identity(), {**identity(101), field: value}])
    monkeypatch.setattr(capability_sandbox, "restart_application_identity", lambda *a, **kw: None)
    monkeypatch.setattr(stack, "owned_database_identity", lambda *a: next(replies))
    monkeypatch.setattr(stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0))
    with pytest.raises(CheckFailure, match="新库身份"):
        stack.recreate_owned_native_database(
            SimpleNamespace(id="owned-sandbox"), plan(), 30, identity()
        )


def test_identity_reads_only_fixed_private_database(monkeypatch):
    seen = []
    body = identity()
    body.pop("sandbox_id")

    def execute(sandbox, argv, timeout):
        seen.append(argv)
        return SimpleNamespace(exit_code=0, result=json.dumps(body))

    monkeypatch.setattr(stack, "control_exec", execute)
    assert stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30) == identity()
    command = seen[0]
    assert command[:4] == ["/usr/sbin/runuser", "-u", "postgres", "--"]
    assert "PGOPTIONS=-c search_path=pg_catalog" in command
    assert stack.PG_SOCKET in command and "rnd_product" in command
    assert "pg_catalog.pg_control_system()" in command[-1]
    assert "SELECT oid::pg_catalog.int8 FROM pg_catalog.pg_database" in command[-1]


@pytest.mark.parametrize(
    "field,value",
    [
        ("database", "userdb"),
        ("directory", "/other/data"),
        ("database_oid", "100"),
        ("database_oid", True),
        ("database_oid", 100.0),
        ("database_oid", None),
        ("cluster", ""),
        ("cluster", "other"),
        ("cluster", "1" * 31),
        ("unexpected", True),
    ],
)
def test_identity_rejects_untrusted_fields_without_coercion(monkeypatch, field, value):
    body = identity()
    body.pop("sandbox_id")
    body[field] = value
    monkeypatch.setattr(
        stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(body))
    )
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


@pytest.mark.parametrize("body", ["", "not-json", "null", "[]", "{}", " " * 4097])
def test_identity_rejects_missing_malformed_or_oversize_reply(monkeypatch, body):
    monkeypatch.setattr(stack, "control_exec", lambda *a: SimpleNamespace(exit_code=0, result=body))
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


def test_identity_rejects_failed_command_even_with_valid_json(monkeypatch):
    body = identity()
    body.pop("sandbox_id")
    monkeypatch.setattr(
        stack, "control_exec", lambda *a: SimpleNamespace(exit_code=1, result=json.dumps(body))
    )
    with pytest.raises(CheckFailure, match="私有临时数据库身份"):
        stack.owned_database_identity(SimpleNamespace(id="owned-sandbox"), 30)


@pytest.mark.postgres
def test_postgres_oid_json_requires_int8_cast():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; mandatory in postgres Actions job")
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            value = connection.exec_driver_sql(
                "SELECT pg_catalog.json_build_object("
                "'original_oid',oid,'numeric_oid',oid::pg_catalog.int8,"
                "'maximum_oid',4294967295::pg_catalog.oid::pg_catalog.int8) "
                "FROM pg_catalog.pg_database WHERE datname=current_database()"
            ).scalar_one()
        assert type(value["original_oid"]) is str
        assert type(value["numeric_oid"]) is int
        assert value["numeric_oid"] == int(value["original_oid"]) > 0
        assert type(value["maximum_oid"]) is int
        assert value["maximum_oid"] == 2**32 - 1
    finally:
        engine.dispose()
