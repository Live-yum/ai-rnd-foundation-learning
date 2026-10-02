# tests/test_real_model_ci.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](tests__test_real_model_ci_py--002.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.ci_real_model`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `config`（L24–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`configuration`。 返回路径：L25的`configuration({"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": "test-only-secret"})`。
- `test_invalid_configuration_fails_before_provider_access`（L38–L40）：接收`values`。 调用`pytest.raises`、`configuration`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_not_in_config_representation`（L43–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44断言`"test-only-secret" not in repr(config())`。 调用`repr`、`config`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reject_untrusted_execution_context`（L58–L67）：接收`key`、`value`。 调用`next`、`iter`、`pytest.raises`、`trusted_dispatch`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_provider_error_is_sanitized_and_never_retried`（L71–L88）：接收`status`。 控制顺序：L84断言`caught.value.status == status`；L85断言`"test-only-secret" not in str(caught.value)`；L86断言`len(calls) == 1`；L87断言`str(calls[0].url) == ENDPOINT + "/chat/completions"`；L88断言`json.loads(calls[0].content) == SMOKE_PAYLOAD`。 调用`pytest.raises`、`smoke`、`config`、`httpx.MockTransport`、`str`、`len`、`json.loads`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_provider_error_is_sanitized_and_never_retried.handler`（L74–L80）：接收`request`。 调用`calls.append`、`httpx.Response`。 返回路径：L76的`httpx.Response( status, json={"error": {"message": "test-only-secret raw provider data"}},…`。
- `test_successful_smoke_receipt_has_no_provider_content`（L91–L106）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102断言`receipt == { "passed": True, "http_status": 200, "actual_provider_request": True, }`。 调用`httpx.MockTransport`、`httpx.Response`、`smoke`、`config`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_smoke_response_fails_closed`（L110–L115）：接收`body`。 调用`pytest.raises`、`smoke`、`config`、`httpx.MockTransport`、`httpx.Response`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_rejects_substitution_and_bounds_tokens_and_calls`（L118–L153）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`json.loads(requests[0].content)["max_tokens"] == 65536`。 调用`BoundedRealTransport`、`config`、`transport.transport.close`、`httpx.MockTransport`、`requests.append`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_model_plan_must_preserve_explicit_customer_obligations`（L157–L171）：接收`mutation`。 控制顺序：L160按`mutation == "isolation"`分支；L162按`mutation == "roles"`分支；L164按`mutation == "metrics"`分支；L166按`mutation == "workflow"`分支。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`require_customer_spec`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_gate_requires_each_metric_meaning_not_just_four_kinds`（L207–L211）：接收`name`、`change`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next(metric for metric in spec["business"]["metrics"] if metric["…`、`next`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_gate_accepts_provider_metric_names_extra_metrics_and_equivalent_resolution_filter`（L214–L223）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L216遍历`enumerate(spec["business"]["metrics"])`；L218按`metric["kind"] == "average_duration"`分支；L220按`metric["filters"]`分支；L222断言`len(spec["business"]["metrics"]) > 5`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`enumerate`、`len`、`require_customer_spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_gate_requires_every_requested_reminder`（L237–L245）：接收`entity`、`event`、`transition`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_gate_only_pins_the_explicit_resolution_recipient`（L248–L258）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L250遍历`spec["business"]["notifications"]`；L251按`(notice["entity"], notice["transition"]) != ("requests", "resolve")`分支；L254遍历`spec["business"]["notifications"]`；L255按`(notice["entity"], notice["transition"]) == ("requests", "resolve")`分支。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`require_customer_spec`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_query_access_never_implies_customer_write_or_audit_permissions`（L263–L271）：接收`role`、`action`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next( grant for grant in spec["business"]["permissions"] if grant…`、`next`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_role_administration_is_manager_only`（L275–L279）：接收`role`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`spec["business"]["role_admin_roles"].append`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_collaboration_tasks_are_created_only_by_managers`（L283–L300）：接收`role`、`scope`。 控制顺序：L293按`permission is None`分支。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`spec["business"]["permissions"].append`、`permission["actions"].append`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_gate_rejects_each_explicit_role_action_omission`（L331–L340）：接收`role`、`entity`、`action`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`permission["actions"].remove`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_managers_require_all_record_scope`（L345–L354）：接收`entity`、`scope`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_collaboration_task_assignment_is_manager_only`（L358–L375）：接收`role`、`scope`。 控制顺序：L368按`permission is None`分支。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`spec["business"]["permissions"].append`、`permission["actions"].append`、`pytest.raises`、`require_customer_spec`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_is_manual_environment_scoped_and_artifact_allowlisted`（L378–L457）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L385断言`set(doc["on"]) == {"workflow_dispatch"}`；L387断言`job["environment"] == "rnd"`；L388断言`"github.event_name == 'workflow_dispatch'" in job["if"]`；L389断言`REPOSITORY in job["if"]`；L391断言`len(secret_steps) == 2`；L392断言`secret_steps[0]["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"`；L393断言`secret_steps[0]["env"]["BASE_URL"] == "${{ vars.BASE_URL }}"`；L394断言`secret_steps[0]["env"]["MODE"] == "${{ vars.MODE }}"`。后续分支沿下方源码相同行号继续阅读。 调用`yaml.load`、`(ROOT / ".github/workflows/real-model.yml").read_text`、`set`、`step.get`、`len`、`step.get("uses", "").startswith`、`(ROOT / ".github/workflows/native-probe.yml").read_text`、`entry["jobs"]["verify-bundles"].get`、`entry.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_profiles_use_authorized_configuration_despite_hostile_ambient_overrides`（L460–L476）：接收`tmp_path`、`monkeypatch`。 控制顺序：L470遍历`STAGES`；L472断言`profile.base_url == ENDPOINT and profile.model == MODEL`；L473断言`profile.api_key.get_secret_value() == "test-only-secret"`；L474断言`settings.max_model_calls == 16`；L475断言`settings.install_products is True`；L476断言`settings.model_review is True`。 调用`monkeypatch.setenv`、`acceptance_settings`、`config`、`settings.require_model`、`settings.model_for`、`profile.api_key.get_secret_value`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_full_run_requires_matching_same_run_successful_smoke`（L479–L500）：接收`tmp_path`。 控制顺序：L497断言`verified_smoke_receipt(path, config(), env)["passed"] is True`。 调用`pytest.raises`、`verified_smoke_receipt`、`config`、`path.write_text`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_user_smoke_payload_preserved_by_real_transport`（L503–L526）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L519断言`json.loads(requests[0].content) == SMOKE_PAYLOAD`；L520断言`"max_tokens" not in json.loads(requests[0].content)`。 调用`BoundedRealTransport`、`config`、`transport.transport.close`、`httpx.MockTransport`、`requests.append`、`httpx.Response`、`transport.handle_request`、`httpx.Request`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_actions_empty_secret_mapping_identifies_only_field_presence`（L529–L543）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L534断言`caught.value.code == "missing_configuration_API_KEY"`；L535断言`caught.value.details == { "BASE_URL_present": True, "MODE_present": True, "API_KEY_pr…`；L542断言`ENDPOINT not in json.dumps(caught.value.details)`；L543断言`MODEL not in json.dumps(caught.value.details)`。 调用`pytest.raises`、`configuration`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_string_mode_reports_field_name_not_value`（L547–L551）：接收`value`。 控制顺序：L550断言`caught.value.code == "invalid_configuration_type_MODE"`；L551断言`"test-only-secret" not in str(caught.value)`。 调用`pytest.raises`、`configuration`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_string_actions_values_and_exact_secret_mapping_are_accepted`（L554–L557）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L556断言`cfg.model == MODEL and cfg.base_url == ENDPOINT`；L557断言`cfg.key.get_secret_value() == "test-only-secret"`。 调用`configuration`、`cfg.key.get_secret_value`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_manual_runs_on_authorized_branches_can_use_provider`（L561–L586）：接收`tmp_path`、`ref`。 调用`trusted_dispatch`、`path.write_text`、`json.dumps`、`env.update`、`str`、`pytest.raises`、`pytest.mark.parametrize`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_provider_diagnostics_emit_only_schema_codes_counts_and_flags`（L589–L617）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L608断言`receipt["schema_valid"] is False`；L609断言`receipt["schema_error_types"] == ["extra_forbidden", "missing"]`；L610断言`receipt["usage"] == {"total_tokens": 42}`；L612遍历`( "test-only-secret", "private reasoning", "injected-private-fiel…`；L617断言`forbidden not in encoded`。 调用`json.dumps( { "choices": [ { "finish_reason": "stop", "message": …`、`json.dumps`、`response_receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_buffered_diagnostic_transport_preserves_client_response_and_secret_privacy`（L620–L634）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L629断言`smoke(config(), transport)["passed"] is True`；L630断言`transport.receipts[0]["finish_reason"] == "stop"`；L631断言`transport.receipts[0]["usage"] == {"total_tokens": 10}`；L632断言`"test-only-secret" not in json.dumps(transport.receipts)`。 调用`BoundedRealTransport`、`config`、`transport.transport.close`、`httpx.MockTransport`、`httpx.Response`、`smoke`、`json.dumps`、`transport.shutdown`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_prompt_is_prose_not_precomputed_plan`（L637–L647）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L641断言`"客户服务管理系统" in request`；L642断言`"不是模型响应" in request`。 调用`customer_request`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`require_customer_spec`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_paid_matrix_covers_three_native_ui_families`（L650–L666）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L653遍历`("native-probe.yml", "real-model.yml")`；L658断言`{row["template"] for row in job["strategy"]["matrix"]["include"]} == { "python-basic"…`；L663断言`"feat/customer-service-acceptance" in job["if"]`；L664断言`not any( "API_KEY" in step.get("env", {}) for step in job["steps"] if step.get("uses"…`。 调用`yaml.load`、`(ROOT / ".github/workflows" / name).read_text`、`any`、`step.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requirement_snapshot_preserves_entity_mapping_without_text`（L669–L683）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L682断言`[item["entity"] for item in result] == ["requests", "tasks"]`；L683断言`"test-only-secret" not in json.dumps(result)`。 调用`contract_snapshot`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_safe_coverage_diagnostics_include_source_and_no_raw_prose_or_choices`（L686–L710）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L702断言`any(item["source"]["section"] == "features" for item in result)`；L703断言`any( item["source"]["encoding"] == "structured" for item in result if item["source"][…`；L708断言`any(item["targets"] == [{"entity": "customers", "field": "category"}] for item in res…`；L709断言`any(item.get("expected_count") == 1 for item in result)`；L710断言`"test-only-secret" not in json.dumps(result)`。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Requirement`、`safe_coverage_details`、`requirement.model_dump`、`plan.model_dump`、`any`、`item.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_label_failure_is_exact_finite_code_with_no_description_export`（L713–L722）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L719断言`result["code"] == "native_label_contract"`；L720断言`result["entity_labels"][0]["allowed_characters"] is False`；L721断言`result["entity_labels"][0]["single_line"] is True`；L722断言`"test-only-secret" not in json.dumps(result)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`safe_native_plan_details`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_native_plan_validation_message_has_a_finite_safe_code`（L725–L738）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L733遍历`(validate_plan, runtime_config)`；L735遍历`ast.walk(tree)`；L736按`isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call)`分支；L737断言`isinstance(node.exc.args[0], ast.Constant)`；L738断言`node.exc.args[0].value in DESIGN_REASON_CODES`。 调用`ast.parse`、`inspect.getsource`、`ast.walk`、`isinstance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_diagnostics_separate_model_coverage_and_native_origins`（L741–L789）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L785断言`result["coverage_diagnostics"][0]["codes"] == ["planner_unsupported"]`；L786断言`result["coverage_diagnostics"][0]["origin"] == "planner_unsupported"`；L787断言`result["coverage_diagnostics"][1]["origin"] == "requirement_coverage"`；L788断言`result["unsupported_diagnostics"][0]["topics"] == ["date_range", "capability"]`；L789断言`"test-only-secret" not in json.dumps(result)`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Requirement`、`coverage_gaps`、`Plan.model_validate`、`safe_workflow_details`、`Store`、`DiagnosticTextBudget`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_diagnostics_separate_model_coverage_and_native_origins.Store`（L757–L780）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_workflow_diagnostics_separate_model_coverage_and_native_origins.Store.get_run`（L758–L773）：接收`run_id`。 调用`len`。 返回路径：L759的`{ "status": "BLOCKED", "template": "python-basic", "model_calls": 4, "pending": { "stage":…`。
- `test_workflow_diagnostics_separate_model_coverage_and_native_origins.Store.latest_revision`（L775–L780）：接收`run_id`、`stage`。 调用`requirement.model_dump`。 返回路径：L776的`{"requirement": requirement.model_dump()} if stage == "requirements" else {"plan": plan}`。
- `test_validation_excerpt_scrubs_credentials_headers_tokens_and_url_userinfo`（L808–L813）：接收`value`、`secret`。 控制顺序：L812断言`secret not in result`；L813断言`"REDACTED" in result`。 调用`DiagnosticTextBudget().excerpt`、`DiagnosticTextBudget`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_key_redaction_precedes_truncation_and_total_budget_is_shared`（L816–L826）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L822断言`"exact" not in first and len(first) <= 600`；L824断言`len(first) + sum(map(len, rest)) == 6000`；L825断言`all(len(item) <= 600 for item in rest)`；L826断言`budget.excerpt("more") == ""`。 调用`DiagnosticTextBudget`、`budget.excerpt`、`len`、`budget.excerpts`、`sum`、`map`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_safe_coverage_excerpt_is_selected_and_redacted_without_full_requirement`（L829–L849）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L847断言`"必须支持精确筛选" in rendered`；L848断言`"opaque-private-canary" not in rendered`；L849断言`"private summary" not in rendered and "unrelated unselected" not in rendered`。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Requirement`、`safe_coverage_details`、`requirement.model_dump`、`DiagnosticTextBudget`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_review_gap_diagnostics_preserve_blocking_count_and_omit_other_model_text`（L852–L868）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L864断言`result["uncovered_requirements_count"] == 1`；L865断言`"客户历史请求未验证" in result["uncovered_requirement_excerpts"][0]`；L867断言`"opaque-private-canary" not in encoded and "raw private provider" not in encoded`；L868断言`review.uncovered_requirements == ["客户历史请求未验证，opaque-private-canary"]`。 调用`ModelReview`、`completed_stage_details`、`DiagnosticTextBudget`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_real_model_ci.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L870。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`34790`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_real_model_ci.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "38e9a574c272a00a68d39129f6388b994a2ff53f079b78cbc0875acd5550ece6"} -->
````python
# tests/test_real_model_ci.py
"""No paid calls here: test doubles only test the real-run harness' safety boundaries."""

import json

import httpx
import pytest

from scripts.ci_real_model import (
    ENDPOINT,
    MODEL,
    REFS,
    REPOSITORY,
    SMOKE_PAYLOAD,
    BoundedRealTransport,
    SafeFailure,
    configuration,
    require_customer_spec,
    smoke,
    trusted_dispatch,
)
from workbench.settings import ROOT


def config():
    return configuration({"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": "test-only-secret"})


@pytest.mark.parametrize(
    "values",
    [
        {},
        {"BASE_URL": "https://evil.example", "MODE": MODEL, "API_KEY": "secret"},
        {"BASE_URL": ENDPOINT, "MODE": "fallback-model", "API_KEY": "secret"},
        {"BASE_URL": ENDPOINT, "MODE": MODEL},
        {"BASE_URL": ENDPOINT + "/v1", "MODE": MODEL, "API_KEY": "secret"},
    ],
)
def test_invalid_configuration_fails_before_provider_access(values):
    with pytest.raises(SafeFailure, match="configuration"):
        configuration(values)


def test_secret_not_in_config_representation():
    assert "test-only-secret" not in repr(config())


@pytest.mark.parametrize(
    "key,value",
    [
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_EVENT_NAME", "pull_request_target"),
        ("GITHUB_EVENT_NAME", "schedule"),
        ("GITHUB_REPOSITORY", "attacker/fork"),
        ("GITHUB_REF", "refs/heads/untrusted"),
    ],
)
def test_reject_untrusted_execution_context(key, value):
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": next(iter(REFS)),
    }
    env[key] = value
    with pytest.raises(SafeFailure, match="untrusted_dispatch"):
        trusted_dispatch(env)


@pytest.mark.parametrize("status", [301, 400, 401, 403, 404, 429, 500])
def test_smoke_provider_error_is_sanitized_and_never_retried(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            status,
            json={"error": {"message": "test-only-secret raw provider data"}},
            headers={"location": "https://evil.example"},
        )

    with pytest.raises(SafeFailure) as caught:
        smoke(config(), httpx.MockTransport(handler))
    assert caught.value.status == status
    assert "test-only-secret" not in str(caught.value)
    assert len(calls) == 1
    assert str(calls[0].url) == ENDPOINT + "/chat/completions"
    assert json.loads(calls[0].content) == SMOKE_PAYLOAD


def test_successful_smoke_receipt_has_no_provider_content():
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "OK test-only-secret"}}],
                "provider_private_field": "must not leave",
            },
        )
    )
    receipt = smoke(config(), transport)
    assert receipt == {
        "passed": True,
        "http_status": 200,
        "actual_provider_request": True,
    }


@pytest.mark.parametrize("body", [{}, {"choices": []}, {"choices": [{"message": {"content": ""}}]}])
def test_invalid_smoke_response_fails_closed(body):
    with pytest.raises(SafeFailure, match="invalid_smoke_response"):
        smoke(
            config(),
            httpx.MockTransport(lambda request: httpx.Response(200, json=body)),
        )


def test_transport_rejects_substitution_and_bounds_tokens_and_calls():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    requests = []
    transport.transport = httpx.MockTransport(
        lambda req: requests.append(req) or httpx.Response(200)
    )
    try:
        transport.handle_request(
            httpx.Request(
                "POST",
                ENDPOINT + "/chat/completions",
                headers={"Authorization": "Bearer test-only-secret"},
                json={"model": MODEL, "max_tokens": 90000},
            )
        )
        assert json.loads(requests[0].content)["max_tokens"] == 65536
        with pytest.raises(SafeFailure, match="model_substitution"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": "fallback"})
            )
        with pytest.raises(SafeFailure, match="request_scope"):
            transport.handle_request(
                httpx.Request(
                    "POST",
                    "https://evil.example/chat/completions",
                    json={"model": MODEL},
                )
            )
        transport.calls = 17
        with pytest.raises(SafeFailure, match="request_scope_or_budget"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json={"model": MODEL})
            )
    finally:
        transport.shutdown()


@pytest.mark.parametrize("mutation", ["roles", "metrics", "isolation", "workflow", "category"])
def test_actual_model_plan_must_preserve_explicit_customer_obligations(mutation):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    require_customer_spec(spec)
    if mutation == "isolation":
        spec["data_scope"] = "per_user"
    elif mutation == "roles":
        spec["business"]["registration"]["default_role"] = "manager"
    elif mutation == "metrics":
        spec["business"]["metrics"] = []
    elif mutation == "workflow":
        spec["business"]["workflows"] = []
    else:
        spec["entities"][0]["fields"][3]["choices"] = ["企业"]
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize(
    "name,change",
    [
        ("total", {"filters": [{"field": "request_state", "value": "resolved"}]}),
        ("resolved_total", {"filters": []}),
        (
            "resolved_total",
            {"filters": [{"field": "request_state", "op": "ne", "value": "resolved"}]},
        ),
        (
            "resolved_total",
            {"entity": "tasks", "filters": [{"field": "task_state", "value": "resolved"}]},
        ),
        (
            "resolved_total",
            {
                "filters": [
                    {"field": "request_state", "value": "resolved"},
                    {"field": "priority", "value": "紧急"},
                ]
            },
        ),
        ("resolution", {"start_field": "due_at"}),
        ("resolution", {"end_field": "due_at"}),
        ("resolution", {"filters": [{"field": "priority", "value": "紧急"}]}),
        ("customer_categories", {"entity": "requests", "group_by": "customer_id"}),
        ("customer_categories", {"group_by": "organization"}),
        ("customer_categories", {"filters": [{"field": "category", "value": "企业"}]}),
        ("daily", {"time_field": "due_at"}),
        ("daily", {"entity": "customers"}),
        ("daily", {"filters": [{"field": "request_state", "value": "resolved"}]}),
    ],
)
def test_customer_gate_requires_each_metric_meaning_not_just_four_kinds(name, change):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    next(metric for metric in spec["business"]["metrics"] if metric["name"] == name).update(change)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_customer_gate_accepts_provider_metric_names_extra_metrics_and_equivalent_resolution_filter():
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    for number, metric in enumerate(spec["business"]["metrics"]):
        metric["name"] = f"provider_metric_{number}"
        if metric["kind"] == "average_duration":
            metric["filters"] = []
        elif metric["filters"]:
            metric["filters"] = [{"field": "request_state", "op": "in", "value": ["resolved"]}]
    assert len(spec["business"]["metrics"]) > 5
    require_customer_spec(spec)


@pytest.mark.parametrize("entity", ["requests", "tasks"])
@pytest.mark.parametrize(
    "event,transition",
    [
        ("assigned", None),
        ("note_added", None),
        ("transitioned", "start"),
        ("transitioned", "resolve"),
        ("due", None),
    ],
)
def test_customer_gate_requires_every_requested_reminder(entity, event, transition):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    spec["business"]["notifications"] = [
        notice
        for notice in spec["business"]["notifications"]
        if (notice["entity"], notice["event"], notice["transition"]) != (entity, event, transition)
    ]
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_customer_gate_only_pins_the_explicit_resolution_recipient():
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    for notice in spec["business"]["notifications"]:
        if (notice["entity"], notice["transition"]) != ("requests", "resolve"):
            notice["recipient"] = "creator" if notice["recipient"] == "assignee" else "assignee"
    require_customer_spec(spec)
    for notice in spec["business"]["notifications"]:
        if (notice["entity"], notice["transition"]) == ("requests", "resolve"):
            notice["recipient"] = "assignee"
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role", ["service", "employee"])
@pytest.mark.parametrize("action", ["create", "update", "archive", "add_note", "read_audit"])
def test_customer_query_access_never_implies_customer_write_or_audit_permissions(role, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    next(
        grant
        for grant in spec["business"]["permissions"]
        if grant["role"] == role and grant["entity"] == "customers"
    )["actions"].append(action)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role", ["service", "employee"])
def test_customer_role_administration_is_manager_only(role):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    spec["business"]["role_admin_roles"].append(role)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role,scope", [("service", "assigned"), ("employee", "own")])
def test_customer_collaboration_tasks_are_created_only_by_managers(role, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        (
            grant
            for grant in spec["business"]["permissions"]
            if grant["role"] == role and grant["entity"] == "tasks"
        ),
        None,
    )
    if permission is None:
        spec["business"]["permissions"].append(
            {"role": role, "entity": "tasks", "actions": ["read", "create"], "scope": scope}
        )
    else:
        permission["actions"].append("create")
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize(
    "role,entity,action",
    [
        ("manager", "customers", action)
        for action in ("create", "read", "update", "archive", "read_audit")
    ]
    + [
        ("manager", entity, action)
        for entity in ("requests", "tasks")
        for action in (
            "create",
            "read",
            "update",
            "archive",
            "add_note",
            "read_history",
            "read_audit",
            "assign",
            "transition",
        )
    ]
    + [
        ("service", entity, action)
        for entity in ("requests", "tasks")
        for action in ("read", "update", "add_note", "transition", "read_history", "read_audit")
    ]
    + [("employee", "requests", action) for action in ("create", "read")],
)
def test_customer_gate_rejects_each_explicit_role_action_omission(role, entity, action):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        grant
        for grant in spec["business"]["permissions"]
        if (grant["role"], grant["entity"]) == (role, entity)
    )
    permission["actions"].remove(action)
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("entity", ["customers", "requests", "tasks"])
@pytest.mark.parametrize("scope", ["own", "assigned"])
def test_customer_managers_require_all_record_scope(entity, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        grant
        for grant in spec["business"]["permissions"]
        if grant["role"] == "manager" and grant["entity"] == entity
    )
    permission["scope"] = scope
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


@pytest.mark.parametrize("role,scope", [("service", "assigned"), ("employee", "own")])
def test_customer_collaboration_task_assignment_is_manager_only(role, scope):
    spec = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    permission = next(
        (
            grant
            for grant in spec["business"]["permissions"]
            if grant["role"] == role and grant["entity"] == "tasks"
        ),
        None,
    )
    if permission is None:
        spec["business"]["permissions"].append(
            {"role": role, "entity": "tasks", "actions": ["read", "assign"], "scope": scope}
        )
    else:
        permission["actions"].append("assign")
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(spec)


def test_workflow_is_manual_environment_scoped_and_artifact_allowlisted():
    import yaml

    doc = yaml.load(
        (ROOT / ".github/workflows/real-model.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert set(doc["on"]) == {"workflow_dispatch"}
    job = doc["jobs"]["real-model"]
    assert job["environment"] == "rnd"
    assert "github.event_name == 'workflow_dispatch'" in job["if"]
    assert REPOSITORY in job["if"]
    secret_steps = [step for step in job["steps"] if "API_KEY" in step.get("env", {})]
    assert len(secret_steps) == 2
    assert secret_steps[0]["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"
    assert secret_steps[0]["env"]["BASE_URL"] == "${{ vars.BASE_URL }}"
    assert secret_steps[0]["env"]["MODE"] == "${{ vars.MODE }}"
    uploads = [
        step for step in job["steps"] if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert [step["with"]["path"] for step in uploads] == [
        "reports/real-model/summary.json",
        "reports/real-model/screenshots/*.png",
    ]
    entry = yaml.load(
        (ROOT / ".github/workflows/native-probe.yml").read_text(encoding="utf-8"),
        Loader=yaml.BaseLoader,
    )
    assert set(entry["on"]) == {"workflow_dispatch", "pull_request"}
    inputs = entry["on"]["workflow_dispatch"]["inputs"]
    assert inputs["real_model"]["type"] == "boolean"
    assert inputs["real_model"]["default"] == "false"
    assert inputs["real_model"]["required"] == "false"
    assert inputs["expected_sha"]["type"] == "string"
    assert inputs["expected_sha"]["default"] == ""
    assert set(entry["jobs"]) == {"verify-bundles", "real-model"}
    assert entry["jobs"]["verify-bundles"].get("environment") != "rnd"
    paid = entry["jobs"]["real-model"]
    assert paid["environment"] == "rnd"
    assert "uses" not in paid
    assert "github.event_name == 'workflow_dispatch'" in paid["if"]
    assert "inputs.real_model == true" in paid["if"]
    assert f"github.repository == '{REPOSITORY}'" in paid["if"]
    for ref in REFS:
        assert f"github.ref == '{ref}'" in paid["if"]
    assert "API_KEY" not in entry.get("env", {})
    assert "API_KEY" not in paid.get("env", {})
    guard = paid["steps"][0]
    assert guard["shell"] == "bash"
    assert guard["env"] == {"EXPECTED_SHA": "${{ inputs.expected_sha }}"}
    assert "set -euo pipefail" in guard["run"]
    assert '[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]' in guard["run"]
    assert 'test "$EXPECTED_SHA" = "$GITHUB_SHA"' in guard["run"]
    checkout = paid["steps"][1]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["ref"] == "${{ github.sha }}"
    assert checkout["with"]["persist-credentials"] == "false"
    paid_secret_steps = [step for step in paid["steps"] if "API_KEY" in step.get("env", {})]
    assert len(paid_secret_steps) == 2
    for step in paid_secret_steps:
        assert step["env"]["API_KEY"] == "${{ secrets.APK_KEY }}"
        assert step["env"]["BASE_URL"] == "${{ vars.BASE_URL }}"
        assert step["env"]["MODE"] == "${{ vars.MODE }}"
    assert [step["run"] for step in paid_secret_steps] == [
        "uv run python -m scripts.ci_real_model --phase smoke",
        "uv run python -m scripts.ci_real_model --phase full --template ${{ matrix.template }}",
    ]
    paid_uploads = [
        step for step in paid["steps"] if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert [step["with"]["path"] for step in paid_uploads] == [
        "reports/real-model/summary.json",
        "reports/real-model/approved-plan-replay.json",
        "reports/real-model/unapproved-design-contract.json",
        "reports/real-model/screenshots/*.png",
    ]
    assert paid_uploads[1]["if"] == "failure()"
    assert paid_uploads[1]["with"]["retention-days"] == "7"
    assert paid_uploads[2]["if"] == "failure()"
    assert paid_uploads[2]["with"]["retention-days"] == "7"


def test_all_profiles_use_authorized_configuration_despite_hostile_ambient_overrides(
    tmp_path, monkeypatch
):
    from scripts.ci_real_model import acceptance_settings
    from workbench.settings import STAGES

    monkeypatch.setenv("PLANNING_BASE_URL", "https://evil.example")
    monkeypatch.setenv("CODING_MODE", "silent-fallback")
    settings = acceptance_settings(config(), tmp_path)
    settings.require_model()
    for stage in STAGES:
        profile = settings.model_for(stage)
        assert profile.base_url == ENDPOINT and profile.model == MODEL
        assert profile.api_key.get_secret_value() == "test-only-secret"
    assert settings.max_model_calls == 16
    assert settings.install_products is True
    assert settings.model_review is True


def test_full_run_requires_matching_same_run_successful_smoke(tmp_path):
    from scripts.ci_real_model import verified_smoke_receipt

    path = tmp_path / "summary.json"
    env = {"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_SHA": "a" * 40}
    with pytest.raises(SafeFailure, match="matching_successful_smoke"):
        verified_smoke_receipt(path, config(), env)
    receipt = {
        "passed": True,
        "acceptance_scope": "smoke_only",
        "model": MODEL,
        "endpoint": ENDPOINT,
        "run_identity": ["1", "2", "a" * 40],
        "actual_http_calls": 1,
        "provider_statuses": [200],
        "smoke": {"passed": True, "http_status": 200, "actual_provider_request": True},
    }
    path.write_text(json.dumps(receipt), encoding="utf-8")
    assert verified_smoke_receipt(path, config(), env)["passed"] is True
    env["GITHUB_SHA"] = "b" * 40
    with pytest.raises(SafeFailure, match="matching_successful_smoke"):
        verified_smoke_receipt(path, config(), env)


def test_exact_user_smoke_payload_preserved_by_real_transport():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    requests = []
    transport.transport = httpx.MockTransport(
        lambda req: requests.append(req) or httpx.Response(200)
    )
    try:
        transport.handle_request(
            httpx.Request(
                "POST",
                ENDPOINT + "/chat/completions",
                headers={"Authorization": "Bearer test-only-secret"},
                json=SMOKE_PAYLOAD,
            )
        )
        assert json.loads(requests[0].content) == SMOKE_PAYLOAD
        assert "max_tokens" not in json.loads(requests[0].content)
        with pytest.raises(SafeFailure, match="unexpected_authorization"):
            transport.handle_request(
                httpx.Request("POST", ENDPOINT + "/chat/completions", json=SMOKE_PAYLOAD)
            )
    finally:
        transport.shutdown()


def test_actual_actions_empty_secret_mapping_identifies_only_field_presence():
    # The failed Actions job provided correct vars and an empty API_KEY binding.
    env = {"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": ""}
    with pytest.raises(SafeFailure) as caught:
        configuration(env)
    assert caught.value.code == "missing_configuration_API_KEY"
    assert caught.value.details == {
        "BASE_URL_present": True,
        "MODE_present": True,
        "API_KEY_present": False,
        "BASE_URL_matches_authorized_destination": True,
        "MODE_matches_authorized_model": True,
    }
    assert ENDPOINT not in json.dumps(caught.value.details)
    assert MODEL not in json.dumps(caught.value.details)


@pytest.mark.parametrize("value", [None, 1, True, [], {}])
def test_non_string_mode_reports_field_name_not_value(value):
    with pytest.raises(SafeFailure) as caught:
        configuration({"BASE_URL": ENDPOINT, "MODE": value, "API_KEY": "test-only-secret"})
    assert caught.value.code == "invalid_configuration_type_MODE"
    assert "test-only-secret" not in str(caught.value)


def test_string_actions_values_and_exact_secret_mapping_are_accepted():
    cfg = configuration({"BASE_URL": ENDPOINT, "MODE": MODEL, "API_KEY": "test-only-secret"})
    assert cfg.model == MODEL and cfg.base_url == ENDPOINT
    assert cfg.key.get_secret_value() == "test-only-secret"


@pytest.mark.parametrize("ref", sorted(REFS))
def test_only_explicit_manual_runs_on_authorized_branches_can_use_provider(tmp_path, ref):
    env = {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_REF": ref,
    }
    trusted_dispatch(env)
    # The former iteration marker cannot re-enable automatic paid calls.
    path = tmp_path / "event.json"
    path.write_text(
        json.dumps(
            {
                "head_commit": {
                    "message": "test: run authorized real-model validation iteration",
                    "id": "a" * 40,
                },
                "after": "a" * 40,
                "repository": {"full_name": REPOSITORY},
            }
        ),
        encoding="utf-8",
    )
    env.update(GITHUB_EVENT_NAME="push", GITHUB_SHA="a" * 40, GITHUB_EVENT_PATH=str(path))
    with pytest.raises(SafeFailure, match="untrusted_dispatch"):
        trusted_dispatch(env)


def test_provider_diagnostics_emit_only_schema_codes_counts_and_flags():
    from scripts.ci_real_model import response_receipt
    from workbench.domain import Requirement

    raw = json.dumps(
        {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": json.dumps({"injected-private-field": "test-only-secret"}),
                        "reasoning_content": "private reasoning must never leave",
                    },
                }
            ],
            "usage": {"total_tokens": 42, "secret": "test-only-secret"},
        }
    ).encode()
    receipt = response_receipt(200, raw, "requirement", Requirement)
    assert receipt["schema_valid"] is False
    assert receipt["schema_error_types"] == ["extra_forbidden", "missing"]
    assert receipt["usage"] == {"total_tokens": 42}
    encoded = json.dumps(receipt)
    for forbidden in (
        "test-only-secret",
        "private reasoning",
        "injected-private-field",
    ):
        assert forbidden not in encoded


def test_buffered_diagnostic_transport_preserves_client_response_and_secret_privacy():
    transport = BoundedRealTransport(config())
    transport.transport.close()
    body = {
        "choices": [{"finish_reason": "stop", "message": {"content": "OK"}}],
        "usage": {"total_tokens": 10},
    }
    transport.transport = httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    try:
        assert smoke(config(), transport)["passed"] is True
        assert transport.receipts[0]["finish_reason"] == "stop"
        assert transport.receipts[0]["usage"] == {"total_tokens": 10}
        assert "test-only-secret" not in json.dumps(transport.receipts)
    finally:
        transport.shutdown()


def test_customer_prompt_is_prose_not_precomputed_plan():
    from scripts.ci_real_model import customer_request

    request = customer_request()
    assert "客户服务管理系统" in request
    assert "不是模型响应" in request
    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    require_customer_spec(plan)
    plan["business"]["metrics"] = []
    with pytest.raises(SafeFailure, match="customer_obligation"):
        require_customer_spec(plan)


def test_paid_matrix_covers_three_native_ui_families():
    import yaml

    for name in ("native-probe.yml", "real-model.yml"):
        doc = yaml.load(
            (ROOT / ".github/workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader
        )
        job = doc["jobs"]["real-model"]
        assert {row["template"] for row in job["strategy"]["matrix"]["include"]} == {
            "python-basic",
            "fastapiadmin",
            "yudao-vben",
        }
        assert "feat/customer-service-acceptance" in job["if"]
        assert not any(
            "API_KEY" in step.get("env", {}) for step in job["steps"] if step.get("uses")
        )


def test_requirement_snapshot_preserves_entity_mapping_without_text():
    from scripts.ci_real_model import contract_snapshot

    result = contract_snapshot(
        {
            "field_requirements": [
                {"entity": "requests", "field": "title", "required": True},
                {"entity": "tasks", "field": "title", "required": False},
            ],
            "features": ["test-only-secret"],
        },
        requirement=True,
    )
    assert [item["entity"] for item in result] == ["requests", "tasks"]
    assert "test-only-secret" not in json.dumps(result)


def test_safe_coverage_diagnostics_include_source_and_no_raw_prose_or_choices():
    from scripts.ci_real_model import safe_coverage_details
    from workbench.domain import Plan, Requirement

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    requirement = Requirement(
        summary="test-only-secret",
        users=["test-only-secret"],
        features=["customers：category必须可搜索 test-only-secret"],
        acceptance=[],
        data_scope="shared",
        facts={"customers": {"category": {"choices": ["test-only-secret"]}}},
    )
    result = safe_coverage_details(requirement.model_dump(), plan.model_dump())
    assert any(item["source"]["section"] == "features" for item in result)
    assert any(
        item["source"]["encoding"] == "structured"
        for item in result
        if item["source"]["section"] == "facts"
    )
    assert any(item["targets"] == [{"entity": "customers", "field": "category"}] for item in result)
    assert any(item.get("expected_count") == 1 for item in result)
    assert "test-only-secret" not in json.dumps(result)


def test_native_label_failure_is_exact_finite_code_with_no_description_export():
    from scripts.ci_real_model import safe_native_plan_details

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["entities"][0]["description"] = "客户管理，test-only-secret"
    result = safe_native_plan_details(plan)
    assert result["code"] == "native_label_contract"
    assert result["entity_labels"][0]["allowed_characters"] is False
    assert result["entity_labels"][0]["single_line"] is True
    assert "test-only-secret" not in json.dumps(result)


def test_every_native_plan_validation_message_has_a_finite_safe_code():
    import ast
    import inspect

    from scripts.ci_real_model import DESIGN_REASON_CODES
    from workbench.native_delivery import runtime_config
    from workbench.native_modules import validate_plan

    for function in (validate_plan, runtime_config):
        tree = ast.parse(inspect.getsource(function))
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                assert isinstance(node.exc.args[0], ast.Constant)
                assert node.exc.args[0].value in DESIGN_REASON_CODES


def test_workflow_diagnostics_separate_model_coverage_and_native_origins():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_workflow_details
    from workbench.domain import Plan, Requirement
    from workbench.requirement_coverage import coverage_gaps

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    plan["unsupported"] = ["模板日期范围能力不支持 test-only-secret"]
    requirement = Requirement(
        summary="test-only-secret",
        users=["客服"],
        data_scope="shared",
        features=["customers：category可搜索 test-only-secret"],
        acceptance=[],
    )
    coverage = coverage_gaps(requirement, Plan.model_validate(plan))

    class Store:
        def get_run(self, run_id):
            return {
                "status": "BLOCKED",
                "template": "python-basic",
                "model_calls": 4,
                "pending": {
                    "stage": "design",
                    "data": {
                        "blocked": [*plan["unsupported"], *coverage],
                        "block_sources": [
                            "planner_unsupported",
                            *["requirement_coverage"] * len(coverage),
                        ],
                    },
                },
            }

        def latest_revision(self, run_id, stage):
            return (
                {"requirement": requirement.model_dump()}
                if stage == "requirements"
                else {"plan": plan}
            )

    result = safe_workflow_details(
        Store(), "run", [], text_budget=DiagnosticTextBudget(secrets=("test-only-secret",))
    )
    assert result["coverage_diagnostics"][0]["codes"] == ["planner_unsupported"]
    assert result["coverage_diagnostics"][0]["origin"] == "planner_unsupported"
    assert result["coverage_diagnostics"][1]["origin"] == "requirement_coverage"
    assert result["unsupported_diagnostics"][0]["topics"] == ["date_range", "capability"]
    assert "test-only-secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "value,secret",
    [
        ("API_KEY=credential_canary", "credential_canary"),
        ('{"password": "password_canary"}', "password_canary"),
        ("诊断：密码：password_canary", "password_canary"),
        ("request failed Authorization: Bearer header_canary", "header_canary"),
        ('metadata "Cookie": "session=cookie_canary"', "cookie_canary"),
        ("postgresql+psycopg://alice:url_canary@127.0.0.1/private", "url_canary"),
        ("https://example.invalid/?access_token=query_canary", "query_canary"),
        ("Bearer bearer_canary", "bearer_canary"),
        ("sk-testcredentialcanary123", "sk-testcredentialcanary123"),
        ("github_pat_credentialcanary123", "github_pat_credentialcanary123"),
        ("eyJhbGciOiJIUzI1NiJ9.credentialcanary.signature", "credentialcanary"),
    ],
)
def test_validation_excerpt_scrubs_credentials_headers_tokens_and_url_userinfo(value, secret):
    from scripts.ci_real_model import DiagnosticTextBudget

    result = DiagnosticTextBudget().excerpt(value)
    assert secret not in result
    assert "REDACTED" in result


def test_exact_key_redaction_precedes_truncation_and_total_budget_is_shared():
    from scripts.ci_real_model import DiagnosticTextBudget

    secret = "exact-key-canary-private"
    budget = DiagnosticTextBudget(secrets=(secret,))
    first = budget.excerpt("x" * 595 + secret)
    assert "exact" not in first and len(first) <= 600
    rest = budget.excerpts(["y" * 1000] * 20)
    assert len(first) + sum(map(len, rest)) == 6000
    assert all(len(item) <= 600 for item in rest)
    assert budget.excerpt("more") == ""


def test_safe_coverage_excerpt_is_selected_and_redacted_without_full_requirement():
    from scripts.ci_real_model import DiagnosticTextBudget, safe_coverage_details
    from workbench.domain import Requirement

    plan = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    requirement = Requirement(
        summary="private summary not selected",
        users=["not selected"],
        data_scope="shared",
        features=["customers：name 必须支持精确筛选，opaque-private-canary"],
        acceptance=["unrelated unselected wording"],
    )
    result = safe_coverage_details(
        requirement.model_dump(),
        plan,
        text_budget=DiagnosticTextBudget(secrets=("opaque-private-canary",)),
    )
    rendered = json.dumps(result, ensure_ascii=False)
    assert "必须支持精确筛选" in rendered
    assert "opaque-private-canary" not in rendered
    assert "private summary" not in rendered and "unrelated unselected" not in rendered


def test_review_gap_diagnostics_preserve_blocking_count_and_omit_other_model_text():
    from scripts.ci_real_model import DiagnosticTextBudget, completed_stage_details
    from workbench.domain import ModelReview

    review = ModelReview(
        summary="raw private provider summary",
        observations=["raw private provider observation"],
        uncovered_requirements=["客户历史请求未验证，opaque-private-canary"],
    )
    result = completed_stage_details(
        review, DiagnosticTextBudget(secrets=("opaque-private-canary",))
    )
    assert result["uncovered_requirements_count"] == 1
    assert "客户历史请求未验证" in result["uncovered_requirement_excerpts"][0]
    encoded = json.dumps(result, ensure_ascii=False)
    assert "opaque-private-canary" not in encoded and "raw private provider" not in encoded
    assert review.uncovered_requirements == ["客户历史请求未验证，opaque-private-canary"]


````
