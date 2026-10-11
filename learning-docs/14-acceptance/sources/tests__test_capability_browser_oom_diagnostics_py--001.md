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
- `test_oom_gate_preserves_original_proof_budget_and_cleanup`（L67–L250）：接收`monkeypatch`、`tmp_path`、`case`、`oom`、`running`、`exit_code`、`observation`。 控制顺序：L75按`observation == "write_failure"`分支；L196按`case == "genuine_oom"`分支；L202断言`"memory_observation" not in report`；L204按`observation == "write_failure"`分支；L205断言`not sidecar.exists()`；L208断言`set(diagnostic) == {"memory_observation"}`；L209断言`"secret" not in json.dumps(diagnostic)`；L210按`observation == "oom_counters"`分支。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setattr`、`SimpleNamespace`、`operations.append`、`isolation.image_source_identity`、`probe.main`、`pytest.raises`、`json.loads`、`(tmp_path / "reports/capability-browser-isolation.json").read_byt…`、`sidecar.exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.fail_sidecar`（L78–L81）：接收`path`、`data`。 控制顺序：L79按`path.name == "capability-browser-memory-diagnostic.json"`分支；L80抛异常，停止当前正常路径。 调用`PermissionError`、`write_json`。 返回路径：L81的`write_json(path, data)`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.Observer`（L85–L100）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.Observer.__init__`（L86–L87）：接收`*args`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.Observer.start`（L89–L90）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.Observer.finish`（L92–L100）：接收`stopped`。 控制顺序：L94断言`stopped is (not running and case not in {"inspect_failure", "malformed_state"})`；L95按`observation == "finish_failure"`分支；L96抛异常，停止当前正常路径。 调用`operations.append`、`RuntimeError`。 返回路径：L97的`{ "available": observation == "oom_counters", "observed_delta": {"oom_kill": 1} if observa…`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.run`（L138–L168）：接收`args`、`timeout`。 控制顺序：L140按`"-e" in args`分支；L141断言`args[args.index("-e") + 1] == "const a=[];while(true)a.push(Buffer.alloc(16*1024*1024…`；L145按`"inspect" in args`分支；L147按`inspections == 3`分支；L148断言`"diagnostic_finished" not in operations`；L149按`inspections == 3 and case == "inspect_failure"`分支；L150抛异常，停止当前正常路径；L153按`"start" in args`分支。 调用`args.index`、`RuntimeError`、`json.dumps([{"State": value}]).encode`、`json.dumps`、`json.dumps( { key: True for key in ( "passed", "kernel_resource_l…`。 返回路径：L152的`json.dumps([{"State": value}]).encode()`；L154的`json.dumps( { key: True for key in ( "passed", "kernel_resource_limits", "network_none", "…`；L168的`b""`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.process`（L170–L180）：接收`args`、`**kwargs`。 控制顺序：L171按`"start" in args`分支；L173断言`kwargs["timeout"] == 30`；L174按`case == "timeout"`分支；L175抛异常，停止当前正常路径；L177断言`"rm" in args and "-f" in args`；L179断言`kwargs["timeout"] == 15`。 调用`operations.append`、`subprocess.TimeoutExpired`、`SimpleNamespace`。 返回路径：L176的`SimpleNamespace(returncode=exit_code, stdout=b"secret", stderr=b"secret")`；L180的`SimpleNamespace(returncode=0)`。
- `test_oom_gate_preserves_original_proof_budget_and_cleanup.browser`（L182–L191）：接收`url`、`token`、`scenarios`、`*args`。 控制顺序：L184按`mode == "positive"`分支；L191抛异常，停止当前正常路径。 调用`probe.BrowserFailure`。 返回路径：L185的`[True]`。

</details>

**创建路径：** `tests/test_capability_browser_oom_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L250。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9786`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_oom_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cf031c51d4a5c8a7fb8283a73f419719fbae87bb613021eb337825fa025bcd22"} -->
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
@pytest.mark.parametrize(
    "observation", ["unavailable", "oom_counters", "finish_failure", "write_failure"]
)
def test_oom_gate_preserves_original_proof_budget_and_cleanup(
    monkeypatch, tmp_path, case, oom, running, exit_code, observation
):
    from scripts import browser_memory_observation
    from workbench import capability_browser_isolation as isolation

    image = "sha256:" + "a" * 64
    operations = []
    if observation == "write_failure":
        write_json = probe.write_json

        def fail_sidecar(path, data):
            if path.name == "capability-browser-memory-diagnostic.json":
                raise PermissionError("secret sidecar write failure")
            return write_json(path, data)

        monkeypatch.setattr(probe, "write_json", fail_sidecar)

    class Observer:
        def __init__(self, *args):
            pass

        def start(self):
            pass

        def finish(self, *, stopped):
            operations.append("diagnostic_finished")
            assert stopped is (not running and case not in {"inspect_failure", "malformed_state"})
            if observation == "finish_failure":
                raise RuntimeError("secret diagnostic failure")
            return {
                "available": observation == "oom_counters",
                "observed_delta": {"oom_kill": 1} if observation == "oom_counters" else None,
            }

    monkeypatch.setattr(browser_memory_observation, "MemoryObservation", Observer)
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
    monkeypatch.setattr(
        isolation, "BROWSER_ACCEPTANCE", tmp_path / "reports/capability-browser-isolation.json"
    )
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: {})
    monkeypatch.setattr(isolation, "selected_policy", lambda: None)
    monkeypatch.setattr(probe, "runtime_identity", lambda image: {})
    monkeypatch.setattr(probe, "selected_policy", lambda: None)
    monkeypatch.setattr(
        probe, "require_image_sources", lambda name: isolation.image_source_identity()
    )
    monkeypatch.setattr(probe, "require_worker_inspection", lambda *args: None)
    monkeypatch.setattr(probe, "worker_command", lambda image, name: ["docker", "create", image])
    monkeypatch.setattr(probe, "ThreadingHTTPServer", lambda *args: server)
    monkeypatch.setattr(
        probe.threading, "Thread", lambda **kwargs: SimpleNamespace(start=lambda: None)
    )

    def run(args, timeout=30):
        nonlocal inspections
        if "-e" in args:
            assert (
                args[args.index("-e") + 1]
                == "const a=[];while(true)a.push(Buffer.alloc(16*1024*1024,255))"
            )
        if "inspect" in args:
            inspections += 1
            if inspections == 3:
                assert "diagnostic_finished" not in operations
            if inspections == 3 and case == "inspect_failure":
                raise RuntimeError("secret inspection failure")
            value = [] if case == "malformed_state" else state
            return json.dumps([{"State": value}]).encode()
        if "start" in args:
            return json.dumps(
                {
                    key: True
                    for key in (
                        "passed",
                        "kernel_resource_limits",
                        "network_none",
                        "tmpfs_exhaustion",
                        "pid_exhaustion",
                        "readonly_root",
                        "browser_build",
                    )
                }
            ).encode()
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
    assert "memory_observation" not in report
    sidecar = tmp_path / "reports/capability-browser-memory-diagnostic.json"
    if observation == "write_failure":
        assert not sidecar.exists()
    else:
        diagnostic = json.loads(sidecar.read_bytes())
        assert set(diagnostic) == {"memory_observation"}
        assert "secret" not in json.dumps(diagnostic)
        if observation == "oom_counters":
            assert diagnostic["memory_observation"]["observed_delta"] == {"oom_kill": 1}
    if case == "genuine_oom":
        assert isolation.require_browser_acceptance(image) == image
        # Neither sidecar contents nor its presence grant acceptance authority.
        sidecar.write_text('{"passed":true,"memory_observation":{"secret":"ignored"}}')
        assert isolation.require_browser_acceptance(image) == image
        sidecar.unlink()
        assert isolation.require_browser_acceptance(image) == image
        for key, value in (
            ("unknown_field", True),
            ("memory_observation", {}),
            ("sources", {}),
            ("runtime", {"stale": True}),
            ("image_sources", {}),
            ("checks", {}),
            ("passed", 1),
            ("mocked", True),
        ):
            isolation.BROWSER_ACCEPTANCE.write_text(json.dumps({**report, key: value}))
            with pytest.raises(ValueError, match="missing, stale, or incomplete"):
                isolation.require_browser_acceptance(image)
        isolation.BROWSER_ACCEPTANCE.write_text(json.dumps(report))
    else:
        with pytest.raises(ValueError, match="missing, stale, or incomplete"):
            isolation.require_browser_acceptance(image)
    assert report["passed"] is (case == "genuine_oom")
    assert report["checks"].get("memory_exhaustion") is (True if case == "genuine_oom" else None)
    assert operations == [
        "memory_start",
        "diagnostic_finished",
        "final_cleanup",
        "server_shutdown",
        "server_close",
    ]
    assert "secret" not in json.dumps(report)
    if case != "genuine_oom":
        assert report["diagnostic"]["timed_out"] is (case == "timeout")
        assert report["diagnostic"]["inspection_failed"] is (
            case in {"inspect_failure", "malformed_state"}
        )
````
