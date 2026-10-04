# scripts/ci_native_capability_security.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.ci_native_capability_security；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_security_probe`、`scripts.ci_capability_profile`、`scripts.daytona_capability_profile`、`scripts.daytona_native_capability_profile`、`workbench.capability_browser_isolation`、`workbench.capability_contracts`、`workbench.capability_execution`、`workbench.capability_sandbox`、`workbench.domain`、`workbench.filesystem`、`workbench.local_only`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `baseline_table`（L47–L85）：接收`product`。 源码说明：Read data contracts only; do not import generated deployment code.。 控制顺序：L50按`path.stat().st_size > 1_000_000`分支；L51抛异常，停止当前正常路径；L53按`metadata.get("template") != "fastapiadmin" or metadata.get("format") != 1 or metadata…`分支；L60抛异常，停止当前正常路径；L64按`len(entities) != 1 or len(targets) != 1`分支；L65抛异常，停止当前正常路径；L67按`[(field.name, field.kind) for field in entities[0].fields] != DEVICE_FIELDS or target…`分支；L77抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`inside`、`path.stat`、`ValueError`、`json.loads`、`path.read_text`、`metadata.get`、`digest`、`Plan.model_validate`、`target.get`等。 返回路径：L85的`target["table"]`。
- `login_steps`（L88–L118）：接收`actor`、`username`、`password`。 返回路径：L89的`[ { "path": "/system/auth/captcha/get", "status": 200, "equals": {"$.code": 0, "$.data.ena…`。
- `native_browser_steps`（L121–L145）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L124的`[ {"action": "open", "value": "/#/login"}, {"action": "visible", "selector": ".login-page-…`。
- `fixed_plan`（L148–L333）：接收`product`。 调用`baseline_table`、`scope_sources`、`login_steps`、`native_browser_steps`、`CapabilityPlan.model_validate`、`digest`、`selection`。 返回路径：L295的`CapabilityPlan.model_validate( { "title": "Native FastapiAdmin security positive", "summar…`。
- `require_native_positive`（L336–L374）：接收`proof`、`plan`、`source_digest`、`browser_image`。 控制顺序：L348按`proof.get("restart_kind") != "application_process" or not isinstance(restarted_checks…`分支；L366抛异常，停止当前正常路径；L370按`any( database["after"][name] <= database["baseline"][name] for name in plan.runtime.d…`分支；L374抛异常，停止当前正常路径。 调用`require_profile_evidence`、`digest`、`plan.model_dump`、`plan.selection.model_dump`、`proof.get`、`isinstance`、`any`、`restarted_checks.values`、`set`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `certify`（L377–L472）：接收`product`、`directory`。 控制顺序：L402按`settings.sandbox_provider != "daytona"`分支；L403抛异常，停止当前正常路径；L408按`record["inputs"]["product"] != str(product) or record["inputs"][ "source_identity" ] …`分支；L411抛异常，停止当前正常路径；L456按`require_native_profile(directory, record["snapshot"]["snapshot"]) != record or manife…`分支；L460抛异常，停止当前正常路径；L461按`require_browser_acceptance(settings.capability_browser_image) != browser_image`分支；L462抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path(product).resolve`、`Path`、`Path(directory).resolve`、`selection`、`inside`、`receipt_name`、`write_json`、`install_loopback_guard`、`Settings`等。 返回路径：L466的`acceptance`。
- `main`（L475–L483）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`certify`、`print`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_capability_security.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L487。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19798`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_capability_security.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6ec3dcd45efa4f0439447b6736a340610801f6a39a445caf8b709dd2e81ccdc6"} -->
````python
# scripts/ci_native_capability_security.py
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
        != {
            "preinstalled_dependencies_verified",
            "frontend_build",
            "frontend_typecheck",
            "source_frozen",
        }
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
            profile_record=record,
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
            "preinstalled_dependencies": proof["preinstalled_dependencies"],
            "positive_source_digest": proof["source_digest"],
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
````
