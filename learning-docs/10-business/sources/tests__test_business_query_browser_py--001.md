# tests/test_business_query_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_browser_proves_each_declared_query_field_and_role`（L14–L82）：接收`tmp_path`。 控制顺序：L17断言`result.returncode == 0 and report["passed"] is True`；L19断言`browser["real_browser"] is True`；L20断言`"business-browser-query-matrix" in browser["checks"]`；L24遍历`plan.business.permissions`；L25按`"read" not in permission.actions`分支；L29遍历`entity.fields`；L30按`field.searchable`分支；L32按`field.filterable`分支。后续分支沿下方源码相同行号继续阅读。 调用`browser_evidence.customer_plan`、`browser_evidence.run_browser_gate`、`set`、`next`、`expected.add`、`key`、`len`、`item.items`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_proves_each_declared_query_field_and_role.key`（L37–L38）：接收`item`。 返回路径：L38的`item["role"], item["entity"], item["field"], item["kind"]`。
- `test_browser_rejects_query_control_and_rendering_faults`（L118–L133）：接收`tmp_path`、`monkeypatch`、`before`、`after`、`failure`。 控制顺序：L132断言`result.returncode != 0 and report["passed"] is False`；L133断言`"business-browser-" + failure in report["message"]`。 调用`monkeypatch.setattr`、`browser_evidence.run_browser_gate`、`browser_evidence.customer_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_rejects_query_control_and_rendering_faults.with_ui_fault`（L123–L128）：接收`plan`、`product`、`selection`。 控制顺序：L127断言`source.count(before) == 1`。 调用`generate`、`app.read_text`、`source.count`、`app.write_text`、`source.replace`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_query_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L133。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5343`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_query_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "56e81434f8981d9c2b099331b7c252bba0d130c0dbf6644dfc2dea986ce063cd"} -->
````python
# tests/test_business_query_browser.py
"""Real Chromium query evidence, including failures the retained-row check missed.

Every case runs the generated product and its actual verification driver. Mutations
touch only the disposable generated UI and cannot supply passing evidence.
"""

import json
import re

import pytest
import test_business_browser_evidence as browser_evidence


def test_browser_proves_each_declared_query_field_and_role(tmp_path):
    plan = browser_evidence.customer_plan()
    result, report = browser_evidence.run_browser_gate(tmp_path, plan)
    assert result.returncode == 0 and report["passed"] is True, report
    browser = report["browser"]
    assert browser["real_browser"] is True
    assert "business-browser-query-matrix" in browser["checks"]
    matrix = browser["evidence"]["query_matrix"]
    api_matrix = report["business"]["evidence"]["query_matrix"]
    expected = set()
    for permission in plan.business.permissions:
        if "read" not in permission.actions:
            continue
        entity = next(entity for entity in plan.entities if entity.name == permission.entity)
        searchable = [field for field in entity.fields if field.searchable]
        for field in entity.fields:
            if field.searchable:
                expected.add((permission.role, entity.name, field.name, "keyword"))
            if field.filterable:
                expected.add((permission.role, entity.name, field.name, "exact_filter"))
                if searchable:
                    expected.add((permission.role, entity.name, field.name, "combined"))

    def key(item):
        return item["role"], item["entity"], item["field"], item["kind"]

    assert {key(item) for item in matrix} == expected
    assert len(matrix) == len(expected)
    api_by_key = {key(item): item for item in api_matrix}
    browser_flags = {
        "query_values_verified",
        "response_ids_exact",
        "rendered_ids_exact",
        "controls_reset",
    }
    for item in matrix:
        assert {name: value for name, value in item.items() if name not in browser_flags} == (
            api_by_key[key(item)]
        )
        assert all(item[name] is True for name in browser_flags)
        assert item["cases"] == 2
        assert item["exact_results"] is True and item["role_scope"] is True
        assert all(
            type(item[name]) is int and 0 <= item[name] <= 200
            for name in (
                "positive_matches",
                "other_matches",
                "excluded_records",
                "foreign_matches",
                "isolated_matches",
            )
        )
    for entity in plan.entities:
        for field in entity.fields:
            if field.searchable:
                assert any(
                    item["entity"] == entity.name
                    and item["field"] == field.name
                    and item["kind"] == "keyword"
                    and item["isolated_matches"] > 0
                    for item in matrix
                )
    # The summary carries approved field names and aggregate counts only.
    encoded = json.dumps(matrix, ensure_ascii=False)
    assert not re.search(r"[0-9a-f]{8}-[0-9a-f-]{27,}", encoded, re.I)
    assert not any(
        private in encoded
        for private in ["password", "token", "verify-", "expected_ids", "params", "record_id"]
    )


@pytest.mark.parametrize(
    "before,after,failure",
    [
        (
            "if (value) query.set(key, value);",
            'if (value && key !== "q") query.set(key, value);',
            "query-control-values",
        ),
        (
            "if (value) query.set(key, value);",
            'if (value && !key.startsWith("filter_")) query.set(key, value);',
            "query-control-values",
        ),
        (
            'query.set("limit", "50");',
            'query.set("limit", "50");\n'
            '  if (query.has("q")) for (const key of [...query.keys()])\n'
            '    if (key.startsWith("filter_")) query.delete(key);',
            "query-control-values",
        ),
        (
            "for (const row of rows) {",
            'for (const row of query.has("q") ? rows.slice(1) : rows) {',
            "query-rendered-ids",
        ),
        (
            'HTMLFormElement.prototype.reset.call($("filters"));',
            "/* Fault injection: leave the submitted controls populated. */",
            "query-control-values",
        ),
    ],
    ids=["missing-keyword", "missing-filter", "ignored-and", "missing-rendered-row", "stale-reset"],
)
def test_browser_rejects_query_control_and_rendering_faults(
    tmp_path, monkeypatch, before, after, failure
):
    generate = browser_evidence.generate_basic

    def with_ui_fault(plan, product, selection):
        generate(plan, product, selection)
        app = product / "web/app.js"
        source = app.read_text(encoding="utf-8")
        assert source.count(before) == 1, "Fault must target the actual generated UI exactly once"
        app.write_text(source.replace(before, after), encoding="utf-8")

    monkeypatch.setattr(browser_evidence, "generate_basic", with_ui_fault)
    result, report = browser_evidence.run_browser_gate(tmp_path, browser_evidence.customer_plan())
    assert result.returncode != 0 and report["passed"] is False, report
    assert "business-browser-" + failure in report["message"], report
````
