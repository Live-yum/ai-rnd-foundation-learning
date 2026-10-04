# tests/test_capability_browser_oom_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_memory_diagnostics_never_release_raw_errors_output_or_unknown_state`（L12–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L26断言`result == { "phase": "memory_exhaustion", "timed_out": False, "inspection_failed": Fa…`；L39断言`"secret" not in json.dumps(result)`；L40断言`len(json.dumps(result)) < 512`。 调用`probe.memory_probe_diagnostic`、`SimpleNamespace`、`json.dumps`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_memory_state_can_only_produce_empty_finite_facts`（L44–L48）：接收`state`。 控制顺序：L46断言`result["container_status"] == "other"`；L47断言`result["container_oom_killed"] is None`；L48断言`"secret" not in json.dumps(result)`。 调用`probe.memory_probe_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup`（L64–L150）：接收`monkeypatch`、`tmp_path`、`case`、`oom`、`running`、`exit_code`。 控制顺序：L136按`case == "genuine_oom"`分支；L142断言`report["passed"] is (case == "genuine_oom")`；L143断言`report["checks"].get("memory_exhaustion") is (True if case == "genuine_oom" else None…`；L144断言`operations == ["memory_start", "final_cleanup", "server_shutdown", "server_close"]`；L145断言`"secret" not in json.dumps(report)`；L146按`case != "genuine_oom"`分支；L147断言`report["diagnostic"]["timed_out"] is (case == "timeout")`；L148断言`report["diagnostic"]["inspection_failed"] is ( case in {"inspect_failure", "malformed…`。 调用`SimpleNamespace`、`operations.append`、`monkeypatch.setattr`、`probe.main`、`pytest.raises`、`json.loads`、`(tmp_path / "reports/capability-browser-isolation.json").read_byt…`、`report["checks"].get`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.run`（L98–L108）：接收`args`、`timeout`。 控制顺序：L100按`"inspect" in args`分支；L102按`inspections == 3 and case == "inspect_failure"`分支；L103抛异常，停止当前正常路径；L106按`"start" in args`分支。 调用`RuntimeError`、`json.dumps([{"State": value}]).encode`、`json.dumps`。 返回路径：L105的`json.dumps([{"State": value}]).encode()`；L107的`b"{}"`；L108的`b""`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.process`（L110–L120）：接收`args`、`**kwargs`。 控制顺序：L111按`"start" in args`分支；L113断言`kwargs["timeout"] == 30`；L114按`case == "timeout"`分支；L115抛异常，停止当前正常路径；L117断言`"rm" in args and "-f" in args`；L119断言`kwargs["timeout"] == 15`。 调用`operations.append`、`subprocess.TimeoutExpired`、`SimpleNamespace`。 返回路径：L116的`SimpleNamespace(returncode=exit_code, stdout=b"secret", stderr=b"secret")`；L120的`SimpleNamespace(returncode=0)`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.browser`（L122–L131）：接收`url`、`token`、`scenarios`、`*args`。 控制顺序：L124按`mode == "positive"`分支；L131抛异常，停止当前正常路径。 调用`probe.BrowserFailure`。 返回路径：L125的`[True]`。

</details>

**创建路径：** `tests/test_capability_browser_oom_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L150。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5764`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_oom_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5c746d8ba9630867cb25dde90dcf65da9d2c93373d7eb84ebdb4cd7a2735f0e5"} -->
````python
# tests/test_capability_browser_oom_diagnostics.py
"""Bounded OOM diagnostics preserve rejection; mocked transport is not live proof."""

import json
import subprocess
from types import SimpleNamespace

import pytest

from scripts import ci_capability_browser_isolation as probe


def test_memory_diagnostics_never_release_raw_errors_output_or_unknown_state():
    result = probe.memory_probe_diagnostic(
        SimpleNamespace(returncode=2**100, stdout=b"secret stdout", stderr=b"secret stderr"),
        {
            "Status": "secret status",
            "Running": 0,
            "OOMKilled": 1,
            "ExitCode": True,
            "Dead": "secret",
            "Restarting": [],
            "Error": "secret Docker path and credentials",
            "Env": ["secret"],
        },
    )
    assert result == {
        "phase": "memory_exhaustion",
        "timed_out": False,
        "inspection_failed": False,
        "docker_start_returncode": None,
        "container_status": "other",
        "container_running": None,
        "container_oom_killed": None,
        "container_exit_code": None,
        "container_dead": None,
        "container_restarting": None,
        "container_error_present": True,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 512


@pytest.mark.parametrize("state", [None, [], "secret", 1, True])
def test_malformed_memory_state_can_only_produce_empty_finite_facts(state):
    result = probe.memory_probe_diagnostic(None, state)
    assert result["container_status"] == "other"
    assert result["container_oom_killed"] is None
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "case,oom,running,exit_code",
    [
        ("genuine_oom", True, False, 137),
        ("node_abort", False, False, 134),
        ("unproven_sigkill", False, False, 137),
        ("still_running", True, True, 137),
        ("start_failure", False, False, 125),
        ("timeout", False, True, 0),
        ("inspect_failure", False, False, 0),
        ("malformed_state", False, False, 0),
    ],
)
def test_oom_gate_preserves_original_proof_budget_and_cleanup(
    monkeypatch, tmp_path, case, oom, running, exit_code
):
    image = "sha256:" + "a" * 64
    operations = []
    inspections = 0
    state = {
        "Status": "running" if running else "exited",
        "Running": running,
        "OOMKilled": oom,
        "ExitCode": exit_code,
        "Error": "secret internal runtime path",
        "Dead": False,
        "Restarting": False,
    }
    server = SimpleNamespace(
        server_port=1234,
        serve_forever=lambda: None,
        shutdown=lambda: operations.append("server_shutdown"),
        server_close=lambda: operations.append("server_close"),
    )
    monkeypatch.setattr(probe, "ROOT", tmp_path)
    monkeypatch.setattr(probe, "browser_image_identity", lambda: image)
    monkeypatch.setattr(probe, "browser_source_identity", lambda: {})
    monkeypatch.setattr(probe, "runtime_identity", lambda image: {})
    monkeypatch.setattr(probe, "selected_policy", lambda: None)
    monkeypatch.setattr(probe, "require_image_sources", lambda name: {})
    monkeypatch.setattr(probe, "require_worker_inspection", lambda *args: None)
    monkeypatch.setattr(probe, "worker_command", lambda image, name: ["docker", "create", image])
    monkeypatch.setattr(probe, "ThreadingHTTPServer", lambda *args: server)
    monkeypatch.setattr(
        probe.threading, "Thread", lambda **kwargs: SimpleNamespace(start=lambda: None)
    )

    def run(args, timeout=30):
        nonlocal inspections
        if "inspect" in args:
            inspections += 1
            if inspections == 3 and case == "inspect_failure":
                raise RuntimeError("secret inspection failure")
            value = [] if case == "malformed_state" else state
            return json.dumps([{"State": value}]).encode()
        if "start" in args:
            return b"{}"
        return b""

    def process(args, **kwargs):
        if "start" in args:
            operations.append("memory_start")
            assert kwargs["timeout"] == 30
            if case == "timeout":
                raise subprocess.TimeoutExpired(args, 30, output=b"secret output")
            return SimpleNamespace(returncode=exit_code, stdout=b"secret", stderr=b"secret")
        assert "rm" in args and "-f" in args
        operations.append("final_cleanup")
        assert kwargs["timeout"] == 15
        return SimpleNamespace(returncode=0)

    def browser(url, token, scenarios, *args):
        mode = scenarios[0].id
        if mode == "positive":
            return [True]
        diagnostic = (
            {"error_code": "application-error"}
            if mode == "error"
            else {"error_type": "TimeoutError"}
        )
        raise probe.BrowserFailure(diagnostic)

    monkeypatch.setattr(probe, "run", run)
    monkeypatch.setattr(probe.subprocess, "run", process)
    monkeypatch.setattr(probe, "run_isolated_browser", browser)
    if case == "genuine_oom":
        probe.main()
    else:
        with pytest.raises((RuntimeError, ValueError, subprocess.TimeoutExpired)):
            probe.main()
    report = json.loads((tmp_path / "reports/capability-browser-isolation.json").read_bytes())
    assert report["passed"] is (case == "genuine_oom")
    assert report["checks"].get("memory_exhaustion") is (True if case == "genuine_oom" else None)
    assert operations == ["memory_start", "final_cleanup", "server_shutdown", "server_close"]
    assert "secret" not in json.dumps(report)
    if case != "genuine_oom":
        assert report["diagnostic"]["timed_out"] is (case == "timeout")
        assert report["diagnostic"]["inspection_failed"] is (
            case in {"inspect_failure", "malformed_state"}
        )
````
