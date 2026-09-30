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
    report = json.loads((reports / "basic.json").read_text())
    if any(report.get(name) is not True for name in ("passed", "http", "restart")):
        raise ValueError("PostgreSQL product did not complete runtime verification")
    return {**report, "fresh_database": True}


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
