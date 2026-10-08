# tests/test_business_query_api.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_customer_api_query_matrix_is_field_specific_and_role_scoped`（L14–L56）：接收`tmp_path`。 控制顺序：L21断言`result.returncode == 0`；L24断言`"business-query-matrix" in report["business"]["checks"]`；L25遍历`plan.entities`；L26遍历`entity.fields`；L27按`field.searchable`分支；L33断言`records and all(p["other_matches"] == 0 for p in records)`；L34断言`any(p["isolated_matches"] > 0 for p in records)`；L35按`field.filterable`分支。后续分支沿下方源码相同行号继续阅读。 调用`customer_plan`、`generate_basic`、`execute`、`json.loads`、`result.stdout.splitlines`、`all`、`any`、`len`、`json.dumps(proof).encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bounded_integer_query_controls_use_valid_values_including_singleton`（L68–L98）：接收`tmp_path`、`maximum`。 控制顺序：L88断言`result.returncode == 0`；L93断言`validation["minimum"] == 2 and validation["maximum"] == maximum`；L94断言`validation["below_minimum_rejected"] and validation["above_maximum_rejected"]`；L96断言`controls and all( item["positive_matches"] > 0 and item["excluded_records"] > 0 for i…`。 调用`runtime_plan().model_dump`、`runtime_plan`、`raw["entities"][0]["fields"].append`、`Plan.model_validate`、`generate_basic`、`execute`、`json.loads`、`result.stdout.splitlines`、`require_business_evidence`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_short_keyword_fields_keep_independent_positive_controls`（L102–L123）：接收`tmp_path`、`maximum`。 控制顺序：L120断言`result.returncode == 0`；L123断言`short and all(entry["isolated_matches"] > 0 for entry in short)`。 调用`runtime_plan().model_dump`、`runtime_plan`、`raw["entities"][0]["fields"].append`、`generate_basic`、`Plan.model_validate`、`execute`、`json.loads`、`result.stdout.splitlines`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_matrix_rejects_each_disabled_declared_query_field`（L127–L148）：接收`tmp_path`、`entity`、`field`、`kind`。 控制顺序：L136按`kind == "keyword"`分支；L142断言`before in source`；L146断言`result.returncode == 1 and report["passed"] is False`；L147断言`"Query matrix differs" in report["message"]`；L148断言`f"/{entity}/{field}/" in report["message"]`。 调用`generate_basic`、`customer_plan`、`path.read_text`、`path.write_text`、`source.replace`、`execute`、`json.loads`、`result.stdout.splitlines`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_matrix_rejects_broken_and_or_row_scope`（L154–L179）：接收`tmp_path`、`fault`。 控制顺序：L161按`fault in {"ignored_combined_filter", "keyword_requires_full_value"}`分支；L174断言`before in source`；L178断言`result.returncode == 1 and report["passed"] is False`；L179断言`"Query matrix differs" in report["message"]`。 调用`generate_basic`、`customer_plan`、`path.read_text`、`path.write_text`、`source.replace`、`execute`、`json.loads`、`result.stdout.splitlines`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_query_api.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L179。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7552`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_query_api.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e38c7542eb3a2216a043ad3831453eb4decfcac100d16b3737179845437c2fc1"} -->
````python
# tests/test_business_query_api.py
"""Generated HTTP query matrices and real implementation faults, never model substitutes."""

import json

import pytest
from test_business_acceptance_evidence import customer_plan, execute
from test_business_python import runtime_plan

from workbench.domain import Plan
from workbench.generator import generate_basic
from workbench.verification import require_business_evidence


def test_customer_api_query_matrix_is_field_specific_and_role_scoped(tmp_path):
    plan = customer_plan()
    product = tmp_path / "product"
    generate_basic(
        plan, product, {"template": "python-basic", "frontend": "api-only", "database": "sqlite"}
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    proof = report["business"]["evidence"]["query_matrix"]
    assert "business-query-matrix" in report["business"]["checks"]
    for entity in plan.entities:
        for field in entity.fields:
            if field.searchable:
                records = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"]) == (entity.name, field.name, "keyword")
                ]
                assert records and all(p["other_matches"] == 0 for p in records)
                assert any(p["isolated_matches"] > 0 for p in records)
            if field.filterable:
                records = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"])
                    == (entity.name, field.name, "exact_filter")
                ]
                assert records and all(
                    p["positive_matches"] > 0 and p["excluded_records"] > 0 for p in records
                )
                combined = [
                    p
                    for p in proof
                    if (p["entity"], p["field"], p["kind"]) == (entity.name, field.name, "combined")
                ]
                assert combined and all(p["excluded_records"] > 0 for p in combined)
    assert all(p["foreign_matches"] > 0 for p in proof if p["scope"] != "all")
    assert all(p["cases"] == 2 and p["exact_results"] and p["role_scope"] for p in proof)
    assert len(json.dumps(proof).encode()) < 20000
    assert not any(
        key in json.dumps(proof) for key in ("expected_ids", "params", "Bearer", "password")
    )


FLAGGED_FIELDS = [
    (entity.name, field.name, "keyword" if field.searchable else "exact_filter")
    for entity in customer_plan().entities
    for field in entity.fields
    if field.searchable or field.filterable
]


@pytest.mark.parametrize("maximum", [8, 2])
def test_bounded_integer_query_controls_use_valid_values_including_singleton(tmp_path, maximum):
    raw = runtime_plan().model_dump()
    raw["entities"][0]["fields"].append(
        {
            "name": "quantity",
            "kind": "integer",
            "required": True,
            "minimum": 2,
            "maximum": maximum,
            "filterable": True,
        }
    )
    product = tmp_path / "product"
    plan = Plan.model_validate(raw)
    generate_basic(
        plan,
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout.splitlines()[-1])
    require_business_evidence(plan.model_dump(), report, False)
    evidence = report["business"]["evidence"]
    validation = next(item for item in evidence["field_validation"] if item["field"] == "quantity")
    assert validation["minimum"] == 2 and validation["maximum"] == maximum
    assert validation["below_minimum_rejected"] and validation["above_maximum_rejected"]
    controls = [item for item in evidence["query_matrix"] if item["field"] == "quantity"]
    assert controls and all(
        item["positive_matches"] > 0 and item["excluded_records"] > 0 for item in controls
    )


@pytest.mark.parametrize("maximum", [1, 2])
def test_short_keyword_fields_keep_independent_positive_controls(tmp_path, maximum):
    raw = runtime_plan().model_dump()
    raw["entities"][0]["fields"].append(
        {
            "name": "short_code",
            "kind": "text",
            "required": True,
            "max_length": maximum,
            "searchable": True,
        }
    )
    product = tmp_path / "product"
    generate_basic(
        Plan.model_validate(raw),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    result = execute(product)
    assert result.returncode == 0, result.stdout + result.stderr
    proof = json.loads(result.stdout.splitlines()[-1])["business"]["evidence"]["query_matrix"]
    short = [entry for entry in proof if entry["field"] == "short_code"]
    assert short and all(entry["isolated_matches"] > 0 for entry in short)


@pytest.mark.parametrize("entity,field,kind", FLAGGED_FIELDS)
def test_query_matrix_rejects_each_disabled_declared_query_field(tmp_path, entity, field, kind):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    path = product / "querying.py"
    source = path.read_text(encoding="utf-8")
    if kind == "keyword":
        before = 'if field.get("searchable")'
        after = f'if field.get("searchable") and not (entity["name"] == {entity!r} and name == {field!r})'
    else:
        before = "if key in query:"
        after = f'if key in query and not (entity["name"] == {entity!r} and name == {field!r}):'
    assert before in source
    path.write_text(source.replace(before, after), encoding="utf-8")
    result = execute(product)
    report = json.loads(result.stdout.splitlines()[-1])
    assert result.returncode == 1 and report["passed"] is False, report
    assert "Query matrix differs" in report["message"], report
    assert f"/{entity}/{field}/" in report["message"], report


@pytest.mark.parametrize(
    "fault", ["ignored_combined_filter", "query_scope_bypass", "keyword_requires_full_value"]
)
def test_query_matrix_rejects_broken_and_or_row_scope(tmp_path, fault):
    product = tmp_path / "product"
    generate_basic(
        customer_plan(),
        product,
        {"template": "python-basic", "frontend": "api-only", "database": "sqlite"},
    )
    if fault in {"ignored_combined_filter", "keyword_requires_full_value"}:
        path = product / "querying.py"
        source = path.read_text(encoding="utf-8")
        before, after = (
            ("if key in query:", 'if key in query and not query.get("q"):')
            if fault == "ignored_combined_filter"
            else ("table.c[name].icontains(q, autoescape=True)", "table.c[name].ilike(q)")
        )
    else:
        path = product / "business_runtime.py"
        source = path.read_text(encoding="utf-8")
        before = 'expressions += [target.c.archived_at.is_(None), *scope(actor, entity, "read")]'
        after = 'expressions += [target.c.archived_at.is_(None), *([] if request.query_params.get("q") else scope(actor, entity, "read"))]'
    assert before in source
    path.write_text(source.replace(before, after), encoding="utf-8")
    result = execute(product)
    report = json.loads(result.stdout.splitlines()[-1])
    assert result.returncode == 1 and report["passed"] is False, report
    assert "Query matrix differs" in report["message"], report
````
