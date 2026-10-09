# tests/test_legacy_date_requirements.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L9–L37）：接收`text`、`section`。 控制顺序：L33按`section == "facts"`分支。 调用`Plan`、`Requirement`、`setattr`。 返回路径：L37的`requirement, plan`。
- `test_format_negation_and_catalog_prose_do_not_require_a_date_field`（L70–L75）：接收`section`、`text`。 控制顺序：L73断言`coverage_gaps(requirement, plan) == []`；L74断言`requirement.model_dump() == before`；L75断言`all(field.kind != "date" for field in plan.entities[0].fields)`。 调用`case`、`requirement.model_dump`、`coverage_gaps`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_field_date_contract_still_requires_executable_date`（L94–L104）：接收`section`、`text`。 控制顺序：L97断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L98断言`any( item["code"] == "date_kind" and item["targets"] == [{"entity": "records", "field…`；L104断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_another_entity_date_cannot_satisfy_explicit_missing_or_wrong_field`（L107–L118）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L116断言`coverage_gaps(requirement, plan)`；L118断言`coverage_gaps(requirement, plan)`。 调用`case`、`plan.entities.append`、`plan.entities[0].model_copy`、`coverage_gaps`、`plan.entities[0].fields.pop`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_explicit_date_subjects_must_be_dates`（L121–L126）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L124断言`coverage_gaps(requirement, plan)`；L126断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typed_date_contract_cannot_be_suppressed_by_formatting_or_negative_metadata`（L129–L141）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L135断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L136断言`any( item["source"]["section"] == "field_requirements" and item["attribute"] == "kind…`；L141断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`FieldRequirement`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unscoped_explicit_real_date_feature_still_requires_a_date`（L144–L148）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L146断言`coverage_gaps(requirement, plan)`；L148断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fact_catalog_heading_retains_its_context`（L152–L155）：接收`key`。 控制顺序：L155断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_range_queries_never_require_an_additional_exact_filter`（L173–L186）：接收`text`、`section`。 控制顺序：L178断言`field.filterable is False`；L180断言`coverage_gaps(requirement, plan) == []`；L181断言`(requirement.model_dump(), plan.model_dump()) == before`；L184断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L185断言`any(row["attribute"] == "date_range" for row in diagnostics)`；L186断言`not any(row["attribute"] == "filterable" for row in diagnostics)`。 调用`case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_an_explicit_exact_filter_stays_independent_of_the_range_query`（L198–L208）：接收`text`。 控制顺序：L202断言`coverage_gaps(requirement, plan) == []`；L203遍历`("date_range", "filterable")`；L206断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L207断言`any(row["attribute"] == flag for row in diagnostics)`。 调用`case`、`coverage_gaps`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_range_and_exact_queries_bind_to_their_own_named_fields`（L219–L234）：接收`text`。 控制顺序：L224断言`coverage_gaps(requirement, plan) == []`；L225遍历`((exact, "filterable"), (ranged, "date_range"))`；L228断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L229断言`any( row["attribute"] == flag and row["targets"] == [{"entity": "records", "field": f…`。 调用`case`、`coverage_gaps`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_a_shared_range_filter_verb_still_binds_coordinated_non_date_fields`（L249–L270）：接收`text`、`section`。 控制顺序：L255断言`coverage_gaps(requirement, plan) == []`；L256断言`event_on.filterable is False`；L257断言`(requirement.model_dump(), plan.model_dump()) == before`；L259按`"recorded_at" in text`分支；L261遍历`targets`；L264断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L265断言`any( row["attribute"] == flag and row["targets"] == [{"entity": "records", "field": f…`。 调用`case`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`targets.append`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_coordinated_date_fields_share_only_the_range_operation`（L282–L299）：接收`text`。 控制顺序：L286遍历`(event_on, recorded_at)`；L288断言`coverage_gaps(requirement, plan) == []`；L289断言`not event_on.filterable and not recorded_at.filterable`；L290遍历`(event_on, recorded_at)`；L293断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L294断言`any(row["attribute"] == "date_range" for row in diagnostics)`；L295断言`not any(row["attribute"] == "filterable" for row in diagnostics)`；L297按`"name" in text`分支。后续分支沿下方源码相同行号继续阅读。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_or_completed_field_descriptions_do_not_share_a_range_filter_verb`（L315–L320）：接收`text`。 控制顺序：L319断言`all(not field.filterable for field in plan.entities[0].fields)`；L320断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`all`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shared_filter_projection_keeps_the_original_entity_scope`（L323–L340）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L328遍历`archive.fields`；L331断言`coverage_gaps(requirement, plan) == []`；L335断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L336断言`any( row["attribute"] == "filterable" and row["targets"] == [{"entity": "records", "f…`。 调用`case`、`plan.entities[0].model_copy`、`plan.entities.append`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_range_queries_still_enforce_an_explicit_exact_filter_prohibition`（L350–L358）：接收`text`。 控制顺序：L354断言`coverage_gaps(requirement, plan) == []`；L357断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L358断言`any(row["attribute"] == "filterable" and row["expected"] is False for row in diagnost…`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_disabling_a_range_query_does_not_disable_its_explicit_exact_filter`（L369–L378）：接收`text`。 控制顺序：L373断言`coverage_gaps(requirement, plan) == []`；L376断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L377断言`any(row["attribute"] == "date_range" and row["expected"] is False for row in diagnost…`；L378断言`not any(row["attribute"] == "filterable" for row in diagnostics)`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_an_unrequested_range_query_is_not_a_positive_or_negative_obligation`（L388–L394）：接收`text`。 控制顺序：L392遍历`(False, True)`；L394断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_range_wording_cannot_override_an_explicit_typed_exact_filter_prohibition`（L397–L411）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L404断言`coverage_gaps(requirement, plan) == []`；L407断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L408断言`any( row["source"]["section"] == "field_requirements" and row["attribute"] == "filter…`。 调用`case`、`FieldRequirement`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_legacy_date_requirements.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L411。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16649`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_legacy_date_requirements.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f065902f19c107ca6351ad037cfaa7c4a19da9167cc5dce2d3658b3af09ee247"} -->
````python
# tests/test_legacy_date_requirements.py
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
````
