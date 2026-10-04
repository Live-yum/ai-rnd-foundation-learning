"""Controller resets only its attested ephemeral cluster; never user databases."""

import json
from types import SimpleNamespace

import pytest

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
    [("cluster", "other"), ("sandbox_id", "other"), ("database", "userdb"), ("database_oid", 999)],
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
    assert stack.PG_SOCKET in command and "rnd_product" in command
    assert "pg_catalog.pg_control_system()" in command[-1]
