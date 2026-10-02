# tests/test_entity_group_clause_scope.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recorded`（L21–L34）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23断言`len(raw) == 46721`；L24断言`hashlib.sha256(raw).hexdigest() == "fd69760f6ad7b4431b16a387e47ea29ee22dbea03f811199d…`；L29断言`envelope["approval_status"] == "unapproved"`；L30断言`envelope["execution_authorized"] is False`；L31断言`envelope["purpose"] == "offline_contract_validation_only"`。 调用`(FIXTURE / "python-unapproved-design.json").read_bytes`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L32的`Requirement.model_validate(envelope["requirement"]), Plan.model_validate( envelope["candid…`。
- `test_exact_recorded_requirement_and_candidate_validate_without_rewriting_either`（L37–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L41断言`coverage_gaps(requirement, plan, diagnostics=diagnostics) == []`；L42断言`diagnostics == []`；L43断言`(requirement.model_dump(), plan.model_dump()) == original`；L45断言`hashlib.sha256(raw).hexdigest() == "018c8f491895293e02f522fcce19a80f191df60ad302463bf…`；L50断言`len(source) == 1 and source[0]["code"] == "legacy_missing_field"`；L51断言`source[0]["source"] == {"section": "acceptance", "index": 1, "clause": 1}`。 调用`recorded`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`(FIXTURE / "python-summary.json").read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_group_cannot_hide_real_field_or_length_changes`（L58–L65）：接收`entity`、`field`、`mutation`。 控制顺序：L61按`mutation == "missing"`分支；L65断言`coverage_gaps(requirement, plan)`。 调用`recorded`、`next`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `case`（L68–L118）：接收`text`、`section`、`typed`。 控制顺序：L101按`typed`分支；L114按`section == "facts"`分支。 调用`Plan`、`Requirement`、`FieldRequirement`、`setattr`。 返回路径：L118的`requirement, plan`。
- `test_equivalent_entity_group_boundaries_preserve_independent_field_limits`（L136–L151）：接收`separator`、`group`、`section`。 控制顺序：L141断言`coverage_gaps(requirement, plan) == []`；L144断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L145断言`any( d["attribute"] == "max_length" and d["expected"] == 200 and d["targets"] == [{"e…`；L151断言`not any(t["entity"] == "alpha" for d in diagnostics for t in d["targets"])`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_each_group_member_has_its_own_positive_field_and_bound_obligation`（L166–L173）：接收`declaration`、`entity`、`field`。 控制顺序：L170断言`coverage_gaps(requirement, plan) == []`；L173断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_grouped_negation_never_leaks_to_previous_or_unrelated_entity`（L180–L191）：接收`separator`、`prohibition`。 控制顺序：L183断言`coverage_gaps(requirement, plan) == []`；L184遍历`[1, 2]`；L188断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L189断言`[d["targets"] for d in diagnostics if d["code"] == "forbidden_field"] == [ [{"entity"…`。 调用`case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`、`plan.model_copy`、`changed.entities[entity].fields.append`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_single_entity_switch_resets_group_and_prior_namespace`（L195–L201）：接收`separator`。 控制顺序：L199断言`coverage_gaps(requirement, plan) == []`；L201断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unqualified_continuation_retains_explicit_group_until_next_subject`（L204–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L208断言`coverage_gaps(requirement, plan) == []`；L210断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_coordinated_qualified_fields_keep_each_owner_and_shared_predicate`（L214–L225）：接收`separator`。 控制顺序：L216断言`coverage_gaps(requirement, plan) == []`；L217遍历`[("alpha", "title"), ("beta", "detail")]`；L222断言`coverage_gaps(requirement, changed)`；L225断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`plan.model_copy`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_entity_in_explicit_group_cannot_use_surviving_member_fields`（L228–L230）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L230断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_group_subjects_cannot_be_fabricated_from_adjacent_qualified_field_names`（L233–L240）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L235断言`coverage_gaps(requirement, plan) == []`；L237断言`all( not clause.startswith("title::") for clause in _legacy_clauses(requirement.featu…`。 调用`case`、`coverage_gaps`、`all`、`clause.startswith`、`_legacy_clauses`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_descriptions_never_become_new_requirement_obligations`（L243–L249）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L247断言`coverage_gaps(requirement, plan) == []`；L249断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compact_minimum_and_numeric_field_predicate_keep_distinct_meaning`（L252–L258）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L254断言`coverage_gaps(requirement, plan) == []`；L256断言`coverage_gaps(requirement, plan)`；L258断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requirement_only_projection_reuses_binder_and_preserves_raw_source_indices`（L261–L277）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L266断言`{(r["entity"], r["field"], r["attribute"], r["expected"]) for r in records} == { ("al…`；L273断言`all( r["source"]["section"] == "features" and r["source"]["index"] == 0 and r["text"]…`；L277断言`requirement.model_dump() == before`。 调用`case`、`requirement.model_dump`、`explicit_legacy_field_constraints`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requirement_only_projection_keeps_conflicts_and_does_not_infer_missing_vocabulary`（L280–L291）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L288断言`[r["expected"] for r in records] == [120, 200]`；L289断言`requirement.acceptance[-1] == "unknown max_length=5"`；L291断言`explicit_legacy_field_constraints(requirement) == []`。 调用`case`、`explicit_legacy_field_constraints`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requirement_only_projection_includes_reliably_typed_structured_facts`（L294–L307）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L300断言`{(r["entity"], r["field"], r["attribute"], r["expected"]) for r in records} == { ("be…`；L304断言`all( r["source"]["encoding"] == "structured" and r["source"]["path"] == "beta.fields.…`。 调用`case`、`explicit_legacy_field_constraints`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_scope_analysis_keeps_metric_conjunctions_in_the_metric_domain`（L310–L325）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L318断言`normalized == text and exclusions == []`；L320断言`len(metrics) == 1`；L321断言`metrics[0]["entity"] == "beta" and metrics[0]["kind"] == "count"`；L322断言`[(p["field"], p["op"], p["value"]) for p in metrics[0]["predicates"]] == [ ("quantity…`。 调用`case`、`_legacy_field_exclusions`、`_metric_clauses`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inline_entity_subject_does_not_scope_a_later_independent_query_summary`（L328–L337）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L335断言`coverage_gaps(requirement, plan) == []`；L337断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`plan.entities[0].fields.append`、`FieldSpec`、`plan.entities[1].fields.append`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_entity_group_clause_scope.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L337。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13636`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_entity_group_clause_scope.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4cbac39cb073a7b2a19cbc4d311098bea4dd190197300b6eb931b83007746f22"} -->
````python
# tests/test_entity_group_clause_scope.py
"""Explicit entity groups bind equivalent prose without donating prior namespaces."""

import hashlib
import json
from pathlib import Path

import pytest

from workbench.domain import FieldRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import (
    _legacy_clauses,
    _legacy_field_exclusions,
    _metric_clauses,
    coverage_gaps,
    explicit_legacy_field_constraints,
)

FIXTURE = Path(__file__).parent / "fixtures/customer_design_diagnostics/dd7e5f2"


def recorded():
    raw = (FIXTURE / "python-unapproved-design.json").read_bytes()
    assert len(raw) == 46721
    assert (
        hashlib.sha256(raw).hexdigest()
        == "fd69760f6ad7b4431b16a387e47ea29ee22dbea03f811199dc5f996f2456d642"
    )
    envelope = json.loads(raw)
    assert envelope["approval_status"] == "unapproved"
    assert envelope["execution_authorized"] is False
    assert envelope["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(envelope["requirement"]), Plan.model_validate(
        envelope["candidate_plan"]
    )


def test_exact_recorded_requirement_and_candidate_validate_without_rewriting_either():
    requirement, plan = recorded()
    original = requirement.model_dump(), plan.model_dump()
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics) == []
    assert diagnostics == []
    assert (requirement.model_dump(), plan.model_dump()) == original
    raw = (FIXTURE / "python-summary.json").read_bytes()
    assert (
        hashlib.sha256(raw).hexdigest()
        == "018c8f491895293e02f522fcce19a80f191df60ad302463bf1ee668b6a0ab7f5"
    )
    source = json.loads(raw)["failure_details"]["coverage_sources"]
    assert len(source) == 1 and source[0]["code"] == "legacy_missing_field"
    assert source[0]["source"] == {"section": "acceptance", "index": 1, "clause": 1}


@pytest.mark.parametrize(
    "entity,field", [(e, f) for e in ["requests", "tasks"] for f in ["title", "detail"]]
)
@pytest.mark.parametrize("mutation", ["length", "missing"])
def test_recorded_group_cannot_hide_real_field_or_length_changes(entity, field, mutation):
    requirement, plan = recorded()
    target = next(e for e in plan.entities if e.name == entity)
    if mutation == "missing":
        target.fields = [f for f in target.fields if f.name != field]
    else:
        next(f for f in target.fields if f.name == field).max_length = 120
    assert coverage_gaps(requirement, plan)


def case(text="", section="features", typed=False):
    plan = Plan(
        title="Inventory",
        data_scope="shared",
        acceptance=["Store inventory"],
        entities=[
            {
                "name": entity,
                "description": entity,
                "fields": [
                    {"name": "name", "kind": "text", "max_length": 120, "searchable": True},
                    {
                        "name": "title",
                        "kind": "text",
                        "max_length": 80 if entity == "alpha" else 200,
                        "min_length": 0 if entity == "alpha" else 1,
                        "searchable": True,
                    },
                    {
                        "name": "detail",
                        "kind": "text",
                        "max_length": 90 if entity == "alpha" else 3000,
                        "searchable": True,
                    },
                    {"name": "quantity", "kind": "integer"},
                ],
            }
            for entity in ["alpha", "beta", "gamma"]
        ],
    )
    requirement = Requirement(
        summary="Inventory", users=["staff"], data_scope="shared", features=[], acceptance=[]
    )
    if typed:
        requirement.field_requirements = [
            FieldRequirement(
                entity=e.name,
                field=f.name,
                kind=f.kind,
                max_length=f.max_length,
                min_length=f.min_length,
                required=f.required,
            )
            for e in plan.entities
            for f in e.fields
        ]
    if section == "facts":
        requirement.facts = {"notes": text}
    else:
        setattr(requirement, section, [text] if text else [])
    return requirement, plan


SEPARATORS = ["；", ";", "，", ", ", " and ", "、"]
GROUPS = [
    "beta/gamma 的",
    "beta/gamma：",
    "beta和gamma 的",
    "beta and gamma:",
    "beta、gamma：",
    "beta/gamma",
    "beta/gamma::",
]


@pytest.mark.parametrize("separator", SEPARATORS)
@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_equivalent_entity_group_boundaries_preserve_independent_field_limits(
    separator, group, section
):
    text = f"文本长度上限：alpha.name≤120{separator}{group} title≤200、detail≤3000"
    requirement, plan = case(text, section)
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[1].max_length = 120
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        d["attribute"] == "max_length"
        and d["expected"] == 200
        and d["targets"] == [{"entity": "beta", "field": "title"}]
        for d in diagnostics
    )
    assert not any(t["entity"] == "alpha" for d in diagnostics for t in d["targets"])


@pytest.mark.parametrize(
    "declaration",
    [
        "Text length limits: beta/gamma: title<=200, detail<=3000",
        "长度限制：beta/gamma.title≤200、detail≤3000",
        "beta/gamma: title max_length=200、detail max_length=3000",
        "beta/gamma: title（长度上限200）、detail（长度上限3000）",
    ],
)
@pytest.mark.parametrize(
    "entity,field", [(e, f) for e in ["beta", "gamma"] for f in ["title", "detail"]]
)
def test_each_group_member_has_its_own_positive_field_and_bound_obligation(
    declaration, entity, field
):
    requirement, plan = case(declaration)
    assert coverage_gaps(requirement, plan) == []
    target = next(e for e in plan.entities if e.name == entity)
    target.fields = [f for f in target.fields if f.name != field]
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize("separator", SEPARATORS)
@pytest.mark.parametrize(
    "prohibition", ["不得添加 published_on 字段", "禁止 published_on 字段", "不出现 published_on"]
)
def test_grouped_negation_never_leaks_to_previous_or_unrelated_entity(separator, prohibition):
    requirement, plan = case(f"alpha：name 可搜索{separator}beta/gamma：{prohibition}")
    plan.entities[0].fields.append(FieldSpec(name="published_on", kind="date"))
    assert coverage_gaps(requirement, plan) == []
    for entity in [1, 2]:
        changed = plan.model_copy(deep=True)
        changed.entities[entity].fields.append(FieldSpec(name="published_on", kind="date"))
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert [d["targets"] for d in diagnostics if d["code"] == "forbidden_field"] == [
            [{"entity": changed.entities[entity].name, "field": "published_on"}]
        ]


@pytest.mark.parametrize("separator", SEPARATORS)
def test_explicit_single_entity_switch_resets_group_and_prior_namespace(separator):
    requirement, plan = case(
        f"beta/gamma: title max_length=200{separator}alpha::title max_length=80"
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[1].max_length = 200
    assert coverage_gaps(requirement, plan)


def test_unqualified_continuation_retains_explicit_group_until_next_subject():
    requirement, plan = case(
        "beta/gamma: title max_length=200；detail max_length=3000；alpha: title max_length=80"
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[2].fields[2].max_length = 90
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize("separator", [" and ", " 和 ", "、"])
def test_coordinated_qualified_fields_keep_each_owner_and_shared_predicate(separator):
    requirement, plan = case(f"alpha.title{separator}beta.detail 必填")
    assert coverage_gaps(requirement, plan) == []
    for entity, field in [("alpha", "title"), ("beta", "detail")]:
        changed = plan.model_copy(deep=True)
        next(
            f for e in changed.entities if e.name == entity for f in e.fields if f.name == field
        ).required = False
        assert coverage_gaps(requirement, changed)
    plan.entities[1].fields[1].required = False
    plan.entities[0].fields[2].required = False
    assert coverage_gaps(requirement, plan) == []


def test_missing_entity_in_explicit_group_cannot_use_surviving_member_fields():
    requirement, plan = case("beta/missing：title（必填，长度上限200）")
    assert coverage_gaps(requirement, plan)


def test_group_subjects_cannot_be_fabricated_from_adjacent_qualified_field_names():
    requirement, plan = case("beta.title 和 beta.detail 必填")
    assert coverage_gaps(requirement, plan) == []
    fields = [(e.name, f) for e in plan.entities for f in e.fields]
    assert all(
        not clause.startswith("title::")
        for clause in _legacy_clauses(requirement.features[0], fields)
    )


def test_candidate_descriptions_never_become_new_requirement_obligations():
    requirement, plan = case("beta/gamma：title max_length=200", typed=True)
    plan.acceptance = ["beta.title max_length=120", "必须添加 published_on"]
    plan.entities[1].description = "title max_length=50"
    assert coverage_gaps(requirement, plan) == []
    requirement.acceptance = ["beta.title max_length=120"]
    assert coverage_gaps(requirement, plan)


def test_compact_minimum_and_numeric_field_predicate_keep_distinct_meaning():
    requirement, plan = case("文本长度：beta/gamma 的 title≥1、detail≤3000")
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[1].min_length = 0
    assert coverage_gaps(requirement, plan)
    requirement.features = ["beta.quantity<=100"]
    assert coverage_gaps(requirement, plan) == []


def test_requirement_only_projection_reuses_binder_and_preserves_raw_source_indices():
    text = "文本长度上限：alpha.name≤120，beta/gamma 的 title≤200、detail≤3000"
    requirement, _ = case(text, typed=True)
    before = requirement.model_dump()
    records = explicit_legacy_field_constraints(requirement)
    assert {(r["entity"], r["field"], r["attribute"], r["expected"]) for r in records} == {
        ("alpha", "name", "max_length", 120),
        ("beta", "title", "max_length", 200),
        ("gamma", "title", "max_length", 200),
        ("beta", "detail", "max_length", 3000),
        ("gamma", "detail", "max_length", 3000),
    }
    assert all(
        r["source"]["section"] == "features" and r["source"]["index"] == 0 and r["text"] == text
        for r in records
    )
    assert requirement.model_dump() == before


def test_requirement_only_projection_keeps_conflicts_and_does_not_infer_missing_vocabulary():
    requirement, _ = case("beta.title max_length=120", typed=True)
    requirement.acceptance = [
        "beta.title max_length=200",
        "title max_length=50",
        "unknown max_length=5",
    ]
    records = explicit_legacy_field_constraints(requirement)
    assert [r["expected"] for r in records] == [120, 200]
    assert requirement.acceptance[-1] == "unknown max_length=5"
    requirement.field_requirements = []
    assert explicit_legacy_field_constraints(requirement) == []


def test_requirement_only_projection_includes_reliably_typed_structured_facts():
    requirement, _ = case(typed=True)
    requirement.facts = {
        "beta": {"fields": [{"name": "title", "max_length": "120字符", "required": "false"}]}
    }
    records = explicit_legacy_field_constraints(requirement)
    assert {(r["entity"], r["field"], r["attribute"], r["expected"]) for r in records} == {
        ("beta", "title", "max_length", 120),
        ("beta", "title", "required", False),
    }
    assert all(
        r["source"]["encoding"] == "structured" and r["source"]["path"] == "beta.fields.0"
        for r in records
    )


def test_entity_scope_analysis_keeps_metric_conjunctions_in_the_metric_domain():
    text = (
        "alpha: name max_length=120；beta/gamma: title max_length=200；"
        "beta count filter quantity>=1 and title=done；alpha: detail max_length=90"
    )
    _, plan = case()
    fields = [(entity.name, field) for entity in plan.entities for field in entity.fields]
    normalized, exclusions = _legacy_field_exclusions(text, fields)
    assert normalized == text and exclusions == []
    _, metrics = _metric_clauses(normalized, fields)
    assert len(metrics) == 1
    assert metrics[0]["entity"] == "beta" and metrics[0]["kind"] == "count"
    assert [(p["field"], p["op"], p["value"]) for p in metrics[0]["predicates"]] == [
        ("quantity", "gte", 1),
        ("title", "eq", "done"),
    ]


def test_inline_entity_subject_does_not_scope_a_later_independent_query_summary():
    requirement, plan = case(
        "关键词搜索分别作用于 alpha 的 name、beta 的 title/detail、gamma 的 title/detail；"
        "category 与 priority 精确筛选"
    )
    plan.entities[0].fields.append(FieldSpec(name="category", kind="text", filterable=True))
    plan.entities[1].fields.append(FieldSpec(name="priority", kind="text", filterable=True))
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))
````
