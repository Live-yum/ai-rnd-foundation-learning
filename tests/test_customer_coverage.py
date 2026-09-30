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


def customer_metric_case(kind="count"):
    import json

    from workbench.business_contracts import MetricSpec
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    field = next(
        f
        for e in plan.entities
        if e.name == "requests"
        for f in e.fields
        if f.name == "request_state"
    )
    field.filterable = False
    options = {
        "count": {},
        "group_count": {"group_by": "priority"},
        "time_count": {"time_field": "created_at"},
        "average_duration": {"start_field": "created_at", "end_field": "resolved_at"},
    }[kind]
    plan.business.metrics = [
        MetricSpec(
            name="matching",
            label="条件指标",
            entity="requests",
            kind=kind,
            filters=[{"field": "request_state", "op": "eq", "value": "resolved"}],
            **options,
        )
    ]
    requirement = Requirement(
        summary="指标合同",
        users=["管理人员", "服务人员"],
        features=[],
        acceptance=[],
        data_scope="shared",
        field_requirements=[
            FieldRequirement(entity="requests", field="request_state", filterable=False)
        ],
    )
    return requirement, plan


@pytest.mark.parametrize("kind", ["count", "group_count", "time_count", "average_duration"])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_metric_predicates_are_not_list_filter_flags(kind, section):
    requirement, plan = customer_metric_case(kind)
    text = f"requests：业务指标（{kind}，按 request_state=resolved 筛选）"
    if section == "facts":
        requirement.facts = {"统计条件": text}
    else:
        setattr(requirement, section, [text])
    before = plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert plan.model_dump() == before
    plan.business.metrics[0].filters = []
    gaps = coverage_gaps(requirement, plan)
    assert gaps and all("业务指标" in gap for gap in gaps)


@pytest.mark.parametrize("mutation", ["entity", "kind", "value", "op", "missing_business"])
def test_metric_predicate_still_requires_the_correct_executable_metric(mutation):
    requirement, plan = customer_metric_case()
    requirement.features = ["已解决数（count，按 requests.request_state=resolved 筛选）"]
    assert coverage_gaps(requirement, plan) == []
    if mutation == "missing_business":
        plan.business = None
    elif mutation in {"entity", "kind"}:
        setattr(
            plan.business.metrics[0], mutation, "tasks" if mutation == "entity" else "time_count"
        )
    else:
        setattr(
            plan.business.metrics[0].filters[0], mutation, "active" if mutation == "value" else "ne"
        )
    assert any("业务指标" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("surface", ["列表", "表格", "页面", "查询参数", "list", "table", "UI"])
def test_metric_context_does_not_override_explicit_list_filtering(surface):
    requirement, plan = customer_metric_case()
    requirement.features = [f"统计{surface}必须支持 request_state 筛选"]
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


def test_metric_predicate_and_unrelated_ui_filter_remain_separate():
    requirement, plan = customer_metric_case()
    requirement.features = [
        "已解决数（count，按 request_state=resolved 筛选），客户列表支持 category 筛选"
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any(
        "filterable" in gap and "category" in gap for gap in coverage_gaps(requirement, plan)
    )


def test_metric_predicate_does_not_override_explicit_typed_legacy_conflict():
    requirement, plan = customer_metric_case()
    requirement.features = [
        "已解决数（count，按 request_state=resolved 筛选）",
        "requests.request_state filterable=true",
    ]
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))
    next(
        f
        for e in plan.entities
        if e.name == "requests"
        for f in e.fields
        if f.name == "request_state"
    ).filterable = True
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text",
    [
        "所有统计指标按本人可见权限范围过滤",
        "服务人员的count指标按assigned负责范围筛选",
        "manager/service的统计按角色权限筛选，只计算可见行",
    ],
)
def test_metric_row_scope_does_not_require_global_ui_filter(text):
    requirement, plan = customer_metric_case()
    requirement.features = [text]
    before = plan.business.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert plan.business.model_dump() == before


@pytest.mark.parametrize("first", ["name", "organization", "contact"])
@pytest.mark.parametrize("heading", ["客户管理", "customers：", "客户档案（customers）"])
def test_entity_capability_heading_does_not_make_first_search_field_filterable(first, heading):
    requirement, plan = customer_case()
    names = [first, *[name for name in ("name", "organization", "contact") if name != first]]
    requirement.features = [
        heading
        + "支持关键词搜索和精确筛选，字段包括"
        + "、".join(name + "（可搜索）" for name in names)
        + "、category（可精确筛选）"
    ]
    assert coverage_gaps(requirement, plan) == []
    requirement.features.append(f"customers：{first}搜索和精确筛选")
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


def test_unrequested_metric_filter_does_not_become_a_positive_metric_predicate():
    requirement, plan = customer_metric_case()
    requirement.features = ["count统计无需request_state筛选"]
    plan.business.metrics[0].filters = []
    assert coverage_gaps(requirement, plan) == []


ACTUAL_TIMESTAMP_EXCLUSIONS = [
    "resolved_at 与 due_at 仅作为时间戳存储，不提供关键词搜索、精确筛选或日期范围筛选。",
    "datetime 字段（resolved_at、due_at）仅存储时间戳，不参与搜索、筛选或日期范围查询；关系键字段不参与关键词搜索与日期范围。",
]
ACTUAL_REQUEST_DESCRIPTORS = (
    "请求字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、"
    "customer_id（必填关系键→customers）、assignee_id（可选关系键→$users）、"
    "request_state（必填枚举 new/active/resolved）、resolved_at（datetime）、due_at（datetime）、"
    "priority（必填枚举 普通/紧急，可精确筛选）"
)


def actual_customer_field_case():
    import json

    from workbench.settings import ROOT

    # Public deterministic contract is only the unit-test comparison target.
    # These exact Requirement excerpts came from the sanitized real-run report.
    source = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    plan = Plan(
        title="字段合同", data_scope="shared", entities=source.entities, acceptance=["字段合同验证"]
    )
    requirement = Requirement(
        summary="客服字段", users=["客服"], data_scope="shared", features=[], acceptance=[]
    )
    return requirement, plan


@pytest.mark.parametrize("text", ACTUAL_TIMESTAMP_EXCLUSIONS)
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_exact_real_model_timestamp_exclusions_do_not_invent_query_obligations(text, section):
    requirement, plan = actual_customer_field_case()
    if section == "facts":
        requirement.facts = {"字段查询约束": text}
    else:
        setattr(requirement, section, [text])
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("text", ACTUAL_TIMESTAMP_EXCLUSIONS)
@pytest.mark.parametrize("attribute", ["searchable", "filterable", "date_range"])
@pytest.mark.parametrize("entity", ["requests", "tasks"])
def test_explicit_nonparticipating_timestamp_operations_remain_false_constraints(
    text, attribute, entity
):
    requirement, plan = actual_customer_field_case()
    requirement.acceptance = [text]
    # The actual run also supplied per-entity false flags. An unscoped repeated
    # name cannot independently establish that every entity shares one policy.
    requirement.field_requirements = typed_field_ledger(plan)
    field = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "due_at"
    )
    setattr(field, attribute, True)
    assert any(attribute in gap for gap in coverage_gaps(requirement, plan))


def test_exact_descriptor_list_keeps_bare_datetime_fields_separate_and_scoped():
    requirement, plan = actual_customer_field_case()
    requirement.features = [ACTUAL_REQUEST_DESCRIPTORS]
    tasks = next(entity for entity in plan.entities if entity.name == "tasks")
    next(field for field in tasks.fields if field.name == "title").required = False
    next(field for field in tasks.fields if field.name == "detail").required = False
    next(field for field in tasks.fields if field.name == "assignee_id").required = True
    assert coverage_gaps(requirement, plan) == []
    priority = next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "priority"
    )
    priority.filterable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "requests", "field": "priority"}]
    priority.filterable = True
    priority.required = False
    assert any("priority" in gap and "必填" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("kind", ["datetime", "text", "integer", "boolean"])
def test_completed_type_only_descriptor_cannot_inherit_next_fields_predicates(kind):
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    plan.entities[0].fields.insert(0, FieldSpec(name="extra", kind=kind, required=False))
    requirement.features = [f"customers：extra（{kind}）、category（必填枚举，可精确筛选）"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("negative", ["不参与", "不提供"])
@pytest.mark.parametrize("separator", ["、", "与", "和", "或", "以及"])
def test_negative_operation_coordination_stops_at_later_positive_field_clause(negative, separator):
    requirement, plan = customer_case()
    requirement.features = [
        f"requests：resolved_at{negative}搜索{separator}日期范围查询，但title必须可搜索"
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].searchable = False
    assert any("searchable" in gap and "title" in gap for gap in coverage_gaps(requirement, plan))


def test_optional_negative_wording_does_not_disable_an_existing_search_capability():
    requirement, plan = customer_case()
    requirement.features = ["customers：name不要求搜索与日期范围查询"]
    assert plan.entities[0].fields[0].searchable
    assert coverage_gaps(requirement, plan) == []


def test_prohibition_before_field_name_retains_its_false_constraint():
    requirement, plan = customer_case()
    requirement.features = ["customers：禁止category搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].searchable = True
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_positive_operation_after_negative_contrast_keeps_its_field_subject():
    requirement, plan = customer_case()
    requirement.features = ["customers：name不提供搜索，但必须支持精确筛选"]
    plan.entities[0].fields[0].searchable = False
    assert plan.entities[0].fields[-1].filterable  # Another field cannot satisfy name's filter.
    assert any("filterable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[0].filterable = True
    assert coverage_gaps(requirement, plan) == []


def test_explicit_shared_predicate_survives_completed_descriptor_boundaries():
    requirement, plan = customer_case()
    requirement.features = ["customers：name（必填文本）、contact（可选文本）均可搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan))


def test_ambiguous_localized_heading_does_not_inherit_the_previous_entity():
    requirement, plan = customer_case()
    requirement.features = ["tasks：title（可选）；另一组字段：title（可选）"]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = ["tasks：title（可选）；所有实体：title（可选）"]
    assert any("title" in gap and "可选" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("descriptor", ["name（{negative}搜索）", "name{negative}搜索"])
def test_explicit_unsupported_search_is_false_constraint(negative, section, descriptor):
    requirement, plan = customer_case()
    text = "customers：" + descriptor.format(negative=negative)
    if section == "facts":
        requirement.facts = {"查询限制": text}
    else:
        setattr(requirement, section, [text])
    field = plan.entities[0].fields[0]
    field.searchable = False
    assert coverage_gaps(requirement, plan) == []
    field.searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "searchable"
        and item["expected"] is False
        and item["targets"] == [{"entity": "customers", "field": "name"}]
        for item in diagnostics
    )


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize("separator", ["，", "；", "，但", "。"])
def test_unsupported_search_does_not_negate_adjacent_positive_field(negative, separator):
    requirement, plan = customer_case()
    requirement.features = [f"customers：name{negative}搜索{separator}contact必须可搜索"]
    name, contact = plan.entities[0].fields[0], plan.entities[0].fields[2]
    name.searchable = False
    assert contact.searchable
    assert coverage_gaps(requirement, plan) == []
    contact.searchable = False
    assert any("searchable" in gap and "contact" in gap for gap in coverage_gaps(requirement, plan))
    contact.searchable = True
    name.searchable = True
    assert any(
        "searchable=False" in gap and "name" in gap for gap in coverage_gaps(requirement, plan)
    )


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize(
    "kind,attribute,operation",
    [
        ("text", "searchable", "关键词搜索"),
        ("text", "filterable", "精确筛选"),
        ("date", "date_range", "日期范围查询"),
    ],
)
def test_unsupported_operations_remain_field_scoped(negative, kind, attribute, operation):
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    field = FieldSpec(name="extra", kind=kind)
    plan.entities[0].fields.append(field)
    requirement.features = [f"customers：extra{negative}{operation}，name必须可搜索"]
    assert coverage_gaps(requirement, plan) == []
    setattr(field, attribute, True)
    assert any(attribute in gap and "extra" in gap for gap in coverage_gaps(requirement, plan))


FINAL_CUSTOMER_QUERY = (
    "客户搜索与筛选：按 name、organization、contact 关键词搜索，"
    "按 category（企业/个人/合作伙伴）精确筛选。"
)
FINAL_REQUEST_QUERY = (
    "服务请求管理：创建服务请求，记录 title、detail、customer_id、priority、due_at，"
    "并按 title、detail 关键词搜索。"
)
FINAL_REQUEST_FIELDS = (
    "requests 服务请求：创建请求需填写 title（必填，≤200）、detail（必填，≤3000）、"
    "customer_id（必填关联 customers）、priority（必填枚举：普通/紧急），"
    "可选填 assignee_id（关联 $users）、due_at。"
)


def typed_field_ledger(plan):
    return [
        FieldRequirement(
            entity=entity.name,
            field=field.name,
            **field.model_dump(include=set(FieldRequirement.model_fields) - {"entity", "field"}),
        )
        for entity in plan.entities
        for field in entity.fields
    ]


@pytest.mark.parametrize("text", [FINAL_CUSTOMER_QUERY, FINAL_REQUEST_QUERY, FINAL_REQUEST_FIELDS])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("typed", [False, True])
def test_exact_final_model_clauses_respect_inventory_heading_and_typed_ledger(text, section, typed):
    requirement, plan = actual_customer_field_case()
    if section == "facts":
        requirement.facts = {"功能说明": text}
    else:
        setattr(requirement, section, [text])
    if typed:
        requirement.field_requirements = typed_field_ledger(plan)
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "query",
    [
        "按 title、detail 关键词搜索",
        "对 title、detail 进行关键词搜索",
        "search using title, detail",
        "search by detail and title",
        "using title and detail for keyword search",
    ],
)
@pytest.mark.parametrize(
    "inventory",
    [
        "title、detail、customer_id、priority、due_at",
        "due_at、priority、customer_id、detail、title",
        "priority, title, due_at, customer_id, detail",
    ],
)
@pytest.mark.parametrize("heading", ["服务请求管理", "Request management", "requests"])
def test_direct_query_binds_its_own_list_and_unambiguous_section(query, inventory, heading):
    requirement, plan = actual_customer_field_case()
    tasks = next(entity for entity in plan.entities if entity.name == "tasks")
    for field in tasks.fields:
        field.searchable = False
    requirement.features = [f"{heading}：记录 {inventory}，{query}。"]
    requirement.field_requirements = typed_field_ledger(plan)
    assert coverage_gaps(requirement, plan) == []
    # Prove the explicit prose still carries an independent obligation.
    requirement.field_requirements = []
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    next(field for field in requests.fields if field.name == "title").searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    query_gaps = [item for item in diagnostics if item["attribute"] == "searchable"]
    assert query_gaps
    assert all(
        target["entity"] == "requests" and target["field"] in {"title", "detail"}
        for item in query_gaps
        for target in item["targets"]
    )
    assert all(
        item["source"]["section"] == "features" and item["source"]["index"] == 0
        for item in query_gaps
    )


@pytest.mark.parametrize(
    "text",
    [
        FINAL_CUSTOMER_QUERY,
        "Customer search and filtering: search using contact, name, organization, filter by category.",
        "客户查询：按 category 精确筛选，并对 organization、contact、name 关键词搜索。",
        "customers: filter by category and search using organization, name, contact",
    ],
)
def test_query_headings_and_operation_order_do_not_cross_assign_flags(text):
    requirement, plan = actual_customer_field_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    customers = plan.entities[0]
    for field_name, attribute in (
        ("name", "searchable"),
        ("organization", "searchable"),
        ("contact", "searchable"),
        ("category", "filterable"),
    ):
        changed = plan.model_copy(deep=True)
        target = next(field for field in changed.entities[0].fields if field.name == field_name)
        setattr(target, attribute, False)
        assert any(attribute in gap for gap in coverage_gaps(requirement, changed)), field_name
    assert all(not field.filterable for field in customers.fields if field.name != "category")


def test_final_python_required_priority_is_not_changed_by_next_optional_subject():
    requirement, plan = actual_customer_field_case()
    requirement.features = [FINAL_REQUEST_FIELDS]
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    assert coverage_gaps(requirement, plan) == []
    for name, invalid in (("priority", False), ("assignee_id", True), ("due_at", True)):
        changed = plan.model_copy(deep=True)
        field = next(
            field
            for entity in changed.entities
            if entity.name == "requests"
            for field in entity.fields
            if field.name == name
        )
        field.required = invalid
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["targets"] == [{"entity": "requests", "field": name}]
            and item["attribute"] == "required"
            for item in diagnostics
        )
    requirement.field_requirements = typed_field_ledger(plan)
    next(field for field in requests.fields if field.name == "priority").required = False
    assert coverage_gaps(requirement, plan)


def test_explicit_query_conflict_with_typed_prohibition_keeps_both_provenances():
    requirement, plan = actual_customer_field_case()
    requirement.features = ["服务请求管理：记录 title、detail、customer_id，按 customer_id 搜索"]
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="customer_id", searchable=False)
    ]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features"
        and item["targets"] == [{"entity": "requests", "field": "customer_id"}]
        for item in diagnostics
    )
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "customer_id"
    ).searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize(
    "heading", ["请求搜索与筛选", "Service request queries", "功能说明：请求查询"]
)
def test_ambiguous_duplicate_prose_does_not_override_typed_entity_policies(heading):
    requirement, plan = actual_customer_field_case()
    for entity in plan.entities:
        if entity.name == "tasks":
            for field in entity.fields:
                if field.name in {"title", "detail"}:
                    field.searchable = False
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"{heading}：按 title、detail 搜索"]
    assert coverage_gaps(requirement, plan) == []
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    next(field for field in requests.fields if field.name == "title").searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize("scope", ["requests", "所有实体", "all entities", "both entities"])
@pytest.mark.parametrize("negative", [False, True])
def test_explicit_entity_or_universal_subject_preserves_positive_and_false_obligations(
    scope, negative
):
    requirement, plan = actual_customer_field_case()
    operation = "不提供搜索" if negative else "必须可搜索"
    requirement.features = [f"{scope}：title{operation}"]
    for entity in plan.entities:
        for field in entity.fields:
            if field.name == "title":
                field.searchable = not negative
    assert coverage_gaps(requirement, plan) == []
    target_entity = "requests" if scope == "requests" else "tasks"
    next(
        field
        for entity in plan.entities
        if entity.name == target_entity
        for field in entity.fields
        if field.name == "title"
    ).searchable = negative
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        target["entity"] == target_entity for item in diagnostics for target in item["targets"]
    )


@pytest.mark.parametrize(
    "heading", ["客户搜索与筛选", "Customer search and filtering", "搜索和筛选"]
)
def test_combined_capability_heading_cannot_donate_operations_to_a_bare_list(heading):
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"{heading}：name、organization、contact"]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("heading", ["search", "搜索", "search fields", "关键词搜索"])
def test_single_operation_heading_is_an_explicit_field_list_predicate(heading):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers：{heading}: name, organization, contact"]
    assert coverage_gaps(requirement, plan) == []
    next(
        field for field in plan.entities[0].fields if field.name == "organization"
    ).searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("heading", ["searchable=false", "禁止搜索", "不提供搜索"])
def test_explicit_false_operation_heading_is_not_discarded_as_context(heading):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers：{heading}: name"]
    name = next(field for field in plan.entities[0].fields if field.name == "name")
    assert coverage_gaps(requirement, plan)
    name.searchable = False
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("entity", ["requests", "tasks"])
@pytest.mark.parametrize(
    "heading,attribute,expected,invalid",
    [
        ("required", "required", True, False),
        ("required=true", "required", True, False),
        ("required=false", "required", False, True),
        ("required: false", "required", False, True),
        ("optional", "required", False, True),
        ("required fields", "required", True, False),
        ("必填", "required", True, False),
        ("必填字段", "required", True, False),
        ("可选", "required", False, True),
        ("非必填", "required", False, True),
        ("max_length=120", "max_length", 120, 200),
        ("max_length: 120", "max_length", 120, 200),
        ("min_length=1", "min_length", 1, 0),
        ("min_length=0", "min_length", 0, 1),
        ("长度上限120", "max_length", 120, 200),
        ("最小长度0", "min_length", 0, 1),
    ],
)
def test_explicit_property_headings_retain_values_and_entity_scope(
    entity, heading, attribute, expected, invalid
):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"{entity}: {heading}: title"]
    target = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "title"
    )
    setattr(target, attribute, expected)
    assert coverage_gaps(requirement, plan) == []
    setattr(target, attribute, invalid)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == attribute
        and item["expected"] == expected
        and item["targets"] == [{"entity": entity, "field": "title"}]
        for item in diagnostics
    )


@pytest.mark.parametrize(
    "heading,attribute,expected,invalid",
    [("max_length=120", "max_length", 120, 200), ("min_length=1", "min_length", 1, 0)],
)
def test_unique_field_property_heading_is_not_discarded(heading, attribute, expected, invalid):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers: {heading}: name"]
    name = next(field for field in plan.entities[0].fields if field.name == "name")
    setattr(name, attribute, expected)
    assert coverage_gaps(requirement, plan) == []
    setattr(name, attribute, invalid)
    assert coverage_gaps(requirement, plan)


STRUCTURED_BUSINESS_METADATA = [
    {
        "metrics": [
            {
                "name": "requests_total",
                "entity": "requests",
                "kind": "count",
                "role_scope": ["manager", "service"],
            }
        ]
    },
    {
        "metrics": [
            {
                "name": "title",
                "entity": "requests",
                "kind": "average_duration",
                "start_field": "created_at",
                "end_field": "resolved_at",
                "role_scope": ["manager"],
                "filters": [{"field": "request_state", "op": "in", "value": ["resolved"]}],
            }
        ]
    },
    {
        "relations": [
            {
                "entity": "requests",
                "field": "customer_id",
                "target_entity": "customers",
                "roles": ["manager", "service"],
            }
        ]
    },
    {
        "permissions": [
            {
                "entity": "requests",
                "role": "service",
                "scope": "assigned",
                "actions": ["read", "update", "add_note"],
            }
        ]
    },
    {
        "notifications": [
            {
                "entity": "requests",
                "event": "transitioned",
                "transition": "resolve",
                "recipient": "creator",
                "role_scope": ["employee"],
            }
        ]
    },
    {
        "roles": [
            {
                "name": "category",
                "label": "可选分类",
                "actions": ["read"],
                "role_scope": ["manager"],
            }
        ]
    },
    {
        "resources": [
            {"entity": "requests", "assignee_field": "assignee_id", "notes": True, "required": True}
        ]
    },
    {
        "workflows": [
            {
                "entity": "requests",
                "status_field": "request_state",
                "transitions": [
                    {
                        "name": "title",
                        "from_states": ["new"],
                        "to_state": "active",
                        "roles": ["manager", "service"],
                    }
                ],
            }
        ]
    },
    {
        "entities": [
            {
                "name": "requests",
                "fields": ["title", "detail"],
                "role_scope": ["manager", "service"],
            }
        ]
    },
]


def encode_fact_shapes(facts, encoding):
    import json
    from copy import deepcopy

    facts = deepcopy(facts)
    if encoding == "json":
        return {key: json.dumps(value, ensure_ascii=False) for key, value in facts.items()}
    if encoding == "items":
        return {
            key: [json.dumps(item, ensure_ascii=False) for item in value]
            for key, value in facts.items()
        }
    return facts


@pytest.mark.parametrize("facts", STRUCTURED_BUSINESS_METADATA)
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_business_structures_are_not_field_names_kinds_or_enum_lists(facts, encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(facts, encoding)
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before


@pytest.mark.parametrize(
    "namespace",
    ["metrics", "relations", "permissions", "notifications", "roles", "resources", "workflows"],
)
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_explicit_field_constraints_nested_in_metadata_cannot_disappear(namespace, encoding):
    requirement, plan = actual_customer_field_case()
    facts = {
        namespace: [
            {
                "name": "business_definition",
                "entity": "requests",
                "role_scope": ["manager"],
                "field_constraints": [{"entity": "requests", "field": "title", "required": False}],
            }
        ]
    }
    requirement.facts = encode_fact_shapes(facts, encoding)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "required"
        and item["targets"] == [{"entity": "requests", "field": "title"}]
        and item["source"]["path"] == f"{namespace}.0.field_constraints.0"
        for item in diagnostics
    )
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "title"
    ).required = False
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_relation_field_attributes_are_preserved_without_treating_roles_as_choices(encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(
        {
            "relations": [
                {
                    "entity": "requests",
                    "field": "customer_id",
                    "target_entity": "customers",
                    "required": True,
                    "roles": ["manager", "employee"],
                }
            ]
        },
        encoding,
    )
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "customer_id"
    ).required = False
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_explicit_enum_descriptor_preserves_membership_inside_json(encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(
        {
            "fields": [
                {"entity": "customers", "name": "category", "choices": ["个人", "企业", "合作伙伴"]}
            ]
        },
        encoding,
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].choices = ["个人", "企业"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "facts",
    [
        {"fields": [{"field": "missing", "required": True}]},
        {"fields": [{"entity": "requests", "field": "missing"}]},
        {"requests": {"missing": {"required": True}}},
        {"fields": {"missing": {"choices": ["a", "b"]}}},
        {"title": {"entity": "requests", "field": "missing", "required": True}},
    ],
)
def test_genuine_missing_field_declaration_is_not_satisfied_by_metadata_or_ancestor(facts):
    requirement, plan = actual_customer_field_case()
    requirement.facts = facts
    diagnostics = []
    assert any(
        "missing" in gap for gap in coverage_gaps(requirement, plan, diagnostics=diagnostics)
    )
    assert any(
        item["code"] == "structured_missing_field"
        and item["source"]["path"]
        and not item["targets"]
        for item in diagnostics
    )


@pytest.mark.parametrize("name", ["metrics", "permissions", "fields", "entities", "role_scope"])
def test_field_identifier_can_equal_a_metadata_namespace(name):
    from workbench.domain import FieldSpec

    requirement, plan = actual_customer_field_case()
    plan.entities[0].fields.append(FieldSpec(name=name, kind="text", required=True))
    requirement.facts = {"fields": {name: {"entity": "customers", "required": False}}}
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[-1].required = False
    assert coverage_gaps(requirement, plan) == []


def test_structured_subject_identity_does_not_match_wrapper_field_names():
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"title": {"entity": "tasks", "field": "resolved_at", "required": False}}
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "resolved_at"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "resolved_at"}]
    assert diagnostics[0]["source"]["path"] == "title"


def test_structured_field_fact_and_typed_opposite_constraint_both_remain_blocking():
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="title", required=True)
    ]
    requirement.facts = {"fields": [{"entity": "requests", "name": "title", "required": False}]}
    for value, source in [(True, "facts"), (False, "field_requirements")]:
        next(
            field
            for entity in plan.entities
            if entity.name == "requests"
            for field in entity.fields
            if field.name == "title"
        ).required = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == source
            and item["targets"] == [{"entity": "requests", "field": "title"}]
            for item in diagnostics
        )


@pytest.mark.parametrize("kind", [{"type": "text"}, ["text"], True, None])
def test_malformed_explicit_field_kind_blocks_without_parser_crash(kind):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"fields": [{"entity": "requests", "field": "title", "kind": kind}]}
    gaps = coverage_gaps(requirement, plan)
    assert bool(gaps) is (kind is not None)


@pytest.mark.parametrize("entity", [17, {}, "not an identifier"])
def test_invalid_explicit_field_entity_cannot_fall_back_to_another_target(entity):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"fields": [{"entity": entity, "field": "title", "required": True}]}
    assert coverage_gaps(requirement, plan)


def test_keyed_field_constraints_honor_their_explicit_entity_identity():
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"title": {"entity": "tasks", "required": False}}
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "title"
    ).required = False
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "title"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]


def test_json_encoded_enum_attribute_keeps_membership_and_raw_source():
    import json

    requirement, plan = actual_customer_field_case()
    requirement.facts = {
        "fields": [
            {
                "entity": "customers",
                "field": "category",
                "choices": json.dumps(["个人", "企业", "合作伙伴"]),
            }
        ]
    }
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    plan.entities[0].fields[-1].choices = ["企业"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


def scoped_resource_field_case(attribute, expected, other, kind):
    """Repeated identifiers with deliberately different per-entity properties."""
    requirement, _ = customer_case()
    plan = Plan(
        title="Scoped fields",
        data_scope="shared",
        entities=[
            {
                "name": entity,
                "description": entity,
                "fields": [
                    {
                        "name": "value",
                        "kind": kind,
                        **({"choices": ["a", "b"]} if kind == "enum" else {}),
                        attribute: value,
                    }
                ],
            }
            for entity, value in [("alpha", expected), ("beta", other)]
        ],
        acceptance=["Scoped field constraints"],
    )
    return requirement, plan


def encode_resource_collection(collection, encoding):
    import json

    if encoding == "json":
        return json.dumps(collection)
    if encoding == "items":
        if isinstance(collection, list):
            return [json.dumps(item) for item in collection]
        return {
            key: json.dumps(value) if isinstance(value, (dict, list)) else value
            for key, value in collection.items()
        }
    return collection


@pytest.mark.parametrize(
    "attribute,expected,other,kind",
    [
        ("required", False, True, "text"),
        ("min_length", 0, 1, "text"),
        ("max_length", 120, 160, "text"),
        ("searchable", True, False, "text"),
        ("filterable", False, True, "text"),
        ("date_range", False, True, "date"),
        ("choices", ["a", "b"], ["a", "c"], "enum"),
        ("kind", "text", "integer", "text"),
    ],
)
@pytest.mark.parametrize("shape", ["entity_list", "name_list", "keyed", "aliased_key", "single"])
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_resource_namespace_scopes_every_field_property_without_cross_binding(
    attribute, expected, other, kind, shape, encoding
):
    requirement, plan = scoped_resource_field_case(attribute, expected, other, kind)
    record = {
        "fields": [{"name": "value", attribute: expected}],
        "label": "A resource whose field name also exists elsewhere",
        "capabilities": ["search", "filter", "value"],
        "role_scope": ["manager"],
    }
    if shape == "entity_list":
        collection = [{"entity": "alpha", **record}]
        path = "business.resources.0.fields.0"
    elif shape == "name_list":
        collection = [{"name": "alpha", **record}]
        path = "business.resources.0.fields.0"
    elif shape == "keyed":
        collection = {"alpha": {**record, "fields": {"value": {attribute: expected}}}}
        path = "business.resources.alpha.fields.value"
    elif shape == "aliased_key":
        collection = {"value": {"entity": "alpha", **record}}
        path = "business.resources.value.fields.0"
    else:
        collection = {"entity": "alpha", **record}
        path = "business.resources.fields.0"
    requirement.facts = {
        "business": {"resources": encode_resource_collection(collection, encoding)}
    }
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    setattr(plan.entities[0].fields[0], attribute, other)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "value"}]
    assert diagnostics[0]["attribute"] == attribute
    assert diagnostics[0]["source"]["path"] == path


@pytest.mark.parametrize("shape", ["list", "keyed", "source_group", "resource_nested", "single"])
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_relation_namespace_uses_source_scope_and_never_target_or_wrapper_scope(shape, encoding):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    record = {"field": "value", "to": "beta", "required": False, "kind": "foreign_key"}
    if shape == "list":
        collection = [{"from": "alpha", **record}]
        path = "business.relations.0"
    elif shape == "keyed":
        collection = {"value": {"from": "alpha", **record}}
        path = "business.relations.value"
    elif shape == "source_group":
        collection = {"alpha": [record]}
        path = "business.relations.alpha.0"
    elif shape == "single":
        collection = {"from": "alpha", **record}
        path = "business.relations"
    else:
        collection = [record]
        path = "business.resources.0.relations.0"
    facts = {"relations": encode_resource_collection(collection, encoding)}
    if shape == "resource_nested":
        facts = {"resources": [{"entity": "alpha", **facts}]}
    requirement.facts = {"business": facts}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "value"}]
    assert diagnostics[0]["source"]["path"] == path


@pytest.mark.parametrize("namespace", ["resources", "entities", "资源", "实体"])
def test_leaf_explicit_entity_overrides_resource_context_and_keeps_typed_conflict(namespace):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.field_requirements = [FieldRequirement(entity="beta", field="value", required=True)]
    requirement.facts = {
        namespace: {"alpha": {"fields": [{"entity": "beta", "name": "value", "required": False}]}}
    }
    for value, section in [(True, "facts"), (False, "field_requirements")]:
        plan.entities[1].fields[0].required = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert len(diagnostics) == 1
        assert diagnostics[0]["source"]["section"] == section
        assert diagnostics[0]["targets"] == [{"entity": "beta", "field": "value"}]


@pytest.mark.parametrize("scope", ["missing", 12, {}, "not an identifier"])
@pytest.mark.parametrize("namespace", ["resources", "relations"])
def test_invalid_resource_or_relation_scope_cannot_fall_back_to_matching_field(scope, namespace):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    record = (
        {"entity": scope, "fields": [{"name": "value", "required": False}]}
        if namespace == "resources"
        else {"from": scope, "field": "value", "to": "beta", "required": False}
    )
    requirement.facts = {namespace: [record]}
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "structured_missing_field"
    assert diagnostics[0]["source"]["path"].startswith(namespace)


def test_conflicting_relation_source_identifiers_block_instead_of_picking_one():
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.facts = {
        "relations": [{"from": "alpha", "entity": "beta", "field": "value", "required": True}]
    }
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "structured_missing_field"


@pytest.mark.parametrize("name", ["value", "alpha", "resources", "relations"])
def test_business_names_and_prose_do_not_supply_implicit_field_scope(name):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.facts = {
        "business": {
            "resources": [{"name": name, "required": True, "capabilities": ["value", "filter"]}],
            "metrics": [
                {
                    "name": name,
                    "kind": "count",
                    "from": "beta",
                    "to": "alpha",
                    "role_scope": ["manager"],
                }
            ],
            "metadata": {"name": name, "label": "value", "from": "beta"},
        }
    }
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("entity", ["resources", "entities", "relations", "fields"])
@pytest.mark.parametrize("field", ["resources", "relations", "fields", "name"])
def test_resource_and_field_identifiers_can_collide_with_namespace_names(entity, field):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    plan.entities[0].name = entity
    for item in plan.entities:
        item.fields[0].name = field
    requirement.facts = {"resources": {entity: {"fields": {field: {"required": False}}}}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": field}]
    assert diagnostics[0]["source"]["path"] == f"resources.{entity}.fields.{field}"


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize(
    "attribute,kind,operation",
    [
        ("searchable", "text", "搜索"),
        ("searchable", "text", "检索"),
        ("filterable", "text", "精确筛选"),
        ("filterable", "text", "过滤"),
        ("date_range", "date", "日期范围查询"),
        ("date_range", "date", "日期区间筛选"),
    ],
)
@pytest.mark.parametrize(
    "noun", ["结果", "结果集", "的效果", "后的结果", "返回的结果", "输出", "条件"]
)
def test_chinese_query_result_nouns_never_declare_field_operations(
    enabled, attribute, kind, operation, noun
):
    requirement, plan = scoped_resource_field_case(attribute, enabled, not enabled, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        f"alpha: value 的{operation}{noun}由系统展示，没有{operation}{noun}时显示空列表"
    ]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize(
    "attribute,kind,operation",
    [
        ("searchable", "text", "search"),
        ("filterable", "text", "filter"),
        ("date_range", "date", "date range"),
    ],
)
@pytest.mark.parametrize("noun", ["results", "outcomes", "outputs", "conditions", "criteria"])
def test_english_query_result_nouns_never_declare_field_operations(
    enabled, attribute, kind, operation, noun
):
    requirement, plan = scoped_resource_field_case(attribute, enabled, not enabled, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        f"alpha: value appears in the {operation} {noun}; no {operation} {noun} are available"
    ]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "attribute,kind,text",
    [
        ("searchable", "text", "搜索结果中 value 必须支持搜索"),
        ("searchable", "text", "value 的搜索结果应正确；value 必须支持搜索"),
        ("filterable", "text", "按 value 筛选搜索结果"),
        ("filterable", "text", "filter results by value"),
        ("searchable", "text", "search results using value"),
        ("searchable", "text", "value 作为搜索条件"),
        ("filterable", "text", "value 用作精确筛选条件"),
        ("searchable", "text", "搜索条件包括 value"),
        ("filterable", "text", "value is a filter condition"),
        ("searchable", "text", "search criteria: value"),
        ("date_range", "date", "value 作为日期范围查询条件"),
        ("date_range", "date", "date range conditions include value"),
    ],
)
def test_explicit_operation_predicates_with_result_nouns_preserve_typed_contradictions(
    attribute, kind, text
):
    requirement, plan = scoped_resource_field_case(attribute, False, False, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = ["alpha: " + text]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "acceptance"
        and item["attribute"] == attribute
        and item["targets"] == [{"entity": "alpha", "field": "value"}]
        for item in diagnostics
    )
    setattr(plan.entities[0].fields[0], attribute, True)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize("operation", ["searched", "filtered", "searching", "filtering"])
def test_inflected_operation_result_nouns_do_not_create_query_flags(operation):
    requirement, plan = scoped_resource_field_case("filterable", False, False, "text")
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"alpha: value is displayed in the {operation} results"]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "attribute,kind,text",
    [
        ("searchable", "text", "value 不可作为搜索条件"),
        ("filterable", "text", "value is not a filter condition"),
        ("date_range", "date", "value 不得用作日期范围查询条件"),
        ("searchable", "text", "搜索条件不包括 value"),
        ("searchable", "text", "search criteria do not include value"),
    ],
)
def test_explicit_negated_condition_bindings_are_still_false_obligations(attribute, kind, text):
    requirement, plan = scoped_resource_field_case(attribute, True, False, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = ["alpha: " + text]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features"
        and item["attribute"] == attribute
        and item["expected"] is False
        for item in diagnostics
    )
    setattr(plan.entities[0].fields[0], attribute, False)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


def test_exact_2a4_fastapi_search_result_acceptance_preserves_independent_query_flags():
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        "客户列表支持按 name、organization、contact 关键词搜索，并可按 category（企业/个人/合作伙伴）精确筛选，搜索结果符合筛选条件。"
    ]
    assert coverage_gaps(requirement, plan) == []
    for field_name, flag in [("name", "searchable"), ("category", "filterable")]:
        changed = plan.model_copy(deep=True)
        setattr(
            next(field for field in changed.entities[0].fields if field.name == field_name),
            flag,
            False,
        )
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "acceptance" and item["attribute"] == flag
            for item in diagnostics
        )


def scoped_inventory_case():
    requirement, _ = customer_case()
    plan = Plan(
        title="Nested inventory",
        data_scope="shared",
        entities=[
            {
                "name": entity,
                "description": entity,
                "fields": [
                    {
                        "name": "short_text",
                        "kind": "text",
                        "required": True,
                        "min_length": 0,
                        "max_length": 200,
                        "searchable": True,
                    },
                    {
                        "name": "long_text",
                        "kind": "text",
                        "required": False,
                        "min_length": 1,
                        "max_length": 3000,
                        "searchable": True,
                    },
                ],
            }
            for entity in ["alpha", "beta"]
        ],
        acceptance=["Independent field descriptors"],
    )
    requirement.field_requirements = typed_field_ledger(plan)
    return requirement, plan


@pytest.mark.parametrize("brackets", ["（）", "()", "[]", "【】"])
@pytest.mark.parametrize("separator", ["、", "，", ", ", " and "])
@pytest.mark.parametrize("reverse", [False, True])
def test_nested_field_inventory_constraints_bind_nearest_subject(brackets, separator, reverse):
    requirement, plan = scoped_inventory_case()
    descriptors = ["short_text 必填 最长200 最小0", "long_text 可选 最长3000 最小1"]
    if reverse:
        descriptors.reverse()
    requirement.features = [
        f"alpha: 创建对象{brackets[0]}{separator.join(descriptors)}{brackets[1]}、编辑、归档"
    ]
    assert coverage_gaps(requirement, plan) == []
    for name, attribute, wrong in [
        ("short_text", "max_length", 3000),
        ("long_text", "max_length", 200),
        ("long_text", "min_length", 0),
        ("long_text", "required", True),
    ]:
        changed = plan.model_copy(deep=True)
        setattr(
            next(field for field in changed.entities[0].fields if field.name == name),
            attribute,
            wrong,
        )
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features"
            and item["attribute"] == attribute
            and item["targets"] == [{"entity": "alpha", "field": name}]
            for item in diagnostics
        )


@pytest.mark.parametrize("wrapper", ["define({body})", "define(fields({body}))", "search({body})"])
def test_nested_inventory_keeps_outer_capability_and_inner_explicit_conflicts(wrapper):
    requirement, plan = scoped_inventory_case()
    body = "short_text(required max_length=200), long_text(optional max_length=3000)"
    requirement.features = ["alpha: " + wrapper.format(body=body)]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = ["alpha: " + wrapper.format(body=body.replace("3000", "200"))]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(
        item["targets"] == [{"entity": "alpha", "field": "long_text"}] for item in diagnostics
    )
    assert all(item["source"]["section"] == "features" for item in diagnostics)
    plan.entities[0].fields[1].max_length = 200
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)
    if wrapper.startswith("search"):
        plan.entities[0].fields[0].searchable = False
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features" and item["attribute"] == "searchable"
            for item in diagnostics
        )


def test_nested_inventory_preserves_adjacent_disabled_and_enabled_query_predicates():
    requirement, plan = scoped_inventory_case()
    plan.entities[0].fields[0].searchable = False
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = ["alpha: 定义字段（short_text 不可搜索、long_text 必须可搜索）"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features" and item["expected"] is False
        for item in diagnostics
    )


def test_repeated_subject_in_nested_inventory_keeps_contradictory_limits():
    requirement, plan = scoped_inventory_case()
    requirement.features = ["alpha: define(short_text max_length=200, short_text max_length=3000)"]
    for value, expected in [(200, 3000), (3000, 200)]:
        plan.entities[0].fields[0].max_length = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features" and item["expected"] == expected
            for item in diagnostics
        )


@pytest.mark.parametrize(
    "entity,text",
    [
        (
            "requests",
            "requests::创建请求（title 必填最长200、detail 必填最长3000、customer_id 必填外键、priority 必填枚举 普通/紧急）、编辑、归档",
        ),
        (
            "tasks",
            "tasks::创建任务（title 最长200、detail 最长3000、request_id 关联 requests）、分配",
        ),
    ],
)
def test_exact_2a4_yudao_parenthesized_numeric_inventory_keeps_each_field_limit(entity, text):
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = [
        text.replace("detail 必填最长3000", "detail 必填最长200").replace(
            "detail 最长3000", "detail 最长200"
        )
    ]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "features" for item in diagnostics)
    assert all(item["targets"] == [{"entity": entity, "field": "detail"}] for item in diagnostics)
    assert all(
        item["attribute"] == "max_length" and item["expected"] == 200 for item in diagnostics
    )


@pytest.mark.parametrize("kind", ["foreign_key", "many-to-one"])
@pytest.mark.parametrize("entity,index", [("requests", 1), ("tasks", 3)])
def test_exact_f6b_python_yudao_relation_facts_keep_assignee_scope(kind, entity, index):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {
        "business": {
            "relations": [
                {
                    "from": "requests",
                    "field": "customer_id",
                    "to": "customers",
                    "required": True,
                    "kind": kind,
                },
                {
                    "from": "requests",
                    "field": "assignee_id",
                    "to": "$users",
                    "required": False,
                    "kind": kind,
                },
                {
                    "from": "tasks",
                    "field": "request_id",
                    "to": "requests",
                    "required": True,
                    "kind": kind,
                },
                {
                    "from": "tasks",
                    "field": "assignee_id",
                    "to": "$users",
                    "required": False,
                    "kind": kind,
                },
            ]
        }
    }
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "assignee_id"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": "assignee_id"}]
    assert diagnostics[0]["source"]["path"] == f"business.relations.{index}"


@pytest.mark.parametrize("entity,index", [("requests", 1), ("tasks", 2)])
@pytest.mark.parametrize(
    "field_name,attribute,wrong,field_index",
    [
        ("title", "required", False, 0),
        ("detail", "max_length", 200, 1),
        ("assignee_id", "required", True, 3),
        ("resolved_at", "searchable", True, 5),
        ("due_at", "filterable", True, 6),
    ],
)
def test_exact_f6b_fastapi_nested_resource_fields_keep_scope_and_provenance(
    entity, index, field_name, attribute, wrong, field_index
):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"business": {"resources": ACTUAL_F6B_FASTAPI_RESOURCES}}
    assert coverage_gaps(requirement, plan) == []
    target = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == field_name
    )
    setattr(target, attribute, wrong)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": field_name}]
    assert diagnostics[0]["source"]["path"] == f"business.resources.{index}.fields.{field_index}"


# Exact diagnostic-only facts from final f6b; no candidate Plan is used as a fixture.
ACTUAL_F6B_FASTAPI_RESOURCES = [
    {
        "entity": "customers",
        "label": "客户",
        "features": ["native-crud", "append-only-audit", "archive-history"],
        "fields": [
            {
                "name": "name",
                "label": "客户名称",
                "kind": "text",
                "required": True,
                "max_length": 120,
                "searchable": True,
            },
            {
                "name": "organization",
                "label": "所属组织",
                "kind": "text",
                "required": False,
                "max_length": 160,
                "searchable": True,
            },
            {
                "name": "contact",
                "label": "联系方式",
                "kind": "text",
                "required": False,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "category",
                "label": "客户分类",
                "kind": "enum",
                "required": True,
                "choices": ["企业", "个人", "合作伙伴"],
                "filterable": True,
            },
        ],
    },
    {
        "entity": "requests",
        "label": "服务请求",
        "features": [
            "native-crud",
            "foreign-key-relations",
            "assignment",
            "named-state-transitions",
            "handling-notes",
            "append-only-audit",
            "archive-history",
            "in-app-reminders",
        ],
        "fields": [
            {
                "name": "title",
                "label": "请求标题",
                "kind": "text",
                "required": True,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "detail",
                "label": "请求详情",
                "kind": "text",
                "required": True,
                "max_length": 3000,
                "searchable": True,
            },
            {
                "name": "customer_id",
                "label": "关联客户",
                "kind": "text",
                "required": True,
                "relation": "customers",
            },
            {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": False,
                "relation": "$users",
            },
            {
                "name": "request_state",
                "label": "请求状态",
                "kind": "enum",
                "required": True,
                "choices": ["new", "active", "resolved"],
                "choice_labels": {"new": "待处理", "active": "处理中", "resolved": "已解决"},
            },
            {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "priority",
                "label": "优先级",
                "kind": "enum",
                "required": True,
                "choices": ["普通", "紧急"],
                "filterable": True,
            },
        ],
    },
    {
        "entity": "tasks",
        "label": "协作任务",
        "features": [
            "native-crud",
            "foreign-key-relations",
            "assignment",
            "named-state-transitions",
            "handling-notes",
            "append-only-audit",
            "archive-history",
            "in-app-reminders",
        ],
        "fields": [
            {
                "name": "title",
                "label": "任务标题",
                "kind": "text",
                "required": True,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "detail",
                "label": "任务详情",
                "kind": "text",
                "required": True,
                "max_length": 3000,
                "searchable": True,
            },
            {
                "name": "request_id",
                "label": "关联请求",
                "kind": "text",
                "required": True,
                "relation": "requests",
            },
            {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": False,
                "relation": "$users",
            },
            {
                "name": "task_state",
                "label": "任务状态",
                "kind": "enum",
                "required": True,
                "choices": ["new", "active", "resolved"],
                "choice_labels": {"new": "待处理", "active": "处理中", "resolved": "已解决"},
            },
            {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
        ],
    },
]
