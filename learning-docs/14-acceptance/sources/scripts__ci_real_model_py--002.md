# scripts/ci_real_model.py · 2/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__ci_real_model_py--001.md) · [下一段](scripts__ci_real_model_py--003.md)

**作用：显式授权的真实模型完整验收。** 可信客服分支的手动任务在rnd中将APK_KEY映射为API_KEY，三个模板各自先Hello再校验同提交同attempt回执。完整需求由原文、默认决策和命名约定构成；真实网页只一次初始智能推荐，随后必须READY、实际下载、新库HTTP/浏览器/重启；公开白名单状态及经过校验的合成页面截图，不输出密钥或模型原文。

**对应关系：** native-probe手动real_model=true+expected_sha，或real-model手动矩阵 → rnd job → ModelGateway真实请求 → 当前模板独立产品 → summary.json与合成PNG；工具矩阵和BLOCKED恢复另验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `preserve_unapproved_design_contract`（L821–L902）：接收`store`、`run_id`、`destination`、`text_budget`、`acceptance_failed`。 源码说明：Failure-only diagnostic contract; this envelope carries no execution approval. Only normalized Requirement/Plan revisions from this synthetic customer run are selected. No provider response, runtime e。 控制顺序：L834按`any(path.is_symlink() for path in (destination, *destination.parents))`分支；L836按`not isinstance(run_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", run_id)`分支；L840按`run.get("status") not in {"FAILED", "BLOCKED"} and not ( acceptance_failed is True an…`分支；L844按`run.get("template") not in {"python-basic", "fastapiadmin", "yudao-vben"}`分支；L848按`not requirement or not plan`分支；L851按`len(json.dumps(selected, ensure_ascii=False).encode("utf-8")) > MAX_REPLAY_PLAN_BYTES`分支；L855按`{entity.name for entity in plan.entities} != {"customers", "requests", "tasks"} or no…`分支；L882按`not credential_free(payload)`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`any`、`path.is_symlink`、`isinstance`、`re.fullmatch`、`store.get_run`、`run.get`、`(store.latest_revision(run_id, "requirements") or {}).get`、`store.latest_revision`等。 返回路径：L835的`{"status": "unsafe_path"}`；L837的`{"status": "unavailable"}`；L843的`{"status": "not_failure"}`。
- `preserve_unapproved_design_contract.credential_free`（L871–L880）：接收`value`。 控制顺序：L872按`isinstance(value, str)`分支；L874按`isinstance(value, list)`分支；L876按`isinstance(value, dict)`分支。 调用`isinstance`、`text_budget.scrub`、`all`、`credential_free`、`value.items`。 返回路径：L873的`text_budget.scrub(value) == value`；L875的`all(credential_free(item) for item in value)`；L877的`all( credential_free(key) and credential_free(item) for key, item in value.items() )`。
- `safe_workflow_details`（L905–L1075）：接收`store`、`run_id`、`traces`、`text_budget`、`native_reports`。 控制顺序：L908按`run_id`分支；L929按`conflicts`分支；L953按`requirement and plan`分支；L963按`run.get("template") in {"fastapiadmin", "yudao-vben"}`分支。 调用`DiagnosticTextBudget`、`store.get_run`、`run.get`、`safe_runtime_details`、`pending.get`、`safe_analysis_conflict_details`、`(pending.get("data") or {}).get`、`(store.latest_revision(run_id, "requirements") or {}).get`、`store.latest_revision`等。 返回路径：L1075的`details`。
- `smoke`（L1078–L1106）：接收`config`、`transport`。 源码说明：A single bounded genuine request. Provider error bodies are never emitted.。 控制顺序：L1091按`status != 200`分支；L1093抛异常，停止当前正常路径；L1095遍历`response.iter_bytes()`；L1097按`len(data) > 131072`分支；L1098抛异常，停止当前正常路径；L1100按`not isinstance(content, str) or not content.strip()`分支；L1101抛异常，停止当前正常路径；L1103抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`httpx.Client`、`client.stream`、`config.key.get_secret_value`、`SafeFailure`、`bytearray`、`response.iter_bytes`、`data.extend`、`len`、`json.loads`等。 返回路径：L1106的`{"passed": True, "http_status": status, "actual_provider_request": True}`。
- `customer_request`（L1147–L1157）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`"\n\n".join`、`(ROOT / "examples/requirements" / name).read_text`。 返回路径：L1150的`"\n\n".join( (ROOT / "examples/requirements" / name).read_text(encoding="utf-8") for name …`。
- `require_customer_spec`（L1210–L1456）：接收`spec`、`approved_requirement`。 控制顺序：L1216断言`plan.business is not None and plan.data_scope == "shared" and not plan.unsupported`；L1219断言`{e.name for e in plan.entities} == {"customers", "requests", "tasks"}`；L1222断言`{r.name for r in plan.business.roles} == {"manager", "service", "employee"}`；L1232断言`not business_gaps(requirement, plan)`；L1233按`approved_requirement is not None`分支；L1235断言`not business_gaps(approved, plan)`；L1250断言`any( metric.entity == "requests" and metric.kind == "count" and not metric.filters fo…`；L1254断言`any( metric.entity == "requests" and metric.kind == "count" and resolved_only(metric)…`。后续分支沿下方源码相同行号继续阅读。 调用`Plan.model_validate`、`Requirement`、`customer_request`、`business_gaps`、`Requirement.model_validate`、`any`、`resolved_only`、`all`、`set`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_customer_spec.resolved_only`（L1239–L1247）：接收`metric`。 调用`bool`、`all`。 返回路径：L1240的`bool(metric.filters) and all( rule.field == "request_state" and ( (rule.op == "eq" and rul…`。
- `acceptance_settings`（L1459–L1497）：接收`config`、`directory`。 调用`Settings`。 返回路径：L1462的`Settings( data_dir=directory / "private-platform", database_url="", checkpoint_url="", bas…`。
- `run_acceptance`（L1500–L1757）：接收`config`、`transport`、`directory`、`template`。 控制顺序：L1514按`template != "python-basic"`分支；L1610遍历`range(150)`；L1611按`server.started`分支；L1615抛异常，停止当前正常路径；L1645按`process.returncode or not result_path.is_file()`分支；L1648按`result_path.is_file()`分支；L1651抛异常，停止当前正常路径；L1656按`run["status"] != "READY" or not run["auto_mode"] or not archive.is_file()`分支。后续分支沿下方源码相同行号继续阅读。 调用`acceptance_settings`、`Selection`、`settings.prepare`、`write_json`、`runtime_path`、`DiagnosticTextBudget`、`config.key.get_secret_value`、`create_app`、`ObservedGateway`等。 返回路径：L1719的`{ "passed": True, "real_model": True, "single_initial_smart_consent": True, "explicit_cust…`。
- `run_acceptance.ObservedGateway`（L1528–L1541）：继承`ModelGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `run_acceptance.ObservedGateway.complete`（L1529–L1541）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 调用`key.split`、`traces.append`、`super().complete`、`super`、`trace.update`、`completed_stage_details`。 返回路径：L1541的`value`。

</details>

**创建路径：** `scripts/ci_real_model.py`；**本文件共有 3 段**。本段覆盖源文件 L821–L1559。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`31665`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_real_model.py", "part": 2, "parts": 3, "encoding": "utf-8", "sha256": "eed6ce9de188a85b152da2f7f1b3bd75759bbdaec05ae51a0f317350d22376be"} -->
````python
# scripts/ci_real_model.py
def preserve_unapproved_design_contract(
    store, run_id, destination, text_budget, *, acceptance_failed=False
):
    """Failure-only diagnostic contract; this envelope carries no execution approval.

    Only normalized Requirement/Plan revisions from this synthetic customer run
    are selected. No provider response, runtime environment, database or log is
    read. The envelope is deliberately not a valid Plan/generation input.
    """
    from workbench.domain import Plan, Requirement
    from workbench.filesystem import atomic_text

    destination = Path(destination)
    if any(path.is_symlink() for path in (destination, *destination.parents)):
        return {"status": "unsafe_path"}
    if not isinstance(run_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", run_id):
        return {"status": "unavailable"}
    try:
        run = store.get_run(run_id)
        if run.get("status") not in {"FAILED", "BLOCKED"} and not (
            acceptance_failed is True and run.get("status") in {"READY", "SOURCE_READY"}
        ):
            return {"status": "not_failure"}
        if run.get("template") not in {"python-basic", "fastapiadmin", "yudao-vben"}:
            return {"status": "outside_customer_scope"}
        requirement = (store.latest_revision(run_id, "requirements") or {}).get("requirement")
        plan = (store.latest_revision(run_id, "design") or {}).get("plan")
        if not requirement or not plan:
            return {"status": "unavailable"}
        selected = {"requirement": requirement, "candidate_plan": plan}
        if len(json.dumps(selected, ensure_ascii=False).encode("utf-8")) > MAX_REPLAY_PLAN_BYTES:
            return {"status": "size_limit"}
        requirement = Requirement.model_validate(requirement)
        plan = Plan.model_validate(plan)
        if (
            {entity.name for entity in plan.entities} != {"customers", "requests", "tasks"}
            or not plan.business
            or plan.custom_rules
        ):
            return {"status": "outside_customer_scope"}
        payload = {
            "format": "customer-design-diagnostic-v1",
            "approval_status": "unapproved",
            "execution_authorized": False,
            "purpose": "offline_contract_validation_only",
            "template": run["template"],
            "requirement": requirement.model_dump(mode="json"),
            "candidate_plan": plan.model_dump(mode="json"),
        }

        def credential_free(value):
            if isinstance(value, str):
                return text_budget.scrub(value) == value
            if isinstance(value, list):
                return all(credential_free(item) for item in value)
            if isinstance(value, dict):
                return all(
                    credential_free(key) and credential_free(item) for key, item in value.items()
                )
            return True

        if not credential_free(payload):
            return {"status": "secret_scan_rejected"}
        rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if text_budget.scrub(rendered) != rendered:
            return {"status": "secret_scan_rejected"}
        data = rendered.encode("utf-8")
        if len(data) > MAX_REPLAY_PLAN_BYTES:
            return {"status": "size_limit"}
        atomic_text(destination, rendered)
        return {
            "status": "saved",
            "file": "unapproved-design-contract.json",
            "approval_status": "unapproved",
            "execution_authorized": False,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    except ValueError, TypeError:
        return {"status": "invalid_schema"}
    except OSError:
        return {"status": "io_error"}


def safe_workflow_details(store, run_id, traces, *, text_budget=None, native_reports=None):
    text_budget = text_budget or DiagnosticTextBudget()
    details = {"model_stages": traces}
    if run_id:
        run = store.get_run(run_id)
        state = run.get("status")
        details["terminal_state"] = (
            state
            if state in {"READY", "SOURCE_READY", "FAILED", "BLOCKED", "PAUSED_LIMIT", "REJECTED"}
            else "not_terminal"
        )
        # Reserve the shared text budget for the actual runtime failure before
        # lower-priority coverage/model wording can exhaust it.
        details["runtime_diagnostics"] = safe_runtime_details(
            run.get("error") or "", native_reports, text_budget
        )
        pending = run.get("pending") or {}
        stage = pending.get("stage")
        details["pending_stage"] = (
            stage if stage in {"clarification", "requirements", "design", "delivery"} else None
        )
        conflicts = safe_analysis_conflict_details(
            (pending.get("data") or {}).get("analysis_diagnostics"), text_budget
        )
        if conflicts:
            details["analysis_source_conflicts"] = conflicts
        details["model_calls"] = run.get("model_calls", 0)
        requirement = (store.latest_revision(run_id, "requirements") or {}).get("requirement", {})
        plan = (store.latest_revision(run_id, "design") or {}).get("plan", {})
        details["valid_plan_present"] = bool(plan)
        business = plan.get("business") or {}
        details["business_contract_present"] = bool(business)
        details["business_counts"] = {
            key: len(business.get(key, []))
            for key in (
                "roles",
                "resources",
                "relations",
                "permissions",
                "workflows",
                "notifications",
                "metrics",
            )
            if isinstance(business.get(key, []), list)
        }
        details["plan_contract"] = contract_snapshot(plan)
        details["requirement_contract"] = contract_snapshot(requirement, requirement=True)
        details["unsupported_excerpts"] = text_budget.excerpts(plan.get("unsupported", []))
        if requirement and plan:
            from workbench.domain import Plan, Requirement
            from workbench.requirement_coverage import coverage_gaps

            details["coverage_reason_excerpts"] = text_budget.excerpts(
                coverage_gaps(Requirement.model_validate(requirement), Plan.model_validate(plan))
            )
            details["coverage_sources"] = safe_coverage_details(
                requirement, plan, text_budget=text_budget
            )
            if run.get("template") in {"fastapiadmin", "yudao-vben"}:
                details["native_plan_validation"] = safe_native_plan_details(plan)
        error = run.get("error") or ""
        categories = {
            "requirement_source_conflict": ("需求分析来源冲突",),
            "model_schema_invalid": ("结构化契约",),
            "context_limit": ("上下文过大",),
            "provider_error": ("模型鉴权", "模型地址", "模型请求被拒绝", "模型服务超时"),
            "requirement_coverage": ("设计未覆盖", "已确认字段", "已确认条件", "覆盖不足"),
            "tool_failure": ("工具执行失败",),
            "browser_acceptance": ("浏览器", "browser"),
            "model_budget": ("调用次数", "模型调用预算"),
        }
        details["error_categories"] = [
            code for code, tokens in categories.items() if any(t in error for t in tokens)
        ]
        blocked = (pending.get("data") or {}).get("blocked", [])
        details["coverage_block_count"] = len(blocked) if isinstance(blocked, list) else 0
        diagnostic_kinds = {
            "missing_or_ambiguous": "缺失或映射不唯一",
            "legacy_missing_field": "缺少对应字段",
            "required": "必填",
            "optional": "可选",
            "max_length": "长度上限",
            "min_length": "最小长度",
            "date_kind": "真实日期类型",
            "uncovered_operation": "设计未覆盖已确认的",
            "constraint_mismatch": "设计不一致",
            "missing_metric_predicate": "业务指标缺少已确认的筛选条件",
            "business_capability": "业务设计缺少",
        }
        attributes = (
            "kind",
            "required",
            "searchable",
            "filterable",
            "date_range",
            "min_length",
            "max_length",
            "choices",
        )
        known_names = {
            field["name"] for entity in details["plan_contract"] for field in entity["fields"]
        }
        sources = (pending.get("data") or {}).get("block_sources", [])
        known_sources = {
            "planner_unsupported",
            "template_field_kind",
            "requirement_coverage",
            "business_coverage",
            "business_contract",
            "coding_disabled",
            "native_coding_engine",
            "native_validation_or_runtime",
            "sandbox_configuration",
        }
        details["coverage_diagnostics"] = [
            {
                "codes": (
                    [DESIGN_REASON_CODES[reason]]
                    if reason in DESIGN_REASON_CODES
                    else [code for code, marker in diagnostic_kinds.items() if marker in reason]
                    or (
                        ["planner_unsupported"]
                        if reason in plan.get("unsupported", [])
                        else ["unclassified_design_block"]
                    )
                ),
                "origin": sources[index]
                if index < len(sources) and sources[index] in known_sources
                else "not_recorded",
                "attributes": [attribute for attribute in attributes if attribute in reason],
                "fields": sorted(
                    name
                    for name in known_names
                    if name != "unrecognized"
                    and re.search(r"(?<![a-z0-9_])" + re.escape(name) + r"(?![a-z0-9_])", reason)
                ),
            }
            for index, reason in enumerate((blocked if isinstance(blocked, list) else [])[:40])
            if isinstance(reason, str)
        ]
        details["unsupported_diagnostics"] = [
            {
                "index": index,
                "topics": [
                    code
                    for code, pattern in (
                        ("search", r"搜索|检索|search"),
                        ("filter", r"筛选|过滤|filter"),
                        ("date_range", r"日期范围|日期区间|date.?range"),
                        ("capability", r"模板|能力|capabilit"),
                        ("external_service", r"外部|短信|邮件|支付|采集|external"),
                        ("business", r"角色|关系|流程|统计|business"),
                    )
                    if re.search(pattern, reason, re.I)
                ],
            }
            for index, reason in enumerate(plan.get("unsupported", [])[:40])
            if isinstance(reason, str)
        ]
        paths = {f["name"] for e in details["plan_contract"] for f in e["fields"]}
        details["coverage_fields"] = (
            sorted(
                name
                for name in paths
                if name != "unrecognized"
                and any(name in reason for reason in blocked if isinstance(reason, str))
            )
            if isinstance(blocked, list)
            else []
        )
    return details


def smoke(config, transport):
    """A single bounded genuine request. Provider error bodies are never emitted."""
    try:
        with httpx.Client(
            transport=transport, timeout=120, follow_redirects=False, trust_env=False
        ) as client:
            with client.stream(
                "POST",
                config.base_url + "/chat/completions",
                headers={"Authorization": "Bearer " + config.key.get_secret_value()},
                json=SMOKE_PAYLOAD,
            ) as response:
                status = response.status_code
                if status != 200:
                    code = "model_unavailable" if status == 404 else "provider_rejected"
                    raise SafeFailure(code, status)
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > 131072:
                        raise SafeFailure("smoke_response_too_large", status)
        content = json.loads(data)["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise SafeFailure("invalid_smoke_response", status)
    except httpx.HTTPError:
        raise SafeFailure("provider_transport_failure") from None
    except ValueError, KeyError, IndexError, TypeError:
        raise SafeFailure("invalid_smoke_response") from None
    return {"passed": True, "http_status": status, "actual_provider_request": True}


BROWSER_DRIVER = r"""
const fs = require('node:fs');
const [file, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(file, 'utf8'));
async function main() {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  const errors=[];
  page.on('pageerror', () => errors.push('page_error'));
  try {
    await page.goto(cfg.platform);
    await page.locator('#token').fill(cfg.token);
    await page.locator('#connect button').click();
    await page.locator('#template').selectOption(cfg.template);
    await page.locator('#frontend').selectOption(cfg.frontend);
    await page.locator('#database').selectOption(cfg.database);
    await page.locator('#choose').click();
    await page.locator('#project-title').fill('真实 DeepSeek 客服完整验收');
    await page.locator('#requirement').fill(cfg.requirement);
    // Exactly one initial delegation, no subsequent approval or retry clicks.
    await page.locator('#initial-smart').check();
    await page.locator('#new-run button').click();
    await page.waitForFunction(() => ['READY','SOURCE_READY','FAILED','BLOCKED','PAUSED_LIMIT','REJECTED']
      .some(s=>document.querySelector('#status').textContent === '状态：'+s), null, {timeout:6900000});
    const state=(await page.locator('#status').innerText()).replace('状态：','');
    const runId=(await page.locator('#run-title').innerText()).split(' ').at(-1);
    fs.writeFileSync(cfg.result, JSON.stringify({state,run_id:runId,page_errors:errors.length}));
    if(state!=='READY' || errors.length) throw new Error('workflow_not_ready');
    const download=page.waitForEvent('download');
    await page.locator('#download').click();
    await (await download).saveAs(cfg.download);
  } finally { await browser.close(); }
}
main().catch(()=> { console.error('real-model browser acceptance did not complete'); process.exitCode=1; });
"""


def customer_request():
    from workbench.settings import ROOT

    return "\n\n".join(
        (ROOT / "examples/requirements" / name).read_text(encoding="utf-8")
        for name in (
            "customer-service.md",
            "customer-service-decisions.md",
            "customer-service-contract.md",
        )
    )


CUSTOMER_GUARD_CODES = frozenset(
    [
        "approved_business_obligations",
        "assignee_field",
        "bootstrap_role",
        "canonical_business_obligations",
        "customer_categories",
        "customer_forbidden_actions",
        "customer_read_scope",
        "declarative_rules_only",
        "employee_forbidden_actions",
        "employee_no_metrics",
        "employee_request_access",
        "employee_scope",
        "entities_exact",
        "field_labels",
        "fields_exact",
        "immutable_audit",
        "initial_state",
        "manager_scope",
        "metric_customer_groups",
        "metric_daily_trend",
        "metric_duration",
        "metric_resolved",
        "metric_total",
        "metrics_permissions",
        "notes_archive",
        "notification_creator_resolution",
        "notification_event",
        "registration",
        "relations",
        "request_priorities",
        "required_actions",
        "resolve_transition",
        "resolved_timestamp",
        "role_administration",
        "roles_exact",
        "service_scope",
        "shared_business_supported",
        "start_transition",
        "state_choice_labels",
        "state_labels_readable",
        "status_field",
        "task_creation_assignment",
        "transition_labels",
        "transition_roles",
    ]
)


def require_customer_spec(spec, *, approved_requirement=None):
    from workbench.business_capabilities import business_gaps
    from workbench.domain import Plan, Requirement

    try:
        plan = Plan.model_validate(spec)
        assert plan.business is not None and plan.data_scope == "shared" and not plan.unsupported, (
            "shared_business_supported"
        )
        assert {e.name for e in plan.entities} == {"customers", "requests", "tasks"}, (
            "entities_exact"
        )
        assert {r.name for r in plan.business.roles} == {"manager", "service", "employee"}, (
            "roles_exact"
        )
        requirement = Requirement(
            summary=customer_request(),
            users=["管理人员", "服务人员", "普通员工"],
            features=[],
            acceptance=[],
            data_scope="shared",
        )
        assert not business_gaps(requirement, plan), "canonical_business_obligations"
        if approved_requirement is not None:
            approved = Requirement.model_validate(approved_requirement)
            assert not business_gaps(approved, plan), "approved_business_obligations"

        # Match the public metric meanings, never provider-selected names/labels.
        # Extra supported metrics remain valid, but cannot substitute for these five.
        def resolved_only(metric):
            return bool(metric.filters) and all(
                rule.field == "request_state"
                and (
                    (rule.op == "eq" and rule.value == "resolved")
                    or (rule.op == "in" and rule.value == ["resolved"])
                )
                for rule in metric.filters
            )

        metrics = plan.business.metrics
        assert any(
            metric.entity == "requests" and metric.kind == "count" and not metric.filters
            for metric in metrics
        ), "metric_total"
        assert any(
            metric.entity == "requests" and metric.kind == "count" and resolved_only(metric)
            for metric in metrics
        ), "metric_resolved"
        assert any(
            metric.entity == "requests"
            and metric.kind == "average_duration"
            and metric.start_field == "created_at"
            and metric.end_field == "resolved_at"
            and (not metric.filters or resolved_only(metric))
            for metric in metrics
        ), "metric_duration"
        assert any(
            metric.entity == "customers"
            and metric.kind == "group_count"
            and metric.group_by == "category"
            and not metric.filters
            for metric in metrics
        ), "metric_customer_groups"
        assert any(
            metric.entity == "requests"
            and metric.kind == "time_count"
            and metric.time_field == "created_at"
            and not metric.filters
            for metric in metrics
        ), "metric_daily_trend"
        notices = plan.business.notifications
        for entity in ("requests", "tasks"):
            for event, transition, due_field in (
                ("assigned", None, None),
                ("note_added", None, None),
                ("transitioned", "start", None),
                ("transitioned", "resolve", None),
                ("due", None, "due_at"),
            ):
                assert any(
                    notice.entity == entity
                    and notice.event == event
                    and notice.transition == transition
                    and notice.due_field == due_field
                    for notice in notices
                ), "notification_event"
        assert any(
            notice.entity == "requests"
            and notice.event == "transitioned"
            and notice.transition == "resolve"
            and notice.recipient == "creator"
            for notice in notices
        ), "notification_creator_resolution"
        assert not plan.custom_rules, "declarative_rules_only"
        entities = {
            entity.name: {field.name: field for field in entity.fields} for entity in plan.entities
        }
        expected = {
            "customers": {"name", "organization", "contact", "category"},
            "requests": {
                "title",
                "detail",
                "customer_id",
                "assignee_id",
                "request_state",
                "resolved_at",
                "due_at",
                "priority",
            },
            "tasks": {
                "title",
                "detail",
                "request_id",
                "assignee_id",
                "task_state",
                "resolved_at",
                "due_at",
            },
        }
        assert all(set(entities[name]) == fields for name, fields in expected.items()), (
            "fields_exact"
        )
        assert all(field.label for fields in entities.values() for field in fields.values()), (
            "field_labels"
        )
        for entity, field_name in (("requests", "request_state"), ("tasks", "task_state")):
            field = entities[entity][field_name]
            assert set(field.choice_labels) == set(field.choices), "state_choice_labels"
            assert all(field.choice_labels[value] != value for value in field.choices), (
                "state_labels_readable"
            )
        assert set(entities["customers"]["category"].choices) == {"企业", "个人", "合作伙伴"}, (
            "customer_categories"
        )
        assert set(entities["requests"]["priority"].choices) == {"普通", "紧急"}, (
            "request_priorities"
        )
        relations = {(r.entity, r.field, r.target_entity) for r in plan.business.relations}
        assert {
            ("requests", "customer_id", "customers"),
            ("tasks", "request_id", "requests"),
            ("requests", "assignee_id", "$users"),
            ("tasks", "assignee_id", "$users"),
        } <= relations, "relations"
        assert plan.business.bootstrap_role == "manager", "bootstrap_role"
        assert set(plan.business.role_admin_roles) == {"manager"}, "role_administration"
        assert (
            plan.business.registration.enabled
            and plan.business.registration.default_role == "employee"
        ), "registration"
        policies = {(p.role, p.entity): p for p in plan.business.permissions}
        # Minimum capabilities explicitly promised for this customer case.
        # Keep optional actions separate from these obligations; query access alone
        # must neither imply a grant nor excuse a missing processing action.
        customer_manager_actions = {"create", "read", "update", "archive", "read_audit"}
        processing_actions = {
            "read",
            "update",
            "add_note",
            "transition",
            "read_history",
            "read_audit",
        }
        manager_processing_actions = processing_actions | {"create", "archive", "assign"}
        required_actions = {
            ("manager", "customers"): customer_manager_actions,
            ("manager", "requests"): manager_processing_actions,
            ("manager", "tasks"): manager_processing_actions,
            ("service", "requests"): processing_actions,
            ("service", "tasks"): processing_actions,
            ("employee", "requests"): {"create", "read"},
        }
        for identity, actions in required_actions.items():
            assert actions <= set(policies[identity].actions), "required_actions"
        assert all(policies[("manager", entity)].scope == "all" for entity in expected), (
            "manager_scope"
        )
        assert all(
            not {"create", "assign"} & set(policy.actions)
            for policy in plan.business.permissions
            if policy.entity == "tasks" and policy.role != "manager"
        ), "task_creation_assignment"
        for role in ("manager", "service"):
            for entity in ("customers", "requests"):
                assert {"read", "read_metrics"} <= set(policies[(role, entity)].actions), (
                    "metrics_permissions"
                )
        for role in ("service", "employee"):
            customer_policy = policies[(role, "customers")]
            assert customer_policy.scope == "all" and "read" in customer_policy.actions, (
                "customer_read_scope"
            )
            assert not {"create", "update", "archive", "add_note", "read_audit"} & set(
                customer_policy.actions
            ), "customer_forbidden_actions"
        resources = {resource.entity: resource for resource in plan.business.resources}
        assert all(resources[entity].audit for entity in ("customers", "requests", "tasks")), (
            "immutable_audit"
        )
        for entity in ("requests", "tasks"):
            assert resources[entity].notes and resources[entity].archive, "notes_archive"
            assert resources[entity].assignee_field == "assignee_id", "assignee_field"
            if ("employee", entity) in policies:
                assert policies[("employee", entity)].scope in (
                    {"own"} if entity == "requests" else {"own", "assigned"}
                ), "employee_scope"
                forbidden = {"assign", "transition", "read_metrics"}
                if entity == "tasks":
                    forbidden |= {"create", "update", "archive", "add_note"}
                assert not forbidden & set(policies[("employee", entity)].actions), (
                    "employee_forbidden_actions"
                )
            else:
                assert entity == "tasks", "employee_request_access"
            assert policies[("service", entity)].scope == "assigned", "service_scope"
            workflow = next(w for w in plan.business.workflows if w.entity == entity)
            transitions = {t.name: t for t in workflow.transitions}
            assert all(transition.label for transition in workflow.transitions), "transition_labels"
            assert workflow.initial == "new", "initial_state"
            assert (
                workflow.status_field
                == {"requests": "request_state", "tasks": "task_state"}[entity]
            ), "status_field"
            assert all(
                set(transition.roles) == {"manager", "service"}
                for transition in transitions.values()
            ), "transition_roles"
            assert (
                transitions["start"].from_states == ["new"]
                and transitions["start"].to_state == "active"
            ), "start_transition"
            assert (
                transitions["resolve"].from_states == ["active"]
                and transitions["resolve"].to_state == "resolved"
            ), "resolve_transition"
            assert transitions["resolve"].set_timestamp == "resolved_at", "resolved_timestamp"
        assert all(
            "read_metrics" not in policy.actions
            for policy in plan.business.permissions
            if policy.role == "employee"
        ), "employee_no_metrics"
    except (ValueError, KeyError, TypeError, AssertionError, StopIteration) as error:
        failure = SafeFailure("explicit_customer_obligation_not_preserved")
        # Assertion messages are fixed local identifiers, never model wording.
        code = error.args[0] if isinstance(error, AssertionError) and error.args else None
        failure.guard_code = code if code in CUSTOMER_GUARD_CODES else "schema_or_missing_contract"
        raise failure from None


def acceptance_settings(config, directory):
    from workbench.settings import STAGES, Settings

    return Settings(
        data_dir=directory / "private-platform",
        database_url="",
        checkpoint_url="",
        base_url=config.base_url,
        api_key=config.key,
        MODE=config.model,
        provider="deepseek",
        output_mode="json_object",
        max_output_tokens=MAX_COMPLETION_TOKENS,
        **{
            stage + suffix: value
            for stage in STAGES
            for suffix, value in (
                ("_base_url", config.base_url),
                ("_api_key", config.key),
                ("_model", config.model),
                ("_provider", "deepseek"),
                ("_output_mode", "json_object"),
                ("_max_output_tokens", MAX_COMPLETION_TOKENS),
            )
        },
        install_products=True,
        tool_timeout=600,
        model_review=True,
        llm_timeout=180,
        max_model_calls=MAX_WORKFLOW_CALLS,
        max_rounds=5,
        max_repair_attempts=1,
        coding_engine="bounded",
        repo_map_provider="symbols",
        retrieval_engine="local",
        embedding_enabled=False,
        sandbox_provider="local",
        _env_file=None,
    )


def run_acceptance(config, transport, directory, template="python-basic"):
    import uvicorn

    from workbench.api import create_app
    from workbench.filesystem import unpack, write_json
    from workbench.llm import ModelGateway
    from workbench.settings import ROOT
    from workbench.tools import clean_env
    from workbench.verification import product_interpreter, require_browser_evidence, run_probe

    settings = acceptance_settings(config, directory)
    from workbench.catalog import Selection

    selection = Selection(template=template)
    if template != "python-basic":
        from workbench.native_delivery import runtime_path

        settings.prepare()
        write_json(
            runtime_path(settings, template),
            {
                "database_url_env": "NATIVE_TEST_DATABASE_URL",
                "initialize_empty_database": True,
            },
        )
    traces = []
    diagnostic_text = DiagnosticTextBudget(secrets=(config.key.get_secret_value(),))

    class ObservedGateway(ModelGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            stage = key.split(":")[0]
            stage = (
                stage
                if stage in {"requirement", "recommend", "plan", "coding", "review"}
                else "unknown"
            )
            transport.current_schema, transport.current_stage = schema, stage
            trace = {"stage": stage, "completed": False}
            traces.append(trace)
            value = super().complete(run_id, key, instruction, payload, schema)
            trace.update(completed_stage_details(value, diagnostic_text))
            return value

    application = create_app(
        settings, gateway_factory=lambda store: ObservedGateway(settings, store, transport)
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            application, host="127.0.0.1", port=port, log_level="critical", access_log=False
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    run_id = None
    result_path = directory / "browser-result.json"
    acceptance_stage = "platform_start"

````
