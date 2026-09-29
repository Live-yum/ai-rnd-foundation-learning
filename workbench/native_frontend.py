"""Build the original native application with any generated modules already mounted."""

import json
import os
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

from workbench.filesystem import atomic_text, sha, write_json
from workbench.native_vben import prepare_vben_source
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, run_command, stop_process


def frontend_environment(template, backend_url):
    common = {
        "CI": "true",
        "HUSKY": "0",
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "NODE_OPTIONS": "--max-old-space-size=4096 --dns-result-order=ipv4first",
    }
    if template == "fastapiadmin":
        return {
            **common,
            "VITE_APP_TITLE": "Native lab",
            "VITE_VERSION": "3.0.0",
            "VITE_PORT": "5173",
            "VITE_BASE_URL": "/",
            "VITE_APP_BASE_API": "/api/v1",
            "VITE_API_BASE_URL": backend_url,
            "VITE_API_TIMEOUT": "120000",
            "VITE_ACCESS_MODE": "mixed",
            "VITE_WITH_CREDENTIALS": "false",
            "VITE_LOCK_ENCRYPT_KEY": "native-lab-only",
        }
    if template != "yudao-vben":
        raise ValueError("Unknown native frontend")
    return {
        **common,
        "VITE_APP_TITLE": "Native lab",
        "VITE_APP_NAMESPACE": "native-lab-vben",
        # Bound Rust bundler parallelism; give the full Vben graph its native heap budget.
        "RAYON_NUM_THREADS": "2",
        "NODE_OPTIONS": "--max-old-space-size=8192 --dns-result-order=ipv4first",
        "VITE_APP_STORE_SECURE_KEY": "native-lab-only",
        "VITE_BASE": "/",
        "VITE_BASE_URL": backend_url,
        "VITE_GLOB_API_URL": "/admin-api",
        "VITE_NITRO_MOCK": "false",
        "VITE_APP_TENANT_ENABLE": "true",
        "VITE_APP_CAPTCHA_ENABLE": "false",
        "VITE_APP_API_ENCRYPT_ENABLE": "false",
        "VITE_APP_BAIDU_CODE": "",
        "VITE_ROUTER_HISTORY": "hash",
        "VITE_PWA": "false",
        "VITE_ARCHIVER": "false",
        "VITE_COMPRESS": "none",
        "VITE_UPLOAD_TYPE": "server",
    }


def frontend_app(template, root):
    root = Path(root).resolve()
    return root if template == "fastapiadmin" else root / "apps/web-antd"


def build_frontend(template, root, env, reports):
    root, reports = Path(root).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    app = frontend_app(template, root)
    if not (root / "pnpm-lock.yaml").is_file():
        raise ValueError("Native frontend lockfile is required")
    if template == "yudao-vben":
        prepare_vben_source(root, reports)
        # Vben's own loadAndConvertEnv / runtime-config plugin reads dotenv files,
        # not process.env. Persist only explicitly public VITE_* values in the
        # disposable workspace; never copy platform or database credentials.
        public = {key: value for key, value in env.items() if key.startswith("VITE_")}
        body = (
            "\n".join(f"{key}={json.dumps(value)}" for key, value in sorted(public.items())) + "\n"
        )
        atomic_text(app / ".env.production", body)
        atomic_text(app / ".env.production.example", body)
        write_json(reports / "frontend-public-config.json", public)
    # Native Vite plugins produce auto-imports/components declarations on first build.
    # Checking a pristine checkout before generating them yields false missing-name errors.
    # Type checking remains mandatory, AFTER deterministic generation; no errors are ignored.
    checks = [
        ("install", ["pnpm", "install", "--frozen-lockfile"], root),
        ("build", ["pnpm", "exec", "vite", "build", "--mode", "production"], app),
        ("typecheck", ["pnpm", "exec", "vue-tsc", "--noEmit", "--skipLibCheck"], app),
    ]
    evidence = []
    for name, command, cwd in checks:
        try:
            result = run_command(command, cwd, 900, env, heartbeat=f"native-frontend-{name}")
        except Exception as exc:
            atomic_text(reports / f"frontend-{name}.log", getattr(exc, "log", str(exc)))
            raise
        atomic_text(reports / f"frontend-{name}.log", result["log"])
        evidence.append({"name": name, "command": command, "returncode": 0})
    if not (app / "dist/index.html").is_file():
        raise ValueError("Frontend build did not produce dist/index.html")
    write_json(
        reports / "frontend-build.json",
        {
            "checks": evidence,
            "lock_sha256": sha(root / "pnpm-lock.yaml"),
            "scope": "native-application",
        },
    )


@contextmanager
def frontend_preview(template, root, env, reports):
    app, reports = frontend_app(template, root), Path(reports).resolve()
    url = "http://127.0.0.1:5173"
    command = [
        "pnpm",
        "exec",
        "vite",
        "preview",
        "--host",
        "127.0.0.1",
        "--port",
        "5173",
        "--strictPort",
    ]
    log = (reports / "frontend-runtime.log").open("ab")
    process = subprocess.Popen(
        command,
        cwd=app,
        env=clean_env(env),
        stdout=log,
        stderr=subprocess.STDOUT,
        **process_options(),
    )
    try:
        with httpx.Client(trust_env=False, timeout=3) as client:
            for _ in range(60):
                if process.poll() is not None:
                    raise RuntimeError("Frontend preview exited")
                try:
                    response = client.get(url)
                    if response.status_code == 200 and "<html" in response.text.lower():
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(1)
            else:
                raise TimeoutError("Frontend preview never became ready")
        yield url
    finally:
        stop_process(process)
        log.close()


def browser_check(template, url, reports):
    executable = ROOT / "scripts/native_browser.cjs"
    playwright_module = ROOT / ".native/browser/node_modules/playwright"
    if not playwright_module.exists():
        raise ValueError("Install the pinned Playwright tooling described in the handbook")
    result = run_command(
        [
            "node",
            str(executable),
            template,
            url,
            str(Path(reports).resolve()),
            str(playwright_module),
        ],
        ROOT,
        180,
        {
            "NODE_OPTIONS": "--dns-result-order=ipv4first",
            "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
        },
    )
    atomic_text(Path(reports) / "browser.log", result["log"])
