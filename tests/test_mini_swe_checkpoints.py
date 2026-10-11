"""Offline checkpoint control flow; fake proofs are never live acceptance evidence."""

import json
import os
import signal
import time
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace

import pytest

from scripts.sla_fixture import design
from workbench.coding import mini_swe as agent
from workbench.coding.ports import AgentTurn
from workbench.core.contracts import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest


def exercise(
    settings,
    tmp_path,
    monkeypatch,
    outcomes,
    *,
    bad_edit=None,
    repeat=False,
    changed_snapshot=False,
    cleanup_effect=lambda: None,
):
    if not agent.worker_python().is_file():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory locked Worker missing"
        pytest.skip("optional locked Worker not installed")
    plan = design().implementation
    task = plan.tasks[0]
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("# baseline\n")
    settings = settings.model_copy(update={"mini_swe_enabled": True, "max_context_chars": 20000})
    requests, checkpoints, cleaned = [], [], []
    snapshot = {}

    class Gateway:
        def complete(self, run_id, key, instruction, payload, schema):
            requests.append(deepcopy(payload))
            assert "新库初始化" in instruction
            number = len(requests)
            if number % 2 == 0 or (repeat and number > 2):
                return AgentTurn(operation="submit")
            context = payload["context"]
            files = [
                {
                    "path": name,
                    "before_sha256": context[name]["sha256"],
                    "content": f"# revision {number}\n",
                }
                for name in task.allowed_paths
            ]
            if bad_edit == "path":
                files[0]["path"] = "start.py"
            if bad_edit == "before":
                files[0]["before_sha256"] = "f" * 64
            return AgentTurn.model_validate(
                {"operation": "edit", "edits": {"explanation": "fixture", "files": files}}
            )

    class Environment:
        def write(self, edits):
            snapshot.update({e.path: e.content for e in edits.files})

        def snapshot(self, paths):
            result = dict(snapshot)
            if changed_snapshot:
                result["app.py"] += "# tampered\n"
            return result

    @contextmanager
    def environment(*args):
        try:
            yield Environment()
        finally:
            cleaned.append(True)
            cleanup_effect()

    def checkpoint(s, t, p, candidate, deadline):
        checkpoints.append((manifest(candidate), deadline))
        result = outcomes[min(len(checkpoints) - 1, len(outcomes) - 1)]
        if isinstance(result, Exception):
            raise result
        return {
            "passed": result,
            "source_digest": digest(manifest(candidate)),
            **({} if result else {"category": "application_startup"}),
        }

    monkeypatch.setattr(agent, "check_candidate", checkpoint)

    def run():
        return agent.run_agent(
            settings,
            Gateway(),
            "fixture",
            task,
            plan,
            product,
            tmp_path / "worker",
            {},
            environment_factory=environment,
        )

    return run, requests, checkpoints, cleaned, product


def test_failed_submit_repairs_current_candidate_in_same_worker(settings, tmp_path, monkeypatch):
    run, requests, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [False, True]
    )
    edits = run()
    assert len(requests) == 4 and len(checks) == 2 and cleaned == [True]
    assert requests[0]["verification_feedback"] is None
    assert requests[2]["verification_feedback"] == {
        "passed": False,
        "source_digest": digest(checks[0][0]),
        "category": "application_startup",
    }
    assert requests[2]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]
    assert checks[0][1] == checks[1][1]  # no fresh verification time window
    assert checks[0][0] != checks[1][0]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert (
        next(e for e in edits.files if e.path == "app.py").before_sha256
        == manifest(product)["app.py"]
    )
    budget = json.loads((tmp_path / "worker/agent-budget.json").read_text())
    assert budget["requests"] == 8
    with pytest.raises(UnsupportedScope, match="重置"):
        run()


def test_persistent_failure_exhausts_existing_eight_steps(settings, tmp_path, monkeypatch):
    run, requests, checks, cleaned, _ = exercise(settings, tmp_path, monkeypatch, [False])
    with pytest.raises((UnsupportedScope, ValueError)):
        run()
    assert len(requests) == 8 and len(checks) == 4 and cleaned == [True]
    assert json.loads((tmp_path / "worker/agent-budget.json").read_text())["requests"] == 16
    assert not (tmp_path / "worker/agent-result.json").exists()


@pytest.mark.parametrize(
    "failure", [TimeoutError("fixed timeout"), UnsupportedScope("cleanup unconfirmed")]
)
def test_checkpoint_failures_stop_without_model_repair(settings, tmp_path, monkeypatch, failure):
    run, requests, checks, cleaned, _ = exercise(settings, tmp_path, monkeypatch, [failure])
    with pytest.raises(type(failure)):
        run()
    assert len(requests) == 2 and len(checks) == 1 and cleaned == [True]


@pytest.mark.parametrize("bad_edit", ["path", "before"])
def test_checkpoint_never_grants_edit_authority(settings, tmp_path, monkeypatch, bad_edit):
    run, requests, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], bad_edit=bad_edit
    )
    with pytest.raises(ValueError):
        run()
    assert not checks and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"


@pytest.mark.parametrize("case", ["repeat", "snapshot"])
def test_repeated_or_changed_submissions_fail_closed(settings, tmp_path, monkeypatch, case):
    run, requests, checks, cleaned, _ = exercise(
        settings,
        tmp_path,
        monkeypatch,
        [case == "snapshot"],
        repeat=case == "repeat",
        changed_snapshot=case == "snapshot",
    )
    with pytest.raises(ValueError):
        run()
    assert len(checks) == 1 and cleaned == [True]


def bound_check_fixture(tmp_path, monkeypatch, mutate):
    from workbench import capability_sandbox as sandbox

    plan = design().implementation
    task = plan.tasks[0]
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "app.py").write_text("# fixture\n")
    # Only tests of filtering mock admission. Production uses the unchanged guards.
    monkeypatch.setattr("workbench.capability_isolation.require_container_evidence", lambda *a: {})
    monkeypatch.setattr(
        "workbench.capability_isolation.require_isolation_evidence", lambda *a, **kw: {}
    )

    def verifier(product, p, scenarios, settings, **kwargs):
        from workbench.capability_execution import VERIFIER

        proof = {
            "verifier": VERIFIER,
            "checkpoint": kwargs["checkpoint"],
            "source_digest": digest(manifest(product)),
            "plan_digest": digest(p.model_dump()),
            "scope": "node",
            "cleanup": "deleted",
            "passed": False,
            "repairable_failure": "application_startup",
            "network_block_all": True,
            "credentials_uploaded": False,
            "startup_diagnostic": {
                "message": "execute secret command",
                "path": "private-path",
                "startup_phase_hint": "lifespan",
                "command_exit_code": 3,
                "output_hints": ["private-command"],
                "exception_type": "private-exception",
            },
        }
        mutate(proof)
        return proof

    monkeypatch.setattr(sandbox, "verify_capabilities", verifier)
    return plan, task, candidate


def test_feedback_strips_instructions_unknown_fields_and_paths(settings, tmp_path, monkeypatch):
    plan, task, candidate = bound_check_fixture(tmp_path, monkeypatch, lambda p: None)
    feedback = agent.check_candidate(settings, task, plan, candidate, time.monotonic() + 40)
    assert feedback["category"] == "application_startup"
    assert feedback["startup"]["command_exit_code"] == 3
    assert not any(x in json.dumps(feedback) for x in ("secret", "private", "execute"))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.update(cleanup="delete-failed"),
        lambda p: p.update(checkpoint={**p["checkpoint"], "nonce": "stale"}),
        lambda p: p.update(checkpoint={**p["checkpoint"], "task": "other-module"}),
        lambda p: p.update(source_digest="f" * 64),
        lambda p: p.update(plan_digest="f" * 64),
        lambda p: p.update(kind="checkpoint_timeout"),
        lambda p: p.update(repairable_failure="isolation_environment"),
        lambda p: p.update(passed=True),
    ],
)
def test_untrusted_or_stale_checkpoint_cannot_finish(settings, tmp_path, monkeypatch, mutation):
    plan, task, candidate = bound_check_fixture(tmp_path, monkeypatch, mutation)
    with pytest.raises((UnsupportedScope, ValueError)):
        agent.check_candidate(settings, task, plan, candidate, time.monotonic() + 40)


@pytest.mark.skipif(
    not hasattr(signal, "SIGUSR1"), reason="checkpoint requires dedicated POSIX process"
)
def test_check_deadline_interrupts_exception_handlers_and_runs_cleanup(monkeypatch):
    from workbench import capability_sandbox as sandbox

    events = []

    def work(payload, **kwargs):
        try:
            try:
                time.sleep(1)
            except Exception:
                events.append("incorrectly-swallowed")
        finally:
            events.append("cleanup")

    monkeypatch.setattr(sandbox, "_execute_payload_inner", work)
    start = time.monotonic()
    with pytest.raises(sandbox.CheckpointExpired):
        sandbox._execute_payload({"checkpoint": {"deadline": start + 10.05}})
    assert events == ["cleanup"] and time.monotonic() - start < 1


def test_final_oracle_rejection_does_not_reopen_agent_budget(settings, store, monkeypatch):
    from workbench.flow import Workflow

    workflow = Workflow(settings, store, None)
    selected = design()
    monkeypatch.setattr(workflow, "checked_extension", lambda state: selected)
    monkeypatch.setattr(
        workflow, "extension_task", lambda state, d: selected.implementation.tasks[0]
    )
    with pytest.raises(UnsupportedScope, match="不重启"):
        workflow.extension_after_verify({"extension_candidate_passed": False})
    with pytest.raises(UnsupportedScope, match="不重启"):
        workflow.extension_after_aggregate({"extension_aggregate_passed": False})


@pytest.mark.parametrize("phase", ["check", "cleanup"])
def test_checks_and_cleanup_share_module_deadline(settings, tmp_path, monkeypatch, phase):
    clock = [1000.0]
    monkeypatch.setattr(agent, "time", SimpleNamespace(monotonic=lambda: clock[0], time=time.time))

    def expire():
        clock[0] += 181

    run, requests, checks, cleaned, _ = exercise(
        settings,
        tmp_path,
        monkeypatch,
        [True],
        cleanup_effect=expire if phase == "cleanup" else lambda: None,
    )
    if phase == "check":
        original = agent.check_candidate

        def delayed(*args):
            value = original(*args)
            expire()
            return value

        monkeypatch.setattr(agent, "check_candidate", delayed)
    with pytest.raises(UnsupportedScope):
        run()
    assert len(requests) == 2 and cleaned == [True]
    assert not (tmp_path / "worker/agent-result.json").exists()


def test_internal_success_is_not_ledger_acceptance(settings, tmp_path, monkeypatch):
    from workbench.coding.candidates import apply_candidate
    from workbench.production.candidates import ProductLedger

    run, requests, checks, cleaned, product = exercise(settings, tmp_path, monkeypatch, [True])
    edits = run()
    plan = design().implementation
    ledger = ProductLedger(tmp_path / "ledger", plan)
    ledger.baseline(product)
    candidate = tmp_path / "final"
    apply_candidate(product, edits, plan.tasks[0], plan.selection.model_dump(), candidate)
    with pytest.raises(ValueError):
        ledger.promote(
            candidate, plan.tasks[0], {"passed": False, "cleanup": "deleted"}, manifest(product)
        )
    assert ledger._load()["version"] == 0
    assert len(checks) == 1 and cleaned == [True]


@pytest.mark.parametrize("status,body,error", [(500, b"{}", True), (200, b'{"ok":false}', True)])
def test_only_completed_business_assertions_are_repairable(status, body, error):
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, run_steps

    with httpx.Client(
        base_url="http://fixture.invalid",
        transport=httpx.MockTransport(
            lambda r: httpx.Response(status, stream=httpx.ByteStream(body))
        ),
    ) as client:
        with pytest.raises(BusinessCheckFailure):
            run_steps(client, [HttpStep(path="/check", status=200, equals={"$.ok": True})], {})


def test_transport_failure_is_not_business_repair():
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, CheckFailure, run_steps

    def timeout(request):
        raise httpx.ReadTimeout("private-transport")

    with httpx.Client(
        base_url="http://fixture.invalid", transport=httpx.MockTransport(timeout)
    ) as client:
        with pytest.raises(CheckFailure) as error:
            run_steps(client, [HttpStep(path="/check", status=200)], {})
    assert not isinstance(error.value, BusinessCheckFailure)


@pytest.mark.parametrize(
    "mutation,repairable",
    [
        ({}, True),
        ({"exception_type": "PermissionError"}, False),
        ({"exception_type": "MemoryError"}, False),
        ({"output_hints": ["storage-full"]}, False),
        ({"output_hints": ["process-terminated"]}, False),
        ({"output_hints": ["memory-error"]}, False),
        ({"output_hints": ["missing-module"]}, False),
        ({"command_exit_status": "unknown"}, False),
        ({"command_exit_code": 137}, False),
        ({"command_exit_code": 143}, False),
        ({"startup_phase_hint": "unknown"}, False),
        ({"application_startup_reported": True}, False),
    ],
)
def test_real_startup_classification_never_turns_infrastructure_into_repair(mutation, repairable):
    import ast
    import inspect

    from workbench import capability_sandbox as sandbox

    tree = ast.parse(inspect.getsource(sandbox._verify))
    block = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and any(
            isinstance(child, ast.Assign)
            and any(
                isinstance(target, ast.Subscript)
                and isinstance(target.slice, ast.Constant)
                and target.slice.value == "repairable_failure"
                for target in child.targets
            )
            and isinstance(child.value, ast.Constant)
            and child.value.value == "application_startup"
            for child in node.body
        )
    )
    scope = {
        "checkpoint": {"nonce": "fixture"},
        "receipt": {},
        "startup": {
            "command_exit_status": "nonzero",
            "command_exit_code": 3,
            "startup_phase_hint": "lifespan",
            "application_startup_reported": False,
            "output_hints": [],
            "exception_type": "other",
            **mutation,
        },
    }
    exec(
        compile(ast.Module(body=[block], type_ignores=[]), "<actual-startup-classifier>", "exec"),
        scope,
    )
    assert ("repairable_failure" in scope["receipt"]) is repairable


def test_sdk_download_retains_integer_overload_with_remaining_deadline(monkeypatch):
    from scripts.sla_fixture import design
    from workbench.infrastructure.sandbox import coding

    task = design().implementation.tasks[0]
    calls = []

    def download(path, timeout):
        assert type(timeout) is int and 0 < timeout <= 12
        calls.append(timeout)
        return b"# fixture\n"

    env = coding.DaytonaFiles(
        SimpleNamespace(fs=SimpleNamespace(download_file=download)),
        task,
        120,
        time.monotonic() + 12.9,
    )
    assert set(env.snapshot(task.allowed_paths)) == set(task.allowed_paths)
    assert len(calls) == len(task.allowed_paths)
    env.deadline = time.monotonic() + 0.1
    with pytest.raises(UnsupportedScope):
        env.snapshot(task.allowed_paths)


@pytest.mark.parametrize("delete_fails", [False, True])
@pytest.mark.skipif(not hasattr(signal, "setitimer"), reason="checkpoint requires POSIX timer")
def test_actual_verifier_timeout_handler_preserves_owned_cleanup(
    tmp_path, delete_fails, monkeypatch
):
    import ast
    import inspect

    from workbench import capability_sandbox as sandbox

    timers = []

    tree = ast.parse(inspect.getsource(sandbox._verify))
    original = next(n for n in tree.body[0].body if isinstance(n, ast.Try))
    tested = ast.Try(
        body=[ast.Raise(exc=ast.Name(id="injected", ctx=ast.Load()), cause=None)],
        handlers=original.handlers,
        orelse=[],
        finalbody=original.finalbody,
    )
    deleted = []

    def delete(value, **kwargs):
        deleted.append(value.id)
        if delete_fails:
            raise RuntimeError("private cleanup text")

    def absent(identifier):
        from daytona.common.errors import DaytonaNotFoundError

        raise DaytonaNotFoundError("owned fixture absent")

    scope = {
        **vars(sandbox),
        "injected": sandbox.CheckpointExpired("fixed timeout"),
        "diagnostic_error": None,
        "oracle_adapter": None,
        "native": False,
        "checkpoint": {"nonce": "fixture", "deadline": time.monotonic() + 10},
        "checkpoint_deadline": SimpleNamespace(enter_cleanup=lambda: timers.append(True)),
        "name": "owned",
        "receipt": {
            "passed": False,
            "cleanup": "pending",
            "repairable_failure": "application_startup",
        },
        "sandbox": SimpleNamespace(id="owned"),
        "client": SimpleNamespace(delete=delete, get=absent),
        "settings": SimpleNamespace(tool_timeout=10),
        "receipt_path": tmp_path / "receipt.json",
    }
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[tested], type_ignores=[])),
            "<actual-timeout-handler>",
            "exec",
        ),
        scope,
    )
    receipt = json.loads((tmp_path / "receipt.json").read_text())
    assert deleted == ["owned"]
    assert timers == [True]
    assert receipt["kind"] == "checkpoint_timeout" and receipt["passed"] is False
    assert receipt["cleanup"] == ("delete-failed" if delete_fails else "deleted")
    assert "repairable_failure" not in receipt
    assert "private" not in json.dumps(receipt)


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="dedicated POSIX verifier")
@pytest.mark.parametrize("blocking", [False, True])
def test_real_locked_sdk_cannot_erase_checkpoint_deadline(blocking):
    """Exercise the real SDK decorator, including the old failing timer setup."""
    from importlib.metadata import version

    from daytona._utils.timeout import with_timeout

    from workbench.infrastructure.sandbox.deadline import CheckpointDeadline, CheckpointExpired
    from workbench.local_only import DAYTONA_VERSION

    assert version("daytona") == DAYTONA_VERSION

    @with_timeout()
    def sdk_call(timeout, delay=0):
        time.sleep(delay)

    previous = signal.signal(signal.SIGALRM, lambda *args: None)
    try:
        signal.setitimer(signal.ITIMER_REAL, 1)
        sdk_call(timeout=2)
        assert signal.getitimer(signal.ITIMER_REAL)[0] == 0  # real pre-fix conflict
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    events = []
    start = time.monotonic()
    with CheckpointDeadline(start + 10.15) as controller:
        with pytest.raises(CheckpointExpired):
            try:
                sdk_call(timeout=2, delay=1 if blocking else 0)
                time.sleep(1)
            except Exception:
                events.append("incorrectly-swallowed")
            finally:
                controller.enter_cleanup()
                sdk_call(timeout=1, delay=0.03)
                events.append("cleaned")
    assert events == ["cleaned"] and time.monotonic() - start < 1
    assert signal.getsignal(signal.SIGALRM) == previous


def cleanup_binding():
    plan = design().implementation
    task = plan.tasks[0]
    return (
        task,
        plan,
        {
            "task": digest(task.model_dump()),
            "plan": digest(plan.model_dump()),
            "source": "a" * 64,
            "nonce": "b" * 32,
        },
    )


@pytest.mark.parametrize("observation", ["absent", "present", "error"])
def test_deletion_requires_typed_absence_after_delete(observation):
    from daytona.common.errors import DaytonaNotFoundError

    from workbench.infrastructure.sandbox.cleanup import confirm_deleted

    seen = []

    def get(identifier):
        seen.append(identifier)
        if observation == "absent":
            raise DaytonaNotFoundError("owned fixture")
        if observation == "error":
            raise RuntimeError("private SDK details")
        return object()

    client = SimpleNamespace(delete=lambda target, timeout: seen.append("delete"), get=get)
    if observation == "absent":
        confirm_deleted(client, SimpleNamespace(id="owned"), time.monotonic() + 0.03, 1)
    else:
        with pytest.raises((RuntimeError, TimeoutError)):
            confirm_deleted(client, SimpleNamespace(id="owned"), time.monotonic() + 0.03, 1)
    assert seen[:2] == ["delete", "owned"]


@pytest.mark.parametrize("mismatch", ["name", "id"])
def test_cleanup_cannot_delete_another_task_sandbox(settings, monkeypatch, mismatch):
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    name = "rnd-source-agent-" + "b" * 32
    target = SimpleNamespace(
        name=name if mismatch == "id" else "another-task",
        id="another-id" if mismatch == "id" else "owned",
    )
    calls = []
    client = SimpleNamespace(get=lambda key: target, delete=lambda *a, **k: calls.append(True))
    monkeypatch.setattr("workbench.sandbox.client_for", lambda settings: client)
    monkeypatch.setattr("workbench.sandbox.close_client", lambda client: None)
    monkeypatch.setattr("workbench.local_only.install_loopback_guard", lambda: None)
    with pytest.raises(ValueError, match="identity"):
        cleanup.perform(
            {
                "name": name,
                "identifier": "owned",
                "binding": binding,
                "settings": {},
                "deadline": time.monotonic() + 2,
            }
        )
    assert not calls


@pytest.mark.parametrize("case", ["success", "wrong-binding", "late", "unknown-create"])
def test_cleanup_parent_is_only_terminal_receipt_writer(settings, tmp_path, monkeypatch, case):
    from workbench.infrastructure.sandbox import cleanup

    _, _, binding = cleanup_binding()
    name = "rnd-source-agent-" + "b" * 32
    path = tmp_path / "cleanup.json"

    class Process:
        returncode = 0

        def communicate(self, body, timeout):
            request = json.loads(body)
            assert request["name"] == name and request["binding"] == binding
            value = dict(binding)
            if case == "wrong-binding":
                value["source"] = "c" * 64
            return json.dumps({"binding": value, "deleted": True}).encode(), b""

        def poll(self):
            return 0

    monkeypatch.setattr(cleanup.subprocess, "Popen", lambda *a, **k: Process())
    args = (
        settings,
        name,
        None if case == "unknown-create" else "owned",
        binding,
        path,
        time.monotonic() + (-1 if case == "late" else 1),
    )
    if case == "success":
        cleanup.delete_owned(*args)
    else:
        with pytest.raises(UnsupportedScope):
            cleanup.delete_owned(*args)
    value = json.loads(path.read_text())
    assert value["binding"] == binding
    assert value["status"] == ("deleted" if case == "success" else "unconfirmed")
    assert (
        settings.daytona_api_key.get_secret_value() not in path.read_text()
        or not settings.daytona_api_key.get_secret_value()
    )


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="POSIX child deadline")
@pytest.mark.parametrize("expired", [False, True])
def test_real_sdk_thread_timeout_is_cut_off_by_cleanup_supervisor(
    settings, tmp_path, monkeypatch, expired
):
    """A real child and real SDK timeout around blocking C sleep; no SDK mocking."""
    import subprocess
    import sys

    from workbench.infrastructure.sandbox import cleanup

    _, _, binding = cleanup_binding()
    marker = tmp_path / "entered-sdk"
    child = """import json,sys,time,threading
from pathlib import Path
from daytona._utils.timeout import with_timeout
p=json.loads(sys.stdin.buffer.read())
@with_timeout()
def sdk_call(timeout):
    Path(sys.argv[1]).write_text("entered")
    time.sleep(6)
def worker():
    try: sdk_call(timeout=1)
    except Exception: pass
t=threading.Thread(target=worker);t.start();t.join()
print(json.dumps({"binding":p["binding"],"deleted":True}))
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        process = original([sys.executable, "-c", child, str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(cleanup.subprocess, "Popen", launch)
    path = tmp_path / "cleanup.json"
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        cleanup.delete_owned(
            settings,
            "rnd-source-agent-" + "b" * 32,
            "owned",
            binding,
            path,
            start + (-1 if expired else 2),
        )
    assert marker.read_text() == "entered"
    assert time.monotonic() - start < 4
    assert children[0].poll() is not None
    value = json.loads(path.read_text())
    assert value["status"] == "unconfirmed" and value["binding"] == binding


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["binding"].update(task="c" * 64),
        lambda value: value["binding"].update(source="private"),
        lambda value: value.update(status="private"),
        lambda value: value.update(reason="private"),
        lambda value: value.update(sandbox_name="another-unowned-sandbox"),
    ],
)
def test_public_cleanup_rejects_stale_or_poisoned_receipts(tmp_path, mutate):
    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    value = cleanup.receipt(binding, "rnd-source-agent-" + "b" * 32, "private-sdk-id")
    mutate(value)
    write_json(path, value)
    assert cleanup.public_receipt(path, task, plan) == {
        "status": "unconfirmed",
        "reason": "invalid_or_missing",
    }


def test_public_cleanup_survives_workspace_deletion_without_raw_sdk_data(tmp_path):
    import tempfile
    from pathlib import Path

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    with tempfile.TemporaryDirectory(dir=tmp_path) as directory:
        path = Path(directory) / "cleanup.json"
        value = cleanup.receipt(
            binding, "rnd-source-agent-" + "b" * 32, "private-sdk-id", "deletion_unconfirmed"
        )
        value["exception"] = "private secret"
        write_json(path, value)
        exported = cleanup.public_receipt(path, task, plan)
    assert not path.exists()
    assert exported["status"] == "unconfirmed" and exported["binding"] == binding
    assert "private" not in json.dumps(exported)


def test_terminal_checkpoint_cannot_retain_late_pass_or_repair(tmp_path):
    from workbench.capability_sandbox import terminate_checkpoint
    from workbench.filesystem import write_json

    path = tmp_path / "receipt.json"
    write_json(
        path, {"passed": True, "cleanup": "deleted", "repairable_failure": "application_startup"}
    )
    checkpoint = {"nonce": "b" * 32, "task": "approved", "deadline": time.monotonic()}
    terminate_checkpoint(path, checkpoint)
    value = json.loads(path.read_text())
    assert value["passed"] is False and value["cleanup"] == "unconfirmed"
    assert value["checkpoint"] == checkpoint and "repairable_failure" not in value


def test_real_sdk_thread_timer_alone_cannot_bound_blocking_c_call():
    import threading

    from daytona._utils.timeout import with_timeout
    from daytona.common.errors import DaytonaTimeoutError

    observed = []

    @with_timeout()
    def sdk_call(timeout):
        time.sleep(1.25)

    def work():
        start = time.monotonic()
        try:
            sdk_call(timeout=1)
        except DaytonaTimeoutError:
            observed.append(time.monotonic() - start)

    thread = threading.Thread(target=work)
    thread.start()
    thread.join(timeout=3)
    assert not thread.is_alive() and len(observed) == 1 and observed[0] >= 1.2


@pytest.mark.parametrize("wrong_source", [False, True])
def test_checkpoint_cleanup_summary_binds_task_and_current_candidate(tmp_path, wrong_source):
    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox.cleanup import checkpoint_receipts

    task, plan, binding = cleanup_binding()
    candidate = tmp_path / "step-1"
    candidate.mkdir()
    (candidate / "app.py").write_text("# fixture")
    source = digest(manifest(candidate))
    write_json(
        tmp_path / "step-1-node-verification.json",
        {
            "checkpoint": {"nonce": binding["nonce"], "task": binding["task"]},
            "plan_digest": binding["plan"],
            "source_digest": "c" * 64 if wrong_source else source,
            "sandbox_name": "rnd-source-" + "d" * 32,
            "passed": False,
            "cleanup": "unconfirmed",
            "error": "private-sdk-body",
            "repairable_failure": "private",
        },
    )
    result = checkpoint_receipts(tmp_path, task, plan)
    assert len(result) == 1 and result[0]["cleanup"] == "unconfirmed"
    assert result[0]["binding_valid"] is not wrong_source
    assert "private" not in json.dumps(result)
    if not wrong_source:
        assert result[0]["binding"]["source"] == source


@pytest.mark.parametrize("fail_write", [False, True])
def test_file_cleanup_tracks_expected_candidate_even_after_partial_upload(
    settings, tmp_path, monkeypatch, fail_write
):
    from workbench.infrastructure.sandbox import cleanup, coding

    task, plan, binding = cleanup_binding()
    operations = []
    client = SimpleNamespace()
    target = SimpleNamespace(
        id="owned", name=None, network_block_all=True, public=False, refresh_data=lambda: None
    )

    def create(parameters, timeout):
        target.name = parameters.name
        return target

    client.create = create
    monkeypatch.setattr(coding, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(coding, "client_for", lambda *a: client)
    monkeypatch.setattr(coding, "close_client", lambda *a: operations.append("closed"))
    monkeypatch.setattr(coding, "require_container_evidence", lambda *a: {})
    monkeypatch.setattr(coding, "require_profile_container_binding", lambda *a: None)
    monkeypatch.setattr(
        "scripts.daytona_capability_profile.inspect_created_sandbox", lambda *a, **k: {}
    )
    monkeypatch.setattr(coding.DaytonaFiles, "write", lambda *a: None)

    def delete(settings, name, identifier, bound, path, deadline):
        assert name == target.name and identifier == target.id
        assert bound == {**binding, "source": "c" * 64}
        operations.append("delete")
        assert json.loads(path.read_text())["binding"] == bound

    monkeypatch.setattr(cleanup, "delete_owned", delete)
    path = tmp_path / "agent-cleanup.json"

    def run():
        with coding._local_environment(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            deadline=time.monotonic() + 30,
            cleanup_record=path,
            cleanup_binding=binding,
        ) as environment:
            environment.bind_candidate("c" * 64)
            if fail_write:
                raise RuntimeError("partial upload failed")

    if fail_write:
        with pytest.raises(RuntimeError):
            run()
    else:
        run()
    assert operations == ["delete", "closed"]


def test_checkpoint_parent_kills_child_and_freezes_early_success(settings, tmp_path, monkeypatch):
    import subprocess
    import sys

    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier
    from workbench.generator import PrerequisiteError

    product = tmp_path / "product"
    plan = fixed_application(product)
    monkeypatch.setattr(
        "workbench.capability_execution.capability_execution_prerequisites",
        lambda *a: (tmp_path, {}),
    )
    monkeypatch.setattr(
        "workbench.capability_dependencies.require_dependency_descriptors", lambda *a: None
    )
    child = """import json,sys,time
from pathlib import Path
p=json.loads(sys.stdin.buffer.read())
Path(p['receipt']).write_text(json.dumps({'passed':True,'cleanup':'deleted','checkpoint':p['checkpoint'],'repairable_failure':'application_startup'}))
time.sleep(30)
"""
    original = subprocess.Popen
    children, auxiliary = [], []

    def launch(command, **kwargs):
        if command != [sys.executable, "-m", "workbench.capability_sandbox"]:
            auxiliary.append(command[0])
            return original(command, **kwargs)
        process = original([sys.executable, "-c", child], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    checkpoint = {
        "task": digest(plan.tasks[0].model_dump()),
        "nonce": "a" * 32,
        "deadline": time.monotonic() + 0.5,
    }
    with pytest.raises(PrerequisiteError, match="超时"):
        verifier.verify_capabilities(
            product,
            plan,
            plan.scenarios,
            settings,
            aggregate=False,
            checkpoint=checkpoint,
            selection=plan.selection.model_dump(),
        )
    assert len(children) == 1 and children[0].poll() is not None
    assert auxiliary == (["taskkill"] if os.name == "nt" else [])
    value = json.loads((tmp_path / "product-node-verification.json").read_text())
    assert value["passed"] is False and value["cleanup"] == "unconfirmed"
    assert value["checkpoint"] == checkpoint and "repairable_failure" not in value


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="dedicated POSIX deadline")
def test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline():
    from daytona._utils.timeout import with_timeout

    from workbench.infrastructure.sandbox.deadline import CheckpointDeadline, CheckpointExpired

    @with_timeout()
    def cleanup_call(timeout):
        time.sleep(12)

    start = time.monotonic()
    with CheckpointDeadline(start + 10.1) as controller:
        controller.enter_cleanup()
        with pytest.raises(CheckpointExpired):
            cleanup_call(timeout=20)
    elapsed = time.monotonic() - start
    assert 10 <= elapsed < 11.5


@pytest.mark.parametrize("status", [502, 503, 504])
def test_preview_gateway_errors_cannot_authorize_business_repair(status):
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, CheckFailure, run_steps

    with httpx.Client(
        base_url="http://fixture.invalid",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(status, stream=httpx.ByteStream(b"upstream unavailable"))
        ),
    ) as client:
        with pytest.raises(CheckFailure) as error:
            run_steps(client, [HttpStep(path="/check", status=200)], {})
    assert not isinstance(error.value, BusinessCheckFailure)


@pytest.mark.parametrize("phase", ["create", "refresh", "write", "snapshot", "idle", "success"])
def test_entire_file_sdk_lifecycle_is_supervised(settings, tmp_path, monkeypatch, phase):
    """Event-blocked real SDK refresh/API transport in a real child, no external network."""
    import subprocess
    import sys

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import file_session
    from workbench.infrastructure.sandbox.coding import coding_environment
    from workbench.planning.contracts import CapabilityEdits

    task, plan, binding = cleanup_binding()
    marker = tmp_path / "blocked"
    child = r"""
import io,json,socket,sys,threading,subprocess
from pathlib import Path
from unittest.mock import patch
from daytona import Daytona,DaytonaConfig
from daytona._utils.timeout import with_timeout
from urllib3.response import HTTPResponse
from workbench.infrastructure.sandbox import file_session,coding
phase,marker=sys.argv[1:]
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
client=Daytona(DaytonaConfig(api_url='http://127.0.0.1:1/api',api_key='offline-fixture',target='local',otel_enabled=False))
state={'name':None,'count':0}
def block():
 if phase=='refresh':
  descendant=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
  Path(marker+'.pid').write_text(str(descendant.pid))
 Path(marker).write_text('entered')
 threading.Event().wait(60)
def request(method,url,**kw):
 state['count']+=1
 if state['count']>1 and phase=='refresh':block()
 dto={'id':'owned','organizationId':'fixture','name':state['name'],'user':'root','env':{},'labels':{},'public':False,'networkBlockAll':True,'target':'local','cpu':1,'gpu':0,'memory':1,'disk':1,'toolboxProxyUrl':'http://127.0.0.1:1/toolbox','state':'started'}
 return HTTPResponse(status=200,body=io.BytesIO(json.dumps(dto).encode()),headers={'content-type':'application/json'},preload_content=False)
client._api_client.rest_client.pool_manager.request=request
@with_timeout()
def create(parameters,timeout):
 state['name']=parameters.name
 if phase=='create':block()
 return client.get(parameters.name)
client.create=create
writes=[0]
def write(self,edits):
 writes[0]+=1
 if phase=='write' and writes[0]>1:block()
def snapshot(self,paths):
 if phase=='snapshot':block()
 return {p:'' for p in paths}
with patch.object(coding,'client_for',lambda *a:client),patch.object(coding,'capability_execution_prerequisites',lambda *a:(Path('/tmp'),{})),patch.object(coding,'require_container_evidence',lambda *a:{}),patch.object(coding,'require_profile_container_binding',lambda *a:None),patch('scripts.daytona_capability_profile.inspect_created_sandbox',lambda *a,**k:{}),patch.object(coding.DaytonaFiles,'write',write),patch.object(coding.DaytonaFiles,'snapshot',snapshot):
 file_session.main()
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        with (tmp_path / "child-errors").open("wb") as errors:
            kwargs["stderr"] = errors
            process = original([sys.executable, "-c", child, phase, str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(file_session.subprocess, "Popen", launch)
    cleaned = []

    def cleanup(settings, name, identifier, bound, path, deadline):
        cleaned.append((identifier, time.monotonic(), dict(bound)))
        value = file_session.receipt(
            bound, name, identifier, "create_unconfirmed" if identifier is None else "pending"
        )
        if identifier is not None:
            value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)
        if identifier is None:
            raise UnsupportedScope("Unknown create stays unconfirmed")

    monkeypatch.setattr(file_session, "delete_owned", cleanup)
    start = time.monotonic()
    path = tmp_path / "agent-cleanup.json"
    from contextlib import nullcontext

    with nullcontext() if phase == "success" else pytest.raises(UnsupportedScope):
        with coding_environment(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            deadline=start + 25,
            cleanup_record=path,
            cleanup_binding=binding,
        ) as environment:
            if phase == "success":
                assert environment.snapshot(task.allowed_paths) == {
                    p: "" for p in task.allowed_paths
                }
            if phase == "write":
                environment.bind_candidate("c" * 64)
                environment.write(
                    CapabilityEdits(
                        explanation="fixture",
                        files=[{"path": p, "content": ""} for p in task.allowed_paths],
                    )
                )
            elif phase == "snapshot":
                environment.snapshot(task.allowed_paths)
            elif phase == "idle":
                assert environment.done.wait(12), "watchdog must clean while parent is idle"
                environment.snapshot(task.allowed_paths)
    assert time.monotonic() - start < 14
    assert len(cleaned) == 1 and cleaned[0][1] < start + 25
    assert children[0].poll() is not None
    value = json.loads(path.read_text())
    safe_failure = {
        key: value.get(key)
        for key in (
            "reason",
            "supervision_failure_phase",
            "supervision_failure_kind",
            "failure_phase",
            "failure_kind",
            "cleanup_failure_kind",
        )
    }
    assert value["status"] == ("unconfirmed" if phase == "create" else "deleted"), safe_failure
    assert value["binding"]["source"] == ("c" * 64 if phase == "write" else binding["source"])
    if phase not in {"idle", "success"}:
        assert marker.read_text() == "entered"
    if phase == "refresh" and os.name == "posix":
        from pathlib import Path

        descendant = Path("/proc") / (tmp_path / "blocked.pid").read_text() / "stat"
        if descendant.exists():
            assert descendant.read_text().split()[2] == "Z", (
                "Owned inspector must not survive SDK kill"
            )


@pytest.mark.parametrize("mutation", [None, "missing", "sha", "job", "scenario", "policy"])
def test_real_file_entrypoint_rechecks_forwarded_scope(settings, tmp_path, monkeypatch, mutation):
    """Real Session/main/local-environment/browser gate; stop before SDK/network use."""
    import subprocess
    import sys

    from test_capability_browser_policy import IMAGE, approved_manual

    from workbench import capability_browser_isolation as isolation
    from workbench import capability_browser_policy as policy
    from workbench.infrastructure.sandbox import file_session

    # The selector is Linux-only; exercise that exact identity on every CI controller.
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    approved_manual(monkeypatch)
    for key in ("API_KEY", "GITHUB_TOKEN", "HTTP_PROXY", "HTTPS_PROXY"):
        monkeypatch.setenv(key, "private-must-not-forward")
    browser = tmp_path / "browser.json"
    browser.write_text(
        json.dumps(
            {
                "protocol": "offline-browser-isolation-v3",
                "passed": True,
                "mocked": False,
                "image": IMAGE,
                "runtime": {"fixture_approved_runtime": True},
                "sources": isolation.browser_source_identity(),
                "image_sources": isolation.image_source_identity(),
                "checks": {
                    "kernel_and_network": dict.fromkeys(
                        (
                            "passed",
                            "kernel_resource_limits",
                            "network_none",
                            "tmpfs_exhaustion",
                            "pid_exhaustion",
                            "readonly_root",
                            "browser_build",
                            "apparmor_enforced",
                        ),
                        True,
                    ),
                    **dict.fromkeys(
                        (
                            "positive",
                            "error",
                            "abuse",
                            "failure_cleanup",
                            "memory_exhaustion",
                            "raw_syscalls",
                        ),
                        True,
                    ),
                },
            }
        )
    )
    marker = tmp_path / "admitted"
    child = r"""
import os,sys,socket
from pathlib import Path
from workbench.infrastructure.sandbox import file_session,coding
from workbench import capability_browser_isolation as isolation, capability_browser_policy as policy
from workbench.errors import UnsupportedScope
browser,marker=sys.argv[1:]
assert not any(k in os.environ for k in ('API_KEY','GITHUB_TOKEN','HTTP_PROXY','HTTPS_PROXY'))
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
policy.platform.system=lambda:'Linux'
policy.platform.machine=lambda:'x86_64'
isolation.BROWSER_ACCEPTANCE=Path(browser)
isolation.runtime_identity=lambda image: ({'fixture_approved_runtime':True} if policy.selected_policy() else {'policy_sha256':None,'mode':'docker-default'})
def prerequisites(*args):
 isolation.require_browser_acceptance('sha256:'+'a'*64)
 Path(marker).write_text('admitted')
 return Path(browser).parent,{}
def stop(*args):raise UnsupportedScope('private SDK sentinel must never be exported')
coding.capability_execution_prerequisites=prerequisites
coding.client_for=stop
file_session.main()
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        env = kwargs["env"]
        assert env["GITHUB_SHA"] == env["REVIEWED_SHA"] == env["GITHUB_WORKFLOW_SHA"]
        if mutation == "missing":
            env.pop("CAPABILITY_BROWSER_APPROVED_POLICY")
        elif mutation is not None:
            key, value = {
                "sha": ("REVIEWED_SHA", "b" * 40),
                "job": ("GITHUB_JOB", "real-model"),
                "scenario": ("LIVE_SCENARIO", "legacy"),
                "policy": ("CAPABILITY_BROWSER_APPROVED_POLICY", "0" * 64),
            }[mutation]
            env[key] = value
        process = original([sys.executable, "-c", child, str(browser), str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(file_session.subprocess, "Popen", launch)

    def unresolved(*args):
        raise UnsupportedScope("Unknown create remains unconfirmed")

    monkeypatch.setattr(file_session, "delete_owned", unresolved)
    task, plan, binding = cleanup_binding()
    path = tmp_path / "agent-cleanup.json"
    with pytest.raises(UnsupportedScope):
        file_session.Session(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            time.monotonic() + 25,
            path,
            binding,
        )
    assert len(children) == 1 and children[0].poll() is not None
    assert marker.exists() is (mutation is None)
    value = json.loads(path.read_text())
    assert value["failure_phase"] == ("client" if mutation is None else "admission")
    assert value["failure_kind"] in {"UnsupportedScope", "PrerequisiteError", "ValueError"}
    assert value["status"] == "unconfirmed" and value["reason"] == "create_unconfirmed"
    assert "private" not in path.read_text()


@pytest.mark.parametrize(
    "bad_scope",
    [("GITHUB_JOB", "real-model"), ("GITHUB_RUN_ATTEMPT", "2"), ("REVIEWED_SHA", "b" * 40)],
)
def test_file_session_rejects_extra_scope_before_launch(settings, tmp_path, monkeypatch, bad_scope):
    from test_capability_browser_policy import approved_manual

    from workbench import capability_browser_policy as policy
    from workbench.infrastructure.sandbox import file_session

    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    approved_manual(monkeypatch)
    monkeypatch.setenv(*bad_scope)
    launches = []
    monkeypatch.setattr(file_session.subprocess, "Popen", lambda *a, **k: launches.append(True))
    task, plan, binding = cleanup_binding()
    path = tmp_path / "journal"
    with pytest.raises(ValueError, match="approved Actions scope"):
        file_session.Session(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            time.monotonic() + 25,
            path,
            binding,
        )
    assert not launches and not path.exists()


@pytest.mark.parametrize("mode", ["absent", "eventual", "present", "forbidden", "server", "late"])
def test_real_sdk_deletion_requires_timely_typed_absence(monkeypatch, mode):
    """Actual pinned SDK get/delete/error interception, only HTTP transport synthesized."""
    import io
    import socket

    from daytona import Daytona, DaytonaConfig
    from daytona.common.errors import DaytonaAuthorizationError, DaytonaError
    from urllib3.response import HTTPResponse

    from workbench.infrastructure.sandbox.cleanup import confirm_deleted
    from workbench.sandbox import close_client

    def deny(*a, **k):
        raise AssertionError("offline only")

    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    client = Daytona(
        DaytonaConfig(
            api_url="http://127.0.0.1:1/api",
            api_key="offline-fixture",
            target="local",
            otel_enabled=False,
        )
    )
    state = {"deleted": False, "gets": 0}
    calls = []
    dto = {
        "id": "owned-id",
        "organizationId": "fixture",
        "name": "rnd-source-agent-" + "a" * 32,
        "user": "root",
        "env": {},
        "labels": {},
        "public": False,
        "networkBlockAll": True,
        "target": "local",
        "cpu": 1,
        "gpu": 0,
        "memory": 1,
        "disk": 1,
        "toolboxProxyUrl": "http://127.0.0.1:1/toolbox",
        "state": "started",
    }

    def request(method, url, **kwargs):
        status, body = 200, dto
        if method == "DELETE":
            state["deleted"] = True
            status, body = 204, None
        elif state["deleted"]:
            state["gets"] += 1
            if mode == "late":
                time.sleep(0.25)
            status = {
                "absent": 404,
                "eventual": 200 if state["gets"] == 1 else 404,
                "present": 200,
                "forbidden": 403,
                "server": 500,
                "late": 404,
            }[mode]
            body = dto if status == 200 else {"message": "owned fixture"}
        calls.append((method, status))
        return HTTPResponse(
            status=status,
            body=io.BytesIO(json.dumps(body).encode() if body else b""),
            headers={"content-type": "application/json"},
            preload_content=False,
        )

    monkeypatch.setattr(client._api_client.rest_client.pool_manager, "request", request)
    try:
        target = client.get(dto["name"])
        if mode in {"absent", "eventual"}:
            confirm_deleted(client, target, time.monotonic() + 1, 1)
            assert calls[-1] == ("GET", 404)
        else:
            error = {
                "present": TimeoutError,
                "late": TimeoutError,
                "forbidden": DaytonaAuthorizationError,
                "server": DaytonaError,
            }[mode]
            with pytest.raises(error):
                confirm_deleted(client, target, time.monotonic() + 0.12, 1)
        assert ("DELETE", 204) in calls
    finally:
        close_client(client)


@pytest.mark.parametrize(
    "failure",
    [
        None,
        "CreateJobObjectW",
        "SetInformationJobObject",
        "AssignProcessToJobObject",
        "TerminateJobObject",
        "CloseHandle",
    ],
)
def test_windows_job_owns_subtree_and_fails_closed(failure):
    import ctypes

    from workbench.infrastructure.sandbox.windows_job import ExtendedLimits, WindowsJob

    calls = []

    class Function:
        def __init__(self, name):
            self.name = name

        def __call__(self, *args):
            calls.append((self.name, args))
            if self.name == "SetInformationJobObject":
                limits = ctypes.cast(args[2], ctypes.POINTER(ExtendedLimits)).contents
                assert limits.BasicLimitInformation.LimitFlags == 0x2000
                assert args[1] == 9 and args[3] == ctypes.sizeof(ExtendedLimits)
            return 0 if self.name == failure else 99 if self.name == "CreateJobObjectW" else 1

    api = SimpleNamespace(
        **{
            name: Function(name)
            for name in (
                "CreateJobObjectW",
                "SetInformationJobObject",
                "AssignProcessToJobObject",
                "TerminateJobObject",
                "CloseHandle",
            )
        }
    )
    if failure is None:
        job = WindowsJob(SimpleNamespace(_handle=7), api=api)
        job.terminate()
        job.close()
        job.close()
        assert [name for name, _ in calls] == [
            "CreateJobObjectW",
            "SetInformationJobObject",
            "AssignProcessToJobObject",
            "TerminateJobObject",
            "CloseHandle",
        ]
        assert calls[2][1] == (99, 7)
        assert calls[3][1] == (99, 1)
    else:
        with pytest.raises(UnsupportedScope):
            job = WindowsJob(SimpleNamespace(_handle=7), api=api)
            job.terminate()
            job.close()
        if failure in {"SetInformationJobObject", "AssignProcessToJobObject"}:
            assert calls[-1][0] == "CloseHandle"


@pytest.mark.skipif(os.name != "nt", reason="native Windows Job Object process-tree proof")
def test_native_windows_job_kills_pipe_holding_descendant(tmp_path):
    import ctypes
    import subprocess
    import sys

    from workbench.infrastructure.sandbox.file_session import close_pipes_bounded
    from workbench.infrastructure.sandbox.windows_job import WindowsJob

    marker = tmp_path / "pid"
    child = """import subprocess,sys
from pathlib import Path
sys.stdin.readline()
p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
marker=Path(sys.argv[1]); temporary=marker.with_suffix('.tmp')
temporary.write_text(str(p.pid)); temporary.replace(marker)
print('ready',flush=True)
p.wait()
"""
    process = subprocess.Popen(
        [sys.executable, "-c", child, str(marker)], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    job = None
    descendant = None
    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    api.OpenProcess.restype = ctypes.c_void_p
    api.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    api.WaitForSingleObject.restype = ctypes.c_uint32
    api.CloseHandle.argtypes = [ctypes.c_void_p]
    try:
        job = WindowsJob(process)
        process.stdin.write(b"start\n")
        process.stdin.flush()
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        assert marker.exists()
        descendant = api.OpenProcess(0x00100000, False, int(marker.read_text()))
        assert descendant
        start = time.monotonic()
        job.terminate()
        process.wait(timeout=2)
        assert api.WaitForSingleObject(descendant, 2000) == 0
        close_pipes_bounded(process)
        assert time.monotonic() - start < 4
    finally:
        if job is not None:
            job.close()
        else:
            process.kill()
        if descendant:
            api.CloseHandle(descendant)
        process.wait(timeout=2)
        close_pipes_bounded(process)


def test_pipe_reaping_has_independent_bound():
    import threading

    from workbench.infrastructure.sandbox.file_session import close_pipes_bounded

    release = threading.Event()
    process = SimpleNamespace(
        stdin=SimpleNamespace(close=lambda: release.wait(5)),
        stdout=SimpleNamespace(close=lambda: None),
    )
    start = time.monotonic()
    try:
        with pytest.raises(UnsupportedScope, match="pipe close exceeded bound"):
            close_pipes_bounded(process)
        assert time.monotonic() - start < 1
    finally:
        release.set()


@pytest.mark.parametrize("known", [False, True])
def test_cleanup_child_exports_only_bound_failure_kind(settings, tmp_path, monkeypatch, known):
    import subprocess
    import sys

    from workbench.infrastructure.sandbox import cleanup

    child = r"""
import io,json,socket
from daytona import Daytona,DaytonaConfig
from urllib3.response import HTTPResponse
from workbench.infrastructure.sandbox import cleanup
from workbench import sandbox
def deny(*a,**k):raise AssertionError('offline only')
socket.socket.connect=deny;socket.create_connection=deny
client=Daytona(DaytonaConfig(api_url='http://127.0.0.1:1/api',api_key='offline-fixture',target='local',otel_enabled=False))
def request(*a,**k):
 return HTTPResponse(status=403,body=io.BytesIO(json.dumps({'message':'private server text must not escape'}).encode()),headers={'content-type':'application/json'},preload_content=False)
client._api_client.rest_client.pool_manager.request=request
sandbox.client_for=lambda *a:client
cleanup.main()
"""
    original = subprocess.Popen
    monkeypatch.setattr(
        cleanup.subprocess,
        "Popen",
        lambda command, **kw: original([sys.executable, "-c", child], **kw),
    )
    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    with pytest.raises(UnsupportedScope):
        cleanup.delete_owned(
            settings,
            "rnd-source-agent-" + "a" * 32,
            "owned-id" if known else None,
            binding,
            path,
            time.monotonic() + 10,
        )
    value = json.loads(path.read_text())
    assert value["status"] == "unconfirmed"
    assert value["reason"] == ("deletion_unconfirmed" if known else "create_unconfirmed")
    assert value["cleanup_failure_kind"] == "DaytonaAuthorizationError"
    assert "private" not in path.read_text()
    exported = cleanup.public_receipt(path, task, plan)
    assert exported["cleanup_failure_kind"] == "DaytonaAuthorizationError"
    assert exported["status"] == "unconfirmed"


@pytest.mark.parametrize("phase", ["reader", "pipe"])
def test_local_reap_failure_still_attempts_owned_deletion(tmp_path, monkeypatch, phase):
    import subprocess
    import sys
    import threading

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import file_session
    from workbench.tools import process_options

    process = subprocess.Popen(
        [sys.executable, "-c", "import time;time.sleep(30)"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        **process_options(),
    )
    session = file_session.Session.__new__(file_session.Session)
    session.process = process
    session.deadline = time.monotonic() + 15
    session.lock, session.done, session.cancel = (
        threading.Lock(),
        threading.Event(),
        threading.Event(),
    )
    session.closing, session.error, session.failure = False, None, {}
    session.windows_job = None
    if os.name == "nt":
        from workbench.infrastructure.sandbox.windows_job import WindowsJob

        session.windows_job = WindowsJob(process)
    session.settings = SimpleNamespace()
    session.path = tmp_path / "cleanup.json"
    _, _, session.binding = cleanup_binding()
    session.name, session.identifier = "rnd-source-agent-" + "e" * 32, "known-owned-id"
    write_json(
        session.path, file_session.receipt(session.binding, session.name, session.identifier)
    )
    release, calls = threading.Event(), []
    original_close = file_session.close_pipes_bounded

    def deletion(settings, name, identifier, binding, path, deadline):
        assert identifier == session.identifier and binding == session.binding
        assert deadline == session.deadline and time.monotonic() < deadline
        calls.append(identifier)
        value = file_session.receipt(binding, name, identifier)
        value.update(status="deleted", reason="confirmed_absent")
        write_json(path, value)  # Mock remote absence cannot hide a local reaping failure.

    def blocked_close(_):
        original_close(
            SimpleNamespace(
                stdin=SimpleNamespace(close=lambda: release.wait(5)),
                stdout=SimpleNamespace(close=lambda: None),
            )
        )

    monkeypatch.setattr(file_session, "delete_owned", deletion)
    if phase == "pipe":
        monkeypatch.setattr(file_session, "close_pipes_bounded", blocked_close)
    else:
        session.reader = threading.Thread(target=lambda: release.wait(5), daemon=True)
        session.reader.start()
    try:
        with pytest.raises(UnsupportedScope):
            session.finish()
        assert process.poll() is not None and session.deadline - time.monotonic() > 10
        assert calls == [session.identifier]
        value = json.loads(session.path.read_text())
        assert value["status"] == "unconfirmed" and value["reason"] == "deletion_unconfirmed"
        assert value["supervision_failure_phase"] == ("reader" if phase == "reader" else "pipes")
        assert value["supervision_failure_kind"] == "UnsupportedScope"
        assert session.done.is_set()
    finally:
        release.set()
        if hasattr(session, "reader"):
            session.reader.join(1)
        process.wait(timeout=2)
        original_close(process)


def test_model_turn_timing_preserves_failed_outcome_and_original_budget(tmp_path, monkeypatch):
    from workbench.coding import timing

    clock = [100.0]
    monkeypatch.setattr(timing, "time", SimpleNamespace(monotonic=lambda: clock[0]))
    transport = SimpleNamespace(calls=2)
    path = tmp_path / "timing.json"
    failure = RuntimeError("private-model-failure")
    with pytest.raises(RuntimeError) as found:
        with timing.record_turn(path, 0, 180, 31.5, {"secret": "private-prompt"}, transport):
            clock[0] = 164
            transport.calls = 4
            raise failure
    assert found.value is failure
    value = timing.read_turns(path)[0]
    assert value == {
        "step": 0,
        "module_remaining_seconds": 80,
        "work_remaining_seconds": 65,
        "timeout_seconds": 31.5,
        "elapsed_seconds": 64,
        "remaining_after_seconds": 16,
        "overrun_seconds": 0,
        "payload_chars": len(json.dumps({"secret": "private-prompt"})),
        "http_attempts_before": 2,
        "http_attempts_after": 4,
    }
    assert "private" not in path.read_text()
    monkeypatch.setattr(
        timing, "write_json", lambda *a: (_ for _ in ()).throw(OSError("private-io"))
    )
    with pytest.raises(RuntimeError) as found:
        with timing.record_turn(path, 1, 180, 7, {}, transport):
            raise failure
    assert found.value is failure


def test_supervision_diagnostics_are_fixed_and_cannot_upgrade_cleanup(tmp_path):
    from workbench.infrastructure.sandbox import cleanup, file_session

    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    name = "rnd-source-agent-" + "a" * 32
    for phase in file_session.SUPERVISION_PHASES:
        value = file_session.receipt(binding, name, "owned-id")
        value.update(status="deleted", reason="confirmed_absent")
        path.write_text(json.dumps(value))
        error = OSError("private local details")
        failure = file_session.supervision_failure(phase, error)
        file_session.preserve_state(path, binding, name, "owned-id", error, failure)
        result = cleanup.public_receipt(path, task, plan)
        assert result["status"] == "unconfirmed"
        assert result["supervision_failure_phase"] == phase
        assert result["supervision_failure_kind"] == "OSError"
        assert "private" not in json.dumps(result)
    value.update(supervision_failure_phase="private-phase", supervision_failure_kind="private-kind")
    path.write_text(json.dumps(value))
    assert "private" not in json.dumps(cleanup.public_receipt(path, task, plan))
    path.write_text("{}")
    file_session.preserve_state(path, binding, name, "owned-id", None, {})
    assert cleanup.public_receipt(path, task, plan)["supervision_failure_phase"] == "journal"
