# tests/test_customer_coverage.py · 3/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_customer_coverage_py--002.md) · 

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `scoped_inventory_case`（L1761–L1794）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`customer_case`、`Plan`、`typed_field_ledger`。 返回路径：L1794的`requirement, plan`。
- `test_nested_field_inventory_constraints_bind_nearest_subject`（L1800–L1828）：接收`brackets`、`separator`、`reverse`。 控制顺序：L1803按`reverse`分支；L1808断言`coverage_gaps(requirement, plan) == []`；L1809遍历`[ ("short_text", "max_length", 3000), ("long_text", "max_length",…`；L1822断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L1823断言`any( item["source"]["section"] == "features" and item["attribute"] == attribute and i…`。 调用`scoped_inventory_case`、`descriptors.reverse`、`separator.join`、`coverage_gaps`、`plan.model_copy`、`setattr`、`next`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_inventory_keeps_outer_capability_and_inner_explicit_conflicts`（L1832–L1855）：接收`wrapper`。 控制顺序：L1836断言`coverage_gaps(requirement, plan) == []`；L1839断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1840断言`all( item["targets"] == [{"entity": "alpha", "field": "long_text"}] for item in diagn…`；L1843断言`all(item["source"]["section"] == "features" for item in diagnostics)`；L1846断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1847断言`all(item["source"]["section"] == "field_requirements" for item in diagnostics)`；L1848按`wrapper.startswith("search")`分支；L1851断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`。后续分支沿下方源码相同行号继续阅读。 调用`scoped_inventory_case`、`wrapper.format`、`coverage_gaps`、`body.replace`、`all`、`wrapper.startswith`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_inventory_preserves_adjacent_disabled_and_enabled_query_predicates`（L1858–L1870）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1863断言`coverage_gaps(requirement, plan) == []`；L1866断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1867断言`any( item["source"]["section"] == "features" and item["expected"] is False for item i…`。 调用`scoped_inventory_case`、`typed_field_ledger`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_repeated_subject_in_nested_inventory_keeps_contradictory_limits`（L1873–L1883）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1876遍历`[(200, 3000), (3000, 200)]`；L1879断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1880断言`any( item["source"]["section"] == "features" and item["expected"] == expected for ite…`。 调用`scoped_inventory_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_2a4_yudao_parenthesized_numeric_inventory_keeps_each_field_limit`（L1899–L1915）：接收`entity`、`text`。 控制顺序：L1903断言`coverage_gaps(requirement, plan) == []`；L1910断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1911断言`all(item["source"]["section"] == "features" for item in diagnostics)`；L1912断言`all(item["targets"] == [{"entity": entity, "field": "detail"}] for item in diagnostic…`；L1913断言`all( item["attribute"] == "max_length" and item["expected"] == 200 for item in diagno…`。 调用`actual_customer_field_case`、`typed_field_ledger`、`coverage_gaps`、`text.replace("detail 必填最长3000", "detail 必填最长200").replace`、`text.replace`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_f6b_python_yudao_relation_facts_keep_assignee_scope`（L1920–L1968）：接收`kind`、`entity`、`index`。 控制顺序：L1956断言`coverage_gaps(requirement, plan) == []`；L1965断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1966断言`len(diagnostics) == 1`；L1967断言`diagnostics[0]["targets"] == [{"entity": entity, "field": "assignee_id"}]`；L1968断言`diagnostics[0]["source"]["path"] == f"business.relations.{index}"`。 调用`actual_customer_field_case`、`coverage_gaps`、`next`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_f6b_fastapi_nested_resource_fields_keep_scope_and_provenance`（L1982–L2000）：接收`entity`、`index`、`field_name`、`attribute`、`wrong`、`field_index`。 控制顺序：L1987断言`coverage_gaps(requirement, plan) == []`；L1997断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1998断言`len(diagnostics) == 1`；L1999断言`diagnostics[0]["targets"] == [{"entity": entity, "field": field_name}]`；L2000断言`diagnostics[0]["source"]["path"] == f"business.resources.{index}.fields.{field_index}…`。 调用`actual_customer_field_case`、`coverage_gaps`、`next`、`setattr`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_coverage.py`；**本文件共有 3 段**。本段覆盖源文件 L1761–L2196。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15520`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_coverage.py", "part": 3, "parts": 3, "encoding": "utf-8", "sha256": "a1460b4044058e831e4162664006b01fbe4e0990dc49c707f6c4687d0276819e"} -->
````python
# tests/test_customer_coverage.py
def scoped_inventory_case():
    requirement, _ = customer_case()
    plan = Plan(
        title="Nested inventory",
        data_scope="shared",
        entities=[
            {
                "name": entity,
                "description": entity,
                "fields": [
                    {
                        "name": "short_text",
                        "kind": "text",
                        "required": True,
                        "min_length": 0,
                        "max_length": 200,
                        "searchable": True,
                    },
                    {
                        "name": "long_text",
                        "kind": "text",
                        "required": False,
                        "min_length": 1,
                        "max_length": 3000,
                        "searchable": True,
                    },
                ],
            }
            for entity in ["alpha", "beta"]
        ],
        acceptance=["Independent field descriptors"],
    )
    requirement.field_requirements = typed_field_ledger(plan)
    return requirement, plan


@pytest.mark.parametrize("brackets", ["（）", "()", "[]", "【】"])
@pytest.mark.parametrize("separator", ["、", "，", ", ", " and "])
@pytest.mark.parametrize("reverse", [False, True])
def test_nested_field_inventory_constraints_bind_nearest_subject(brackets, separator, reverse):
    requirement, plan = scoped_inventory_case()
    descriptors = ["short_text 必填 最长200 最小0", "long_text 可选 最长3000 最小1"]
    if reverse:
        descriptors.reverse()
    requirement.features = [
        f"alpha: 创建对象{brackets[0]}{separator.join(descriptors)}{brackets[1]}、编辑、归档"
    ]
    assert coverage_gaps(requirement, plan) == []
    for name, attribute, wrong in [
        ("short_text", "max_length", 3000),
        ("long_text", "max_length", 200),
        ("long_text", "min_length", 0),
        ("long_text", "required", True),
    ]:
        changed = plan.model_copy(deep=True)
        setattr(
            next(field for field in changed.entities[0].fields if field.name == name),
            attribute,
            wrong,
        )
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features"
            and item["attribute"] == attribute
            and item["targets"] == [{"entity": "alpha", "field": name}]
            for item in diagnostics
        )


@pytest.mark.parametrize("wrapper", ["define({body})", "define(fields({body}))", "search({body})"])
def test_nested_inventory_keeps_outer_capability_and_inner_explicit_conflicts(wrapper):
    requirement, plan = scoped_inventory_case()
    body = "short_text(required max_length=200), long_text(optional max_length=3000)"
    requirement.features = ["alpha: " + wrapper.format(body=body)]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = ["alpha: " + wrapper.format(body=body.replace("3000", "200"))]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(
        item["targets"] == [{"entity": "alpha", "field": "long_text"}] for item in diagnostics
    )
    assert all(item["source"]["section"] == "features" for item in diagnostics)
    plan.entities[0].fields[1].max_length = 200
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)
    if wrapper.startswith("search"):
        plan.entities[0].fields[0].searchable = False
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features" and item["attribute"] == "searchable"
            for item in diagnostics
        )


def test_nested_inventory_preserves_adjacent_disabled_and_enabled_query_predicates():
    requirement, plan = scoped_inventory_case()
    plan.entities[0].fields[0].searchable = False
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = ["alpha: 定义字段（short_text 不可搜索、long_text 必须可搜索）"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features" and item["expected"] is False
        for item in diagnostics
    )


def test_repeated_subject_in_nested_inventory_keeps_contradictory_limits():
    requirement, plan = scoped_inventory_case()
    requirement.features = ["alpha: define(short_text max_length=200, short_text max_length=3000)"]
    for value, expected in [(200, 3000), (3000, 200)]:
        plan.entities[0].fields[0].max_length = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "features" and item["expected"] == expected
            for item in diagnostics
        )


@pytest.mark.parametrize(
    "entity,text",
    [
        (
            "requests",
            "requests::创建请求（title 必填最长200、detail 必填最长3000、customer_id 必填外键、priority 必填枚举 普通/紧急）、编辑、归档",
        ),
        (
            "tasks",
            "tasks::创建任务（title 最长200、detail 最长3000、request_id 关联 requests）、分配",
        ),
    ],
)
def test_exact_2a4_yudao_parenthesized_numeric_inventory_keeps_each_field_limit(entity, text):
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = [
        text.replace("detail 必填最长3000", "detail 必填最长200").replace(
            "detail 最长3000", "detail 最长200"
        )
    ]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "features" for item in diagnostics)
    assert all(item["targets"] == [{"entity": entity, "field": "detail"}] for item in diagnostics)
    assert all(
        item["attribute"] == "max_length" and item["expected"] == 200 for item in diagnostics
    )


@pytest.mark.parametrize("kind", ["foreign_key", "many-to-one"])
@pytest.mark.parametrize("entity,index", [("requests", 1), ("tasks", 3)])
def test_exact_f6b_python_yudao_relation_facts_keep_assignee_scope(kind, entity, index):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {
        "business": {
            "relations": [
                {
                    "from": "requests",
                    "field": "customer_id",
                    "to": "customers",
                    "required": True,
                    "kind": kind,
                },
                {
                    "from": "requests",
                    "field": "assignee_id",
                    "to": "$users",
                    "required": False,
                    "kind": kind,
                },
                {
                    "from": "tasks",
                    "field": "request_id",
                    "to": "requests",
                    "required": True,
                    "kind": kind,
                },
                {
                    "from": "tasks",
                    "field": "assignee_id",
                    "to": "$users",
                    "required": False,
                    "kind": kind,
                },
            ]
        }
    }
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "assignee_id"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": "assignee_id"}]
    assert diagnostics[0]["source"]["path"] == f"business.relations.{index}"


@pytest.mark.parametrize("entity,index", [("requests", 1), ("tasks", 2)])
@pytest.mark.parametrize(
    "field_name,attribute,wrong,field_index",
    [
        ("title", "required", False, 0),
        ("detail", "max_length", 200, 1),
        ("assignee_id", "required", True, 3),
        ("resolved_at", "searchable", True, 5),
        ("due_at", "filterable", True, 6),
    ],
)
def test_exact_f6b_fastapi_nested_resource_fields_keep_scope_and_provenance(
    entity, index, field_name, attribute, wrong, field_index
):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"business": {"resources": ACTUAL_F6B_FASTAPI_RESOURCES}}
    assert coverage_gaps(requirement, plan) == []
    target = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == field_name
    )
    setattr(target, attribute, wrong)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": field_name}]
    assert diagnostics[0]["source"]["path"] == f"business.resources.{index}.fields.{field_index}"


# Exact diagnostic-only facts from final f6b; no candidate Plan is used as a fixture.
ACTUAL_F6B_FASTAPI_RESOURCES = [
    {
        "entity": "customers",
        "label": "客户",
        "features": ["native-crud", "append-only-audit", "archive-history"],
        "fields": [
            {
                "name": "name",
                "label": "客户名称",
                "kind": "text",
                "required": True,
                "max_length": 120,
                "searchable": True,
            },
            {
                "name": "organization",
                "label": "所属组织",
                "kind": "text",
                "required": False,
                "max_length": 160,
                "searchable": True,
            },
            {
                "name": "contact",
                "label": "联系方式",
                "kind": "text",
                "required": False,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "category",
                "label": "客户分类",
                "kind": "enum",
                "required": True,
                "choices": ["企业", "个人", "合作伙伴"],
                "filterable": True,
            },
        ],
    },
    {
        "entity": "requests",
        "label": "服务请求",
        "features": [
            "native-crud",
            "foreign-key-relations",
            "assignment",
            "named-state-transitions",
            "handling-notes",
            "append-only-audit",
            "archive-history",
            "in-app-reminders",
        ],
        "fields": [
            {
                "name": "title",
                "label": "请求标题",
                "kind": "text",
                "required": True,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "detail",
                "label": "请求详情",
                "kind": "text",
                "required": True,
                "max_length": 3000,
                "searchable": True,
            },
            {
                "name": "customer_id",
                "label": "关联客户",
                "kind": "text",
                "required": True,
                "relation": "customers",
            },
            {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": False,
                "relation": "$users",
            },
            {
                "name": "request_state",
                "label": "请求状态",
                "kind": "enum",
                "required": True,
                "choices": ["new", "active", "resolved"],
                "choice_labels": {"new": "待处理", "active": "处理中", "resolved": "已解决"},
            },
            {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "priority",
                "label": "优先级",
                "kind": "enum",
                "required": True,
                "choices": ["普通", "紧急"],
                "filterable": True,
            },
        ],
    },
    {
        "entity": "tasks",
        "label": "协作任务",
        "features": [
            "native-crud",
            "foreign-key-relations",
            "assignment",
            "named-state-transitions",
            "handling-notes",
            "append-only-audit",
            "archive-history",
            "in-app-reminders",
        ],
        "fields": [
            {
                "name": "title",
                "label": "任务标题",
                "kind": "text",
                "required": True,
                "max_length": 200,
                "searchable": True,
            },
            {
                "name": "detail",
                "label": "任务详情",
                "kind": "text",
                "required": True,
                "max_length": 3000,
                "searchable": True,
            },
            {
                "name": "request_id",
                "label": "关联请求",
                "kind": "text",
                "required": True,
                "relation": "requests",
            },
            {
                "name": "assignee_id",
                "label": "负责人",
                "kind": "text",
                "required": False,
                "relation": "$users",
            },
            {
                "name": "task_state",
                "label": "任务状态",
                "kind": "enum",
                "required": True,
                "choices": ["new", "active", "resolved"],
                "choice_labels": {"new": "待处理", "active": "处理中", "resolved": "已解决"},
            },
            {
                "name": "resolved_at",
                "label": "解决时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
            {
                "name": "due_at",
                "label": "截止时间",
                "kind": "datetime",
                "required": False,
                "searchable": False,
                "filterable": False,
                "date_range": False,
            },
        ],
    },
]
````
