# tests/test_description_facts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.news_fixture`、`workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_unmodified_guided_browser_news_fixture_has_no_coverage_gap`（L8–L13）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L11断言`coverage_gaps(requirement, plan) == []`；L13断言`any("date_range" in gap for gap in coverage_gaps(requirement, plan))`。 调用`Requirement.model_validate`、`news_requirement`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_descriptive_legacy_flags_still_require_executable_capability`（L24–L34）：接收`key`、`description`、`field`、`flag`。 控制顺序：L31断言`coverage_gaps(requirement, plan) == []`；L34断言`any(flag in gap for gap in coverage_gaps(requirement, plan))`。 调用`news_requirement`、`raw.update`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`next`、`setattr`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_typed_object_attribute_does_not_become_legacy_prose`（L37–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L40断言`coverage_gaps(Requirement.model_validate(raw), Plan.model_validate(news_spec()))`。 调用`news_requirement`、`coverage_gaps`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_scalar_normalizes_boolean_literal_before_inversion`（L46–L54）：接收`value`、`required`。 控制顺序：L52断言`coverage_gaps(requirement, plan) == []`；L54断言`coverage_gaps(requirement, plan)`。 调用`news_requirement`、`raw.update`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_numeric_scalar_flag_remains_invalid_not_prose`（L57–L60）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L60断言`coverage_gaps(Requirement.model_validate(raw), Plan.model_validate(news_spec()))`。 调用`news_requirement`、`coverage_gaps`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_setup_catalog_is_metadata_not_field_obligation`（L72–L85）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78断言`coverage_gaps(requirement, plan) == []`；L79断言`requirement.model_dump() == before`；L80断言`not plan.entities[0].fields[2].searchable`；L82断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`；L85断言`any("date_range" in gap for gap in coverage_gaps(requirement, plan))`。 调用`news_requirement`、`raw["facts"].update`、`Requirement.model_validate`、`requirement.model_dump`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metadata_does_not_override_typed_required_obligation`（L88–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L95断言`any( "required" in gap for gap in coverage_gaps(requirement, Plan.model_validate(news…`。 调用`news_requirement`、`raw["facts"].update`、`Requirement.model_validate`、`FieldRequirement`、`any`、`coverage_gaps`、`Plan.model_validate`、`news_spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `original_requirement`（L128–L131）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`news_requirement`、`raw.update`、`Requirement.model_validate`。 返回路径：L131的`Requirement.model_validate(raw)`。
- `test_exact_original_requirement_matches_news_plan_without_mutation`（L134–L138）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L137断言`coverage_gaps(requirement, Plan.model_validate(news_spec())) == []`；L138断言`requirement.model_dump() == before`。 调用`original_requirement`、`requirement.model_dump`、`coverage_gaps`、`Plan.model_validate`、`news_spec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_requirement_still_blocks_missing_query_obligations`（L150–L153）：接收`field`、`flag`。 控制顺序：L153断言`any(flag in gap for gap in coverage_gaps(original_requirement(), plan))`。 调用`Plan.model_validate`、`news_spec`、`setattr`、`next`、`any`、`coverage_gaps`、`original_requirement`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_date_range_requirement_does_not_invent_an_exact_date_filter`（L156–L169）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L158断言`requirement.field_requirements == []`；L163断言`coverage_gaps(requirement, plan) == []`；L164断言`(requirement.model_dump(), plan.model_dump()) == before`；L167断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L168断言`any(row["attribute"] == "date_range" for row in diagnostics)`；L169断言`not any(row["attribute"] == "filterable" for row in diagnostics)`。 调用`original_requirement`、`Plan.model_validate`、`news_spec`、`next`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_an_explicit_exact_and_range_date_requirement_keeps_both_obligations`（L180–L189）：接收`obligation`、`flag`。 控制顺序：L184断言`coverage_gaps(requirement, plan) == []`；L188断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L189断言`any(row["attribute"] == flag for row in diagnostics)`。 调用`original_requirement`、`requirement.features.append`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`next`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_query_clause_retains_shared_search_targets`（L192–L201）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L197断言`coverage_gaps(requirement, plan) == []`；L198遍历`["title", "body"]`；L201断言`coverage_gaps(requirement, changed)`。 调用`news_requirement`、`raw.update`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`、`coverage_gaps`、`plan.model_copy`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts`（L204–L265）：接收`tmp_path`、`monkeypatch`。 控制顺序：L255断言`store.get_run(run)["status"] == "BLOCKED"`；L256断言`store.get_run(run)["pending"]["data"]["requirement"]["facts"] == FACTS`；L261断言`final["status"] == "READY"`；L262断言`final["result"]["cleanroom"]["passed"]`；L263断言`len(store.messages(run)) == 1`。 调用`Settings`、`Store`、`store.migrate`、`store.create_project`、`store.create_run`、`monkeypatch.context`、`patch.setattr`、`Runtime`、`Stale`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts.old_requirements`（L210–L222）：接收`state`。 控制顺序：L220按`outcome["decision"] in {"answer", "revise", "recommend"}`分支。 调用`dict`、`raw.pop`、`self.gate`。 返回路径：L222的`outcome`。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts.Stale`（L224–L231）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts.Stale.complete`（L225–L231）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L226断言`schema is Requirement`。 调用`original_requirement`。 返回路径：L231的`value`。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts.Fixed`（L233–L241）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_exact_original_legacy_blocked_run_recovers_without_losing_facts.Fixed.complete`（L234–L241）：接收`run`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L235按`schema is Requirement`分支；L239断言`schema is Plan`；L240断言`payload["approved_requirement"]["facts"] == FACTS`。 调用`original_requirement`、`Plan.model_validate`、`news_spec`。 返回路径：L238的`value`；L241的`Plan.model_validate(news_spec())`。
- `test_operation_only_continuation_keeps_previous_field_target`（L268–L276）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L273断言`plan.entities[0].fields[-1].filterable`；L274断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`；L276断言`coverage_gaps(requirement, plan) == []`。 调用`news_requirement`、`raw.update`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_description_facts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L276。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11885`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_description_facts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fcc88882b6fa574fb4d1208de2f449879dcf0588a0139f8f228c06e98b19208a"} -->
````python
# tests/test_description_facts.py
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
        ("published_on", "date_range"),
    ],
)
def test_original_requirement_still_blocks_missing_query_obligations(field, flag):
    plan = Plan.model_validate(news_spec())
    setattr(next(f for f in plan.entities[0].fields if f.name == field), flag, False)
    assert any(flag in gap for gap in coverage_gaps(original_requirement(), plan))


def test_original_date_range_requirement_does_not_invent_an_exact_date_filter():
    requirement = original_requirement()
    assert requirement.field_requirements == []
    plan = Plan.model_validate(news_spec())
    date = next(field for field in plan.entities[0].fields if field.name == "published_on")
    date.filterable = False
    before = requirement.model_dump(), plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == before
    date.date_range = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(row["attribute"] == "date_range" for row in diagnostics)
    assert not any(row["attribute"] == "filterable" for row in diagnostics)


@pytest.mark.parametrize(
    "obligation",
    [
        "发布日期必须支持精确筛选和日期范围筛选",
        "published_on requires exact filtering and date range filtering",
    ],
)
@pytest.mark.parametrize("flag", ["filterable", "date_range"])
def test_an_explicit_exact_and_range_date_requirement_keeps_both_obligations(obligation, flag):
    requirement = original_requirement()
    requirement.features.append(obligation)
    plan = Plan.model_validate(news_spec())
    assert coverage_gaps(requirement, plan) == []
    date = next(field for field in plan.entities[0].fields if field.name == "published_on")
    setattr(date, flag, False)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(row["attribute"] == flag for row in diagnostics)


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
````
