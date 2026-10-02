# tests/test_business_contracts.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `business_plan`（L9–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L10的`{ "title": "Generic linked workflow", "data_scope": "shared", "acceptance": ["Verified"], …`。
- `test_generic_business_contract_roundtrip_and_schema`（L157–L163）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L160断言`Plan.model_validate_json(plan.model_dump_json()) == plan`；L161断言`plan.business.registration.default_role == "employee"`；L162断言`plan.business.metrics[1].unit == "seconds"`；L163断言`"BusinessSpec" in Plan.model_json_schema()["$defs"]`。 调用`business_plan`、`Plan.model_validate`、`Plan.model_validate_json`、`plan.model_dump_json`、`Plan.model_json_schema`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_crud_plan_does_not_gain_serialized_null_business`（L166–L178）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L176断言`plan.business is None`；L177断言`"business" not in plan.model_dump()`；L178断言`"business" not in plan.model_dump_json()`。 调用`Plan.model_validate`、`plan.model_dump`、`plan.model_dump_json`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_contradictory_or_unsafe_contracts_fail_closed`（L226–L233）：接收`path`、`value`。 控制顺序：L229遍历`path[:-1]`。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_declarations_fail_closed`（L240–L244）：接收`collection`。 调用`business_plan`、`raw["business"][collection].append`、`deepcopy`、`pytest.raises`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_cannot_redeclare_server_owned_fields`（L247–L251）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`business_plan`、`raw["entities"][0]["fields"].append`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_no_arbitrary_executable_contract`（L254–L258）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_enum_predicates_must_reference_actual_state`（L261–L265）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_internal_tables_cannot_be_generated_entities`（L271–L275）：接收`reserved`。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_relation_wire_contract_is_text_even_when_native_storage_is_integer`（L278–L282）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_assignee_is_nullable_before_authorized_assignment`（L285–L289）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`business_plan`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_display_labels_preserve_stored_enum_contract`（L292–L309）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L302断言`value.choices == ["queued", "done"]`；L303断言`value.model_dump()["choice_labels"]["done"] == "已完成"`。 调用`FieldSpec`、`value.model_dump`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_contracts.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L309。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11831`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_contracts.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ec7eb46b686355c037251e30d5fd1bbd566035d35fea704b3bd09f5e5f820d22"} -->
````python
# tests/test_business_contracts.py
from copy import deepcopy

import pytest
from pydantic import ValidationError

from workbench.domain import Plan


def business_plan():
    return {
        "title": "Generic linked workflow",
        "data_scope": "shared",
        "acceptance": ["Verified"],
        "entities": [
            {
                "name": "customers",
                "description": "Customers",
                "fields": [{"name": "name", "kind": "text"}],
            },
            {
                "name": "requests",
                "description": "Requests",
                "fields": [
                    {"name": "customer_id", "kind": "text"},
                    {"name": "assignee_id", "kind": "text", "required": False},
                    {
                        "name": "request_state",
                        "kind": "enum",
                        "choices": ["new", "active", "resolved"],
                    },
                    {"name": "resolved_at", "kind": "datetime", "required": False},
                    {"name": "due_at", "kind": "datetime", "required": False},
                ],
            },
        ],
        "business": {
            "roles": [{"name": role, "label": role} for role in ["manager", "service", "employee"]],
            "registration": {"enabled": True, "default_role": "employee"},
            "bootstrap_role": "manager",
            "role_admin_roles": ["manager"],
            "resources": [
                {"entity": "customers"},
                {"entity": "requests", "assignee_field": "assignee_id"},
            ],
            "relations": [
                {"entity": "requests", "field": "customer_id", "target_entity": "customers"},
                {"entity": "requests", "field": "assignee_id", "target_entity": "$users"},
            ],
            "permissions": [
                {
                    "role": "manager",
                    "entity": "customers",
                    "actions": [
                        "create",
                        "read",
                        "update",
                        "archive",
                        "read_audit",
                        "read_metrics",
                    ],
                    "scope": "all",
                },
                {
                    "role": "manager",
                    "entity": "requests",
                    "actions": [
                        "create",
                        "read",
                        "update",
                        "assign",
                        "transition",
                        "read_metrics",
                        "read_history",
                    ],
                    "scope": "all",
                },
                {
                    "role": "service",
                    "entity": "requests",
                    "actions": ["read", "transition", "add_note"],
                    "scope": "assigned",
                },
                {
                    "role": "employee",
                    "entity": "requests",
                    "actions": ["create", "read", "read_history"],
                    "scope": "own",
                },
            ],
            "workflows": [
                {
                    "entity": "requests",
                    "status_field": "request_state",
                    "initial": "new",
                    "transitions": [
                        {
                            "name": "start",
                            "from_states": ["new"],
                            "to_state": "active",
                            "roles": ["manager", "service"],
                        },
                        {
                            "name": "resolve",
                            "from_states": ["active"],
                            "to_state": "resolved",
                            "roles": ["manager", "service"],
                            "set_timestamp": "resolved_at",
                        },
                    ],
                }
            ],
            "notifications": [
                {"entity": "requests", "event": "assigned", "recipient": "assignee"},
                {
                    "entity": "requests",
                    "event": "transitioned",
                    "transition": "resolve",
                    "recipient": "creator",
                },
                {
                    "entity": "requests",
                    "event": "due",
                    "due_field": "due_at",
                    "recipient": "assignee",
                },
            ],
            "metrics": [
                {"name": "total", "label": "Total", "entity": "requests", "kind": "count"},
                {
                    "name": "resolution",
                    "label": "Seconds",
                    "entity": "requests",
                    "kind": "average_duration",
                    "start_field": "created_at",
                    "end_field": "resolved_at",
                    "filters": [{"field": "request_state", "value": "resolved"}],
                },
                {
                    "name": "by_customer",
                    "label": "Customers",
                    "entity": "requests",
                    "kind": "group_count",
                    "group_by": "customer_id",
                },
                {
                    "name": "daily",
                    "label": "Daily",
                    "entity": "requests",
                    "kind": "time_count",
                    "time_field": "created_at",
                },
            ],
        },
    }


def test_generic_business_contract_roundtrip_and_schema():
    raw = business_plan()
    plan = Plan.model_validate(raw)
    assert Plan.model_validate_json(plan.model_dump_json()) == plan
    assert plan.business.registration.default_role == "employee"
    assert plan.business.metrics[1].unit == "seconds"
    assert "BusinessSpec" in Plan.model_json_schema()["$defs"]


def test_existing_crud_plan_does_not_gain_serialized_null_business():
    raw = {
        "title": "Old",
        "data_scope": "per_user",
        "entities": [
            {"name": "notes", "description": "Notes", "fields": [{"name": "body", "kind": "text"}]}
        ],
        "acceptance": ["CRUD"],
    }
    plan = Plan.model_validate(raw)
    assert plan.business is None
    assert "business" not in plan.model_dump()
    assert "business" not in plan.model_dump_json()


@pytest.mark.parametrize(
    "path,value",
    [
        (("business", "registration", "default_role"), "manager"),
        (("business", "bootstrap_role"), "unknown"),
        (("business", "role_admin_roles"), ["manager", "manager"]),
        (("business", "role_admin_roles"), ["service"]),
        (("data_scope",), "per_user"),
        (("business", "relations", 0, "target_entity"), "absent"),
        (("business", "relations", 0, "field"), "missing"),
        (("business", "relations", 1, "target_entity"), "customers"),
        (("business", "relations", 0, "on_delete"), "cascade"),
        (("business", "resources", 0, "assignee_field"), "name"),
        (("business", "resources", 0, "archive"), False),
        (("business", "resources", 0, "audit"), False),
        (("business", "resources", 1, "notes"), False),
        (("business", "permissions", 0, "role"), "unknown"),
        (("business", "permissions", 0, "entity"), "unknown"),
        (("business", "permissions", 0, "scope"), "assigned"),
        (("business", "permissions", 0, "actions"), ["read", "read"]),
        (("business", "permissions", 0, "actions"), ["delete"]),
        (("business", "workflows", 0, "initial"), "absent"),
        (("business", "workflows", 0, "status_field"), "customer_id"),
        (("business", "workflows", 0, "transitions", 0, "to_state"), "new"),
        (("business", "workflows", 0, "transitions", 0, "roles"), ["employee"]),
        (("business", "workflows", 0, "transitions", 1, "set_timestamp"), "created_at"),
        (("business", "notifications", 0, "channel"), "email"),
        (("business", "notifications", 1, "transition"), "absent"),
        (("business", "notifications", 2, "due_field"), "customer_id"),
        (("business", "metrics", 0, "group_by"), "customer_id"),
        (("business", "metrics", 1, "end_field"), "customer_id"),
        (("business", "metrics", 1, "end_field"), "created_at"),
        (("business", "metrics", 2, "group_by"), "missing"),
        (("business", "metrics", 3, "timezone"), "user-provided-SQL"),
        (("business", "metrics", 0, "filters"), [{"field": "created_at", "value": "2026-01-01"}]),
        (
            ("business", "metrics", 0, "filters"),
            [{"field": "customer_id", "value": {"sql": "1=1"}}],
        ),
        (
            ("business", "metrics", 0, "filters"),
            [{"field": "customer_id", "op": "in", "value": "not-list"}],
        ),
    ],
)
def test_contradictory_or_unsafe_contracts_fail_closed(path, value):
    raw = business_plan()
    current = raw
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


@pytest.mark.parametrize(
    "collection",
    ["roles", "resources", "relations", "permissions", "workflows", "notifications", "metrics"],
)
def test_duplicate_declarations_fail_closed(collection):
    raw = business_plan()
    raw["business"][collection].append(deepcopy(raw["business"][collection][0]))
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_business_cannot_redeclare_server_owned_fields():
    raw = business_plan()
    raw["entities"][0]["fields"].append({"name": "created_by", "kind": "text"})
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_no_arbitrary_executable_contract():
    raw = business_plan()
    raw["business"]["metrics"][0]["sql"] = "SELECT anything"
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_metric_enum_predicates_must_reference_actual_state():
    raw = business_plan()
    raw["business"]["metrics"][1]["filters"][0]["value"] = "invented-state"
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


@pytest.mark.parametrize(
    "reserved", ["business_audit", "business_notes", "business_notifications", "business_setup"]
)
def test_runtime_internal_tables_cannot_be_generated_entities(reserved):
    raw = business_plan()
    raw["entities"][0]["name"] = reserved
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_relation_wire_contract_is_text_even_when_native_storage_is_integer():
    raw = business_plan()
    raw["entities"][1]["fields"][0]["kind"] = "integer"
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_assignee_is_nullable_before_authorized_assignment():
    raw = business_plan()
    raw["entities"][1]["fields"][1]["required"] = True
    with pytest.raises(ValidationError):
        Plan.model_validate(raw)


def test_display_labels_preserve_stored_enum_contract():
    from workbench.domain import FieldSpec

    value = FieldSpec(
        name="status",
        kind="enum",
        choices=["queued", "done"],
        label="处理状态",
        choice_labels={"queued": "待处理", "done": "已完成"},
    )
    assert value.choices == ["queued", "done"]
    assert value.model_dump()["choice_labels"]["done"] == "已完成"
    with pytest.raises(ValueError, match="choice_labels"):
        FieldSpec(
            name="status", kind="enum", choices=["queued"], choice_labels={"unknown": "不存在"}
        )
    with pytest.raises(ValueError, match="choice_labels"):
        FieldSpec(name="description", kind="text", choice_labels={"queued": "待处理"})
````
