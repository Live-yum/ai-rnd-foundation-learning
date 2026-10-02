# tests/test_business_query_evidence_contract.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_query_matrix_requires_exact_complete_unique_plan_targets`（L12–L27）：接收`section`、`mutation`。 控制顺序：L15按`mutation == "missing"`分支；L17按`mutation == "empty"`分支；L19按`mutation == "partial"`分支；L23按`mutation == "extra"`分支。 调用`receipt`、`report[section]["evidence"].pop`、`rows.clear`、`rows.pop`、`dict`、`rows.append`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_matrix_rejects_substitution_unbounded_or_non_typed_observations`（L56–L60）：接收`section`、`field`、`bad`。 调用`receipt`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_query_requires_executed_values_exact_sets_and_reset`（L67–L71）：接收`field`、`bad`。 调用`receipt`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_zero_only_query_cases_cannot_prove_declared_capability`（L84–L98）：接收`kind`、`count`。 控制顺序：L87遍历`("business", "browser")`；L88遍历`report[section]["evidence"]["query_matrix"]`；L89按`(row["entity"], row["field"], row["kind"]) == ( target["entity"], target["field"], ki…`分支；L95按`count == "positive_matches"`分支。 调用`receipt`、`next`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_zero_visible_rows_for_one_role_are_valid_without_inventing_access`（L101–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103遍历`("business", "browser")`；L104遍历`report[section]["evidence"]["query_matrix"]`；L105按`row["role"] == "employee" and row["entity"] == "requests"`分支。 调用`receipt`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_browser_counts_must_equal_independent_api_expectations`（L110–L114）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`receipt`、`pytest.raises`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_execution_marker_cannot_be_omitted`（L121–L125）：接收`section`、`marker`。 调用`receipt`、`report[section]["checks"].remove`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_proof_does_not_accept_raw_terms_or_record_ids`（L128–L133）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L129遍历`("business", "browser")`。 调用`receipt`、`pytest.raises`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_alternate_value_may_have_real_matches_without_weakening_exact_sets`（L136–L143）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L138遍历`("business", "browser")`。 调用`receipt`、`next`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_singleton_filter_has_no_legal_unequal_choice`（L146–L175）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L166遍历`("business", "browser")`；L168遍历`report[section]["evidence"]["query_matrix"]`；L169按`(row["entity"], row["field"], row["kind"]) == ( "customers", "category", "exact_filte…`分支。 调用`receipt`、`next`、`field["choice_labels"].items`、`digest`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_query_evidence_contract.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L175。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6382`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_query_evidence_contract.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "eae9516b6d642492c6ff73e5e9ed306f4cef6e128eefcc356bb88eb695d67eed"} -->
````python
# tests/test_business_query_evidence_contract.py
"""Exact per-field/role API and real-browser query proof cannot be omitted or forged."""

import pytest
from test_business_receipt import receipt

from workbench.generator import PrerequisiteError
from workbench.verification import require_business_evidence


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize("mutation", ["missing", "empty", "duplicate", "partial", "extra"])
def test_query_matrix_requires_exact_complete_unique_plan_targets(section, mutation):
    spec, report = receipt()
    rows = report[section]["evidence"]["query_matrix"]
    if mutation == "missing":
        report[section]["evidence"].pop("query_matrix")
    elif mutation == "empty":
        rows.clear()
    elif mutation == "partial":
        rows.pop()
    else:
        row = dict(rows[0])
        if mutation == "extra":
            row["field"] = "not_declared"
        rows.append(row)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize(
    "field,bad",
    [
        ("role", "unapproved_role"),
        ("entity", "unapproved_entity"),
        ("scope", "own"),
        ("field", "category"),
        ("kind", "unsupported"),
        ("keyword_field", "name"),
        ("cases", 1),
        ("cases", True),
        ("positive_matches", True),
        ("positive_matches", -1),
        ("positive_matches", 101),
        ("other_matches", 1),
        ("excluded_records", True),
        ("excluded_records", 201),
        ("foreign_matches", 1),
        ("foreign_matches", 201),
        ("isolated_matches", 101),
        ("exact_results", 1),
        ("exact_results", False),
        ("role_scope", False),
    ],
)
def test_query_matrix_rejects_substitution_unbounded_or_non_typed_observations(section, field, bad):
    spec, report = receipt()
    report[section]["evidence"]["query_matrix"][0][field] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "field", ["query_values_verified", "response_ids_exact", "rendered_ids_exact", "controls_reset"]
)
@pytest.mark.parametrize("bad", [False, 1, None])
def test_browser_query_requires_executed_values_exact_sets_and_reset(field, bad):
    spec, report = receipt()
    report["browser"]["evidence"]["query_matrix"][0][field] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "kind,count",
    [
        ("keyword", "isolated_matches"),
        ("keyword", "positive_matches"),
        ("exact_filter", "positive_matches"),
        ("combined", "positive_matches"),
        ("exact_filter", "excluded_records"),
    ],
)
def test_zero_only_query_cases_cannot_prove_declared_capability(kind, count):
    spec, report = receipt()
    target = next(r for r in report["business"]["evidence"]["query_matrix"] if r["kind"] == kind)
    for section in ("business", "browser"):
        for row in report[section]["evidence"]["query_matrix"]:
            if (row["entity"], row["field"], row["kind"]) == (
                target["entity"],
                target["field"],
                kind,
            ):
                row[count] = 0
                if count == "positive_matches":
                    row["isolated_matches"] = 0
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_zero_visible_rows_for_one_role_are_valid_without_inventing_access():
    spec, report = receipt()
    for section in ("business", "browser"):
        for row in report[section]["evidence"]["query_matrix"]:
            if row["role"] == "employee" and row["entity"] == "requests":
                row["positive_matches"] = row["other_matches"] = row["isolated_matches"] = 0
    require_business_evidence(spec, report, True)


def test_browser_counts_must_equal_independent_api_expectations():
    spec, report = receipt()
    report["browser"]["evidence"]["query_matrix"][0]["excluded_records"] += 1
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,marker",
    [("business", "business-query-matrix"), ("browser", "business-browser-query-matrix")],
)
def test_query_execution_marker_cannot_be_omitted(section, marker):
    spec, report = receipt()
    report[section]["checks"].remove(marker)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_query_proof_does_not_accept_raw_terms_or_record_ids():
    for section in ("business", "browser"):
        spec, report = receipt()
        report[section]["evidence"]["query_matrix"][0]["raw_query"] = "unneeded private term"
        with pytest.raises(PrerequisiteError):
            require_business_evidence(spec, report, True)


def test_combined_alternate_value_may_have_real_matches_without_weakening_exact_sets():
    spec, report = receipt()
    for section in ("business", "browser"):
        row = next(
            r for r in report[section]["evidence"]["query_matrix"] if r["kind"] == "combined"
        )
        row["other_matches"] = 1
    require_business_evidence(spec, report, True)


def test_required_singleton_filter_has_no_legal_unequal_choice():
    from workbench.domain import digest

    spec, report = receipt()
    field = next(
        f
        for e in spec["entities"]
        if e["name"] == "customers"
        for f in e["fields"]
        if f["name"] == "category"
    )
    field["choices"] = [field["choices"][0]]
    field["choice_labels"] = {
        k: v for k, v in field["choice_labels"].items() if k in field["choices"]
    }
    next(
        p
        for p in report["business"]["evidence"]["field_validation"]
        if (p["entity"], p["field"]) == ("customers", "category")
    )["declared_choices"] = 1
    for section in ("business", "browser"):
        report[section]["spec_digest"] = digest(spec)
        for row in report[section]["evidence"]["query_matrix"]:
            if (row["entity"], row["field"], row["kind"]) == (
                "customers",
                "category",
                "exact_filter",
            ):
                row["excluded_records"] = 0
    require_business_evidence(spec, report, True)
````
