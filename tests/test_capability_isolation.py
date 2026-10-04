"""Verify every source command is composed through the same non-bypassable launcher."""

import json
import os
import shlex
import subprocess
import sys
from types import SimpleNamespace

import pytest

from workbench.capability_isolation import IsolationUnavailable, product_argv


@pytest.mark.parametrize(
    "output,exit_code,shape",
    [
        ("warning: setlocale: private-sentinel\n0\n", 0, "locale-warning"),
        ("private-sentinel\n0\n", 0, "other"),
        ("", 0, "empty"),
        (None, 0, "empty"),
        (b"0\n", 0, "empty"),
        (0, 0, "empty"),
        ("1000\n", 0, "decimal"),
        ("0\n", 7, "decimal"),
        ("0\n", False, "decimal"),
        ("0\n", "0", "decimal"),
        ("0\n0\n", 0, "other"),
        ("\x1b[0m0\n", 0, "other"),
    ],
)
def test_identity_rejects_output_contamination_before_any_setup(output, exit_code, shape):
    from workbench.capability_isolation import CONTROL_SHELL_ENV, prepare_identity

    calls = []

    def execute(command, *, env, timeout):
        calls.append((command, env, timeout))
        assert len(calls) == 1, "No setup or application command after failed identity"
        assert shlex.split(command)[-2:] == ["/usr/bin/id", "-u"]
        assert env == CONTROL_SHELL_ENV and timeout == 10
        return SimpleNamespace(result=output, exit_code=exit_code)

    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    with pytest.raises(IsolationUnavailable) as caught:
        prepare_identity(sandbox, object(), 10)
    evidence = caught.value.evidence
    assert evidence["control_output_shape"] == shape
    assert evidence["control_result_chars"] == (len(output) if isinstance(output, str) else None)
    assert "private-sentinel" not in json.dumps(evidence)
    assert set(evidence) == {
        "control_exec_exit_code",
        "control_euid",
        "control_result_type",
        "control_result_chars",
        "control_output_shape",
    }
    assert len(calls) == 1


def test_exact_root_identity_progresses_to_setup_without_weaker_parsing():
    from workbench.capability_isolation import prepare_identity

    calls = []

    def execute(command, *, env, timeout):
        calls.append(shlex.split(command))
        return SimpleNamespace(
            result="0\n" if len(calls) == 1 else "", exit_code=0 if len(calls) == 1 else 1
        )

    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    with pytest.raises(IsolationUnavailable, match="无法建立"):
        prepare_identity(sandbox, object(), 10)
    assert len(calls) == 2
    assert "/usr/sbin/groupadd" in calls[1]


@pytest.mark.skipif(os.name != "posix", reason="Pinned daemon shell fixture requires POSIX bash")
def test_actual_sdk_env_protocol_prevents_outer_shell_contamination(tmp_path):
    """Real SDK + subprocess protocol fixture, not the missing live CI output."""
    import httpx
    from daytona._sync.process import Process

    from workbench.capability_isolation import CONTROL_SHELL_ENV, control_exec, system_argv

    bootstrap = tmp_path / "fixture-bootstrap.sh"
    bootstrap.write_text("printf 'private-bootstrap-sentinel\\n'\n", encoding="utf-8")
    requests = []

    def execute_command(*, request, **kwargs):
        requests.append(request)
        result = subprocess.run(
            ["/bin/bash"],
            input=request.command,
            env={
                "PATH": os.defpath,
                "LC_ALL": "rnd_nonexistent_locale.UTF-8",
                "BASH_ENV": str(bootstrap),
                **(request.envs or {}),
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10,
            check=False,
        )
        return SimpleNamespace(
            result=result.stdout, exit_code=result.returncode, additional_properties={}
        )

    with httpx.Client(trust_env=False) as client:
        sdk = Process("python", SimpleNamespace(execute_command=execute_command), client)
        sandbox = SimpleNamespace(process=sdk)
        noisy = sdk.exec(shlex.join(system_argv(["/usr/bin/id", "-u"])), timeout=10)
        assert noisy.exit_code == 0
        assert "setlocale" in noisy.result and "private-bootstrap-sentinel" in noisy.result
        assert noisy.result.strip() != str(os.geteuid())
        safe = control_exec(sandbox, ["/usr/bin/id", "-u"], 10)
        assert safe.exit_code == 0 and safe.result.strip() == str(os.geteuid())
        assert requests[-1].envs == CONTROL_SHELL_ENV


@pytest.mark.parametrize("engine", ["sqlite", "postgresql"])
def test_physical_count_probe_uses_same_outer_shell_environment(engine):
    from workbench.capability_isolation import CONTROL_SHELL_ENV
    from workbench.capability_stack import database_counts

    calls = []

    def execute(command, *, env, timeout):
        calls.append(shlex.split(command))
        assert env == CONTROL_SHELL_ENV and timeout == 10
        assert calls[-1][:2] == ["/usr/bin/env", "-i"]
        return SimpleNamespace(exit_code=0, result='{"entries":7}' if engine == "sqlite" else "7\n")

    plan = SimpleNamespace(
        selection=SimpleNamespace(database=engine),
        runtime=SimpleNamespace(database_tables=["entries"], database_path="data/app.db"),
    )
    sandbox = SimpleNamespace(process=SimpleNamespace(exec=execute))
    assert database_counts(sandbox, plan, 10) == {"entries": 7}
    assert len(calls) == (1 if engine == "sqlite" else 2)
    if engine == "postgresql":
        assert "rnd_verify" in calls[0][-1]
        assert "postgres-verifier.json" in calls[0][-1]
        assert "head" in " ".join(calls[1])


@pytest.mark.parametrize("database", ["sqlite", "postgresql"])
def test_generated_prepare_and_start_cannot_bypass_identity_or_network_guard(database):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=8123), selection=SimpleNamespace(database=database)
    )
    command = ["/bin/sh", "-c", "sudo -n id; curl http://127.0.0.1:2280/process/execute"]
    result = product_argv(plan, command, {"DATABASE_URL": "synthetic-only"})
    assert result[:2] == ["/usr/bin/env", "-i"]
    assert "--reuid=rnd-module" in result and "--regid=rnd-module" in result
    session = result.index("/usr/bin/setsid")
    assert result[session : session + 4] == [
        "/usr/bin/setsid",
        "--fork",
        "--wait",
        "/usr/bin/setpriv",
    ]
    for flag in (
        "--clear-groups",
        "--no-new-privs",
        "--bounding-set=-all",
        "--inh-caps=-all",
        "--ambient-caps=-all",
    ):
        assert flag in result
    index = result.index("/usr/bin/python3")
    assert result[index : index + 6] == [
        "/usr/bin/python3",
        "-I",
        "-S",
        "/tmp/rnd-module-control/guard.py",
        "8123",
        "55432" if database == "postgresql" else "",
    ]
    assert result[-len(command) :] == command
    assert result.index("--") < index
    assert result[index + 6] == "--"


@pytest.mark.parametrize("port", [2280, 55432])
def test_product_cannot_allow_its_control_or_database_listener(port):
    plan = SimpleNamespace(
        runtime=SimpleNamespace(port=port), selection=SimpleNamespace(database="sqlite")
    )
    with pytest.raises(IsolationUnavailable):
        product_argv(plan, ["echo", "should-not-run"], {})


def test_isolation_receipt_requires_each_field_actual_abi_and_current_guard_digest():
    from workbench.capability_isolation import (
        APP_UID,
        ISOLATION_FLAGS,
        ISOLATION_PROFILE,
        require_isolation_evidence,
    )
    from workbench.filesystem import sha
    from workbench.settings import ROOT

    value = {
        "profile": ISOLATION_PROFILE,
        "application_uid": APP_UID,
        "landlock_abi": 6,
        "guard_sha256": sha(ROOT / "scripts/capability_guard.py"),
        **dict.fromkeys(ISOLATION_FLAGS, True),
    }
    assert require_isolation_evidence(value) == value
    for key in list(value):
        missing = {k: v for k, v in value.items() if k != key}
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence(missing)
    for invalid in [True, 5, "6"]:
        with pytest.raises(IsolationUnavailable):
            require_isolation_evidence({**value, "landlock_abi": invalid})
    with pytest.raises(IsolationUnavailable):
        require_isolation_evidence({**value, "guard_sha256": "0" * 64})


@pytest.mark.skipif(os.name != "posix", reason="Linux executor profile uses util-linux setsid")
@pytest.mark.parametrize("exit_code", [0, 7])
def test_detached_session_waits_for_ordinary_command_and_preserves_exit(tmp_path, exit_code):
    completed = tmp_path / "completed.txt"
    result = subprocess.run(
        [
            "/usr/bin/setsid",
            "--fork",
            "--wait",
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import pathlib,sys,time;time.sleep(0.05);pathlib.Path(sys.argv[1]).write_text('completed',encoding='utf-8');raise SystemExit(int(sys.argv[2]))",
            str(completed),
            str(exit_code),
        ],
        capture_output=True,
        timeout=5,
        start_new_session=True,
    )
    assert result.returncode == exit_code
    assert completed.read_text(encoding="utf-8") == "completed"


def test_container_receipt_requires_current_sandbox_and_all_boundaries():
    from workbench.capability_isolation import require_container_evidence

    identifier = "00000000-0000-0000-0000-000000000001"
    value = {
        "profile": "fixed-authored-sqlite-v1",
        "sandbox_id": identifier,
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
        "runner_image_id": "sha256:" + "0" * 64,
        "snapshot_image_id": "sha256:" + "1" * 64,
        "snapshot_digest": "registry:6000/rnd-python@sha256:" + "2" * 64,
    }
    assert require_container_evidence(value, identifier) == value
    for key in value:
        with pytest.raises(IsolationUnavailable):
            require_container_evidence({k: v for k, v in value.items() if k != key}, identifier)
    with pytest.raises(IsolationUnavailable):
        require_container_evidence(value, None)
    with pytest.raises(IsolationUnavailable):
        require_container_evidence({**value, "privileged": True}, identifier)


@pytest.mark.parametrize("unknown_error", [False, True])
def test_live_container_inspection_failure_stops_before_source_upload(
    settings, tmp_path, unknown_error
):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_sandbox import _verify

    product = tmp_path / "product"
    plan = fixed_application(product)
    operations = []

    def forbidden(*args, **kwargs):
        pytest.fail("No source upload or command before container policy verification")

    def observer(_):
        if unknown_error:
            error = ValueError("secret error /private/path TOKEN=must-not-leak")
            # An arbitrary provider exception cannot opt in to trusted evidence.
            error.evidence = {"container_rejection": "resource_limits", "TOKEN": "must-not-leak"}
            raise error
        return {}

    sandbox = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        fs=SimpleNamespace(create_folder=forbidden, upload_file=forbidden),
        process=SimpleNamespace(exec=forbidden),
    )
    client = SimpleNamespace(
        create=lambda *a, **k: sandbox, delete=lambda *a, **k: operations.append("deleted")
    )
    settings.daytona_snapshot = "fixture-owned-snapshot"
    result = _verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "receipt.json",
        client=client,
        aggregate=True,
        control_observer=observer,
    )
    assert result["passed"] is False and result["cleanup"] == "deleted"
    assert result["kind"] == "isolation_environment" and operations == ["deleted"]
    assert result["isolation_diagnostic"] == {}
    assert "must-not-leak" not in json.dumps(result) and "private/path" not in json.dumps(result)


BROWSER_FAILURE_FIXTURES = {
    "browser-launch": {"phase": "launch", "error_code": "operation-failed"},
    "browser-timeout": {"phase": "python-timeout", "error_code": "timeout", "cleanup": "stopped"},
    "browser-json": {
        "phase": "python-report",
        "error_code": "invalid-report",
        "report_error": "invalid-json",
    },
    "browser-head": {
        "phase": "python-report",
        "error_code": "invalid-report",
        "report_error": "wrong-verifier-or-request",
    },
    "browser-exit": {"phase": "python-exit", "error_code": "nonzero-exit", "exit_code": 1},
    "browser-cleanup": {"phase": "launch", "error_code": "operation-failed"},
}


STARTUP_FAILURE_FIXTURES = {
    "startup-status",
    "startup-connect",
    "startup-timeout",
    "startup-output-unavailable",
    "startup-probe-error",
    "startup-probe-nonzero",
    "startup-probe-malformed",
    "startup-probe-boolean",
    "startup-probe-executable",
}


@pytest.mark.parametrize(
    "failure",
    [
        None,
        "baseline",
        "initial",
        "restart-health",
        "restart",
        *BROWSER_FAILURE_FIXTURES,
        *sorted(STARTUP_FAILURE_FIXTURES),
    ],
)
@pytest.mark.parametrize("secure_execution", [False, True])
def test_verifier_closes_health_opened_http_clients_on_all_paths(
    settings, tmp_path, monkeypatch, failure, secure_execution
):
    """Real HTTPX lifecycle with transport/process fixtures, not live isolation proof."""
    import httpx

    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier
    from workbench.capability_verification import BrowserFailure, CheckFailure

    product = tmp_path / "product"
    plan = fixed_application(product)
    if failure in STARTUP_FAILURE_FIXTURES:
        plan.runtime.startup_seconds = 1
        clock = [0]
        monkeypatch.setattr(verifier.time, "monotonic", lambda: clock[0])
        monkeypatch.setattr(verifier.time, "sleep", lambda _: clock.__setitem__(0, clock[0] + 1))
    identifier = "00000000-0000-0000-0000-000000000001"
    events, clients = [], []
    original_client = httpx.Client

    def build_http(**kwargs):
        launch = len(clients)
        assert kwargs["headers"] == {"x-daytona-preview-token": "fixture-private-token"}
        assert kwargs["trust_env"] is False and kwargs["follow_redirects"] is False

        def respond(request):
            events.append((launch, request.url.path))
            assert request.url.host == f"8123-{identifier}.proxy.localhost"
            if failure == "startup-connect":
                raise httpx.ConnectError("secret transport path and token", request=request)
            if failure == "startup-timeout":
                raise httpx.ReadTimeout("secret transport path and token", request=request)
            if failure in STARTUP_FAILURE_FIXTURES:
                return httpx.Response(503)
            if failure == "restart-health" and launch == 1:
                raise RuntimeError("fixture health failure")
            return httpx.Response(200, json={"ok": True})

        client = original_client(**kwargs, transport=httpx.MockTransport(respond))
        clients.append(client)
        return client

    sandbox = SimpleNamespace(
        id=identifier,
        public=False,
        network_block_all=True,
        refresh_data=lambda: events.append("network-refreshed"),
        fs=SimpleNamespace(create_folder=lambda *a: None, upload_file=lambda *a, **k: None),
        process=SimpleNamespace(
            create_session=lambda *a: None,
            execute_session_command=lambda *a, **k: SimpleNamespace(cmd_id="fixture-command"),
        ),
        get_preview_link=lambda port: SimpleNamespace(
            url=f"http://{port}-{identifier}.proxy.localhost", token="fixture-private-token"
        ),
    )

    def delete(*args, **kwargs):
        events.append("deleted")
        if failure == "browser-cleanup":
            raise RuntimeError("fixture sandbox cleanup failure")

    def create(parameters, **kwargs):
        # Reproduce the pinned SDK's actual delete-on-stop parameter semantics.
        # An aggregate sandbox must survive both bounded lifecycle operations;
        # the ordinary disposable verifier policy must remain zero.
        from workbench.sandbox import params_for

        ordinary = params_for(settings, "fixture-ordinary")
        assert ordinary.auto_delete_interval == 0
        assert parameters.auto_delete_interval > (2 * settings.tool_timeout) / 60
        assert parameters.network_block_all is True
        assert parameters.public is False
        assert parameters.name.startswith("rnd-source-" if secure_execution else "rnd-capability-")
        sandbox.auto_delete_interval = parameters.auto_delete_interval
        return sandbox

    def stop(*args, **kwargs):
        assert sandbox.auto_delete_interval > 0, "Zero deletes the sandbox before restart"
        events.append("stopped")

    daytona = SimpleNamespace(
        create=create,
        stop=stop,
        start=lambda *a, **k: events.append("started"),
        delete=delete,
    )
    counts = iter([0, 1, 1])

    def database_counts(*args):
        if failure == "baseline":
            raise CheckFailure("fixture baseline failure")
        return {"entries": next(counts)}

    def run_scenarios(http, scenarios, *, saved=None, after_restart=False):
        phase = "restart" if after_restart else "initial"
        assert http.get("/fixture-" + phase).status_code == 200
        if failure == phase:
            raise CheckFailure("fixture scenario failure")
        return [{"phase": phase, "fixture_only": True}], {}

    def run_browser(*args):
        if failure in BROWSER_FAILURE_FIXTURES:
            raise BrowserFailure(BROWSER_FAILURE_FIXTURES[failure].copy())
        return [{"fixture_only": True}]

    monkeypatch.setattr(verifier, "require_container_evidence", lambda *a: {"fixture_only": True})
    monkeypatch.setattr(verifier, "prepare_identity", lambda *a: {"fixture_only": True})

    def control(sandbox, argv, timeout):
        if "os.statvfs('/tmp')" in argv[-1]:
            assert timeout <= 5
            events.append("tmpfs-mode-read")
            if failure == "startup-probe-error":
                raise RuntimeError("secret probe failure")
            return SimpleNamespace(
                exit_code=1
                if failure == "startup-probe-nonzero"
                else False
                if failure == "startup-probe-boolean"
                else 0,
                result="secret"
                if failure == "startup-probe-malformed"
                else "0\n"
                if failure == "startup-probe-executable"
                else "1\n",
            )
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(verifier, "control_exec", control)

    def startup_output(sandbox, path, timeout):
        assert path.startswith("/tmp/rnd-module-control/private/")
        assert timeout <= 5
        events.append("startup-output-read")
        if failure == "startup-output-unavailable":
            raise RuntimeError("secret private log path")
        return "PermissionError: secret path, content and fixture-private-token"

    monkeypatch.setattr(verifier, "read_command_output", startup_output)
    monkeypatch.setattr(verifier, "database_counts", database_counts)
    monkeypatch.setattr(verifier, "run_scenarios", run_scenarios)

    def fixed_browser(*args):
        assert not secure_execution, "Custom source must never fall back to host Chromium"
        return run_browser(*args)

    def isolated_browser(*args, image):
        assert secure_execution
        assert image == settings.capability_browser_image
        events.append("isolated-browser")
        return run_browser(*args)

    monkeypatch.setattr(verifier, "run_browser", fixed_browser)
    monkeypatch.setattr(
        "workbench.capability_browser_isolation.run_isolated_browser", isolated_browser
    )
    monkeypatch.setattr(verifier.httpx, "Client", build_http)
    monkeypatch.setattr(
        "workbench.daytona_sessions.run_session_command",
        lambda *a, **k: SimpleNamespace(exit_code=0),
    )
    settings.daytona_snapshot = "fixture-owned-snapshot"

    def security_probe(*args):
        events.append("security-probed")
        return {"fixture_only": True}

    try:
        result = verifier._verify(
            product,
            plan,
            plan.scenarios,
            settings,
            plan.selection.model_dump(),
            tmp_path / "receipt.json",
            client=daytona,
            aggregate=True,
            control_observer=lambda _: {},
            security_probe=security_probe if secure_execution else None,
        )
        assert result["passed"] is (failure is None)
        assert result["restarted"] is (failure is None)
        assert result["cleanup"] == ("delete-failed" if failure == "browser-cleanup" else "deleted")
        assert events[-1] == "deleted"
        assert len(clients) == (
            1
            if failure
            in {"baseline", "initial", *BROWSER_FAILURE_FIXTURES, *STARTUP_FAILURE_FIXTURES}
            else 2
        )
        assert all(client.is_closed for client in clients)
        assert (0, "/health") in events
        persisted = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
        assert persisted == result
        if failure in STARTUP_FAILURE_FIXTURES:
            diagnostic = persisted["startup_diagnostic"]
            assert diagnostic["phase"] == "health_deadline"
            assert diagnostic["http_error"] == (
                "connect"
                if failure == "startup-connect"
                else "timeout"
                if failure == "startup-timeout"
                else "none"
            )
            assert diagnostic["http_status"] == (
                None if failure in {"startup-connect", "startup-timeout"} else 503
            )
            assert diagnostic["output_hints"] == (
                [] if failure == "startup-output-unavailable" else ["permission-denied"]
            )
            assert events.count("startup-output-read") == 1
            assert events.count("tmpfs-mode-read") == 1
            assert diagnostic["tmpfs_noexec"] is (
                False
                if failure == "startup-probe-executable"
                else None
                if failure.startswith("startup-probe-")
                else True
            )
            assert "secret" not in json.dumps(persisted)
            assert "fixture-private-token" not in json.dumps(persisted)
        else:
            assert "startup-output-read" not in events and "tmpfs-mode-read" not in events
            assert "startup_diagnostic" not in persisted
        if failure in BROWSER_FAILURE_FIXTURES:
            assert persisted["browser_diagnostic"] == BROWSER_FAILURE_FIXTURES[failure]
            assert "fixture-private-token" not in json.dumps(persisted)
            if failure == "browser-cleanup":
                assert persisted["error"] == "真实浏览器场景未通过；查看安全阶段诊断，未跳过"
                assert "删除未确认" in persisted["cleanup_error"]
        if failure is None:
            assert result["restart_kind"] == (
                "application_process" if secure_execution else "container"
            )
            if secure_execution:
                assert "stopped" not in events and "started" not in events
                assert events.count("security-probed") == 2
                assert result["restart_security_checks"] == result["security_checks"]
            else:
                assert "stopped" in events and "started" in events
            assert [check["phase"] for check in result["checks"]] == ["initial", "restart"]
            assert (0, "/openapi.json") in events
            assert (0, "/fixture-initial") in events and (1, "/fixture-restart") in events
            assert result["database"]["after_restart"] == {"entries": 1}
    finally:
        for client in clients:
            client.close()


def test_nonaggregate_verifier_keeps_delete_on_stop_and_mandatory_cleanup(settings, tmp_path):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_sandbox import _verify

    product = tmp_path / "product"
    plan = fixed_application(product)
    settings.daytona_snapshot = "fixture-owned-snapshot"
    sandbox = SimpleNamespace(id="00000000-0000-0000-0000-000000000001")
    calls = []

    def create(parameters, **kwargs):
        assert parameters.auto_delete_interval == 0
        assert parameters.network_block_all is True and parameters.public is False
        calls.append("created")
        return sandbox

    client = SimpleNamespace(create=create, delete=lambda *a, **k: calls.append("deleted"))
    result = _verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        tmp_path / "receipt.json",
        client=client,
        aggregate=False,
        # Deliberately reject before source upload; this is a lifecycle contract
        # regression and supplies no live container or application evidence.
        control_observer=lambda identifier: {},
    )
    assert calls == ["created", "deleted"]
    assert result["passed"] is False
    assert result["cleanup"] == "deleted"
