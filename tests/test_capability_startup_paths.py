"""Finite metadata from real owned launch fixtures, without candidate execution."""

import ast
import copy
import json
import os
import shlex
import shutil
import stat
import struct
import subprocess
from types import SimpleNamespace

import pytest

from workbench import capability_startup_paths as diagnostic


def helpers(loader):
    tree = ast.parse(diagnostic.PROBE)
    functions = ast.Module([node for node in tree.body if isinstance(node, ast.FunctionDef)], [])
    # Pure regular-file ELF parsing remains covered on Windows. Only this test
    # adapter supplies zero for an absent nonblocking flag; real FIFO handling
    # is separately POSIX-only and the production Linux probe is unchanged.
    probe_os = SimpleNamespace(**vars(os))
    probe_os.O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
    scope = {"os": probe_os, "stat": stat, "struct": struct, "paths": {"elf_loader": str(loader)}}
    exec(compile(functions, "trusted-probe-functions", "exec"), scope)
    return scope


def elf(loader=b"/lib64/ld-linux-x86-64.so.2\0"):
    data = bytearray(256)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", data, 32, 64)
    struct.pack_into("<HH", data, 54, 56, 1)
    struct.pack_into("<I", data, 64, 3)
    struct.pack_into("<Q", data, 72, 128)
    struct.pack_into("<Q", data, 96, len(loader))
    data[128 : 128 + len(loader)] = loader
    return data


def test_missing_regular_directory_and_dangling_link(tmp_path):
    scope = helpers(tmp_path / "loader")
    inspect = scope["inspect"]
    path = tmp_path / "private-sentinel"
    assert inspect(str(path))["entry"] == "missing"
    path.write_bytes(b"inert")
    assert inspect(str(path))["target"] == "regular"
    assert inspect(str(tmp_path))["target"] == "directory"
    link = tmp_path / "link"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("Creating symlinks requires platform support")
    assert inspect(str(link))["entry"] == "symlink"
    assert inspect(str(link))["target"] == "regular"
    path.unlink()
    value = inspect(str(link))
    assert value["entry"] == "symlink" and value["target"] == "missing"
    assert "private-sentinel" not in json.dumps(value)


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits and directory traversal")
def test_app_dac_does_not_use_root_access(tmp_path):
    # All existing ancestors have to permit UID 20000 traversal too.
    base = tmp_path / "directory"
    base.mkdir(mode=0o755)
    file = base / "program"
    file.write_bytes(b"inert")
    file.chmod(0o000)
    result = helpers(base / "loader")["inspect"](str(file))
    assert result["dac_read"] is False and result["dac_exec"] is False
    assert file.read_bytes() == b"inert" if os.geteuid() == 0 else True


@pytest.mark.parametrize("present", [True, False])
def test_real_elf_header_reports_only_fixed_loader_state(tmp_path, present):
    loader = tmp_path / "loader"
    if present:
        loader.write_bytes(b"inert")
    program = tmp_path / "program"
    program.write_bytes(elf())
    result = helpers(loader)["executable_format"](str(program))
    assert result == {"format": "elf", "loader": "present" if present else "missing"}


@pytest.mark.parametrize(
    "data,kind,loader",
    [
        (b"#!/private/secret\n", "script", "unknown"),
        (b"private-sentinel", "other", "unknown"),
        (elf(b"/private/secret\0"), "elf", "unexpected"),
        (b"\x7fELF", "elf", "unknown"),
    ],
)
def test_unknown_binary_and_shebang_never_expose_content(tmp_path, data, kind, loader):
    program = tmp_path / "program"
    program.write_bytes(data)
    result = helpers(tmp_path / "loader")["executable_format"](str(program))
    assert result == {"format": kind, "loader": loader}
    assert "private" not in json.dumps(result)


def test_elf_program_header_outside_read_budget_is_unknown(tmp_path):
    program = tmp_path / "program"
    data = elf() + bytearray(70000)
    struct.pack_into("<Q", data, 72, 66000)
    program.write_bytes(data)
    assert helpers(tmp_path / "loader")["executable_format"](str(program)) == {
        "format": "elf",
        "loader": "unknown",
    }


@pytest.mark.skipif(os.name != "posix", reason="Actual FIFO requires POSIX nonblocking open")
def test_fifo_is_never_read_and_descriptor_is_closed(tmp_path):
    fifo = tmp_path / "owned-fifo"
    os.mkfifo(fifo)
    scope = helpers(tmp_path / "loader")
    descriptors = []
    opened = scope["os"].open

    def open_fd(*args):
        fd = opened(*args)
        descriptors.append(fd)
        return fd

    scope["os"].open = open_fd
    scope["os"].read = lambda *a: pytest.fail("Non-regular contents must not be read")
    assert scope["executable_format"](str(fifo)) == {"format": "unknown", "loader": "unknown"}
    assert len(descriptors) == 1
    with pytest.raises(OSError):
        os.fstat(descriptors[0])


def receipt():
    return {
        "paths": {
            name: {"entry": "regular", "target": "regular", "dac_read": True, "dac_exec": False}
            for name in diagnostic.PATH_ROLES
        },
        "native_binary": {"format": "elf", "loader": "present"},
    }


def test_controller_requests_only_fixed_program_and_bounds_output(monkeypatch):
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append((argv, timeout))
        return SimpleNamespace(exit_code=0, result=json.dumps(receipt()))

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "observed", **receipt()}
    assert calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.PROBE], 5)]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(secret="private-sentinel"),
        lambda d: d["paths"].pop("native_python"),
        lambda d: d["paths"].update(secret=d["paths"]["env"]),
        lambda d: d["paths"]["env"].update(entry="private-sentinel"),
        lambda d: d["paths"]["env"].update(dac_read=1),
        lambda d: d["paths"]["env"].update(dac_exec="true"),
        lambda d: d["native_binary"].update(loader="private-sentinel"),
        lambda d: d.update(native_binary=[]),
    ],
)
def test_malformed_receipt_is_unknown(monkeypatch, mutate):
    value = copy.deepcopy(receipt())
    mutate(value)
    monkeypatch.setattr(
        diagnostic,
        "control_exec",
        lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(value)),
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "code,output", [(False, "{}"), (1, "private-sentinel"), (0, "x" * 2049), (0, "{"), (0, None)]
)
def test_failed_or_oversize_probe_never_serializes_output(monkeypatch, code, output):
    monkeypatch.setattr(
        diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code, result=output)
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("/usr/bin/env: '/private/secret': No such file or directory", ["env-launcher"]),
        ("/bin/sh: 1: cd: can't cd to /private/secret", ["shell-launcher"]),
        (
            "/private/secret: error while loading shared libraries: private.so: cannot open shared object file: No such file or directory",
            ["elf-loader", "shared-library-open"],
        ),
        (
            "2026-10-05 08:00:00.001 | ERROR    | app.core.discover:_build:44 - private-sentinel",
            ["vendor-loguru"],
        ),
        (
            "\x1b[31mFileNotFoundError: private-sentinel\x1b[0m",
            ["file-not-found-type", "ansi-control"],
        ),
        ("private-sentinel", []),
        (None, []),
    ],
)
def test_output_format_classification_never_copies_content(text, expected):
    assert diagnostic.output_shapes(text) == expected
    assert diagnostic.output_shapes("x" * 8000 + (text or "")) == []


def native_plan():
    return SimpleNamespace(
        selection=SimpleNamespace(template="fastapiadmin", database="postgresql"),
        runtime=SimpleNamespace(port=8123),
    )


def smoke_checks():
    return dict.fromkeys(("version_matches", "executable_matches", "cwd_matches", "isolated"), True)


def test_smoke_uses_original_guard_and_env_with_shared_five_second_budget(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    plan = native_plan()
    database = {"DATABASE_PASSWORD": "private-sentinel"}
    identity = {"native_semaphore_storage": True}
    expected = diagnostic.product_argv(
        plan,
        [
            "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python",
            "-I",
            "-S",
            "-c",
            diagnostic.SMOKE,
        ],
        database,
        **identity,
    )

    def execute(sandbox, argv, timeout):
        assert timeout == 5
        assert argv[:2] == ["/bin/sh", "-c"]
        assert argv[2].startswith("cd /tmp/rnd-capability/product/backend && ")
        inner = shlex.split(argv[2].split(" && ", 1)[1])
        assert inner[:2] == ["/bin/sh", "-c"]
        launcher = shlex.split(inner[2].split(" </dev/null ", 1)[0])
        assert launcher == ["exec", *expected]
        assert "--native-shm" in launcher and "--reuid=rnd-module" in launcher
        clock[0] = 4
        return SimpleNamespace(exit_code=0)

    def read(sandbox, path, timeout, limit, tail):
        assert timeout == 1 and limit == 512 and tail is True
        assert path.startswith("/tmp/rnd-module-control/private/")
        return json.dumps(smoke_checks())

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(diagnostic, "read_command_output", read)
    result = diagnostic.native_startup_smoke(object(), plan, database, identity, 99)
    assert result == {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "code,output,expected",
    [
        (127, "/usr/bin/env: private-sentinel: No such file or directory", "nonzero"),
        (0, '{"version_matches":true,"version_matches":false}', "zero"),
        (False, "private-sentinel", "unknown"),
        (0, "private-sentinel", "zero"),
        (0, "x" * 513, "zero"),
        (0, json.dumps({**smoke_checks(), "isolated": 1}), "zero"),
        (0, json.dumps({**smoke_checks(), "secret": "private-sentinel"}), "zero"),
    ],
)
def test_smoke_failure_and_corrupt_output_are_finite(monkeypatch, code, output, expected):
    monkeypatch.setattr(diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code))
    monkeypatch.setattr(diagnostic, "read_command_output", lambda *a, **k: output)
    result = diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    )
    assert result["exit_status"] == expected and result["checks"] is None
    assert "private-sentinel" not in json.dumps(result)


def test_smoke_timeout_keeps_unknown_and_does_not_start_another_read(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])

    def execute(*args):
        clock[0] = 5.1
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(
        diagnostic, "read_command_output", lambda *a, **k: pytest.fail("Deadline exceeded")
    )
    assert diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    ) == {"exit_status": "zero", "output_shapes": [], "checks": None}


def test_all_native_diagnostic_reads_fit_existing_byte_budget():
    assert (
        diagnostic.NATIVE_TAIL_LIMIT + diagnostic.PATH_OUTPUT_LIMIT + diagnostic.SMOKE_OUTPUT_LIMIT
        == 8000
    )
    assert len(json.dumps(receipt()).encode()) < diagnostic.PATH_OUTPUT_LIMIT


@pytest.mark.parametrize("probe", ["metadata", "smoke"])
@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("role", ["backend", "frontend"])
def test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline(
    monkeypatch, probe, fail, role
):
    import httpx
    from daytona._sync.process import Process

    from workbench.daytona_sessions import _DEADLINE, harden_toolbox_transport

    clock = [10.0]
    expected_checks = smoke_checks()
    expected_paths = receipt()
    if role == "frontend":
        expected_checks["no_preload"] = expected_checks.pop("isolated")
        expected_paths["paths"] = {
            key: next(iter(expected_paths["paths"].values())) for key in diagnostic.NODE_PATH_ROLES
        }
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    requests, transports = [], []
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda method, url, **kwargs: transports.append(kwargs["_request_timeout"]),
    )
    harden_toolbox_transport(SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest)))

    def execute_command(*, request, **kwargs):
        requests.append(request)
        assert type(request.timeout) is int and 1 <= request.timeout <= 5
        assert _DEADLINE.get() == 15
        clock[0] += 1.25
        # Exercise the actual SDK-selected larger HTTP budget through the real
        # hardened transport. The absolute deadline must win over that budget.
        rest.request("POST", "https://owned.invalid", **kwargs)
        assert 0 < transports[-1] <= 15 - clock[0]
        if fail:
            raise RuntimeError("private-sentinel")
        value = expected_paths if probe == "metadata" else expected_checks
        return SimpleNamespace(result=json.dumps(value), exit_code=0, additional_properties={})

    outer = _DEADLINE.set(999.0)
    try:
        with httpx.Client(trust_env=False) as client:
            sandbox = SimpleNamespace(
                process=Process("python", SimpleNamespace(execute_command=execute_command), client)
            )
            result = (
                diagnostic.native_startup_paths(sandbox, 5, role=role)
                if probe == "metadata"
                else diagnostic.native_startup_smoke(
                    sandbox, native_plan(), {}, {"native_semaphore_storage": True}, 5, role=role
                )
            )
        assert len(requests) == (1 if probe == "metadata" or fail else 2)
        assert len(transports) == len(requests)
        assert _DEADLINE.get() == 999.0
        if probe == "metadata":
            assert result["status"] == ("unknown" if fail else "observed")
        else:
            assert result["checks"] == (None if fail else expected_checks)
        assert "private-sentinel" not in json.dumps(result)
    finally:
        _DEADLINE.reset(outer)


@pytest.mark.parametrize("failure", [None, "paths", "smoke"])
@pytest.mark.parametrize("native", [False, True])
def test_actual_start_keeps_health_failure_and_closes_http(monkeypatch, failure, native):
    import uuid
    from pathlib import Path

    from daytona import SessionExecuteRequest
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_dependencies import readonly_start_command
    from workbench.capability_sandbox import startup_failure_diagnostic
    from workbench.capability_verification import CheckFailure

    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    start = next(
        n
        for n in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
        if isinstance(n, ast.FunctionDef) and n.name == "start"
    )
    events = []
    plan = complete_native_plan()
    plan.obligations = []  # Authored native diagnostic fixture, not atomic SQLite acceptance.
    clock = iter((0, plan.runtime.startup_seconds + 1))
    client = SimpleNamespace(close=lambda: events.append("closed"))

    def paths(*args, role):
        assert role == "backend"
        events.append("paths")
        if failure == "paths":
            raise RuntimeError("private-sentinel")
        return {"status": "observed", **receipt()}

    def smoke(*args, role):
        assert role == "backend"
        events.append("smoke")
        if failure == "smoke":
            raise RuntimeError("private-sentinel")
        return {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}

    monkeypatch.setattr(diagnostic, "native_startup_paths", paths)
    monkeypatch.setattr(diagnostic, "native_startup_smoke", smoke)

    output_limit = diagnostic.NATIVE_TAIL_LIMIT if native else 8000
    output = "/usr/bin/env: private-sentinel: No such file or directory".ljust(output_limit)

    def read(*args, limit, tail):
        assert limit == output_limit and tail is True
        events.append("tail")
        return output

    state = {}
    process = SimpleNamespace(
        create_session=lambda *a: None,
        execute_session_command=lambda *a, **k: SimpleNamespace(cmd_id="owned"),
    )
    scope = {
        "readonly_start_command": readonly_start_command,
        "consumer": None,  # Native/legacy diagnostic fixture has no consumer launcher contract.
        "require_preinstalled_evidence": lambda *a, **k: None,
        "verify_readonly_dependencies": lambda *a, **k: {},
        "dependency_profile": {},
        "before": {},
        "receipt": {"source_digest": "bound"},
        "plan": plan,
        "settings": SimpleNamespace(tool_timeout=20),
        "sandbox": SimpleNamespace(
            id="owned",
            process=process,
            get_preview_link=lambda *a: SimpleNamespace(url="owned", token="private-sentinel"),
        ),
        "uuid": uuid,
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "product_argv": diagnostic.product_argv,
        "redirected_command": diagnostic.redirected_command,
        "SessionExecuteRequest": SessionExecuteRequest,
        "REMOTE": "/tmp/rnd-capability",
        "shlex": shlex,
        "preview_url": lambda *a: "http://owned.invalid",
        "httpx": SimpleNamespace(Client=lambda **k: client),
        "time": SimpleNamespace(monotonic=lambda: next(clock)),
        "read_command_output": read,
        "control_exec": lambda *a: SimpleNamespace(exit_code=0, result="1"),
        "startup_failure_diagnostic": startup_failure_diagnostic,
        "startup_command_exit_facts": lambda *a: {
            "command_exit_status": "nonzero",
            "command_exit_code": 2,
        },
        "native": native,
        "CheckFailure": CheckFailure,
    }
    exec(compile(ast.Module([start], []), "actual-start-function", "exec"), scope)
    with pytest.raises(CheckFailure, match="健康检查"):
        scope["start"]()
    state = scope["receipt"]["startup_diagnostic"]
    assert events == (["tail", "paths", "smoke", "closed"] if native else ["tail", "closed"])
    assert state["command_exit_status"] == "nonzero"
    assert state["command_exit_code"] == 2
    assert state["output_raw_bytes"] == output_limit
    assert state["output_read_limit_reached"] is True
    if native:
        assert state["launch_paths"]["status"] == ("unknown" if failure == "paths" else "observed")
        assert state["interpreter_probe"]["exit_status"] == (
            "unknown" if failure == "smoke" else "zero"
        )
    else:
        assert "launch_paths" not in state and "interpreter_probe" not in state
    assert "private-sentinel" not in json.dumps(state)


@pytest.mark.parametrize("role", ["backend", "frontend"])
def test_startup_target_binds_registered_original_command(role):
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import frontend_start_command

    plan = complete_native_plan()
    plan.obligations = []  # Authored native diagnostic fixture, not atomic SQLite acceptance.
    original = frontend_start_command() if role == "frontend" else plan.runtime.start
    command, target = diagnostic.startup_target(plan, original)
    assert target == {
        "role": role,
        "interpreter": "node" if role == "frontend" else "python",
        "port": 5173 if role == "frontend" else plan.runtime.port,
        "health_endpoint": "frontend-root" if role == "frontend" else "plan-health",
        "registered_command_bound": True,
    }
    assert command.argv[0] == (
        "/usr/local/bin/node"
        if role == "frontend"
        else "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python"
    )
    assert plan.runtime.health_path not in json.dumps(target)


@pytest.mark.parametrize(
    "frontend,port,health",
    [
        (False, 5173, None),
        (False, True, None),
        (False, 0, None),
        (False, None, "/"),
        (True, 8001, None),
        (True, None, "/openapi.json"),
        (True, "5173", "/"),
    ],
)
def test_startup_target_rejects_role_port_or_endpoint_mismatch(frontend, port, health):
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import frontend_start_command
    from workbench.capability_verification import CheckFailure

    with pytest.raises(CheckFailure):
        diagnostic.startup_target(
            complete_native_plan(), frontend_start_command() if frontend else None, port, health
        )


def test_startup_target_rejects_unregistered_command():
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_contracts import TaskCommand
    from workbench.capability_verification import CheckFailure

    with pytest.raises(CheckFailure):
        diagnostic.startup_target(
            complete_native_plan(), TaskCommand(cwd="frontend/web", argv=["node", "private.js"])
        )


def test_frontend_paths_read_only_fixed_node_and_vite_metadata(monkeypatch):
    value = receipt()
    value["paths"] = {
        key: next(iter(value["paths"].values())) for key in diagnostic.NODE_PATH_ROLES
    }
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append((argv, timeout))
        return SimpleNamespace(exit_code=0, result=json.dumps(value))

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    assert diagnostic.native_startup_paths(object(), 5, role="frontend") == {
        "status": "observed",
        **value,
    }
    assert calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.NODE_PROBE], 5)]
    assert {"native_node", "vite_entry", "frontend", "dist_index", "preview_launcher"} <= set(
        value["paths"]
    )
    assert {"native_python", "backend", "app"}.isdisjoint(value["paths"])
    assert len(json.dumps(value).encode()) < diagnostic.PATH_OUTPUT_LIMIT
    # A Python receipt cannot be presented as frontend metadata.
    monkeypatch.setattr(
        diagnostic,
        "control_exec",
        lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(receipt())),
    )
    assert diagnostic.native_startup_paths(object(), 5, role="frontend") == {"status": "unknown"}


def test_frontend_smoke_uses_same_guard_identity_environment_and_frontend_cwd(monkeypatch):
    plan = native_plan()
    database = {
        "DATABASE_PASSWORD": "private-sentinel",
        "NODE_OPTIONS": "--max-old-space-size=3072",
    }
    identity = {"native_semaphore_storage": True}
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    expected = diagnostic.product_argv(
        plan,
        ["/usr/local/bin/node", "--input-type=module", "--eval", diagnostic.NODE_SMOKE],
        database,
        **identity,
    )
    checks = {
        "version_matches": True,
        "executable_matches": True,
        "cwd_matches": True,
        "no_preload": True,
    }

    def execute(sandbox, argv, timeout):
        assert timeout == 5
        assert argv[:2] == ["/bin/sh", "-c"]
        assert argv[2].startswith("cd /tmp/rnd-capability/product/frontend/web && ")
        inner = shlex.split(argv[2].split(" && ", 1)[1])
        launcher = shlex.split(inner[2].split(" </dev/null ", 1)[0])
        assert launcher == ["exec", *expected]
        clock[0] = 4
        return SimpleNamespace(exit_code=0)

    def read(sandbox, path, timeout, limit, tail):
        assert timeout == 1 and limit == 512 and tail is True
        return json.dumps(checks)

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(diagnostic, "read_command_output", read)
    result = diagnostic.native_startup_smoke(
        object(), plan, database, identity, 99, role="frontend"
    )
    assert result == {"exit_status": "zero", "output_shapes": [], "checks": checks}
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned smoke fixture"
)
@pytest.mark.parametrize(
    "node_options,expected",
    [(None, True), ("--max-old-space-size=3072", True), ("--stack-trace-limit=2", False)],
)
def test_source_free_node_smoke_runs_as_owned_fixture(tmp_path, node_options, expected):
    environment = {
        key: value for key, value in os.environ.items() if key not in {"NODE_OPTIONS", "NODE_PATH"}
    }
    if node_options is not None:
        environment["NODE_OPTIONS"] = node_options
    result = subprocess.run(
        [shutil.which("node"), "--input-type=module", "--eval", diagnostic.NODE_SMOKE],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        env=environment,
    )
    assert result.returncode == 0 and result.stderr == ""
    value = json.loads(result.stdout)
    assert set(value) == {"version_matches", "executable_matches", "cwd_matches", "no_preload"}
    assert all(type(item) is bool for item in value.values())
    assert value["no_preload"] is expected and value["cwd_matches"] is False
    assert len(result.stdout.encode()) < diagnostic.SMOKE_OUTPUT_LIMIT


@pytest.mark.parametrize("role", [None, [], {}, True, "private-sentinel"])
def test_invalid_probe_roles_do_not_execute(monkeypatch, role):
    monkeypatch.setattr(
        diagnostic, "control_exec", lambda *a: pytest.fail("Unknown target executed")
    )
    assert diagnostic.native_startup_paths(object(), 5, role=role) == {"status": "unknown"}
    assert (
        diagnostic.native_startup_smoke(object(), native_plan(), {}, {}, 5, role=role)["checks"]
        is None
    )


@pytest.mark.parametrize("failed_role", ["backend", "frontend"])
@pytest.mark.parametrize("status", [1, None, True, "1", -1, 256, "wrong-command", "missing"])
@pytest.mark.parametrize("phase", ["initial", "restart"])
def test_actual_sequential_start_binds_failed_target_and_closes_both_clients(
    monkeypatch, failed_role, status, phase
):
    from contextlib import closing, contextmanager
    from pathlib import Path

    from daytona import SessionExecuteRequest
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import FRONTEND_PORT, frontend_start_command
    from workbench.capability_sandbox import startup_command_exit_facts, startup_failure_diagnostic
    from workbench.capability_verification import CheckFailure

    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    tree = ast.parse(source.read_text())
    outer = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Try)
        and any(isinstance(child, ast.FunctionDef) and child.name == "start" for child in n.body)
    )
    first = next(
        i for i, n in enumerate(outer.body) if isinstance(n, ast.FunctionDef) and n.name == "start"
    )
    last = next(i for i in range(first, len(outer.body)) if isinstance(outer.body[i], ast.With))
    body = outer.body[first : last + 1]
    if phase == "restart":
        parent = next(
            n
            for n in ast.walk(outer)
            if isinstance(n, ast.If)
            and any(
                isinstance(child, ast.Assign)
                and isinstance(child.targets[0], ast.Tuple)
                and [item.id for item in child.targets[0].elts if isinstance(item, ast.Name)]
                == ["http", "_", "_"]
                for child in n.body
            )
        )
        begin = next(
            i
            for i, child in enumerate(parent.body)
            if isinstance(child, ast.Assign)
            and isinstance(child.targets[0], ast.Tuple)
            and [item.id for item in child.targets[0].elts if isinstance(item, ast.Name)]
            == ["http", "_", "_"]
        )
        finish = next(
            i for i in range(begin, len(parent.body)) if isinstance(parent.body[i], ast.With)
        )
        body = [outer.body[first], *parent.body[begin : finish + 1]]
    tested = ast.Try(body=body, handlers=[], orelse=[], finalbody=outer.finalbody)
    plan = complete_native_plan()
    plan.obligations = []  # Authored native diagnostic fixture, not atomic SQLite acceptance.
    plan.runtime.health_path = "/private-health-sentinel"
    events, sessions, outputs = [], {}, {}
    moments = iter(
        [0, 0, plan.runtime.startup_seconds + 1]
        if failed_role == "backend"
        else [0, 0, 0, 0, plan.runtime.startup_seconds + 1]
    )
    ids = iter(["b" * 32, "f" * 32])

    class Client:
        def __init__(self, base_url, **kwargs):
            self.role = "frontend" if base_url.endswith("5173") else "backend"

        @contextmanager
        def stream(self, method, endpoint):
            assert method == "GET"
            assert endpoint == ("/" if self.role == "frontend" else plan.runtime.health_path)
            events.append(("health", self.role, endpoint))
            yield SimpleNamespace(
                status_code=200 if self.role == "backend" and failed_role == "frontend" else 503
            )

        def close(self):
            events.append(("closed", self.role))

    def redirect(argv):
        role = "frontend" if "/usr/local/bin/node" in argv else "backend"
        command, path = diagnostic.redirected_command(argv)
        outputs[role] = path
        return command, path

    def submit(session, request, **kwargs):
        role = "frontend" if "native-preview.mjs" in request.command else "backend"
        sessions[role] = session
        return SimpleNamespace(cmd_id=role + "-owned-id")

    def command_status(session, command):
        assert session == sessions[failed_role]
        assert command == failed_role + "-owned-id"
        events.append(("status", failed_role))
        if status == "missing":
            return None
        return SimpleNamespace(
            id="another-owned-id" if status == "wrong-command" else command, exit_code=status
        )

    def read(sandbox, path, timeout, *, limit, tail):
        assert (
            path == outputs[failed_role] and limit == diagnostic.NATIVE_TAIL_LIMIT and tail is True
        )
        return "private-sentinel"

    def paths(sandbox, timeout, *, role):
        assert role == failed_role and timeout == 5
        events.append(("paths", role))
        return {"status": "unknown"}

    def smoke(sandbox, passed_plan, database, identity, timeout, *, role):
        assert role == failed_role and passed_plan is plan and timeout == 5
        events.append(("smoke", role))
        return {"exit_status": "unknown", "output_shapes": [], "checks": None}

    monkeypatch.setattr(diagnostic, "native_startup_paths", paths)
    monkeypatch.setattr(diagnostic, "native_startup_smoke", smoke)
    sandbox = SimpleNamespace(
        id="owned",
        process=SimpleNamespace(
            create_session=lambda *a: None,
            execute_session_command=submit,
            get_session_command=command_status,
        ),
        get_preview_link=lambda port: SimpleNamespace(url="private-preview", token="private-token"),
    )
    scope = {
        "require_preinstalled_evidence": lambda *a, **k: None,
        "verify_readonly_dependencies": lambda *a, **k: {},
        "dependency_profile": {},
        "before": {},
        # A previous backend observation must not survive a failed new attempt.
        "receipt": {
            "source_digest": "bound",
            "passed": False,
            "cleanup": "pending",
            "backend_health_observed": True,
        },
        "plan": plan,
        "settings": SimpleNamespace(tool_timeout=20),
        "sandbox": sandbox,
        "uuid": SimpleNamespace(uuid4=lambda: SimpleNamespace(hex=next(ids))),
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "product_argv": diagnostic.product_argv,
        "redirected_command": redirect,
        "SessionExecuteRequest": SessionExecuteRequest,
        "REMOTE": "/tmp/rnd-capability",
        "shlex": shlex,
        "preview_url": lambda url, sid, port: "https://owned.invalid/" + str(port),
        "httpx": SimpleNamespace(Client=Client),
        "time": SimpleNamespace(monotonic=lambda: next(moments), sleep=lambda *a: None),
        "read_command_output": read,
        "control_exec": lambda *a: SimpleNamespace(exit_code=0, result="1"),
        "startup_failure_diagnostic": startup_failure_diagnostic,
        "startup_command_exit_facts": startup_command_exit_facts,
        "native": True,
        "consumer": None,  # This authored native diagnostic fixture retains its native launcher.
        "FRONTEND_PORT": FRONTEND_PORT,
        "frontend_start_command": frontend_start_command,
        "CheckFailure": CheckFailure,
        "closing": closing,
        "oracle_adapter": None,
        "client": SimpleNamespace(
            delete=lambda actual, **k: events.append(("deleted", actual is sandbox))
        ),
        "write_json": lambda *a: None,
        "receipt_path": "unused",
    }
    with pytest.raises(CheckFailure, match="健康检查"):
        exec(
            compile(
                ast.fix_missing_locations(ast.Module([tested], [])),
                "actual-sequential-start-and-cleanup",
                "exec",
            ),
            scope,
        )
    state = scope["receipt"]["startup_diagnostic"]
    assert state["target"] == {
        "role": failed_role,
        "interpreter": "node" if failed_role == "frontend" else "python",
        "port": 5173 if failed_role == "frontend" else plan.runtime.port,
        "health_endpoint": "frontend-root" if failed_role == "frontend" else "plan-health",
        "registered_command_bound": True,
        "backend_health_observed": failed_role == "frontend",
    }
    assert state["command_exit_code"] == (1 if type(status) is int and status == 1 else None)
    assert events.count(("status", failed_role)) == 1
    assert ("node_error" in state) is (failed_role == "frontend")
    assert ("closed", failed_role) in events and ("closed", "backend") in events
    assert events[-1] == ("deleted", True) and scope["receipt"]["cleanup"] == "deleted"
    assert scope["receipt"]["passed"] is False
    assert "private" not in json.dumps(scope["receipt"])
    assert "owned-id" not in json.dumps(scope["receipt"])
