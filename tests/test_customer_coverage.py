"""Model-style summaries must preserve entity/field subjects without fixture substitution."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def customer_case():
    plan = Plan(
        title="客服",
        data_scope="shared",
        entities=[
            {
                "name": "customers",
                "description": "客户",
                "fields": [
                    {"name": "name", "kind": "text", "max_length": 120, "searchable": True},
                    {
                        "name": "organization",
                        "kind": "text",
                        "required": False,
                        "max_length": 160,
                        "searchable": True,
                    },
                    {
                        "name": "contact",
                        "kind": "text",
                        "required": False,
                        "max_length": 200,
                        "searchable": True,
                    },
                    {
                        "name": "category",
                        "kind": "enum",
                        "choices": ["企业", "个人"],
                        "filterable": True,
                    },
                ],
            },
            {
                "name": "requests",
                "description": "请求",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 200, "searchable": True},
                    {"name": "detail", "kind": "text", "max_length": 3000, "searchable": True},
                    {"name": "resolved_at", "kind": "datetime", "required": False},
                ],
            },
            {
                "name": "tasks",
                "description": "任务",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80, "required": False},
                    {"name": "resolved_at", "kind": "datetime", "required": True},
                ],
            },
        ],
        acceptance=["客服字段合同"],
    )
    requirement = Requirement(
        summary="客服字段合同",
        users=["管理人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
    )
    return requirement, plan


def test_nested_entity_facts_do_not_cross_apply_duplicate_field_names():
    requirement, plan = customer_case()
    requirement.facts = {
        "entities": [
            {
                "name": "requests",
                "fields": [{"name": "title", "required": True, "max_length": 200}],
            },
            {"name": "tasks", "fields": [{"name": "title", "required": False, "max_length": 80}]},
        ]
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[2].fields[0].max_length = 200
    assert any("max_length" in gap for gap in coverage_gaps(requirement, plan))


def test_fact_metadata_identifiers_are_not_field_name_fragments():
    requirement, plan = customer_case()
    requirement.facts = {
        "entity_names": ["customers", "requests", "tasks"],
        "display_name": "客服必填字段验证",
        "request_title": "页面标题",
    }
    assert coverage_gaps(requirement, plan) == []


CUSTOMER_FEATURES = [
    "customers：name（必填文本，最长120，可搜索）、organization（可选文本，最长160，可搜索）、"
    "contact（可选文本，最长200，可搜索）、category（必填枚举，可精确筛选）",
    "requests：title（必填文本，最长200，可搜索）、detail（必填文本，最长3000，可搜索）、"
    "resolved_at（可选 datetime）",
    "tasks：title（可选文本，最长80）、resolved_at（必填 datetime）",
]


@pytest.mark.parametrize("typed", [False, True])
def test_compact_model_field_summaries_preserve_each_subject(typed):
    requirement, plan = customer_case()
    requirement.features = CUSTOMER_FEATURES
    if typed:
        requirement.field_requirements = [
            FieldRequirement(
                entity=entity.name,
                field=field.name,
                **field.model_dump(
                    include=set(FieldRequirement.model_fields) - {"entity", "field"}
                ),
            )
            for entity in plan.entities
            for field in entity.fields
        ]
    assert coverage_gaps(requirement, plan) == []
    for entity_name, field_name, attribute, value in [
        ("customers", "name", "max_length", 160),
        ("customers", "organization", "required", True),
        ("customers", "contact", "searchable", False),
        ("customers", "category", "filterable", False),
        ("requests", "title", "searchable", False),
        ("requests", "detail", "max_length", 200),
        ("requests", "resolved_at", "required", True),
        ("tasks", "title", "max_length", 200),
        ("tasks", "resolved_at", "required", False),
    ]:
        changed = plan.model_copy(deep=True)
        target = next(
            field
            for entity in changed.entities
            if entity.name == entity_name
            for field in entity.fields
            if field.name == field_name
        )
        setattr(target, attribute, value)
        assert coverage_gaps(requirement, changed), (entity_name, field_name, attribute)


def test_nested_legacy_descriptions_preserve_entity_scope_and_extra_obligations():
    requirement, plan = customer_case()
    requirement.facts = {
        "requests": {"title": {"required": True, "说明": "必填文本，最长200，可搜索"}},
        "tasks": {"title": {"required": False, "说明": "可选文本，最长80"}},
    }
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="title", required=True)
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_typed_contract_does_not_override_explicit_legacy_conflict():
    requirement, plan = customer_case()
    requirement.field_requirements = [
        FieldRequirement(entity="tasks", field="title", required=False)
    ]
    requirement.features = ["tasks：title 必填"]
    assert coverage_gaps(requirement, plan)
    plan.entities[2].fields[0].required = True
    assert coverage_gaps(requirement, plan)


def test_model_validation_summary_does_not_make_optional_fields_required():
    requirement, plan = customer_case()
    requirement.features = ["客户信息包含 name、organization、contact，必填字段缺失时拒绝保存"]
    assert coverage_gaps(requirement, plan) == []


def test_both_length_bounds_use_their_own_number():
    requirement, plan = customer_case()
    requirement.features = ["requests：title 最小长度0，最大长度200"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].max_length = 201
    assert coverage_gaps(requirement, plan)


def test_qualified_prose_scopes_each_duplicate_field_independently():
    requirement, plan = customer_case()
    requirement.features = ["requests.title 必填且最长200、tasks.title 可选且最长80"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[2].fields[0].required = True
    assert coverage_gaps(requirement, plan)


def test_shared_legacy_subject_cannot_lose_one_field():
    requirement, plan = customer_case()
    requirement.features = ["标题和正文都必填并且可搜索"]
    assert any("body" in gap for gap in coverage_gaps(requirement, plan))


def test_known_identifier_description_does_not_invent_alias_field():
    requirement, plan = customer_case()
    requirement.features = ["requests：detail（正文）必填且可搜索"]
    assert coverage_gaps(requirement, plan) == []


def test_presentation_labels_do_not_become_executable_field_obligations():
    requirement, plan = customer_case()
    requirement.facts = {
        "customers": {
            "category": {
                "required": True,
                "choices": ["企业", "个人"],
                "label": "可选分类",
                "choice_labels": {"企业": "必填企业"},
            }
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].choices = ["个人"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("fact", [{"required": True, "max_length": 120}, "必填文本，最长120"])
def test_field_literally_named_name_is_not_descriptor_metadata(fact):
    requirement, plan = customer_case()
    requirement.facts = {"customers": {"name": fact, "organization": {"required": False}}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = False
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].required = True
    plan.entities[0].fields[0].max_length = 200
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text",
    [
        "customers：支持分类筛选和关键词搜索",
        "customers：支持关键词搜索和category分类筛选",
        "category用于客户分类，name、organization、contact可搜索",
        "客户支持关键词搜索（name、organization、contact）和按category精确筛选",
        "客户支持关键词搜索(name、organization、contact)和按category精确筛选",
    ],
)
def test_query_summary_does_not_invent_category_search(text):
    requirement, plan = customer_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    # A genuine category-search requirement must still conflict with this plan.
    requirement.features.append("customers：category必须可搜索")
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text",
    [
        "datetime字段searchable=false、filterable=false、date_range=false",
        "时间字段不搜索、不筛选、无日期范围",
        "datetime仅存储时间戳，不添加搜索或日期范围",
        "datetime 字段不支持 date_range",
        "datetime仅存储，不要求日期范围筛选",
    ],
)
def test_negative_date_capability_cannot_invent_a_date_field(text):
    requirement, plan = customer_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    requirement.features.append("必须支持日期范围筛选")
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))


def test_negative_clause_cannot_erase_positive_search_requirement():
    requirement, plan = customer_case()
    requirement.features = ["customers：name可搜索，category不支持搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_generic_query_clause_stays_in_its_entity_scope():
    requirement, plan = customer_case()
    requirement.features = ["customers：支持分类筛选和关键词搜索"]
    assert coverage_gaps(requirement, plan) == []
    for field in plan.entities[0].fields:
        field.searchable = False
    # requests.title still searches, but cannot satisfy customers' obligation.
    assert plan.entities[1].fields[0].searchable
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_parenthesized_operation_targets_all_remain_required():
    requirement, plan = customer_case()
    requirement.features = ["customers：关键词搜索（name、organization、contact）和category筛选"]
    assert coverage_gaps(requirement, plan) == []
    for name in ("name", "organization", "contact"):
        changed = plan.model_copy(deep=True)
        next(field for field in changed.entities[0].fields if field.name == name).searchable = False
        assert any("searchable" in gap for gap in coverage_gaps(requirement, changed)), name


def test_gap_diagnostics_trace_typed_and_legacy_conflict_without_overriding_either():
    requirement, plan = customer_case()
    requirement.field_requirements = [
        FieldRequirement(entity="customers", field="category", searchable=False)
    ]
    requirement.features = ["customers：category必须可搜索"]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["source"] == {"section": "features", "index": 0, "clause": 0}
    assert diagnostics[0]["targets"] == [{"entity": "customers", "field": "category"}]
    assert diagnostics[0]["attribute"] == "searchable"
    plan.entities[0].fields[-1].searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["source"] == {"section": "field_requirements", "index": 0}
    assert diagnostics[0]["expected"] is False
    assert diagnostics[0]["actual"] is True


def test_exact_customer_field_contract_text_does_not_invent_query_flags():
    import json

    from workbench.settings import ROOT

    # This fixture is a comparison target only; the real-provider harness still
    # obtains every Requirement and Plan from the authorized provider.
    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    text = (ROOT / "examples/requirements/customer-service-contract.md").read_text(encoding="utf-8")
    requirement = Requirement(
        summary="客服字段合同",
        users=["客服"],
        acceptance=[],
        data_scope="shared",
        features=[
            line.removeprefix("- ")
            for line in text.splitlines()
            if line.startswith(("- customers：", "- requests：", "- tasks：", "字段的补充精确定义"))
        ],
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text,attribute",
    [
        ("customers.category searchable=false", "searchable"),
        ("customers：category filterable=false", "filterable"),
        ("customers：category 禁用搜索", "searchable"),
        ("customers：category 禁止筛选", "filterable"),
    ],
)
def test_explicit_field_prohibition_is_enforced_without_typed_ledger(text, attribute):
    requirement, plan = customer_case()
    requirement.features = [text]
    target = plan.entities[0].fields[-1]
    setattr(target, attribute, False)
    assert coverage_gaps(requirement, plan) == []
    setattr(target, attribute, True)
    assert any(attribute in gap for gap in coverage_gaps(requirement, plan))


def test_textual_false_and_true_conflict_is_never_silently_overridden():
    requirement, plan = customer_case()
    requirement.features = [
        "customers.category searchable=false",
        "customers.category searchable=true",
    ]
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[-1].searchable = True
    assert coverage_gaps(requirement, plan)


def test_unrequested_capability_does_not_disable_other_requested_search():
    requirement, plan = customer_case()
    requirement.features = ["customers：name 不要求搜索"]
    assert plan.entities[0].fields[0].searchable is True
    assert coverage_gaps(requirement, plan) == []


def test_textual_false_date_range_is_enforced_for_named_date_field():
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    plan.entities[0].fields.append(FieldSpec(name="meeting_date", kind="date"))
    requirement.features = ["customers.meeting_date date_range=false"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].date_range = True
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))
