import pytest

from scripts.news_fixture import news_requirement, news_spec
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def test_unmodified_guided_browser_news_fixture_has_no_coverage_gap():
    requirement = Requirement.model_validate(news_requirement(True))
    plan = Plan.model_validate(news_spec())
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[2].date_range = False
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "key,description,field,flag",
    [
        ("日期区间", "包含起始日和结束日", "published_on", "date_range"),
        ("标题支持搜索", "按标题关键词查询", "title", "searchable"),
        ("分类可筛选", "按分类精确匹配", "category", "filterable"),
    ],
)
def test_descriptive_legacy_flags_still_require_executable_capability(
    key, description, field, flag
):
    raw = news_requirement(True)
    raw.update(facts={key: description}, features=[], acceptance=[])
    requirement = Requirement.model_validate(raw)
    plan = Plan.model_validate(news_spec())
    assert coverage_gaps(requirement, plan) == []
    target = next(f for f in plan.entities[0].fields if f.name == field)
    setattr(target, flag, False)
    assert any(flag in gap for gap in coverage_gaps(requirement, plan))


def test_malformed_typed_object_attribute_does_not_become_legacy_prose():
    raw = news_requirement(True)
    raw["facts"] = {"category": {"required": "not a boolean"}}
    assert coverage_gaps(Requirement.model_validate(raw), Plan.model_validate(news_spec()))


@pytest.mark.parametrize(
    "value,required", [(" False ", True), (" TRUE ", False), ("可选", False), ("非必填", False)]
)
def test_optional_scalar_normalizes_boolean_literal_before_inversion(value, required):
    raw = news_requirement(True)
    raw.update(facts={"分类是否可选": value}, features=[], acceptance=[])
    requirement = Requirement.model_validate(raw)
    plan = Plan.model_validate(news_spec())
    plan.entities[0].fields[-1].required = required
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].required = not required
    assert coverage_gaps(requirement, plan)


def test_numeric_scalar_flag_remains_invalid_not_prose():
    raw = news_requirement(True)
    raw["facts"] = {"发布日期支持日期范围": 1}
    assert coverage_gaps(Requirement.model_validate(raw), Plan.model_validate(news_spec()))


ORIGINAL_SETUP_FACTS = {
    "可用能力": "认证、用户隔离、增删改查、关键词搜索、精确筛选、日期范围筛选、枚举和字段长度校验",
    "模板": "python-basic",
    "前端": "simple-admin",
    "数据库": "SQLite",
    "数据范围": "per_user",
}


def test_original_setup_catalog_is_metadata_not_field_obligation():
    raw = news_requirement(True)
    raw["facts"].update(ORIGINAL_SETUP_FACTS)
    requirement = Requirement.model_validate(raw)
    before = requirement.model_dump()
    plan = Plan.model_validate(news_spec())
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    assert not plan.entities[0].fields[2].searchable
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[0].searchable = True
    plan.entities[0].fields[2].date_range = False
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))


def test_metadata_does_not_override_typed_required_obligation():
    from workbench.domain import FieldRequirement

    raw = news_requirement(True)
    raw["facts"].update(ORIGINAL_SETUP_FACTS)
    requirement = Requirement.model_validate(raw)
    requirement.field_requirements = [FieldRequirement(field="category", required=True)]
    assert any(
        "required" in gap for gap in coverage_gaps(requirement, Plan.model_validate(news_spec()))
    )


FEATURES = [
    "用户注册或登录后管理资讯；每位用户只能查看、搜索、新增、编辑和删除自己的资讯。",
    "资讯字段：标题、正文、发布日期、分类。标题和正文为必填文本；发布日期为必填日期；分类可选。",
    "标题最多250字符，正文最多3000字符；日期格式为YYYY-MM-DD。",
    "支持按标题或正文关键词搜索。",
    "支持按分类精确筛选，并支持按发布日期范围筛选；日期区间包含起始日和结束日。",
    "提供简单管理页面及对应的增删改查能力。",
]
ACCEPTANCE = [
    "用户可以新增、查看、编辑和删除自己的资讯记录。",
    "不同用户无法查看或操作彼此的资讯记录。",
    "标题或正文超过长度限制、必填字段缺失或日期格式无效时，系统拒绝保存并提示错误。",
    "关键词搜索、分类精确筛选和包含首尾日期的日期范围筛选均可正常使用，筛选条件可组合使用。",
    "分类不填写时仍可保存资讯。",
]
FACTS = {
    "模板": "FastAPI + 轻量管理页面",
    "前端": "simple-admin",
    "数据库": "sqlite",
    "数据范围": "per_user",
    "可用能力": "认证、用户隔离、增删改查、关键词搜索、精确筛选、日期范围筛选、枚举和字段长度校验",
    "日期区间": "包含起始日和结束日",
    "标题长度上限": "250字符",
    "正文长度上限": "3000字符",
    "分类是否必填": "否",
}


def original_requirement():
    raw = news_requirement(True)
    raw.update(features=FEATURES, acceptance=ACCEPTANCE, facts=FACTS)
    return Requirement.model_validate(raw)


def test_exact_original_requirement_matches_news_plan_without_mutation():
    requirement = original_requirement()
    before = requirement.model_dump()
    assert coverage_gaps(requirement, Plan.model_validate(news_spec())) == []
    assert requirement.model_dump() == before


@pytest.mark.parametrize(
    "field,flag",
    [
        ("title", "searchable"),
        ("body", "searchable"),
        ("category", "filterable"),
        ("published_on", "filterable"),
        ("published_on", "date_range"),
    ],
)
def test_original_requirement_still_blocks_missing_query_obligations(field, flag):
    plan = Plan.model_validate(news_spec())
    setattr(next(f for f in plan.entities[0].fields if f.name == field), flag, False)
    assert any(flag in gap for gap in coverage_gaps(original_requirement(), plan))


def test_combined_query_clause_retains_shared_search_targets():
    raw = news_requirement(True)
    raw.update(features=["标题、正文搜索和分类筛选"], acceptance=[], facts={})
    requirement = Requirement.model_validate(raw)
    plan = Plan.model_validate(news_spec())
    assert coverage_gaps(requirement, plan) == []
    for field in ["title", "body"]:
        changed = plan.model_copy(deep=True)
        next(f for f in changed.entities[0].fields if f.name == field).searchable = False
        assert coverage_gaps(requirement, changed)


def test_exact_original_legacy_blocked_run_recovers_without_losing_facts(tmp_path, monkeypatch):
    from workbench.flow import Workflow
    from workbench.runtime import Runtime
    from workbench.settings import Settings
    from workbench.store import Store

    def old_requirements(self, state):
        raw = dict(state["requirement"])
        raw.pop("limitations", None)
        outcome = self.gate(
            state,
            "clarification",
            {"requirement": raw, "ready": False},
            ["answer", "reject"],
            False,
        )
        if outcome["decision"] in {"answer", "revise", "recommend"}:
            outcome["round"] = state["round"] + 1
        return outcome

    class Stale:
        def complete(self, run, key, instruction, payload, schema):
            assert schema is Requirement
            value = original_requirement()
            value.questions = ["需要个人资讯管理页面，还是无需登录的公众资讯网站？"]
            value.unsupported = ["自动从外部网站采集资讯不受支持", "匿名公众网站不受支持"]
            value.limitations = []
            return value

    class Fixed:
        def complete(self, run, key, instruction, payload, schema):
            if schema is Requirement:
                value = original_requirement()
                value.facts = {}  # Model omission must not erase persisted confirmed facts.
                return value
            assert schema is Plan
            assert payload["approved_requirement"]["facts"] == FACTS
            return Plan.model_validate(news_spec())

    settings = Settings(data_dir=tmp_path / "state", install_products=False, _env_file=None)
    store = Store(settings)
    store.migrate()
    try:
        project = store.create_project("原资讯需求恢复", "project")
        run = store.create_run(
            project["id"], {"requirement": "游戏资讯", "intelligent": True}, "run"
        )["run_id"]
        with monkeypatch.context() as patch:
            patch.setattr(Workflow, "requirements", old_requirements)
            with Runtime(settings, store, Stale()) as runtime:
                runtime.tick()
        assert store.get_run(run)["status"] == "BLOCKED"
        assert store.get_run(run)["pending"]["data"]["requirement"]["facts"] == FACTS
        store.set_automation(run, True, "resume-existing")
        with Runtime(settings, store, Fixed()) as runtime:
            runtime.tick()
        final = store.get_run(run)
        assert final["status"] == "READY", final
        assert final["result"]["cleanroom"]["passed"]
        assert len(store.messages(run)) == 1
    finally:
        store.engine.dispose()


def test_operation_only_continuation_keeps_previous_field_target():
    raw = news_requirement(True)
    raw.update(features=["标题支持关键词搜索和精确筛选"], acceptance=[], facts={})
    requirement = Requirement.model_validate(raw)
    plan = Plan.model_validate(news_spec())
    assert plan.entities[0].fields[-1].filterable
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[0].filterable = True
    assert coverage_gaps(requirement, plan) == []
