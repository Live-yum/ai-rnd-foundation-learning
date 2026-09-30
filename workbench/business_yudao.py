"""Declarative business policy mounted on genuine Yudao Infra/MyBatis and Vben scaffolds.

No model source, dynamic SQL from user inputs, destructive database initialization,
or generic replacement frontend. Schema installation is explicit and owned by the caller.
"""

import json
import re
from pathlib import Path

from workbench.domain import Plan, digest
from workbench.filesystem import atomic_text, inside, sha, write_json
from workbench.settings import ROOT

TEMPLATES = ROOT / "templates/business/yudao"
JAVA_ROOT = "yudao-module-infra/yudao-module-infra-server/src/main/java"
JAVA_PACKAGE = "cn/iocoder/yudao/module/infra"
RESOURCE_ROOT = "yudao-module-infra/yudao-module-infra-server/src/main/resources"


def _quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def _name(value):
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value):
        raise ValueError("Untrusted native SQL identifier")
    return value


def _class(entity):
    return "Wb" + "".join(part.title() for part in entity.split("_"))


def business_schema(plan, targets, prefix):
    """Fresh, manifest-bound extension; duplicate installation is deliberately not hidden."""
    prefix = _name(prefix)
    lines = [
        "-- Apply after native business generation and before starting the policy runtime.",
        f"CREATE TABLE {prefix}_setup (tenant_id BIGINT PRIMARY KEY,spec_digest VARCHAR(64) NOT NULL,bootstrap_user_id BIGINT NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);",
        f"CREATE TABLE {prefix}_audit (id BIGSERIAL PRIMARY KEY, tenant_id BIGINT NOT NULL, "
        "entity VARCHAR(40) NOT NULL, record_id BIGINT NOT NULL, actor_id BIGINT NOT NULL, "
        "action VARCHAR(60) NOT NULL, before_data TEXT NOT NULL, after_data TEXT NOT NULL, "
        "note VARCHAR(4000) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);",
        f"CREATE INDEX {prefix}_audit_row ON {prefix}_audit(tenant_id,entity,record_id,id);",
        f"CREATE FUNCTION {prefix}_immutable() RETURNS trigger LANGUAGE plpgsql AS $$ "
        "BEGIN RAISE EXCEPTION 'Business audit is append-only'; END; $$;",
        f"CREATE TRIGGER {prefix}_audit_immutable BEFORE UPDATE OR DELETE ON {prefix}_audit "
        f"FOR EACH ROW EXECUTE FUNCTION {prefix}_immutable();",
        f"CREATE TABLE {prefix}_notifications (id BIGSERIAL PRIMARY KEY,tenant_id BIGINT NOT NULL,"
        "entity VARCHAR(40) NOT NULL,record_id BIGINT NOT NULL,recipient_id BIGINT NOT NULL,"
        "event_key VARCHAR(220) NOT NULL,message VARCHAR(500) NOT NULL,"
        "created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,read_at TIMESTAMPTZ,"
        "UNIQUE(tenant_id,recipient_id,event_key));",
    ]
    for target in targets:
        table = _name(target["table"])
        lines.append(f"ALTER TABLE {table} ADD COLUMN rnd_archived_at TIMESTAMP NULL;")
    return "\n".join(lines) + "\n"


def business_role_seed(plan, targets, prefix):
    """The authenticated bootstrap endpoint installs approved roles transactionally."""
    _name(prefix)
    return (
        "-- No implicit user-ID assignment or native-global-role mutation.\n"
        "-- POST /admin-api/infra/rnd-business/bootstrap as an authenticated native super_admin.\n"
        "-- The atomic endpoint creates only this plan's namespaced business roles/menu grants.\n"
        "SELECT 1;\n"
    )


def _mount_panel(body, entity):
    marker = re.search(r"<script\b[^>]*\bsetup\b[^>]*>", body)
    if not marker or body.count("</Page>") != 1:
        raise ValueError("Native Vben Page/setup contract changed")
    imports = (
        "\nimport { ref as rndBusinessRef } from 'vue';\n"
        "import RndBusinessPanel from '../rnd-business/panel.vue';\n"
        "const rndBusinessRecord = rndBusinessRef<string>();\n"
        "function rndOpenBusiness(row: { id?: string | number }) { "
        "if (row.id !== undefined) rndBusinessRecord.value = String(row.id); }\n"
    )
    body = body[: marker.end()] + imports + body[marker.end() :]
    slot = body.find('<template #actions="{ row }">')
    if slot < 0:
        raise ValueError("Native Vben row actions slot missing")
    action = body.find(':actions="[', slot)
    if action < 0:
        raise ValueError("Native TableAction contract changed")
    action += len(':actions="[')
    body = (
        body[:action]
        + "\n{ label: '业务详情', onClick: () => rndOpenBusiness(row) },"
        + body[action:]
    )
    panel = (
        f'    <RndBusinessPanel entity="{entity}" :record-id="rndBusinessRecord" '
        '@changed="handleRefresh" />\n  </Page>'
    )
    body = body.replace("</Page>", panel)
    body = body.replace("<Grid", '<Grid class="rnd-business-grid"', 1)
    return (
        body
        + "\n<style scoped>\n.rnd-business-grid :deep(.vxe-header--column .vxe-cell) { white-space: nowrap; }\n</style>\n"
    )


def install_yudao_business(plan, backend, frontend, targets, reports):
    """Mount policy source and emit ordered explicit SQL; caller executes SQL before restart."""
    plan = Plan.model_validate(plan)
    if plan.business is None:
        raise ValueError("Yudao business adapter requires an approved business contract")
    backend, frontend, reports = Path(backend), Path(frontend), Path(reports)
    if {target["entity"] for target in targets} != {entity.name for entity in plan.entities}:
        raise ValueError("Native generation targets differ from the business plan")
    if len(targets) != len(plan.entities):
        raise ValueError("Duplicate native business targets")
    table_prefixes = set()
    for target in targets:
        name = target["entity"]
        table = target.get("table")
        match = re.fullmatch(r"wb_([0-9a-f]{8})_" + re.escape(name), table or "")
        if match is None:
            raise ValueError("Business target table is not the native generated binding")
        table_prefixes.add(match.group(1))
        kebab = "wb-" + name.replace("_", "-")
        if target.get("permission") != "infra:" + kebab:
            raise ValueError("Business target permission is not the native generated binding")
        expected_routes = {
            "api": "/admin-api/infra/" + kebab,
            "list": "/admin-api/infra/" + kebab + "/page",
            "route": "/workbench/" + kebab,
        }
        if any(key in target and target[key] != value for key, value in expected_routes.items()):
            raise ValueError("Business target route is not the native generated binding")
    if len(table_prefixes) != 1:
        raise ValueError("Business targets must belong to one native generation")
    prefix = "rndb_" + digest({"plan": plan.model_dump(), "targets": targets})[:12]
    receipt_path = reports / "business-yudao.json"
    identity = digest(plan.model_dump())
    if receipt_path.is_file():
        saved = json.loads(receipt_path.read_text(encoding="utf-8"))
        if saved.get("spec_digest") != identity or saved.get("prefix") != prefix:
            raise ValueError("Business adapter receipt identity changed")
        for item in saved["files"]:
            root = backend if item["root"] == "backend" else frontend
            if sha(inside(root, item["path"])) != item["sha256"]:
                raise ValueError("Mounted business source changed; preserve and inspect")
        return saved
    writes = []
    bindings = []
    provenance = []
    for entity in plan.entities:
        slug, name = "wb" + entity.name.replace("_", ""), _class(entity.name)
        relative = f"{JAVA_ROOT}/{JAVA_PACKAGE}/controller/admin/{slug}/{name}Controller.java"
        controller = inside(backend, relative)
        original = controller.read_text(encoding="utf-8")
        if (
            f"class {name}Controller" not in original
            or f'"/infra/wb-{entity.name.replace("_", "-")}"' not in original
        ):
            raise ValueError("Unexpected original Infra-generated controller")
        provenance.append({"entity": entity.name, "controller_sha256": sha(controller)})
        rendered = (TEMPLATES / "EntityController.java").read_text(encoding="utf-8")
        for key, value in {
            "__SLUG__": slug,
            "__CLASS__": name,
            "__ENTITY__": entity.name,
            "__KEBAB__": "wb-" + entity.name.replace("_", "-"),
        }.items():
            rendered = rendered.replace(key, value)
        writes.append(("backend", relative, rendered, True))
        do_relative = f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/dataobject/{slug}/{name}DO.java"
        do_source = inside(backend, do_relative).read_text(encoding="utf-8")
        if f"class {name}DO" not in do_source or not do_source.rstrip().endswith("}"):
            raise ValueError("Unexpected original Infra-generated data object")
        do_source = (
            do_source.rstrip()[:-1]
            + '\n    @com.baomidou.mybatisplus.annotation.TableField("rnd_archived_at")\n    private java.time.LocalDateTime rndArchivedAt;\n}\n'
        )
        writes.append(("backend", do_relative, do_source, True))
        mapper_relative = f"{JAVA_ROOT}/{JAVA_PACKAGE}/dal/mysql/{slug}/{name}Mapper.java"
        if not inside(backend, mapper_relative).is_file():
            raise ValueError("Actual Infra-generated mapper is required")
        bindings.append(
            {
                "entity": entity.name,
                "requestVO": "cn.iocoder.yudao.module.infra.controller.admin."
                + slug
                + ".vo."
                + name
                + "SaveReqVO",
                "permission": next(t["permission"] for t in targets if t["entity"] == entity.name),
                "mapper": "cn.iocoder.yudao.module.infra.dal.mysql." + slug + "." + name + "Mapper",
                "dataObject": "cn.iocoder.yudao.module.infra.dal.dataobject."
                + slug
                + "."
                + name
                + "DO",
            }
        )
        data_path = f"apps/web-antd/src/views/infra/{slug}/data.ts"
        data_source = inside(frontend, data_path).read_text(encoding="utf-8")
        signature = "export function useFormSchema(): VbenFormSchema[] {"
        if data_source.count(signature) != 1:
            raise ValueError("Native Vben form schema contract changed")
        data_source = data_source.replace(
            signature, "function nativeBusinessFormSchema(): VbenFormSchema[] {", 1
        )
        wrappers = [
            f"export function useFormSchema(): VbenFormSchema[] {{ return businessFormSchema('{entity.name}', nativeBusinessFormSchema()); }}"
        ]
        for function, native, helper in (
            ("useGridFormSchema", "nativeBusinessSearchSchema", "businessSearchSchema"),
            ("useGridColumns", "nativeBusinessGridColumns", "businessGridColumns"),
        ):
            pattern = re.compile(r"export function " + function + r"\(\): ([^\n{]+)\s*\{")
            matches = list(pattern.finditer(data_source))
            if len(matches) != 1:
                raise ValueError("Native Vben grid schema contract changed")
            return_type = matches[0].group(1).strip()
            data_source = pattern.sub(
                lambda match: f"function {native}(): {return_type} {{", data_source, count=1
            )
            wrappers.append(
                f"export function {function}(): {return_type} {{ return {helper}('{entity.name}', {native}()); }}"
            )
        data_source = (
            "import { businessFormSchema, businessSearchSchema, businessGridColumns } from '../rnd-business/business-form';\n"
            + data_source
        )
        data_source += "\n" + "\n".join(wrappers) + "\n"
        writes.append(("frontend", data_path, data_source, True))
        form_path = f"apps/web-antd/src/views/infra/{slug}/modules/form.vue"
        form_source = inside(frontend, form_path).read_text(encoding="utf-8")
        marker = re.search(r"<script\b[^>]*\bsetup\b[^>]*>", form_source)
        anchor = "(await formApi.getValues())"
        typed_value = re.compile(
            r"\(await formApi\.getValues\(\)\) as [A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*"
        )
        if (
            not marker
            or form_source.count(anchor) != 1
            or len(typed_value.findall(form_source)) != 1
        ):
            raise ValueError("Native Vben form submit contract changed")
        form_source = (
            form_source[: marker.end()]
            + "\nimport { businessPayload } from '../../rnd-business/business-form';\n"
            + form_source[marker.end() :]
        )
        form_source = typed_value.sub(
            lambda match: f"businessPayload('{entity.name}', {match.group(0)})",
            form_source,
            count=1,
        )
        writes.append(("frontend", form_path, form_source, True))
        page = f"apps/web-antd/src/views/infra/{slug}/index.vue"
        writes.append(
            (
                "frontend",
                page,
                _mount_panel(inside(frontend, page).read_text(encoding="utf-8"), entity.name),
                True,
            )
        )
    config = {
        **plan.model_dump(),
        "bindings": bindings,
        "rolePrefix": prefix + "_",
        "specDigest": identity,
    }
    writes.append(
        (
            "backend",
            f"{RESOURCE_ROOT}/rnd-business-contract.json",
            json.dumps(config, ensure_ascii=False, indent=2) + "\n",
            False,
        )
    )
    for file in TEMPLATES.glob("Rnd*.java"):
        text = file.read_text(encoding="utf-8").replace("__PREFIX__", prefix)
        package_path = (
            "controller/admin/rndbusiness"
            if file.name == "RndBusinessController.java"
            else "business"
        )
        writes.append(
            ("backend", f"{JAVA_ROOT}/{JAVA_PACKAGE}/{package_path}/{file.name}", text, False)
        )
    for file in TEMPLATES.glob("*.vue"):
        writes.append(
            (
                "frontend",
                f"apps/web-antd/src/views/infra/rnd-business/{file.name}",
                file.read_text(encoding="utf-8"),
                False,
            )
        )
    form_specs = {}
    for entity in plan.entities:
        workflow = next((w for w in plan.business.workflows if w.entity == entity.name), None)
        resource = next(r for r in plan.business.resources if r.entity == entity.name)
        controlled = {resource.assignee_field} if resource.assignee_field else set()
        if workflow:
            controlled.add(workflow.status_field)
            controlled.update(t.set_timestamp for t in workflow.transitions if t.set_timestamp)
        references = {}
        for relation in plan.business.relations:
            if relation.entity == entity.name:
                if relation.target_entity == "$users":
                    references[relation.field] = {"target": "$users", "label": "displayName"}
                    continue
                references[relation.field] = {
                    "target": relation.target_entity,
                    "label": "_recordLabel",
                }
        form_specs[entity.name] = {
            "fields": [f.model_dump() for f in entity.fields],
            "controlled": sorted(controlled),
            "references": references,
            "statusField": workflow.status_field if workflow else "",
        }
    form_source = (
        (TEMPLATES / "business-form.ts")
        .read_text(encoding="utf-8")
        .replace("__FORM_CONFIG__", json.dumps(form_specs, ensure_ascii=False))
    )
    writes.append(
        (
            "frontend",
            "apps/web-antd/src/views/infra/rnd-business/business-form.ts",
            form_source,
            False,
        )
    )
    before = {}
    for kind, name, _, existing in writes:
        target = inside(backend if kind == "backend" else frontend, name)
        if target.exists() and not existing:
            raise FileExistsError("Refusing to replace unowned business source: " + name)
        before[kind, name] = target.read_text(encoding="utf-8") if target.is_file() else None
    changed = []
    try:
        for kind, name, text, _ in writes:
            target = inside(backend if kind == "backend" else frontend, name)
            atomic_text(target, text)
            changed.append((kind, name, target))
        atomic_text(
            reports / "business-extension-schema.sql", business_schema(plan, targets, prefix)
        )
        atomic_text(reports / "business-role-seed.sql", business_role_seed(plan, targets, prefix))
    except BaseException:
        for kind, name, target in reversed(changed):
            if before[kind, name] is None:
                target.unlink()
            else:
                atomic_text(target, before[kind, name])
        raise
    receipt = {
        "template": "yudao-vben",
        "spec_digest": identity,
        "prefix": prefix,
        "native_scaffold_provenance": provenance,
        "runtime_verified": False,
        "schema_order": ["business-extension-schema.sql", "business-role-seed.sql"],
        "extension_tables": {
            prefix + "_setup": ["tenant_id", "spec_digest", "bootstrap_user_id", "created_at"],
            prefix + "_audit": [
                "id",
                "tenant_id",
                "entity",
                "record_id",
                "actor_id",
                "action",
                "before_data",
                "after_data",
                "note",
                "created_at",
            ],
            prefix + "_notifications": [
                "id",
                "tenant_id",
                "entity",
                "record_id",
                "recipient_id",
                "event_key",
                "message",
                "created_at",
                "read_at",
            ],
        },
        "bootstrap_endpoint": "/admin-api/infra/rnd-business/bootstrap",
        "files": [
            {"root": kind, "path": name, "sha256": sha(target)} for kind, name, target in changed
        ],
    }
    write_json(receipt_path, receipt)
    return receipt


# Stable integration alias for the native generation hook.
mount_business = install_yudao_business
extend_business = install_yudao_business
