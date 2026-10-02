# tests/test_requirement_coverage.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.errors`、`workbench.flow`、`workbench.requirement_coverage`、`workbench.runtime`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_model_omission_preserves_confirmed_fact_features_and_acceptance`（L16–L23）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L20断言`merged.facts == old.facts`；L21断言`set(old.features) <= set(merged.features)`；L22断言`set(old.acceptance) <= set(merged.acceptance)`；L23断言`merged.data_scope == old.data_scope`。 调用`news_requirement`、`requirement`、`reconcile`、`old.gate_dump`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fresh_source_backed_fact_update_and_explicit_deletion`（L26–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L49断言`ignored.facts["title_max_length"] == 250`；L50断言`"标题搜索" in ignored.features`；L52断言`updated.facts["title_max_length"] == 500`；L53断言`"标题搜索" not in updated.features`；L54断言`not updated.changes`。 调用`requirement().model_copy`、`requirement`、`old.model_dump`、`Requirement.model_validate`、`reconcile`、`old.gate_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_quote_about_another_field_cannot_authorize_replacement`（L57–L73）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L68断言`reconcile(old.gate_dump(), Requirement.model_validate(proposed), ["正文上限改为500"]).facts…`。 调用`news_requirement`、`old.model_dump`、`reconcile`、`old.gate_dump`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_terraria_news_obligations_block_loss`（L90–L95）：接收`field`、`attribute`、`value`。 控制顺序：L95断言`coverage_gaps(approved, plan)`。 调用`news_requirement`、`news_plan`、`next(f for f in plan.entities[0].fields if f.name == field).__set…`、`next`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_news_complete_design_covers_legacy_and_typed_obligations`（L98–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103断言`coverage_gaps(approved, news_plan()) == []`。 调用`news_requirement`、`FieldRequirement`、`coverage_gaps`、`news_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typed_arbitrary_field_and_entity_constraints`（L106–L119）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L115断言`any("priority" in gap for gap in coverage_gaps(approved, plan))`；L116断言`reconcile(approved.gate_dump(), requirement(), []).field_requirements == approved.fie…`。 调用`requirement().model_copy`、`requirement`、`FieldRequirement`、`news_plan`、`any`、`coverage_gaps`、`reconcile`、`approved.gate_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smart_replans_dropped_search_without_reanalysing_requirements`（L122–L144）：接收`settings`、`store`。 控制顺序：L143断言`store.get_run(run)["status"] == "READY"`；L144断言`gateway.calls == ["recommend:1", "plan:1", "plan:2"]`。 调用`new_run`、`store.set_automation`、`Gateway`、`news_plan`、`Runtime`、`runtime.tick`、`store.get_run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smart_replans_dropped_search_without_reanalysing_requirements.Gateway`（L123–L136）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_smart_replans_dropped_search_without_reanalysing_requirements.Gateway.complete`（L124–L136）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L126按`schema is Requirement`分支；L128断言`schema is Plan`；L129按`key == "plan:1"`分支；L133断言`payload["resolution_feedback"]["stage"] == "design"`；L134断言`any("searchable" in gap for gap in payload["resolution_feedback"]["blocked"])`；L135断言`payload["approved_requirement"]["facts"]["title_max_length"] == 250`。 调用`self.calls.append`、`news_requirement`、`news_plan`、`any`。 返回路径：L127的`news_requirement()`；L132的`result`；L136的`news_plan()`。
- `test_legacy_package_cannot_erase_persisted_review_gap`（L147–L169）：接收`settings`、`store`、`plan`。 控制顺序：L163断言`json.loads(path.read_text(encoding="utf-8"))["uncovered_requirements"] == ["搜索未实现"]`；L169断言`json.loads(path.read_text(encoding="utf-8"))["delivery_clearance"] is True`。 调用`new_run`、`Workflow`、`FixtureGateway`、`plan.model_dump`、`workflow.product`、`path.parent.mkdir`、`path.write_text`、`json.dumps`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_adapters_fail_closed_for_unimplemented_options`（L176–L190）：接收`plan`、`attribute`、`value`。 控制顺序：L181按`attribute == "date_range"`分支。 调用`setattr`、`pytest.raises`、`validate_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typed_field_constraint_accepts_explicit_single_value_correction`（L193–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L209断言`changed.field_requirements[0].max_length == 500`；L210断言`changed.field_requirements[0].searchable is True`。 调用`requirement().model_copy`、`requirement`、`FieldRequirement`、`old.model_dump`、`reconcile`、`old.gate_dump`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chinese_correction_reconciles_legacy_text_and_records_provenance`（L213–L282）：接收`settings`、`store`、`plan`。 控制顺序：L271断言`store.get_run(run)["status"] == "READY"`；L276断言`entry["before"]["facts"]["title_max_length"] == 250`；L277断言`entry["after"]["facts"]["title_max_length"] == 100`；L278断言`len(entry["changes"]) == 3`；L279断言`all( change["authorized"] and change["sources"][0]["user_message_index"] == 1 for cha…`。 调用`requirement().model_copy`、`requirement`、`new_run`、`Runtime`、`Gateway`、`runtime.tick`、`decision`、`store.set_automation`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chinese_correction_reconciles_legacy_text_and_records_provenance.Gateway`（L227–L263）：继承`FixtureGateway`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_chinese_correction_reconciles_legacy_text_and_records_provenance.Gateway.complete`（L228–L263）：接收`rid`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L229按`schema is Requirement`分支；L230按`not payload["fresh_user_corrections"]`分支；L232断言`payload["fresh_user_corrections"] == [correction]`；L259断言`payload["approved_requirement"]["features"] == ["标题最多100字符"]`；L260断言`payload["approved_requirement"]["facts"]["title_max_length"] == 100`。 调用`Requirement.model_validate`、`old.model_dump`、`plan.model_copy`。 返回路径：L231的`old`；L233的`Requirement.model_validate( { **old.model_dump(), "questions": [], "facts": {"title_max_le…`；L263的`result`。
- `test_chinese_optional_correction_cannot_be_inverted_by_model`（L285–L300）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L289遍历`[(False, False), (True, True)]`；L300断言`changed.field_requirements[0].required is expected`。 调用`requirement().model_copy`、`requirement`、`FieldRequirement`、`old.model_dump`、`reconcile`、`old.gate_dump`、`Requirement.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cancelled_search_description_does_not_require_search`（L303–L305）：接收`plan`。 控制顺序：L305断言`coverage_gaps(approved, plan) == []`。 调用`requirement().model_copy`、`requirement`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_narrow_search_cancellation_cannot_delete_compound_requirement`（L309–L317）：接收`feature`。 控制顺序：L317断言`feature in changed.features`。 调用`requirement().model_copy`、`requirement`、`old.model_dump`、`reconcile`、`old.gate_dump`、`Requirement.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_requirement_coverage.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L317。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12510`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_requirement_coverage.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c1a1c383bdda545ea43928df1ca84f7fd6fd134cec76763aa654ff29a11e09d2"} -->
````python
# tests/test_requirement_coverage.py
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
````
