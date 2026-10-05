# tests/test_native_plan_normalization.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.native_modules`、`workbench.native_plan_normalization`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `registration`（L26–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`。 返回路径：L27的`Plan.model_validate( { "title": "Registration", "data_scope": "shared", "acceptance": ["CR…`。
- `approved`（L43–L59）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Requirement.model_validate`。 返回路径：L44的`Requirement.model_validate( { "summary": "报名", "users": ["管理员"], "data_scope": "shared", "…`。
- `test_nine_field_replay_maps_audit_collision_without_inventing_required_fields`（L63–L83）：接收`template`。 控制顺序：L70断言`[field.name for field in normalized.entities[0].fields] == [ *NAMES[:-1], "registrati…`；L74断言`all(not field.required for field in normalized.entities[0].fields)`；L75断言`coverage_gaps(requirement, normalized, native_normalization=report) == []`；L76断言`(plan.model_dump(), requirement.model_dump()) == snapshot`；L77断言`source_plan(normalized, report) == plan`；L78断言`normalize_native_plan(plan, requirement, template) == (normalized, report)`；L79断言`normalize_native_plan(normalized, requirement, template, prior_normalization=report) …`；L83断言`normalize_native_plan(normalized, requirement, template)[0] == normalized`。 调用`registration`、`approved`、`plan.model_dump`、`requirement.model_dump`、`pytest.raises`、`validate_plan`、`normalize_native_plan`、`all`、`coverage_gaps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collision_safe_names_and_constraint_drift_stays_blocked`（L86–L100）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L92断言`normalized.entities[0].fields[-2].name == "registration_status_2"`；L95断言`coverage_gaps( requirement, normalized, native_normalization=report, diagnostics=diag…`；L98断言`any( item.get("attribute") == "required" and item["source"]["index"] == 8 for item in…`。 调用`registration().model_dump`、`registration`、`data["entities"][0]["fields"].append`、`approved().model_copy`、`approved`、`normalize_native_plan`、`coverage_gaps`、`any`、`item.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rule_example_keys_change_but_example_values_and_labels_never_do`（L103–L118）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L115断言`normalized.custom_rules[0].accept_examples == [{"registration_status": "status"}]`；L116断言`normalized.custom_rules[0].description == "registration_status must be allowed"`；L117断言`normalized.entities[0].fields[-1].label == "status"`；L118断言`source_plan(normalized, report) == Plan.model_validate(data)`。 调用`registration().model_dump`、`registration`、`normalize_native_plan`、`approved`、`source_plan`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_references_are_remapped_without_changing_values_or_permissions`（L121–L150）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L141断言`normalized.business.workflows[0].status_field == "requests_status"`；L142断言`normalized.business.workflows[0].transitions[-1].set_timestamp == "requests_updated_t…`；L143断言`normalized.business.notifications[-1].due_field == "requests_deleted_time"`；L144断言`normalized.business.resources[-1].assignee_field == "requests_created_id"`；L145断言`normalized.business.relations[0].field == "requests_uuid"`；L146断言`normalized.business.metrics[1].filters[0].field == "requests_status"`；L147断言`normalized.business.metrics[2].group_by == "requests_uuid"`；L148断言`normalized.business.permissions == original.business.permissions`。后续分支沿下方源码相同行号继续阅读。 调用`business_plan`、`Plan.model_validate`、`rename`、`normalize_native_plan`、`approved`、`source_plan`、`validate_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_references_are_remapped_without_changing_values_or_permissions.rename`（L132–L137）：接收`value`。 控制顺序：L133按`isinstance(value, dict)`分支；L135按`isinstance(value, list)`分支。 调用`isinstance`、`rename`、`value.items`、`replacements.get`。 返回路径：L134的`{key: rename(item) for key, item in value.items()}`；L136的`[rename(item) for item in value]`；L137的`replacements.get(value, value) if isinstance(value, str) else value`。
- `test_python_template_unchanged_and_invalid_mapping_rejected`（L153–L162）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L156断言`normalized == plan`；L157断言`report["field_mappings"] == []`。 调用`registration`、`normalize_native_plan`、`approved`、`deepcopy`、`pytest.raises`、`source_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_replanning_with_prior_mapping_accepts_source_names_and_detects_missing_field`（L165–L177）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L168断言`normalize_native_plan(plan, requirement, "fastapiadmin", prior_normalization=report) …`；L177断言`coverage_gaps(requirement, next_plan, native_normalization=next_report)`。 调用`registration`、`approved`、`normalize_native_plan`、`plan.model_dump`、`omitted["entities"][0]["fields"].pop`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_long_names_stay_within_identifier_limit_with_deterministic_suffix`（L180–L190）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L188断言`plan.entities[0].fields[0].name == "registration_archive_updated_time_2"`；L190断言`source_plan(plan, report) == Plan.model_validate(data)`。 调用`registration().model_dump`、`registration`、`normalize_native_plan`、`approved`、`validate_plan`、`source_plan`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_plan_normalization.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L190。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7845`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_plan_normalization.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d58a0fdb40369fbd34a12ed9d01056d49f69df95b55a577b5b004d47970a5135"} -->
````python
# tests/test_native_plan_normalization.py
"""Replay the nine-field registration recommendation without live project data."""

from copy import deepcopy

import pytest
from test_business_contracts import business_plan

from workbench.domain import Plan, Requirement
from workbench.native_modules import validate_plan
from workbench.native_plan_normalization import normalize_native_plan, source_plan
from workbench.requirement_coverage import coverage_gaps

NAMES = [
    "applicant_name",
    "student_id",
    "school",
    "phone",
    "email",
    "category",
    "project_name",
    "project_description",
    "status",
]


def registration():
    return Plan.model_validate(
        {
            "title": "Registration",
            "data_scope": "shared",
            "acceptance": ["CRUD"],
            "entities": [
                {
                    "name": "registration",
                    "description": "报名",
                    "fields": [{"name": name, "kind": "text", "required": False} for name in NAMES],
                }
            ],
        }
    )


def approved():
    return Requirement.model_validate(
        {
            "summary": "报名",
            "users": ["管理员"],
            "data_scope": "shared",
            "features": ["CRUD"],
            "acceptance": ["CRUD"],
            "field_requirements": [
                {"entity": "registration", "field": name, "required": False} for name in NAMES
            ],
            "entity_requirements": [
                {"entity": "registration", "fields": NAMES, "additional_fields": False}
            ],
            "additional_entities": False,
        }
    )


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_nine_field_replay_maps_audit_collision_without_inventing_required_fields(template):
    plan, requirement = registration(), approved()
    snapshot = (plan.model_dump(), requirement.model_dump())
    with pytest.raises(ValueError, match="Field conflicts with native framework audit columns"):
        validate_plan(plan)
    normalized, report = normalize_native_plan(plan, requirement, template)
    validate_plan(normalized)
    assert [field.name for field in normalized.entities[0].fields] == [
        *NAMES[:-1],
        "registration_status",
    ]
    assert all(not field.required for field in normalized.entities[0].fields)
    assert coverage_gaps(requirement, normalized, native_normalization=report) == []
    assert (plan.model_dump(), requirement.model_dump()) == snapshot
    assert source_plan(normalized, report) == plan
    assert normalize_native_plan(plan, requirement, template) == (normalized, report)
    assert normalize_native_plan(normalized, requirement, template, prior_normalization=report) == (
        normalized,
        report,
    )
    assert normalize_native_plan(normalized, requirement, template)[0] == normalized


def test_collision_safe_names_and_constraint_drift_stays_blocked():
    data = registration().model_dump()
    data["entities"][0]["fields"].append({"name": "registration_status", "kind": "text"})
    requirement = approved().model_copy(deep=True)
    requirement.entity_requirements[0].additional_fields = True
    normalized, report = normalize_native_plan(data, requirement, "fastapiadmin")
    assert normalized.entities[0].fields[-2].name == "registration_status_2"
    normalized.entities[0].fields[-2].required = True
    diagnostics = []
    assert coverage_gaps(
        requirement, normalized, native_normalization=report, diagnostics=diagnostics
    )
    assert any(
        item.get("attribute") == "required" and item["source"]["index"] == 8 for item in diagnostics
    )


def test_rule_example_keys_change_but_example_values_and_labels_never_do():
    data = registration().model_dump()
    data["entities"][0]["fields"][-1]["label"] = "status"
    data["custom_rules"] = [
        {
            "entity": "registration",
            "description": "status must be allowed",
            "accept_examples": [{"status": "status"}],
            "reject_examples": [{"status": "no"}],
        }
    ]
    normalized, report = normalize_native_plan(data, approved(), "fastapiadmin")
    assert normalized.custom_rules[0].accept_examples == [{"registration_status": "status"}]
    assert normalized.custom_rules[0].description == "registration_status must be allowed"
    assert normalized.entities[0].fields[-1].label == "status"
    assert source_plan(normalized, report) == Plan.model_validate(data)


def test_business_references_are_remapped_without_changing_values_or_permissions():
    data = business_plan()
    # Fixture replacement changes a real workflow, its predicates and refs.
    replacements = {
        "request_state": "status",
        "resolved_at": "updated_time",
        "due_at": "deleted_time",
        "assignee_id": "created_id",
        "customer_id": "uuid",
    }

    def rename(value):
        if isinstance(value, dict):
            return {key: rename(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rename(item) for item in value]
        return replacements.get(value, value) if isinstance(value, str) else value

    original = Plan.model_validate(rename(data))
    normalized, report = normalize_native_plan(original, approved(), "fastapiadmin")
    assert normalized.business.workflows[0].status_field == "requests_status"
    assert normalized.business.workflows[0].transitions[-1].set_timestamp == "requests_updated_time"
    assert normalized.business.notifications[-1].due_field == "requests_deleted_time"
    assert normalized.business.resources[-1].assignee_field == "requests_created_id"
    assert normalized.business.relations[0].field == "requests_uuid"
    assert normalized.business.metrics[1].filters[0].field == "requests_status"
    assert normalized.business.metrics[2].group_by == "requests_uuid"
    assert normalized.business.permissions == original.business.permissions
    assert source_plan(normalized, report) == original
    validate_plan(normalized)


def test_python_template_unchanged_and_invalid_mapping_rejected():
    plan = registration()
    normalized, report = normalize_native_plan(plan, approved(), "python-basic")
    assert normalized == plan
    assert report["field_mappings"] == []
    normalized, report = normalize_native_plan(plan, approved(), "fastapiadmin")
    invalid = deepcopy(report)
    invalid["field_mappings"][0]["source_field"] = "applicant_name"
    with pytest.raises(ValueError, match="映射无效"):
        source_plan(normalized, invalid)


def test_replanning_with_prior_mapping_accepts_source_names_and_detects_missing_field():
    plan, requirement = registration(), approved()
    normalized, report = normalize_native_plan(plan, requirement, "fastapiadmin")
    assert normalize_native_plan(plan, requirement, "fastapiadmin", prior_normalization=report) == (
        normalized,
        report,
    )
    omitted = plan.model_dump()
    omitted["entities"][0]["fields"].pop()
    next_plan, next_report = normalize_native_plan(
        omitted, requirement, "fastapiadmin", prior_normalization=report
    )
    assert coverage_gaps(requirement, next_plan, native_normalization=next_report)


def test_long_names_stay_within_identifier_limit_with_deterministic_suffix():
    data = registration().model_dump()
    data["entities"][0]["name"] = "registration_archive"
    data["entities"][0]["fields"] = [
        {"name": "updated_time", "kind": "text", "required": False},
        {"name": "registration_archive_updated_time", "kind": "text", "required": False},
    ]
    plan, report = normalize_native_plan(data, approved(), "fastapiadmin")
    assert plan.entities[0].fields[0].name == "registration_archive_updated_time_2"
    validate_plan(plan)
    assert source_plan(plan, report) == Plan.model_validate(data)
````
