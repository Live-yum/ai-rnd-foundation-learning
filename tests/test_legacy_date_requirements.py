"""Date-shaped presentation text must not invent an application field."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def case(text="", section="features"):
    plan = Plan(
        title="Record register",
        data_scope="shared",
        entities=[
            {
                "name": "records",
                "description": "Records",
                "fields": [
                    {"name": "name", "kind": "text"},
                    {"name": "event_on", "kind": "text"},
                    {"name": "recorded_at", "kind": "datetime"},
                ],
            }
        ],
        acceptance=["Store records"],
    )
    requirement = Requirement(
        summary="Record register",
        users=["Staff"],
        data_scope="shared",
        features=[],
        acceptance=[],
    )
    if section == "facts":
        requirement.facts = {"notes": text}
    else:
        setattr(requirement, section, [text])
    return requirement, plan


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize(
    "text",
    [
        "所有 datetime 以 UTC 存储，仅作为时间戳，界面按本地时区以 YYYY-MM-DD HH:mm 展示。",
        "recorded_at 按日期格式 YYYY-MM-DD HH:mm 展示。",
        "日期显示格式统一为 YYYY-MM-DD。",
        "默认日期格式 YYYY-MM-DD。",
        "默认真实日期格式 YYYY-MM-DD。",
        "日期格式为 YYYY-MM-DD。",
        "recorded_at 日期格式为 YYYY-MM-DD HH:mm。",
        "records.event_on 日期格式为 YYYY-MM-DD。",
        "本应用不需要 published_on 真实日期字段。",
        "示例：published_on 使用真实日期。",
        "日期显示格式统一为 YYYY-MM-DD；resolved_at、due_at 等 datetime 仅存储时间戳，"
        "默认不参与搜索、筛选与日期范围查询。",
        "本应用不需要真实日期字段。",
        "本应用无需真实日期。",
        "不要求 records.event_on 使用真实日期。",
        "records.event_on 不使用真实日期。",
        "records.event_on 无需 YYYY-MM-DD 日期格式校验。",
        "真实日期字段不需要。",
        "模板支持真实日期，例如 YYYY-MM-DD。",
        "可用能力：真实日期类型、YYYY-MM-DD。",
        "示例：records.event_on 使用真实日期。",
        "如果使用真实日期字段，则格式为 YYYY-MM-DD。",
        "Template capability example: real date in YYYY-MM-DD format.",
        "records.event_on does not require a real date.",
    ],
)
def test_format_negation_and_catalog_prose_do_not_require_a_date_field(section, text):
    requirement, plan = case(text, section)
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    assert all(field.kind != "date" for field in plan.entities[0].fields)


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 必须使用真实日期。",
        "records.event_on（真实日期）。",
        "records.event_on 类型为 date。",
        "records.event_on 为日期类型。",
        "records.event_on 输入必须按 YYYY-MM-DD 校验。",
        "records.event_on uses a real date.",
        "records.event_on 必须使用真实日期，界面显示 YYYY-MM-DD。",
        "模板支持真实日期；records.event_on 必须使用真实日期。",
        "模板支持真实日期，records.event_on 必须使用真实日期。",
        "无需真实日期示例，但 records.event_on 必须使用真实日期。",
    ],
)
def test_explicit_field_date_contract_still_requires_executable_date(section, text):
    requirement, plan = case(text, section)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["code"] == "date_kind"
        and item["targets"] == [{"entity": "records", "field": "event_on"}]
        for item in diagnostics
    )
    plan.entities[0].fields[1].kind = "date"
    assert coverage_gaps(requirement, plan) == []


def test_another_entity_date_cannot_satisfy_explicit_missing_or_wrong_field():
    requirement, plan = case("records.event_on 必须使用真实日期。")
    plan.entities.append(
        plan.entities[0].model_copy(
            deep=True,
            update={"name": "archive"},
        )
    )
    plan.entities[1].fields[1].kind = "date"
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields.pop(1)
    assert coverage_gaps(requirement, plan)


def test_all_explicit_date_subjects_must_be_dates():
    requirement, plan = case("records.event_on 和 records.recorded_at 必须使用真实日期。")
    plan.entities[0].fields[1].kind = "date"
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[2].kind = "date"
    assert coverage_gaps(requirement, plan) == []


def test_typed_date_contract_cannot_be_suppressed_by_formatting_or_negative_metadata():
    requirement, plan = case("默认日期格式 YYYY-MM-DD；本应用不需要真实日期示例。")
    requirement.field_requirements = [
        FieldRequirement(entity="records", field="event_on", kind="date")
    ]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "field_requirements" and item["attribute"] == "kind"
        for item in diagnostics
    )
    plan.entities[0].fields[1].kind = "date"
    assert coverage_gaps(requirement, plan) == []


def test_unscoped_explicit_real_date_feature_still_requires_a_date():
    requirement, plan = case("真实日期录入与校验")
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[1].kind = "date"
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("key", ["template_capabilities", "可用能力", "示例"])
def test_fact_catalog_heading_retains_its_context(key):
    requirement, plan = case()
    requirement.facts = {key: "records.event_on 使用真实日期"}
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 起止日期范围筛选",
        "records.event_on 日期区间过滤",
        "records.event_on 包含首尾的日期范围查询",
        "records.event_on date range filter",
        "records.event_on date-range filtering",
        "records.event_on date_range queries",
        "Filter by date range on records.event_on",
        "records.event_on 需要日期范围筛选，无需精确筛选",
        "records.event_on does not require exact filtering, but supports date range filtering",
    ],
)
def test_range_queries_never_require_an_additional_exact_filter(text, section):
    requirement, plan = case(text, section)
    field = plan.entities[0].fields[1]
    field.kind = "date"
    field.date_range = True
    assert field.filterable is False
    before = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    field.date_range = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(row["attribute"] == "date_range" for row in diagnostics)
    assert not any(row["attribute"] == "filterable" for row in diagnostics)


@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 日期范围筛选和精确筛选",
        "records.event_on 精确筛选与日期范围过滤",
        "records.event_on date range filter and exact filter",
        "records.event_on exact filtering and date-range filtering",
    ],
)
def test_an_explicit_exact_filter_stays_independent_of_the_range_query(text):
    requirement, plan = case(text)
    field = plan.entities[0].fields[1]
    field.kind, field.date_range, field.filterable = "date", True, True
    assert coverage_gaps(requirement, plan) == []
    for flag in ("date_range", "filterable"):
        setattr(field, flag, False)
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(row["attribute"] == flag for row in diagnostics)
        setattr(field, flag, True)


@pytest.mark.parametrize(
    "text",
    [
        "records: event_on 日期范围筛选，name 精确筛选",
        "records: name 精确筛选，event_on 日期范围过滤",
        "records: event_on date range filtering, name exact filtering",
    ],
)
def test_range_and_exact_queries_bind_to_their_own_named_fields(text):
    requirement, plan = case(text)
    exact, ranged = plan.entities[0].fields[:2]
    exact.filterable = True
    ranged.kind, ranged.date_range = "date", True
    assert coverage_gaps(requirement, plan) == []
    for field, flag in ((exact, "filterable"), (ranged, "date_range")):
        setattr(field, flag, False)
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            row["attribute"] == flag
            and row["targets"] == [{"entity": "records", "field": field.name}]
            for row in diagnostics
        )
        setattr(field, flag, True)


@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize(
    "text",
    [
        "name 和含边界日期区间筛选",
        "name 与 event_on 起止日期范围过滤",
        "records: name、recorded_at 和 event_on 日期范围筛选",
        "records: name and inclusive date range filtering",
        "records: name, recorded_at and event_on date-range filtering",
        "name and inclusive date range filtering on records.event_on",
    ],
)
def test_a_shared_range_filter_verb_still_binds_coordinated_non_date_fields(text, section):
    requirement, plan = case(text, section)
    name, event_on, recorded_at = plan.entities[0].fields
    name.filterable = recorded_at.filterable = True
    event_on.kind, event_on.date_range = "date", True
    before = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert event_on.filterable is False
    assert (requirement.model_dump(), plan.model_dump()) == before
    targets = [(name, "filterable"), (event_on, "date_range")]
    if "recorded_at" in text:
        targets.append((recorded_at, "filterable"))
    for field, flag in targets:
        setattr(field, flag, False)
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            row["attribute"] == flag
            and row["targets"] == [{"entity": "records", "field": field.name}]
            for row in diagnostics
        )
        setattr(field, flag, True)


@pytest.mark.parametrize(
    "text",
    [
        "event_on 和 recorded_at 日期范围筛选",
        "records: event_on and recorded_at date-range filtering",
        "event_on、name 和 recorded_at 含边界日期区间过滤",
        "event_on, name and recorded_at inclusive date range filtering",
    ],
)
def test_coordinated_date_fields_share_only_the_range_operation(text):
    requirement, plan = case(text)
    name, event_on, recorded_at = plan.entities[0].fields
    name.filterable = True
    for field in (event_on, recorded_at):
        field.kind, field.date_range = "date", True
    assert coverage_gaps(requirement, plan) == []
    assert not event_on.filterable and not recorded_at.filterable
    for field in (event_on, recorded_at):
        field.date_range = False
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(row["attribute"] == "date_range" for row in diagnostics)
        assert not any(row["attribute"] == "filterable" for row in diagnostics)
        field.date_range = True
    if "name" in text:
        name.filterable = False
        assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text",
    [
        "name（必填）和 event_on 日期范围筛选",
        "name is required and event_on date range filtering",
        "name，event_on 日期范围筛选",
        "name; event_on date range filtering",
        "name 和日期范围筛选结果展示",
        "name and date range filter results are displayed",
        "name 和 event_on 不需要日期范围筛选",
        "name and event_on does not require date range filtering",
    ],
)
def test_context_or_completed_field_descriptions_do_not_share_a_range_filter_verb(text):
    requirement, plan = case(text)
    plan.entities[0].fields[1].kind = "date"
    plan.entities[0].fields[1].date_range = True
    assert all(not field.filterable for field in plan.entities[0].fields)
    assert coverage_gaps(requirement, plan) == []


def test_shared_filter_projection_keeps_the_original_entity_scope():
    requirement, plan = case("records: name 和 event_on 日期范围筛选")
    name, event_on = plan.entities[0].fields[:2]
    name.filterable, event_on.kind, event_on.date_range = True, "date", True
    archive = plan.entities[0].model_copy(deep=True, update={"name": "archive"})
    for field in archive.fields:
        field.filterable = field.date_range = False
    plan.entities.append(archive)
    assert coverage_gaps(requirement, plan) == []
    name.filterable = False
    archive.fields[0].filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        row["attribute"] == "filterable"
        and row["targets"] == [{"entity": "records", "field": "name"}]
        for row in diagnostics
    )


@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 禁止精确筛选，支持日期范围查询",
        "records.event_on must not allow exact filtering, supports date range filtering",
    ],
)
def test_range_queries_still_enforce_an_explicit_exact_filter_prohibition(text):
    requirement, plan = case(text)
    field = plan.entities[0].fields[1]
    field.kind, field.date_range = "date", True
    assert coverage_gaps(requirement, plan) == []
    field.filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(row["attribute"] == "filterable" and row["expected"] is False for row in diagnostics)


@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 禁止日期范围筛选，必须精确筛选",
        "records.event_on must not support date range filtering, requires exact filtering",
        "records.event_on date_range=false and filterable=true",
    ],
)
def test_disabling_a_range_query_does_not_disable_its_explicit_exact_filter(text):
    requirement, plan = case(text)
    field = plan.entities[0].fields[1]
    field.kind, field.filterable = "date", True
    assert coverage_gaps(requirement, plan) == []
    field.date_range = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(row["attribute"] == "date_range" and row["expected"] is False for row in diagnostics)
    assert not any(row["attribute"] == "filterable" for row in diagnostics)


@pytest.mark.parametrize(
    "text",
    [
        "records.event_on 不需要日期范围筛选，必须精确筛选",
        "records.event_on does not require date range filtering, requires exact filtering",
    ],
)
def test_an_unrequested_range_query_is_not_a_positive_or_negative_obligation(text):
    requirement, plan = case(text)
    field = plan.entities[0].fields[1]
    field.kind, field.filterable = "date", True
    for value in (False, True):
        field.date_range = value
        assert coverage_gaps(requirement, plan) == []


def test_range_wording_cannot_override_an_explicit_typed_exact_filter_prohibition():
    requirement, plan = case("records.event_on 日期范围筛选")
    field = plan.entities[0].fields[1]
    field.kind, field.date_range = "date", True
    requirement.field_requirements = [
        FieldRequirement(entity="records", field="event_on", filterable=False, date_range=True)
    ]
    assert coverage_gaps(requirement, plan) == []
    field.filterable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        row["source"]["section"] == "field_requirements" and row["attribute"] == "filterable"
        for row in diagnostics
    )
