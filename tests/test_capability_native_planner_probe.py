"""Planner-probe protocol mocks; never a live PostgreSQL safety certificate."""

from types import SimpleNamespace

import pytest

from scripts import capability_native_planner_probe as probe
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection

NAME = "rnd_planner_" + "a" * 32


def setup(monkeypatch, *, count=1, read="restricted", fail_create=False, fail_cleanup=False):
    calls = []
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex="a" * 32))
    monkeypatch.setattr(probe, "product_argv", lambda plan, argv, env: ["app-only", *argv])
    monkeypatch.setattr(probe, "pg_verifier_argv", lambda sql: ["reader-only", sql])

    def guarded(sandbox, argv, timeout):
        calls.append(argv)
        if argv[0] == "app-only":
            cleanup = "DROP TABLE" in argv[-1]
            failed = fail_cleanup if cleanup else fail_create
            return (1, "") if failed else (0, probe.COMPLETE)
        assert argv[0] == "reader-only"
        return 0, read

    def counts(sandbox, plan, timeout):
        calls.append(["production-count", *plan.runtime.database_tables])
        assert plan.runtime.database_tables == [NAME]
        return {NAME: count}

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    monkeypatch.setattr(probe, "database_counts", counts)
    return calls


def execute():
    plan = SimpleNamespace(selection=Selection(template="fastapiadmin"))
    return probe.verify_native_planner_identity(None, plan, {"DATABASE_PASSWORD": "synthetic"}, 30)


def test_owned_probe_uses_app_ddl_and_separate_reader_then_cleans_up(monkeypatch):
    calls = setup(monkeypatch)
    assert execute() == {probe.CHECK: True}
    assert [call[0] for call in calls] == [
        "app-only",
        "production-count",
        "reader-only",
        "app-only",
    ]
    assert "CREATE INDEX" in calls[0][-1]
    assert "IMMUTABLE" in calls[0][-1]
    assert "privileged planner evaluation" in calls[0][-1]
    assert "SET ROLE postgres" in calls[2][-1]
    assert "insufficient_privilege" in calls[2][-1]
    assert "END;\n$probe$" in calls[0][-1]
    assert "session_user='rnd_verify'" in calls[2][-1]
    assert calls[-1][-1] == probe.statements(NAME)[2]
    assert "TO PROGRAM" not in calls[0][-1] and "pg_read_file" not in calls[0][-1]


@pytest.mark.parametrize("updates", [{"count": 0}, {"read": "postgres"}, {"fail_create": True}])
def test_failed_probe_never_emits_success_and_still_cleans_up(monkeypatch, updates):
    calls = setup(monkeypatch, **updates)
    with pytest.raises(CheckFailure):
        execute()
    assert calls[-1][0] == "app-only" and "DROP TABLE" in calls[-1][-1]


def test_failed_cleanup_prevents_certificate(monkeypatch):
    setup(monkeypatch, fail_cleanup=True)
    with pytest.raises(CheckFailure, match="清理"):
        execute()


@pytest.mark.parametrize(
    "name", ["user_table", "rnd_planner_" + "a" * 32 + ";DROP DATABASE x", NAME.upper()]
)
def test_only_controller_generated_probe_identifiers_are_allowed(name):
    with pytest.raises(CheckFailure):
        probe.statements(name)


def test_non_native_database_is_rejected_before_any_command(monkeypatch):
    monkeypatch.setattr(probe, "run_guarded_control", lambda *a: pytest.fail("command ran"))
    with pytest.raises(CheckFailure):
        probe.verify_native_planner_identity(None, SimpleNamespace(selection=Selection()), {}, 10)
