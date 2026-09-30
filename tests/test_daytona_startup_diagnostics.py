"""Read-only startup inspection must be scoped, redacted and cleanup-independent."""

import json
from types import SimpleNamespace

import pytest
from pydantic import SecretStr

from workbench import daytona_diagnostics as diagnostics
from workbench.filesystem import atomic_text
from workbench.generator import PrerequisiteError
from workbench.sandbox import verify_in_daytona
from workbench.tools import ToolFailure

OWNED_ID = "11111111-2222-4333-8444-555555555555"
OWNED_NAME = "rnd-verify-" + "a" * 32


def local_compose(tmp_path, monkeypatch):
    from scripts import daytona_local

    monkeypatch.setattr(daytona_local, "HOME", tmp_path)
    atomic_text(tmp_path / "compose.lock.yaml", "fixture-only-compose")
    atomic_text(tmp_path / "credentials.json", json.dumps({"password": "local-password-sentinel"}))
    return daytona_local


def test_diagnostics_only_exact_owned_id_fixed_daemons_and_no_environment_dump(
    tmp_path, settings, monkeypatch
):
    local_compose(tmp_path, monkeypatch)
    settings.daytona_api_key = SecretStr("api-secret-sentinel")
    calls = []

    def command(argv, cwd, timeout):
        calls.append(argv)
        assert 0 < timeout <= 5
        assert argv[:2] == ["docker", "--host"]
        assert "unix:///var/run/docker.sock" in argv
        assert "runner" in argv and OWNED_ID in argv
        assert "ps" not in argv and "Env" not in " ".join(argv)
        return {
            "log": "x" * 10000
            + " api-secret-sentinel local-password-sentinel Bearer hidden-token password=other-secret"
            + ' {"token":"json-private-token"} postgresql://u:db-private-password@127.0.0.1/test'
        }

    monkeypatch.setattr(diagnostics, "run_command", command)
    report = diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)
    assert len(calls) == 3 and report["affects_acceptance"] is False
    body = json.dumps(report)
    for secret in [
        "api-secret-sentinel",
        "local-password-sentinel",
        "hidden-token",
        "other-secret",
        "json-private-token",
        "db-private-password",
    ]:
        assert secret not in body
    assert all(
        len(value["text"]) <= diagnostics.MAX_CHARS for value in report["diagnostics"].values()
    )
    assert "OOMKilled" in calls[0][calls[0].index("--format") + 1]
    assert calls[-1][-4:] == ["tail", "-c", "8192", "/tmp/daytona-daemon.log"]


@pytest.mark.parametrize(
    "identifier,name",
    [
        ("other-container", OWNED_NAME),
        (OWNED_ID, "user-sandbox"),
        (OWNED_ID, "rnd-verify-../../other"),
    ],
)
def test_invalid_identity_never_invokes_docker(identifier, name, settings, monkeypatch):
    monkeypatch.setattr(
        diagnostics,
        "run_command",
        lambda *a, **kw: pytest.fail("must not inspect another container"),
    )
    with pytest.raises(ValueError):
        diagnostics.capture_startup(identifier, name, settings)


def test_missing_fixed_compose_does_not_discover_other_installations(
    tmp_path, settings, monkeypatch
):
    from scripts import daytona_local

    monkeypatch.setattr(daytona_local, "HOME", tmp_path)
    monkeypatch.setattr(
        diagnostics, "run_command", lambda *a, **kw: pytest.fail("must not enumerate Docker")
    )
    assert (
        diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)["status"]
        == "fixed-local-compose-unavailable"
    )


def test_diagnostic_errors_are_bounded_and_do_not_escape(tmp_path, settings, monkeypatch):
    local_compose(tmp_path, monkeypatch)

    def fail(*a, **kw):
        error = ToolFailure("private exception must not be serialized")
        error.log = "password=hidden-secret"
        raise error

    monkeypatch.setattr(diagnostics, "run_command", fail)
    report = diagnostics.capture_startup(OWNED_ID, OWNED_NAME, settings)
    assert len(report["diagnostics"]) == 3
    assert all(row["status"] == "unavailable" for row in report["diagnostics"].values())
    assert "hidden-secret" not in json.dumps(report)
    assert "private exception" not in json.dumps(report)


@pytest.mark.parametrize(
    "enabled,diagnostic_failure", [(False, False), (True, False), (True, True)]
)
def test_failed_create_diagnostics_run_before_delete_and_never_skip_cleanup(
    tmp_path, settings, monkeypatch, enabled, diagnostic_failure
):
    product = tmp_path / "product"
    product.mkdir()
    atomic_text(product / "pyproject.toml", "fixture")
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = True
    settings.daytona_api_key = SecretStr("test-local-only")
    settings.daytona_snapshot = "test-local-snapshot"
    settings.daytona_capture_startup_diagnostics = enabled
    events = []

    class Client:
        def create(self, params, **kwargs):
            self.name = params.name
            events.append("create")
            raise RuntimeError("timeout waiting for daemon to start")

        def get(self, name):
            assert name == self.name and name.startswith("rnd-verify-")
            events.append("lookup-exact-name")
            return SimpleNamespace(id=OWNED_ID)

        def delete(self, sandbox, **kwargs):
            assert sandbox.id == OWNED_ID
            events.append("delete")

    def capture(identifier, name, configuration):
        assert identifier == OWNED_ID and name.startswith("rnd-verify-")
        events.append("diagnostics")
        if diagnostic_failure:
            raise RuntimeError("must-not-leak-private-exception")
        return {"status": "captured", "affects_acceptance": False}

    monkeypatch.setattr(diagnostics, "capture_startup", capture)
    with pytest.raises(PrerequisiteError):
        verify_in_daytona(product, "fastapiadmin", settings, client=Client())
    assert events == [
        "create",
        "lookup-exact-name",
        *(["diagnostics"] if enabled else []),
        "delete",
    ]
    body = (tmp_path / "daytona-verification.json").read_text(encoding="utf-8")
    report = json.loads(body)
    assert report["passed"] is False and report["cleanup"] == "deleted"
    assert report["sandbox_id"] == OWNED_ID and "must-not-leak-private-exception" not in body
