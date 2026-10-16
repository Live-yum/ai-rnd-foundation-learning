# tests/test_native_failure_classification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance`、`workbench.core.contracts`、`workbench.delivery.recovery`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_native_lab_does_not_downgrade_unknown_or_integrity_failures`（L13–L56）：接收`tmp_path`、`monkeypatch`、`kind`。 控制顺序：L56断言`not isinstance(error.value, NativeValidationFailure)`。 调用`source.mkdir`、`source_file.write_text`、`Plan`、`monkeypatch.setattr`、`pytest.raises`、`native_lab._run_acceptance`、`isinstance`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_lab_does_not_downgrade_unknown_or_integrity_failures.fail`（L28–L35）：接收`*args`。 控制顺序：L29按`kind == "source_changed"`分支；L31按`kind == "plan_changed"`分支；L33按`kind == "permission"`分支；L34抛异常，停止当前正常路径；L35抛异常，停止当前正常路径。 调用`source_file.write_text`、`PermissionError`、`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_runtime_check_marks_validation_failed`（L59–L64）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`native_lab._runtime_check`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_runtime_check_marks_validation_failed.failed_check`（L60–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L61抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_check_diagnostic_is_bounded_and_does_not_copy_assertion_secrets`（L67–L81）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76断言`"check_id=generated-permissions" in text`；L77断言`"reason=assertion_failed" in text`；L78断言`len(text) < 160`；L79断言`"private-token" not in text`；L80断言`"password" not in text`；L81断言`"sensitive" not in text`。 调用`pytest.raises`、`native_lab._runtime_check`、`str`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_check_diagnostic_is_bounded_and_does_not_copy_assertion_secrets.failed_check`（L70–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L71抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_lab_failure_log_keeps_safe_check_identifier`（L85–L137）：接收`tmp_path`、`monkeypatch`、`browser_failure`。 控制顺序：L129断言`( "check_id=customer-service-browser" if browser_failure else "check_id=generated-cru…`；L132断言`( "reason=browser_evidence_failed" if browser_failure else "reason=assertion_failed" …`；L135断言`"super-secret" not in log`；L136断言`"private-body" not in log`；L137断言`len(log) < 300`。 调用`source.mkdir`、`(source / "upstream.py").write_text`、`Plan`、`monkeypatch.setattr`、`pytest.raises`、`native_lab._run_acceptance`、`(reports / "failure.log").read_text`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_lab_failure_log_keeps_safe_check_identifier.failed_check`（L99–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L100抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_lab_failure_log_keeps_safe_check_identifier.fail`（L102–L113）：接收`*args`。 控制顺序：L103按`browser_failure`分支。 调用`native_lab._runtime_check`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_failure_identifies_trusted_assertion_frame_without_payload`（L140–L149）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L146断言`"source=workbench/acceptance/native_acceptance.py:" in text`；L147断言`":list_rows" in text`；L148断言`"private response body" not in text`；L149断言`len(text) < 300`。 调用`pytest.raises`、`native_lab._runtime_check`、`str`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_trusted_business_browser_failures_are_runtime_validation`（L153–L173）：接收`kind`。 控制顺序：L157按`kind == "failed_report"`分支；L160按`kind == "missing_journey"`分支；L172断言`"reason=browser_evidence_failed" in str(failure.value)`；L173断言`"secret-response" not in str(failure.value)`。 调用`pytest.raises`、`native_lab._runtime_check`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_boundary_preserves_unknown_and_security_failures`（L177–L189）：接收`kind`。 控制顺序：L189断言`not isinstance(failure.value, NativeValidationFailure)`。 调用`pytest.raises`、`native_lab._runtime_check`、`isinstance`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_boundary_preserves_unknown_and_security_failures.check`（L180–L185）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L181按`kind == "identity"`分支；L183按`kind == "permission"`分支；L184抛异常，停止当前正常路径；L185抛异常，停止当前正常路径。 调用`require_business_browser`、`PermissionError`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_failure_type_is_not_converted_at_other_boundaries`（L192–L199）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`native_lab._runtime_check`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_failure_type_is_not_converted_at_other_boundaries.check`（L195–L196）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L196抛异常，停止当前正常路径。 调用`BusinessBrowserValidationFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_failure_classification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L199。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7544`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_failure_classification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c161627df57ad45bc334ef36873c7634023f9aba326cd841a9628d6ad5134999"} -->
````python
# tests/test_native_failure_classification.py
"""Exercise the real native lab wrapper, not a mocked delivery entry point."""

import pytest

pytest.importorskip("psycopg")

from workbench.acceptance import native_lab
from workbench.core.contracts import Plan
from workbench.delivery.recovery import NativeIntegrityError, NativeValidationFailure


@pytest.mark.parametrize("kind", ["unknown_assert", "permission", "source_changed", "plan_changed"])
def test_native_lab_does_not_downgrade_unknown_or_integrity_failures(tmp_path, monkeypatch, kind):
    source = tmp_path / "source"
    source.mkdir()
    source_file = source / "upstream.py"
    source_file.write_text("value = 1\n", encoding="utf-8")
    plan = Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )
    monkeypatch.setattr(native_lab, "prepare_fastapi_transactions", lambda *args: {})

    def fail(*args):
        if kind == "source_changed":
            source_file.write_text("corrupted\n", encoding="utf-8")
        if kind == "plan_changed":
            plan.title = "changed approval"
        if kind == "permission":
            raise PermissionError("denied")
        raise AssertionError("unclassified assertion before executable validation")

    monkeypatch.setattr(native_lab, "bootstrap_database", fail)
    expected = (
        NativeIntegrityError
        if kind in {"source_changed", "plan_changed"}
        else PermissionError
        if kind == "permission"
        else AssertionError
    )
    with pytest.raises(expected) as error:
        native_lab._run_acceptance(
            "fastapiadmin",
            source,
            tmp_path / "product",
            None,
            "postgresql://localhost/test_codegen",
            tmp_path / "reports",
            plan,
            backend_port=18001,
        )
    assert not isinstance(error.value, NativeValidationFailure)


def test_only_explicit_runtime_check_marks_validation_failed():
    def failed_check():
        raise AssertionError("HTTP acceptance mismatch")

    with pytest.raises(NativeValidationFailure):
        native_lab._runtime_check(failed_check, check_id="generated-crud")


def test_runtime_check_diagnostic_is_bounded_and_does_not_copy_assertion_secrets():
    secret = "Bearer private-token https://user:password@host/" + "sensitive body" * 1000

    def failed_check():
        raise AssertionError(secret)

    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(failed_check, check_id="generated-permissions")
    text = str(failure.value)
    assert "check_id=generated-permissions" in text
    assert "reason=assertion_failed" in text
    assert len(text) < 160
    assert "private-token" not in text
    assert "password" not in text
    assert "sensitive" not in text


@pytest.mark.parametrize("browser_failure", [False, True])
def test_real_lab_failure_log_keeps_safe_check_identifier(tmp_path, monkeypatch, browser_failure):
    source = tmp_path / "source"
    source.mkdir()
    (source / "upstream.py").write_text("value = 1\n", encoding="utf-8")
    plan = Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )
    monkeypatch.setattr(native_lab, "prepare_fastapi_transactions", lambda *args: {})

    def failed_check():
        raise AssertionError("Bearer super-secret HTTP response private-body")

    def fail(*args):
        if browser_failure:
            from workbench.business.browser import require_business_browser

            native_lab._runtime_check(
                require_business_browser,
                {"template": "fastapiadmin", "passed": False, "errors": ["super-secret"]},
                plan,
                "fastapiadmin",
                check_id="customer-service-browser",
            )
        native_lab._runtime_check(failed_check, check_id="generated-crud")

    monkeypatch.setattr(native_lab, "bootstrap_database", fail)
    reports = tmp_path / "reports"
    with pytest.raises(NativeValidationFailure):
        native_lab._run_acceptance(
            "fastapiadmin",
            source,
            tmp_path / "product",
            None,
            "postgresql://localhost/test_codegen",
            reports,
            plan,
            backend_port=18001,
        )
    log = (reports / "failure.log").read_text(encoding="utf-8")
    assert (
        "check_id=customer-service-browser" if browser_failure else "check_id=generated-crud"
    ) in log
    assert (
        "reason=browser_evidence_failed" if browser_failure else "reason=assertion_failed"
    ) in log
    assert "super-secret" not in log
    assert "private-body" not in log
    assert len(log) < 300


def test_runtime_failure_identifies_trusted_assertion_frame_without_payload():
    from workbench.acceptance.native_acceptance import list_rows

    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(list_rows, "private response body", check_id="generated-crud")
    text = str(failure.value)
    assert "source=workbench/acceptance/native_acceptance.py:" in text
    assert ":list_rows" in text
    assert "private response body" not in text
    assert len(text) < 300


@pytest.mark.parametrize("kind", ["failed_report", "missing_role", "missing_journey"])
def test_trusted_business_browser_failures_are_runtime_validation(kind):
    from workbench.business.browser import require_business_browser

    report = {"template": "fastapiadmin", "passed": True, "errors": [], "checks": []}
    if kind == "failed_report":
        report["passed"] = False
        report["errors"] = ["Bearer secret-response"]
    if kind == "missing_journey":
        report["checks"] = [
            role + ":real_native_login_menu_shell" for role in ("manager", "service", "employee")
        ]
    with pytest.raises(NativeValidationFailure) as failure:
        native_lab._runtime_check(
            require_business_browser,
            report,
            None,
            "fastapiadmin",
            check_id="customer-service-browser",
        )
    assert "reason=browser_evidence_failed" in str(failure.value)
    assert "secret-response" not in str(failure.value)


@pytest.mark.parametrize("kind", ["unknown_value", "permission", "identity"])
def test_browser_boundary_preserves_unknown_and_security_failures(kind):
    from workbench.business.browser import require_business_browser

    def check():
        if kind == "identity":
            require_business_browser({"template": "yudao-vben"}, None, "fastapiadmin")
        if kind == "permission":
            raise PermissionError("denied")
        raise ValueError("unknown security or malformed data error")

    with pytest.raises(PermissionError if kind == "permission" else ValueError) as failure:
        native_lab._runtime_check(check, check_id="customer-service-browser")
    assert not isinstance(failure.value, NativeValidationFailure)


def test_browser_failure_type_is_not_converted_at_other_boundaries():
    from workbench.business.browser import BusinessBrowserValidationFailure

    def check():
        raise BusinessBrowserValidationFailure("not the selected browser boundary")

    with pytest.raises(BusinessBrowserValidationFailure):
        native_lab._runtime_check(check, check_id="generated-crud")
````
