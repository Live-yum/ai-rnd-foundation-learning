# scripts/daytona_matrix_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：沙箱内独立数据库和产品验收。** 在沙箱内创建自有PG/Redis，离线安装/构建并通过独立启动器运行产品，执行HTTP、权限、浏览器及重启；检查服务退出后生成严格报告。

**对应关系：** sandbox固定命令 → 本脚本 → 当前profile的运行证据；不复用主机库。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.daytona_profiles`、`workbench.domain`、`workbench.filesystem`、`workbench.native_acceptance`、`workbench.native_business_checks`、`workbench.native_environment`、`workbench.owned_lifecycle`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `redact`（L38–L41）：接收`value`。 控制顺序：L39遍历`PROBE_SECRETS`。 调用`value.replace`。 返回路径：L41的`value`。
- `local_services`（L45–L141）：接收`directory`。 源码说明：Never contacts or changes a host database. Files and processes are owned by this probe.。 控制顺序：L111遍历`range(60)`；L112按`any(p.poll() is not None for p in processes)`分支；L113抛异常，停止当前正常路径；L117按`run_command(["redis-cli", "-h", "127.0.0.1", "ping"], directory, 5)[ "log" ].strip() …`分支；L125按`attempt == 59`分支；L126抛异常，停止当前正常路径；L136遍历`reversed(processes)`；L140按`any(process.poll() is None for process in processes)`分支。后续分支沿下方源码相同行号继续阅读。 调用`directory.mkdir`、`secrets.token_hex`、`PROBE_SECRETS.append`、`pwfile.write_text`、`pwfile.chmod`、`run_command`、`str`、`(directory / "services.log").open`、`processes.append`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `local_services.create`（L129–L132）：接收`name`。 调用`psycopg.connect`、`c.execute`、`sql.SQL("CREATE DATABASE {}").format`、`sql.SQL`、`sql.Identifier`。 返回路径：L132的`f"postgresql+psycopg://rnd:{password}@127.0.0.1:5432/{name}"`。
- `native_process`（L145–L185）：接收`product`、`url`、`template`、`reports`。 控制顺序：L165遍历`range(360)`；L166按`process.poll() is not None`分支；L167抛异常，停止当前正常路径；L173按`api.status_code == 200 and front.status_code == 200`分支；L177按`attempt == 359`分支；L178抛异常，停止当前正常路径。 调用`clean_env`、`(reports / "launcher.log").open`、`subprocess.Popen`、`str`、`process_options`、`httpx.Client`、`range`、`process.poll`、`RuntimeError`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `native_probe`（L188–L300）：接收`template`、`product`、`create`、`reports`。 控制顺序：L190按`metadata["template"] != template`分支；L191抛异常，停止当前正常路径；L194遍历`zip(targets, plan.entities, strict=True)`；L198按`rule`分支；L219按`restored.get("passed") is not True or restored.get("frontend_started") is not True`分支；L220抛异常，停止当前正常路径；L221按`plan.business`分支；L226按`business.get("passed") is not True or browser.get("passed") is not True or browser.ge…`分支。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`(product / "deployment/manifest.json").read_text`、`ValueError`、`Plan.model_validate`、`zip`、`field.model_dump`、`target.pop`、`next`、`wire`等。 返回路径：L243的`{ "http": True, "restart": True, "fresh_database": True, "frontend_build": True, "frontend…`；L285的`{ "http": True, "restart": persistence["process_restart_preserves_records"], "fresh_databa…`。
- `basic_runtime_evidence`（L303–L317）：接收`report`、`database`。 控制顺序：L304按`database not in {"sqlite", "postgresql"}`分支；L305抛异常，停止当前正常路径；L306按`any(report.get(name) is not True for name in ("passed", "http", "restart"))`分支；L307抛异常，停止当前正常路径；L308按`report.get("database") != "real-isolated-" + database`分支；L309抛异常，停止当前正常路径。 调用`ValueError`、`any`、`report.get`。 返回路径：L312的`{ **report, "runtime_database": report["database"], "database": database, "fresh_database"…`。
- `basic_probe`（L320–L350）：接收`product`、`create`、`reports`、`database`。 调用`run_command`、`create`、`environment.update`、`str`、`json.loads`、`(reports / "basic.json").read_text`、`basic_runtime_evidence`。 返回路径：L350的`basic_runtime_evidence(report, database)`。
- `main`（L353–L412）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L368按`profile != expected`分支；L369抛异常，停止当前正常路径；L372按`os.environ.get("RND_OFFLINE_TOOLS") != "1"`分支；L373抛异常，停止当前正常路径；L400抛异常，停止当前正常路径。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`Path.cwd().resolve`、`Path.cwd`、`manifest`、`json.loads`、`Path("/opt/rnd/profile.json").read_text`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_matrix_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L416。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`14972`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_matrix_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "50873105d27d0a920c0e3a373c7b43cee0a64ba92f0e51a49db8932fe70f8e20"} -->
````python
# scripts/daytona_matrix_probe.py
"""Trusted verifier inside a no-egress sandbox, not the application's startup dependency.

This process owns a new PostgreSQL cluster and Redis instance INSIDE the sandbox.
The independent native launcher runs in another process with its own dependencies.
"""

import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx
import psycopg
from psycopg import sql

from workbench.daytona_profiles import dependency_identity
from workbench.domain import Plan, digest
from workbench.filesystem import manifest, write_json
from workbench.native_acceptance import (
    check_generated_persistence,
    generated_crud,
    generated_permissions,
)
from workbench.native_business_checks import check_business_examples, wire
from workbench.native_environment import login
from workbench.owned_lifecycle import stop_native
from workbench.tools import clean_env, process_options, run_command, stop_process

ROOT = Path(__file__).resolve().parents[1]
PROBE_SECRETS = []


def redact(value):
    for secret in PROBE_SECRETS:
        value = value.replace(secret, "[redacted-local-sandbox-secret]")
    return value


@contextmanager
def local_services(directory):
    """Never contacts or changes a host database. Files and processes are owned by this probe."""
    directory.mkdir(mode=0o700)
    password = secrets.token_hex(24)
    PROBE_SECRETS.append(password)
    pwfile = directory / "password"
    pwfile.write_text(password)
    pwfile.chmod(0o600)
    cluster = directory / "postgres"
    run_command(
        [
            "initdb",
            "-D",
            str(cluster),
            "--username=rnd",
            "--auth-host=scram-sha-256",
            "--auth-local=trust",
            "--pwfile=" + str(pwfile),
            "--no-locale",
            "--encoding=UTF8",
        ],
        directory,
        90,
    )
    log = (directory / "services.log").open("ab")
    processes = []
    try:
        processes.append(
            subprocess.Popen(
                [
                    "postgres",
                    "-D",
                    str(cluster),
                    "-h",
                    "127.0.0.1",
                    "-p",
                    "5432",
                    "-k",
                    str(directory),
                ],
                stdout=log,
                stderr=log,
                env=clean_env(),
                **process_options(),
            )
        )
        processes.append(
            subprocess.Popen(
                [
                    "redis-server",
                    "--bind",
                    "127.0.0.1",
                    "--port",
                    "6379",
                    "--save",
                    "",
                    "--appendonly",
                    "no",
                ],
                stdout=log,
                stderr=log,
                env=clean_env(),
                **process_options(),
            )
        )
        url = f"postgresql://rnd:{password}@127.0.0.1:5432/postgres"
        for attempt in range(60):
            if any(p.poll() is not None for p in processes):
                raise RuntimeError("Sandbox database/Redis process exited")
            try:
                with psycopg.connect(url, connect_timeout=1) as connection:
                    connection.execute("SELECT 1")
                if (
                    run_command(["redis-cli", "-h", "127.0.0.1", "ping"], directory, 5)[
                        "log"
                    ].strip()
                    == "PONG"
                ):
                    break
            except psycopg.Error, RuntimeError:
                if attempt == 59:
                    raise
                time.sleep(0.5)

        def create(name):
            with psycopg.connect(url, autocommit=True) as c:
                c.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
            return f"postgresql+psycopg://rnd:{password}@127.0.0.1:5432/{name}"

        yield create
    finally:
        for process in reversed(processes):
            stop_process(process)
        log.close()
        pwfile.unlink(missing_ok=True)
        if any(process.poll() is None for process in processes):
            raise RuntimeError("Sandbox service cleanup failed")


@contextmanager
def native_process(product, url, template, reports):
    base = "http://127.0.0.1:" + ("8001" if template == "fastapiadmin" else "48080")
    env = clean_env(
        {
            "NATIVE_DELIVERY_DATABASE_URL": url,
            "NATIVE_DELIVERY_REDIS_PORT": "6379",
            "NATIVE_DELIVERY_REDIS_DB": "8",
        }
    )
    log = (reports / "launcher.log").open("ab")
    process = subprocess.Popen(
        [sys.executable, str(product / "start.py"), "--skip-build"],
        cwd=product,
        env=env,
        stdout=log,
        stderr=log,
        **process_options(),
    )
    try:
        with httpx.Client(trust_env=False, timeout=2) as client:
            for attempt in range(360):
                if process.poll() is not None:
                    raise RuntimeError("Standalone native launcher exited")
                try:
                    api = client.get(
                        base + ("/openapi.json" if template == "fastapiadmin" else "/v3/api-docs")
                    )
                    front = client.get("http://127.0.0.1:5173/")
                    if api.status_code == 200 and front.status_code == 200:
                        break
                except httpx.HTTPError:
                    pass
                if attempt == 359:
                    raise TimeoutError("Standalone native frontend/backend not ready")
                time.sleep(0.5)
        yield base
    finally:
        try:
            stop_native(process, [8001 if template == "fastapiadmin" else 48080, 5173])
        finally:
            log.close()


def native_probe(template, product, create, reports):
    metadata = json.loads((product / "deployment/manifest.json").read_text())
    if metadata["template"] != template:
        raise ValueError("Native product template mismatch")
    plan = Plan.model_validate(metadata["plan"])
    targets = metadata["targets"]
    for target, entity in zip(targets, plan.entities, strict=True):
        target["fields"] = [field.model_dump() for field in entity.fields]
        target.pop("sample", None)
        rule = next((rule for rule in plan.custom_rules if rule.entity == entity.name), None)
        if rule:
            target["business_rule"] = {
                "accept": wire(template, rule.accept_examples[0]),
                "reject": wire(template, rule.reject_examples[0]),
            }
    url = create("sandbox_delivery_codegen")
    environment = {
        "NATIVE_DELIVERY_DATABASE_URL": url,
        "NATIVE_DELIVERY_REDIS_PORT": "6379",
        "NATIVE_DELIVERY_REDIS_DB": "8",
        "PRODUCT_VERIFY_PLAYWRIGHT": "/opt/rnd/browser/node_modules/playwright",
        "PLAYWRIGHT_BROWSERS_PATH": "/opt/rnd/browsers",
    }
    run_command(
        [sys.executable, str(product / "start.py"), "--check"],
        product,
        2400,
        environment,
        heartbeat="Daytona-standalone-install",
    )
    restored = json.loads((product / ".deployment/reports/portable-start.json").read_text())
    if restored.get("passed") is not True or restored.get("frontend_started") is not True:
        raise ValueError("Daytona standalone restore did not reach both servers")
    if plan.business:
        from workbench.business_probe import BusinessClient

        business = restored.get("business") or {}
        browser = restored.get("browser") or {}
        if (
            business.get("passed") is not True
            or browser.get("passed") is not True
            or browser.get("errors") != []
        ):
            raise ValueError(
                "Customer sandbox lacks complete independent business/browser evidence"
            )
        with native_process(product, url, template, reports) as base:
            client = BusinessClient(template, base, login(template, base), targets)
            try:
                for entity, identity in business["records"].items():
                    assert any(str(row["id"]) == identity for row in client.rows(entity)), (
                        "Business data lost on sandbox restart"
                    )
            finally:
                client.close()
        return {
            "http": True,
            "restart": True,
            "fresh_database": True,
            "frontend_build": True,
            "frontend_typecheck": True,
            "browser": True,
            "permissions": True,
            "standalone_launcher": True,
            "business_rules": True,
            "native_business": business,
            "browser_report": browser,
            "original_platform_imported_by_product": False,
        }
    with native_process(product, url, template, reports) as base:
        token = login(template, base)
        records = generated_crud(template, base, token, targets, plan)
        permissions = generated_permissions(template, base, token, targets, plan)
        business = check_business_examples(template, base, token, targets, plan)
        write_json(reports / "browser-targets.json", targets)
        run_command(
            [
                "node",
                str(ROOT / "scripts/native_browser.cjs"),
                template,
                "http://127.0.0.1:5173",
                str(reports),
                "/opt/rnd/browser/node_modules/playwright",
                str(reports / "browser-targets.json"),
            ],
            ROOT,
            300,
            {"PLAYWRIGHT_BROWSERS_PATH": "/opt/rnd/browsers"},
            heartbeat="Daytona-native-browser",
        )
        browser = json.loads((reports / "browser.json").read_text())
        if browser.get("passed") is not True:
            raise ValueError("Real native browser acceptance failed")
    with native_process(product, url, template, reports) as base:
        persistence = check_generated_persistence(
            template, base, login(template, base), targets, records
        )
    return {
        "http": True,
        "restart": persistence["process_restart_preserves_records"],
        "fresh_database": True,
        "frontend_build": True,
        "frontend_typecheck": True,
        "browser": True,
        "permissions": True,
        "standalone_launcher": True,
        "business_rules": business["passed"],
        "native_records": records,
        "native_permissions": permissions,
        "native_business": business,
        "browser_report": browser,
        "original_platform_imported_by_product": False,
    }


def basic_runtime_evidence(report, database):
    if database not in {"sqlite", "postgresql"}:
        raise ValueError("Unregistered Python database")
    if any(report.get(name) is not True for name in ("passed", "http", "restart")):
        raise ValueError("Python product did not complete runtime verification")
    if report.get("database") != "real-isolated-" + database:
        raise ValueError("Python runtime database evidence does not match selected database")
    # The generic verifier describes its actual isolation mode. The matrix
    # envelope reserves database for the registered sqlite/postgresql identity.
    return {
        **report,
        "runtime_database": report["database"],
        "database": database,
        "fresh_database": True,
    }


def basic_probe(product, create, reports, database):
    extras = ["--extra", "postgres"] if database == "postgresql" else []
    run_command(
        ["uv", "sync", "--locked", "--offline", "--no-dev", "--python", "3.14", *extras],
        product,
        180,
    )
    environment = (
        {"VERIFY_DATABASE_URL": create("sandbox_basic_codegen")} if database == "postgresql" else {}
    )
    environment.update(
        PRODUCT_VERIFY_PLAYWRIGHT="/opt/rnd/browser/node_modules/playwright",
        PLAYWRIGHT_BROWSERS_PATH="/opt/rnd/browsers",
    )
    run_command(
        [
            sys.executable,
            str(ROOT / "templates/product/verify.py"),
            "--product",
            str(product),
            "--python",
            str(product / ".venv/bin/python"),
            "--report",
            str(reports / "basic.json"),
        ],
        ROOT,
        300,
        environment,
    )
    report = json.loads((reports / "basic.json").read_text(encoding="utf-8"))
    return basic_runtime_evidence(report, database)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--template", required=True, choices=["python-basic", "fastapiadmin", "yudao-vben"]
    )
    parser.add_argument("--database", required=True, choices=["sqlite", "postgresql"])
    args = parser.parse_args()
    product = Path.cwd().resolve()
    before = manifest(product)
    profile = json.loads(Path("/opt/rnd/profile.json").read_text())
    expected = {
        "template": args.template,
        "database": args.database,
        "dependency_identity": dependency_identity(product),
    }
    if profile != expected:
        raise ValueError(
            "Snapshot profile/locks do not match the selected product; explicitly prepare the correct local snapshot"
        )
    if os.environ.get("RND_OFFLINE_TOOLS") != "1":
        raise ValueError("Offline sandbox policy is required")
    report = {
        "passed": False,
        "template": args.template,
        "database": args.database,
        "source_digest": digest(before),
        "host_database_used": False,
        "host_credentials_used": False,
        "offline": True,
        "locked_install": True,
        "services_stopped": False,
    }
    reports = product.parent / "probe-evidence"
    reports.mkdir()
    try:
        with local_services(product.parent / "owned-services") as create:
            details = (
                basic_probe(product, create, reports, args.database)
                if args.template == "python-basic"
                else native_probe(args.template, product, create, reports)
            )
            report.update(details)
        report.update(passed=True, services_stopped=True)
    except Exception as exc:
        detail = redact(str(exc) + "\n" + getattr(exc, "log", ""))[-12000:]
        report.update(error_type=type(exc).__name__, error=detail)
        print(detail, file=sys.stderr)
        raise RuntimeError("Independent sandbox runtime failed") from None
    finally:
        write_json(product.parent / "runtime.json", json.loads(redact(json.dumps(report))))
    print(
        json.dumps(
            {
                "passed": True,
                "template": args.template,
                "database": args.database,
                "services_stopped": True,
            }
        )
    )


if __name__ == "__main__":
    main()
````
