# tests/test_business_evidence_contract.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `integer_receipt`（L11–L34）：接收`constraints`、`required`、`low`、`high`。 源码说明：Independent unit receipt values; never a model or live execution substitute.。 控制顺序：L29按`required`分支；L32遍历`("business", "browser")`。 调用`receipt`、`entity["fields"].append`、`FieldSpec(name="quantity", kind="integer", required=required, **c…`、`FieldSpec`、`proof.update`、`report["business"]["evidence"]["field_validation"].append`、`digest`。 返回路径：L34的`spec, report, proof`。
- `test_integer_proof_matches_effective_approved_domain_and_all_negative_requests`（L52–L57）：接收`constraints`、`required`、`low`、`high`。 调用`integer_receipt`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_integer_proof_rejects_missing_wrong_or_unexecuted_boundaries`（L78–L85）：接收`key`、`bad`。 控制顺序：L80按`bad is None`分支。 调用`integer_receipt`、`proof.pop`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_delivery_requires_versioned_detailed_proof`（L90–L99）：接收`section`、`mutation`。 控制顺序：L92按`mutation == "missing"`分支；L94按`mutation == "empty"`分支。 调用`receipt`、`report[section].pop`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_detailed_proof_is_bound_to_plan_and_observed_counts`（L137–L141）：接收`section`、`proof`、`key`、`bad`。 调用`receipt`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_empty_or_duplicated_proof_sets_cannot_replace_required_work`（L163–L173）：接收`section`、`proof`、`mutation`。 控制顺序：L166按`mutation == "omit"`分支；L168按`mutation == "duplicate"`分支。 调用`receipt`、`values.append`、`dict`、`report[section]["evidence"].pop`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_required_update_or_enum_rejection_cannot_be_hidden_by_create_checks`（L176–L188）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L177遍历`( "invalid_updates_rejected", "invalid_enum_rejected", "protected…`。 调用`receipt`、`next`、`proof.pop`、`pytest.raises`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_evidence_contract.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L188。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7456`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_evidence_contract.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5554900b9e026b3337c8230b8ca0b00a263ae4a09fe4119e4cdb7be77c2f039f"} -->
````python
# tests/test_business_evidence_contract.py
"""Missing, substituted or partial detailed proof must never authorize delivery."""

import pytest
from test_business_receipt import receipt

from workbench.domain import FieldSpec, digest
from workbench.generator import PrerequisiteError
from workbench.verification import require_business_evidence


def integer_receipt(constraints, required, low, high):
    """Independent unit receipt values; never a model or live execution substitute."""
    spec, report = receipt()
    entity = spec["entities"][0]
    entity["fields"].append(
        FieldSpec(name="quantity", kind="integer", required=required, **constraints).model_dump()
    )
    proof = {
        "entity": entity["name"],
        "field": "quantity",
        "kind": "integer",
        "required": required,
        "minimum": low,
        "maximum": high,
        "below_minimum_rejected": True,
        "above_maximum_rejected": True,
        "invalid_updates_rejected": 3 if required else 2,
    }
    if required:
        proof.update(missing_required_rejected=True, null_rejected=True)
    report["business"]["evidence"]["field_validation"].append(proof)
    for section in ("business", "browser"):
        report[section]["spec_digest"] = digest(spec)
    return spec, report, proof


@pytest.mark.parametrize(
    "constraints,required,low,high",
    [
        ({}, True, -2147483648, 2147483647),
        ({"minimum": 0, "maximum": 100000}, True, 0, 100000),
        ({"exclusive_minimum": 0, "exclusive_maximum": 10}, True, 1, 9),
        (
            {"minimum": 2, "maximum": 8, "exclusive_minimum": 3, "exclusive_maximum": 7},
            True,
            4,
            6,
        ),
        ({"minimum": 0, "maximum": 10}, False, 0, 10),
    ],
)
def test_integer_proof_matches_effective_approved_domain_and_all_negative_requests(
    constraints, required, low, high
):
    spec, report, _ = integer_receipt(constraints, required, low, high)
    require_business_evidence(spec, report, True)
    require_business_evidence(spec, report, False)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("minimum", None),
        ("maximum", None),
        ("below_minimum_rejected", None),
        ("above_maximum_rejected", None),
        ("minimum", -1),
        ("maximum", 100001),
        ("minimum", False),
        ("maximum", 100000.0),
        ("below_minimum_rejected", False),
        ("above_maximum_rejected", 1),
        ("invalid_updates_rejected", 1),
        ("invalid_updates_rejected", 2),
        ("invalid_updates_rejected", 4),
    ],
)
def test_integer_proof_rejects_missing_wrong_or_unexecuted_boundaries(key, bad):
    spec, report, proof = integer_receipt({"minimum": 0, "maximum": 100000}, True, 0, 100000)
    if bad is None:
        proof.pop(key)
    else:
        proof[key] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize("section", ["business", "browser"])
@pytest.mark.parametrize("mutation", ["missing", "empty", "true_version", "wrong_version"])
def test_business_delivery_requires_versioned_detailed_proof(section, mutation):
    spec, report = receipt()
    if mutation == "missing":
        report[section].pop("evidence")
    elif mutation == "empty":
        report[section]["evidence"] = {}
    else:
        report[section]["evidence"]["version"] = True if mutation == "true_version" else 0
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,proof,key,bad",
    [
        ("business", "field_validation", "entity", "wrong_resource"),
        ("business", "field_validation", "missing_required_rejected", False),
        ("business", "field_validation", "max_length", 999),
        ("business", "field_validation", "over_max_length_rejected", 1),
        ("business", "field_validation", "invalid_updates_rejected", True),
        ("business", "related_views", "target_row_acl", False),
        ("business", "related_views", "role", "unknown_role"),
        ("business", "related_views", "target_entities", []),
        ("business", "relation_labels", "references_checked", True),
        ("business", "relation_labels", "readable_labels_verified", False),
        ("business", "datetime_policy", "searchable", True),
        ("business", "datetime_policy", "timestamp_stored", False),
        ("business", "datetime_policy", "undeclared_query_parameters_rejected", ["filter"]),
        ("business", "due_notifications", "past_due_events_verified", 0),
        ("business", "due_notifications", "past_due_events_verified", True),
        ("business", "due_notifications", "recipient", "other"),
        ("business", "due_notifications", "future_deadline_no_event", False),
        ("business", "due_notifications", "event_and_read_state_persisted_after_restart", False),
        ("business", "audit_immutability", "entries_checked", True),
        ("business", "audit_immutability", "mutation_delete_attempts_rejected", 0),
        ("business", "audit_immutability", "archive_and_restart_preserved", False),
        ("browser", "relation_labels", "list", False),
        ("browser", "relation_labels", "records_checked", True),
        ("browser", "related_sources", "groups_checked", True),
        ("browser", "related_sources", "source_records", 99),
        ("browser", "related_views", "target_acl", False),
        ("browser", "related_views", "visible_records", 99),
        ("browser", "related_views", "navigation", None),
        ("browser", "datetime_controls", "controls_absent", False),
        ("browser", "datetime_controls", "date_range", True),
    ],
)
def test_detailed_proof_is_bound_to_plan_and_observed_counts(section, proof, key, bad):
    spec, report = receipt()
    report[section]["evidence"][proof][0][key] = bad
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


@pytest.mark.parametrize(
    "section,proof",
    [
        ("business", name)
        for name in (
            "field_validation",
            "related_views",
            "relation_labels",
            "datetime_policy",
            "due_notifications",
            "audit_immutability",
        )
    ]
    + [
        ("browser", name)
        for name in ("relation_labels", "related_sources", "related_views", "datetime_controls")
    ],
)
@pytest.mark.parametrize("mutation", ["omit", "duplicate", "missing_list"])
def test_empty_or_duplicated_proof_sets_cannot_replace_required_work(section, proof, mutation):
    spec, report = receipt()
    values = report[section]["evidence"][proof]
    if mutation == "omit":
        report[section]["evidence"][proof] = []
    elif mutation == "duplicate":
        values.append(dict(values[0]))
    else:
        report[section]["evidence"].pop(proof)
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)


def test_missing_required_update_or_enum_rejection_cannot_be_hidden_by_create_checks():
    for attribute in (
        "invalid_updates_rejected",
        "invalid_enum_rejected",
        "protected_update_rejected",
    ):
        spec, report = receipt()
        proof = next(
            item for item in report["business"]["evidence"]["field_validation"] if attribute in item
        )
        proof.pop(attribute)
        with pytest.raises(PrerequisiteError):
            require_business_evidence(spec, report, True)
````
