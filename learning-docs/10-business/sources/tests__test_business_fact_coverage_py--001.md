# tests/test_business_fact_coverage.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `case`（L14–L21）：接收`facts`。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Requirement`。 返回路径：L21的`requirement, plan`。
- `test_business_declarations_keep_semantics_in_all_structural_encodings`（L26–L43）：接收`domain`、`encoding`。 控制顺序：L30按`encoding == "json_list"`分支；L32按`encoding == "json_item"`分支；L35按`encoding == "nested"`分支；L37按`encoding == "json_wrapper"`分支；L39断言`business_gaps(requirement, plan) == []`；L41断言`business_gaps(requirement, plan)`；L43断言`business_gaps(requirement, plan)`。 调用`case`、`getattr(plan.business, domain)[0].model_dump`、`getattr`、`json.dumps`、`business_gaps`、`getattr(plan.business, domain).pop`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_domain_meaning_is_not_satisfied_by_same_name`（L68–L74）：接收`domain`、`index`、`attribute`、`value`。 控制顺序：L72断言`business_gaps(requirement, plan) == []`；L74断言`business_gaps(requirement, plan)`。 调用`case`、`getattr(plan.business, domain)[index].model_dump`、`getattr`、`business_gaps`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_role_scopes_are_actual_read_metrics_grants`（L81–L91）：接收`scope`、`encoding`。 控制顺序：L85断言`business_gaps(requirement, plan) == []`；L91断言`len(gaps) == 1 and "role_scope" in gaps[0]`。 调用`case`、`json.dumps`、`business_gaps`、`next`、`permission.actions.remove`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_role_scope_mapping_cannot_widen_row_access`（L94–L102）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L98断言`business_gaps(requirement, plan) == []`；L102断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_explicit_metric_scope_blocks_without_guessing`（L119–L122）：接收`scope`。 控制顺序：L122断言`len(gaps) == 1 and "形状不支持" in gaps[0] and "metrics.0.role_scope" in gaps[0]`。 调用`case`、`business_gaps`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_undeclared_role_cannot_receive_metric_access_through_other_roles`（L125–L127）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L127断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_keyed_dictionary_and_entity_container_preserve_identity`（L130–L136）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`business_gaps(requirement, plan) == []`；L136断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_keyed_metric_names_can_be_descriptor_keywords`（L140–L145）：接收`name`。 控制顺序：L143断言`business_gaps(requirement, plan) == []`；L145断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`plan.business.metrics.pop`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_entity_mapping_does_not_derive_its_scope_from_surviving_plan_entities`（L148–L152）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L152断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_keyed_field_named_metrics_is_not_a_metric_declaration`（L155–L158）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L158断言`business_gaps(requirement, plan) == []`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_names_that_are_field_keywords_remain_business_identifiers`（L162–L167）：接收`name`。 控制顺序：L165断言`business_gaps(requirement, plan) == []`；L167断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`plan.business.metrics.pop`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_containers_and_display_metadata_do_not_invent_business_obligations`（L170–L180）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L180断言`business_gaps(requirement, plan) == []`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_filters_default_eq_and_preserve_literal_json_looking_values`（L183–L204）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L194断言`business_gaps(requirement, plan) == []`；L202断言`business_gaps(requirement, plan) == []`；L204断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_explicit_filters_cannot_match_any_existing_predicate`（L210–L212）：接收`filters`。 控制顺序：L212断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_transition_roles_and_timestamps_remain_semantic_obligations`（L215–L221）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L219断言`business_gaps(requirement, plan) == []`；L221断言`business_gaps(requirement, plan)`。 调用`case`、`workflow.model_dump`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_scalar_business_prose_is_not_flattened_into_field_or_business_descriptors`（L224–L229）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L229断言`business_gaps(requirement, plan) == []`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structural_aliases_preserve_exact_domain_meaning`（L244–L254）：接收`domain`、`index`、`aliases`、`encoded`。 控制顺序：L247遍历`aliases.items()`；L251断言`business_gaps(requirement, plan) == []`；L253断言`business_gaps(requirement, plan)`；L254断言`requirement.model_dump_json() == before`。 调用`case`、`getattr(plan.business, domain)[index].model_dump`、`getattr`、`aliases.items`、`descriptor.pop`、`json.dumps`、`requirement.model_dump_json`、`business_gaps`、`getattr(plan.business, domain).pop`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_workflow_state_and_timestamp_aliases_are_checked`（L258–L270）：接收`alias`。 控制顺序：L261遍历`descriptor["transitions"]`；L265按`timestamp`分支；L268断言`business_gaps(requirement, plan) == []`；L270断言`business_gaps(requirement, plan)`。 调用`case`、`plan.business.workflows[0].model_dump`、`transition.pop`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_filter_aliases_cannot_lose_the_actual_predicate`（L276–L282）：接收`predicate`。 控制顺序：L280断言`business_gaps(requirement, plan) == []`；L282断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_action_aliases_still_require_real_action`（L295–L307）：接收`alias`、`action`。 控制顺序：L305断言`business_gaps(requirement, plan) == []`；L307断言`business_gaps(requirement, plan)`。 调用`case`、`next`、`permission.model_dump`、`business_gaps`、`permission.actions.remove`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_read_only_allows_independently_approved_metrics_but_never_writes`（L310–L339）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L337断言`business_gaps(requirement, plan) == []`；L339断言`business_gaps(requirement, plan)`。 调用`case`、`next`、`business_gaps`、`permission.actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_action_restrictions_override_other_positive_grants`（L350–L373）：接收`restriction`。 控制顺序：L373断言`business_gaps(requirement, plan)`。 调用`case`、`next`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `complete_policy_case`（L376–L387）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`case`、`item.model_dump`。 返回路径：L387的`requirement, plan`。
- `test_complete_policy_rejects_new_rows_roles_admins_and_privilege_expansion`（L393–L420）：接收`mutation`。 控制顺序：L397断言`business_gaps(requirement, plan) == []`；L398按`mutation == "extra_row"`分支；L402按`mutation == "extra_role"`分支；L404按`mutation == "admin_role"`分支；L406按`mutation == "scope"`分支；L419断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L420断言`diagnostics and diagnostics[0]["expected"] != diagnostics[0]["actual"]`。 调用`complete_policy_case`、`business_gaps`、`plan.business.permissions.append`、`PermissionSpec`、`plan.business.roles.append`、`BusinessRole`、`plan.business.role_admin_roles.append`、`next`、`next( item for item in plan.business.permissions if item.role == …`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_audit_derives_only_information_subset_history_not_other_permissions`（L423–L443）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L441断言`business_gaps(requirement, plan) == []`；L443断言`business_gaps(requirement, plan)`。 调用`case`、`next`、`business_gaps`、`permission.actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_virtual_metrics_permissions_use_explicit_resource_scopes`（L446–L481）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L472遍历`plan.business.permissions`；L473按`permission.role == "service" and permission.entity in {"customers", "requests"}`分支；L475断言`business_gaps(requirement, plan) == []`；L481断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reverse_relation_is_implemented_by_correct_child_foreign_key`（L484–L499）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L497断言`business_gaps(requirement, plan) == []`；L499断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_aggregate_notification_catalog_is_not_a_cartesian_recipient_policy`（L503–L524）：接收`alias`。 控制顺序：L514断言`business_gaps(requirement, plan) == []`；L524断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_event_aliases_preserve_explicit_entity_and_recipient`（L536–L547）：接收`event`、`canonical`。 控制顺序：L541断言`business_gaps(requirement, plan) == []`；L547断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resolved_notification_uses_target_state_not_a_hard_coded_action_name`（L550–L560）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L555遍历`plan.business.notifications`；L556按`notice.entity == "requests" and notice.transition == "resolve"`分支；L558断言`business_gaps(requirement, plan) == []`；L560断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_event_specific_recipient_list_requires_all_on_same_resource`（L563–L575）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L575断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_conflicting_aliases_block_without_crashing_or_changing_facts`（L585–L589）：接收`descriptor`。 控制顺序：L588断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L589断言`diagnostics[0]["code"] == "business_unsupported_shape"`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_handling_history_requirement_keeps_entity_scope_and_independent_action`（L592–L608）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L602遍历`plan.business.permissions`；L603按`"read_history" in permission.actions`分支；L606断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L608断言`history and {item["expected"]["entity"] for item in history} == {"requests"}`。 调用`case`、`permission.actions.remove`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resource_query_capabilities_are_scoped_without_inventing_target_fields`（L614–L621）：接收`capability`、`attribute`。 控制顺序：L618断言`business_gaps(requirement, plan) == []`；L619遍历`plan.entities[0].fields`；L621断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_resource_scope_cannot_crash_history_review`（L625–L630）：接收`entity`。 控制顺序：L630断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_global_metric_scope_cannot_overwrite_explicit_per_metric_scope`（L637–L662）：接收`entity`、`name`、`explicit_scope`。 控制顺序：L661断言`business_gaps(requirement, plan, diagnostics=diagnostics)`；L662断言`any(item["code"] == "business_unsupported_shape" for item in diagnostics)`。 调用`case`、`item.model_dump`、`business_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_keyed_kind_only_fields_do_not_become_business_collections`（L667–L680）：接收`name`、`encoded`。 控制顺序：L675断言`coverage_gaps(requirement, plan) == []`；L676断言`business_gaps(requirement, plan) == []`；L678断言`coverage_gaps(requirement, plan)`；L680断言`coverage_gaps(requirement, plan)`。 调用`case`、`plan.entities[0].fields.append`、`FieldSpec`、`json.dumps`、`coverage_gaps`、`business_gaps`、`plan.entities[0].fields.pop`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `transition_notification_case`（L683–L697）：接收`descriptor`。 调用`case`、`plan.model_dump`、`Plan.model_validate`。 返回路径：L697的`requirement, Plan.model_validate(raw)`。
- `test_generic_state_change_facts_require_every_declared_transition`（L704–L732）：接收`event`、`selector`、`encoded`、`missing`。 控制顺序：L714按`selector != "omitted"`分支；L717按`encoded`分支；L720断言`business_gaps(requirement, plan) == []`；L731断言`business_gaps(requirement, plan)`；L732断言`requirement.model_dump_json() == before`。 调用`transition_notification_case`、`json.dumps`、`requirement.model_dump_json`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_state_change_selector_is_exact_not_all_transitions`（L737–L750）：接收`event`、`selected`。 控制顺序：L746断言`business_gaps(requirement, plan) == []`；L750断言`business_gaps(requirement, plan)`。 调用`transition_notification_case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ordinary_transition_identifiers_are_not_invented_wildcards`（L754–L772）：接收`selected`。 控制顺序：L764遍历`plan.business.notifications`；L765按`item.entity == "requests" and item.transition == "start"`分支；L772断言`business_gaps(requirement, plan) == []`。 调用`transition_notification_case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_state_change_obligation_expands_when_workflow_gains_transition`（L775–L806）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L786断言`business_gaps(requirement, plan) == []`；L792断言`business_gaps(requirement, plan)`；L798断言`business_gaps(requirement, plan)`；L806断言`business_gaps(requirement, plan) == []`。 调用`transition_notification_case`、`business_gaps`、`plan.business.workflows[0].transitions.append`、`TransitionSpec`、`plan.business.notifications.append`、`NotificationSpec`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_requirement_never_relaxes_executable_notification_validator`（L809–L817）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L813断言`business_gaps(requirement, plan) == []`。 调用`transition_notification_case`、`business_gaps`、`plan.model_dump`、`pytest.raises`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_or_unknown_specific_transition_is_not_a_generic_requirement`（L821–L830）：接收`selector`。 控制顺序：L830断言`business_gaps(requirement, plan)`。 调用`transition_notification_case`、`business_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transition_wildcard_does_not_change_non_transition_event_semantics`（L833–L846）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L846断言`business_gaps(requirement, plan)`。 调用`case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unscoped_generic_transition_does_not_invent_notifications_on_every_entity`（L849–L858）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L856断言`business_gaps(requirement, plan) == []`；L858断言`business_gaps(requirement, plan)`。 调用`transition_notification_case`、`business_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_fact_coverage.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L858。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`31760`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_fact_coverage.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "db2a2889d3389949c7510250ee58441adf92f3490510170f09eede9de5fff865"} -->
````python
# tests/test_business_fact_coverage.py
"""Structured business facts use business semantics, never field-name heuristics."""

import json

import pytest

from workbench.business_capabilities import business_gaps
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT

DOMAINS = ("metrics", "relations", "permissions", "notifications", "workflows", "resources")


def case(facts):
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    requirement = Requirement(
        summary="客服", users=["员工"], data_scope="shared", features=[], acceptance=[], facts=facts
    )
    return requirement, plan


@pytest.mark.parametrize("domain", DOMAINS)
@pytest.mark.parametrize("encoding", ["native", "nested", "json_list", "json_item", "json_wrapper"])
def test_business_declarations_keep_semantics_in_all_structural_encodings(domain, encoding):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[0].model_dump()
    value = [descriptor]
    if encoding == "json_list":
        value = json.dumps(value)
    elif encoding == "json_item":
        value = [json.dumps(descriptor)]
    requirement.facts = {domain: value}
    if encoding == "nested":
        requirement.facts = {"confirmed": {"business": requirement.facts}}
    elif encoding == "json_wrapper":
        requirement.facts = {"confirmed": json.dumps(requirement.facts)}
    assert business_gaps(requirement, plan) == []
    getattr(plan.business, domain).pop(0)
    assert business_gaps(requirement, plan), (domain, encoding)
    plan.business = None
    assert business_gaps(requirement, plan), (domain, encoding, "business omitted")


@pytest.mark.parametrize(
    "domain,index,attribute,value",
    [
        ("metrics", 0, "entity", "tasks"),
        ("metrics", 0, "kind", "time_count"),
        ("metrics", 1, "filters", []),
        ("metrics", 2, "end_field", "due_at"),
        ("metrics", 3, "group_by", "priority"),
        ("metrics", 4, "time_field", "updated_at"),
        ("relations", 0, "target_entity", "tasks"),
        ("relations", 0, "field", "assignee_id"),
        ("permissions", 4, "scope", "all"),
        ("permissions", 4, "actions", ["read"]),
        ("notifications", 0, "recipient", "creator"),
        ("notifications", 1, "transition", "start"),
        ("notifications", 2, "due_field", "resolved_at"),
        ("workflows", 0, "initial", "active"),
        ("workflows", 0, "status_field", "priority"),
        ("resources", 1, "assignee_field", None),
        ("resources", 1, "notes", False),
    ],
)
def test_changed_domain_meaning_is_not_satisfied_by_same_name(domain, index, attribute, value):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[index].model_dump()
    requirement.facts = {domain: [descriptor]}
    assert business_gaps(requirement, plan) == []
    setattr(getattr(plan.business, domain)[index], attribute, value)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "scope", [["manager", "service"], {"manager": "all", "service": "assigned"}]
)
@pytest.mark.parametrize("encoding", [False, True])
def test_metric_role_scopes_are_actual_read_metrics_grants(scope, encoding):
    requirement, plan = case(
        {"metrics": [{"name": "total", "role_scope": json.dumps(scope) if encoding else scope}]}
    )
    assert business_gaps(requirement, plan) == []
    permission = next(
        p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
    )
    permission.actions.remove("read_metrics")
    gaps = business_gaps(requirement, plan)
    assert len(gaps) == 1 and "role_scope" in gaps[0]


def test_metric_role_scope_mapping_cannot_widen_row_access():
    requirement, plan = case(
        {"metrics": [{"name": "total", "role_scope": {"service": "assigned"}}]}
    )
    assert business_gaps(requirement, plan) == []
    next(
        p for p in plan.business.permissions if p.role == "service" and p.entity == "requests"
    ).scope = "all"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "scope",
    [
        None,
        True,
        "all",
        [],
        {},
        ["manager", "manager"],
        ["管理人员"],
        {"service": "team"},
        [{"role": "manager", "scope": "all"}],
    ],
)
def test_unknown_explicit_metric_scope_blocks_without_guessing(scope):
    requirement, plan = case({"metrics": [{"name": "total", "role_scope": scope}]})
    gaps = business_gaps(requirement, plan)
    assert len(gaps) == 1 and "形状不支持" in gaps[0] and "metrics.0.role_scope" in gaps[0]


def test_undeclared_role_cannot_receive_metric_access_through_other_roles():
    requirement, plan = case({"metrics": [{"name": "total", "role_scope": ["missing"]}]})
    assert business_gaps(requirement, plan)


def test_metric_keyed_dictionary_and_entity_container_preserve_identity():
    requirement, plan = case(
        {"entities": [{"name": "requests", "metrics": {"total": {"kind": "count"}}}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.metrics[0].entity = "customers"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("name", ["name", "kind", "entity", "filters", "role_scope"])
def test_keyed_metric_names_can_be_descriptor_keywords(name):
    requirement, plan = case({"metrics": {name: {"entity": "requests", "kind": "count"}}})
    plan.business.metrics[0].name = name
    assert business_gaps(requirement, plan) == []
    plan.business.metrics.pop(0)
    assert business_gaps(requirement, plan)


def test_explicit_entity_mapping_does_not_derive_its_scope_from_surviving_plan_entities():
    requirement, plan = case(
        {"entities": {"missing": {"metrics": [{"name": "total", "kind": "count"}]}}}
    )
    assert business_gaps(requirement, plan)


def test_entity_keyed_field_named_metrics_is_not_a_metric_declaration():
    requirement, plan = case({"requests": {"metrics": {"kind": "text", "required": True}}})
    plan.business = None
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize("name", ["title", "category", "required", "name", "searchable"])
def test_business_names_that_are_field_keywords_remain_business_identifiers(name):
    requirement, plan = case({"metrics": [{"name": name, "entity": "requests", "kind": "count"}]})
    plan.business.metrics[0].name = name
    assert business_gaps(requirement, plan) == []
    plan.business.metrics.pop(0)
    assert business_gaps(requirement, plan)


def test_field_containers_and_display_metadata_do_not_invent_business_obligations():
    requirement, plan = case(
        {
            "fields": [{"name": "metrics", "required": True, "metrics": [{"name": "missing"}]}],
            "metrics": [{"label": "title必填搜索", "description": "权限提醒"}],
            "nested": {"metrics": {"display": {"label": "显示文字"}}},
            "template_capabilities": {"metrics": [{"name": "missing"}]},
        }
    )
    plan.business = None
    assert business_gaps(requirement, plan) == []


def test_metric_filters_default_eq_and_preserve_literal_json_looking_values():
    requirement, plan = case(
        {
            "metrics": [
                {
                    "name": "resolved_total",
                    "filters": [{"field": "request_state", "value": "resolved"}],
                }
            ]
        }
    )
    assert business_gaps(requirement, plan) == []
    predicate = plan.business.metrics[1].filters[0]
    predicate.field, predicate.value = "title", '["urgent"]'
    requirement.facts = {
        "metrics": [
            {"name": "resolved_total", "filters": [{"field": "title", "value": '["urgent"]'}]}
        ]
    }
    assert business_gaps(requirement, plan) == []
    predicate.value = "urgent"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "filters", [[{}], [{"label": "filter"}], [{"field": "priority"}], {"request_state": "resolved"}]
)
def test_malformed_explicit_filters_cannot_match_any_existing_predicate(filters):
    requirement, plan = case({"metrics": [{"name": "resolved_total", "filters": filters}]})
    assert business_gaps(requirement, plan)


def test_workflow_transition_roles_and_timestamps_remain_semantic_obligations():
    requirement, plan = case({})
    workflow = plan.business.workflows[0]
    requirement.facts = {"workflows": [workflow.model_dump()]}
    assert business_gaps(requirement, plan) == []
    workflow.transitions[-1].roles = ["manager"]
    assert business_gaps(requirement, plan)


def test_scalar_business_prose_is_not_flattened_into_field_or_business_descriptors():
    requirement, plan = case(
        {"metrics": "title count filter", "permissions": ["manager", "service"]}
    )
    plan.business = None
    assert business_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "domain,index,aliases",
    [
        ("relations", 0, {"entity": "from", "target_entity": "to"}),
        ("relations", 0, {"target_entity": "target"}),
        ("workflows", 0, {"status_field": "field", "initial": "initial_state"}),
        ("metrics", 3, {"kind": "type", "group_by": "group_field"}),
        ("metrics", 4, {"kind": "type", "bucket": "interval"}),
        ("resources", 1, {"entity": "name", "notes": "handling_notes"}),
    ],
)
@pytest.mark.parametrize("encoded", [False, True])
def test_structural_aliases_preserve_exact_domain_meaning(domain, index, aliases, encoded):
    requirement, plan = case({})
    descriptor = getattr(plan.business, domain)[index].model_dump()
    for canonical, alias in aliases.items():
        descriptor[alias] = descriptor.pop(canonical)
    requirement.facts = {domain: [json.dumps(descriptor) if encoded else descriptor]}
    before = requirement.model_dump_json()
    assert business_gaps(requirement, plan) == []
    getattr(plan.business, domain).pop(index)
    assert business_gaps(requirement, plan)
    assert requirement.model_dump_json() == before


@pytest.mark.parametrize("alias", ["set", "sets", "set_fields"])
def test_workflow_state_and_timestamp_aliases_are_checked(alias):
    requirement, plan = case({})
    descriptor = plan.business.workflows[0].model_dump()
    for transition in descriptor["transitions"]:
        transition["from"] = transition.pop("from_states")[0]
        transition["to"] = transition.pop("to_state")
        timestamp = transition.pop("set_timestamp")
        if timestamp:
            transition[alias] = {timestamp: "now"}
    requirement.facts = {"workflows": [descriptor]}
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions[-1].set_timestamp = None
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "predicate", [{"field": "request_state", "value": "resolved"}, {"request_state": "resolved"}]
)
def test_metric_filter_aliases_cannot_lose_the_actual_predicate(predicate):
    requirement, plan = case(
        {"metrics": [{"name": "resolved_total", "type": "count", "filter": predicate}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.metrics[1].filters = []
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "alias,action",
    [
        ("comment", "add_note"),
        ("note", "add_note"),
        ("view_audit", "read_audit"),
        ("view_metrics", "read_metrics"),
        ("view_history", "read_history"),
    ],
)
def test_permission_action_aliases_still_require_real_action(alias, action):
    requirement, plan = case({})
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    )
    descriptor = permission.model_dump()
    descriptor["actions"] = [alias if item == action else item for item in descriptor["actions"]]
    requirement.facts = {"permissions": [descriptor]}
    assert business_gaps(requirement, plan) == []
    permission.actions.remove(action)
    assert business_gaps(requirement, plan)


def test_read_only_allows_independently_approved_metrics_but_never_writes():
    requirement, plan = case(
        {
            "permissions": [
                {
                    "role": "service",
                    "entity": "customers",
                    "scope": "all",
                    "actions": ["read"],
                    "read_only": True,
                }
            ],
            "metrics": [
                {
                    "name": "customer_total",
                    "entity": "customers",
                    "allowed_roles": ["manager", "service"],
                }
            ],
        }
    )
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "customers"
    )
    permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan) == []
    permission.actions.append("update")
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "restriction",
    [
        {"only_actions": ["read"]},
        {"denied_actions": ["read_metrics"]},
        {"forbidden_actions": ["view_metrics"]},
    ],
)
def test_explicit_action_restrictions_override_other_positive_grants(restriction):
    requirement, plan = case(
        {
            "permissions": [
                {
                    "role": "service",
                    "entity": "customers",
                    "scope": "all",
                    "actions": ["read"],
                    **restriction,
                }
            ],
            "metrics": [
                {"name": "customer_total", "entity": "customers", "role_scope": ["service"]}
            ],
        }
    )
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "customers"
    )
    permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan)


def complete_policy_case():
    requirement, plan = case({})
    requirement.facts = {
        "business": {
            "roles": [item.model_dump() for item in plan.business.roles],
            "resources": [item.model_dump() for item in plan.business.resources],
            "permissions": [item.model_dump() for item in plan.business.permissions],
            "bootstrap_role": "manager",
            "role_admin_roles": ["manager"],
        }
    }
    return requirement, plan


@pytest.mark.parametrize(
    "mutation", ["extra_row", "extra_role", "admin_role", "scope", "extra_write"]
)
def test_complete_policy_rejects_new_rows_roles_admins_and_privilege_expansion(mutation):
    from workbench.business_contracts import BusinessRole, PermissionSpec

    requirement, plan = complete_policy_case()
    assert business_gaps(requirement, plan) == []
    if mutation == "extra_row":
        plan.business.permissions.append(
            PermissionSpec(role="employee", entity="tasks", actions=["read"], scope="all")
        )
    elif mutation == "extra_role":
        plan.business.roles.append(BusinessRole(name="intruder", label="其他角色"))
    elif mutation == "admin_role":
        plan.business.role_admin_roles.append("service")
    elif mutation == "scope":
        next(
            item
            for item in plan.business.permissions
            if item.role == "service" and item.entity == "requests"
        ).scope = "all"
    else:
        next(
            item
            for item in plan.business.permissions
            if item.role == "employee" and item.entity == "customers"
        ).actions.append("update")
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics and diagnostics[0]["expected"] != diagnostics[0]["actual"]


def test_audit_derives_only_information_subset_history_not_other_permissions():
    requirement, plan = case({})
    permission = next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    )
    permission.actions = ["read", "read_audit", "read_history"]
    requirement.facts = {
        "permissions": [
            {
                "role": "service",
                "entity": "requests",
                "actions": ["read", "view_audit"],
                "scope": "assigned",
            }
        ]
    }
    assert business_gaps(requirement, plan) == []
    permission.actions.append("assign")
    assert business_gaps(requirement, plan)


def test_virtual_metrics_permissions_use_explicit_resource_scopes():
    requirement, plan = case(
        {
            "business": {
                "permissions": [
                    {"role": "service", "entity": "customers", "actions": ["read"], "scope": "all"},
                    {
                        "role": "service",
                        "entity": "requests",
                        "actions": ["read"],
                        "scope": "assigned",
                    },
                    {
                        "role": "service",
                        "entity": "metrics",
                        "actions": ["read"],
                        "scope": "assigned",
                    },
                ],
                "metrics": [
                    {"name": "customer_total", "entity": "customers"},
                    {"name": "total", "entity": "requests"},
                ],
            }
        }
    )
    for permission in plan.business.permissions:
        if permission.role == "service" and permission.entity in {"customers", "requests"}:
            permission.actions = ["read", "read_metrics"]
    assert business_gaps(requirement, plan) == []
    next(
        item
        for item in plan.business.permissions
        if item.role == "service" and item.entity == "requests"
    ).scope = "all"
    assert business_gaps(requirement, plan)


def test_reverse_relation_is_implemented_by_correct_child_foreign_key():
    requirement, plan = case(
        {
            "relations": [
                {
                    "entity": "customers",
                    "field": "requests",
                    "target": "requests",
                    "kind": "reverse",
                }
            ]
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.relations[0].target_entity = "tasks"
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("alias", ["in-app", "in_app_persistent", "in_app"])
def test_aggregate_notification_catalog_is_not_a_cartesian_recipient_policy(alias):
    requirement, plan = case(
        {
            "notifications": {
                "channel": alias,
                "persistent": True,
                "triggers": ["assignment", "handling_note", "state_change", "resolved", "overdue"],
                "recipients": ["assignee", "request_submitter"],
            }
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (
            item.event == "transitioned"
            and item.transition == "resolve"
            and item.recipient == "creator"
        )
    ]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "event,canonical",
    [
        ("assignment", "assigned"),
        ("comment_added", "note_added"),
        ("handling_note", "note_added"),
        ("overdue", "due"),
    ],
)
def test_event_aliases_preserve_explicit_entity_and_recipient(event, canonical):
    recipient = "created_by" if canonical == "note_added" else "assignee_id"
    requirement, plan = case(
        {"notifications": [{"entity": "requests", "event": event, "recipients": [recipient]}]}
    )
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (item.entity == "requests" and item.event == canonical)
    ]
    assert business_gaps(requirement, plan)


def test_resolved_notification_uses_target_state_not_a_hard_coded_action_name():
    requirement, plan = case(
        {"reminders": [{"entity": "requests", "event": "resolved", "recipient": "creator"}]}
    )
    plan.business.workflows[0].transitions[-1].name = "finish"
    for notice in plan.business.notifications:
        if notice.entity == "requests" and notice.transition == "resolve":
            notice.transition = "finish"
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions[-1].to_state = "closed"
    assert business_gaps(requirement, plan)


def test_event_specific_recipient_list_requires_all_on_same_resource():
    requirement, plan = case(
        {
            "notifications": [
                {
                    "entity": "requests",
                    "event": "note_added",
                    "recipients": ["created_by", "assignee_id"],
                }
            ]
        }
    )
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "descriptor",
    [
        {"name": "total", "type": "count", "kind": "time_count"},
        {"name": "total", "allowed_roles": ["manager"], "role_scope": ["service"]},
    ],
)
def test_conflicting_aliases_block_without_crashing_or_changing_facts(descriptor):
    requirement, plan = case({"metrics": [descriptor]})
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "business_unsupported_shape"


def test_handling_history_requirement_keeps_entity_scope_and_independent_action():
    requirement, plan = case(
        {
            "resources": [
                {"entity": "requests", "label": "服务请求"},
                {"entity": "tasks", "label": "协作任务"},
            ]
        }
    )
    requirement.features = ["服务请求：查看处理过程"]
    for permission in plan.business.permissions:
        if "read_history" in permission.actions:
            permission.actions.remove("read_history")
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    history = [item for item in diagnostics if item["code"] == "business_missing_history_grant"]
    assert history and {item["expected"]["entity"] for item in history} == {"requests"}


@pytest.mark.parametrize(
    "capability,attribute", [("keyword_search", "searchable"), ("exact_filter", "filterable")]
)
def test_resource_query_capabilities_are_scoped_without_inventing_target_fields(
    capability, attribute
):
    requirement, plan = case({"resources": [{"name": "customers", "capabilities": [capability]}]})
    assert business_gaps(requirement, plan) == []
    for field in plan.entities[0].fields:
        setattr(field, attribute, False)
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("entity", [None, [], {}, True])
def test_malformed_resource_scope_cannot_crash_history_review(entity):
    requirement, plan = case(
        {"resources": [{"entity": entity, "label": "服务请求", "notes": True}]}
    )
    requirement.features = ["查看处理过程"]
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize(
    "entity,name,explicit_scope",
    [("customers", "customer_total", "own"), ("requests", "total", "all")],
)
def test_global_metric_scope_cannot_overwrite_explicit_per_metric_scope(
    entity, name, explicit_scope
):
    requirement, plan = case({})
    permissions = [
        item.model_dump()
        for item in plan.business.permissions
        if item.entity == entity and item.role in {"manager", "service"}
    ]
    requirement.facts = {
        "business": {
            "permissions": permissions,
            "metrics_roles": ["manager", "service"],
            "metrics_scope": "manager=all；service=assigned（只按本人可见行计算）",
            "metrics": [
                {
                    "name": name,
                    "entity": entity,
                    "role_scope": {"manager": "all", "service": explicit_scope},
                }
            ],
        }
    }
    diagnostics = []
    assert business_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["code"] == "business_unsupported_shape" for item in diagnostics)


@pytest.mark.parametrize("name", DOMAINS)
@pytest.mark.parametrize("encoded", [False, True])
def test_entity_keyed_kind_only_fields_do_not_become_business_collections(name, encoded):
    from workbench.domain import FieldSpec
    from workbench.requirement_coverage import coverage_gaps

    requirement, plan = case({})
    plan.entities[0].fields.append(FieldSpec(name=name, kind="text"))
    definition = {name: {"kind": "text"}}
    requirement.facts = {"customers": json.dumps(definition) if encoded else definition}
    assert coverage_gaps(requirement, plan) == []
    assert business_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].kind = "integer"
    assert coverage_gaps(requirement, plan), "The field kind obligation must stay binding"
    plan.entities[0].fields.pop()
    assert coverage_gaps(requirement, plan), "A missing explicit field must still block"


def transition_notification_case(descriptor):
    requirement, plan = case({"notifications": [descriptor]})
    raw = plan.model_dump()
    raw["business"]["notifications"] = [
        {
            "entity": workflow.entity,
            "event": "transitioned",
            "recipient": recipient,
            "transition": transition.name,
        }
        for workflow in plan.business.workflows
        for transition in workflow.transitions
        for recipient in ("assignee", "creator")
    ]
    return requirement, Plan.model_validate(raw)


@pytest.mark.parametrize("event", ["transitioned", "state_change", "state_changed"])
@pytest.mark.parametrize("selector", ["omitted", None, "*"])
@pytest.mark.parametrize("encoded", [False, True])
@pytest.mark.parametrize("missing", ["start", "resolve"])
def test_generic_state_change_facts_require_every_declared_transition(
    event, selector, encoded, missing
):
    descriptor = {
        "entity": "requests",
        "event": event,
        "recipient": "assignee",
        "due_field": None,
        "channel": "in_app",
    }
    if selector != "omitted":
        descriptor["transition"] = selector
    requirement, plan = transition_notification_case(descriptor)
    if encoded:
        requirement.facts = {"notifications": json.dumps([descriptor])}
    before = requirement.model_dump_json()
    assert business_gaps(requirement, plan) == []
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (
            item.entity == "requests"
            and item.recipient == "assignee"
            and item.transition == missing
        )
    ]
    # The same transition remains on the wrong entity and wrong recipient.
    assert business_gaps(requirement, plan)
    assert requirement.model_dump_json() == before


@pytest.mark.parametrize("event", ["transitioned", "state_change", "state_changed"])
@pytest.mark.parametrize("selected", ["start", "resolve"])
def test_explicit_state_change_selector_is_exact_not_all_transitions(event, selected):
    requirement, plan = transition_notification_case(
        {"entity": "requests", "event": event, "recipient": "assignee", "transition": selected}
    )
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if item.entity != "requests" or item.recipient != "assignee" or item.transition == selected
    ]
    assert business_gaps(requirement, plan) == []
    requirement.facts["notifications"][0]["transition"] = (
        "resolve" if selected == "start" else "start"
    )
    assert business_gaps(requirement, plan)


@pytest.mark.parametrize("selected", ["all", "any"])
def test_ordinary_transition_identifiers_are_not_invented_wildcards(selected):
    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipient": "assignee",
            "transition": selected,
        }
    )
    plan.business.workflows[0].transitions[0].name = selected
    for item in plan.business.notifications:
        if item.entity == "requests" and item.transition == "start":
            item.transition = selected
    plan.business.notifications = [
        item
        for item in plan.business.notifications
        if not (item.entity == "requests" and item.transition == "resolve")
    ]
    assert business_gaps(requirement, plan) == []


def test_generic_state_change_obligation_expands_when_workflow_gains_transition():
    from workbench.business_contracts import NotificationSpec, TransitionSpec

    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipients": ["assignee", "creator"],
            "transition": None,
        }
    )
    assert business_gaps(requirement, plan) == []
    plan.business.workflows[0].transitions.append(
        TransitionSpec(
            name="reopen", from_states=["resolved"], to_state="active", roles=["manager"]
        )
    )
    assert business_gaps(requirement, plan)
    plan.business.notifications.append(
        NotificationSpec(
            entity="requests", event="transitioned", recipient="assignee", transition="reopen"
        )
    )
    assert business_gaps(requirement, plan), (
        "Every explicitly named recipient needs the new transition"
    )
    plan.business.notifications.append(
        NotificationSpec(
            entity="requests", event="transitioned", recipient="creator", transition="reopen"
        )
    )
    assert business_gaps(requirement, plan) == []


def test_generic_requirement_never_relaxes_executable_notification_validator():
    requirement, plan = transition_notification_case(
        {"entity": "requests", "event": "transitioned", "recipient": "assignee", "transition": None}
    )
    assert business_gaps(requirement, plan) == []
    raw = plan.model_dump()
    raw["business"]["notifications"][0]["transition"] = None
    with pytest.raises(ValueError, match="Notification requires a known transition"):
        Plan.model_validate(raw)


@pytest.mark.parametrize("selector", ["missing", "", [], {}, False])
def test_invalid_or_unknown_specific_transition_is_not_a_generic_requirement(selector):
    requirement, plan = transition_notification_case(
        {
            "entity": "requests",
            "event": "transitioned",
            "recipient": "assignee",
            "transition": selector,
        }
    )
    assert business_gaps(requirement, plan)


def test_transition_wildcard_does_not_change_non_transition_event_semantics():
    requirement, plan = case(
        {
            "notifications": [
                {
                    "entity": "requests",
                    "event": "assigned",
                    "recipient": "assignee",
                    "transition": "*",
                }
            ]
        }
    )
    assert business_gaps(requirement, plan)


def test_unscoped_generic_transition_does_not_invent_notifications_on_every_entity():
    requirement, plan = transition_notification_case(
        {"event": "transitioned", "recipient": "assignee", "transition": None}
    )
    plan.business.notifications = [
        item for item in plan.business.notifications if item.entity == "requests"
    ]
    assert business_gaps(requirement, plan) == []
    requirement.facts["notifications"][0]["entity"] = "tasks"
    assert business_gaps(requirement, plan)
````
