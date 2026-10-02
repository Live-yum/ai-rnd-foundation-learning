"""Deterministic approved batch-import module for actual FastapiAdmin products.

The caller owns the approval gate. Installation is additive to a newly generated
business product; it does not upgrade a running product or migrate user data.
"""

import ast
import shutil
from pathlib import Path
from typing import Literal

from pydantic import Field

from workbench.domain import Contract, Name, Plan, digest
from workbench.filesystem import atomic_text, sha, write_json
from workbench.settings import ROOT


class ImportModuleSpec(Contract):
    entity: Name
    duplicate_policy: Literal["reject_all"] = "reject_all"
    max_rows: int = Field(default=1000, ge=1, le=1000, strict=True)


def install_import_module(
    plan, backend, frontend, reports, *, entity, duplicate_policy="reject_all", max_rows=1000
):
    """Install only after the parent workflow approved this exact plan and spec."""
    plan = Plan.model_validate(plan)
    spec = ImportModuleSpec(entity=entity, duplicate_policy=duplicate_policy, max_rows=max_rows)
    if not plan.business:
        raise ValueError("Batch import requires the actual approved native business product")
    plan.business.validate_plan(plan)
    entities = {item.name: item for item in plan.entities}
    if entity not in entities:
        raise ValueError("Import entity must exist in the approved business plan")
    if not any(
        p.entity == entity and {"create", "read"} <= set(p.actions)
        for p in plan.business.permissions
    ):
        raise ValueError("No business role may both create and read the import entity")
    backend, frontend, reports = map(Path, (backend, frontend, reports))
    plugin = backend / "app/plugin/module_business"
    source = ROOT / "templates/modules/fastapiadmin"
    if (plugin / "import.json").exists():
        raise ValueError("Import module already exists; incremental installation needs a new plan")
    business_config = plugin / "business.json"
    if not business_config.is_file():
        raise ValueError("Actual generated native business configuration is missing")
    import json

    existing = json.loads(business_config.read_text(encoding="utf-8"))
    if digest(existing["plan"]) != digest(plan.model_dump(mode="json")):
        raise ValueError("Installed business product differs from the approved plan")
    runtime = plugin / "runtime.py"
    if not runtime.is_file() or not any(
        isinstance(node, ast.AsyncFunctionDef) and node.name == "stage_create"
        for node in ast.parse(runtime.read_text(encoding="utf-8")).body
    ):
        raise ValueError("Native runtime lacks atomic stage_create; regenerate this product")
    controller = plugin / "controller.py"
    controller_body = controller.read_text(encoding="utf-8")
    anchor = 'BusinessRouter = APIRouter(tags=["Business workflows"])'
    if controller_body.count(anchor) != 1 or "import_routes" in controller_body:
        raise ValueError("Unexpected native BusinessRouter shape; refusing unsafe installation")
    controller_body = controller_body.replace(
        anchor,
        anchor
        + "\n\nfrom .import_routes import router as import_router\nBusinessRouter.include_router(import_router)",
    )
    ast.parse(controller_body)
    changes = [(controller, controller_body)]
    page_anchor = '          <ElButton data-testid="business-create"'
    script_anchor = "import { request } from '@utils';"
    for item in plan.entities:
        page = frontend / f"src/views/module_rnd/{item.name}/index.vue"
        body = page.read_text(encoding="utf-8")
        if body.count(page_anchor) != 1 or body.count(script_anchor) != 1 or "ImportWizard" in body:
            raise ValueError("Native business page has no recognized module extension point")
        entry = (
            f"          <ImportWizard v-if=\"tab === '{entity}' &amp;&amp; can('create') &amp;&amp; can('read')\" "
            f':entity="tab" :fields="editableFields" :max-rows="{max_rows}" @committed="refresh" />\n'
        )
        body = body.replace(page_anchor, entry + page_anchor, 1)
        body = body.replace(
            script_anchor,
            script_anchor + "\nimport ImportWizard from '@/components/business/ImportWizard.vue';",
            1,
        )
        changes.append((page, body))
    destination = frontend / "src/components/business/ImportWizard.vue"
    if destination.exists():
        raise ValueError("Import component path is already occupied")
    for name in ("import_runtime.py", "import_routes.py"):
        if (plugin / name).exists():
            raise ValueError("Import runtime path is already occupied")
        ast.parse((source / name).read_text(encoding="utf-8"))
    backups = reports / "import-module-originals"
    if backups.exists():
        raise ValueError("Prior import installation evidence exists")
    backups.mkdir(parents=True)
    originals = {}
    for index, (path, _) in enumerate(changes):
        shutil.copyfile(path, backups / f"{index}-{path.name}")
        originals[str(path.relative_to(backend if path.is_relative_to(backend) else frontend))] = (
            sha(path)
        )
    for name in ("import_runtime.py", "import_routes.py"):
        shutil.copyfile(source / name, plugin / name)
    config = {
        **spec.model_dump(),
        "module": "batch-import-v1",
        "plan_digest": digest(plan.model_dump(mode="json")),
    }
    write_json(plugin / "import.json", config)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source / "ImportWizard.vue", destination)
    for path, body in changes:
        atomic_text(path, body)
    receipt = {
        "module": "batch-import-v1",
        "template": "fastapiadmin",
        "spec": spec.model_dump(),
        "plan_digest": config["plan_digest"],
        "config_digest": digest(config),
        "originals": originals,
        "schema_migration_required": False,
        "journal": "existing native business event table, owner-bound",
        "duplicate_match": "all importable fields in nonarchived authorized records",
        "atomic_commit": "stage_create rows and audit plus journal receipt in one transaction",
        "runtime_verified": False,
        "native_shell_modified": False,
        "files": {
            str(path.relative_to(backend if path.is_relative_to(backend) else frontend)): sha(path)
            for path in [
                *(p for p, _ in changes),
                destination,
                plugin / "import.json",
                plugin / "import_routes.py",
                plugin / "import_runtime.py",
            ]
        },
    }
    write_json(reports / "import-module-installation.json", receipt)
    return receipt
