# tests/test_permission_contract_equivalence.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.domain`、`workbench.requirement_coverage`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `recorded`（L28–L52）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L30遍历`RECORDED.items()`；L32断言`len(raw) == size`；L33断言`hashlib.sha256(raw).hexdigest() == digest`；L37断言`data["approval_status"] == "unapproved"`；L38断言`data["execution_authorized"] is False`；L39断言`data["purpose"] == "offline_contract_validation_only"`；L40断言`summary["passed"] is False`；L41断言`summary["run_identity"] == [ "36840557604", "1", "dd7e5f2135fdfe8b84f36dd1de5ab6e090c…`。后续分支沿下方源码相同行号继续阅读。 调用`RECORDED.items`、`(FIXTURES / filename).read_bytes`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`json.loads`、`sum`、`receipt.get`、`Requirement.model_validate`等。 返回路径：L50的`Requirement.model_validate(data["requirement"]), Plan.model_validate( data["candidate_plan…`。
- `grant`（L55–L62）：接收`role`、`entity`、`scope`、`actions`、`**restrictions`。 返回路径：L56的`{ "role": role, "entity": entity, "scope": scope, "actions": actions if actions is not Non…`。
- `case`（L65–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`permission`、`Requirement`、`grant`。 返回路径：L74的`requirement, plan`。
- `permission`（L77–L80）：接收`plan`、`role`、`entity`。 调用`next`。 返回路径：L78的`next( item for item in plan.business.permissions if item.role == role and item.entity == e…`。
- `test_exact_unapproved_fastapi_split_grants_are_covered_without_rewriting_either_contract`（L83–L98）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87断言`[ row["actions"] for row in rows if row["role"] == "service" and row["entity"] == "cu…`；L93断言`permission(plan).actions == ["read", "read_metrics"]`；L95断言`business_gaps(requirement, plan, diagnostics=diagnostics) == diagnostics == []`；L96断言`coverage_gaps(requirement, plan) == []`；L97断言`(requirement.model_dump(), plan.model_dump()) == original`。 调用`recorded`、`requirement.model_dump`、`plan.model_dump`、`permission`、`business_gaps`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recorded_permission_losses_and_authorization_expansion_remain_blocked`（L115–L144）：接收`mutation`。 控制顺序：L120按`mutation.startswith("missing_") and mutation != "missing_row"`分支；L122按`mutation == "missing_row"`分支；L124按`mutation == "scope"`分支；L126按`mutation == "scope_widening"`分支；L130按`mutation == "foreign_role"`分支；L133按`mutation == "foreign_entity"`分支；L135按`mutation == "extra_row"`分支；L142断言`mutation in {"foreign_entity", "unknown_action"}`。后续分支沿下方源码相同行号继续阅读。 调用`recorded`、`original.model_dump`、`next`、`mutation.startswith`、`target["actions"].remove`、`rows.remove`、`value["business"]["roles"].append`、`rows.append`、`grant`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_split_grants_never_allow_unapproved_action_supersets`（L160–L164）：接收`action`。 控制顺序：L162断言`business_gaps(requirement, plan) == []`；L164断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`permission(plan).actions.append`、`permission`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_same_collection_split_grants_support_structural_encodings_and_order`（L181–L203）：接收`encoding`、`reverse`。 控制顺序：L184按`reverse`分支；L187按`encoding == "nested"`分支；L189按`encoding == "json_list"`分支；L191按`encoding == "json_item"`分支；L193按`encoding == "json_wrapper"`分支；L195按`encoding == "keyed"`分支；L197按`encoding == "nested_list"`分支；L199按`encoding == "entity_inherited"`分支。后续分支沿下方源码相同行号继续阅读。 调用`case`、`rows.reverse`、`permission(plan).actions.reverse`、`permission`、`json.dumps`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_positive_rows_are_idempotent_but_duplicate_plan_rows_stay_invalid`（L206–L213）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L209断言`business_gaps(requirement, plan) == []`。 调用`case`、`requirement.facts["permissions"].append`、`grant`、`business_gaps`、`plan.model_dump`、`value["business"]["permissions"].append`、`permission(plan).model_dump`、`permission`、`pytest.raises`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_matrix_preserves_all_permission_actions_under_arbitrary_partitioning`（L218–L239）：接收`chunk_size`、`reverse`。 控制顺序：L223遍历`plan.business.permissions`；L225遍历`range(0, len(actions), chunk_size)`；L234断言`business_gaps(requirement, plan) == []`；L235遍历`plan.business.permissions`；L236遍历`item.actions`；L239断言`business_gaps(requirement, changed)`。 调用`case`、`range`、`len`、`rows.append`、`item.model_dump`、`role.model_dump`、`resource.model_dump`、`business_gaps`、`plan.model_copy`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actions_cannot_be_borrowed_from_another_role_entity_or_scope`（L252–L255）：接收`key`、`value`。 控制顺序：L255断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_descriptors_do_not_authorize_pooling`（L259–L262）：接收`missing`。 控制顺序：L262断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_or_unknown_positive_actions_cannot_be_laundered_through_valid_row`（L279–L286）：接收`actions`。 控制顺序：L282按`actions is None`分支；L285断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L286断言`any(item["code"] == "business_unsupported_shape" for item in diagnostics)`。 调用`case`、`requirement.facts["permissions"].append`、`grant`、`business_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_original_restriction_stays_binding_after_positive_union`（L299–L302）：接收`restriction`、`row`。 控制顺序：L302断言`business_gaps(requirement, plan)`。 调用`case`、`requirement.facts["permissions"][row].update`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_actions_in_restrictions_fail_closed`（L306–L311）：接收`key`。 控制顺序：L310断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L311断言`any(item["code"] == "business_unsupported_shape" for item in diagnostics)`。 调用`case`、`business_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_read_only_allows_split_read_metrics_but_rejects_even_explicit_write_union`（L314–L320）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L317断言`business_gaps(requirement, plan) == []`；L320断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`requirement.facts["permissions"].append`、`grant`、`permission(plan).actions.append`、`permission`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_independent_permission_collections_cannot_authorize_each_others_extras`（L325–L353）：接收`complete`、`placement`。 控制顺序：L343按`complete`分支；L345按`placement == "siblings"`分支；L347按`placement == "nested"`分支；L352断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L353断言`any(item["source"]["domain"] == "permissions" for item in diagnostics)`。 调用`case`、`permission`、`row.model_dump`、`next`、`deepcopy`、`business_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_presentation_only_permissions_never_add_authority`（L356–L360）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L360断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_merged_failures_keep_original_source_indices_and_exact_required_action_set`（L363–L369）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L367断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L368断言`{item["source"]["path"] for item in diagnostics} == {"permissions.0", "permissions.1"…`；L369断言`all(item["expected"]["actions"] == ["read", "read_metrics"] for item in diagnostics)`。 调用`case`、`permission`、`business_gaps`、`all`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_permission_contract_equivalence.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L369。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13553`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_permission_contract_equivalence.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "441d76d961b1bde48f5d80784165c7a30cbe870dcc86bf46635b4d2e47fdc2fd"} -->
````python
# tests/test_permission_contract_equivalence.py
"""Pure permission validators; recorded unapproved candidates are never executed."""

import hashlib
import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.requirement_coverage import coverage_gaps
from workbench.settings import ROOT

FIXTURES = ROOT / "tests/fixtures/customer_design_diagnostics/dd7e5f2"
RECORDED = {
    "fastapi-unapproved-design.json": (
        49980,
        "9c8cdc4576208ee3f3954d724a7789e2f635e50ae25b66f65d75e34d0e41b5f5",
    ),
    "fastapi-summary.json": (
        17671,
        "a7782be7e86a74cfae44ca9ccad835107ac4a7de2e7fff9ebcb4d747b6138e7a",
    ),
}


def recorded():
    values = {}
    for filename, (size, digest) in RECORDED.items():
        raw = (FIXTURES / filename).read_bytes()
        assert len(raw) == size
        assert hashlib.sha256(raw).hexdigest() == digest
        values[filename] = json.loads(raw)
    data = values["fastapi-unapproved-design.json"]
    summary = values["fastapi-summary.json"]
    assert data["approval_status"] == "unapproved"
    assert data["execution_authorized"] is False
    assert data["purpose"] == "offline_contract_validation_only"
    assert summary["passed"] is False
    assert summary["run_identity"] == [
        "36840557604",
        "1",
        "dd7e5f2135fdfe8b84f36dd1de5ab6e090c6a45a",
    ]
    assert summary["failure_details"]["coverage_block_count"] == 2
    assert (
        sum(receipt.get("schema_valid") is False for receipt in summary["provider_receipts"]) == 2
    )
    return Requirement.model_validate(data["requirement"]), Plan.model_validate(
        data["candidate_plan"]
    )


def grant(role="service", entity="customers", scope="all", actions=None, **restrictions):
    return {
        "role": role,
        "entity": entity,
        "scope": scope,
        "actions": actions if actions is not None else ["read"],
        **restrictions,
    }


def case():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    permission(plan).actions = ["read", "read_metrics"]
    requirement = Requirement(
        summary="客服", users=[], data_scope="shared", features=[], acceptance=[], facts={}
    )
    requirement.facts = {"permissions": [grant(), grant(actions=["read_metrics"])]}
    return requirement, plan


def permission(plan, role="service", entity="customers"):
    return next(
        item for item in plan.business.permissions if item.role == role and item.entity == entity
    )


def test_exact_unapproved_fastapi_split_grants_are_covered_without_rewriting_either_contract():
    requirement, plan = recorded()
    original = (requirement.model_dump(), plan.model_dump())
    rows = requirement.facts["business"]["permissions"]
    assert [
        row["actions"] for row in rows if row["role"] == "service" and row["entity"] == "customers"
    ] == [
        ["read"],
        ["read_metrics"],
    ]
    assert permission(plan).actions == ["read", "read_metrics"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics) == diagnostics == []
    assert coverage_gaps(requirement, plan) == []
    assert (requirement.model_dump(), plan.model_dump()) == original
    recorded()  # Raw hashes, unapproved status, and original failing receipts stay unchanged.


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_read",
        "missing_metrics",
        "missing_row",
        "scope",
        "scope_widening",
        "foreign_role",
        "foreign_entity",
        "extra_row",
        "unknown_action",
    ],
)
def test_recorded_permission_losses_and_authorization_expansion_remain_blocked(mutation):
    requirement, original = recorded()
    value = original.model_dump()
    rows = value["business"]["permissions"]
    target = next(row for row in rows if row["role"] == "service" and row["entity"] == "customers")
    if mutation.startswith("missing_") and mutation != "missing_row":
        target["actions"].remove("read" if mutation == "missing_read" else "read_metrics")
    elif mutation == "missing_row":
        rows.remove(target)
    elif mutation == "scope":
        target["scope"] = "own"
    elif mutation == "scope_widening":
        next(row for row in rows if row["role"] == "employee" and row["entity"] == "requests")[
            "scope"
        ] = "all"
    elif mutation == "foreign_role":
        value["business"]["roles"].append({"name": "outsider", "label": "Outsider"})
        target["role"] = "outsider"
    elif mutation == "foreign_entity":
        target["entity"] = "foreign_resource"
    elif mutation == "extra_row":
        rows.append(grant(role="employee", entity="tasks"))
    else:
        target["actions"].append("delete_everything")
    try:
        candidate = Plan.model_validate(value)
    except ValidationError:
        assert mutation in {"foreign_entity", "unknown_action"}
    else:
        assert business_gaps(requirement, candidate), mutation


@pytest.mark.parametrize(
    "action",
    [
        "create",
        "update",
        "archive",
        "assign",
        "transition",
        "add_note",
        "read_audit",
        "read_history",
    ],
)
def test_split_grants_never_allow_unapproved_action_supersets(action):
    requirement, plan = case()
    assert business_gaps(requirement, plan) == []
    permission(plan).actions.append(action)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "encoding",
    [
        "native",
        "nested",
        "json_list",
        "json_item",
        "json_wrapper",
        "keyed",
        "nested_list",
        "entity_inherited",
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_same_collection_split_grants_support_structural_encodings_and_order(encoding, reverse):
    requirement, plan = case()
    rows = requirement.facts["permissions"]
    if reverse:
        rows.reverse()
        permission(plan).actions.reverse()
    if encoding == "nested":
        requirement.facts = {"confirmed": {"business": requirement.facts}}
    elif encoding == "json_list":
        requirement.facts["permissions"] = json.dumps(rows)
    elif encoding == "json_item":
        requirement.facts["permissions"] = [json.dumps(row) for row in rows]
    elif encoding == "json_wrapper":
        requirement.facts = {"confirmed": json.dumps(requirement.facts)}
    elif encoding == "keyed":
        requirement.facts["permissions"] = {"first": rows[0], "second": rows[1]}
    elif encoding == "nested_list":
        requirement.facts["permissions"] = [[rows[0]], [rows[1]]]
    elif encoding == "entity_inherited":
        for row in rows:
            del row["entity"]
        requirement.facts = {"entities": [{"name": "customers", "permissions": rows}]}
    assert business_gaps(requirement, plan) == []


def test_duplicate_positive_rows_are_idempotent_but_duplicate_plan_rows_stay_invalid():
    requirement, plan = case()
    requirement.facts["permissions"].append(grant(actions=["read", "view_metrics"]))
    assert business_gaps(requirement, plan) == []
    value = plan.model_dump()
    value["business"]["permissions"].append(permission(plan).model_dump())
    with pytest.raises(ValidationError, match="Duplicate/contradictory business declaration"):
        Plan.model_validate(value)


@pytest.mark.parametrize("chunk_size", [1, 2, 3])
@pytest.mark.parametrize("reverse", [False, True])
def test_complete_matrix_preserves_all_permission_actions_under_arbitrary_partitioning(
    chunk_size, reverse
):
    requirement, plan = case()
    rows = []
    for item in plan.business.permissions:
        actions = item.actions[::-1] if reverse else item.actions
        for start in range(0, len(actions), chunk_size):
            rows.append({**item.model_dump(), "actions": actions[start : start + chunk_size]})
    requirement.facts = {
        "business": {
            "roles": [role.model_dump() for role in plan.business.roles],
            "resources": [resource.model_dump() for resource in plan.business.resources],
            "permissions": rows[::-1] if reverse else rows,
        }
    }
    assert business_gaps(requirement, plan) == []
    for item in plan.business.permissions:
        for action in item.actions:
            changed = plan.model_copy(deep=True)
            permission(changed, item.role, item.entity).actions.remove(action)
            assert business_gaps(requirement, changed), (item.role, item.entity, action)


@pytest.mark.parametrize(
    "key,value",
    [
        ("role", "employee"),
        ("entity", "requests"),
        ("scope", "own"),
        ("scope", "assigned"),
        ("scope", "team"),
    ],
)
def test_actions_cannot_be_borrowed_from_another_role_entity_or_scope(key, value):
    requirement, plan = case()
    requirement.facts["permissions"][1][key] = value
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("missing", ["role", "entity", "scope", "actions"])
def test_partial_descriptors_do_not_authorize_pooling(missing):
    requirement, plan = case()
    del requirement.facts["permissions"][1][missing]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "actions",
    [
        None,
        True,
        "read_metrics",
        {"read_metrics": True},
        [],
        ["read_metrics", "read_metrics"],
        ["read_metrics", "view_metrics"],
        ["unknown_action"],
        ["read_metrics", "unknown_action"],
    ],
)
def test_malformed_or_unknown_positive_actions_cannot_be_laundered_through_valid_row(actions):
    requirement, plan = case()
    requirement.facts["permissions"].append(grant(actions=actions))
    if actions is None:
        requirement.facts["permissions"][-1]["actions"] = None
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


@pytest.mark.parametrize(
    "restriction",
    [
        {"only_actions": ["read"]},
        {"denied_actions": ["read_metrics"]},
        {"forbidden_actions": ["view_metrics"]},
        {"read_only": "yes"},
    ],
)
@pytest.mark.parametrize("row", [0, 1])
def test_every_original_restriction_stays_binding_after_positive_union(restriction, row):
    requirement, plan = case()
    requirement.facts["permissions"][row].update(restriction)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("key", ["only_actions", "denied_actions", "forbidden_actions"])
def test_unknown_actions_in_restrictions_fail_closed(key):
    requirement, plan = case()
    requirement.facts["permissions"][0][key] = ["unknown_action"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


def test_read_only_allows_split_read_metrics_but_rejects_even_explicit_write_union():
    requirement, plan = case()
    requirement.facts["permissions"][0]["read_only"] = True
    assert business_gaps(requirement, plan) == []
    requirement.facts["permissions"].append(grant(actions=["update"]))
    permission(plan).actions.append("update")
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("complete", [False, True])
@pytest.mark.parametrize("placement", ["siblings", "nested", "colliding_display_path"])
def test_independent_permission_collections_cannot_authorize_each_others_extras(
    complete, placement
):
    requirement, plan = case()
    # Use a non-metric action so neither collection gets independent metric approval.
    permission(plan).actions = ["read", "update"]
    first = {"permissions": [row.model_dump() for row in plan.business.permissions]}
    next(
        row
        for row in first["permissions"]
        if row["role"] == "service" and row["entity"] == "customers"
    )["actions"] = ["read"]
    second = deepcopy(first)
    next(
        row
        for row in second["permissions"]
        if row["role"] == "service" and row["entity"] == "customers"
    )["actions"] = ["read", "update"]
    if complete:
        first["permissions_complete"] = second["permissions_complete"] = True
    if placement == "siblings":
        requirement.facts = {"business": first, "business_constraints": second}
    elif placement == "nested":
        requirement.facts = {"business": {**first, "business_constraints": second}}
    else:
        requirement.facts = {"confirmed.business": first, "confirmed": {"business": second}}
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["source"]["domain"] == "permissions" for item in diagnostics)


def test_presentation_only_permissions_never_add_authority():
    requirement, plan = case()
    rows = requirement.facts["permissions"]
    requirement.facts = {"permissions": [rows[0]], "labels": {"permissions": [rows[1]]}}
    assert business_gaps(requirement, plan)


def test_merged_failures_keep_original_source_indices_and_exact_required_action_set():
    requirement, plan = case()
    permission(plan).actions = ["read"]
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert {item["source"]["path"] for item in diagnostics} == {"permissions.0", "permissions.1"}
    assert all(item["expected"]["actions"] == ["read", "read_metrics"] for item in diagnostics)
````
