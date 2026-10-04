# tests/test_real_model_ci.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_real_model_ci_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_real_model`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_runtime_diagnostics_keep_exact_failure_stage_and_safe_headline`（L871–L907）：接收`tmp_path`。 控制顺序：L895断言`"business_probe.py:271" in result["error_excerpt"]`；L896断言`result["native_stage"] == "customer-service-http"`；L897断言`result["native_template"] == "fastapiadmin"`；L898断言`result["native_exception"] == { "exception_type": "AssertionError", "file": "business…`；L906遍历`("exact-key-canary", "second-secret", "unselected", "private envi…`；L907断言`value not in encoded`。 调用`(tmp_path / "progress.json").write_text`、`json.dumps`、`(tmp_path / "failure.log").write_text`、`safe_runtime_details`、`DiagnosticTextBudget`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_diagnostics_reject_unrecognized_report_values`（L922–L931）：接收`tmp_path`、`stage`、`headline`。 控制顺序：L928断言`"native_exception" not in result`；L929断言`result.get("native_stage") == ( "customer-service-http" if stage == "customer-service…`。 调用`(tmp_path / "progress.json").write_text`、`json.dumps`、`(tmp_path / "failure.log").write_text`、`safe_runtime_details`、`DiagnosticTextBudget`、`result.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_diagnostics_reject_symlinked_files_and_report_directory`（L934–L959）：接收`tmp_path`、`monkeypatch`。 控制顺序：L948遍历`("progress.json", "failure.log")`；L958遍历`(reports, linked_directory, linked_directory / "nested")`；L959断言`safe_runtime_details("", path, DiagnosticTextBudget()) == {}`。 调用`outside.mkdir`、`(outside / "progress.json").write_text`、`(outside / "failure.log").write_text`、`reports.mkdir`、`(reports / name).symlink_to`、`linked_directory.symlink_to`、`type`、`monkeypatch.setattr`、`original`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget`（L962–L983）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L978断言`result["terminal_state"] == "FAILED"`；L979断言`result["runtime_diagnostics"]["error_excerpt"].startswith( "RuntimeError：native_modul…`；L982断言`len(result["runtime_diagnostics"]["error_excerpt"]) == 40`；L983断言`budget.remaining == 0`。 调用`DiagnosticTextBudget`、`safe_workflow_details`、`Store`、`result["runtime_diagnostics"]["error_excerpt"].startswith`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget.Store`（L965–L974）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget.Store.get_run`（L966–L971）：接收`run_id`。 返回路径：L967的`{ "status": "FAILED", "template": "fastapiadmin", "error": "RuntimeError：native_modules.py…`。
- `test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget.Store.latest_revision`（L973–L974）：接收`run_id`、`stage`。 返回路径：L974的`{}`。
- `test_native_progress_allowlist_covers_real_literal_stages`（L986–L1003）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1003断言`stages == NATIVE_PROGRESS_STAGES`。 调用`ast.parse`、`inspect.getsource`、`ast.walk`、`isinstance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_exception_headline_redaction_precedes_truncation_and_ignores_log`（L1006–L1022）：接收`tmp_path`。 控制顺序：L1020断言`len(message) == 600`；L1021断言`"private" not in json.dumps(result)`；L1022断言`message.endswith("[REDA")`。 调用`(tmp_path / "failure.log").write_text`、`DiagnosticTextBudget`、`safe_runtime_details`、`len`、`json.dumps`、`message.endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_plan_replay_preserves_exact_normalized_customer_contract`（L1025–L1045）：接收`tmp_path`。 控制顺序：L1037断言`result["status"] == "saved" and result["exact_normalized_plan"] is True`；L1038断言`result["file"] == destination.name`；L1039断言`result["bytes"] == len(destination.read_bytes())`；L1040断言`json.loads(destination.read_text(encoding="utf-8")) == Plan.model_validate(plan).mode…`；L1044断言`list(destination.parent.iterdir()) == [destination]`；L1045断言`"unselected secret" not in destination.read_text(encoding="utf-8")`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`reports.mkdir`、`(reports / "approved-spec.json").write_text`、`json.dumps`、`(reports / "raw-provider-response.json").write_text`、`DiagnosticTextBudget`、`preserve_approved_customer_plan`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_plan_replay_rejects_credentials_before_persistence`（L1060–L1072）：接收`tmp_path`、`secret_text`。 控制顺序：L1070断言`result == {"status": "secret_scan_rejected"}`；L1071断言`not destination.exists()`；L1072断言`secret_text not in json.dumps(result)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`plan["acceptance"].append`、`(tmp_path / "approved-spec.json").write_text`、`json.dumps`、`preserve_approved_customer_plan`、`DiagnosticTextBudget`、`destination.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_plan_replay_rejects_unknown_schema_and_does_not_read_other_files`（L1075–L1090）：接收`tmp_path`。 控制顺序：L1081断言`preserve_approved_customer_plan(tmp_path, destination, budget) == { "status": "unavai…`；L1087断言`preserve_approved_customer_plan(tmp_path, destination, budget) == { "status": "invali…`；L1090断言`not destination.exists()`。 调用`DiagnosticTextBudget`、`(tmp_path / "design.json").write_text`、`preserve_approved_customer_plan`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`(tmp_path / "approved-spec.json").write_text`、`json.dumps`、`destination.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_plan_replay_size_is_bounded_on_read_and_normalized_write`（L1093–L1114）：接收`tmp_path`。 控制顺序：L1103断言`preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == { "…`；L1109断言`len(compact.encode("utf-8")) > MAX_REPLAY_PLAN_BYTES`；L1111断言`preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == { "…`；L1114断言`not destination.exists()`。 调用`source.write_bytes`、`preserve_approved_customer_plan`、`DiagnosticTextBudget`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.dumps`、`len`、`compact.encode`、`source.write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_plan_replay_rejects_linked_input`（L1117–L1137）：接收`tmp_path`、`monkeypatch`。 控制顺序：L1134断言`preserve_approved_customer_plan(reports, destination, DiagnosticTextBudget()) == { "s…`；L1137断言`not destination.exists()`。 调用`real.write_bytes`、`(ROOT / "examples/plans/customer-service.json").read_bytes`、`reports.mkdir`、`(reports / "approved-spec.json").symlink_to`、`type`、`monkeypatch.setattr`、`original`、`preserve_approved_customer_plan`、`DiagnosticTextBudget`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_native_harness_preserves_replay_before_private_cleanup`（L1140–L1207）：接收`tmp_path`、`monkeypatch`。 控制顺序：L1198断言`details["terminal_state"] == "FAILED"`；L1199断言`details["runtime_diagnostics"]["native_stage"] == "customer-service-http"`；L1200断言`"HTTP 422" in details["runtime_diagnostics"]["native_exception"]["message_excerpt"]`；L1201断言`details["approved_plan_replay"]["status"] == "saved"`；L1202断言`"test-only-secret" not in json.dumps(details)`；L1203断言`"raw log" not in json.dumps(details)`；L1204断言`not directory.exists()`；L1206断言`json.loads(replay.read_text(encoding="utf-8"))["business"] == plan["business"]`。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`public_root.mkdir`、`monkeypatch.setattr`、`SimpleNamespace`、`Store`、`tempfile.TemporaryDirectory`、`Path`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_native_harness_preserves_replay_before_private_cleanup.Store`（L1158–L1168）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_failed_native_harness_preserves_replay_before_private_cleanup.Store.get_run`（L1159–L1165）：接收`run_id`。 控制顺序：L1160断言`run_id == "test-run"`。 返回路径：L1161的`{ "status": "FAILED", "template": "fastapiadmin", "error": "AssertionError：business_probe.…`。
- `test_failed_native_harness_preserves_replay_before_private_cleanup.Store.latest_revision`（L1167–L1168）：接收`run_id`、`stage`。 返回路径：L1168的`{"plan": plan} if stage == "design" else {}`。
- `test_failed_native_harness_preserves_replay_before_private_cleanup.failed_browser`（L1179–L1190）：接收`command`、`**kwargs`。 调用`write_json`、`(reports / "failure.log").write_text`、`SimpleNamespace`。 返回路径：L1190的`SimpleNamespace(returncode=1)`。
- `test_schema_root_validation_reason_is_bounded_redacted_without_input`（L1210–L1249）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1238断言`first["schema_errors"][0]["field_path"] == []`；L1239断言`first["schema_errors"][0]["message"].startswith("Value error, Known transition requir…`；L1240断言`len(first["schema_errors"][0]["message"]) == 600`；L1241断言`len(second["schema_errors"][0]["message"]) == 200`；L1243遍历`( "exact-private-canary", "provider-input-never-exported", "reaso…`；L1248断言`forbidden not in encoded`；L1249断言`"[REDACTED]" in encoded`。 调用`json.dumps( { "choices": [ { "finish_reason": "stop", "message": …`、`json.dumps`、`DiagnosticTextBudget`、`response_receipt`、`first["schema_errors"][0]["message"].startswith`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_root_validation_reason_is_bounded_redacted_without_input.Contract`（L1215–L1220）：继承`BaseModel`。声明的数据项为`value`；类型约束/数据库列参数以完整定义为准。
- `test_schema_root_validation_reason_is_bounded_redacted_without_input.Contract.validate_contract`（L1219–L1220）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1220抛异常，停止当前正常路径。 调用`ValueError`、`model_validator`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_employee_task_scope_binds_approved_requirement`（L1253–L1276）：接收`scope`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`permissions.append`、`Requirement`、`deepcopy`、`require_customer_spec`、`approved.model_dump`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_employee_tasks_remain_read_only_under_each_allowed_scope`（L1283–L1291）：接收`scope`、`action`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`permissions.append`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_replay_uses_only_registered_generated_artifact`（L1302–L1324）：接收`tmp_path`、`template`、`leaf`。 控制顺序：L1310断言`source == tmp_path / "runs/synthetic-run" / leaf`；L1315断言`preserve_approved_customer_plan(source, destination, DiagnosticTextBudget())["status"…`；L1320断言`preserve_approved_customer_plan(source, destination, DiagnosticTextBudget())["status"…`；L1324断言`json.loads(destination.read_text(encoding="utf-8"))["business"] == plan["business"]`。 调用`approved_plan_artifact_directory`、`source.mkdir`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`(source / "candidate-plan.json").write_text`、`json.dumps`、`preserve_approved_customer_plan`、`DiagnosticTextBudget`、`(source / "approved-spec.json").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_replay_rejects_invalid_run_artifact_identity`（L1328–L1331）：接收`tmp_path`、`run_id`。 控制顺序：L1331断言`approved_plan_artifact_directory(tmp_path, run_id, "python-basic") is None`。 调用`approved_plan_artifact_directory`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_notification_schema_exposes_existing_cross_field_invariants`（L1334–L1340）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1338断言`"never null or a wildcard" in fields["transition"]["description"]`；L1339断言`"per named transition and recipient" in fields["transition"]["description"]`；L1340断言`"other events require null" in fields["due_field"]["description"]`。 调用`NotificationSpec.model_json_schema`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_real_model_ci.py`；**本文件共有 2 段**。本段覆盖源文件 L871–L1340。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20686`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_real_model_ci.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "22677c914a976c3f82a664c3952a4493671eee10e34c6e85e677ee8eb51332b1"} -->
````python
# tests/test_real_model_ci.py
def test_runtime_diagnostics_keep_exact_failure_stage_and_safe_headline(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    (tmp_path / "progress.json").write_text(
        json.dumps(
            {
                "template": "fastapiadmin",
                "stage": "customer-service-http",
                "environment": "private environment not selected",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "failure.log").write_text(
        "AssertionError at business_probe.py:271 (customer_service_acceptance): "
        "Native API failed: POST /business/requests/create HTTP 422 exact-key-canary\n"
        "unselected subprocess log and provider response\nAuthorization: Bearer second-secret\n",
        encoding="utf-8",
    )
    result = safe_runtime_details(
        "AssertionError：business_probe.py:271（customer_service_acceptance），请检查本次运行报告",
        tmp_path,
        DiagnosticTextBudget(secrets=("exact-key-canary",)),
    )
    assert "business_probe.py:271" in result["error_excerpt"]
    assert result["native_stage"] == "customer-service-http"
    assert result["native_template"] == "fastapiadmin"
    assert result["native_exception"] == {
        "exception_type": "AssertionError",
        "file": "business_probe.py",
        "function": "customer_service_acceptance",
        "line": 271,
        "message_excerpt": "Native API failed: POST /business/requests/create HTTP 422 [REDACTED]",
    }
    encoded = json.dumps(result)
    for value in ("exact-key-canary", "second-secret", "unselected", "private environment"):
        assert value not in encoded


@pytest.mark.parametrize(
    "stage,headline",
    [
        ("arbitrary model text", "raw provider response\n"),
        (["customer-service-http"], "Authorization: Bearer secret\n"),
        ("customer-service-http", "A" * 65537 + "\n"),
        ("customer-service-http", "AssertionError at /private/path.py:2 (f): secret\n"),
    ],
    # Pytest exports the node ID as PYTEST_CURRENT_TEST; never put the 64-KiB
    # hostile payload there (Windows environment values are limited to 32767).
    ids=["unknown-stage", "non-string-stage", "oversized-headline", "private-path"],
)
def test_runtime_diagnostics_reject_unrecognized_report_values(tmp_path, stage, headline):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    (tmp_path / "progress.json").write_text(json.dumps({"stage": stage}), encoding="utf-8")
    (tmp_path / "failure.log").write_text(headline, encoding="utf-8")
    result = safe_runtime_details("", tmp_path, DiagnosticTextBudget())
    assert "native_exception" not in result
    assert result.get("native_stage") == (
        "customer-service-http" if stage == "customer-service-http" else None
    )


def test_runtime_diagnostics_reject_symlinked_files_and_report_directory(tmp_path, monkeypatch):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "progress.json").write_text('{"stage":"customer-service-http"}', encoding="utf-8")
    (outside / "failure.log").write_text(
        "AssertionError at hidden.py:1 (hidden): private canary\n", encoding="utf-8"
    )
    reports = tmp_path / "reports"
    reports.mkdir()
    linked_directory = tmp_path / "linked"
    linked_paths = {reports / "progress.json", reports / "failure.log", linked_directory}
    try:
        for name in ("progress.json", "failure.log"):
            (reports / name).symlink_to(outside / name)
        linked_directory.symlink_to(outside, target_is_directory=True)
    except OSError:
        # Windows can deny unprivileged symlink creation. Still exercise the
        # same rejection branch instead of silently skipping the safety check.
        original = type(reports).is_symlink
        monkeypatch.setattr(
            type(reports), "is_symlink", lambda path: path in linked_paths or original(path)
        )
    for path in (reports, linked_directory, linked_directory / "nested"):
        assert safe_runtime_details("", path, DiagnosticTextBudget()) == {}


def test_runtime_diagnostics_prioritize_failure_over_shared_coverage_budget():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_workflow_details

    class Store:
        def get_run(self, run_id):
            return {
                "status": "FAILED",
                "template": "fastapiadmin",
                "error": "RuntimeError：native_modules.py:23（generate_modules），请检查本次运行报告",
            }

        def latest_revision(self, run_id, stage):
            return {}

    budget = DiagnosticTextBudget(limit=40)
    result = safe_workflow_details(Store(), "run", [], text_budget=budget)
    assert result["terminal_state"] == "FAILED"
    assert result["runtime_diagnostics"]["error_excerpt"].startswith(
        "RuntimeError：native_modules.py"
    )
    assert len(result["runtime_diagnostics"]["error_excerpt"]) == 40
    assert budget.remaining == 0


def test_native_progress_allowlist_covers_real_literal_stages():
    import ast
    import inspect

    from scripts.ci_real_model import NATIVE_PROGRESS_STAGES
    from workbench import native_lab

    # The public entrypoint owns the port lease; the module contains the actual
    # acceptance phases, including the implementation called within that lease.
    tree = ast.parse(inspect.getsource(native_lab))
    stages = {
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "stage"
    }
    assert stages == NATIVE_PROGRESS_STAGES


def test_native_exception_headline_redaction_precedes_truncation_and_ignores_log(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, safe_runtime_details

    secret = "private-exact-credential-canary"
    (tmp_path / "failure.log").write_text(
        "ValueError at native_modules.py:8 (generate_modules): "
        + "x" * 595
        + secret
        + "\nsubprocess private output",
        encoding="utf-8",
    )
    budget = DiagnosticTextBudget(secrets=(secret,))
    result = safe_runtime_details("", tmp_path, budget)
    message = result["native_exception"]["message_excerpt"]
    assert len(message) == 600
    assert "private" not in json.dumps(result)
    assert message.endswith("[REDA")


def test_approved_plan_replay_preserves_exact_normalized_customer_contract(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan
    from workbench.domain import Plan

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    reports = tmp_path / "native-evidence"
    reports.mkdir()
    (reports / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    (reports / "raw-provider-response.json").write_text("unselected secret", encoding="utf-8")
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    budget = DiagnosticTextBudget(secrets=("test-only-secret",), limit=0)
    result = preserve_approved_customer_plan(reports, destination, budget)
    assert result["status"] == "saved" and result["exact_normalized_plan"] is True
    assert result["file"] == destination.name
    assert result["bytes"] == len(destination.read_bytes())
    assert (
        json.loads(destination.read_text(encoding="utf-8"))
        == Plan.model_validate(plan).model_dump()
    )
    assert list(destination.parent.iterdir()) == [destination]
    assert "unselected secret" not in destination.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "secret_text",
    [
        "test-only-secret",
        "password=credential_canary",
        "Authorization: Bearer header_canary",
        "https://alice:credential_canary@example.invalid",
        "API_KEY=credential_canary",
        "sk-credentialcanary12345",
        'metadata {"password": "credential_canary"}',
    ],
)
def test_approved_plan_replay_rejects_credentials_before_persistence(tmp_path, secret_text):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["acceptance"].append(secret_text)
    (tmp_path / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    result = preserve_approved_customer_plan(
        tmp_path, destination, DiagnosticTextBudget(secrets=("test-only-secret",))
    )
    assert result == {"status": "secret_scan_rejected"}
    assert not destination.exists()
    assert secret_text not in json.dumps(result)


def test_approved_plan_replay_rejects_unknown_schema_and_does_not_read_other_files(tmp_path):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    budget = DiagnosticTextBudget()
    (tmp_path / "design.json").write_text('{"secret": "unapproved plan"}', encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, budget) == {
        "status": "unavailable"
    }
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["provider_headers"] = "private provider data"
    (tmp_path / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, budget) == {
        "status": "invalid_schema"
    }
    assert not destination.exists()


def test_approved_plan_replay_size_is_bounded_on_read_and_normalized_write(tmp_path):
    from scripts.ci_real_model import (
        MAX_REPLAY_PLAN_BYTES,
        DiagnosticTextBudget,
        preserve_approved_customer_plan,
    )

    source = tmp_path / "approved-spec.json"
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    source.write_bytes(b" " * (MAX_REPLAY_PLAN_BYTES + 1))
    assert preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == {
        "status": "size_limit"
    }
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["acceptance"] = ["中文" * 1000] * 21
    compact = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    assert len(compact.encode("utf-8")) > MAX_REPLAY_PLAN_BYTES
    source.write_text(compact, encoding="utf-8")
    assert preserve_approved_customer_plan(tmp_path, destination, DiagnosticTextBudget()) == {
        "status": "size_limit"
    }
    assert not destination.exists()


def test_approved_plan_replay_rejects_linked_input(tmp_path, monkeypatch):
    from scripts.ci_real_model import DiagnosticTextBudget, preserve_approved_customer_plan

    real = tmp_path / "actual.json"
    real.write_bytes((ROOT / "examples/plans/customer-service.json").read_bytes())
    reports = tmp_path / "reports"
    reports.mkdir()
    destination = tmp_path / "safe-artifacts/approved-plan-replay.json"
    try:
        (reports / "approved-spec.json").symlink_to(real)
    except OSError:
        original = type(reports).is_symlink
        monkeypatch.setattr(
            type(reports),
            "is_symlink",
            lambda path: path == reports / "approved-spec.json" or original(path),
        )
    assert preserve_approved_customer_plan(reports, destination, DiagnosticTextBudget()) == {
        "status": "unsafe_path"
    }
    assert not destination.exists()


def test_failed_native_harness_preserves_replay_before_private_cleanup(tmp_path, monkeypatch):
    import tempfile
    from pathlib import Path
    from types import SimpleNamespace

    import uvicorn

    from scripts import ci_real_model
    from workbench import api
    from workbench import settings as settings_module
    from workbench.filesystem import write_json

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    public_root = tmp_path / "public"
    public_root.mkdir()
    monkeypatch.setattr(settings_module, "ROOT", public_root)
    monkeypatch.setattr(ci_real_model, "customer_request", lambda: "Synthetic customer request")

    class Store:
        def get_run(self, run_id):
            assert run_id == "test-run"
            return {
                "status": "FAILED",
                "template": "fastapiadmin",
                "error": "AssertionError：business_probe.py:123（customer_service_acceptance）",
            }

        def latest_revision(self, run_id, stage):
            return {"plan": plan} if stage == "design" else {}

    application = SimpleNamespace(state=SimpleNamespace(token="test-auth", store=Store()))
    monkeypatch.setattr(api, "create_app", lambda *args, **kwargs: application)
    monkeypatch.setattr(uvicorn, "Config", lambda *args, **kwargs: None)
    server = SimpleNamespace(started=True, run=lambda: None, should_exit=False)
    monkeypatch.setattr(uvicorn, "Server", lambda *args: server)

    with tempfile.TemporaryDirectory(dir=tmp_path) as private:
        directory = Path(private)

        def failed_browser(command, **kwargs):
            write_json(directory / "browser-result.json", {"run_id": "test-run"})
            reports = directory / "private-platform/runs/test-run/native-evidence"
            write_json(reports / "approved-spec.json", plan)
            write_json(reports / "progress.json", {"stage": "customer-service-http"})
            (reports / "failure.log").write_text(
                "AssertionError at business_probe.py:123 (customer_service_acceptance): "
                "Native API failed: POST /business/tasks/create HTTP 422 test-only-secret\n"
                "raw log must remain private",
                encoding="utf-8",
            )
            return SimpleNamespace(returncode=1)

        monkeypatch.setattr(ci_real_model.subprocess, "run", failed_browser)
        with pytest.raises(SafeFailure, match="workflow_not_ready") as caught:
            ci_real_model.run_acceptance(
                config(), SimpleNamespace(statuses=[200]), directory, "fastapiadmin"
            )
        details = caught.value.details
        assert details["terminal_state"] == "FAILED"
        assert details["runtime_diagnostics"]["native_stage"] == "customer-service-http"
        assert "HTTP 422" in details["runtime_diagnostics"]["native_exception"]["message_excerpt"]
        assert details["approved_plan_replay"]["status"] == "saved"
        assert "test-only-secret" not in json.dumps(details)
        assert "raw log" not in json.dumps(details)
    assert not directory.exists()
    replay = public_root / "reports/real-model/approved-plan-replay.json"
    assert json.loads(replay.read_text(encoding="utf-8"))["business"] == plan["business"]
    assert list(replay.parent.iterdir()) == [replay]


def test_schema_root_validation_reason_is_bounded_redacted_without_input():
    from pydantic import BaseModel, model_validator

    from scripts.ci_real_model import DiagnosticTextBudget, response_receipt

    class Contract(BaseModel):
        value: str

        @model_validator(mode="after")
        def validate_contract(self):
            raise ValueError("Known transition required; exact-private-canary " + "x" * 2000)

    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({"value": "provider-input-never-exported"}),
                        "reasoning_content": "reasoning-never-exported",
                    },
                }
            ]
        }
    ).encode()
    budget = DiagnosticTextBudget(secrets=("exact-private-canary",), limit=800)
    first = response_receipt(200, raw, "plan", Contract, text_budget=budget)
    second = response_receipt(200, raw, "plan", Contract, text_budget=budget)
    assert first["schema_errors"][0]["field_path"] == []
    assert first["schema_errors"][0]["message"].startswith("Value error, Known transition required")
    assert len(first["schema_errors"][0]["message"]) == 600
    assert len(second["schema_errors"][0]["message"]) == 200
    encoded = json.dumps([first, second])
    for forbidden in (
        "exact-private-canary",
        "provider-input-never-exported",
        "reasoning-never-exported",
    ):
        assert forbidden not in encoded
    assert "[REDACTED]" in encoded


@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_customer_employee_task_scope_binds_approved_requirement(scope):
    from copy import deepcopy

    from workbench.domain import Requirement

    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permissions = spec["business"]["permissions"]
    permissions[:] = [p for p in permissions if (p["role"], p["entity"]) != ("employee", "tasks")]
    permissions.append({"role": "employee", "entity": "tasks", "actions": ["read"], "scope": scope})
    approved = Requirement(
        summary="已确认角色合同",
        users=["普通员工"],
        data_scope="shared",
        features=[],
        acceptance=[],
        facts={"business": deepcopy(spec["business"])},
    )
    require_customer_spec(spec, approved_requirement=approved.model_dump())
    permissions[-1]["scope"] = "assigned" if scope == "own" else "own"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec, approved_requirement=approved.model_dump())
    permissions[-1]["scope"] = "all"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("scope", ["own", "assigned"])
@pytest.mark.parametrize(
    "action", ["create", "update", "archive", "add_note", "assign", "transition", "read_metrics"]
)
def test_customer_employee_tasks_remain_read_only_under_each_allowed_scope(scope, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permissions = spec["business"]["permissions"]
    permissions[:] = [p for p in permissions if (p["role"], p["entity"]) != ("employee", "tasks")]
    permissions.append(
        {"role": "employee", "entity": "tasks", "actions": ["read", action], "scope": scope}
    )
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize(
    "template,leaf",
    [
        ("python-basic", "product"),
        ("fastapiadmin", "native-evidence"),
        ("yudao-vben", "native-evidence"),
    ],
)
def test_approved_replay_uses_only_registered_generated_artifact(tmp_path, template, leaf):
    from scripts.ci_real_model import (
        DiagnosticTextBudget,
        approved_plan_artifact_directory,
        preserve_approved_customer_plan,
    )

    source = approved_plan_artifact_directory(tmp_path, "synthetic-run", template)
    assert source == tmp_path / "runs/synthetic-run" / leaf
    source.mkdir(parents=True)
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    (source / "candidate-plan.json").write_text(json.dumps(plan), encoding="utf-8")
    destination = tmp_path / "public/approved-plan-replay.json"
    assert (
        preserve_approved_customer_plan(source, destination, DiagnosticTextBudget())["status"]
        == "unavailable"
    )
    (source / "approved-spec.json").write_text(json.dumps(plan), encoding="utf-8")
    assert (
        preserve_approved_customer_plan(source, destination, DiagnosticTextBudget())["status"]
        == "saved"
    )
    assert json.loads(destination.read_text(encoding="utf-8"))["business"] == plan["business"]


@pytest.mark.parametrize("run_id", [None, "../outside", "a/b", "a\\b", "", "a" * 101])
def test_approved_replay_rejects_invalid_run_artifact_identity(tmp_path, run_id):
    from scripts.ci_real_model import approved_plan_artifact_directory

    assert approved_plan_artifact_directory(tmp_path, run_id, "python-basic") is None


def test_notification_schema_exposes_existing_cross_field_invariants():
    from workbench.business_contracts import NotificationSpec

    fields = NotificationSpec.model_json_schema()["properties"]
    assert "never null or a wildcard" in fields["transition"]["description"]
    assert "per named transition and recipient" in fields["transition"]["description"]
    assert "other events require null" in fields["due_field"]["description"]
````
