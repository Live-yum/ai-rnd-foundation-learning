# tests/test_edit_and_submit.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding`、`workbench.coding.ports`、`workbench.coding.timing`、`workbench.core.contracts`、`workbench.errors`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_explicit_completion_preserves_legacy_flow`（L18–L35）：接收`settings`、`tmp_path`、`monkeypatch`、`combined`、`expected`。 控制顺序：L25断言`len(calls) == expected and len(checks) == 1 and cleaned == [True]`；L26断言`(product / "app.py").read_text() == "# baseline\n"`；L27断言`len(result.files) == 2`；L29断言`receipt["candidate_submitted"] is True`；L30断言`receipt["implementation_verified"] is False`；L31断言`receipt["budget"]["requests"] == 2 * expected`；L33断言`[t["operation"] for t in turns] == ( ["edit_and_submit"] if combined else ["edit", "s…`。 调用`exercise`、`run`、`len`、`(product / "app.py").read_text`、`json.loads`、`(tmp_path / "worker/agent-result.json").read_text`、`(tmp_path / "worker/agent-model-timings.json").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_failure_repairs_in_same_session`（L38–L53）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L43断言`len(calls) == len(checks) == 2 and cleaned == [True]`；L44断言`calls[1]["verification_feedback"] == { "passed": False, "source_digest": digest(check…`；L49断言`calls[1]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]`；L50断言`checks[0][1] == checks[1][1] and checks[0][0] != checks[1][0]`；L51断言`(product / "app.py").read_text() == "# baseline\n"`。 调用`exercise`、`run`、`len`、`digest`、`(product / "app.py").read_text`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_rejects_bad_files_before_checkpoint`（L57–L65）：接收`settings`、`tmp_path`、`monkeypatch`、`bad_edit`。 控制顺序：L63断言`len(calls) == 1 and checks == [] and cleaned == [True]`；L64断言`(product / "app.py").read_text() == "# baseline\n"`；L65断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`exercise`、`pytest.raises`、`run`、`len`、`(product / "app.py").read_text`、`(tmp_path / "worker/agent-result.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_partial_write_cannot_check_or_promote`（L68–L76）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L74断言`len(calls) == 1 and checks == [] and cleaned == [True]`；L75断言`(product / "app.py").read_text() == "# baseline\n"`；L76断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`exercise`、`pytest.raises`、`run`、`len`、`(product / "app.py").read_text`、`(tmp_path / "worker/agent-result.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_infrastructure_failure_cannot_repair`（L87–L94）：接收`settings`、`tmp_path`、`monkeypatch`、`failure`。 控制顺序：L93断言`len(calls) == len(checks) == 1 and cleaned == [True]`；L94断言`(product / "app.py").read_text() == "# baseline\n"`。 调用`exercise`、`pytest.raises`、`type`、`run`、`len`、`(product / "app.py").read_text`、`pytest.mark.parametrize`、`TimeoutError`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_rejects_replay_tamper_lateness_and_cleanup`（L98–L120）：接收`settings`、`tmp_path`、`monkeypatch`、`case`。 控制顺序：L118断言`len(checks) == 1 and cleaned == [True]`；L119断言`(product / "app.py").read_text() == "# baseline\n"`；L120断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`exercise`、`pytest.raises`、`run`、`len`、`(product / "app.py").read_text`、`(tmp_path / "worker/agent-result.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_rejects_replay_tamper_lateness_and_cleanup.expire`（L102–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_failed_candidates_keep_original_step_ceiling`（L123–L132）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L129断言`len(calls) == len(checks) == 8 and cleaned == [True]`；L131断言`receipt["requests"] == 16`；L132断言`len({deadline for _, deadline in checks}) == 1`。 调用`exercise`、`pytest.raises`、`run`、`len`、`json.loads`、`(tmp_path / "worker/agent-budget.json").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_both_edit_actions_require_complete_approved_files`（L136–L149）：接收`operation`。 控制顺序：L142断言`schema.model_validate(value).operation == operation`；L143遍历`([], value["edits"]["files"][:1], value["edits"]["files"] * 2)`。 调用`edit`、`approved_turn_schema`、`design`、`schema.model_validate`、`pytest.raises`、`AgentTurn`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_operation_receipt_projects_only_fixed_enum`（L152–L161）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L153遍历`["edit", "submit", "edit_and_submit", "private-content", True, {}…`；L155断言`result["operation"] == ( operation if type(operation) is str and operation in {"edit"…`；L160断言`"private-content" not in json.dumps(result)`；L161断言`"operation" not in timing_receipts([{}])[0]`。 调用`timing_receipts`、`type`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_checkpoint_rejects_replayed_nonce`（L164–L186）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L182断言`len(calls) == len(bindings) == 2 and cleaned == [True]`；L183断言`bindings[0]["nonce"] != bindings[1]["nonce"]`；L184断言`bindings[0]["deadline"] == bindings[1]["deadline"]`；L185断言`not (tmp_path / "worker/agent-result.json").exists()`；L186断言`(product / "app.py").read_text() == "# baseline\n"`。 调用`bound_check_fixture`、`exercise`、`monkeypatch.setattr`、`pytest.raises`、`run`、`len`、`(tmp_path / "worker/agent-result.json").exists`、`(product / "app.py").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_checkpoint_rejects_replayed_nonce.replay`（L170–L173）：接收`proof`。 控制顺序：L172按`len(bindings) > 1`分支。 调用`bindings.append`、`dict`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_atomic_local_write_failure_keeps_baseline`（L189–L210）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L207断言`len(writes) == 2 and len(calls) == 1 and checks == [] and cleaned == [True]`；L208断言`(product / "app.py").read_text() == "# baseline\n"`；L209断言`not (tmp_path / "worker/step-1").exists()`；L210断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`monkeypatch.setattr`、`exercise`、`pytest.raises`、`run`、`len`、`(product / "app.py").read_text`、`(tmp_path / "worker/step-1").exists`、`(tmp_path / "worker/agent-result.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_atomic_local_write_failure_keeps_baseline.failed_second_write`（L195–L199）：接收`path`、`content`。 控制顺序：L197按`len(writes) == 2`分支；L198抛异常，停止当前正常路径。 调用`writes.append`、`len`、`OSError`、`original_write`。 返回路径：L199的`original_write(path, content)`。
- `test_worker_cannot_change_or_replay_model_operation`（L214–L254）：接收`settings`、`tmp_path`、`monkeypatch`、`mode`。 控制顺序：L252断言`len(calls) == 1 and len(checks) == (1 if mode == "replay" else 0)`；L253断言`cleaned == [True] and (product / "app.py").read_text() == "# baseline\n"`；L254断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`wrapper.write_text`、`str`、`monkeypatch.setattr`、`SimpleNamespace`、`exercise`、`pytest.raises`、`run`、`len`、`(product / "app.py").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_cannot_change_or_replay_model_operation.launch`（L238–L240）：接收`args`、`**kwargs`。 控制顺序：L239断言`args[1:] == ["-I", str(original_worker)]`。 调用`str`、`subprocess.Popen`。 返回路径：L240的`subprocess.Popen([args[0], "-I", str(wrapper)], **kwargs)`。

</details>

**创建路径：** `tests/test_edit_and_submit.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L254。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10290`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_edit_and_submit.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1bf271d611d53755139029676239e8ef59f18c1402f18c2bff07d7d160285b3d"} -->
````python
# tests/test_edit_and_submit.py
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
````
