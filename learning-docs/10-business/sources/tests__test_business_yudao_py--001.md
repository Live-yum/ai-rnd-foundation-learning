# tests/test_business_yudao.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_yudao`、`workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `approved_plan`（L20–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`、`business_plan`。 返回路径：L24的`Plan.model_validate(business_plan())`。
- `test_native_registration_setting_maps_the_pinned_configuration_key`（L27–L42）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：BeanUtils cannot map the native configKey property to request key.。 控制顺序：L37断言`"private String configKey;" in stored`；L38断言`"private String key;" in request`；L41断言`mapping in service`；L42断言`service.index(mapping) < service.index("nativeConfiguration.updateConfig(request)")`。 调用`zipfile.ZipFile`、`archive.read(base + "/dal/dataobject/config/ConfigDO.java").decod…`、`archive.read`、`archive.read(base + "/controller/admin/config/vo/ConfigSaveReqVO.…`、`(TEMPLATES / "RndBusinessService.java").read_text`、`service.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `generated_native_source`（L45–L90）：接收`tmp_path`、`plan`。 控制顺序：L48遍历`enumerate(plan.entities)`。 调用`enumerate`、`entity.name.replace`、`"".join`、`part.title`、`entity.name.split`、`atomic_text`、`targets.append`。 返回路径：L90的`backend, frontend, targets, reports`。
- `test_mount_retains_real_mappers_and_binds_every_original_crud_route`（L93–L134）：接收`tmp_path`。 控制顺序：L99断言`receipt["runtime_verified"] is False`；L100断言`mapper.read_bytes() == original_mapper`；L101断言`receipt["bootstrap_endpoint"].endswith("/bootstrap")`；L102断言`len(receipt["extension_tables"]) == 3`；L107遍历`("create", "update", "archive", "archiveBatch", "get", "page")`；L108断言`"business." + function + "(" in controller`；L109断言`"export-excel" not in controller`；L116断言`config["business"] == plan.business.model_dump()`。后续分支沿下方源码相同行号继续阅读。 调用`approved_plan`、`generated_native_source`、`mapper.read_bytes`、`install_yudao_business`、`receipt["bootstrap_endpoint"].endswith`、`len`、`( backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/wbcusto…`、`json.loads`、`( backend / "yudao-module-infra/yudao-module-infra-server/src/mai…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_vben_form_field_type_covers_the_exact_emitted_metadata`（L137–L152）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L145断言`fields == set(FieldSpec.model_fields)`；L146断言`"businessPayload<T extends object>" in source`；L147断言`"Reflect.deleteProperty(result, name)" in source`；L148断言`"as unknown" not in source and "as any" not in source`；L150断言`"row: Record<string, unknown>" in panel`；L151断言`"typeof record.id !== 'string'" in panel`；L152断言`"row.actions.includes('read_history')" in panel`。 调用`(TEMPLATES / "business-form.ts").read_text`、`re.search(r"interface Field \{([^}]+)\}", source).group`、`re.search`、`set`、`re.findall`、`(TEMPLATES / "panel.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reentry_is_hash_bound_and_tampering_never_overwrites`（L155–L164）：接收`tmp_path`。 控制顺序：L159断言`install_yudao_business(plan, *args) == first`；L164断言`source.read_text(encoding="utf-8") == "// user's inspection changes\n"`。 调用`approved_plan`、`generated_native_source`、`install_yudao_business`、`source.write_text`、`pytest.raises`、`source.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_native_mapper_fails_before_any_controller_is_changed`（L167–L179）：接收`tmp_path`。 控制顺序：L178断言`controller.read_bytes() == original`；L179断言`not (reports / "business-yudao.json").exists()`。 调用`approved_plan`、`generated_native_source`、`controller.read_bytes`、`(backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/mysql/wbcustomers/WbC…`、`pytest.raises`、`install_yudao_business`、`(reports / "business-yudao.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_approved_business_plan_and_exact_targets_required`（L182–L191）：接收`tmp_path`。 调用`approved_plan`、`generated_native_source`、`deepcopy`、`bad_targets.pop`、`pytest.raises`、`install_yudao_business`、`plan.model_copy`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_is_append_only_and_never_seeds_implicit_user_ids`（L194–L205）：接收`tmp_path`。 控制顺序：L198断言`"BEFORE UPDATE OR DELETE" in schema`；L199断言`"ON CONFLICT" not in schema and "IF NOT EXISTS" not in schema`；L200断言`"DROP " not in schema and "TRUNCATE" not in schema`；L201断言`"rnd_archived_at" in schema`；L203断言`"INSERT INTO system_user_role" not in seed`；L204断言`"WHERE u.id=1" not in seed`；L205断言`"POST /admin-api/infra/rnd-business/bootstrap" in seed`。 调用`approved_plan`、`generated_native_source`、`business_schema`、`business_role_seed`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_untrusted_table_identifier_cannot_enter_schema`（L208–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`business_schema`、`approved_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_java_templates_have_valid_syntax`（L213–L228）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L218遍历`TEMPLATES.glob("*.java")`；L228断言`not tree.root_node.has_error`。 调用`Parser`、`Language`、`tree_sitter_java.language`、`TEMPLATES.glob`、`path.read_text(encoding="utf-8") .replace("__PREFIX__", "rndb_tes…`、`path.read_text(encoding="utf-8") .replace`、`path.read_text`、`parser.parse`、`text.encode`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_contains_explicit_native_boundary_guards`（L254–L255）：接收`fragment`。 控制顺序：L255断言`fragment in (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")`。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_registration_keeps_real_service_and_single_transaction`（L258–L263）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L260断言`"AdminUserService.registerUser" in source`；L261断言`"TransactionTemplate" in source and "call.proceed()" in source`；L262断言`"business.registered" in source`；L263断言`"password" not in source.lower().replace("password hashing", "")`。 调用`(TEMPLATES / "RndBusinessRegistration.java").read_text`、`source.lower().replace`、`source.lower`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_role_mapper_cannot_grant_unrelated_global_roles`（L266–L274）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L268断言`'roleCode(String.valueOf(data.get("role")))' in source`；L269断言`"Role not declared by this product" in source`；L270断言`"sidecar.revoke" in source and "oldAdmin&&!newAdmin" in source`；L272断言`"pg_advisory_xact_lock" in mapper`；L273断言`"r.tenant_id=u.tenant_id" in mapper`；L274断言`"WHERE tenant_id=#{tenant} AND recipient_id=#{user}" in mapper`。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`(TEMPLATES / "RndBusinessMapper.java").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_retains_native_components_and_contract_driven_controls`（L277–L286）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L279断言`"useVbenForm" in source and "useVbenModal" in source`；L280断言`"TimelineItem" in source and "'ant-design-vue'" in source`；L281断言`"metrics" in source and "notifications" in source and "roleAdmin" in source`；L282断言`"requestClient" in source and "localStorage" not in source`；L283断言`"useEcharts" in (TEMPLATES / "metric-chart.vue").read_text(encoding="utf-8")`；L285断言`"spec.controlled.map(wire)" in fields`；L286断言`"valueField: 'id'" in fields and "ApiSelect" in fields`。 调用`(TEMPLATES / "panel.vue").read_text`、`(TEMPLATES / "metric-chart.vue").read_text`、`(TEMPLATES / "business-form.ts").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_target_cannot_redirect_schema_or_native_permission`（L302–L314）：接收`tmp_path`、`key`、`value`。 控制顺序：L313断言`controller.read_bytes() == original`；L314断言`not reports.exists()`。 调用`approved_plan`、`generated_native_source`、`controller.read_bytes`、`pytest.raises`、`install_yudao_business`、`reports.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_targets_from_different_native_runs_are_rejected`（L317–L322）：接收`tmp_path`。 调用`approved_plan`、`generated_native_source`、`targets[1]["table"].replace`、`pytest.raises`、`install_yudao_business`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_duplicate_target_cannot_install_extra_tables`（L325–L330）：接收`tmp_path`。 调用`approved_plan`、`generated_native_source`、`targets.append`、`deepcopy`、`pytest.raises`、`install_yudao_business`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_action_modal_opens_before_waiting_for_lazy_form_mount`（L333–L338）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L338断言`body.index("actionModalApi.open()") < body.index("await actionFormApi.resetForm()")`。 调用`(TEMPLATES / "panel.vue").read_text`、`source.index`、`body.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_controller_uses_native_admin_package_prefix`（L341–L355）：接收`tmp_path`。 控制顺序：L350断言`"package cn.iocoder.yudao.module.infra.controller.admin.rndbusiness;" in text`；L351断言`'@RequestMapping("/infra/rnd-business")' in text`；L352断言`"import cn.iocoder.yudao.module.infra.business.RndBusinessService;" in text`；L353断言`not ( backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/business/RndBusinessController.java" ).e…`。 调用`approved_plan`、`generated_native_source`、`install_yudao_business`、`controller.read_text`、`( backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/business/RndBusinessCont…`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_related_history_checks_parent_and_each_child_scope`（L358–L368）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L361断言`'require(name,parent,"read")' in body`；L362断言`'if(!hasAction(child,"read")) continue' in body`；L363断言`".eq(field,id(parent))" in body`；L364断言`'if(!allowed(child,row,"read")) continue' in body`；L365断言`'allowed(child,row,"read_history")' in body`；L366断言`"candidates.size()>10000" in body`；L367断言`"rnd_archived_at" not in body`；L368断言`"target_entity" in body`。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`source.split("public Object related(", 1)[1].split`、`source.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_related_history_uses_native_route_and_visible_timeline`（L371–L381）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L374断言`'@GetMapping("/related")' in controller`；L375断言`"business.related(entity,id)" in controller`；L376断言`"business-related-${group.entity}" in panel`；L377断言`"related-history-${group.entity}-${record.record.id}" in panel`；L378断言`"record.actions.includes('read_history')" in panel`；L379断言`"business-related-history" in panel`；L380断言`"request !== relatedRequest \|\| current !== generation" in panel`；L381断言`'<TimelineItem v-for="entry in relatedEvents"' in panel`。 调用`(TEMPLATES / "RndBusinessController.java").read_text`、`(TEMPLATES / "panel.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_display_metadata_does_not_change_wire_audit_or_metric_serialization`（L384–L397）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L389断言`"_display" not in raw and "userLabel" not in raw and "referenceLabel" not in raw`；L391断言`"encode(out(name,row))" in event and "present(" not in event`；L395断言`'item.put("buckets",counts)' in metrics`；L396断言`'item.put("bucketLabels",labels)' in metrics`；L397断言`"present(" not in metrics`。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`source.split("private Map<String,Object> out(", 1)[1].split`、`source.split`、`source.split("private long event(", 1)[1].split`、`source.split("public Object metrics()", 1)[1].split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reference_and_user_names_are_scoped_cached_and_non_recursive`（L400–L429）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L405断言`"display.references.computeIfAbsent" in relation`；L406断言`'allowed(target,linked,"read")' in relation`；L407断言`relation.index('allowed(target,linked,"read")') < relation.index( "recordLabel(target…`；L410断言`"present(" not in relation`；L414断言`"display.users.computeIfAbsent" in user`；L415断言`"rolesFor(number(key)).isEmpty()" in user`；L416断言`"sidecar.displayUser(tenant(),number(key))" in user`；L417断言`"sidecar.users(" not in user`。后续分支沿下方源码相同行号继续阅读。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`source.split("private String referenceLabel(", 1)[1].split`、`source.split`、`relation.index`、`source.split("private String userLabel(", 1)[1].split`、`(TEMPLATES / "RndBusinessMapper.java").read_text`、`source.split("public Object history(", 1)[1].split`、`history.index`、`source.split("public Object page(", 1)[1].split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_display_helpers_are_generic_labels_and_keep_native_grid_structure`（L432–L458）：接收`tmp_path`。 控制顺序：L438断言`"function nativeBusinessGridColumns(): VxeTableGridOptions<NativeData>['columns']" in…`；L441断言`"businessGridColumns('customers', nativeBusinessGridColumns())" in data`；L442断言`"businessSearchSchema('customers', nativeBusinessSearchSchema())" in data`；L444断言`"field.label \|\| field.name" in source`；L445断言`"field.choice_labels[value] \|\| value" in source`；L446断言`"showHeaderOverflow: true" in source and "minWidth:" in source`；L447断言`"date.toISOString().slice(0, 19)" in source`；L448断言`"Reflect.get(row, '_display')" in source`。后续分支沿下方源码相同行号继续阅读。 调用`approved_plan`、`generated_native_source`、`install_yudao_business`、`(root / "wbcustomers/data.ts").read_text`、`(root / "rnd-business/business-form.ts").read_text`、`(root / "rnd-business/panel.vue").read_text`、`(root / "wbcustomers/index.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_grid_contract_change_fails_before_writing`（L461–L477）：接收`tmp_path`。 控制顺序：L476断言`controller.read_bytes() == before`；L477断言`not reports.exists()`。 调用`approved_plan`、`generated_native_source`、`data.write_text`、`data.read_text(encoding="utf-8").replace`、`data.read_text`、`controller.read_bytes`、`pytest.raises`、`install_yudao_business`、`reports.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_notification_display_preserves_raw_message_and_stable_read_controls`（L480–L491）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L483断言`'n.put("display_message"' in notices`；L484断言`'n.put("message"' not in notices`；L485断言`notices.index('allowed(n.get("entity").toString(),row,"read")') < notices.index( 'n.p…`；L489断言`"business-notice-read-${record.id}" in panel`；L490断言`"business-notice-read-state-${record.id}" in panel`；L491断言`"record.display_message \|\| record.message" in panel`。 调用`(TEMPLATES / "RndBusinessService.java").read_text`、`service.split`、`notices.index`、`(TEMPLATES / "panel.vue").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_yudao.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L491。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22470`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_yudao.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "afb3183abcf1a9516e5d76cdb367012c075f9047bdb3d11bd6bc189d722460e4"} -->
````python
# tests/test_business_yudao.py
"""Native adapter source/safety contracts. These do not claim a Maven/browser runtime pass."""

import json
from copy import deepcopy

import pytest

from workbench.business_yudao import (
    JAVA_PACKAGE,
    JAVA_ROOT,
    TEMPLATES,
    business_role_seed,
    business_schema,
    install_yudao_business,
)
from workbench.domain import Plan
from workbench.filesystem import atomic_text


def approved_plan():
    # Import the shared generic typed contract example, never a production fallback response.
    from test_business_contracts import business_plan

    return Plan.model_validate(business_plan())


def test_native_registration_setting_maps_the_pinned_configuration_key():
    """BeanUtils cannot map the native configKey property to request key."""
    import zipfile

    from workbench.settings import ROOT

    base = JAVA_ROOT + "/" + JAVA_PACKAGE
    with zipfile.ZipFile(ROOT / "templates/vendor/yudao-backend.zip") as archive:
        stored = archive.read(base + "/dal/dataobject/config/ConfigDO.java").decode()
        request = archive.read(base + "/controller/admin/config/vo/ConfigSaveReqVO.java").decode()
    assert "private String configKey;" in stored
    assert "private String key;" in request
    service = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    mapping = "request.setKey(previous.getConfigKey());"
    assert mapping in service
    assert service.index(mapping) < service.index("nativeConfiguration.updateConfig(request)")


def generated_native_source(tmp_path, plan):
    backend, frontend, reports = (tmp_path / name for name in ("backend", "frontend", "reports"))
    targets = []
    for index, entity in enumerate(plan.entities):
        slug = "wb" + entity.name.replace("_", "")
        name = "Wb" + "".join(part.title() for part in entity.name.split("_"))
        controller = f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/{slug}/{name}Controller.java"
        atomic_text(
            backend / controller,
            f'@RequestMapping("/infra/wb-{entity.name.replace("_", "-")}")\npublic class {name}Controller {{}}\n',
        )
        atomic_text(
            backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/dataobject/{slug}/{name}DO.java",
            f"public class {name}DO {{}}\n",
        )
        atomic_text(
            backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/mysql/{slug}/{name}Mapper.java",
            f"public interface {name}Mapper {{}}\n",
        )
        atomic_text(
            frontend / f"apps/web-antd/src/views/infra/{slug}/index.vue",
            """<script lang="ts" setup>
import { Page } from '@vben/common-ui';
function handleRefresh() {}
</script>
<template><Page><Grid><template #actions="{ row }"><TableAction :actions="[]" /></template></Grid></Page></template>
""",
        )
        atomic_text(
            frontend / f"apps/web-antd/src/views/infra/{slug}/data.ts",
            "export function useFormSchema(): VbenFormSchema[] { return []; }\n"
            "export function useGridFormSchema(): VbenFormSchema[] { return []; }\n"
            "export function useGridColumns(): VxeTableGridOptions<NativeData>['columns'] { return []; }\n",
        )
        atomic_text(
            frontend / f"apps/web-antd/src/views/infra/{slug}/modules/form.vue",
            '<script lang="ts" setup>\nconst data = (await formApi.getValues()) as NativeData;\n</script>\n<template><Modal><Form /></Modal></template>\n',
        )
        targets.append(
            {
                "entity": entity.name,
                "table": f"wb_12345678_{entity.name}",
                "permission": "infra:wb-" + entity.name.replace("_", "-"),
            }
        )
    return backend, frontend, targets, reports


def test_mount_retains_real_mappers_and_binds_every_original_crud_route(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    mapper = backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/mysql/wbcustomers/WbCustomersMapper.java"
    original_mapper = mapper.read_bytes()
    receipt = install_yudao_business(plan, backend, frontend, targets, reports)
    assert receipt["runtime_verified"] is False
    assert mapper.read_bytes() == original_mapper
    assert receipt["bootstrap_endpoint"].endswith("/bootstrap")
    assert len(receipt["extension_tables"]) == 3
    controller = (
        backend
        / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/wbcustomers/WbCustomersController.java"
    ).read_text(encoding="utf-8")
    for function in ("create", "update", "archive", "archiveBatch", "get", "page"):
        assert "business." + function + "(" in controller
    assert "export-excel" not in controller
    config = json.loads(
        (
            backend
            / "yudao-module-infra/yudao-module-infra-server/src/main/resources/rnd-business-contract.json"
        ).read_text(encoding="utf-8")
    )
    assert config["business"] == plan.business.model_dump()
    assert config["specDigest"] == receipt["spec_digest"]
    assert all(binding["requestVO"].endswith("SaveReqVO") for binding in config["bindings"])
    assert all(binding["permission"].startswith("infra:wb-") for binding in config["bindings"])
    panel = (frontend / "apps/web-antd/src/views/infra/wbcustomers/index.vue").read_text(
        encoding="utf-8"
    )
    assert '<Page data-rnd-business-entity="customers">' in panel
    assert "<Grid " in panel and "<TableAction" in panel
    assert "<RndBusinessPanel" in panel
    data = (frontend / "apps/web-antd/src/views/infra/wbcustomers/data.ts").read_text(
        encoding="utf-8"
    )
    assert "nativeBusinessFormSchema" in data and "businessFormSchema" in data
    form = (frontend / "apps/web-antd/src/views/infra/wbcustomers/modules/form.vue").read_text(
        encoding="utf-8"
    )
    assert "businessPayload('customers', (await formApi.getValues()) as NativeData)" in form
    assert "as unknown" not in form


def test_vben_form_field_type_covers_the_exact_emitted_metadata():
    import re

    from workbench.domain import FieldSpec

    source = (TEMPLATES / "business-form.ts").read_text(encoding="utf-8")
    declaration = re.search(r"interface Field \{([^}]+)\}", source).group(1)
    fields = set(re.findall(r"(\w+)\s*:", declaration))
    assert fields == set(FieldSpec.model_fields)
    assert "businessPayload<T extends object>" in source
    assert "Reflect.deleteProperty(result, name)" in source
    assert "as unknown" not in source and "as any" not in source
    panel = (TEMPLATES / "panel.vue").read_text(encoding="utf-8")
    assert "row: Record<string, unknown>" in panel
    assert "typeof record.id !== 'string'" in panel
    assert "row.actions.includes('read_history')" in panel


def test_reentry_is_hash_bound_and_tampering_never_overwrites(tmp_path):
    plan = approved_plan()
    args = generated_native_source(tmp_path, plan)
    first = install_yudao_business(plan, *args)
    assert install_yudao_business(plan, *args) == first
    source = args[0] / first["files"][0]["path"]
    source.write_text("// user's inspection changes\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source changed"):
        install_yudao_business(plan, *args)
    assert source.read_text(encoding="utf-8") == "// user's inspection changes\n"


def test_missing_native_mapper_fails_before_any_controller_is_changed(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    controller = (
        backend
        / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/wbcustomers/WbCustomersController.java"
    )
    original = controller.read_bytes()
    (backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/mysql/wbcustomers/WbCustomersMapper.java").unlink()
    with pytest.raises(ValueError, match="Actual Infra-generated mapper"):
        install_yudao_business(plan, backend, frontend, targets, reports)
    assert controller.read_bytes() == original
    assert not (reports / "business-yudao.json").exists()


def test_approved_business_plan_and_exact_targets_required(tmp_path):
    plan = approved_plan()
    args = generated_native_source(tmp_path, plan)
    bad_targets = deepcopy(args[2])
    bad_targets.pop()
    with pytest.raises(ValueError, match="targets differ"):
        install_yudao_business(plan, args[0], args[1], bad_targets, args[3])
    plain = plan.model_copy(update={"business": None})
    with pytest.raises(ValueError, match="approved business contract"):
        install_yudao_business(plain, *args)


def test_schema_is_append_only_and_never_seeds_implicit_user_ids(tmp_path):
    plan = approved_plan()
    _, _, targets, _ = generated_native_source(tmp_path, plan)
    schema = business_schema(plan, targets, "rndb_aabbcc")
    assert "BEFORE UPDATE OR DELETE" in schema
    assert "ON CONFLICT" not in schema and "IF NOT EXISTS" not in schema
    assert "DROP " not in schema and "TRUNCATE" not in schema
    assert "rnd_archived_at" in schema
    seed = business_role_seed(plan, targets, "rndb_aabbcc")
    assert "INSERT INTO system_user_role" not in seed
    assert "WHERE u.id=1" not in seed
    assert "POST /admin-api/infra/rnd-business/bootstrap" in seed


def test_untrusted_table_identifier_cannot_enter_schema():
    with pytest.raises(ValueError, match="SQL identifier"):
        business_schema(approved_plan(), [{"table": "x; DROP TABLE system_users"}], "rndb_safe")


def test_java_templates_have_valid_syntax():
    import tree_sitter_java
    from tree_sitter import Language, Parser

    parser = Parser(Language(tree_sitter_java.language()))
    for path in TEMPLATES.glob("*.java"):
        text = (
            path.read_text(encoding="utf-8")
            .replace("__PREFIX__", "rndb_test")
            .replace("__SLUG__", "wbtest")
            .replace("__CLASS__", "WbTest")
            .replace("__ENTITY__", "test")
            .replace("__KEBAB__", "wb-test")
        )
        tree = parser.parse(text.encode())
        assert not tree.root_node.has_error, path.name


@pytest.mark.parametrize(
    "fragment",
    [
        "getLoginUserId()",
        "getRequiredTenantId()",
        "FOR UPDATE",
        "Business permission denied",
        "Unknown or server-owned field",
        "Relation IDs must be wire strings",
        "if(result.size()>1)",
        "sidecar.lockProject(tenant())",
        "administratorCount",
        "Business bootstrap must complete before registration",
        'sidecar.roles(tenant(),user).contains("super_admin")',
        "Native generated request validation failed",
        "validator.validate(request)",
        "load(target,ref,true)",
        "No workflow",
        "Invalid state transition",
        "sidecar.initialize(tenant()",
        "nativeConfiguration.updateConfig(request)",
    ],
)
def test_runtime_contains_explicit_native_boundary_guards(fragment):
    assert fragment in (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")


def test_native_registration_keeps_real_service_and_single_transaction():
    source = (TEMPLATES / "RndBusinessRegistration.java").read_text(encoding="utf-8")
    assert "AdminUserService.registerUser" in source
    assert "TransactionTemplate" in source and "call.proceed()" in source
    assert "business.registered" in source
    assert "password" not in source.lower().replace("password hashing", "")


def test_role_mapper_cannot_grant_unrelated_global_roles():
    source = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    assert 'roleCode(String.valueOf(data.get("role")))' in source
    assert "Role not declared by this product" in source
    assert "sidecar.revoke" in source and "oldAdmin&&!newAdmin" in source
    mapper = (TEMPLATES / "RndBusinessMapper.java").read_text(encoding="utf-8")
    assert "pg_advisory_xact_lock" in mapper
    assert "r.tenant_id=u.tenant_id" in mapper
    assert "WHERE tenant_id=#{tenant} AND recipient_id=#{user}" in mapper


def test_frontend_retains_native_components_and_contract_driven_controls():
    source = (TEMPLATES / "panel.vue").read_text(encoding="utf-8")
    assert "useVbenForm" in source and "useVbenModal" in source
    assert "TimelineItem" in source and "'ant-design-vue'" in source
    assert "metrics" in source and "notifications" in source and "roleAdmin" in source
    assert "requestClient" in source and "localStorage" not in source
    assert "useEcharts" in (TEMPLATES / "metric-chart.vue").read_text(encoding="utf-8")
    fields = (TEMPLATES / "business-form.ts").read_text(encoding="utf-8")
    assert "spec.controlled.map(wire)" in fields
    assert "valueField: 'id'" in fields and "ApiSelect" in fields


@pytest.mark.parametrize(
    "key,value",
    [
        ("table", "system_users"),
        ("table", "wb_12345678_other"),
        ("table", "wb_1234567_customers"),
        ("permission", "system:user:create"),
        ("permission", "infra:wb-requests"),
        ("api", "/admin-api/system/user"),
        ("list", "/admin-api/system/user/page"),
        ("route", "/system/user"),
    ],
)
def test_target_cannot_redirect_schema_or_native_permission(tmp_path, key, value):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    controller = (
        backend
        / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/wbcustomers/WbCustomersController.java"
    )
    original = controller.read_bytes()
    targets[0][key] = value
    with pytest.raises(ValueError, match="native generated binding"):
        install_yudao_business(plan, backend, frontend, targets, reports)
    assert controller.read_bytes() == original
    assert not reports.exists()


def test_targets_from_different_native_runs_are_rejected(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    targets[1]["table"] = targets[1]["table"].replace("12345678", "aabbccdd")
    with pytest.raises(ValueError, match="one native generation"):
        install_yudao_business(plan, backend, frontend, targets, reports)


def test_duplicate_target_cannot_install_extra_tables(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    targets.append(deepcopy(targets[0]))
    with pytest.raises(ValueError, match="Duplicate native"):
        install_yudao_business(plan, backend, frontend, targets, reports)


def test_action_modal_opens_before_waiting_for_lazy_form_mount():
    source = (TEMPLATES / "panel.vue").read_text(encoding="utf-8")
    start = source.index("async function openAction(")
    end = source.index("async function submitAction(", start)
    body = source[start:end]
    assert body.index("actionModalApi.open()") < body.index("await actionFormApi.resetForm()")


def test_business_controller_uses_native_admin_package_prefix(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    install_yudao_business(plan, backend, frontend, targets, reports)
    controller = (
        backend
        / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/rndbusiness/RndBusinessController.java"
    )
    text = controller.read_text(encoding="utf-8")
    assert "package cn.iocoder.yudao.module.infra.controller.admin.rndbusiness;" in text
    assert '@RequestMapping("/infra/rnd-business")' in text
    assert "import cn.iocoder.yudao.module.infra.business.RndBusinessService;" in text
    assert not (
        backend / f"{JAVA_ROOT}/{JAVA_PACKAGE}/business/RndBusinessController.java"
    ).exists()


def test_related_history_checks_parent_and_each_child_scope():
    source = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    body = source.split("public Object related(", 1)[1].split("public Object history(", 1)[0]
    assert 'require(name,parent,"read")' in body
    assert 'if(!hasAction(child,"read")) continue' in body
    assert ".eq(field,id(parent))" in body
    assert 'if(!allowed(child,row,"read")) continue' in body
    assert 'allowed(child,row,"read_history")' in body
    assert "candidates.size()>10000" in body
    assert "rnd_archived_at" not in body  # Archived child records remain historical.
    assert "target_entity" in body


def test_related_history_uses_native_route_and_visible_timeline():
    controller = (TEMPLATES / "RndBusinessController.java").read_text(encoding="utf-8")
    panel = (TEMPLATES / "panel.vue").read_text(encoding="utf-8")
    assert '@GetMapping("/related")' in controller
    assert "business.related(entity,id)" in controller
    assert "business-related-${group.entity}" in panel
    assert "related-history-${group.entity}-${record.record.id}" in panel
    assert "record.actions.includes('read_history')" in panel
    assert "business-related-history" in panel
    assert "request !== relatedRequest || current !== generation" in panel
    assert '<TimelineItem v-for="entry in relatedEvents"' in panel


def test_native_display_metadata_does_not_change_wire_audit_or_metric_serialization():
    source = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    raw = source.split("private Map<String,Object> out(", 1)[1].split(
        "private static class Presentation", 1
    )[0]
    assert "_display" not in raw and "userLabel" not in raw and "referenceLabel" not in raw
    event = source.split("private long event(", 1)[1].split("private void notify(", 1)[0]
    assert "encode(out(name,row))" in event and "present(" not in event
    metrics = source.split("public Object metrics()", 1)[1].split(
        "public Object notifications()", 1
    )[0]
    assert 'item.put("buckets",counts)' in metrics
    assert 'item.put("bucketLabels",labels)' in metrics
    assert "present(" not in metrics


def test_reference_and_user_names_are_scoped_cached_and_non_recursive():
    source = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    relation = source.split("private String referenceLabel(", 1)[1].split(
        "private Map<String,Object> present(", 1
    )[0]
    assert "display.references.computeIfAbsent" in relation
    assert 'allowed(target,linked,"read")' in relation
    assert relation.index('allowed(target,linked,"read")') < relation.index(
        "recordLabel(target,linked)"
    )
    assert "present(" not in relation
    user = source.split("private String userLabel(", 1)[1].split(
        "private String referenceLabel(", 1
    )[0]
    assert "display.users.computeIfAbsent" in user
    assert "rolesFor(number(key)).isEmpty()" in user
    assert "sidecar.displayUser(tenant(),number(key))" in user
    assert "sidecar.users(" not in user
    mapper = (TEMPLATES / "RndBusinessMapper.java").read_text(encoding="utf-8")
    assert (
        "SELECT nickname, username FROM system_users WHERE tenant_id=#{tenant} AND id=#{user}"
        in mapper
    )
    history = source.split("public Object history(", 1)[1].split("public void bootstrap(", 1)[0]
    assert history.index('require(name,row,audit?"read_audit":"read_history")') < history.index(
        'item.put("actor_name"'
    )
    page = source.split("public Object page(", 1)[1].split("public void archive(", 1)[0]
    assert 'if(!allowed(name,row,"read")' in page
    assert "for(Object row:rows.subList(start,end)) visible.add(present" in page


def test_display_helpers_are_generic_labels_and_keep_native_grid_structure(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    install_yudao_business(plan, backend, frontend, targets, reports)
    root = frontend / "apps/web-antd/src/views/infra"
    data = (root / "wbcustomers/data.ts").read_text(encoding="utf-8")
    assert (
        "function nativeBusinessGridColumns(): VxeTableGridOptions<NativeData>['columns']" in data
    )
    assert "businessGridColumns('customers', nativeBusinessGridColumns())" in data
    assert "businessSearchSchema('customers', nativeBusinessSearchSchema())" in data
    source = (root / "rnd-business/business-form.ts").read_text(encoding="utf-8")
    assert "field.label || field.name" in source
    assert "field.choice_labels[value] || value" in source
    assert "showHeaderOverflow: true" in source and "minWidth:" in source
    assert "date.toISOString().slice(0, 19)" in source
    assert "Reflect.get(row, '_display')" in source
    assert "field: 'customerId'" not in source and "field: 'requestState'" not in source
    panel = (root / "rnd-business/panel.vue").read_text(encoding="utf-8")
    assert "transition.label || transition.name" in panel
    assert "entry.actor_name" in panel
    assert "businessDetails(props.entity, meta.value.record)" in panel
    assert ':bucket-labels="metric.bucketLabels"' in panel
    assert "white-space: nowrap" in panel
    assert 'class="rnd-business-grid"' in (root / "wbcustomers/index.vue").read_text(
        encoding="utf-8"
    )


def test_native_grid_contract_change_fails_before_writing(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    data = frontend / "apps/web-antd/src/views/infra/wbcustomers/data.ts"
    data.write_text(
        data.read_text(encoding="utf-8").replace("useGridColumns", "changedGridColumns"),
        encoding="utf-8",
    )
    controller = (
        backend
        / f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/wbcustomers/WbCustomersController.java"
    )
    before = controller.read_bytes()
    with pytest.raises(ValueError, match="Native Vben grid schema contract changed"):
        install_yudao_business(plan, backend, frontend, targets, reports)
    assert controller.read_bytes() == before
    assert not reports.exists()


def test_notification_display_preserves_raw_message_and_stable_read_controls():
    service = (TEMPLATES / "RndBusinessService.java").read_text(encoding="utf-8")
    notices = service.split("public Object notifications()", 1)[1]
    assert 'n.put("display_message"' in notices
    assert 'n.put("message"' not in notices
    assert notices.index('allowed(n.get("entity").toString(),row,"read")') < notices.index(
        'n.put("display_message"'
    )
    panel = (TEMPLATES / "panel.vue").read_text(encoding="utf-8")
    assert "business-notice-read-${record.id}" in panel
    assert "business-notice-read-state-${record.id}" in panel
    assert "record.display_message || record.message" in panel
````
