# tests/test_native_sandbox_route_gate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.delivery`、`workbench.generation.python_basic`、`workbench.infrastructure.native`、`workbench.infrastructure.processes.tools`、`workbench.infrastructure.sandbox.daytona`、`workbench.production`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configure`（L18–L25）：接收`settings`、`sandbox_config`。 调用`SecretStr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `design_flow`（L28–L57）：接收`settings`、`plan`、`monkeypatch`、`template`。 调用`SimpleNamespace`、`monkeypatch.setattr`、`graph.Workflow`、`plan.model_copy`、`approved.model_dump`、`requirement().model_dump`、`requirement`。 返回路径：L57的`flow, state, gates, approved`。
- `design_flow.gate`（L42–L44）：接收`state`、`stage`、`data`、`actions`、`can_approve`。 调用`gates.append`。 返回路径：L44的`{"decision": "approve" if can_approve else "reject"}`。
- `test_native_design_allows_later_service_source_fallback`（L63–L107）：接收`settings`、`plan`、`monkeypatch`、`template`、`sandbox_config`、`missing`。 控制顺序：L76断言`flow.design(state)["decision"] == "approve"`；L77断言`gates[0][3] is True`；L78断言`"sandbox_configuration" not in gates[0][1]["block_sources"]`；L79断言`"approve" in gates[0][2]`；L102断言`result["execution"] == "source-candidate"`；L103断言`len(calls) == 1`；L107断言`flow.after_verify(state) == "package"`。 调用`configure`、`design_flow`、`monkeypatch.setitem`、`SimpleNamespace`、`monkeypatch.setattr`、`pytest.fail`、`flow.design`、`calls.append`、`native.managed_generate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_design_allows_later_service_source_fallback.unavailable`（L85–L92）：接收`*args`。 控制顺序：L92抛异常，停止当前正常路径。 调用`ToolFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_python_design_still_requires_daytona_configuration`（L111–L118）：接收`settings`、`plan`、`monkeypatch`、`sandbox_config`。 控制顺序：L116断言`flow.design(state)["decision"] == "reject"`；L117断言`gates[0][3] is False`；L118断言`"sandbox_configuration" in gates[0][1]["block_sources"]`。 调用`configure`、`design_flow`、`flow.design`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_native_sandbox_revalidates_before_execution`（L123–L134）：接收`settings`、`monkeypatch`、`template`、`sandbox_config`。 调用`configure`、`monkeypatch.setattr`、`pytest.fail`、`graph.Workflow`、`pytest.raises`、`flow.sandbox`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_native_capability_still_blocks_design`（L138–L144）：接收`settings`、`plan`、`monkeypatch`、`available`。 控制顺序：L142断言`flow.design(state)["decision"] == "reject"`；L143断言`"native_validation_or_runtime" in gates[0][1]["block_sources"]`；L144断言`"sandbox_configuration" not in gates[0][1]["block_sources"]`。 调用`configure`、`design_flow`、`monkeypatch.setattr`、`flow.design`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_sandbox_route_gate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L144。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5942`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_sandbox_route_gate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f6bba42a0cee7a09a6922445b08b778dae035fea0bf94bf6323ef8f7f44a955e"} -->
````python
# tests/test_native_sandbox_route_gate.py
"""Native service fallback must not depend on unused Daytona configuration."""

import sys
from types import SimpleNamespace

import pytest
from conftest import requirement
from pydantic import SecretStr

from workbench.delivery import native, source_candidate
from workbench.generation.python_basic import PrerequisiteError
from workbench.infrastructure.native import resources
from workbench.infrastructure.processes.tools import ToolFailure
from workbench.infrastructure.sandbox.daytona import verification
from workbench.production import graph


def configure(settings, sandbox_config):
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = sandbox_config == "missing-snapshot"
    settings.daytona_api_url = "http://127.0.0.1:3000/api"
    settings.daytona_api_key = SecretStr("test-only-not-a-credential")
    settings.daytona_target = "local"
    settings.daytona_snapshot = ""
    settings.daytona_snapshots = {}


def design_flow(settings, plan, monkeypatch, template):
    selection = SimpleNamespace(
        capabilities=lambda: {"field_kinds": ["text", "integer", "boolean"]},
        model_dump=lambda: {"template": template},
    )
    monkeypatch.setattr(graph, "options_for_run", lambda run: selection)
    monkeypatch.setattr(graph, "coverage_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "business_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "design_pack", lambda *args, **kwargs: {"tasks": []})
    monkeypatch.setattr(native, "generation_capability", lambda *args: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    flow = graph.Workflow(settings, SimpleNamespace(get_run=lambda run: {}), None)
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((stage, data, actions, can_approve))
        return {"decision": "approve" if can_approve else "reject"}

    flow.gate = gate
    approved = (
        plan if template == "python-basic" else plan.model_copy(update={"data_scope": "shared"})
    )
    state = {
        "run_id": "native-route",
        "template": template,
        "round": 1,
        "plan": approved.model_dump(),
        "requirement": requirement().model_dump(),
    }
    return flow, state, gates, approved


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
@pytest.mark.parametrize("missing", ["docker", "compose", "daemon"])
def test_native_design_allows_later_service_source_fallback(
    settings, plan, monkeypatch, template, sandbox_config, missing
):
    configure(settings, sandbox_config)
    flow, state, gates, approved = design_flow(settings, plan, monkeypatch, template)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    monkeypatch.setattr(
        verification,
        "validate_configuration",
        lambda *args: pytest.fail("Source fallback must not require Daytona configuration"),
    )
    assert flow.design(state)["decision"] == "approve"
    assert gates[0][3] is True
    assert "sandbox_configuration" not in gates[0][1]["block_sources"]
    assert "approve" in gates[0][2]

    monkeypatch.setattr(
        resources.shutil, "which", lambda name: None if missing == "docker" else "docker"
    )

    def unavailable(*args):
        error = ToolFailure("service unavailable")
        error.log = (
            "docker: 'compose' is not a docker command."
            if missing == "compose"
            else "Cannot connect to the Docker daemon"
        )
        raise error

    monkeypatch.setattr(resources, "run_command", unavailable)
    calls = []
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *args: calls.append(args) or {"execution": "source-candidate"},
    )
    result = native.managed_generate(settings, template, approved, flow.product(state))
    assert result["execution"] == "source-candidate"
    assert len(calls) == 1
    state.update(
        native_generation=result, verification={"passed": False, "source_checks_passed": True}
    )
    assert flow.after_verify(state) == "package"


@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
def test_python_design_still_requires_daytona_configuration(
    settings, plan, monkeypatch, sandbox_config
):
    configure(settings, sandbox_config)
    flow, state, gates, _ = design_flow(settings, plan, monkeypatch, "python-basic")
    assert flow.design(state)["decision"] == "reject"
    assert gates[0][3] is False
    assert "sandbox_configuration" in gates[0][1]["block_sources"]


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
def test_actual_native_sandbox_revalidates_before_execution(
    settings, monkeypatch, template, sandbox_config
):
    configure(settings, sandbox_config)
    monkeypatch.setattr(
        verification,
        "verify_in_daytona",
        lambda *args: pytest.fail("Sandbox execution must remain gated"),
    )
    flow = graph.Workflow(settings, None, None)
    with pytest.raises(PrerequisiteError):
        flow.sandbox({"run_id": "runtime-route", "template": template})


@pytest.mark.parametrize("available", [None, 0, "yes"])
def test_unknown_native_capability_still_blocks_design(settings, plan, monkeypatch, available):
    configure(settings, "unapproved")
    flow, state, gates, _ = design_flow(settings, plan, monkeypatch, "fastapiadmin")
    monkeypatch.setattr(native, "generation_capability", lambda *args: {"available": available})
    assert flow.design(state)["decision"] == "reject"
    assert "native_validation_or_runtime" in gates[0][1]["block_sources"]
    assert "sandbox_configuration" not in gates[0][1]["block_sources"]
````
