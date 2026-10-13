# tests/test_capability_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_live_modules`、`workbench.capability_diagnostics`、`workbench.generator`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_real_child_failure_survives_parent_raise_and_temporary_workspace`（L15–L62）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L54断言`receipt["exception_type"] == "ValueError"`；L55断言`receipt["stage"] == "verifier_controller"`；L56断言`receipt["passed"] is False`；L57断言`receipt["cleanup"] == "not-started"`；L58断言`type(receipt["trusted_source_line"]) is int`；L59遍历`tmp_path.glob("*verification.json*")`；L61断言`"private" not in json.dumps(progress)`；L62断言`progress["verification_receipts"][0] == receipt`。 调用`fixed_application`、`monkeypatch.setattr`、`Path`、`str`、`stale.write_text`、`json.dumps`、`pytest.raises`、`verify_with_diagnostics`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_child_failure_survives_parent_raise_and_temporary_workspace.launch`（L35–L36）：接收`command`、`**kwargs`。 调用`original`。 返回路径：L36的`original([sys.executable, "-c", child], **kwargs)`。
- `test_node_artifact_whitelist_rejects_content_and_bounds_reads`（L66–L103）：接收`tmp_path`、`corruption`。 控制顺序：L80按`corruption != "missing"`分支；L99断言`"private" not in json.dumps(result)`；L100断言`"trusted_source_line" not in result`；L101断言`result["restarted"] is None`；L102断言`result["cleanup"] == "other"`；L103断言`result["checks_count"] == (2 if corruption == "poisoned" else None)`。 调用`Path`、`str`、`path.write_text`、`json.dumps`、`sidecar.write_text`、`node_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_record_failure_io_error_preserves_original_exception`（L106–L120）：接收`tmp_path`、`monkeypatch`。 控制顺序：L116抛异常，停止当前正常路径；L119抛异常，停止当前正常路径；L120断言`found.value is error`。 调用`monkeypatch.setattr`、`ValueError`、`pytest.raises`、`record_failure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_record_failure_io_error_preserves_original_exception.fail`（L109–L110）：接收`*args`。 控制顺序：L110抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_verifier_child_retains_exact_policy_and_receipt`（L123–L205）：接收`monkeypatch`、`tmp_path`、`settings`。 控制顺序：L205断言`proof == {"passed": True, "cleanup": "deleted"}`。 调用`approved_manual`、`monkeypatch.setenv`、`fixed_application`、`isolation.browser_source_identity`、`isolation.image_source_identity`、`(tmp_path / "browser.json").write_text`、`json.dumps`、`monkeypatch.setattr`、`verifier.verify_capabilities`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_verifier_child_retains_exact_policy_and_receipt.launch`（L193–L194）：接收`command`、`**kwargs`。 调用`original`。 返回路径：L194的`original([sys.executable, "-c", child], **kwargs)`。
- `test_verifier_policy_forwarding_rejects_changed_scope`（L221–L229）：接收`monkeypatch`、`field`、`value`。 调用`approved_manual`、`monkeypatch.setenv`、`pytest.raises`、`verifier_policy_environment`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_verifier_policy_forwarding_is_off_by_default_and_does_not_change_clean_env`（L232–L243）：接收`monkeypatch`。 控制顺序：L239断言`verifier_policy_environment()["GITHUB_JOB"] == "mini-swe-sla"`；L240断言`"GITHUB_JOB" not in clean_env()`；L241断言`"CAPABILITY_BROWSER_APPROVED_POLICY" not in clean_env()`；L243断言`verifier_policy_environment() == {}`。 调用`approved_manual`、`verifier_policy_environment`、`clean_env`、`monkeypatch.delenv`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_diagnostic_cannot_explain_a_new_receipt`（L246–L255）：接收`tmp_path`。 控制顺序：L255断言`node_diagnostic(product, aggregate=False)["exception_type"] == "other"`。 调用`Path`、`str`、`sidecar.write_text`、`json.dumps`、`os.utime`、`path.write_text`、`node_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_startup_classifier_survives_node_export_without_raw_content`（L267–L284）：接收`tmp_path`、`output`、`status`、`http_error`、`exit_code`、`hint`。 控制顺序：L279断言`startup["http_status"] == status`；L280断言`startup["http_error"] == http_error`；L281断言`startup["command_exit_code"] == exit_code`；L282断言`startup["output_hints"] == ([hint] if hint else [])`；L283断言`result["passed"] is False`；L284断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`path.write_text`、`json.dumps`、`node_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_filter_drops_unknown_fields_labels_and_invalid_numeric_types`（L287–L306）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L303断言`result["http_status"] is result["command_exit_code"] is None`；L304断言`result["application_startup_reported"] is None`；L305断言`result["output_hints"] == ["missing-module"]`；L306断言`"private" not in json.dumps(result)`。 调用`startup_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_syntax_gate_does_not_claim_import_or_health_success`（L309–L322）：接收`tmp_path`。 调用`fixed_application`、`app.read_text`、`app.write_text`、`inspect_stack`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L322。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12458`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "67ca037e62235e2a072bda6b7643a8750785b4afa4bc28fb48fc8659101ed7dc"} -->
````python
# tests/test_capability_diagnostics.py
"""Exercise verifier child failure through the live artifact filter, offline."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ci_live_modules import verify_with_diagnostics
from workbench.capability_diagnostics import node_diagnostic, record_failure
from workbench.generator import PrerequisiteError


def test_real_child_failure_survives_parent_raise_and_temporary_workspace(
    settings, tmp_path, monkeypatch
):
    import workbench.capability_dependencies as dependencies
    import workbench.capability_execution as execution
    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier

    product = tmp_path / "product"
    plan = fixed_application(product)
    monkeypatch.setattr(execution, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(dependencies, "require_dependency_descriptors", lambda *a: None)
    original = subprocess.Popen
    child = """from workbench import capability_sandbox as v
def fail(payload):
    raise ValueError('private-url key headers prompt candidate-source')
v._execute_payload=fail
v.main()
"""

    def launch(command, **kwargs):
        return original([sys.executable, "-c", child], **kwargs)

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    stale = Path(str(product.parent / "product-node-verification.json") + ".diagnostic.json")
    stale.write_text(json.dumps({"exception_type": "TypeError", "stage": "sandbox_transport"}))
    progress = {}
    with pytest.raises(PrerequisiteError, match="验证进程失败"):
        verify_with_diagnostics(
            verifier.verify_capabilities,
            product,
            plan,
            plan.scenarios,
            settings,
            aggregate=False,
            selection=plan.selection.model_dump(),
            progress=progress,
        )
    receipt = progress["verification_receipts"][0]
    assert receipt["exception_type"] == "ValueError"
    assert receipt["stage"] == "verifier_controller"
    assert receipt["passed"] is False
    assert receipt["cleanup"] == "not-started"
    assert type(receipt["trusted_source_line"]) is int
    for path in tmp_path.glob("*verification.json*"):
        path.unlink()
    assert "private" not in json.dumps(progress)
    assert progress["verification_receipts"][0] == receipt


@pytest.mark.parametrize("corruption", ["missing", "invalid", "oversized", "poisoned"])
def test_node_artifact_whitelist_rejects_content_and_bounds_reads(tmp_path, corruption):
    product = tmp_path / "product"
    path = tmp_path / "product-node-verification.json"
    sidecar = Path(str(path) + ".diagnostic.json")
    raw = {
        "passed": True,
        "cleanup": "private",
        "checks": ["private"] * 2,
        "error": "private-key",
        "build_diagnostic": "private-source",
        "sandbox_name": "private-name",
        "startup_diagnostic": {"headers": "private"},
        "restarted": 1,
    }
    if corruption != "missing":
        path.write_text(
            "!invalid"
            if corruption == "invalid"
            else "x" * 1_000_001
            if corruption == "oversized"
            else json.dumps(raw)
        )
    sidecar.write_text(
        json.dumps(
            {
                "exception_type": "private",
                "stage": "private",
                "trusted_source_line": True,
                "error": "private",
            }
        )
    )
    result = node_diagnostic(product, aggregate=False)
    assert "private" not in json.dumps(result)
    assert "trusted_source_line" not in result
    assert result["restarted"] is None
    assert result["cleanup"] == "other"
    assert result["checks_count"] == (2 if corruption == "poisoned" else None)


def test_record_failure_io_error_preserves_original_exception(tmp_path, monkeypatch):
    import workbench.filesystem as filesystem

    def fail(*args):
        raise PermissionError("private")

    monkeypatch.setattr(filesystem, "write_json", fail)
    error = ValueError("private-original")
    with pytest.raises(ValueError) as found:
        try:
            raise error
        except ValueError as exc:
            record_failure(tmp_path / "receipt.json", exc)
            raise
    assert found.value is error


def test_actual_verifier_child_retains_exact_policy_and_receipt(monkeypatch, tmp_path, settings):
    from test_capability_browser_policy import IMAGE, approved_manual

    import workbench.capability_dependencies as dependencies
    import workbench.capability_execution as execution
    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_browser_isolation as isolation
    from workbench import capability_sandbox as verifier

    approved_manual(monkeypatch)
    monkeypatch.setenv("API_KEY", "private-model-key")
    monkeypatch.setenv("GITHUB_TOKEN", "private-github-token")
    monkeypatch.setenv("HTTP_PROXY", "private-proxy")
    product = tmp_path / "product"
    plan = fixed_application(product)
    browser_receipt = {
        "protocol": "offline-browser-isolation-v3",
        "passed": True,
        "mocked": False,
        "image": IMAGE,
        "runtime": {"fixture_approved_runtime": True},
        "sources": isolation.browser_source_identity(),
        "image_sources": isolation.image_source_identity(),
        "checks": {
            "kernel_and_network": {
                key: True
                for key in (
                    "passed",
                    "kernel_resource_limits",
                    "network_none",
                    "tmpfs_exhaustion",
                    "pid_exhaustion",
                    "readonly_root",
                    "browser_build",
                    "apparmor_enforced",
                )
            },
            **{
                key: True
                for key in (
                    "positive",
                    "error",
                    "abuse",
                    "failure_cleanup",
                    "memory_exhaustion",
                    "raw_syscalls",
                )
            },
        },
    }
    (tmp_path / "browser.json").write_text(json.dumps(browser_receipt))
    monkeypatch.setattr(execution, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(dependencies, "require_dependency_descriptors", lambda *a: None)
    original = subprocess.Popen
    child = """import json, os
from pathlib import Path
from workbench import capability_sandbox as v
from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy
def inspect(payload):
    assert not any(k in os.environ for k in ('API_KEY', 'GITHUB_TOKEN', 'HTTP_PROXY'))
    path=Path(payload['receipt'])
    isolation.BROWSER_ACCEPTANCE=path.parent/'browser.json'
    isolation.runtime_identity=lambda image: ({'fixture_approved_runtime':True} if policy.selected_policy() else {'policy_sha256':None,'mode':'docker-default'})
    assert isolation.require_browser_acceptance('sha256:'+'a'*64)
    path.write_text(json.dumps({'passed':True,'cleanup':'deleted'}))
v._execute_payload=inspect
v.main()
"""

    def launch(command, **kwargs):
        return original([sys.executable, "-c", child], **kwargs)

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    proof = verifier.verify_capabilities(
        product,
        plan,
        plan.scenarios,
        settings,
        aggregate=False,
        selection=plan.selection.model_dump(),
    )
    assert proof == {"passed": True, "cleanup": "deleted"}  # Mock proof, not product acceptance.


@pytest.mark.parametrize(
    "field,value",
    [
        ("GITHUB_JOB", "other"),
        ("LIVE_SCENARIO", "other"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("REVIEWED_SHA", "b" * 40),
        ("GITHUB_WORKFLOW_SHA", "b" * 40),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_WORKFLOW_REF", "other.yml@refs/heads/main"),
    ],
)
def test_verifier_policy_forwarding_rejects_changed_scope(monkeypatch, field, value):
    from test_capability_browser_policy import approved_manual

    from workbench.capability_sandbox import verifier_policy_environment

    approved_manual(monkeypatch)
    monkeypatch.setenv(field, value)
    with pytest.raises(ValueError, match="approved Actions scope"):
        verifier_policy_environment()


def test_verifier_policy_forwarding_is_off_by_default_and_does_not_change_clean_env(monkeypatch):
    from test_capability_browser_policy import approved_manual

    from workbench.capability_sandbox import verifier_policy_environment
    from workbench.tools import clean_env

    approved_manual(monkeypatch)
    assert verifier_policy_environment()["GITHUB_JOB"] == "mini-swe-sla"
    assert "GITHUB_JOB" not in clean_env()
    assert "CAPABILITY_BROWSER_APPROVED_POLICY" not in clean_env()
    monkeypatch.delenv("CAPABILITY_BROWSER_APPROVED_POLICY")
    assert verifier_policy_environment() == {}


def test_stale_diagnostic_cannot_explain_a_new_receipt(tmp_path):
    import os

    product = tmp_path / "product"
    path = tmp_path / "product-node-verification.json"
    sidecar = Path(str(path) + ".diagnostic.json")
    sidecar.write_text(json.dumps({"exception_type": "ValueError", "stage": "verifier_controller"}))
    os.utime(sidecar, ns=(1_000_000_000, 1_000_000_000))
    path.write_text(json.dumps({"passed": False, "cleanup": "not-started"}))
    assert node_diagnostic(product, aggregate=False)["exception_type"] == "other"


@pytest.mark.parametrize(
    "output,status,http_error,exit_code,hint",
    [
        ("ModuleNotFoundError: No module named 'private_module'", 502, "none", 1, "missing-module"),
        ("NameError: name 'private_symbol' is not defined", 502, "none", 1, None),
        ("Application startup complete", 404, "none", None, None),
        ("", None, "connect", None, None),
    ],
)
def test_actual_startup_classifier_survives_node_export_without_raw_content(
    tmp_path, output, status, http_error, exit_code, hint
):
    from workbench.capability_sandbox import startup_failure_diagnostic

    path = tmp_path / "product-node-verification.json"
    original = startup_failure_diagnostic(output, status, http_error, command_exit_code=exit_code)
    path.write_text(
        json.dumps({"passed": False, "cleanup": "deleted", "startup_diagnostic": original})
    )
    result = node_diagnostic(tmp_path / "product", aggregate=False)
    startup = result["startup"]
    assert startup["http_status"] == status
    assert startup["http_error"] == http_error
    assert startup["command_exit_code"] == exit_code
    assert startup["output_hints"] == ([hint] if hint else [])
    assert result["passed"] is False
    assert "private" not in json.dumps(result)


def test_startup_filter_drops_unknown_fields_labels_and_invalid_numeric_types():
    from workbench.capability_diagnostics import startup_diagnostic

    value = {
        "phase": "private",
        "http_status": True,
        "command_exit_code": 256,
        "http_error": "private",
        "output_hints": ["private", "missing-module"] * 100,
        "application_startup_reported": 1,
        "target": {"role": "private", "url": "private"},
        "exception_type": "private",
        "raw_output": "private-code-key-prompt",
        "headers": "private",
    }
    result = startup_diagnostic(value)
    assert result["http_status"] is result["command_exit_code"] is None
    assert result["application_startup_reported"] is None
    assert result["output_hints"] == ["missing-module"]
    assert "private" not in json.dumps(result)


def test_syntax_gate_does_not_claim_import_or_health_success(tmp_path):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_stack import inspect_stack
    from workbench.capability_verification import CheckFailure

    product = tmp_path / "product"
    plan = fixed_application(product)
    app = product / "app.py"
    original = app.read_text()
    app.write_text("from deliberately_absent_fixture_module import absent\n" + original)
    inspect_stack(product, plan)  # Parse only: never import the candidate on this host.
    app.write_text(original + "\ndef broken(:\n")
    with pytest.raises(CheckFailure, match="语法"):
        inspect_stack(product, plan)
````
