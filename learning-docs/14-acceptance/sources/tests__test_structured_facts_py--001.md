# tests/test_structured_facts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.news_fixture`、`workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L8–L11）：接收`facts`。 调用`news_requirement`、`Requirement.model_validate`、`Plan.model_validate`、`news_spec`。 返回路径：L11的`Requirement.model_validate(raw), Plan.model_validate(news_spec())`。
- `test_optional_structured_facts_are_not_prose`（L23–L25）：接收`facts`。 控制顺序：L25断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_true_required_obligation_still_blocks_optional_field`（L36–L38）：接收`facts`。 控制顺序：L38断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_false_required_obligation_still_blocks_required_field`（L41–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L44断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_enum_membership_is_order_independent_but_cannot_drop_or_add`（L48–L58）：接收`typed`。 控制顺序：L50按`typed`分支；L54断言`coverage_gaps(requirement, plan) == []`；L56断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`；L58断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`FieldRequirement`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structured_lengths_preserve_both_bounds_and_flag_negation`（L61–L73）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L68断言`coverage_gaps(requirement, plan) == []`；L72断言`any("max_length" in gap for gap in gaps)`；L73断言`any("searchable" in gap for gap in gaps)`。 调用`case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_boolean_is_not_silently_truthy`（L76–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L78断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recursive_and_legacy_json_facts_keep_types`（L91–L93）：接收`facts`。 控制顺序：L93断言`coverage_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_conflicting_true_typed_and_false_fact_remains_blocked`（L96–L101）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`；L101断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`FieldRequirement`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_booleans_and_integers_are_not_interchangeable`（L105–L107）：接收`fact`。 控制顺序：L107断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_string_length_fact_preserved`（L110–L114）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L112断言`coverage_gaps(requirement, plan) == []`；L114断言`any("max_length" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_scalar_enum_options_remain_blocked`（L117–L119）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L119断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_chinese_boolean_required_facts_keep_value`（L123–L131）：接收`required`。 控制顺序：L126断言`bool(gaps) is required`；L131断言`any(".required=" in gap for gap in gaps) is not required`。 调用`case`、`coverage_gaps`、`bool`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_legacy_description_retains_filter_obligation`（L134–L138）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L136断言`coverage_gaps(requirement, plan) == []`；L138断言`any("filterable" in gap and "说明" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chinese_optional_boolean_inverse_polarity`（L142–L148）：接收`optional`。 控制顺序：L145断言`any(".required=" in gap for gap in gaps) is not optional`；L148断言`any(".required=" in gap for gap in gaps) is optional`。 调用`case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_fact_entity_qualifier_is_preserved`（L151–L165）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L163断言`coverage_gaps(requirement, plan) == []`；L165断言`coverage_gaps(requirement, plan)`。 调用`case`、`plan.entities[0].model_copy`、`plan.entities.append`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_chinese_boolean_query_flags_keep_polarity`（L180–L188）：接收`key`、`field`、`attribute`、`enabled`。 控制顺序：L186断言`coverage_gaps(requirement, plan) == []`；L188断言`any("." + attribute + "=" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`next`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_legacy_whitespace_canonical_flags_keep_polarity`（L203–L211）：接收`key`、`field`、`attribute`、`enabled`。 控制顺序：L209断言`coverage_gaps(requirement, plan) == []`；L211断言`any("." + attribute + "=" in gap for gap in coverage_gaps(requirement, plan))`。 调用`case`、`next`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_structured_facts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L211。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8688`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_structured_facts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "4755ebb6f5adccbd2a67b52645209d88c883628004de6414e6d6cdf716d2a725"} -->
````python
# tests/test_structured_facts.py
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
````
