# tests/test_requirement_clause_semantics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_contracts`、`workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `diagnostic_case`（L27–L34）：接收`template`。 控制顺序：L29断言`data["approval_status"] == "unapproved"`；L30断言`data["execution_authorized"] is False`；L31断言`data["purpose"] == "offline_contract_validation_only"`。 调用`json.loads`、`(FIXTURES / f"{template}-unapproved-design.json").read_bytes`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L32的`Requirement.model_validate(data["requirement"]), Plan.model_validate( data["candidate_plan…`。
- `test_diagnostic_inputs_and_original_failures_are_byte_exact`（L38–L39）：接收`filename`、`expected`。 控制顺序：L39断言`hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest() == expected`。 调用`hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest`、`hashlib.sha256`、`(FIXTURES / filename).read_bytes`、`pytest.mark.parametrize`、`HASHES.items`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_python_candidate_validates_without_modifying_approved_intent_or_candidate`（L42–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L46断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L47断言`diagnostics == []`；L48断言`(requirement.model_dump(), plan.model_dump()) == original`；L51断言`[(d["code"], d["source"]["index"]) for d in original_sources] == [ ("missing_metric_p…`。 调用`diagnostic_case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`json.loads`、`(FIXTURES / "python-summary.json").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_python_candidate_still_rejects_genuine_contract_changes`（L60–L86）：接收`mutation`。 控制顺序：L62按`mutation == "missing_field"`分支；L64按`mutation == "forbidden_field"`分支；L72按`mutation == "filter"`分支；L74按`mutation == "value"`分支；L76按`mutation == "kind"`分支；L81断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L82按`mutation not in {"missing_field", "forbidden_field"}`分支；L83断言`any( d["code"] == "missing_metric_predicate" and d["source"]["index"] == 7 for d in d…`。 调用`diagnostic_case`、`plan.entities[0].fields.pop`、`plan.entities[0].fields.append`、`FieldSpec`、`next`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_untouched_yudao_candidate_retains_exactly_seven_real_typed_search_conflicts`（L89–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L93断言`len(coverage_gaps(requirement, plan, diagnostics=diagnostics)) == 7`；L94断言`{d["source"]["index"] for d in diagnostics} == {6, 7, 8, 11, 14, 15, 16}`；L95断言`all( d["code"] == "constraint_mismatch" and d["source"]["section"] == "field_requirem…`；L103断言`(requirement.model_dump(), plan.model_dump()) == original`。 调用`diagnostic_case`、`requirement.model_dump`、`plan.model_dump`、`len`、`coverage_gaps`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_synthetic_yudao_correction_obeys_original_typed_flags_without_mutating_fixture`（L106–L123）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L110遍历`requirement.field_requirements`；L111按`obligation.searchable is False`分支；L112遍历`corrected.entities`；L113遍历`entity.fields`；L114按`entity.name == obligation.entity and field.name == obligation.field`分支；L116断言`coverage_gaps(requirement, corrected) == []`；L117断言`recorded.model_dump() == original`；L120断言`coverage_gaps(requirement, corrected, diagnostics=diagnostics)`。后续分支沿下方源码相同行号继续阅读。 调用`diagnostic_case`、`recorded.model_dump`、`recorded.model_copy`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `generic_case`（L126–L207）：接收`text`、`section`。 控制顺序：L203按`section == "facts"`分支。 调用`Plan`、`deepcopy`、`Requirement`、`setattr`。 返回路径：L207的`requirement, plan`。
- `test_explicit_absence_is_not_a_positive_field_declaration`（L224–L230）：接收`section`、`text`。 控制顺序：L226断言`coverage_gaps(requirement, plan) == []`；L229断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L230断言`any(d["code"] == "forbidden_field" for d in diagnostics)`。 调用`generic_case`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exclusion_scope_does_not_forbid_same_field_on_another_entity`（L233–L238）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L236断言`coverage_gaps(requirement, plan) == []`；L238断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`plan.entities[1].fields.append`、`FieldSpec`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exclusion_does_not_erase_adjacent_positive_requirement`（L242–L248）：接收`separator`。 控制顺序：L244断言`coverage_gaps(requirement, plan) == []`；L246断言`coverage_gaps(requirement, plan)`；L248断言`any("body" in g for g in coverage_gaps(requirement, plan))`。 调用`generic_case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nullable_value_and_query_negations_do_not_prohibit_a_field`（L261–L268）：接收`text`。 控制顺序：L266断言`not any(d["code"] == "forbidden_field" for d in diagnostics)`；L267按`"不允许为空" not in text`分支；L268断言`not diagnostics`。 调用`generic_case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_multimetric_lists_bind_only_local_kind_entity_and_predicates`（L273–L289）：接收`separator`、`section`。 控制顺序：L284断言`coverage_gaps(requirement, plan) == []`；L287断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L288断言`all(d["code"] == "missing_metric_predicate" for d in diagnostics)`；L289断言`all(t["field"] == "state" for d in diagnostics for t in d["targets"])`。 调用`separator.join`、`generic_case`、`coverage_gaps`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_a_neighboring_metric_cannot_satisfy_changed_local_predicate`（L293–L308）：接收`mutation`。 控制顺序：L298按`mutation in {"entity", "kind"}`分支；L300按`mutation == "filters"`分支；L308断言`any("业务指标" in g for g in coverage_gaps(requirement, plan))`。 调用`generic_case`、`setattr`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_predicates_for_one_metric_must_coexist_on_that_metric`（L312–L327）：接收`separator`。 控制顺序：L325断言`coverage_gaps(requirement, plan)`；L327断言`coverage_gaps(requirement, plan) == []`。 调用`generic_case`、`plan.business.metrics.append`、`MetricSpec`、`coverage_gaps`、`plan.business.metrics[0].filters.append`、`MetricPredicate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_predicates_do_not_cross_a_new_metric_or_sentence_boundary`（L330–L349）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L343断言`coverage_gaps(requirement, plan) == []`；L345断言`coverage_gaps(requirement, plan)`；L347断言`coverage_gaps(requirement, plan) == []`；L349断言`any("filterable" in g for g in coverage_gaps(requirement, plan))`。 调用`generic_case`、`plan.business.metrics.append`、`MetricSpec`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_null_predicate_preserves_literal_type`（L353–L359）：接收`value`。 控制顺序：L357断言`coverage_gaps(requirement, plan) == []`；L359断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`MetricPredicate`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inventory_does_not_donate_fields_to_a_new_explicit_query_subject`（L364–L384）：接收`entity`、`intro`。 控制顺序：L371断言`coverage_gaps(requirement, plan) == []`；L375断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L376断言`any( d["attribute"] == "searchable" and d["targets"] == [{"entity": entity, "field": …`；L384断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`FieldRequirement`、`coverage_gaps`、`next`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bare_field_target_inventory_keeps_its_shared_affirmative_predicate`（L387–L391）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L389断言`coverage_gaps(requirement, plan)`；L391断言`coverage_gaps(requirement, plan) == []`。 调用`generic_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_arbitrary_excluded_field_identifiers_are_enforced`（L395–L399）：接收`name`。 控制顺序：L397断言`coverage_gaps(requirement, plan) == []`；L399断言`any("已禁止" in gap for gap in coverage_gaps(requirement, plan))`。 调用`generic_case`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_field_requirement_and_exclusion_conflict_cannot_be_erased`（L402–L409）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L407断言`coverage_gaps(requirement, plan)`；L409断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`FieldRequirement`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_not_required_is_an_optional_field_constraint_not_field_absence`（L412–L416）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L414断言`coverage_gaps(requirement, plan)`；L416断言`coverage_gaps(requirement, plan) == []`。 调用`generic_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_predicate_values_are_not_entity_or_clause_subjects`（L420–L425）：接收`value`。 控制顺序：L423断言`coverage_gaps(requirement, plan) == []`；L425断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`MetricPredicate`、`value.strip`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_one_metric_cannot_satisfy_predicates_on_two_explicit_entities`（L428–L430）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L430断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_absence_keeps_trailing_date_descriptor_negative`（L441–L445）：接收`text`。 控制顺序：L443断言`coverage_gaps(requirement, plan) == []`；L445断言`any("已禁止" in gap for gap in coverage_gaps(requirement, plan))`。 调用`generic_case`、`coverage_gaps`、`plan.entities[0].fields.append`、`FieldSpec`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_heading_continues_across_two_exclusion_clauses`（L448–L453）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L451断言`coverage_gaps(requirement, plan) == []`；L453断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`plan.entities[1].fields.append`、`FieldSpec`、`coverage_gaps`、`plan.entities[0].fields.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_fact_exclusion_retains_its_entity_namespace`（L456–L462）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L460断言`coverage_gaps(requirement, plan) == []`；L462断言`coverage_gaps(requirement, plan)`。 调用`generic_case`、`plan.entities[1].fields.append`、`FieldSpec`、`coverage_gaps`、`plan.entities[0].fields.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_and_display_locations_are_not_schema_exclusions`（L475–L478）：接收`text`。 控制顺序：L478断言`coverage_gaps(requirement, plan) == []`。 调用`generic_case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_schema_location_still_forbids_field_even_before_other_query_prose`（L482–L489）：接收`location`。 控制顺序：L488断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L489断言`any(d["code"] == "forbidden_field" for d in diagnostics)`。 调用`generic_case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_negative_query_membership_still_enforces_disabled_capability`（L500–L512）：接收`text`、`attribute`。 控制顺序：L503断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L504断言`all( d["code"] == "constraint_mismatch" and d["attribute"] == attribute and d["expect…`；L512断言`coverage_gaps(requirement, plan) == []`。 调用`generic_case`、`coverage_gaps`、`all`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_requirement_clause_semantics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L512。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21580`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_requirement_clause_semantics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "618ac17ed366ae333c032a8ba1fab0eb0e40990112d8be25118f840c43e98051"} -->
````python
# tests/test_requirement_clause_semantics.py
"""Clause-local intent: exclusions, metric predicates, and explicit query subjects.

Recorded candidates below are unapproved diagnostic inputs for pure validation.
They must never be generated from, executed, or substituted for provider output.
"""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from workbench.business_contracts import MetricPredicate, MetricSpec
from workbench.domain import FieldRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps

FIXTURES = Path(__file__).parent / "fixtures/customer_design_diagnostics/0e8ebdd"
HASHES = {
    "python-unapproved-design.json": "a492b0e6e379b6062698bfde77b05a52ba81aab7e7b47d2a84e15e5173fd7ab6",
    "python-summary.json": "b64b86827ef6ecd63df33ca9fdb3c08ac9b2b9917adc2f32a9e1f1871159f929",
    "yudao-unapproved-design.json": "dd7bf0dbe805ae9d1527b899bd014fd87e1c69179b2134748cdf7d49b0d7c115",
    "yudao-summary.json": "755265754504037327c38c643592894c51cd9789ac399023f1037b6b299c5631",
}


def diagnostic_case(template):
    data = json.loads((FIXTURES / f"{template}-unapproved-design.json").read_bytes())
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


@pytest.mark.parametrize("filename,expected", HASHES.items())
def test_diagnostic_inputs_and_original_failures_are_byte_exact(filename, expected):
    assert hashlib.sha256((FIXTURES / filename).read_bytes()).hexdigest() == expected


def test_actual_python_candidate_validates_without_modifying_approved_intent_or_candidate():
    requirement, plan = diagnostic_case("python")
    original = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert (requirement.model_dump(), plan.model_dump()) == original
    summary = json.loads((FIXTURES / "python-summary.json").read_bytes())
    original_sources = summary["failure_details"]["coverage_sources"]
    assert [(d["code"], d["source"]["index"]) for d in original_sources] == [
        ("missing_metric_predicate", 7),
        ("legacy_missing_field", 10),
    ]


@pytest.mark.parametrize(
    "mutation", ["missing_field", "forbidden_field", "filter", "kind", "entity", "value"]
)
def test_actual_python_candidate_still_rejects_genuine_contract_changes(mutation):
    requirement, plan = diagnostic_case("python")
    if mutation == "missing_field":
        plan.entities[0].fields.pop(0)
    elif mutation == "forbidden_field":
        plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    else:
        metric = next(
            m
            for m in plan.business.metrics
            if m.entity == "requests" and m.kind == "count" and m.filters
        )
        if mutation == "filter":
            metric.filters = []
        elif mutation == "value":
            metric.filters[0].value = "active"
        elif mutation == "kind":
            metric.kind = "average_duration"
        else:
            metric.entity = "tasks"
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    if mutation not in {"missing_field", "forbidden_field"}:
        assert any(
            d["code"] == "missing_metric_predicate" and d["source"]["index"] == 7
            for d in diagnostics
        )


def test_untouched_yudao_candidate_retains_exactly_seven_real_typed_search_conflicts():
    requirement, plan = diagnostic_case("yudao")
    original = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert len(coverage_gaps(requirement, plan, diagnostics=diagnostics)) == 7
    assert {d["source"]["index"] for d in diagnostics} == {6, 7, 8, 11, 14, 15, 16}
    assert all(
        d["code"] == "constraint_mismatch"
        and d["source"]["section"] == "field_requirements"
        and d["attribute"] == "searchable"
        and d["expected"] is False
        and d["actual"] is True
        for d in diagnostics
    )
    assert (requirement.model_dump(), plan.model_dump()) == original


def test_synthetic_yudao_correction_obeys_original_typed_flags_without_mutating_fixture():
    requirement, recorded = diagnostic_case("yudao")
    original = recorded.model_dump()
    corrected = recorded.model_copy(deep=True)
    for obligation in requirement.field_requirements:
        if obligation.searchable is False:
            for entity in corrected.entities:
                for field in entity.fields:
                    if entity.name == obligation.entity and field.name == obligation.field:
                        field.searchable = False
    assert coverage_gaps(requirement, corrected) == []
    assert recorded.model_dump() == original
    corrected.entities[1].fields[0].searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, corrected, diagnostics=diagnostics)
    assert any(
        d["code"] == "uncovered_operation" and d["source"]["index"] == 2 for d in diagnostics
    )


def generic_case(text="", section="features"):
    fields = [
        {"name": "title", "kind": "text", "searchable": True},
        {"name": "detail", "kind": "text", "searchable": True},
        {"name": "assignee_id", "kind": "text", "required": False},
        {"name": "state", "kind": "enum", "choices": ["done", "open"], "filterable": False},
        {"name": "priority", "kind": "enum", "choices": ["high", "low"], "filterable": True},
        {"name": "finished_at", "kind": "datetime", "required": False},
        {"name": "category", "kind": "text"},
        {"name": "quantity", "kind": "integer"},
    ]
    plan = Plan(
        title="Operations",
        data_scope="shared",
        acceptance=["Save operations"],
        entities=[
            {"name": e, "description": e, "fields": deepcopy(fields)}
            for e in ("records", "batches")
        ],
        business={
            "roles": [
                {"name": "operator", "label": "Operator"},
                {"name": "administrator", "label": "Administrator"},
            ],
            "registration": {"enabled": False, "default_role": "operator"},
            "bootstrap_role": "administrator",
            "role_admin_roles": ["administrator"],
            "resources": [{"entity": e} for e in ("records", "batches")],
            "permissions": [
                {
                    "role": "operator",
                    "entity": e,
                    "scope": "all",
                    "actions": ["read", "read_metrics"],
                }
                for e in ("records", "batches")
            ],
            "metrics": [
                {
                    "name": "done",
                    "label": "Done",
                    "entity": "records",
                    "kind": "count",
                    "filters": [{"field": "state", "value": "done"}],
                },
                {
                    "name": "duration",
                    "label": "Duration",
                    "entity": "records",
                    "kind": "average_duration",
                    "start_field": "created_at",
                    "end_field": "finished_at",
                    "filters": [
                        {"field": "state", "value": "done"},
                        {"field": "finished_at", "op": "ne", "value": None},
                    ],
                },
                {
                    "name": "groups",
                    "label": "Groups",
                    "entity": "batches",
                    "kind": "group_count",
                    "group_by": "category",
                },
                {
                    "name": "daily",
                    "label": "Daily",
                    "entity": "records",
                    "kind": "time_count",
                    "time_field": "created_at",
                },
            ],
        },
    )
    requirement = Requirement(
        summary="Operations", users=["operator"], data_scope="shared", features=[], acceptance=[]
    )
    if section == "facts":
        requirement.facts = {"notes": text}
    else:
        setattr(requirement, section, [text] if text else [])
    return requirement, plan


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize(
    "text",
    [
        "不出现 published_on 或其他示例字段。",
        "records：不应包含 published_on 字段。",
        "records：禁止添加 published_on。",
        "records：published_on 字段不得出现。",
        "records: do not include published_on",
        "records: published_on must not be included",
        "records: exclude published_on and body",
        "records：不出现 published_on，但 title 必填且支持 title/detail 搜索。",
    ],
)
def test_explicit_absence_is_not_a_positive_field_declaration(section, text):
    requirement, plan = generic_case(text, section)
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["code"] == "forbidden_field" for d in diagnostics)


def test_exclusion_scope_does_not_forbid_same_field_on_another_entity():
    requirement, plan = generic_case("records：不出现 published_on")
    plan.entities[1].fields.append(FieldSpec(name="published_on", kind="date"))
    assert coverage_gaps(requirement, plan) == []
    requirement.features = ["不出现 published_on"]
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize("separator", ["，", ";", "，但", " and ", "、"])
def test_exclusion_does_not_erase_adjacent_positive_requirement(separator):
    requirement, plan = generic_case(f"records：不出现 published_on{separator}title 必填")
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = False
    assert coverage_gaps(requirement, plan)
    requirement.features = [f"records：不出现 published_on{separator}body 必填"]
    assert any("body" in g for g in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text",
    [
        "records：published_on 非必填",
        "records: published_on is not required",
        "records：published_on 不允许为空",
        "records：published_on 不参与搜索",
        "records: search criteria do not include published_on",
    ],
)
def test_nullable_value_and_query_negations_do_not_prohibit_a_field(text):
    requirement, plan = generic_case(text)
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date", required=False))
    diagnostics = []
    coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert not any(d["code"] == "forbidden_field" for d in diagnostics)
    if "不允许为空" not in text:
        assert not diagnostics


@pytest.mark.parametrize("separator", ["、", "，", ";", " and ", "；"])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_multimetric_lists_bind_only_local_kind_entity_and_predicates(separator, section):
    text = separator.join(
        [
            "统计 records 总数",
            "records 按 state=done 筛选的已解决数",
            "records 由 created_at 至 finished_at 计算的平均时长（秒）",
            "batches 按 category 分组计数",
            "records 按 created_at 的每日趋势",
        ]
    )
    requirement, plan = generic_case(text, section)
    assert coverage_gaps(requirement, plan) == []
    plan.business.metrics[0].filters = []
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(d["code"] == "missing_metric_predicate" for d in diagnostics)
    assert all(t["field"] == "state" for d in diagnostics for t in d["targets"])


@pytest.mark.parametrize("mutation", ["kind", "entity", "value", "op", "field", "filters"])
def test_a_neighboring_metric_cannot_satisfy_changed_local_predicate(mutation):
    requirement, plan = generic_case(
        "records count 按 state=done 筛选、batches group_count 按 category 分组"
    )
    metric = plan.business.metrics[0]
    if mutation in {"entity", "kind"}:
        setattr(metric, mutation, "batches" if mutation == "entity" else "average_duration")
    elif mutation == "filters":
        metric.filters = []
    else:
        setattr(
            metric.filters[0],
            mutation,
            {"value": "open", "op": "ne", "field": "priority"}[mutation],
        )
    assert any("业务指标" in g for g in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("separator", ["、", ", ", " and ", "和"])
def test_all_predicates_for_one_metric_must_coexist_on_that_metric(separator):
    requirement, plan = generic_case(
        "records count filter state=done" + separator + "priority=high"
    )
    plan.business.metrics.append(
        MetricSpec(
            name="other",
            label="Other",
            entity="records",
            kind="count",
            filters=[{"field": "priority", "value": "high"}],
        )
    )
    assert coverage_gaps(requirement, plan)
    plan.business.metrics[0].filters.append(MetricPredicate(field="priority", value="high"))
    assert coverage_gaps(requirement, plan) == []


def test_predicates_do_not_cross_a_new_metric_or_sentence_boundary():
    requirement, plan = generic_case(
        "records count filter state=done、batches count filter state=open"
    )
    plan.business.metrics.append(
        MetricSpec(
            name="batch_open",
            label="Batch open",
            entity="batches",
            kind="count",
            filters=[{"field": "state", "value": "open"}],
        )
    )
    assert coverage_gaps(requirement, plan) == []
    plan.business.metrics[-1].filters = []
    assert coverage_gaps(requirement, plan)
    requirement.features = ["records count filter state=done；records: priority 筛选"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[4].filterable = False
    assert any("filterable" in g for g in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("value", [None, "null"])
def test_null_predicate_preserves_literal_type(value):
    literal = "null" if value is None else '"null"'
    requirement, plan = generic_case(f"records average_duration filter finished_at!={literal}")
    plan.business.metrics[1].filters = [MetricPredicate(field="finished_at", op="ne", value=value)]
    assert coverage_gaps(requirement, plan) == []
    plan.business.metrics[1].filters[0].value = "null" if value is None else None
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize("entity", ["records", "batches"])
@pytest.mark.parametrize("intro", ["支持", "允许", "requires ", "supports "])
def test_inventory_does_not_donate_fields_to_a_new_explicit_query_subject(entity, intro):
    requirement, plan = generic_case(
        f"{entity}：字段含 title、detail、assignee_id、state、finished_at、priority，{intro}title/detail 关键词搜索与 priority 精确筛选"
    )
    requirement.field_requirements = [
        FieldRequirement(entity=entity, field="assignee_id", searchable=False)
    ]
    assert coverage_gaps(requirement, plan) == []
    target = next(e for e in plan.entities if e.name == entity)
    target.fields[0].searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["attribute"] == "searchable"
        and d["targets"]
        == [{"entity": entity, "field": "title"}, {"entity": entity, "field": "detail"}]
        for d in diagnostics
    )
    target.fields[0].searchable = True
    target.fields[4].filterable = False
    assert coverage_gaps(requirement, plan)


def test_bare_field_target_inventory_keeps_its_shared_affirmative_predicate():
    requirement, plan = generic_case("records：title、detail、assignee_id 都支持搜索")
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[2].searchable = True
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("name", ["obsolete_ref", "legacy_on"])
def test_arbitrary_excluded_field_identifiers_are_enforced(name):
    requirement, plan = generic_case(f"records：不出现 {name}")
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name=name, kind="text"))
    assert any("已禁止" in gap for gap in coverage_gaps(requirement, plan))


def test_explicit_field_requirement_and_exclusion_conflict_cannot_be_erased():
    requirement, plan = generic_case("records：不出现 category")
    requirement.field_requirements = [
        FieldRequirement(entity="records", field="category", required=True)
    ]
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields = [f for f in plan.entities[0].fields if f.name != "category"]
    assert coverage_gaps(requirement, plan)


def test_not_required_is_an_optional_field_constraint_not_field_absence():
    requirement, plan = generic_case("records: title is not required")
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].required = False
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("value", ['"batches"', "batches", '"batch,and,records"'])
def test_metric_predicate_values_are_not_entity_or_clause_subjects(value):
    requirement, plan = generic_case(f"records count filter category={value}")
    plan.business.metrics[0].filters = [MetricPredicate(field="category", value=value.strip('"'))]
    assert coverage_gaps(requirement, plan) == []
    plan.business.metrics[0].entity = "batches"
    assert coverage_gaps(requirement, plan)


def test_one_metric_cannot_satisfy_predicates_on_two_explicit_entities():
    requirement, plan = generic_case("count filter records.state=done and batches.state=done")
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text",
    [
        "records：不出现 published_on 真实日期字段",
        "records: do not include published_on date field",
        "records：不应添加 published_on（真实日期字段）",
    ],
)
def test_field_absence_keeps_trailing_date_descriptor_negative(text):
    requirement, plan = generic_case(text)
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    assert any("已禁止" in gap for gap in coverage_gaps(requirement, plan))


def test_entity_heading_continues_across_two_exclusion_clauses():
    requirement, plan = generic_case("records：不出现 published_on；不出现 body")
    plan.entities[1].fields.append(FieldSpec(name="body", kind="text"))
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="body", kind="text"))
    assert coverage_gaps(requirement, plan)


def test_nested_fact_exclusion_retains_its_entity_namespace():
    requirement, plan = generic_case()
    requirement.facts = {"records": {"notes": "不出现 published_on"}}
    plan.entities[1].fields.append(FieldSpec(name="published_on", kind="date"))
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text",
    [
        "records: published_on must not appear in search results",
        "records: do not include published_on in filters",
        "records: published_on must not appear in the UI",
        "records：列表中不得出现 published_on",
        "records：published_on 不得出现在列表中",
    ],
)
def test_query_and_display_locations_are_not_schema_exclusions(text):
    requirement, plan = generic_case(text)
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("location", ["schema", "entities"])
def test_explicit_schema_location_still_forbids_field_even_before_other_query_prose(location):
    requirement, plan = generic_case(
        f"records: do not include published_on in {location}, and supports title search"
    )
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["code"] == "forbidden_field" for d in diagnostics)


@pytest.mark.parametrize(
    "text,attribute",
    [
        ("records: do not include title in search criteria", "searchable"),
        ("records: do not include priority in filters", "filterable"),
        ("records: priority must not appear in filters", "filterable"),
    ],
)
def test_negative_query_membership_still_enforces_disabled_capability(text, attribute):
    requirement, plan = generic_case(text)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(
        d["code"] == "constraint_mismatch"
        and d["attribute"] == attribute
        and d["expected"] is False
        for d in diagnostics
    )
    target = plan.entities[0].fields[0 if attribute == "searchable" else 4]
    setattr(target, attribute, False)
    assert coverage_gaps(requirement, plan) == []
````
