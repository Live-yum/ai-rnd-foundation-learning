"""Live native security certification against the registered generated CI baseline.

Run after ci_native_tools fastapiadmin and native profile prepare/register. This
uses no model and never runs product code on the host. HTTP checks exercise real
signup, captcha/form login, permissions and device CRUD in owned PostgreSQL.
The isolated browser verifies the native Vue login/registration forms; it does
not claim authenticated browser CRUD or replace the native toolchain's UI tests.
"""

import argparse
import json
import re
from pathlib import Path

from scripts.capability_security_probe import security_probe_for_profile
from scripts.ci_capability_profile import require_profile_evidence
from scripts.daytona_capability_profile import inspect_created_sandbox
from scripts.daytona_native_capability_profile import (
    ENVIRONMENT,
    HOME,
    require_native_profile,
    selection,
)
from workbench.capability_browser_isolation import require_browser_acceptance
from workbench.capability_contracts import CapabilityPlan, scope_sources
from workbench.capability_execution import (
    PROTOCOL,
    profile_binding,
    receipt_name,
    require_security_receipt,
    verifier_identity,
)
from workbench.capability_sandbox import _verify
from workbench.domain import Plan, digest
from workbench.filesystem import inside, manifest, write_json
from workbench.local_only import install_loopback_guard
from workbench.sandbox import client_for, close_client, snapshot_for, validate_configuration
from workbench.settings import ROOT, Settings

PRODUCT = ROOT / ".native/tool-product"
GOAL = "原生注册和验证码登录后，管理员操作设备台账，普通注册用户不得越权；真实PostgreSQL记录在应用进程重启后保留，原生Vue表单可交互。"
SIGNUP_USER = "native_security_signup"
SIGNUP_PASSWORD = "NativeSecurity123!"
DEVICE_FIELDS = [("name", "text"), ("quantity", "integer"), ("active", "boolean")]


def baseline_table(product):
    """Read data contracts only; do not import generated deployment code."""
    path = inside(product, "deployment/manifest.json")
    if path.stat().st_size > 1_000_000:
        raise ValueError("Native certification manifest exceeds its input budget")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    if (
        metadata.get("template") != "fastapiadmin"
        or metadata.get("format") != 1
        or metadata.get("contains_user_data") is not False
        or metadata.get("bootstrap") != "native-seed-then-business-schema-and-menus"
        or metadata.get("spec_digest") != digest(metadata.get("plan"))
    ):
        raise ValueError("Native certification requires the generated FastapiAdmin CI baseline")
    plan = Plan.model_validate(metadata["plan"])
    entities = [entity for entity in plan.entities if entity.name == "device"]
    targets = [target for target in metadata.get("targets", []) if target.get("entity") == "device"]
    if len(entities) != 1 or len(targets) != 1:
        raise ValueError("Native certification requires one generated device module")
    target = targets[0]
    if (
        [(field.name, field.kind) for field in entities[0].fields] != DEVICE_FIELDS
        or target.get("api") != "/rnd/device"
        or target.get("list") != "/rnd/device/list"
        or target.get("route") != "/module_rnd/device"
        or target.get("permission") != "module_rnd:device"
        or not re.fullmatch(r"wb_[a-f0-9]{8}_device", str(target.get("table", "")))
        or not {"id", "name", "quantity", "active"}
        <= set(metadata.get("tables", {}).get(target["table"], []))
    ):
        raise ValueError("Native device schema/routes differ from the authored certification")
    for name in (
        "backend/app/__init__.py",
        "backend/app/plugin/module_rnd/device/controller.py",
        "frontend/web/src/views/module_rnd/device/index.vue",
    ):
        if not inside(product, name).is_file():
            raise ValueError("Native certification baseline is missing original/generated source")
    return target["table"]


def login_steps(actor, username, password):
    return [
        {
            "path": "/system/auth/captcha/get",
            "status": 200,
            "equals": {"$.code": 0, "$.data.enable": True},
            "captures": {actor + "_captcha": "$.data.key"},
        },
        {
            "method": "POST",
            "path": "/system/auth/captcha/slider/complete",
            "wait_ms": 300,
            "body": {"captcha_key": "${" + actor + "_captcha}"},
            "status": 200,
            "equals": {"$.code": 0, "$.data.verified": True},
        },
        {
            "method": "POST",
            "path": "/system/auth/login",
            "body_encoding": "form",
            "body": {
                "username": username,
                "password": password,
                "captcha_key": "${" + actor + "_captcha}",
                "login_type": "PC端",
            },
            "status": 200,
            "equals": {"$.code": 0, "$.data.user_info.username": username},
            "captures": {actor: "$.data.access_token"},
        },
    ]


def native_browser_steps():
    # Stable upstream component classes prove real reactive form transitions.
    # No tokens are injected and no browser action disables/completes captcha.
    return [
        {"action": "open", "value": "/#/login"},
        {"action": "visible", "selector": ".login-page-form.el-form"},
        {"action": "visible", "selector": ".drag_verify .dv_handler"},
        {
            "action": "fill",
            "selector": '.login-page-form input[placeholder="请输入账号"]',
            "value": SIGNUP_USER,
        },
        {
            "action": "fill",
            "selector": '.login-page-form input[type="password"]',
            "value": SIGNUP_PASSWORD,
        },
        {"action": "click", "selector": ".login-auth-link-row .el-link"},
        {"action": "visible", "selector": '.login-page-form input[placeholder="请再次确认密码"]'},
        {"action": "text", "selector": ".login-auth-link-row", "value": "已有账号"},
        {"action": "viewport", "width": 390, "height": 844},
        {"action": "visible", "selector": '.login-page-form input[placeholder="请再次确认密码"]'},
        {"action": "click", "selector": ".login-auth-link-row .el-link"},
        {"action": "visible", "selector": ".drag_verify .dv_handler"},
    ]


def fixed_plan(product):
    table = baseline_table(product)
    refs = [item["id"] for item in scope_sources([GOAL])]
    admin = {"Authorization": "Bearer ${admin}"}
    reader = {"Authorization": "Bearer ${reader}"}
    current = {
        "path": "/system/user/current/info",
        "headers": {"Authorization": "Bearer ${signup}"},
        "status": 200,
        "equals": {"$.code": 0, "$.data.username": SIGNUP_USER, "$.data.is_superuser": False},
        "absent": ["$.data.password"],
    }
    persisted = {
        "path": "/rnd/device/detail/${persistent_device}",
        "headers": admin,
        "status": 200,
        "equals": {
            "$.code": 0,
            "$.data.name": "native-persist-${nonce}",
            "$.data.quantity": 7,
            "$.data.active": False,
        },
    }
    scenarios = [
        {
            "id": "native_signup",
            "title": "原生注册、真实验证码表单登录与重启会话",
            "requirements": refs,
            "steps": [
                {
                    "method": "POST",
                    "path": "/system/user/register",
                    "status": 200,
                    "body": {
                        "username": SIGNUP_USER,
                        "password": SIGNUP_PASSWORD,
                        "name": "Native security signup",
                    },
                    "equals": {
                        "$.code": 0,
                        "$.data.username": SIGNUP_USER,
                        "$.data.is_superuser": False,
                    },
                    "absent": ["$.data.password"],
                },
                *login_steps("signup", SIGNUP_USER, SIGNUP_PASSWORD),
                current,
            ],
            "after_restart": [current],
            "browser": native_browser_steps(),
        },
        {
            "id": "native_device_crud",
            "title": "原生设备增删改查、越权拒绝与物理库持久化",
            "requirements": refs,
            "steps": [
                *login_steps("admin", "super", "123456"),
                *login_steps("reader", SIGNUP_USER, SIGNUP_PASSWORD),
                {
                    "path": "/rnd/device/list",
                    "headers": reader,
                    "status": 403,
                    "equals": {"$.success": False},
                },
                {
                    "method": "POST",
                    "path": "/rnd/device/create",
                    "headers": admin,
                    "status": 200,
                    "body": {"name": "native-crud-${nonce}", "quantity": 0, "active": False},
                    "equals": {"$.code": 0, "$.data.quantity": 0, "$.data.active": False},
                    "captures": {"device": "$.data.id"},
                },
                {
                    "path": "/rnd/device/detail/${device}",
                    "headers": admin,
                    "status": 200,
                    "equals": {
                        "$.code": 0,
                        "$.data.name": "native-crud-${nonce}",
                        "$.data.quantity": 0,
                        "$.data.active": False,
                    },
                },
                {
                    "method": "PUT",
                    "path": "/rnd/device/update/${device}",
                    "headers": admin,
                    "status": 200,
                    "body": {"name": "native-updated-${nonce}", "quantity": 3, "active": True},
                    "equals": {"$.code": 0, "$.data.quantity": 3, "$.data.active": True},
                },
                {
                    "path": "/rnd/device/detail/${device}",
                    "headers": admin,
                    "status": 200,
                    "equals": {
                        "$.code": 0,
                        "$.data.name": "native-updated-${nonce}",
                        "$.data.quantity": 3,
                        "$.data.active": True,
                    },
                },
                {
                    "method": "DELETE",
                    "path": "/rnd/device/delete",
                    "headers": admin,
                    "status": 200,
                    "body": ["${device}"],
                    "equals": {"$.code": 0},
                },
                {
                    "path": "/rnd/device/list?name=native-updated-${nonce}",
                    "headers": admin,
                    "status": 200,
                    "equals": {"$.code": 0, "$.data.items": []},
                },
                {
                    "method": "POST",
                    "path": "/rnd/device/create",
                    "headers": admin,
                    "status": 200,
                    "body": {"name": "native-persist-${nonce}", "quantity": 7, "active": False},
                    "equals": {"$.code": 0},
                    "captures": {"persistent_device": "$.data.id"},
                },
                persisted,
                {
                    "method": "POST",
                    "path": "/rnd/device/create",
                    "headers": reader,
                    "status": 403,
                    "body": {"name": "native-denied-${nonce}", "quantity": 1, "active": True},
                    "equals": {"$.success": False},
                },
            ],
            "after_restart": [
                persisted,
                {
                    "path": "/rnd/device/list",
                    "headers": reader,
                    "status": 403,
                    "equals": {"$.success": False},
                },
            ],
        },
    ]
    return CapabilityPlan.model_validate(
        {
            "title": "Native FastapiAdmin security positive",
            "summary": GOAL,
            "source_digest": digest([GOAL]),
            "selection": selection(),
            "tasks": [
                {
                    "id": "native_accounts_devices",
                    "title": "原生身份与设备模块",
                    "requirements": refs,
                    "files": ["backend/app/plugin/module_rnd/device/controller.py"],
                    "contract": GOAL,
                    "scenarios": [row["id"] for row in scenarios],
                }
            ],
            "runtime": {
                "start": {
                    "cwd": "backend",
                    "argv": [
                        ".venv/bin/python",
                        "-m",
                        "uvicorn",
                        "app:create_app",
                        "--factory",
                        "--host",
                        "0.0.0.0",
                        "--port",
                        "8000",
                    ],
                },
                "port": 8000,
                "health_path": "/openapi.json",
                "startup_seconds": 120,
                "database_tables": ["sys_user", table],
            },
            "scenarios": scenarios,
        }
    )


def require_native_positive(proof, plan, source_digest, browser_image):
    require_profile_evidence(
        proof,
        aggregate=True,
        source_digest=source_digest,
        plan_digest=digest(plan.model_dump()),
        scenarios=plan.scenarios,
        selection=plan.selection.model_dump(),
        database_tables=plan.runtime.database_tables,
    )
    build = proof.get("native_build", {})
    restarted_checks = proof.get("restart_security_checks", {})
    if (
        proof.get("restart_kind") != "application_process"
        or not isinstance(restarted_checks, dict)
        or restarted_checks != proof.get("security_checks")
        or any(value is not True for value in restarted_checks.values())
        or proof.get("browser_image") != browser_image
        or not isinstance(build, dict)
        or set(build)
        != {"offline_install", "frontend_build", "frontend_typecheck", "source_frozen"}
        or any(value is not True for value in build.values())
        or proof.get("native_frontend_started") is not True
        or proof.get("native_frontend_restart") is not True
    ):
        raise ValueError("Native live build/browser/restart security evidence is incomplete")
    # Both actual account creation and business writes are required. The generic
    # verifier requires growth in at least one table, which is insufficient here.
    database = proof["database"]
    if any(
        database["after"][name] <= database["baseline"][name]
        for name in plan.runtime.database_tables
    ):
        raise ValueError("Native signup and device writes must both reach physical PostgreSQL")


def certify(product=PRODUCT, directory=HOME):
    product, directory = Path(product).resolve(), Path(directory).resolve()
    selected = selection()
    destination = inside(directory, receipt_name(selected))
    summary_path = ROOT / "reports/native-capability-security.json"
    detail_path = ROOT / "reports/native-capability-security-detail.json"
    summary = {
        "passed": False,
        "paid_model_calls": 0,
        "scope": "registered-native-security-and-fixed-positive",
        "browser_scope": "native-vue-login-registration-forms",
        "production_execution_enabled": False,
    }
    # Stale receipts must not survive an unsuccessful new certification attempt.
    write_json(destination, summary)
    write_json(summary_path, summary)
    install_loopback_guard()
    settings = Settings(
        _env_file=directory / ENVIRONMENT,
        capability_profile_directory=directory,
        capability_execution_enabled=False,
        tool_timeout=900,
    )
    client = None
    try:
        if settings.sandbox_provider != "daytona":
            raise ValueError("Native security certification requires real local Daytona")
        record = require_native_profile(
            directory, snapshot_for(settings, selected["template"], selected)
        )
        inventory = manifest(product)
        if record["inputs"]["product"] != str(product) or record["inputs"][
            "source_identity"
        ] != digest(inventory):
            raise ValueError(
                "Native certificate must test the exact registered preparation baseline"
            )
        plan = fixed_plan(product)
        validate_configuration(settings, selected["template"], selected)
        browser_image = require_browser_acceptance(settings.capability_browser_image)
        verifier = verifier_identity()
        client = client_for(settings)
        proof = _verify(
            product,
            plan,
            plan.scenarios,
            settings,
            selected,
            detail_path,
            client=client,
            aggregate=True,
            control_observer=lambda sandbox_id: inspect_created_sandbox(
                directory, sandbox_id, require_resources=True, selection=selected
            ),
            security_probe=security_probe_for_profile(directory, record),
        )
        summary["proof"] = settings.redact_data(proof)
        require_native_positive(proof, plan, digest(inventory), browser_image)
        acceptance = {
            "protocol": PROTOCOL,
            "passed": True,
            "verifier_identity": verifier,
            "profile": profile_binding(record),
            "selection": selected,
            "checks": proof["security_checks"],
            "positive_product": True,
            "cleanup": proof["cleanup"],
            "paid_model_calls": 0,
            "restart_kind": proof["restart_kind"],
            "browser_image": browser_image,
        }
        require_security_receipt(acceptance, record, browser_image=browser_image)
        closing_client = client
        client = None
        close_client(closing_client)
        # Revalidate after live work/transport cleanup and before publishing admission.
        if (
            require_native_profile(directory, record["snapshot"]["snapshot"]) != record
            or manifest(product) != inventory
        ):
            raise ValueError("Native profile/source changed during live certification")
        if require_browser_acceptance(settings.capability_browser_image) != browser_image:
            raise ValueError("Accepted isolated browser image changed during certification")
        require_security_receipt(acceptance, record, browser_image=browser_image)
        write_json(destination, acceptance)
        summary.update(acceptance)
        return acceptance
    finally:
        try:
            if client is not None:
                close_client(client)
        finally:
            write_json(summary_path, summary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=HOME)
    parser.add_argument("--product", type=Path, default=PRODUCT)
    args = parser.parse_args()
    certify(args.product, args.directory)
    print(
        "Native live security and fixed HTTP/Vue-form acceptance passed; production remains opt-in."
    )


if __name__ == "__main__":
    main()
