"""Explicit combined actions use the original worker, guards and checkpoint."""

import json
from types import SimpleNamespace

import pytest
from test_mini_swe_checkpoints import exercise

from scripts.sla_fixture import design
from workbench.coding import mini_swe as agent
from workbench.coding.ports import AgentTurn, approved_turn_schema
from workbench.coding.timing import timing_receipts
from workbench.core.contracts import digest
from workbench.errors import UnsupportedScope


@pytest.mark.parametrize("combined,expected", [(False, 2), (True, 1)])
def test_explicit_completion_preserves_legacy_flow(
    settings, tmp_path, monkeypatch, combined, expected
):
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], combined=combined
    )
    result = run()
    assert len(calls) == expected and len(checks) == 1 and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert len(result.files) == 2
    receipt = json.loads((tmp_path / "worker/agent-result.json").read_text())
    assert receipt["candidate_submitted"] is True
    assert receipt["implementation_verified"] is False
    assert receipt["budget"]["requests"] == 2 * expected
    turns = json.loads((tmp_path / "worker/agent-model-timings.json").read_text())
    assert [t["operation"] for t in turns] == (
        ["edit_and_submit"] if combined else ["edit", "submit"]
    )


def test_combined_failure_repairs_in_same_session(settings, tmp_path, monkeypatch):
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [False, True], combined=True
    )
    run()
    assert len(calls) == len(checks) == 2 and cleaned == [True]
    assert calls[1]["verification_feedback"] == {
        "passed": False,
        "source_digest": digest(checks[0][0]),
        "category": "application_startup",
    }
    assert calls[1]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]
    assert checks[0][1] == checks[1][1] and checks[0][0] != checks[1][0]
    assert (product / "app.py").read_text() == "# baseline\n"
    with pytest.raises(UnsupportedScope, match="重置"):
        run()


@pytest.mark.parametrize("bad_edit", ["missing", "path", "before"])
def test_combined_rejects_bad_files_before_checkpoint(settings, tmp_path, monkeypatch, bad_edit):
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], combined=True, bad_edit=bad_edit
    )
    with pytest.raises(ValueError):
        run()
    assert len(calls) == 1 and checks == [] and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert not (tmp_path / "worker/agent-result.json").exists()


def test_combined_partial_write_cannot_check_or_promote(settings, tmp_path, monkeypatch):
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], combined=True, write_failure=True
    )
    with pytest.raises(OSError):
        run()
    assert len(calls) == 1 and checks == [] and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert not (tmp_path / "worker/agent-result.json").exists()


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("deadline"),
        UnsupportedScope("cleanup unconfirmed"),
        UnsupportedScope("resource failure"),
    ],
)
def test_combined_infrastructure_failure_cannot_repair(settings, tmp_path, monkeypatch, failure):
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [failure], combined=True
    )
    with pytest.raises(type(failure)):
        run()
    assert len(calls) == len(checks) == 1 and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"


@pytest.mark.parametrize("case", ["repeat", "snapshot", "late", "cleanup"])
def test_combined_rejects_replay_tamper_lateness_and_cleanup(settings, tmp_path, monkeypatch, case):
    clock = [0.0]
    monkeypatch.setattr(agent, "time", SimpleNamespace(monotonic=lambda: clock[0], time=lambda: 0))

    def expire():
        clock[0] = settings.mini_swe_timeout + 1

    run, calls, checks, cleaned, product = exercise(
        settings,
        tmp_path,
        monkeypatch,
        [case != "repeat"],
        combined=True,
        repeat=case == "repeat",
        changed_snapshot=case == "snapshot",
        after_check=expire if case == "late" else lambda: None,
        cleanup_effect=expire if case == "cleanup" else lambda: None,
    )
    with pytest.raises((ValueError, UnsupportedScope)):
        run()
    assert len(checks) == 1 and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert not (tmp_path / "worker/agent-result.json").exists()


def test_combined_failed_candidates_keep_original_step_ceiling(settings, tmp_path, monkeypatch):
    run, calls, checks, cleaned, _ = exercise(
        settings, tmp_path, monkeypatch, [False], combined=True
    )
    with pytest.raises((ValueError, UnsupportedScope)):
        run()
    assert len(calls) == len(checks) == 8 and cleaned == [True]
    receipt = json.loads((tmp_path / "worker/agent-budget.json").read_text())
    assert receipt["requests"] == 16
    assert len({deadline for _, deadline in checks}) == 1


@pytest.mark.parametrize("operation", ["edit", "edit_and_submit"])
def test_both_edit_actions_require_complete_approved_files(operation):
    from test_native_schema import edit

    value = edit()
    value["operation"] = operation
    schema = approved_turn_schema(design().implementation.tasks[0])
    assert schema.model_validate(value).operation == operation
    for files in ([], value["edits"]["files"][:1], value["edits"]["files"] * 2):
        with pytest.raises(ValueError):
            schema.model_validate({**value, "edits": {**value["edits"], "files": files}})
    with pytest.raises(ValueError):
        AgentTurn(operation=operation, edits=None)
    with pytest.raises(ValueError):
        AgentTurn(operation="submit", edits=value["edits"])


def test_operation_receipt_projects_only_fixed_enum():
    for operation in ["edit", "submit", "edit_and_submit", "private-content", True, {}, None]:
        result = timing_receipts([{"operation": operation, "content": "private-content"}])[0]
        assert result["operation"] == (
            operation
            if type(operation) is str and operation in {"edit", "submit", "edit_and_submit"}
            else None
        )
        assert "private-content" not in json.dumps(result)
    assert "operation" not in timing_receipts([{}])[0]


def test_combined_checkpoint_rejects_replayed_nonce(settings, tmp_path, monkeypatch):
    from test_mini_swe_checkpoints import bound_check_fixture

    original_check = agent.check_candidate
    bindings = []

    def replay(proof):
        bindings.append(dict(proof["checkpoint"]))
        if len(bindings) > 1:
            proof["checkpoint"] = {**proof["checkpoint"], "nonce": bindings[0]["nonce"]}

    bound_check_fixture(tmp_path, monkeypatch, replay)
    run, calls, _, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [False], combined=True
    )
    monkeypatch.setattr(agent, "check_candidate", original_check)
    with pytest.raises(UnsupportedScope, match="身份"):
        run()
    assert len(calls) == len(bindings) == 2 and cleaned == [True]
    assert bindings[0]["nonce"] != bindings[1]["nonce"]
    assert bindings[0]["deadline"] == bindings[1]["deadline"]
    assert not (tmp_path / "worker/agent-result.json").exists()
    assert (product / "app.py").read_text() == "# baseline\n"


def test_combined_atomic_local_write_failure_keeps_baseline(settings, tmp_path, monkeypatch):
    from workbench.coding import candidates

    original_write = candidates.atomic_text
    writes = []

    def failed_second_write(path, content):
        writes.append(path)
        if len(writes) == 2:
            raise OSError("bounded write failure")
        return original_write(path, content)

    monkeypatch.setattr(candidates, "atomic_text", failed_second_write)
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], combined=True
    )
    with pytest.raises(OSError):
        run()
    assert len(writes) == 2 and len(calls) == 1 and checks == [] and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert not (tmp_path / "worker/step-1").exists()
    assert not (tmp_path / "worker/agent-result.json").exists()


@pytest.mark.parametrize("mode", ["upgrade", "downgrade", "replay"])
def test_worker_cannot_change_or_replay_model_operation(settings, tmp_path, monkeypatch, mode):
    import subprocess

    wrapper = tmp_path / "altered-worker.py"
    original_worker = agent.ROOT / "tools/mini-swe/worker.py"
    wrapper.write_text(
        "import runpy\n"
        f"ns = runpy.run_path({str(original_worker)!r})\n"
        "cls = ns['DaytonaEnvironment']\n"
        "original = cls.execute\n"
        "def execute(self, action):\n"
        "    action = dict(action)\n"
        + (
            "    action['operation'] = 'edit_and_submit'\n"
            if mode == "upgrade"
            else "    action['operation'] = 'edit'\n"
            if mode == "downgrade"
            else ""
        )
        + "    result = original(self, action)\n"
        + ("    return original(self, action)\n" if mode == "replay" else "    return result\n")
        + "cls.execute = execute\nns['main']()\n"
    )

    def launch(args, **kwargs):
        assert args[1:] == ["-I", str(original_worker)]
        return subprocess.Popen([args[0], "-I", str(wrapper)], **kwargs)

    monkeypatch.setattr(
        agent,
        "subprocess",
        SimpleNamespace(Popen=launch, PIPE=subprocess.PIPE, DEVNULL=subprocess.DEVNULL),
    )
    run, calls, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [False], combined=mode != "upgrade"
    )
    with pytest.raises(ValueError, match="Worker action differs"):
        run()
    assert len(calls) == 1 and len(checks) == (1 if mode == "replay" else 0)
    assert cleaned == [True] and (product / "app.py").read_text() == "# baseline\n"
    assert not (tmp_path / "worker/agent-result.json").exists()
