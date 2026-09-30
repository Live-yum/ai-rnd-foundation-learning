import pytest

from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def case(facts):
    raw = news_requirement(True)
    raw["facts"] = facts
    return Requirement.model_validate(raw), Plan.model_validate(news_spec())


@pytest.mark.parametrize(
    "facts",
    [
        {"category": {"required": False, "choices": ["资讯", "攻略", "大神"]}},
        {"category_required": False},
        {"category_required": "False"},
        {"news": {"category": {"required": False, "filterable": True, "searchable": False}}},
    ],
)
def test_optional_structured_facts_are_not_prose(facts):
    requirement, plan = case(facts)
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "facts",
    [
        {"category": {"required": True}},
        {"category_required": True},
        {"category_required": "true"},
    ],
)
def test_true_required_obligation_still_blocks_optional_field(facts):
    requirement, plan = case(facts)
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


def test_false_required_obligation_still_blocks_required_field():
    requirement, plan = case({"category": {"required": False}})
    plan.entities[0].fields[-1].required = True
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("typed", [True, False])
def test_enum_membership_is_order_independent_but_cannot_drop_or_add(typed):
    requirement, plan = case({} if typed else {"category": {"choices": ["大神", "资讯", "攻略"]}})
    if typed:
        requirement.field_requirements = [
            FieldRequirement(field="category", choices=["大神", "资讯", "攻略"])
        ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].choices = ["资讯", "攻略"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[-1].choices = ["资讯", "攻略", "大神", "额外"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


def test_structured_lengths_preserve_both_bounds_and_flag_negation():
    requirement, plan = case(
        {
            "title": {"min_length": 1, "max_length": 250, "searchable": True},
            "category": {"searchable": False, "filterable": True},
        }
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 300
    plan.entities[0].fields[-1].searchable = True
    gaps = coverage_gaps(requirement, plan)
    assert any("max_length" in gap for gap in gaps)
    assert any("searchable" in gap for gap in gaps)


def test_malformed_boolean_is_not_silently_truthy():
    requirement, plan = case({"category": {"required": "no idea"}})
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "facts",
    [
        {"fields": [{"name": "category", "required": False, "choices": ["大神", "攻略", "资讯"]}]},
        {"category": None, "category_required": None},
        {"category": '{"required": false, "filterable": true}'},
        {"notes": ["confirmed", "read only"], "category": {"required": False}},
        {"fields": [None, {"field": "category", "required": False}]},
    ],
)
def test_recursive_and_legacy_json_facts_keep_types(facts):
    requirement, plan = case(facts)
    assert coverage_gaps(requirement, plan) == []


def test_conflicting_true_typed_and_false_fact_remains_blocked():
    requirement, plan = case({"category": {"required": False}})
    requirement.field_requirements = [FieldRequirement(field="category", required=True)]
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[-1].required = True
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("fact", [{"required": 0}, {"max_length": True}])
def test_booleans_and_integers_are_not_interchangeable(fact):
    requirement, plan = case({"category": fact})
    assert coverage_gaps(requirement, plan)


def test_legacy_string_length_fact_preserved():
    requirement, plan = case({"title_max_length": "250字符"})
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 251
    assert any("max_length" in gap for gap in coverage_gaps(requirement, plan))


def test_invalid_scalar_enum_options_remain_blocked():
    requirement, plan = case({"category": ["资讯", 3]})
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("required", [True, False])
def test_legacy_chinese_boolean_required_facts_keep_value(required):
    requirement, plan = case({"分类是否必填": required})
    gaps = coverage_gaps(requirement, plan)
    assert bool(gaps) is required
    plan.entities[0].fields[-1].required = True
    gaps = coverage_gaps(requirement, plan)
    # The baseline feature independently requires optional; assert the fact's
    # required constraint specifically rather than silently overriding it.
    assert any(".required=" in gap for gap in gaps) is not required


def test_nested_legacy_description_retains_filter_obligation():
    requirement, plan = case({"category": {"required": False, "说明": "分类必须支持筛选"}})
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any("filterable" in gap and "说明" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("optional", [True, False])
def test_chinese_optional_boolean_inverse_polarity(optional):
    requirement, plan = case({"分类可选": optional})
    gaps = coverage_gaps(requirement, plan)
    assert any(".required=" in gap for gap in gaps) is not optional
    plan.entities[0].fields[-1].required = True
    gaps = coverage_gaps(requirement, plan)
    assert any(".required=" in gap for gap in gaps) is optional


def test_explicit_fact_entity_qualifier_is_preserved():
    requirement, plan = case(
        {"fields": [{"entity": "news", "field": "category", "required": False}]}
    )
    # Limit this case to structural obligations; legacy global feature text has
    # no entity qualifier and intentionally continues its existing interpretation.
    requirement.features = []
    requirement.acceptance = []
    other = plan.entities[0].model_copy(deep=True)
    other.name = "other"
    other.fields[-1].required = True
    plan.entities.append(other)
    assert coverage_gaps(requirement, plan) == []
    requirement.facts["fields"][0]["entity"] = "missing"
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "key,field,attribute",
    [
        ("标题支持搜索", "title", "searchable"),
        ("标题支持检索", "title", "searchable"),
        ("分类可筛选", "category", "filterable"),
        ("分类可过滤", "category", "filterable"),
        ("发布日期支持日期范围", "published_on", "date_range"),
        ("发布日期支持日期区间筛选", "published_on", "date_range"),
    ],
)
@pytest.mark.parametrize("enabled", [True, False])
def test_legacy_chinese_boolean_query_flags_keep_polarity(key, field, attribute, enabled):
    requirement, plan = case({key: enabled})
    requirement.features = []
    requirement.acceptance = []
    item = next(item for item in plan.entities[0].fields if item.name == field)
    setattr(item, attribute, enabled)
    assert coverage_gaps(requirement, plan) == []
    setattr(item, attribute, not enabled)
    assert any("." + attribute + "=" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "key,field,attribute",
    [
        ("category required", "category", "required"),
        ("category REQUIRED", "category", "required"),
        ("title searchable", "title", "searchable"),
        ("category filterable", "category", "filterable"),
        ("published_on date_range", "published_on", "date_range"),
        ("category\trequired", "category", "required"),
    ],
)
@pytest.mark.parametrize("enabled", [True, False])
def test_legacy_whitespace_canonical_flags_keep_polarity(key, field, attribute, enabled):
    requirement, plan = case({key: enabled})
    requirement.features = []
    requirement.acceptance = []
    item = next(item for item in plan.entities[0].fields if item.name == field)
    setattr(item, attribute, enabled)
    assert coverage_gaps(requirement, plan) == []
    setattr(item, attribute, not enabled)
    assert any("." + attribute + "=" in gap for gap in coverage_gaps(requirement, plan))
