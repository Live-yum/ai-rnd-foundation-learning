# tests/test_mini_swe_checkpoints.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding`、`workbench.coding.ports`、`workbench.core.contracts`、`workbench.errors`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `exercise`（L21–L112）：接收`settings`、`tmp_path`、`monkeypatch`、`outcomes`、`bad_edit`、`repeat`、`changed_snapshot`、`cleanup_effect`。 控制顺序：L32按`not agent.worker_python().is_file()`分支；L33断言`not os.environ.get("RND_REQUIRE_V2_TOOLS")`。 调用`agent.worker_python().is_file`、`agent.worker_python`、`os.environ.get`、`pytest.skip`、`design`、`product.mkdir`、`(product / "app.py").write_text`、`settings.model_copy`、`monkeypatch.setattr`。 返回路径：L112的`run, requests, checkpoints, cleaned, product`。
- `exercise.Gateway`（L44–L66）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `exercise.Gateway.complete`（L45–L66）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L47断言`"新库初始化" in instruction`；L49按`number % 2 == 0 or (repeat and number > 2)`分支；L60按`bad_edit == "path"`分支；L62按`bad_edit == "before"`分支。 调用`requests.append`、`deepcopy`、`len`、`AgentTurn`、`AgentTurn.model_validate`。 返回路径：L50的`AgentTurn(operation="submit")`；L64的`AgentTurn.model_validate( {"operation": "edit", "edits": {"explanation": "fixture", "files…`。
- `exercise.Environment`（L68–L76）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `exercise.Environment.write`（L69–L70）：接收`edits`。 调用`snapshot.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `exercise.Environment.snapshot`（L72–L76）：接收`paths`。 控制顺序：L74按`changed_snapshot`分支。 调用`dict`。 返回路径：L76的`result`。
- `exercise.environment`（L79–L84）：接收`*args`。 调用`Environment`、`cleaned.append`、`cleanup_effect`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `exercise.checkpoint`（L86–L95）：接收`s`、`t`、`p`、`candidate`、`deadline`。 控制顺序：L89按`isinstance(result, Exception)`分支；L90抛异常，停止当前正常路径。 调用`checkpoints.append`、`manifest`、`min`、`len`、`isinstance`、`digest`。 返回路径：L91的`{ "passed": result, "source_digest": digest(manifest(candidate)), **({} if result else {"c…`。
- `exercise.run`（L99–L110）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`agent.run_agent`、`Gateway`。 返回路径：L100的`agent.run_agent( settings, Gateway(), "fixture", task, plan, product, tmp_path / "worker",…`。
- `test_failed_submit_repairs_current_candidate_in_same_worker`（L115–L138）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L120断言`len(requests) == 4 and len(checks) == 2 and cleaned == [True]`；L121断言`requests[0]["verification_feedback"] is None`；L122断言`requests[2]["verification_feedback"] == { "passed": False, "source_digest": digest(ch…`；L127断言`requests[2]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]`；L128断言`checks[0][1] == checks[1][1]`；L129断言`checks[0][0] != checks[1][0]`；L130断言`(product / "app.py").read_text() == "# baseline\n"`；L131断言`next(e for e in edits.files if e.path == "app.py").before_sha256 == manifest(product)…`。后续分支沿下方源码相同行号继续阅读。 调用`exercise`、`run`、`len`、`digest`、`(product / "app.py").read_text`、`next`、`manifest`、`json.loads`、`(tmp_path / "worker/agent-budget.json").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_persistent_failure_exhausts_existing_eight_steps`（L141–L147）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L145断言`len(requests) == 8 and len(checks) == 4 and cleaned == [True]`；L146断言`json.loads((tmp_path / "worker/agent-budget.json").read_text())["requests"] == 16`；L147断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`exercise`、`pytest.raises`、`run`、`len`、`json.loads`、`(tmp_path / "worker/agent-budget.json").read_text`、`(tmp_path / "worker/agent-result.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_failures_stop_without_model_repair`（L153–L157）：接收`settings`、`tmp_path`、`monkeypatch`、`failure`。 控制顺序：L157断言`len(requests) == 2 and len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`pytest.raises`、`type`、`run`、`len`、`pytest.mark.parametrize`、`TimeoutError`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_never_grants_edit_authority`（L161–L168）：接收`settings`、`tmp_path`、`monkeypatch`、`bad_edit`。 控制顺序：L167断言`not checks and cleaned == [True]`；L168断言`(product / "app.py").read_text() == "# baseline\n"`。 调用`exercise`、`pytest.raises`、`run`、`(product / "app.py").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_repeated_or_changed_submissions_fail_closed`（L172–L183）：接收`settings`、`tmp_path`、`monkeypatch`、`case`。 控制顺序：L183断言`len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`pytest.raises`、`run`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bound_check_fixture`（L186–L227）：接收`tmp_path`、`monkeypatch`、`mutate`。 调用`design`、`candidate.mkdir`、`(candidate / "app.py").write_text`、`monkeypatch.setattr`。 返回路径：L227的`plan, task, candidate`。
- `bound_check_fixture.verifier`（L200–L224）：接收`product`、`p`、`scenarios`、`settings`、`**kwargs`。 调用`digest`、`manifest`、`p.model_dump`、`mutate`。 返回路径：L224的`proof`。
- `test_feedback_strips_instructions_unknown_fields_and_paths`（L230–L235）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L233断言`feedback["category"] == "application_startup"`；L234断言`feedback["startup"]["command_exit_code"] == 3`；L235断言`not any(x in json.dumps(feedback) for x in ("secret", "private", "execute"))`。 调用`bound_check_fixture`、`agent.check_candidate`、`time.monotonic`、`any`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_untrusted_or_stale_checkpoint_cannot_finish`（L251–L254）：接收`settings`、`tmp_path`、`monkeypatch`、`mutation`。 调用`bound_check_fixture`、`pytest.raises`、`agent.check_candidate`、`time.monotonic`、`pytest.mark.parametrize`、`p.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_check_deadline_interrupts_exception_handlers_and_runs_cleanup`（L258–L276）：接收`monkeypatch`。 控制顺序：L276断言`events == ["cleanup"] and time.monotonic() - start < 1`。 调用`monkeypatch.setattr`、`time.monotonic`、`pytest.raises`、`sandbox._execute_payload`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_check_deadline_interrupts_exception_handlers_and_runs_cleanup.work`（L263–L270）：接收`payload`。 调用`time.sleep`、`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_final_oracle_rejection_does_not_reopen_agent_budget`（L279–L291）：接收`settings`、`store`、`monkeypatch`。 调用`Workflow`、`design`、`monkeypatch.setattr`、`pytest.raises`、`workflow.extension_after_verify`、`workflow.extension_after_aggregate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline`（L295–L321）：接收`settings`、`tmp_path`、`monkeypatch`、`phase`。 控制顺序：L309按`phase == "check"`分支；L320断言`len(requests) == 2 and cleaned == [True]`；L321断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`exercise`、`pytest.raises`、`run`、`len`、`(tmp_path / "worker/agent-result.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline.expire`（L299–L300）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline.delayed`（L312–L315）：接收`*args`。 调用`original`、`expire`。 返回路径：L315的`value`。
- `test_internal_success_is_not_ledger_acceptance`（L324–L340）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L339断言`ledger._load()["version"] == 0`；L340断言`len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`run`、`design`、`ProductLedger`、`ledger.baseline`、`apply_candidate`、`plan.selection.model_dump`、`pytest.raises`、`ledger.promote`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_completed_business_assertions_are_repairable`（L344–L357）：接收`status`、`body`、`error`。 调用`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`httpx.ByteStream`、`pytest.raises`、`run_steps`、`HttpStep`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_failure_is_not_business_repair`（L360–L374）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L374断言`not isinstance(error.value, BusinessCheckFailure)`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.raises`、`run_steps`、`HttpStep`、`isinstance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_failure_is_not_business_repair.timeout`（L366–L367）：接收`request`。 控制顺序：L367抛异常，停止当前正常路径。 调用`httpx.ReadTimeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_startup_classification_never_turns_infrastructure_into_repair`（L390–L430）：接收`mutation`、`repairable`。 控制顺序：L430断言`("repairable_failure" in scope["receipt"]) is repairable`。 调用`ast.parse`、`inspect.getsource`、`next`、`ast.walk`、`isinstance`、`any`、`exec`、`compile`、`ast.Module`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sdk_download_retains_integer_overload_with_remaining_deadline`（L433–L455）：接收`monkeypatch`。 控制顺序：L451断言`set(env.snapshot(task.allowed_paths)) == set(task.allowed_paths)`；L452断言`len(calls) == len(task.allowed_paths)`。 调用`design`、`coding.DaytonaFiles`、`SimpleNamespace`、`time.monotonic`、`set`、`env.snapshot`、`len`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sdk_download_retains_integer_overload_with_remaining_deadline.download`（L440–L443）：接收`path`、`timeout`。 控制顺序：L441断言`type(timeout) is int and 0 < timeout <= 12`。 调用`type`、`calls.append`。 返回路径：L443的`b"# fixture\n"`。
- `test_actual_verifier_timeout_handler_preserves_owned_cleanup`（L460–L518）：接收`tmp_path`、`delete_fails`、`monkeypatch`。 控制顺序：L513断言`deleted == ["owned"]`；L514断言`len(timers) == 1 and 0 < timers[0] <= 10`；L515断言`receipt["kind"] == "checkpoint_timeout" and receipt["passed"] is False`；L516断言`receipt["cleanup"] == ("delete-failed" if delete_fails else "deleted")`；L517断言`"repairable_failure" not in receipt`；L518断言`"private" not in json.dumps(receipt)`。 调用`monkeypatch.setattr`、`timers.append`、`ast.parse`、`inspect.getsource`、`next`、`isinstance`、`ast.Try`、`ast.Raise`、`ast.Name`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_verifier_timeout_handler_preserves_owned_cleanup.delete`（L481–L484）：接收`value`、`**kwargs`。 控制顺序：L483按`delete_fails`分支；L484抛异常，停止当前正常路径。 调用`deleted.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_mini_swe_checkpoints.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L518。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18855`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_mini_swe_checkpoints.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "264dd3e231ab81151f2d75bbde069761f8820a1765d7330c9a0b91a7f6a06f97"} -->
````python
# tests/test_mini_swe_checkpoints.py
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


@pytest.mark.skipif(not hasattr(signal, "setitimer"), reason="checkpoint requires Linux timer")
def test_check_deadline_interrupts_exception_handlers_and_runs_cleanup(monkeypatch):
    from workbench import capability_sandbox as sandbox

    events = []

    def work(payload):
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
        ({"output_hints": ["missing-module"]}, False),
        ({"command_exit_status": "unknown"}, False),
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
    monkeypatch.setattr(signal, "setitimer", lambda kind, seconds: timers.append(seconds))

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

    scope = {
        **vars(sandbox),
        "injected": sandbox.CheckpointExpired("fixed timeout"),
        "diagnostic_error": None,
        "oracle_adapter": None,
        "native": False,
        "checkpoint": {"nonce": "fixture", "deadline": time.monotonic() + 10},
        "name": "owned",
        "receipt": {
            "passed": False,
            "cleanup": "pending",
            "repairable_failure": "application_startup",
        },
        "sandbox": SimpleNamespace(id="owned"),
        "client": SimpleNamespace(delete=delete),
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
    assert len(timers) == 1 and 0 < timers[0] <= 10
    assert receipt["kind"] == "checkpoint_timeout" and receipt["passed"] is False
    assert receipt["cleanup"] == ("delete-failed" if delete_fails else "deleted")
    assert "repairable_failure" not in receipt
    assert "private" not in json.dumps(receipt)
````
