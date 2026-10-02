"""A bare alias cannot create a field; explicit legacy contracts remain binding.

These are pure coverage/source checks, not executions of diagnostic candidates.
Raw user declarations omitted from every typed/narrative Requirement source are
not claimed to have general semantic completeness validation here.
"""

import pytest

from workbench.domain import EntityRequirement, FieldRequirement, FieldSpec, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.requirement_sources import analysis_source_conflicts


def case(text, *, typed=False):
    requirement = Requirement(
        summary="Records",
        users=["staff"],
        data_scope="shared",
        features=[text] if text else [],
        acceptance=[],
        field_requirements=[FieldRequirement(entity="records", field="title", required=True)]
        if typed
        else [],
    )
    plan = Plan(
        title="Records",
        data_scope="shared",
        acceptance=["Store records"],
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "title", "kind": "text", "required": True, "searchable": True},
                ],
            }
        ],
    )
    return requirement, plan


@pytest.mark.parametrize(
    "text",
    [
        "不存在 published_on 或任何额外业务字段，也无遗漏",
        "published_on 的说明",
        "关于 body 的说明",
        "不需要 published_on",
        "没有 published_on",
        "不含 published_on",
        "无需 published_on",
    ],
)
@pytest.mark.parametrize("typed", [False, True])
def test_bare_mentions_without_affirmative_predicate_do_not_create_fields(text, typed):
    requirement, plan = case(text, typed=typed)
    original = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == original


@pytest.mark.parametrize("field", ["published_on", "body", "external_ref", "custom_key"])
@pytest.mark.parametrize(
    "declaration",
    [
        "records: 字段 {field}",
        "records: 字段清单：{field}",
        "records: 必须包含 {field}",
        "records: 不得遗漏 {field}",
        "records.{field} 必填",
        "records: {field}（非必填）",
    ],
)
@pytest.mark.parametrize("typed", [False, True])
def test_partial_or_absent_typed_ledger_cannot_hide_positive_extra_field(field, declaration, typed):
    requirement, plan = case(declaration.format(field=field), typed=typed)
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(
        FieldSpec(name=field, kind="text", required="非必填" not in declaration)
    )
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "declaration",
    [
        "records: 不出现 external_ref",
        "records: 禁止添加 external_ref",
        "records: external_ref 字段不得出现",
        "records: do not include external_ref",
    ],
)
def test_existing_explicit_exclusions_remain_binding_in_open_inventory(declaration):
    requirement, plan = case(declaration)
    requirement.entity_requirements = [
        EntityRequirement(entity="records", fields=["title"], additional_fields=True)
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(d["code"] == "forbidden_field" for d in diagnostics)


def test_positive_extra_field_and_closed_catalog_are_not_silently_reconciled():
    requirement, plan = case("records: 必须包含 external_ref", typed=True)
    requirement.entity_requirements = [
        EntityRequirement(entity="records", fields=["title"], additional_fields=False)
    ]
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    assert coverage_gaps(requirement, plan)
    assert requirement.model_dump() == before


@pytest.mark.parametrize("text", ["records.title 最长120", "records: title 可选"])
def test_existing_source_conflicts_remain_blocking(text):
    requirement, _ = case(text, typed=True)
    requirement.field_requirements[0].max_length = 200
    assert analysis_source_conflicts(None, requirement, [])


def test_original_user_scalar_conflict_is_still_checked():
    requirement, _ = case("records.title 最长120", typed=True)
    requirement.field_requirements[0].max_length = 120
    diagnostics = analysis_source_conflicts(None, requirement, ["records.title 最长200"], cursor=1)
    assert any(s["origin"] == "user_input" for d in diagnostics for s in d["sources"])


def test_declared_catalog_tail_preserves_arbitrary_field_after_descriptor():
    requirement, plan = case("records: 字段清单：title（必填）、external_ref", typed=True)
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.append(FieldSpec(name="external_ref", kind="text"))
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "text",
    [
        "records: published_on 必须存在",
        "records: 必须存在 published_on",
        "records: published_on must exist",
        "records: external_ref 必须存在",
    ],
)
def test_explicit_existence_predicate_still_requires_its_named_field(text):
    requirement, plan = case(text)
    assert coverage_gaps(requirement, plan)
    field = "external_ref" if "external_ref" in text else "published_on"
    plan.entities[0].fields.append(FieldSpec(name=field, kind="text"))
    assert coverage_gaps(requirement, plan) == []


def test_legacy_fact_field_label_paths_do_not_become_entity_declarations():
    requirement, plan = case("")
    plan.entities[0].fields[0].max_length = 250
    plan.entities[0].fields.append(FieldSpec(name="body", kind="text", max_length=3000))
    requirement.facts = {"标题长度上限": "250字符", "正文长度上限": "3000字符"}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 200
    assert coverage_gaps(requirement, plan)
