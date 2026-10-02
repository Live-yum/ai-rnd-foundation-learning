"""Intent survives model omissions and cannot disappear behind a green design gate."""

import json

import pytest
from conftest import FixtureGateway, new_run, requirement
from news_case import news_plan, news_requirement

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.errors import UnsupportedScope
from workbench.flow import Workflow
from workbench.requirement_coverage import coverage_gaps, reconcile
from workbench.runtime import Runtime


def test_model_omission_preserves_confirmed_fact_features_and_acceptance():
    old = news_requirement()
    new = requirement()
    merged = reconcile(old.gate_dump(), new, [])
    assert merged.facts == old.facts
    assert set(old.features) <= set(merged.features)
    assert set(old.acceptance) <= set(merged.acceptance)
    assert merged.data_scope == old.data_scope


def test_fresh_source_backed_fact_update_and_explicit_deletion():
    old = requirement().model_copy(
        update={"facts": {"title_max_length": 250}, "features": ["CRUD", "标题搜索"]}
    )
    proposed = old.model_dump()
    proposed["facts"] = {"title_max_length": 500}
    proposed["features"] = ["CRUD"]
    proposed["changes"] = [
        {
            "section": "facts",
            "key": "title_max_length",
            "replacement": 500,
            "source_quote": "标题上限改为500",
        },
        {
            "section": "features",
            "key": "标题搜索",
            "replacement": None,
            "source_quote": "取消标题搜索",
        },
    ]
    model = Requirement.model_validate(proposed)
    ignored = reconcile(old.gate_dump(), model, ["继续智能推荐"])
    assert ignored.facts["title_max_length"] == 250
    assert "标题搜索" in ignored.features
    updated = reconcile(old.gate_dump(), model, ["标题上限改为500，取消标题搜索"])
    assert updated.facts["title_max_length"] == 500
    assert "标题搜索" not in updated.features
    assert not updated.changes


def test_quote_about_another_field_cannot_authorize_replacement():
    old = news_requirement()
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "facts",
            "key": "title_max_length",
            "replacement": 500,
            "source_quote": "正文上限改为500",
        }
    ]
    assert (
        reconcile(old.gate_dump(), Requirement.model_validate(proposed), ["正文上限改为500"]).facts[
            "title_max_length"
        ]
        == 250
    )


@pytest.mark.parametrize(
    "field,attribute,value",
    [
        ("title", "searchable", False),
        ("body", "searchable", False),
        ("category", "filterable", False),
        ("published_on", "date_range", False),
        ("title", "max_length", 80),
        ("body", "max_length", 250),
        ("title", "required", False),
        ("category", "required", True),
        ("category", "choices", ["其他"]),
    ],
)
def test_legacy_terraria_news_obligations_block_loss(field, attribute, value):
    approved = news_requirement()
    approved.features += ["标题与正文必填", "分类可选"]
    plan = news_plan()
    next(f for f in plan.entities[0].fields if f.name == field).__setattr__(attribute, value)
    assert coverage_gaps(approved, plan)


def test_news_complete_design_covers_legacy_and_typed_obligations():
    approved = news_requirement()
    approved.field_requirements = [
        FieldRequirement(field="title", searchable=True, required=True, max_length=250)
    ]
    assert coverage_gaps(approved, news_plan()) == []


def test_typed_arbitrary_field_and_entity_constraints():
    approved = requirement().model_copy(
        update={
            "field_requirements": [
                FieldRequirement(entity="task", field="priority", required=True, kind="integer")
            ]
        }
    )
    plan = news_plan()
    assert any("priority" in gap for gap in coverage_gaps(approved, plan))
    assert (
        reconcile(approved.gate_dump(), requirement(), []).field_requirements
        == approved.field_requirements
    )


def test_smart_replans_dropped_search_without_reanalysing_requirements(settings, store):
    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            self.calls.append(key)
            if schema is Requirement:
                return news_requirement()
            assert schema is Plan
            if key == "plan:1":
                result = news_plan()
                result.entities[0].fields[0].searchable = False
                return result
            assert payload["resolution_feedback"]["stage"] == "design"
            assert any("searchable" in gap for gap in payload["resolution_feedback"]["blocked"])
            assert payload["approved_requirement"]["facts"]["title_max_length"] == 250
            return news_plan()

    run = new_run(store)
    store.set_automation(run, True, "smart")
    gateway = Gateway(news_plan())
    with Runtime(settings, store, gateway) as runtime:
        runtime.tick()
    assert store.get_run(run)["status"] == "READY", store.get_run(run)
    assert gateway.calls == ["recommend:1", "plan:1", "plan:2"]


def test_legacy_package_cannot_erase_persisted_review_gap(settings, store, plan):
    run = new_run(store)
    workflow = Workflow(settings, store, FixtureGateway(plan))
    state = {
        "run_id": run,
        "template": "python-basic",
        "plan": plan.model_dump(),
        "verification": {"passed": True},
    }
    path = workflow.product(state).parent / "model-review.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"enabled": True, "uncovered_requirements": ["搜索未实现"]}), encoding="utf-8"
    )
    with pytest.raises(UnsupportedScope, match="搜索未实现"):
        workflow.package(state)
    assert json.loads(path.read_text(encoding="utf-8"))["uncovered_requirements"] == ["搜索未实现"]
    with pytest.raises(UnsupportedScope):
        workflow.require_review_clearance(state, {"enabled": True, "uncovered_requirements": []})
    workflow.require_review_clearance(
        state, {"enabled": True, "uncovered_requirements": []}, fresh=True
    )
    assert json.loads(path.read_text(encoding="utf-8"))["delivery_clearance"] is True


@pytest.mark.parametrize(
    "attribute,value",
    [("searchable", True), ("filterable", True), ("date_range", True), ("min_length", 1)],
)
def test_native_adapters_fail_closed_for_unimplemented_options(plan, attribute, value):
    from workbench.native_modules import validate_plan

    plan.data_scope = "shared"
    field = plan.entities[0].fields[0]
    if attribute == "date_range":
        # Keep a required text field for the independent native acceptance.
        field = plan.entities[0].fields[1]
        field.kind = "date"
    setattr(field, attribute, value)
    with pytest.raises(
        ValueError,
        match="Native adapters do not yet execute|Native enum/date/datetime fields require a business contract",
    ):
        validate_plan(plan)


def test_typed_field_constraint_accepts_explicit_single_value_correction():
    old = requirement().model_copy(
        update={
            "field_requirements": [FieldRequirement(field="title", max_length=250, searchable=True)]
        }
    )
    proposed = old.model_dump()
    proposed["changes"] = [
        {
            "section": "field_requirements",
            "key": ".title.max_length",
            "replacement": 500,
            "source_quote": "标题上限改为500",
        }
    ]
    changed = reconcile(old.gate_dump(), Requirement.model_validate(proposed), ["标题上限改为500"])
    assert changed.field_requirements[0].max_length == 500
    assert changed.field_requirements[0].searchable is True


def test_chinese_correction_reconciles_legacy_text_and_records_provenance(settings, store, plan):
    from conftest import decision

    search = "支持按标题进行关键词搜索"
    old = requirement().model_copy(
        update={
            "features": ["标题最多250字符", search],
            "acceptance": ["标题最多250字符", search],
            "facts": {"title_max_length": 250},
            "questions": ["是否需要修改？"],
        }
    )
    correction = "标题长度改为100字符，取消关键词搜索"

    class Gateway(FixtureGateway):
        def complete(self, rid, key, instruction, payload, schema):
            if schema is Requirement:
                if not payload["fresh_user_corrections"]:
                    return old
                assert payload["fresh_user_corrections"] == [correction]
                return Requirement.model_validate(
                    {
                        **old.model_dump(),
                        "questions": [],
                        "facts": {"title_max_length": 100},
                        "features": ["标题最多100字符"],
                        "acceptance": ["标题最多100字符"],
                        "changes": [
                            {
                                "section": "facts",
                                "key": "title_max_length",
                                "replacement": 100,
                                "source_quote": "标题长度改为100字符",
                            },
                            *[
                                {
                                    "section": section,
                                    "key": search,
                                    "replacement": None,
                                    "source_quote": "取消关键词搜索",
                                }
                                for section in ("features", "acceptance")
                            ],
                        ],
                    }
                )
            assert payload["approved_requirement"]["features"] == ["标题最多100字符"]
            assert payload["approved_requirement"]["facts"]["title_max_length"] == 100
            result = plan.model_copy(deep=True)
            result.entities[0].fields[0].max_length = 100
            return result

    run = new_run(store)
    with Runtime(settings, store, Gateway(plan)) as runtime:
        runtime.tick()
        decision(store, run, "answer", correction)
        store.set_automation(run, True, "smart-after-correction")
        runtime.tick()
    assert store.get_run(run)["status"] == "READY", store.get_run(run)
    ledger = json.loads(
        (settings.data_dir / "runs" / run / "requirement-ledger.json").read_text(encoding="utf-8")
    )
    entry = ledger[-1]
    assert entry["before"]["facts"]["title_max_length"] == 250
    assert entry["after"]["facts"]["title_max_length"] == 100
    assert len(entry["changes"]) == 3
    assert all(
        change["authorized"] and change["sources"][0]["user_message_index"] == 1
        for change in entry["changes"]
    )


def test_chinese_optional_correction_cannot_be_inverted_by_model():
    old = requirement().model_copy(
        update={"field_requirements": [FieldRequirement(field="category", required=True)]}
    )
    for value, expected in [(False, False), (True, True)]:
        proposed = old.model_dump()
        proposed["changes"] = [
            {
                "section": "field_requirements",
                "key": ".category.required",
                "replacement": value,
                "source_quote": "分类改为可选",
            }
        ]
        changed = reconcile(old.gate_dump(), Requirement.model_validate(proposed), ["分类改为可选"])
        assert changed.field_requirements[0].required is expected


def test_cancelled_search_description_does_not_require_search(plan):
    approved = requirement().model_copy(update={"features": ["不需要标题搜索"]})
    assert coverage_gaps(approved, plan) == []


@pytest.mark.parametrize("feature", ["标题和正文必填，并支持标题搜索和分类筛选", "标题正文搜索"])
def test_narrow_search_cancellation_cannot_delete_compound_requirement(feature):
    old = requirement().model_copy(update={"features": [feature]})
    proposed = old.model_dump()
    proposed["features"] = []
    proposed["changes"] = [
        {"section": "features", "key": feature, "replacement": None, "source_quote": "取消标题搜索"}
    ]
    changed = reconcile(old.gate_dump(), Requirement.model_validate(proposed), ["取消标题搜索"])
    assert feature in changed.features
