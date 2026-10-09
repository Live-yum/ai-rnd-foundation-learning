# tests/test_business_browser_evidence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.tools`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `customer_plan`（L24–L34）：接收`with_employee_history`。 控制顺序：L26按`not with_employee_history`分支；L27遍历`data["business"]["permissions"]`；L28按`permission["role"] == "employee"`分支。 调用`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Plan.model_validate`。 返回路径：L34的`Plan.model_validate(data)`。
- `run_browser_gate`（L37–L94）：接收`tmp_path`、`plan`、`fault`。 控制顺序：L39按`not module or not Path(module).is_dir()`分支；L47按`fault`分支；L73断言`before in source`；L93断言`report.is_file()`。 调用`os.getenv`、`Path(module).is_dir`、`Path`、`pytest.skip`、`generate_basic`、`app.read_text`、`app.write_text`、`source.replace`、`clean_env`等。 返回路径：L94的`result, json.loads(report.read_text(encoding="utf-8"))`。
- `assert_bounded_evidence`（L97–L178）：接收`plan`、`report`。 控制顺序：L99断言`browser["passed"] is True and browser["real_browser"] is True`；L101断言`set(evidence) == { "version", "relation_labels", "related_views", "related_sources", …`；L109断言`evidence["version"] == 1`；L114断言`len(evidence["relation_labels"]) <= len(roles) * len(relations)`；L115断言`len(evidence["related_views"]) <= len(roles) * len(relations)`；L116断言`len(evidence["related_sources"]) <= len(roles) * len(entities)`；L117断言`len(evidence["datetime_controls"]) <= len(roles) * field_count`；L118遍历`evidence["relation_labels"]`。后续分支沿下方源码相同行号继续阅读。 调用`set`、`sum`、`len`、`next`、`json.dumps`、`re.search`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_customer_browser_evidence_is_real_bounded_and_plan_derived`（L182–L217）：接收`tmp_path`、`with_employee_history`。 控制顺序：L187断言`result.returncode == 0 and report["passed"] is True`；L193遍历`[ ("requests", "customer_id"), ("tasks", "request_id"), ("tasks",…`；L198断言`labels["manager", entity, field]["select"] is True`；L199断言`labels["manager", "requests", "assignee_id"]["detail"] is True`；L204断言`views["manager", "customers", "requests"]["visible_records"] > 0`；L205断言`views["manager", "requests", "tasks"]["visible_records"] > 0`；L206断言`views["employee", "customers", "requests"]["visible_records"] > 0`；L207断言`("employee", "requests", "tasks") not in views`。后续分支沿下方源码相同行号继续阅读。 调用`customer_plan`、`run_browser_gate`、`assert_bounded_evidence`、`any`、`set`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_fault_injection_cannot_claim_customer_evidence`（L230–L235）：接收`tmp_path`、`fault`、`failure`。 控制顺序：L232断言`result.returncode != 0 and report["passed"] is False`；L233断言`"business-browser-" + failure in report["message"]`；L234断言`'"source":"verify-business-browser.cjs"' in report["message"]`；L235断言`'"callsites":[{"line":' in report["message"]`。 调用`run_browser_gate`、`customer_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_business_browser_uses_declared_display_fields`（L238–L249）：接收`tmp_path`。 控制顺序：L245断言`not any(field.name in {"name", "title"} for field in plan.entities[1].fields)`；L247断言`result.returncode == 0 and report["passed"] is True`；L249断言`report["browser"]["evidence"]["related_views"]`。 调用`customer_plan().model_dump`、`customer_plan`、`next`、`Plan.model_validate`、`any`、`run_browser_gate`、`assert_bounded_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_minimal_schema_mobile_sticky_actions_remain_inside_table`（L252–L263）：接收`tmp_path`。 控制顺序：L259断言`len(plan.entities[0].fields) == 1`；L261断言`result.returncode == 0 and report["passed"] is True`；L262断言`"business-browser-responsive-actions" in report["browser"]["checks"]`。 调用`runtime_plan`、`len`、`run_browser_gate`、`assert_bounded_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stock_browser_receipt_reaches_platform_gate_without_undeclared_assignment`（L266–L288）：接收`tmp_path`。 控制顺序：L274断言`len(plan.entities) == 3 and len(plan.business.roles) == 3`；L275断言`any(field.kind == "integer" for entity in plan.entities for field in entity.fields)`；L276断言`all(resource.assignee_field is None for resource in plan.business.resources)`；L278断言`result.returncode == 0 and report["passed"] is True`；L280断言`"business-browser-assignment" not in checks`；L281断言`{ "business-browser-transitions", "business-browser-notes-history", "business-browser…`。 调用`fixture_plan`、`load_case`、`len`、`any`、`all`、`run_browser_gate`、`set`、`require_business_evidence`、`plan.model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_browser_evidence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L288。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12102`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_browser_evidence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d576cc69b5f894b09f2c81e9f199a54a4a91cf6bfc4e5be5368604e431a7fac4"} -->
````python
# tests/test_business_browser_evidence.py
"""Real generated-product Chromium evidence and explicit UI fault-injection checks.

Fault cases mutate only a disposable generated product. They prove the independent
browser gate rejects regressions; they never stand in for the passing runtime run.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.tools import clean_env
from workbench.verification import require_business_evidence

ROOT = Path(__file__).parents[1]


def customer_plan(with_employee_history=True):
    data = json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    if not with_employee_history:
        for permission in data["business"]["permissions"]:
            if permission["role"] == "employee":
                permission["actions"] = [
                    action
                    for action in permission["actions"]
                    if action not in {"read_history", "read_audit"}
                ]
    return Plan.model_validate(data)


def run_browser_gate(tmp_path, plan, fault=None):
    module = os.getenv("PRODUCT_VERIFY_PLAYWRIGHT")
    if not module or not Path(module).is_dir():
        pytest.skip("Actual pinned Playwright/Chromium required; no simulated browser fallback")
    product = tmp_path / "product"
    generate_basic(
        plan,
        product,
        {"template": "python-basic", "frontend": "simple-admin", "database": "sqlite"},
    )
    if fault:
        app = product / "web/app.js"
        source = app.read_text(encoding="utf-8")
        mutations = {
            "raw_list_reference": (
                'value=labels[field.name]?.[String(raw)] || "关联记录不可见"',
                "value=String(raw)",
            ),
            "raw_select_reference": (
                'node("option", item.name || item.title || item.id, input)',
                'node("option", item.id, input)',
            ),
            "raw_assignee_detail": (
                'node("option",user.username,select)',
                'node("option",user.id,select)',
            ),
            "omitted_related_records": (
                "group.records.forEach(item=>{",
                "group.records.slice(0,0).forEach(item=>{",
            ),
            "forbidden_datetime_range": (
                "if (field.date_range) {",
                'if (field.date_range || field.kind === "datetime") {',
            ),
        }
        before, after = mutations[fault]
        assert before in source, "UI fault injection must hit the actual generated implementation"
        app.write_text(source.replace(before, after), encoding="utf-8")
    report = tmp_path / "runtime-report.json"
    env = clean_env(
        {
            "PATH": os.environ.get("PATH", ""),
            "PRODUCT_VERIFY_PLAYWRIGHT": module,
            "PLAYWRIGHT_BROWSERS_PATH": "0",
            "PYTHONUTF8": "1",
        }
    )
    result = subprocess.run(
        [sys.executable, "verify.py", "--python", sys.executable, "--report", str(report)],
        cwd=product,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=360,
    )
    assert report.is_file(), result.stdout + result.stderr
    return result, json.loads(report.read_text(encoding="utf-8"))


def assert_bounded_evidence(plan, report):
    browser = report["browser"]
    assert browser["passed"] is True and browser["real_browser"] is True
    evidence = browser["evidence"]
    assert set(evidence) == {
        "version",
        "relation_labels",
        "related_views",
        "related_sources",
        "datetime_controls",
        "query_matrix",
    }
    assert evidence["version"] == 1
    roles = {role.name for role in plan.business.roles}
    entities = {entity.name: entity for entity in plan.entities}
    relations = {(relation.entity, relation.field) for relation in plan.business.relations}
    field_count = sum(len(entity.fields) for entity in plan.entities)
    assert len(evidence["relation_labels"]) <= len(roles) * len(relations)
    assert len(evidence["related_views"]) <= len(roles) * len(relations)
    assert len(evidence["related_sources"]) <= len(roles) * len(entities)
    assert len(evidence["datetime_controls"]) <= len(roles) * field_count
    for entry in evidence["relation_labels"]:
        assert set(entry) == {
            "role",
            "entity",
            "field",
            "list",
            "select",
            "detail",
            "records_checked",
        }
        assert entry["role"] in roles and (entry["entity"], entry["field"]) in relations
        assert entry["list"] is True and 0 < entry["records_checked"] <= 100
        assert entry["select"] is True or entry["select"] is None
        assert entry["detail"] is True or entry["detail"] is None
    for entry in evidence["related_views"]:
        assert set(entry) == {
            "role",
            "entity",
            "target_entity",
            "field",
            "source_records",
            "expected_records",
            "visible_records",
            "target_acl",
            "navigation",
        }
        assert entry["role"] in roles and entry["entity"] in entities
        assert (entry["target_entity"], entry["field"]) in relations
        assert entry["target_acl"] is True
        assert 0 < entry["source_records"] <= 100
        assert entry["expected_records"] == entry["visible_records"]
        assert entry["navigation"] is (True if entry["expected_records"] else None)
    for entry in evidence["related_sources"]:
        assert set(entry) == {"role", "entity", "source_records", "groups_checked", "target_acl"}
        assert entry["role"] in roles and entry["entity"] in entities
        assert entry["target_acl"] is True and 0 < entry["source_records"] <= 100
    for entry in evidence["datetime_controls"]:
        assert set(entry) == {
            "role",
            "entity",
            "field",
            "searchable",
            "date_range",
            "filterable",
            "controls_absent",
        }
        assert entry["role"] in roles and entry["entity"] in entities
        field = next(
            field for field in entities[entry["entity"]].fields if field.name == entry["field"]
        )
        assert field.kind == "datetime"
        assert entry["searchable"] is field.searchable
        assert entry["date_range"] is field.date_range
        assert entry["filterable"] is field.filterable
        assert entry["controls_absent"] is True
    # No raw customer data, generated credentials, usernames or identities escape.
    encoded = json.dumps(evidence, ensure_ascii=False)
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f-]{27,}", encoded, re.I)
    assert not any(
        secret in encoded for secret in ["password", "token", "verify-", "record_id", 'label":']
    )


@pytest.mark.parametrize("with_employee_history", [True, False])
def test_customer_browser_evidence_is_real_bounded_and_plan_derived(
    tmp_path, with_employee_history
):
    plan = customer_plan(with_employee_history)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert_bounded_evidence(plan, report)
    evidence = report["browser"]["evidence"]
    labels = {
        (item["role"], item["entity"], item["field"]): item for item in evidence["relation_labels"]
    }
    for entity, field in [
        ("requests", "customer_id"),
        ("tasks", "request_id"),
        ("tasks", "assignee_id"),
    ]:
        assert labels["manager", entity, field]["select"] is True
    assert labels["manager", "requests", "assignee_id"]["detail"] is True
    views = {
        (item["role"], item["entity"], item["target_entity"]): item
        for item in evidence["related_views"]
    }
    assert views["manager", "customers", "requests"]["visible_records"] > 0
    assert views["manager", "requests", "tasks"]["visible_records"] > 0
    assert views["employee", "customers", "requests"]["visible_records"] > 0
    assert ("employee", "requests", "tasks") not in views
    assert any(
        item["role"] == "employee" and item["entity"] == "requests" and item["groups_checked"] == 0
        for item in evidence["related_sources"]
    )
    assert {
        "business-browser-relation-labels",
        "business-browser-related-views",
        "business-browser-related-row-acl",
        "business-browser-datetime-controls",
    } <= set(report["browser"]["checks"])


@pytest.mark.parametrize(
    "fault, failure",
    [
        ("raw_list_reference", "relation-list-label"),
        ("raw_select_reference", "relation-select-label"),
        ("raw_assignee_detail", "assignee-detail-label"),
        ("omitted_related_records", "related-rendered-records"),
        ("forbidden_datetime_range", "filter-controls-contract"),
    ],
)
def test_browser_fault_injection_cannot_claim_customer_evidence(tmp_path, fault, failure):
    result, report = run_browser_gate(tmp_path, customer_plan(), fault)
    assert result.returncode != 0 and report["passed"] is False, report
    assert "business-browser-" + failure in report["message"], report
    assert '"source":"verify-business-browser.cjs"' in report["message"]
    assert '"callsites":[{"line":' in report["message"]


def test_generic_business_browser_uses_declared_display_fields(tmp_path):
    # An approved generic resource may have no name/title. The customer contract
    # does declare them and remains subject to strict non-ID display assertions.
    data = customer_plan().model_dump()
    requests = next(entity for entity in data["entities"] if entity["name"] == "requests")
    requests["fields"] = [field for field in requests["fields"] if field["name"] != "title"]
    plan = Plan.model_validate(data)
    assert not any(field.name in {"name", "title"} for field in plan.entities[1].fields)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert_bounded_evidence(plan, report)
    assert report["browser"]["evidence"]["related_views"]


def test_minimal_schema_mobile_sticky_actions_remain_inside_table(tmp_path):
    # A single data column used to stretch the auto-layout sticky action column
    # beyond the mobile viewport. Keep every real 390px/1440px, left/right
    # geometry assertion in the generated browser verifier unchanged.
    from test_business_python import runtime_plan

    plan = runtime_plan()
    assert len(plan.entities[0].fields) == 1
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    assert "business-browser-responsive-actions" in report["browser"]["checks"]
    assert_bounded_evidence(plan, report)


def test_stock_browser_receipt_reaches_platform_gate_without_undeclared_assignment(tmp_path):
    # This contract-derived offline Plan exercises the actual generated HTTP,
    # Chromium and restart checks. It never substitutes for the live model Plan.
    from test_template_project_acceptance import fixture_plan

    from scripts.template_acceptance_cases import load_case

    plan = fixture_plan(load_case("stock-purchasing"))
    assert len(plan.entities) == 3 and len(plan.business.roles) == 3
    assert any(field.kind == "integer" for entity in plan.entities for field in entity.fields)
    assert all(resource.assignee_field is None for resource in plan.business.resources)
    result, report = run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    checks = set(report["browser"]["checks"])
    assert "business-browser-assignment" not in checks
    assert {
        "business-browser-transitions",
        "business-browser-notes-history",
        "business-browser-reminders",
        "business-browser-metrics",
        "business-browser-relation-labels",
    } <= checks
    require_business_evidence(plan.model_dump(), report, True)
````
