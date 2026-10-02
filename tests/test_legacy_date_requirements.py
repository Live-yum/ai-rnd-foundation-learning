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
