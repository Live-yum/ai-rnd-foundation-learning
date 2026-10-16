# tests/test_native_service_failures.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.delivery`、`workbench.infrastructure.native`、`workbench.infrastructure.processes`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_service_exit_classification_uses_real_tool_failure`（L27–L38）：接收`tmp_path`、`monkeypatch`、`diagnostic`、`expected`。 控制顺序：L38断言`type(failure.value) is expected`。 调用`monkeypatch.setattr`、`pytest.raises`、`resources.start_services`、`type`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_service_exit_classification_uses_real_tool_failure.command`（L30–L33）：接收`*args`。 调用`tools.run_command`。 返回路径：L31的`tools.run_command( [sys.executable, "-c", f"import sys; print({diagnostic!r}); sys.exit(1)…`。
- `test_managed_generation_only_downgrades_classified_service_unavailability`（L42–L77）：接收`settings`、`monkeypatch`、`known_unavailable`。 控制顺序：L69按`known_unavailable`分支；L70断言`native.managed_generate(settings, "fastapiadmin", native_plan(), product) == { "candi…`；L73断言`len(calls) == 1`；L77断言`calls == []`。 调用`monkeypatch.setattr`、`monkeypatch.setitem`、`SimpleNamespace`、`resources.NativeServiceUnavailable`、`tools.ToolFailure`、`calls.append`、`native.managed_generate`、`native_plan`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_managed_generation_only_downgrades_classified_service_unavailability.fail`（L58–L59）：接收`*args`。 控制顺序：L59抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `rule_plan`（L80–L92）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`native_plan`、`CustomRule`。 返回路径：L92的`plan`。
- `test_unavailable_rule_coder_retains_source_before_any_runtime_effect`（L98–L120）：接收`settings`、`monkeypatch`、`engine`、`enabled`。 控制顺序：L116断言`result["execution"] == "source-candidate"`；L117断言`result["generation_status"] == "partial"`；L118断言`result["runtime_verified"] is False`；L119断言`"CODING_ENGINE=aider" in result["runtime_unavailable_reason"]`；L120断言`result["pending_steps"]`。 调用`monkeypatch.setattr`、`native.managed_generate`、`rule_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unavailable_rule_coder_retains_source_before_any_runtime_effect.forbidden`（L106–L107）：接收`*args`。 控制顺序：L107抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_available_rule_coder_reaches_strict_runtime_path`（L123–L141）：接收`settings`、`monkeypatch`。 控制顺序：L141断言`not product.exists()`。 调用`monkeypatch.setattr`、`monkeypatch.setitem`、`SimpleNamespace`、`pytest.raises`、`native.managed_generate`、`rule_plan`、`product.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_available_rule_coder_reaches_strict_runtime_path.reached`（L134–L135）：接收`*args`。 控制顺序：L135抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_docker_has_no_service_filesystem_side_effect`（L144–L148）：接收`settings`、`monkeypatch`。 控制顺序：L148断言`not (settings.data_dir / "native-services/missing-docker").exists()`。 调用`monkeypatch.setattr`、`pytest.raises`、`resources.for_run`、`(settings.data_dir / "native-services/missing-docker").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_managed_receipt_cannot_be_downgraded_for_missing_rule_coder`（L151–L172）：接收`settings`、`monkeypatch`。 控制顺序：L172断言`not product.exists()`。 调用`rule_plan`、`write_json`、`digest`、`plan.model_dump`、`monkeypatch.setattr`、`pytest.raises`、`native.managed_generate`、`product.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_aider_tool_environment_stays_source_only`（L175–L190）：接收`settings`、`monkeypatch`。 控制顺序：L189断言`"Aider" in result["reason"]`；L190断言`not (settings.data_dir / "native-services").exists()`。 调用`monkeypatch.setattr`、`native.managed_generate`、`rule_plan`、`(settings.data_dir / "native-services").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_aider_tool_environment_stays_source_only.missing`（L182–L183）：接收`settings`。 控制顺序：L183抛异常，停止当前正常路径。 调用`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_service_failures.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L190。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7338`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_service_failures.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1748f1dc81e2dae635b4d62d64363a29d1fa957b5be1ed693103590f707d0bad"} -->
````python
# tests/test_native_service_failures.py
"""Docker errors after successful process spawn must not bypass authorization."""

import sys
from types import SimpleNamespace

import pytest
from test_source_candidate_delivery import native_plan

from workbench.delivery import native
from workbench.infrastructure.native import resources
from workbench.infrastructure.processes import tools


@pytest.mark.parametrize(
    "diagnostic,expected",
    [
        ("permission denied while trying to connect to the Docker daemon socket", PermissionError),
        ("Cannot connect to the Docker daemon: access is denied", PermissionError),
        ("Cannot connect to the Docker daemon: operation not permitted", PermissionError),
        (
            "Cannot connect to the Docker daemon. Is the docker daemon running?",
            resources.NativeServiceUnavailable,
        ),
        ("unclassified server failure", tools.ToolFailure),
    ],
)
def test_service_exit_classification_uses_real_tool_failure(
    tmp_path, monkeypatch, diagnostic, expected
):
    def command(*args):
        return tools.run_command(
            [sys.executable, "-c", f"import sys; print({diagnostic!r}); sys.exit(1)"], tmp_path
        )

    monkeypatch.setattr(resources, "run_command", command)
    with pytest.raises(expected) as failure:
        resources.start_services(["docker", "compose"], tmp_path)
    assert type(failure.value) is expected


@pytest.mark.parametrize("known_unavailable", [False, True])
def test_managed_generation_only_downgrades_classified_service_unavailability(
    settings, monkeypatch, known_unavailable
):
    from workbench.delivery import source_candidate

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    error = (
        resources.NativeServiceUnavailable("daemon stopped")
        if known_unavailable
        else tools.ToolFailure("unknown failure")
    )

    def fail(*args):
        raise error

    monkeypatch.setattr(resources, "for_run", fail)
    calls = []
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *args: calls.append(args) or {"candidate": True},
    )
    product = settings.data_dir / "runs/service-error/product"
    if known_unavailable:
        assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == {
            "candidate": True
        }
        assert len(calls) == 1
    else:
        with pytest.raises(tools.ToolFailure):
            native.managed_generate(settings, "fastapiadmin", native_plan(), product)
        assert calls == []


def rule_plan():
    from workbench.core.contracts import CustomRule

    plan = native_plan()
    plan.custom_rules = [
        CustomRule(
            entity="task",
            description="Title must start with ok",
            accept_examples=[{"title": "ok task"}],
            reject_examples=[{"title": "bad task"}],
        )
    ]
    return plan


@pytest.mark.parametrize(
    "engine,enabled", [("bounded", True), ("bounded", False), ("aider", False)]
)
def test_unavailable_rule_coder_retains_source_before_any_runtime_effect(
    settings, monkeypatch, engine, enabled
):
    from workbench.delivery import source_candidate

    settings.coding_engine, settings.enable_coding = engine, enabled
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})

    def forbidden(*args):
        raise AssertionError("runtime services or coder must not execute")

    monkeypatch.setattr(resources, "for_run", forbidden)
    monkeypatch.setattr(native, "runtime_config", forbidden)
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    product = settings.data_dir / "runs/rule-capability/product"
    result = native.managed_generate(
        settings, "fastapiadmin", rule_plan(), product, customization=forbidden
    )
    assert result["execution"] == "source-candidate"
    assert result["generation_status"] == "partial"
    assert result["runtime_verified"] is False
    assert "CODING_ENGINE=aider" in result["runtime_unavailable_reason"]
    assert result["pending_steps"]


def test_available_rule_coder_reaches_strict_runtime_path(settings, monkeypatch):
    from workbench.coding import aider

    monkeypatch.setattr(aider, "executable", lambda settings: "configured-locked-interpreter")
    settings.coding_engine, settings.enable_coding = "aider", True
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )

    def reached(*args):
        raise PermissionError("runtime service authorization remains required")

    monkeypatch.setattr(resources, "for_run", reached)
    product = settings.data_dir / "runs/rule-runtime/product"
    with pytest.raises(PermissionError):
        native.managed_generate(settings, "fastapiadmin", rule_plan(), product)
    assert not product.exists()


def test_missing_docker_has_no_service_filesystem_side_effect(settings, monkeypatch):
    monkeypatch.setattr(resources.shutil, "which", lambda name: None)
    with pytest.raises(resources.NativeServiceUnavailable):
        resources.for_run(settings, "missing-docker")
    assert not (settings.data_dir / "native-services/missing-docker").exists()


def test_existing_managed_receipt_cannot_be_downgraded_for_missing_rule_coder(
    settings, monkeypatch
):
    from workbench.core.contracts import digest
    from workbench.filesystem import write_json
    from workbench.generation.python_basic import PrerequisiteError

    settings.coding_engine = "bounded"
    plan = rule_plan()
    product = settings.data_dir / "runs/existing-runtime/product"
    write_json(
        product.parent / "native-generation.json",
        {
            "execution": "managed-runtime",
            "template": "fastapiadmin",
            "spec_digest": digest(plan.model_dump()),
        },
    )
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    with pytest.raises(PrerequisiteError, match="不能自动降级"):
        native.managed_generate(settings, "fastapiadmin", plan, product)
    assert not product.exists()


def test_missing_aider_tool_environment_stays_source_only(settings, monkeypatch):
    from workbench.coding import aider
    from workbench.delivery import source_candidate

    settings.coding_engine, settings.enable_coding = "aider", True
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})

    def missing(settings):
        raise ValueError("missing interpreter")

    monkeypatch.setattr(aider, "executable", missing)
    monkeypatch.setattr(source_candidate, "generate_candidate", lambda *args: {"reason": args[-1]})
    product = settings.data_dir / "runs/missing-aider/product"
    result = native.managed_generate(settings, "fastapiadmin", rule_plan(), product)
    assert "Aider" in result["reason"]
    assert not (settings.data_dir / "native-services").exists()
````
