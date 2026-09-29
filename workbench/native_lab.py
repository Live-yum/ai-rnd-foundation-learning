"""Actual native generation, mounting, permissions, CRUD, restart and browser acceptance."""

import os
import traceback
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest, write_json
from workbench.native_acceptance import (
    check_generated_persistence,
    generated_crud,
    generated_permissions,
)
from workbench.native_compatibility import prepare_fastapi_transactions
from workbench.native_environment import (
    bootstrap_database,
    copy_source,
    install_backend,
    login,
    native_environment,
    running_backend,
)
from workbench.native_frontend import build_frontend, frontend_environment, frontend_preview
from workbench.native_modules import create_native_tables, generate_modules, validate_plan
from workbench.portable import (
    build_native_delivery,
    export_menu_sql,
    menu_snapshot,
    verify_native_delivery,
)
from workbench.settings import ROOT
from workbench.tools import run_command


def generated_browser(template, front_url, reports):
    command = [
        "node",
        str(ROOT / "scripts/native_browser.cjs"),
        template,
        front_url,
        str(reports.resolve()),
        str(ROOT / ".native/browser/node_modules/playwright"),
        str((reports / "browser-targets.json").resolve()),
    ]
    try:
        result = run_command(
            command,
            ROOT,
            240,
            {
                "NODE_OPTIONS": "--dns-result-order=ipv4first",
                "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
            },
        )
    except Exception as exc:
        atomic_text(reports / "browser.log", getattr(exc, "log", str(exc)))
        raise
    atomic_text(reports / "browser.log", result["log"])


def run_acceptance(template, source, output, frontend_source, url, reports, plan, redis_port=6379):
    """Shared by CLI and CI; never reset an existing database or workspace."""
    plan = validate_plan(plan)
    source, output, reports = (
        Path(source).resolve(),
        Path(output).resolve(),
        Path(reports).resolve(),
    )
    reports.mkdir(parents=True, exist_ok=True)
    before = manifest(source)
    frontend_before = manifest(frontend_source) if template == "yudao-vben" else None
    copy_source(source, output)
    backend = output / "backend" if template == "fastapiadmin" else output
    if template == "fastapiadmin":
        frontend = output / "frontend/web"
    else:
        frontend = output.parent / "frontend-product"
        copy_source(frontend_source, frontend)
    env = native_environment(
        template, backend, url, 8001 if template == "fastapiadmin" else 48080, redis_port=redis_port
    )
    write_json(reports / "approved-spec.json", plan.model_dump())
    write_json(
        reports / "acceptance.json", {"template": template, "generated_runtime_verified": False}
    )

    def stage(name):
        write_json(reports / "progress.json", {"template": template, "stage": name})
        print(f"Native {template}: {name}", flush=True)

    try:
        if template == "fastapiadmin":
            write_json(reports / "native-compatibility.json", prepare_fastapi_transactions(backend))
        stage("bootstrap-empty-database")
        bootstrap_database(template, backend, url)
        stage("baseline-install")
        install_backend(template, backend, reports / "baseline")
        with running_backend(template, backend, env, reports / "baseline") as (base_url, openapi):
            stage("native-generation")
            token = login(template, base_url)
            write_json(reports / "baseline/login.json", {"native_login": True})
            baseline_menus = menu_snapshot(template, url)
            mapping = create_native_tables(template, plan, url, digest(plan.model_dump()), reports)
            targets = generate_modules(
                template, backend, frontend, base_url, openapi, token, mapping, plan, reports
            )
            export_menu_sql(template, url, baseline_menus, reports / "menu-seed.sql")
        if template == "yudao-vben":
            stage("generated-build")
            install_backend(template, backend, reports / "generated-build")
        with running_backend(template, backend, env, reports / "generated") as (base_url, _):
            token = login(template, base_url)
            stage("generated-crud")
            records = generated_crud(template, base_url, token, targets, plan)
            write_json(reports / "generated/crud.json", records)
            stage("generated-permissions")
            write_json(
                reports / "generated/permissions.json",
                generated_permissions(template, base_url, token, targets, plan),
            )
        # Compile the large Vben application while the Java process is stopped.
        # Running both heaps concurrently needlessly exhausts smaller CI/WSL hosts.
        front_env = frontend_environment(template, base_url)
        stage("native-frontend-build")
        build_frontend(template, frontend, front_env, reports)
        stage("restart-persistence")
        with running_backend(template, backend, env, reports / "restart") as (base_url, _):
            token = login(template, base_url)
            write_json(
                reports / "restart/persistence.json",
                check_generated_persistence(template, base_url, token, targets, records),
            )
            for target, entity in zip(targets, plan.entities, strict=True):
                target["fields"] = [field.model_dump() for field in entity.fields]
            write_json(reports / "browser-targets.json", targets)
            with frontend_preview(template, frontend, front_env, reports) as front_url:
                stage("native-browser")
                generated_browser(template, front_url, reports)
        assert before == manifest(source), "Original native source was modified"
        if frontend_before is not None:
            assert frontend_before == manifest(frontend_source), "Original Vben source was modified"
        write_json(
            reports / "generated-manifest.json",
            {"backend": manifest(backend), "frontend": manifest(frontend)},
        )
        report = {
            "template": template,
            "scope": "generated-native-modules",
            "generated_runtime_verified": True,
            "native_codegen": True,
            "automatic_mount": True,
            "menu_and_permissions": True,
            "real_crud": True,
            "restart_persistence": True,
            "frontend_build": True,
            "frontend_typecheck": True,
            "real_browser": True,
            "entities": [e.name for e in plan.entities],
            "spec_digest": digest(plan.model_dump()),
            "source_unmodified": True,
            "data_scope": "shared-with-native-role-permissions",
        }
        stage("portable-startup-assets")
        product_root = output if template == "fastapiadmin" else output.parent
        report["portable_delivery"] = build_native_delivery(
            template, product_root, reports, plan, targets, url
        )
        stage("independent-native-delivery")
        report["portable_restored"] = verify_native_delivery(product_root, url, reports, redis_port)
        stage("accepted")
        write_json(reports / "acceptance.json", report)
        print(
            "Generated native modules, menus, permissions, CRUD, restart, frontend build and browser PASS"
        )
        return report
    except Exception as exc:
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        atomic_text(
            reports / "failure.log",
            f"{type(exc).__name__} at {Path(frame.filename).name}:{frame.lineno} ({frame.name}): {exc}\n"
            + getattr(exc, "log", ""),
        )
        raise
