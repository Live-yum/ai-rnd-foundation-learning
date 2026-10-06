"""Run real migrations and HTTP checks against an isolated product database.

Usage: uv run python verify.py [--product PATH] [--python EXECUTABLE] [--report PATH]
This file is reviewed test code, never authored or modified by the coding model.
"""

import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Annotated

import httpx
from fields import integer_bounds
from pydantic import Field, TypeAdapter, ValidationError


class CheckFailed(RuntimeError):
    pass


class BrowserPrerequisite(CheckFailed):
    pass


def need(condition, message):
    if not condition:
        raise CheckFailed(message)


def stop(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            capture_output=True,
            timeout=15,
            check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=15)


def verify(product, python=sys.executable, business_screenshots=None):
    product = Path(product).resolve()
    spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
    if spec.get("business"):
        from verify_business import verify_business

        return verify_business(product, python, stop, BrowserPrerequisite, business_screenshots)
    checks = []
    suffix = uuid.uuid4().hex[:10]
    browser_report = {"applicable": False, "reason": "api-only frontend"}
    with tempfile.TemporaryDirectory(prefix="product-verify-") as directory:
        env = {
            k: v
            for k, v in os.environ.items()
            if k.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "TEMP", "TMP"}
        }
        selection = json.loads((product / "selection.json").read_text(encoding="utf-8"))
        if selection["database"] == "postgresql":
            target = os.environ.get("VERIFY_DATABASE_URL")
            need(
                bool(target),
                "Selected PostgreSQL requires an isolated PostgreSQL verification database",
            )
            env["PRODUCT_DATABASE_URL"] = target
        env.update(
            PRODUCT_DATA_DIR=directory,
            HOME=directory,
            USERPROFILE=directory,
            PYTHONUTF8="1",
            PYTHONIOENCODING="utf-8",
            PYTHONDONTWRITEBYTECODE="1",
        )
        migrated = subprocess.run(
            [python, "manage.py", "init"],
            cwd=product,
            env=env,
            capture_output=True,
            timeout=60,
            check=False,
        )
        need(migrated.returncode == 0, "product migration failed")
        checks.append("migration")

        def start_server():
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            options = (
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                if os.name == "nt"
                else {"start_new_session": True}
            )
            process = subprocess.Popen(
                [
                    python,
                    "-m",
                    "uvicorn",
                    "app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--no-access-log",
                ],
                cwd=product,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                **options,
            )
            client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10, trust_env=False)
            for _ in range(150):
                if process.poll() is not None:
                    client.close()
                    raise CheckFailed("product server exited before health check")
                try:
                    if client.get("/health").status_code == 200:
                        return process, client
                except httpx.HTTPError:
                    pass
                time.sleep(0.1)
            stop(process)
            client.close()
            raise CheckFailed("product server did not become healthy")

        process, client = start_server()
        saved = []
        try:
            need(client.get("/openapi.json").status_code == 200, "OpenAPI unavailable")
            checks.extend(["http_start", "openapi"])
            home = client.get("/")
            need(home.status_code == 200, "selected frontend unavailable")
            if selection["frontend"] == "simple-admin":
                need(
                    '<form id="filters">' in home.text,
                    "missing generated search frontend",
                )
                need(
                    client.get("/web/app.js").status_code == 200,
                    "frontend asset unavailable",
                )
                checks.append("generated_frontend_assets")
            password = "Test-only-strong-password-314"
            a = client.post("/auth/register", json={"username": "a" + suffix, "password": password})
            b = client.post("/auth/register", json={"username": "b" + suffix, "password": password})
            need(a.status_code == 201 and b.status_code == 201, "registration failed")
            need(
                client.post(
                    "/auth/login",
                    json={"username": "a" + suffix, "password": "incorrect-password"},
                ).status_code
                == 401,
                "invalid password was accepted",
            )
            login = client.post(
                "/auth/login", json={"username": "a" + suffix, "password": password}
            )
            need(login.status_code == 200, "login failed")
            auth_a = {"Authorization": "Bearer " + login.json()["access_token"]}
            auth_b = {"Authorization": "Bearer " + b.json()["access_token"]}
            need(
                client.get("/api/users", headers=auth_a).status_code == 404,
                "system table exposed",
            )
            checks.append("authentication")
            for entity in spec["entities"]:
                name = entity["name"]
                path = "/api/" + name
                sample = {
                    f["name"]: {
                        "text": f.get("example")
                        if f.get("example") is not None
                        else "x" * max(1, f.get("min_length", 0)),
                        "integer": max(integer_bounds(f)[0], min(1, integer_bounds(f)[1])),
                        "boolean": True,
                        "date": "2026-01-15",
                        "datetime": "2026-01-15T00:00:34.123456Z",
                        "enum": (f.get("choices") or ["sample"])[0],
                    }[f["kind"]]
                    for f in entity["fields"]
                }
                rules = [r for r in spec.get("custom_rules", []) if r["entity"] == name]
                if rules:
                    sample = dict(rules[0]["accept_examples"][0])
                need(client.get(path).status_code in {401, 403}, "anonymous read allowed")
                response = client.post(path, headers=auth_a, json=sample)
                need(response.status_code == 201, f"create failed: {name}")
                item = response.json()
                detail = path + "/" + item["id"]
                need(
                    client.get(detail, headers=auth_a).status_code == 200,
                    "owner read failed",
                )
                need(
                    client.get(path, headers=auth_b).json() == [],
                    "cross-user list leaked data",
                )
                for method in ("GET", "PUT", "DELETE"):
                    kwargs = {"json": sample} if method == "PUT" else {}
                    need(
                        client.request(method, detail, headers=auth_b, **kwargs).status_code == 404,
                        "cross-user record access allowed",
                    )
                need(
                    client.post(
                        path, headers=auth_a, json={**sample, "owner_id": "forged"}
                    ).status_code
                    == 422,
                    "forged ownership field accepted",
                )
                for f in entity["fields"]:
                    invalid = {
                        **sample,
                        f["name"]: {
                            "text": 123,
                            "integer": True,
                            "boolean": "yes",
                            "date": "2026/01/15",
                            "datetime": "2026-01-15T00:00:00",
                            "enum": "__invalid_choice__",
                        }[f["kind"]],
                    }
                    need(
                        client.post(path, headers=auth_a, json=invalid).status_code == 422,
                        "wrong field type accepted",
                    )
                    if f["required"]:
                        missing = {k: v for k, v in sample.items() if k != f["name"]}
                        need(
                            client.post(path, headers=auth_a, json=missing).status_code == 422,
                            "missing field accepted",
                        )
                    if f["kind"] == "integer":
                        low, high = integer_bounds(f)
                        for invalid in (low - 1, high + 1):
                            for target, method in ((path, "POST"), (detail, "PUT")):
                                need(
                                    client.request(
                                        method,
                                        target,
                                        headers=auth_a,
                                        json={**sample, f["name"]: invalid},
                                    ).status_code
                                    == 422,
                                    "approved integer boundary accepted invalid input",
                                )
                        checks.append(f"integer-boundaries:{name}.{f['name']}")
                    if f["kind"] == "text":
                        need(
                            client.post(
                                path,
                                headers=auth_a,
                                json={**sample, f["name"]: "x" * (f["max_length"] + 1)},
                            ).status_code
                            == 422,
                            "overlong field accepted",
                        )
                        if f.get("pattern") is not None:
                            validator = TypeAdapter(Annotated[str, Field(pattern=f["pattern"])])
                            for invalid in (
                                "__invalid_pattern__",
                                "!",
                                str(sample[f["name"]])[::-1],
                            ):
                                try:
                                    validator.validate_python(invalid)
                                except ValidationError:
                                    need(
                                        client.post(
                                            path,
                                            headers=auth_a,
                                            json={**sample, f["name"]: invalid},
                                        ).status_code
                                        == 422,
                                        "text violates approved pattern but was accepted",
                                    )
                need(
                    client.put(detail, headers=auth_a, json=sample).status_code == 200,
                    "update failed",
                )
                for rule in rules:
                    for candidate in rule["accept_examples"]:
                        need(
                            client.post(path, headers=auth_a, json=candidate).status_code == 201,
                            "approved positive rule example rejected",
                        )
                    for candidate in rule["reject_examples"]:
                        need(
                            client.post(path, headers=auth_a, json=candidate).status_code == 422,
                            "approved negative rule example accepted",
                        )
                for field in entity["fields"]:
                    value = sample.get(field["name"])
                    if value is None:
                        continue
                    if field.get("searchable"):
                        found = client.get(path, headers=auth_a, params={"q": str(value)})
                        need(
                            found.status_code == 200
                            and any(row["id"] == item["id"] for row in found.json()),
                            "configured search failed",
                        )
                        need(
                            client.get(path, headers=auth_b, params={"q": str(value)}).json() == [],
                            "search bypassed ownership",
                        )
                        checks.append("search:" + field["name"])
                    if field.get("filterable"):
                        wire = str(value).lower() if type(value) is bool else str(value)
                        found = client.get(
                            path,
                            headers=auth_a,
                            params={"filter_" + field["name"]: wire},
                        )
                        need(
                            found.status_code == 200
                            and any(row["id"] == item["id"] for row in found.json()),
                            "configured exact filter failed",
                        )
                        checks.append("filter:" + field["name"])
                    if field.get("date_range"):
                        found = client.get(
                            path,
                            headers=auth_a,
                            params={
                                "from_" + field["name"]: value,
                                "to_" + field["name"]: value,
                            },
                        )
                        need(
                            found.status_code == 200
                            and any(row["id"] == item["id"] for row in found.json()),
                            "inclusive date boundary failed",
                        )
                        bad = client.post(
                            path,
                            headers=auth_a,
                            json={**sample, field["name"]: "2026-02-30"},
                        )
                        need(bad.status_code == 422, "invalid calendar date accepted")
                        checks.append("inclusive-date-range:" + field["name"])
                saved.append(detail)
                checks.extend([f"crud:{name}", f"isolation:{name}", f"types:{name}"])
                if rules:
                    checks.append(f"business_rules:{name}")
            if selection["frontend"] == "simple-admin":
                module = Path(
                    os.environ.get(
                        "PRODUCT_VERIFY_PLAYWRIGHT",
                        product / ".native/browser/node_modules/playwright",
                    )
                ).resolve()
                if not shutil.which("node") or not module.is_dir():
                    raise BrowserPrerequisite(
                        "Real browser acceptance requires Node and pinned Playwright/Chromium"
                    )
                config = Path(directory) / "browser-input.json"
                output = Path(directory) / "browser-result.json"
                config.write_text(
                    json.dumps({"url": str(client.base_url), "spec": spec}),
                    encoding="utf-8",
                )
                browser_env = dict(env)
                browser_env["PLAYWRIGHT_BROWSERS_PATH"] = os.environ.get(
                    "PLAYWRIGHT_BROWSERS_PATH", "0"
                )
                browser_run = subprocess.run(
                    [
                        shutil.which("node"),
                        str(Path(__file__).with_name("verify-browser.cjs")),
                        str(config),
                        str(module),
                        str(output),
                    ],
                    cwd=product,
                    env=browser_env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=300,
                    check=False,
                )
                if browser_run.returncode and any(
                    text in browser_run.stderr
                    for text in (
                        "Executable doesn't exist",
                        "Host system is missing dependencies",
                        "Cannot find module",
                    )
                ):
                    raise BrowserPrerequisite(
                        "Pinned Chromium/Playwright is not installed or usable"
                    )
                need(
                    browser_run.returncode == 0,
                    "Real browser acceptance failed: " + browser_run.stderr[-2000:],
                )
                need(output.is_file(), "Browser acceptance did not produce evidence")
                browser_report = json.loads(output.read_text(encoding="utf-8"))
                need(
                    browser_report.get("passed") is True
                    and browser_report.get("real_browser") is True
                    and browser_report.get("entities") == [e["name"] for e in spec["entities"]],
                    "Incomplete browser evidence",
                )
                browser_report["applicable"] = True
                checks.append("real-browser-spec-driven")
        finally:
            client.close()
            stop(process)
        process, client = start_server()
        try:
            for detail in saved:
                need(
                    client.get(detail, headers=auth_a).status_code == 200,
                    "data or login lost after process restart",
                )
                need(
                    client.delete(detail, headers=auth_a).status_code == 204,
                    "delete failed",
                )
                need(
                    client.get(detail, headers=auth_a).status_code == 404,
                    "deleted record still visible",
                )
            checks.append("process_restart_persistence")
        finally:
            client.close()
            stop(process)
    return {
        "passed": True,
        "checks": checks,
        "entities": len(spec["entities"]),
        "http": True,
        "database": "real-isolated-" + selection["database"],
        "restart": True,
        "browser": browser_report,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--business-screenshots",
        type=Path,
        help="Optional new empty output directory for synthetic business PNG evidence",
    )
    args = parser.parse_args()
    try:
        result = verify(args.product, args.python, args.business_screenshots)
    except (
        CheckFailed,
        httpx.HTTPError,
        subprocess.SubprocessError,
        OSError,
        ValueError,
    ) as exc:
        result = {
            "passed": False,
            "error": type(exc).__name__,
            "message": str(exc)[:2500],
            "kind": "environment" if isinstance(exc, BrowserPrerequisite) else "code",
        }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
