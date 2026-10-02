# workbench/verification.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：基础产品的真实验收和干净解压复验。** 先用产品自己的锁安装独立环境，再运行产品HTTP和逐规格真实Chromium验收。require_browser_evidence核对当前实体、字段与检查名称，不接纳缺项报告；package_basic解压到新目录再次完整验证，避免仅在工作目录偶然可运行。

**对应关系：** flow → verify_basic/package_basic → templates/product/verify.py/verify_business.py；test_customer_workflow与test_business_python。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.rules`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** verify_basic先核对生成回执与当前源码，再让产品自己的环境真实运行；页面、HTTP和重启失败会保留失败，不能靠模型审阅改成passed。package_basic随后还要在新目录解压复验，检测遗漏文件或借用平台环境的问题。测试后改一个受保护文件，原有报告即失效。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product_interpreter`（L21–L40）：接收`product`、`settings`。 控制顺序：L22按`not settings.install_products`分支；L25按`not uv`分支；L26抛异常，停止当前正常路径；L39抛异常，停止当前正常路径。 调用`shutil.which`、`PrerequisiteError`、`json.loads`、`(Path(product) / "selection.json").read_text`、`Path`、`run_command`、`str`。 返回路径：L23的`sys.executable`；L40的`str(product / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))`。
- `run_probe`（L43–L75）：接收`product`、`python`、`report_path`、`settings`、`business_screenshots`。 调用`json.loads`、`(Path(product) / "selection.json").read_text`、`Path`、`database`、`nullcontext`、`run_command`、`str`、`os.environ.get`。 返回路径：L49的`run_command( [ sys.executable, str(ROOT / "templates/product/verify.py"), "--product", str…`。
- `require_browser_evidence`（L78–L117）：接收`product`、`report`。 控制顺序：L81按`spec.get("business")`分支；L84按`selection["frontend"] != "simple-admin"`分支；L87按`not isinstance(browser, dict) or any(browser.get(key) is not True for key in ("passed…`分支；L92抛异常，停止当前正常路径；L94遍历`spec["entities"]`；L106遍历`entity["fields"]`；L107遍历`( ("searchable", "browser-search"), ("filterable", "browser-filte…`；L112按`field.get(flag)`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`(Path(product) / "selection.json").read_text`、`Path`、`(Path(product) / "approved-spec.json").read_text`、`spec.get`、`require_business_evidence`、`report.get`、`isinstance`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_business_proof`（L120–L489）：接收`spec`、`report`、`with_browser`。 源码说明：Bind detailed executed proof to this Plan; aggregate success markers alone fail closed.。 控制顺序：L144断言`type(proof["version"]) is int and proof["version"] == 1`；L145断言`set(proof) == { "version", "field_validation", "related_views", "relation_labels", "d…`；L174遍历`spec["entities"]`；L176遍历`contract["roles"]`；L177按`not read(role["name"], entity["name"])`分支；L179遍历`entity["fields"]`；L185遍历`kinds`；L191断言`set(queries) == set(expected_queries)`。后续分支沿下方源码相同行号继续阅读。 调用`set`、`len`、`type`、`next`、`read`、`indexed`、`queries.items`、`any`、`resources.values`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_business_proof.indexed`（L130–L135）：接收`values`、`keys`、`limit`。 控制顺序：L131断言`isinstance(values, list) and len(values) <= limit`；L132断言`all(isinstance(value, dict) for value in values)`；L134断言`len(result) == len(values)`。 调用`isinstance`、`len`、`all`、`tuple`。 返回路径：L135的`result`。
- `require_business_proof.positive`（L137–L138）：接收`value`、`limit`。 控制顺序：L138断言`type(value) is int and 0 < value <= limit`。 调用`type`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_business_proof.read`（L140–L141）：接收`role`、`entity`。 调用`permissions.get`、`set`。 返回路径：L141的`"read" in permissions.get((role, entity), set())`。
- `require_business_evidence`（L492–L550）：接收`spec`、`report`、`with_browser`。 控制顺序：L513按`not isinstance(business, dict) or business.get("passed") is not True or business.get(…`分支；L521抛异常，停止当前正常路径；L523按`not with_browser`分支；L542按`not isinstance(browser, dict) or any(browser.get(key) is not True for key in ("passed…`分支；L550抛异常，停止当前正常路径。 调用`report.get`、`isinstance`、`business.get`、`digest`、`required.issubset`、`set`、`PrerequisiteError`、`require_business_proof`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `validate_rule_examples`（L553–L563）：接收`plan`、`product`。 控制顺序：L555遍历`plan.custom_rules`；L556遍历`rule.accept_examples`；L558遍历`rule.reject_examples`；L563抛异常，停止当前正常路径。 调用`Rules`、`(product / "custom_rules.py").read_text`、`rules.validate`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_basic`（L566–L622）：接收`plan`、`product`、`settings`、`attempt`。 控制顺序：L571按`set(current) != set(original) or any( current[k] != v for k, v in original.items() if…`分支；L574抛异常，停止当前正常路径；L575按`receipt["spec_digest"] != digest(plan.model_dump())`分支；L576抛异常，停止当前正常路径；L578遍历`files(product)`；L579按`name.endswith(".py")`分支；L594按`not report_path.exists()`分支；L595抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`json.loads`、`(product.parent / "generation.json").read_text`、`manifest`、`set`、`any`、`original.items`、`PrerequisiteError`、`digest`等。 返回路径：L583的`{ "passed": False, "kind": "code", "error": str(exc)[:500], "attempt": attempt, }`；L601的`{ "passed": False, "kind": "code", "error": report.get("message", "运行验收失败"), "attempt": at…`；L622的`report`。
- `package_basic`（L625–L668）：接收`plan`、`product`、`settings`、`report`。 控制顺序：L628按`report.get("passed") is not True or report.get("source_digest") != digest(listing)`分支；L629抛异常，停止当前正常路径；L635遍历`files(product)`；L643按`manifest(clean) != listing`分支；L644抛异常，停止当前正常路径；L649按`manifest(clean) != listing`分支；L650抛异常，停止当前正常路径；L652按`evidence.get("passed") is not True`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`manifest`、`report.get`、`digest`、`PrerequisiteError`、`require_browser_evidence`、`archive.with_suffix`、`zipfile.ZipFile`、`files`等。 返回路径：L668的`result`。

</details>

**创建路径：** `workbench/verification.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L668。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`29976`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/verification.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7003537acdadcec1c20a1909be45f33898503651794455ad319b62c3bf84ccaa"} -->
````python
# workbench/verification.py
"""Independent runtime checks, reproducible packaging, and clean-room verification."""

import ast
import json
import os
import shutil
import sys
import tempfile
import zipfile
from contextlib import nullcontext
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, manifest, sha, unpack, write_json
from workbench.generator import PrerequisiteError
from workbench.rules import Rules, UnsafeRule
from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command


def product_interpreter(product, settings):
    if not settings.install_products:
        return sys.executable
    uv = shutil.which("uv")
    if not uv:
        raise PrerequisiteError("独立产品验收需要 uv，当前 PATH 中未找到")
    selected = json.loads((Path(product) / "selection.json").read_text(encoding="utf-8"))[
        "database"
    ]
    extras = ["--extra", "postgres"] if selected == "postgresql" else []
    try:
        run_command(
            [uv, "sync", "--locked", "--no-dev", *extras, "--project", str(product)],
            product,
            timeout=settings.tool_timeout,
            extra_env={"UV_PYTHON": sys.executable},
        )
    except ToolFailure as exc:
        raise PrerequisiteError("产品依赖安装失败；这是环境故障，不自动修改业务代码") from exc
    return str(product / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))


def run_probe(product, python, report_path, settings, *, business_screenshots=None):
    from workbench.postgres_lab import database

    selection = json.loads((Path(product) / "selection.json").read_text(encoding="utf-8"))
    scope = database(settings) if selection["database"] == "postgresql" else nullcontext(None)
    with scope as url:
        return run_command(
            [
                sys.executable,
                str(ROOT / "templates/product/verify.py"),
                "--product",
                str(product),
                "--python",
                python,
                "--report",
                str(report_path),
                *(
                    ["--business-screenshots", str(business_screenshots)]
                    if business_screenshots is not None
                    else []
                ),
            ],
            ROOT,
            timeout=settings.tool_timeout,
            extra_env={
                **({"VERIFY_DATABASE_URL": url} if url else {}),
                "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get(
                    "PRODUCT_VERIFY_PLAYWRIGHT",
                    str(ROOT / ".native/browser/node_modules/playwright"),
                ),
                "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
            },
        )


def require_browser_evidence(product, report):
    selection = json.loads((Path(product) / "selection.json").read_text(encoding="utf-8"))
    spec = json.loads((Path(product) / "approved-spec.json").read_text(encoding="utf-8"))
    if spec.get("business"):
        require_business_evidence(spec, report, selection["frontend"] == "simple-admin")
        return
    if selection["frontend"] != "simple-admin":
        return
    browser = report.get("browser")
    if (
        not isinstance(browser, dict)
        or any(browser.get(key) is not True for key in ("passed", "real_browser", "applicable"))
        or browser.get("entities") != [entity["name"] for entity in spec["entities"]]
    ):
        raise PrerequisiteError("simple-admin 缺少逐产品真实浏览器验收，不能交付")
    required = {"browser-registration", "browser-login-invalid-password-logout-reload"}
    for entity in spec["entities"]:
        name = entity["name"]
        required.update(
            f"{check}:{name}"
            for check in (
                "browser-create",
                "browser-field-lengths",
                "browser-combined-filter",
                "browser-user-isolation",
                "browser-update-delete",
            )
        )
        for field in entity["fields"]:
            for flag, check in (
                ("searchable", "browser-search"),
                ("filterable", "browser-filter"),
                ("date_range", "browser-inclusive-date"),
            ):
                if field.get(flag):
                    required.add(f"{check}:{name}.{field['name']}")
            if field["kind"] == "text":
                required.add(f"browser-overlength-rejected:{name}.{field['name']}")
    if not required.issubset(set(browser.get("checks", []))) or browser.get("errors") != []:
        raise PrerequisiteError("真实浏览器验收覆盖不完整或存在页面错误")


def require_business_proof(spec, report, with_browser):
    """Bind detailed executed proof to this Plan; aggregate success markers alone fail closed."""
    try:
        contract = spec["business"]
        fields = {(e["name"], f["name"]): f for e in spec["entities"] for f in e["fields"]}
        resources = {r["entity"]: r for r in contract["resources"]}
        permissions = {(p["role"], p["entity"]): set(p["actions"]) for p in contract["permissions"]}
        relations = {(r["entity"], r["field"]): r["target_entity"] for r in contract["relations"]}
        role_count = len(contract["roles"])

        def indexed(values, keys, limit):
            assert isinstance(values, list) and len(values) <= limit
            assert all(isinstance(value, dict) for value in values)
            result = {tuple(value[key] for key in keys): value for value in values}
            assert len(result) == len(values)
            return result

        def positive(value, limit=10000):
            assert type(value) is int and 0 < value <= limit

        def read(role, entity):
            return "read" in permissions.get((role, entity), set())

        proof = report["business"]["evidence"]
        assert type(proof["version"]) is int and proof["version"] == 1
        assert set(proof) == {
            "version",
            "field_validation",
            "related_views",
            "relation_labels",
            "datetime_policy",
            "due_notifications",
            "audit_immutability",
            "query_matrix",
        }
        query_keys = {
            "role",
            "entity",
            "field",
            "kind",
            "keyword_field",
            "scope",
            "cases",
            "positive_matches",
            "other_matches",
            "excluded_records",
            "foreign_matches",
            "isolated_matches",
            "exact_results",
            "role_scope",
        }
        query_identity = ("role", "entity", "field", "kind")
        expected_queries = {}
        grants = {(p["role"], p["entity"]): p for p in contract["permissions"]}
        for entity in spec["entities"]:
            keyword = next((f["name"] for f in entity["fields"] if f["searchable"]), None)
            for role in contract["roles"]:
                if not read(role["name"], entity["name"]):
                    continue
                for field in entity["fields"]:
                    kinds = (["keyword"] if field["searchable"] else []) + (
                        ["exact_filter", *(["combined"] if keyword else [])]
                        if field["filterable"]
                        else []
                    )
                    for kind in kinds:
                        expected_queries[role["name"], entity["name"], field["name"], kind] = (
                            grants[role["name"], entity["name"]]["scope"],
                            keyword if kind == "combined" else None,
                        )
        queries = indexed(proof["query_matrix"], query_identity, len(expected_queries))
        assert set(queries) == set(expected_queries)
        for identity, item in queries.items():
            assert set(item) == query_keys
            assert (item["scope"], item["keyword_field"]) == expected_queries[identity]
            assert type(item["cases"]) is int and item["cases"] == 2
            for key, maximum in (
                ("positive_matches", 100),
                ("other_matches", 100),
                ("excluded_records", 200),
                ("foreign_matches", 200),
                ("isolated_matches", 100),
            ):
                assert type(item[key]) is int and 0 <= item[key] <= maximum
            assert item["exact_results"] is True and item["role_scope"] is True
            assert item["isolated_matches"] <= item["positive_matches"]
            if item["kind"] == "keyword":
                assert item["other_matches"] == 0
            if item["kind"] != "keyword":
                assert item["isolated_matches"] == 0
            if item["scope"] == "all":
                assert item["foreign_matches"] == 0
        # Zero rows may be correct for a particular read-only/own actor. But each
        # declared capability needs an independent positive/control witness somewhere.
        for entity, field in fields:
            for kind in ("keyword", "exact_filter", "combined"):
                group = [
                    v for (r, e, f, k), v in queries.items() if (e, f, k) == (entity, field, kind)
                ]
                if group:
                    assert any(v["positive_matches"] > 0 for v in group)
                    singleton_filter = (
                        kind == "exact_filter"
                        and fields[entity, field]["kind"] == "enum"
                        and fields[entity, field]["required"] is True
                        and len(fields[entity, field]["choices"]) == 1
                    )
                    if not singleton_filter:
                        assert any(v["excluded_records"] > 0 for v in group)
                    if kind == "keyword":
                        assert any(v["isolated_matches"] > 0 for v in group)
        validations = indexed(proof["field_validation"], ("entity", "field"), len(fields))
        assert set(validations) == set(fields)
        protected = {
            (r["entity"], r["assignee_field"])
            for r in resources.values()
            if r.get("assignee_field")
        }
        for workflow in contract["workflows"]:
            protected.add((workflow["entity"], workflow["status_field"]))
            protected.update(
                (workflow["entity"], t["set_timestamp"])
                for t in workflow["transitions"]
                if t.get("set_timestamp")
            )
        for identity, field in fields.items():
            entity, name = identity
            creators = [
                role["name"]
                for role in contract["roles"]
                if {"create", "read"} <= permissions.get((role["name"], entity), set())
            ]
            creator = (
                contract["bootstrap_role"]
                if contract["bootstrap_role"] in creators
                else creators[0]
            )
            creator_policy = next(
                p for p in contract["permissions"] if (p["role"], p["entity"]) == (creator, entity)
            )
            update = "update" in creator_policy["actions"] and creator_policy["scope"] in {
                "all",
                "own",
            }
            item = validations[identity]
            assert item["kind"] == field["kind"] and item["required"] is field["required"]
            if identity in protected:
                assert item["protected_create_rejected"] is True
                if update:
                    assert item["protected_update_rejected"] is True
            else:
                if field["required"]:
                    assert (
                        item["missing_required_rejected"] is True and item["null_rejected"] is True
                    )
                    if field["kind"] in {"text", "enum"}:
                        assert item["blank_rejected"] is True
                if field["kind"] == "text":
                    assert (
                        type(item["max_length"]) is int
                        and item["max_length"] == field["max_length"]
                    )
                    assert item["over_max_length_rejected"] is True
                    if field.get("min_length", 0):
                        assert (
                            type(item["min_length"]) is int
                            and item["min_length"] == field["min_length"]
                        )
                        assert item["under_min_length_rejected"] is True
                if field["kind"] == "enum":
                    assert type(item["declared_choices"]) is int and item[
                        "declared_choices"
                    ] == len(field["choices"])
                    assert item["invalid_enum_rejected"] is True
                if field["kind"] == "datetime":
                    assert item["invalid_timestamp_rejected"] is True
                invalid_count = (
                    int(field["required"])
                    + int(field["required"] and field["kind"] in {"text", "enum"})
                    + int(field["kind"] == "text")
                    + int(field["kind"] == "text" and bool(field.get("min_length")))
                    + int(field["kind"] == "enum")
                    + int(field["kind"] == "datetime")
                )
                if update and invalid_count:
                    assert (
                        type(item["invalid_updates_rejected"]) is int
                        and item["invalid_updates_rejected"] == invalid_count
                    )
            if "protected_update_rejected" in item:
                assert item["protected_update_rejected"] is True
            if "invalid_updates_rejected" in item:
                positive(item["invalid_updates_rejected"], 6)
        dated = {
            identity: field for identity, field in fields.items() if field["kind"] == "datetime"
        }
        timestamps = indexed(proof["datetime_policy"], ("entity", "field"), len(dated))
        assert set(timestamps) == set(dated)
        for identity, field in dated.items():
            item = timestamps[identity]
            assert all(
                item[key] is field[key] for key in ("searchable", "filterable", "date_range")
            )
            assert item["timestamp_stored"] is True
            if not field["searchable"]:
                assert item["excluded_from_keyword_search"] is True
            expected = ([] if field["filterable"] else ["filter"]) + (
                [] if field["date_range"] else ["from", "to"]
            )
            assert item["undeclared_query_parameters_rejected"] == expected
        due_rules = {
            (n["entity"], n["due_field"], n["recipient"])
            for n in contract["notifications"]
            if n["event"] == "due"
        }
        due = indexed(proof["due_notifications"], ("entity", "field", "recipient"), len(due_rules))
        assert set(due) == due_rules
        for item in due.values():
            positive(item["past_due_events_verified"])
            assert all(
                item[key] is True
                for key in (
                    "future_deadline_no_event",
                    "repeated_reads_deduplicated",
                    "event_and_read_state_persisted_after_restart",
                )
            )
        audits = indexed(proof["audit_immutability"], ("entity",), len(resources))
        assert set(audits) == {(name,) for name, resource in resources.items() if resource["audit"]}
        for item in audits.values():
            positive(item["entries_checked"])
            assert (
                type(item["mutation_delete_attempts_rejected"]) is int
                and item["mutation_delete_attempts_rejected"] == 6
            )
            assert item["surface"] == "http_history_collection_and_entry"
            assert all(
                item[key] is True
                for key in (
                    "action_actor_timestamp",
                    "unchanged_after_attempts",
                    "archive_and_restart_preserved",
                )
            )
        views = indexed(proof["related_views"], ("role", "entity"), role_count * len(resources))
        assert {entity for role, entity in views} == set(resources)
        for (role, entity), item in views.items():
            assert read(role, entity) and item["target_row_acl"] is True
            positive(item["source_records_checked"], 100)
            expected = {
                source
                for (source, field), target in relations.items()
                if target == entity and read(role, source)
            }
            assert sorted(item["target_entities"]) == sorted(expected)
        labels = indexed(
            proof["relation_labels"], ("role", "entity", "field"), role_count * len(relations)
        )
        assert {(entity, field) for role, entity, field in labels} == set(relations)
        for (role, entity, field), item in labels.items():
            assert read(role, entity) and (entity, field) in relations
            assert (role, entity) in views
            positive(item["references_checked"], 100)
            assert all(item[key] is True for key in ("readable_labels_verified", "target_row_acl"))
        if not with_browser:
            return
        browser = report["browser"]["evidence"]
        assert type(browser["version"]) is int and browser["version"] == 1
        assert set(browser) == {
            "version",
            "relation_labels",
            "related_views",
            "related_sources",
            "datetime_controls",
            "query_matrix",
        }
        ui_queries = indexed(browser["query_matrix"], query_identity, len(expected_queries))
        assert set(ui_queries) == set(queries)
        ui_query_keys = {
            "query_values_verified",
            "response_ids_exact",
            "rendered_ids_exact",
            "controls_reset",
        }
        for identity, item in ui_queries.items():
            assert set(item) == query_keys | ui_query_keys
            assert all(item[key] is True for key in ui_query_keys)
            assert all(
                type(item[key]) is type(queries[identity][key])
                and item[key] == queries[identity][key]
                for key in query_keys
            )
        ui_labels = indexed(
            browser["relation_labels"], ("role", "entity", "field"), role_count * len(relations)
        )
        assert set(ui_labels) == set(labels)
        for identity, item in ui_labels.items():
            assert (
                type(item["records_checked"]) is int
                and item["records_checked"] == labels[identity]["references_checked"]
            )
            assert item["list"] is True
            assert all(item[key] is None or item[key] is True for key in ("select", "detail"))
            role, entity, field = identity
            actions = permissions[role, entity]
            if relations[entity, field] == "$users":
                if field == resources[entity].get("assignee_field") and "assign" in actions:
                    assert item["select"] is True and item["detail"] is True
            elif {"create", "update"} & actions:
                assert item["select"] is True
        ui_sources = indexed(
            browser["related_sources"], ("role", "entity"), role_count * len(resources)
        )
        assert set(ui_sources) == set(views)
        expected_views = set()
        for (role, entity), item in ui_sources.items():
            expected = {
                (role, entity, source, field)
                for (source, field), target in relations.items()
                if target == entity and read(role, source)
            }
            expected_views.update(expected)
            assert (
                type(item["source_records"]) is int
                and item["source_records"] == views[role, entity]["source_records_checked"]
            )
            assert (
                type(item["groups_checked"]) is int
                and item["groups_checked"] == len(expected) * item["source_records"]
            )
            assert item["target_acl"] is True
        ui_views = indexed(
            browser["related_views"],
            ("role", "entity", "target_entity", "field"),
            role_count * len(relations),
        )
        assert set(ui_views) == expected_views
        for (role, entity, target, field), item in ui_views.items():
            assert (
                type(item["source_records"]) is int
                and item["source_records"] == views[role, entity]["source_records_checked"]
            )
            assert type(item["expected_records"]) is int and 0 <= item["expected_records"] <= 10000
            assert (
                type(item["visible_records"]) is int
                and item["visible_records"] == item["expected_records"]
            )
            assert item["target_acl"] is True
            assert item["navigation"] is (True if item["visible_records"] else None)
        controls = indexed(
            browser["datetime_controls"], ("role", "entity", "field"), role_count * len(dated)
        )
        assert set(controls) == {
            (role["name"], entity, field)
            for role in contract["roles"]
            for entity, field in dated
            if read(role["name"], entity)
        }
        for (role, entity, field), item in controls.items():
            declared = dated[entity, field]
            assert all(
                item[key] is declared[key] for key in ("searchable", "filterable", "date_range")
            )
            assert item["controls_absent"] is (
                not any(declared[key] for key in ("searchable", "filterable", "date_range"))
            )
    except AssertionError, KeyError, TypeError, ValueError, AttributeError:
        raise PrerequisiteError(
            "逐字段约束、查询矩阵、关联权限、时间戳、逾期与不可改写审计的独立业务证据缺失或不匹配"
        ) from None


def require_business_evidence(spec, report, with_browser):
    business = report.get("business")
    required = {
        "business-bootstrap",
        "business-role-default",
        "business-row-permissions",
        "business-protected-fields",
        "business-relations",
        "business-transitions",
        "business-notes-history",
        "business-notifications",
        "business-scoped-metrics",
        "business-archive",
        "business-field-validation",
        "business-related-views",
        "business-readable-relation-labels",
        "business-datetime-policy",
        "business-due-reminders",
        "business-audit-immutability",
        "business-query-matrix",
    }
    if (
        not isinstance(business, dict)
        or business.get("passed") is not True
        or business.get("spec_digest") != digest(spec)
        or business.get("resources_checked") != [e["name"] for e in spec["entities"]]
        or business.get("roles_checked") != [r["name"] for r in spec["business"]["roles"]]
        or not required.issubset(set(business.get("checks", [])))
    ):
        raise PrerequisiteError("业务关系、流程、角色权限与统计验收证据缺失，不能交付")
    require_business_proof(spec, report, with_browser)
    if not with_browser:
        return
    browser = report.get("browser")
    checks = {
        "business-browser-auth",
        "business-browser-role-navigation",
        "business-browser-assignment",
        "business-browser-transitions",
        "business-browser-notes-history",
        "business-browser-reminders",
        "business-browser-metrics",
        "business-browser-role-restrictions",
        "business-browser-related-views",
        "business-browser-related-row-acl",
        "business-browser-datetime-controls",
        "business-browser-query-matrix",
        *(["business-browser-relation-labels"] if spec["business"]["relations"] else []),
        *["business-browser-records:" + e["name"] for e in spec["entities"]],
    }
    if (
        not isinstance(browser, dict)
        or any(browser.get(key) is not True for key in ("passed", "real_browser", "applicable"))
        or browser.get("spec_digest") != digest(spec)
        or browser.get("entities") != [e["name"] for e in spec["entities"]]
        or browser.get("errors") != []
        or not checks.issubset(set(browser.get("checks", [])))
    ):
        raise PrerequisiteError("业务页面的逐角色真实浏览器验收不完整")


def validate_rule_examples(plan, product):
    rules = Rules((product / "custom_rules.py").read_text(encoding="utf-8"))
    for rule in plan.custom_rules:
        for sample in rule.accept_examples:
            rules.validate(rule.entity, sample)
        for sample in rule.reject_examples:
            try:
                rules.validate(rule.entity, sample)
            except ValueError:
                continue
            raise ValueError("业务规则没有拒绝已经批准的反例")


def verify_basic(plan, product, settings, attempt=0):
    product = Path(product)
    receipt = json.loads((product.parent / "generation.json").read_text(encoding="utf-8"))
    current = manifest(product)
    original = receipt["files"]
    if set(current) != set(original) or any(
        current[k] != v for k, v in original.items() if k != "custom_rules.py"
    ):
        raise PrerequisiteError("可信模板文件被修改；禁止通过修改测试或启动器绕过验收")
    if receipt["spec_digest"] != digest(plan.model_dump()):
        raise PrerequisiteError("生成依据与已批准设计不一致")
    try:
        for name, path in files(product):
            if name.endswith(".py"):
                ast.parse(path.read_text(encoding="utf-8"), filename=name)
        validate_rule_examples(plan, product)
    except (SyntaxError, ValueError, UnsafeRule) as exc:
        return {
            "passed": False,
            "kind": "code",
            "error": str(exc)[:500],
            "attempt": attempt,
        }
    python = product_interpreter(product, settings)
    report_path = product.parent / f"runtime-{attempt}.json"
    try:
        execution = run_probe(product, python, report_path, settings)
    except ToolFailure as exc:
        if not report_path.exists():
            raise PrerequisiteError("运行验收未产生报告；检查本机工具环境与超时配置") from exc
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("kind") == "environment":
            raise PrerequisiteError(report.get("message", "浏览器验收环境不可用")) from exc
        if report.get("passed") is True:
            raise PrerequisiteError("验证进程失败但报告声称成功；拒绝使用该报告") from exc
        return {
            "passed": False,
            "kind": "code",
            "error": report.get("message", "运行验收失败"),
            "attempt": attempt,
            "source_digest": digest(current),
        }
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if manifest(product) != current:
        raise PrerequisiteError("验收期间源码发生变化")
    if report.get("passed") is not True or not report.get("restart") or not report.get("http"):
        raise PrerequisiteError("运行验收证据不完整")
    require_browser_evidence(product, report)
    report.update(
        source_digest=digest(current),
        spec_digest=digest(plan.model_dump()),
        isolated_dependencies=settings.install_products,
        attempt=attempt,
        exit_code=execution["returncode"],
    )
    write_json(product.parent / "verification.json", report)
    return report


def package_basic(plan, product, settings, report):
    product = Path(product)
    listing = manifest(product)
    if report.get("passed") is not True or report.get("source_digest") != digest(listing):
        raise PrerequisiteError("源码在测试后发生变化，必须重新验证")
    require_browser_evidence(product, report)
    archive = product.parent / "delivery.zip"
    temporary = archive.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, path in files(product):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, path.read_bytes())
        with tempfile.TemporaryDirectory(prefix="rnd-cleanroom-") as directory:
            clean = Path(directory) / "product"
            unpack(temporary, clean)
            if manifest(clean) != listing:
                raise PrerequisiteError("ZIP 内文件与通过验收的源码不一致")
            python = product_interpreter(clean, settings)
            clean_report = Path(directory) / "cleanroom.json"
            run_probe(clean, python, clean_report, settings)
            evidence = json.loads(clean_report.read_text(encoding="utf-8"))
            if manifest(clean) != listing:
                raise PrerequisiteError("干净验收期间源码发生变化")
            require_browser_evidence(clean, evidence)
            if evidence.get("passed") is not True:
                raise PrerequisiteError("干净解压验收失败")
        os.replace(temporary, archive)
    finally:
        temporary.unlink(missing_ok=True)
    result = {
        "package": "delivery.zip",
        "sha256": sha(archive),
        "files": listing,
        "spec_digest": digest(plan.model_dump()),
        "cleanroom": evidence,
        "isolated_dependencies": settings.install_products,
        "validation_level": "runtime",
        "production_ready": False,
    }
    write_json(product.parent / "delivery.json", result)
    return result
````
