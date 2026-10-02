# tests/test_semantic_fact_domains.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.domain`、`workbench.requirement_coverage`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L19–L54）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan`、`Requirement`。 返回路径：L54的`requirement, plan`。
- `encode`（L57–L62）：接收`value`、`shape`。 控制顺序：L58按`shape == "json"`分支；L60按`shape == "nested"`分支。 调用`json.dumps`。 返回路径：L59的`json.dumps(value, ensure_ascii=False)`；L61的`[{"arbitrary": [json.dumps({"wrapper": value}, ensure_ascii=False)]}]`；L62的`value`。
- `test_presentation_domain_survives_containers_and_constraint_looking_captions`（L68–L90）：接收`namespace`、`collision`、`shape`。 控制顺序：L89断言`coverage_gaps(requirement, plan) == []`；L90断言`requirement.model_dump_json() == before`。 调用`case`、`encode`、`requirement.model_dump_json`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_explicit_constraint_schema_reenters_presentation_domain`（L96–L119）：接收`namespace`、`declaration`、`shape`。 控制顺序：L112断言`coverage_gaps(requirement, plan) == []`；L115断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L116断言`len(diagnostics) == 1`；L117断言`diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]`；L118断言`diagnostics[0]["source"]["path"].startswith(namespace)`；L119断言`diagnostics[0]["attribute"] == "required"`。 调用`case`、`encode`、`coverage_gaps`、`len`、`diagnostics[0]["source"]["path"].startswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupted_or_missing_explicit_declarations_cannot_hide_in_display`（L139–L148）：接收`namespace`、`entry`。 控制顺序：L147断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L148断言`all(item["source"]["path"].startswith(namespace) for item in diagnostics)`。 调用`case`、`coverage_gaps`、`all`、`item["source"]["path"].startswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_display_domain_cannot_override_an_independent_typed_obligation`（L152–L162）：接收`namespace`。 控制顺序：L158断言`coverage_gaps(requirement, plan) == []`；L161断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L162断言`all(item["source"]["section"] == "field_requirements" for item in diagnostics)`。 调用`case`、`FieldRequirement`、`coverage_gaps`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_name_can_equal_presentation_namespace_in_real_field_schema`（L166–L176）：接收`namespace`。 控制顺序：L174断言`coverage_gaps(requirement, plan) == []`；L176断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_constraints_keep_structural_resource_scope_across_display`（L180–L195）：接收`namespace`。 控制顺序：L191断言`coverage_gaps(requirement, plan) == []`；L194断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L195断言`diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_composition_never_borrows_other_local_operation_targets`（L208–L231）：接收`parts`、`section`、`separator`。 控制顺序：L211按`section == "facts"`分支；L215断言`coverage_gaps(requirement, plan) == []`；L216遍历`[ ("needle", "searchable"), ("contact", "searchable"), ("category…`；L227断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L228断言`any( item["attribute"] == attribute and {"entity": "alpha", "field": name} in item["t…`。 调用`case`、`separator.join`、`setattr`、`coverage_gaps`、`plan.model_copy`、`next(field for field in changed.entities[0].fields if field.name …`、`next`、`any`、`pytest.mark.parametrize`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_composition_alone_does_not_require_any_primitive_search`（L244–L251）：接收`text`。 控制顺序：L247遍历`plan.entities[0].fields`；L249断言`coverage_gaps(requirement, plan) == []`；L251断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`requirement.features.append`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `recorded`（L254–L266）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L257断言`hashlib.sha256(raw).hexdigest() == ( "d0d30b7d9ccd6a77e2f0e6a599592d9b63637884cec6ec6…`；L261断言`data["approval_status"] == "unapproved"`；L262断言`data["execution_authorized"] is False`；L263断言`data["purpose"] == "offline_contract_validation_only"`。 调用`file.read_bytes`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`Requirement.model_validate`、`Plan.model_validate`。 返回路径：L264的`Requirement.model_validate(data["requirement"]), Plan.model_validate( data["candidate_plan…`。
- `test_exact_genuine_candidate_passes_all_pure_semantic_gates_without_mutation`（L269–L274）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L272断言`not coverage_gaps(requirement, plan)`；L273断言`not business_gaps(requirement, plan)`；L274断言`(requirement.model_dump(), plan.model_dump()) == before`。 调用`recorded`、`deepcopy`、`requirement.model_dump`、`plan.model_dump`、`coverage_gaps`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_recorded_candidate_rejects_real_obligation_regressions`（L292–L324）：接收`mutation`。 控制顺序：L296按`mutation.endswith("_search")`分支；L298按`mutation == "category_filter"`分支；L300按`mutation == "max_length"`分支；L302按`mutation == "missing_field"`分支；L304按`mutation == "unknown_obligation"`分支；L308按`mutation == "metadata_constraint"`分支；L312按`mutation == "permission"`分支；L317按`mutation == "relation"`分支。后续分支沿下方源码相同行号继续阅读。 调用`recorded`、`next`、`mutation.endswith`、`mutation.removesuffix`、`customers.fields.remove`、`requirement.field_requirements.append`、`FieldRequirement`、`coverage_gaps`、`business_gaps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_scalar_constraint_namespace_captions_are_presentation_values`（L328–L339）：接收`namespace`。 控制顺序：L338断言`coverage_gaps(requirement, plan) == []`；L339断言`business_gaps(requirement, plan) == []`。 调用`case`、`coverage_gaps`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_scoped_field_can_be_named_like_presentation_domain`（L351–L360）：接收`namespace`、`attribute`、`expected`、`changed`。 控制顺序：L358断言`coverage_gaps(requirement, plan) == []`；L360断言`coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_composition_targets_keep_their_primitive_obligations`（L373–L387）：接收`text`、`attribute`。 控制顺序：L377遍历`plan.entities[0].fields`；L379断言`coverage_gaps(requirement, plan) == []`；L380遍历`targets`；L387断言`coverage_gaps(requirement, changed)`。 调用`case`、`setattr`、`coverage_gaps`、`plan.model_copy`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_presentation_business_vocabulary_is_not_a_business_schema_or_permission_matrix`（L402–L412）：接收`namespace`、`shape`。 控制顺序：L407断言`coverage_gaps(requirement, plan) == []`；L408断言`business_gaps(requirement, plan) == []`；L412断言`business_gaps(actual_requirement, actual_plan) == []`。 调用`case`、`encode`、`coverage_gaps`、`business_gaps`、`recorded`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_business_schema_nested_in_display_preserves_permissions_and_malformed_constraints`（L417–L431）：接收`namespace`、`wrapper`。 控制顺序：L423断言`not business_gaps(requirement, plan)`；L428断言`business_gaps(requirement, plan)`；L431断言`business_gaps(requirement, plan)`。 调用`recorded`、`deepcopy`、`business_gaps`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_business_reentry_keeps_its_nested_real_field_constraints`（L436–L454）：接收`namespace`、`wrapper`。 控制顺序：L450断言`coverage_gaps(requirement, plan) == []`；L453断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L454断言`diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_candidate_preserves_every_typed_field_attribute_and_identity`（L457–L503）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L460遍历`enumerate(requirement.field_requirements)`；L461遍历`obligation.model_dump(exclude_none=True).items()`；L462按`attribute in {"entity", "field"}`分支；L472按`type(expected) is bool`分支；L474按`type(expected) is int`分支；L476按`isinstance(expected, list)`分支；L482断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L483断言`any( item["source"] == {"section": "field_requirements", "index": index} and item["at…`。后续分支沿下方源码相同行号继续阅读。 调用`recorded`、`enumerate`、`obligation.model_dump(exclude_none=True).items`、`obligation.model_dump`、`plan.model_copy`、`next`、`type`、`isinstance`、`setattr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unique_unscoped_field_identity_precedes_a_presentation_namespace_name`（L507–L520）：接收`namespace`。 控制顺序：L511断言`coverage_gaps(requirement, plan)`；L513断言`not coverage_gaps(requirement, plan)`；L520断言`not coverage_gaps(requirement, plan)`。 调用`case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_semantic_fact_domains.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L520。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19905`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_semantic_fact_domains.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2b07546e921923fda3474db3abc825e6d1910726c8ba8eac1e8a4f5a5ec188ff"} -->
````python
# tests/test_semantic_fact_domains.py
"""Presentation namespaces and query composition never grant primitive field flags."""

import hashlib
import json
from copy import deepcopy
from itertools import permutations

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

PRESENTATION = ["labels", "display", "ui", "i18n", "translations", "presentation"]
COLLISIONS = ["fields", "entities", "roles", "permissions", "metrics", "reminders", "relations"]


def case():
    plan = Plan(
        title="Namespace boundaries",
        data_scope="shared",
        entities=[
            {
                "name": "alpha",
                "description": "First resource",
                "fields": [
                    {"name": "needle", "kind": "text", "searchable": True, "max_length": 120},
                    {"name": "contact", "kind": "text", "searchable": True, "max_length": 200},
                    {
                        "name": "category",
                        "kind": "enum",
                        "choices": ["a", "b"],
                        "filterable": True,
                    },
                    {"name": "title", "kind": "text", "required": False, "max_length": 80},
                ],
            },
            {
                "name": "beta",
                "description": "Other resource",
                "fields": [{"name": "title", "kind": "text", "max_length": 200}],
            },
        ],
        acceptance=["Preserve explicit constraints"],
    )
    requirement = Requirement(
        summary="Namespace boundaries",
        users=["Reader"],
        data_scope="shared",
        features=[],
        acceptance=[],
    )
    return requirement, plan


def encode(value, shape):
    if shape == "json":
        return json.dumps(value, ensure_ascii=False)
    if shape == "nested":
        return [{"arbitrary": [json.dumps({"wrapper": value}, ensure_ascii=False)]}]
    return value


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize("collision", COLLISIONS)
@pytest.mark.parametrize("shape", ["native", "json", "nested"])
def test_presentation_domain_survives_containers_and_constraint_looking_captions(
    namespace, collision, shape
):
    requirement, plan = case()
    captions = {
        "alpha": {
            "name": "needle",
            "field": "title",
            "entity": "beta",
            "required": "必填",
            "kind": "text",
            "searchable": "可搜索",
            "filterable": "精确筛选",
            "choices": ["title", "category"],
            "max_length": "最多200",
            "title": "标题必须可搜索",
        },
        "beta": {"title": "必填标题", "category": "可选分类"},
    }
    requirement.facts = {namespace: encode({collision: captions}, shape)}
    before = requirement.model_dump_json()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump_json() == before


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize("declaration", ["field_requirements", "field_constraints", "字段约束"])
@pytest.mark.parametrize("shape", ["native", "json", "nested"])
def test_only_explicit_constraint_schema_reenters_presentation_domain(
    namespace, declaration, shape
):
    requirement, plan = case()
    requirement.facts = {
        namespace: encode(
            {
                "fields": {
                    "translations": {
                        declaration: [{"entity": "alpha", "field": "title", "required": False}],
                    }
                }
            },
            shape,
        ),
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]
    assert diagnostics[0]["source"]["path"].startswith(namespace)
    assert diagnostics[0]["attribute"] == "required"


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize(
    "entry",
    [
        {"entity": "alpha", "field": "missing", "required": True},
        {"entity": "missing", "field": "title", "required": True},
        {"entity": {}, "field": "title", "required": True},
        {"entity": "alpha", "field": None, "required": True},
        {"entity": "alpha", "required": True},
        {"entity": "alpha", "field": "title", "required": "a label"},
        {"entity": "alpha", "field": "title", "max_length": True},
        {"entity": "alpha", "field": "category", "choices": {"a": "A"}},
        {},
        "malformed declaration",
        None,
    ],
)
def test_corrupted_or_missing_explicit_declarations_cannot_hide_in_display(namespace, entry):
    requirement, plan = case()
    requirement.facts = {
        namespace: {
            "field_requirements": [{"entity": "alpha", "field": "title", "required": False}, entry]
        }
    }
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["path"].startswith(namespace) for item in diagnostics)


@pytest.mark.parametrize("namespace", PRESENTATION)
def test_display_domain_cannot_override_an_independent_typed_obligation(namespace):
    requirement, plan = case()
    requirement.field_requirements = [
        FieldRequirement(entity="alpha", field="needle", searchable=True),
    ]
    requirement.facts = {namespace: {"fields": {"needle": {"searchable": False}}}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize("namespace", PRESENTATION)
def test_field_name_can_equal_presentation_namespace_in_real_field_schema(namespace):
    requirement, plan = case()
    plan.entities[0].fields[0].name = namespace
    requirement.facts = {
        "fields": {
            namespace: {"entity": "alpha", "kind": "text", "required": True, "max_length": 120},
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].max_length = 121
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize("namespace", PRESENTATION)
def test_explicit_constraints_keep_structural_resource_scope_across_display(namespace):
    requirement, plan = case()
    requirement.facts = {
        "resources": {
            "alpha": {
                namespace: {
                    "field_constraints": [{"field": "title", "required": False}],
                }
            }
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]


QUERY_PARTS = [
    "按 needle、contact 关键词搜索",
    "按 category 精确筛选",
    "支持不同条件组合检索",
]


@pytest.mark.parametrize("parts", list(permutations(QUERY_PARTS)))
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("separator", ["，", "；", ", ", "并且", "和", " and "])
def test_query_composition_never_borrows_other_local_operation_targets(parts, section, separator):
    requirement, plan = case()
    text = "alpha：" + separator.join(parts)
    if section == "facts":
        requirement.facts = {"description": text}
    else:
        setattr(requirement, section, [text])
    assert coverage_gaps(requirement, plan) == []
    for name, attribute in [
        ("needle", "searchable"),
        ("contact", "searchable"),
        ("category", "filterable"),
    ]:
        changed = plan.model_copy(deep=True)
        next(field for field in changed.entities[0].fields if field.name == name).__setattr__(
            attribute,
            False,
        )
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["attribute"] == attribute and {"entity": "alpha", "field": name} in item["targets"]
            for item in diagnostics
        )


@pytest.mark.parametrize(
    "text",
    [
        "按 category 精确筛选，支持不同条件组合检索",
        "支持不同条件联合查询；category 精确筛选",
        "filter by category, support combined search",
        "support composite filtering; filter by category",
        "support compound queries; filter by category",
    ],
)
def test_composition_alone_does_not_require_any_primitive_search(text):
    requirement, plan = case()
    requirement.features = ["alpha：" + text]
    for field in plan.entities[0].fields:
        field.searchable = False
    assert coverage_gaps(requirement, plan) == []
    requirement.features.append("alpha：category 必须可搜索")
    assert coverage_gaps(requirement, plan)


def recorded():
    file = ROOT / "tests/fixtures/customer_design_diagnostics/1d7c70b/fastapiadmin.json"
    raw = file.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "d0d30b7d9ccd6a77e2f0e6a599592d9b63637884cec6ec627953e395474d4a72"
    )
    data = json.loads(raw)
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


def test_exact_genuine_candidate_passes_all_pure_semantic_gates_without_mutation():
    requirement, plan = recorded()
    before = deepcopy((requirement.model_dump(), plan.model_dump()))
    assert not coverage_gaps(requirement, plan)
    assert not business_gaps(requirement, plan)
    assert (requirement.model_dump(), plan.model_dump()) == before


@pytest.mark.parametrize(
    "mutation",
    [
        "name_search",
        "contact_search",
        "category_filter",
        "max_length",
        "missing_field",
        "unknown_obligation",
        "metadata_constraint",
        "permission",
        "relation",
        "metric",
    ],
)
def test_exact_recorded_candidate_rejects_real_obligation_regressions(mutation):
    requirement, plan = recorded()
    customers = next(entity for entity in plan.entities if entity.name == "customers")
    fields = {field.name: field for field in customers.fields}
    if mutation.endswith("_search"):
        fields[mutation.removesuffix("_search")].searchable = False
    elif mutation == "category_filter":
        fields["category"].filterable = False
    elif mutation == "max_length":
        fields["name"].max_length = 121
    elif mutation == "missing_field":
        customers.fields.remove(fields["contact"])
    elif mutation == "unknown_obligation":
        requirement.field_requirements.append(
            FieldRequirement(entity="customers", field="missing", required=True),
        )
    elif mutation == "metadata_constraint":
        requirement.facts["labels"]["field_constraints"] = [
            {"entity": "customers", "field": "name", "max_length": 121},
        ]
    elif mutation == "permission":
        permission = next(
            p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
        )
        permission.scope = "all"
    elif mutation == "relation":
        plan.business.relations[0].target_entity = "tasks"
    else:
        next(
            metric for metric in plan.business.metrics if metric.kind == "group_count"
        ).group_by = "name"
    # Pure diagnostic replay only. Nothing is generated or executed from the candidate.
    assert coverage_gaps(requirement, plan) or business_gaps(requirement, plan)


@pytest.mark.parametrize("namespace", PRESENTATION)
def test_scalar_constraint_namespace_captions_are_presentation_values(namespace):
    requirement, plan = case()
    requirement.facts = {
        namespace: {
            "field_constraints": "字段约束",
            "field_requirements": "字段要求",
            "字段约束": "约束说明",
            "business": "业务合同",
        }
    }
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize(
    "attribute,expected,changed",
    [
        ("required", True, False),
        ("max_length", 120, 121),
        ("searchable", True, False),
    ],
)
def test_entity_scoped_field_can_be_named_like_presentation_domain(
    namespace, attribute, expected, changed
):
    requirement, plan = case()
    field = plan.entities[0].fields[0]
    field.name = namespace
    requirement.facts = {"alpha": {namespace: {attribute: expected}}}
    assert coverage_gaps(requirement, plan) == []
    setattr(field, attribute, changed)
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text,attribute",
    [
        ("对 needle、contact 进行联合搜索", "searchable"),
        ("needle 和 contact 支持组合搜索", "searchable"),
        ("按 needle 和 contact 组合筛选", "filterable"),
        ("combined search by needle and contact", "searchable"),
        ("category 参与复合搜索", "searchable"),
    ],
)
def test_explicit_composition_targets_keep_their_primitive_obligations(text, attribute):
    requirement, plan = case()
    requirement.features = ["alpha：" + text]
    targets = ["category"] if "category" in text else ["needle", "contact"]
    for field in plan.entities[0].fields:
        setattr(field, attribute, field.name in targets)
    assert coverage_gaps(requirement, plan) == []
    for target in targets:
        changed = plan.model_copy(deep=True)
        setattr(
            next(field for field in changed.entities[0].fields if field.name == target),
            attribute,
            False,
        )
        assert coverage_gaps(requirement, changed)


BUSINESS_CAPTIONS = {
    "metrics": {"name": "指标名称", "kind": "指标类型", "entity": "业务实体"},
    "relations": {"entity": "业务实体", "field": "字段", "target_entity": "目标实体"},
    "permissions": {"role": "角色", "entity": "实体", "actions": "操作", "scope": "范围"},
    "reminders": {"entity": "实体", "event": "事件", "recipient": "接收者"},
    "resources": {"entity": "实体", "audit": "审计", "archive": "归档"},
    "roles": ["manager", "service"],
}


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize("shape", ["native", "json", "nested"])
def test_presentation_business_vocabulary_is_not_a_business_schema_or_permission_matrix(
    namespace, shape
):
    requirement, plan = case()
    requirement.facts = {namespace: encode(BUSINESS_CAPTIONS, shape)}
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []
    # It must not impose an empty complete-policy matrix on existing grants.
    actual_requirement, actual_plan = recorded()
    actual_requirement.facts[namespace] = encode(BUSINESS_CAPTIONS, shape)
    assert business_gaps(actual_requirement, actual_plan) == []


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize("wrapper", ["business", "business_requirements", "business_constraints"])
def test_explicit_business_schema_nested_in_display_preserves_permissions_and_malformed_constraints(
    namespace, wrapper
):
    requirement, plan = recorded()
    business = deepcopy(requirement.facts["business"])
    requirement.facts = {namespace: {wrapper: business}}
    assert not business_gaps(requirement, plan)
    policy = next(
        p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
    )
    policy.scope = "all"
    assert business_gaps(requirement, plan)
    policy.scope = "assigned"
    business["permissions"][0]["actions"] = "malformed actions"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("namespace", PRESENTATION)
@pytest.mark.parametrize("wrapper", ["business", "business_requirements", "business_constraints"])
def test_explicit_business_reentry_keeps_its_nested_real_field_constraints(namespace, wrapper):
    requirement, plan = case()
    requirement.facts = {
        namespace: {
            wrapper: {
                "resources": [
                    {
                        "entity": "alpha",
                        "fields": [{"field": "title", "required": False}],
                    }
                ]
            }
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "title"}]


def test_exact_candidate_preserves_every_typed_field_attribute_and_identity():
    requirement, plan = recorded()
    checked = 0
    for index, obligation in enumerate(requirement.field_requirements):
        for attribute, expected in obligation.model_dump(exclude_none=True).items():
            if attribute in {"entity", "field"}:
                continue
            changed = plan.model_copy(deep=True)
            field = next(
                field
                for entity in changed.entities
                if entity.name == obligation.entity
                for field in entity.fields
                if field.name == obligation.field
            )
            if type(expected) is bool:
                replacement = not expected
            elif type(expected) is int:
                replacement = expected + 1
            elif isinstance(expected, list):
                replacement = [*expected, "unexpected"]
            else:
                replacement = "integer" if expected != "integer" else "text"
            setattr(field, attribute, replacement)
            diagnostics = []
            assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
            assert any(
                item["source"] == {"section": "field_requirements", "index": index}
                and item["attribute"] == attribute
                for item in diagnostics
            ), (
                obligation.entity,
                obligation.field,
                attribute,
            )
            checked += 1
        changed = plan.model_copy(deep=True)
        entity = next(entity for entity in changed.entities if entity.name == obligation.entity)
        entity.fields = [field for field in entity.fields if field.name != obligation.field]
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["source"] == {"section": "field_requirements", "index": index}
            and item["code"] == "missing_or_ambiguous"
            for item in diagnostics
        )
    assert checked == 89


@pytest.mark.parametrize("namespace", PRESENTATION)
def test_unique_unscoped_field_identity_precedes_a_presentation_namespace_name(namespace):
    requirement, plan = case()
    plan.entities[0].fields[0].name = namespace
    requirement.facts = {namespace: {"required": False}}
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].required = False
    assert not coverage_gaps(requirement, plan)
    requirement.facts = {
        namespace: {
            "fields": {"alpha": {namespace: "必填可搜索"}},
            "choices": {"title": "必填标题"},
        }
    }
    assert not coverage_gaps(requirement, plan)
````
