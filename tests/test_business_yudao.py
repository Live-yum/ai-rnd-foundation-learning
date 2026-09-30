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
    service = (TEMPLATES / "RndBusinessService.java").read_text()
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
    ).read_text()
    for function in ("create", "update", "archive", "archiveBatch", "get", "page"):
        assert "business." + function + "(" in controller
    assert "export-excel" not in controller
    config = json.loads(
        (
            backend
            / "yudao-module-infra/yudao-module-infra-server/src/main/resources/rnd-business-contract.json"
        ).read_text()
    )
    assert config["business"] == plan.business.model_dump()
    assert config["specDigest"] == receipt["spec_digest"]
    assert all(binding["requestVO"].endswith("SaveReqVO") for binding in config["bindings"])
    assert all(binding["permission"].startswith("infra:wb-") for binding in config["bindings"])
    panel = (frontend / "apps/web-antd/src/views/infra/wbcustomers/index.vue").read_text()
    assert "<Page>" in panel and "<Grid " in panel and "<TableAction" in panel
    assert "<RndBusinessPanel" in panel
    data = (frontend / "apps/web-antd/src/views/infra/wbcustomers/data.ts").read_text()
    assert "nativeBusinessFormSchema" in data and "businessFormSchema" in data
    form = (frontend / "apps/web-antd/src/views/infra/wbcustomers/modules/form.vue").read_text()
    assert "businessPayload('customers', (await formApi.getValues()) as NativeData)" in form
    assert "as unknown" not in form


def test_vben_form_field_type_covers_the_exact_emitted_metadata():
    import re

    from workbench.domain import FieldSpec

    source = (TEMPLATES / "business-form.ts").read_text()
    declaration = re.search(r"interface Field \{([^}]+)\}", source).group(1)
    fields = set(re.findall(r"(\w+)\s*:", declaration))
    assert fields == set(FieldSpec.model_fields)
    assert "businessPayload<T extends object>" in source
    assert "Reflect.deleteProperty(result, name)" in source
    assert "as unknown" not in source and "as any" not in source
    panel = (TEMPLATES / "panel.vue").read_text()
    assert "row: Record<string, unknown>" in panel
    assert "typeof record.id !== 'string'" in panel
    assert "row.actions.includes('read_history')" in panel


def test_reentry_is_hash_bound_and_tampering_never_overwrites(tmp_path):
    plan = approved_plan()
    args = generated_native_source(tmp_path, plan)
    first = install_yudao_business(plan, *args)
    assert install_yudao_business(plan, *args) == first
    source = args[0] / first["files"][0]["path"]
    source.write_text("// user's inspection changes\n")
    with pytest.raises(ValueError, match="source changed"):
        install_yudao_business(plan, *args)
    assert source.read_text() == "// user's inspection changes\n"


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
    data = (root / "wbcustomers/data.ts").read_text()
    assert (
        "function nativeBusinessGridColumns(): VxeTableGridOptions<NativeData>['columns']" in data
    )
    assert "businessGridColumns('customers', nativeBusinessGridColumns())" in data
    assert "businessSearchSchema('customers', nativeBusinessSearchSchema())" in data
    source = (root / "rnd-business/business-form.ts").read_text()
    assert "field.label || field.name" in source
    assert "field.choice_labels[value] || value" in source
    assert "showHeaderOverflow: true" in source and "minWidth:" in source
    assert "date.toISOString().slice(0, 19)" in source
    assert "Reflect.get(row, '_display')" in source
    assert "field: 'customerId'" not in source and "field: 'requestState'" not in source
    panel = (root / "rnd-business/panel.vue").read_text()
    assert "transition.label || transition.name" in panel
    assert "entry.actor_name" in panel
    assert "businessDetails(props.entity, meta.value.record)" in panel
    assert ':bucket-labels="metric.bucketLabels"' in panel
    assert "white-space: nowrap" in panel
    assert 'class="rnd-business-grid"' in (root / "wbcustomers/index.vue").read_text()


def test_native_grid_contract_change_fails_before_writing(tmp_path):
    plan = approved_plan()
    backend, frontend, targets, reports = generated_native_source(tmp_path, plan)
    data = frontend / "apps/web-antd/src/views/infra/wbcustomers/data.ts"
    data.write_text(data.read_text().replace("useGridColumns", "changedGridColumns"))
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
    service = (TEMPLATES / "RndBusinessService.java").read_text()
    notices = service.split("public Object notifications()", 1)[1]
    assert 'n.put("display_message"' in notices
    assert 'n.put("message"' not in notices
    assert notices.index('allowed(n.get("entity").toString(),row,"read")') < notices.index(
        'n.put("display_message"'
    )
    panel = (TEMPLATES / "panel.vue").read_text()
    assert "business-notice-read-${record.id}" in panel
    assert "business-notice-read-state-${record.id}" in panel
    assert "record.display_message || record.message" in panel
