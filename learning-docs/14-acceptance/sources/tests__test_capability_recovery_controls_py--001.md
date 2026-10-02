# tests/test_capability_recovery_controls.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`、`workbench.recommendation`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `gate_data`（L14–L26）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`requirement(["请明确参与者入口与报名范围"]).gate_dump`、`requirement`。 返回路径：L15的`{ "requirement": requirement(["请明确参与者入口与报名范围"]).gate_dump(), "ready": False, "blocked": ["…`。
- `test_known_scope_gate_keeps_identity_and_does_not_queue_recommendation`（L29–L54）：接收`settings`、`store`。 控制顺序：L35遍历`range(3)`；L37断言`result["status"] == "BLOCKED"`；L38断言`"未发起新的模型请求" in result["message"]`；L39断言`store.claim() is None`；L40断言`store.get_run(run)["pending"] == gate`；L41断言`store.messages(run) == before`；L50断言`store.claim() is None`；L53断言`store.messages(run)[-1]["content"] == answer`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`store.claim`、`store.gate`、`gate_data`、`store.finish`、`store.messages`、`range`、`store.set_automation`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_scope_report_explains_paths_without_claiming_retry_can_fix_capabilities`（L57–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L59断言`report["attempts"] == 0`；L60断言`report["retry_without_changes"] is False`；L61断言`report["alternatives"] == ["明确参与者登录后的操作", "明确仅需管理员维护"]`；L62断言`not report["can_approve"]`。 调用`blocked_report`、`gate_data`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_does_not_resubmit_known_scope_for_smart_or_retry`（L65–L100）：接收`monkeypatch`。 控制顺序：L94断言`result.exit_code == 0`；L95断言`"原始目标已保留" in result.output`；L96断言`"未发送新的模型请求" in result.output`；L98断言`writes == [ ("POST", "/runs/old-run/resume", {"gate_id": "a" * 64, "action": "answer"…`。 调用`gate_data`、`monkeypatch.setattr`、`CliRunner().invoke`、`CliRunner`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cli_does_not_resubmit_known_scope_for_smart_or_retry.client`（L77–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`object`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_cli_does_not_resubmit_known_scope_for_smart_or_retry.api_call`（L80–L86）：接收`client`、`method`、`path`、`body`。 控制顺序：L83按`method == "GET"`分支。 调用`calls.append`。 返回路径：L84的`{"status": status, "error": "需要范围选择", "pending": gate}`；L86的`{}`。

</details>

**创建路径：** `tests/test_capability_recovery_controls.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L100。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3963`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_recovery_controls.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "193fb7266eff08efb6a7d2d5e2b73c2f95cd8ebcbdee730313b470a8484a62c8"} -->
````python
# tests/test_capability_recovery_controls.py
"""A known scope decision cannot be delegated away by retrying the same gate."""

from contextlib import contextmanager

import pytest
from conftest import new_run, requirement
from typer.testing import CliRunner

from workbench import cli
from workbench.recommendation import blocked_report
from workbench.store import Conflict


def gate_data():
    return {
        "requirement": requirement(["请明确参与者入口与报名范围"]).gate_dump(),
        "ready": False,
        "blocked": ["参与者自行提交不能自动改为管理员录入"],
        "capability_conflicts": [
            {
                "code": "registration_scope_confirmation",
                "message": "参与者自行提交不能自动改为管理员录入",
                "alternatives": ["明确参与者登录后的操作", "明确仅需管理员维护"],
            }
        ],
    }


def test_known_scope_gate_keeps_identity_and_does_not_queue_recommendation(settings, store):
    run = new_run(store)
    job = store.claim()
    gate = store.gate(run, "clarification", 4, gate_data(), ["answer", "reject"], False)
    store.finish(job, "BLOCKED", pending=gate, error="需要范围选择")
    before = store.messages(run)
    for index in range(3):
        result = store.set_automation(run, True, f"repeat-smart-{index}")
        assert result["status"] == "BLOCKED"
        assert "未发起新的模型请求" in result["message"]
        assert store.claim() is None
        assert store.get_run(run)["pending"] == gate
        assert store.messages(run) == before
    with pytest.raises(Conflict, match="范围选择"):
        store.submit(
            run,
            {"gate_id": gate["gate_id"], "action": "recommend", "approved": True},
            "direct-recommend",
        )
    with pytest.raises(Conflict, match="范围选择"):
        store.retry(run, "repeat-retry")
    assert store.claim() is None
    answer = "保留参赛者自行提交的目标，需要登录后的参赛者入口，不要求匿名访问"
    store.submit(run, {"gate_id": gate["gate_id"], "action": "answer", "text": answer}, "scope")
    assert store.messages(run)[-1]["content"] == answer
    assert store.claim()["payload"]["gate_id"] == gate["gate_id"]


def test_scope_report_explains_paths_without_claiming_retry_can_fix_capabilities():
    report = blocked_report({"stage": "clarification", "gate_id": "a" * 64, "data": gate_data()}, 0)
    assert report["attempts"] == 0
    assert report["retry_without_changes"] is False
    assert report["alternatives"] == ["明确参与者登录后的操作", "明确仅需管理员维护"]
    assert not report["can_approve"]


def test_cli_does_not_resubmit_known_scope_for_smart_or_retry(monkeypatch):
    calls = []
    status = "BLOCKED"
    gate = {
        "stage": "clarification",
        "gate_id": "a" * 64,
        "can_approve": False,
        "actions": ["answer", "reject", "recommend"],
        "data": gate_data(),
    }

    @contextmanager
    def client():
        yield object()

    def api_call(client, method, path, body=None):
        nonlocal status
        calls.append((method, path, body))
        if method == "GET":
            return {"status": status, "error": "需要范围选择", "pending": gate}
        status = "READY"
        return {}

    monkeypatch.setattr(cli, "client", client)
    monkeypatch.setattr(cli, "api_call", api_call)
    answer = "保留自行报名，先讨论登录后的参赛者入口"
    result = CliRunner().invoke(
        cli.app, ["chat", "--run", "old-run"], input=f"智能推荐\n重试\n{answer}\n"
    )
    assert result.exit_code == 0, result.output
    assert "原始目标已保留" in result.output
    assert "未发送新的模型请求" in result.output
    writes = [call for call in calls if call[0] == "POST"]
    assert writes == [
        ("POST", "/runs/old-run/resume", {"gate_id": "a" * 64, "action": "answer", "text": answer})
    ]
````
