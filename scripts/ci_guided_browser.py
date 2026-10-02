"""Real local HTTP and Chromium regression; model servers are explicit test fixtures only."""

import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import httpx
import uvicorn

from scripts.news_fixture import (
    ORIGINAL_REQUEST,
    assert_approved,
    assert_resolution,
    news_requirement,
    news_spec,
)
from workbench.api import create_app
from workbench.filesystem import unpack, write_json
from workbench.settings import ROOT, Settings
from workbench.tools import clean_env, process_options, stop_process


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    calls = []

    class Provider(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert self.headers["Authorization"] == "Bearer explicit-ci-only"
            model = body["model"]
            payload = json.loads(body["messages"][1]["content"])
            calls.append({"model": model, "path": self.path})
            if model == "requirements-fixture":
                if payload.get("autonomous"):
                    assert_resolution(payload)
                value = news_requirement(payload.get("autonomous", False))
            elif model == "planning-fixture":
                assert_approved(payload)
                value = news_spec()
            elif model == "review-fixture":
                value = {
                    "summary": "根据真实测试报告审阅",
                    "observations": [],
                    "uncovered_requirements": [],
                }
            else:
                raise AssertionError("Unexpected model stage for deterministic CRUD: " + model)
            encoded = json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": json.dumps(value, ensure_ascii=False),
                            }
                        }
                    ],
                    "usage": {"total_tokens": 50},
                },
                ensure_ascii=False,
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    provider = ThreadingHTTPServer(("127.0.0.1", 0), Provider)
    threading.Thread(target=provider.serve_forever, daemon=True).start()
    reports = ROOT / "reports/guided-browser"
    reports.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="guided-browser-") as directory:
        directory = Path(directory)
        port = free_port()
        settings = Settings(
            data_dir=directory / "platform",
            base_url=f"http://127.0.0.1:{provider.server_port}/v1",
            api_key="explicit-ci-only",
            MODE="requirements-fixture",
            PLANNING_MODE="planning-fixture",
            REVIEW_MODE="review-fixture",
            install_products=False,
            retrieval_engine="continue",
            _env_file=None,
        )
        application = create_app(settings)
        server = uvicorn.Server(
            uvicorn.Config(application, host="127.0.0.1", port=port, log_level="error")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        for _ in range(100):
            if server.started:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("Platform did not start")
        browser = ROOT / ".native/browser/node_modules/playwright"
        evidence = directory / "browser-input.json"
        config = {
            "requirement": ORIGINAL_REQUEST,
            "platform": f"http://127.0.0.1:{port}",
            "token": application.state.token,
            "output": str(directory / "download.zip"),
            "reports": str(reports),
        }
        write_json(evidence, config)
        try:
            first = subprocess.run(
                [
                    "node",
                    str(ROOT / "scripts/guided_browser.cjs"),
                    "workbench",
                    str(evidence),
                    str(browser),
                ],
                cwd=ROOT,
                env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
                text=True,
                capture_output=True,
                timeout=150,
            )
            (reports / "workbench.log").write_text(first.stdout + first.stderr, encoding="utf-8")
            assert first.returncode == 0, first.stderr
            outcome = json.loads((reports / "workbench.json").read_text())
            run = application.state.store.get_run(outcome["run_id"])
            assert run["status"] == "READY" and run["auto_mode"]
            assert (
                run["options"]["frontend"] == "simple-admin"
                and run["options"]["database"] == "sqlite"
            )
            assert {c["model"] for c in calls} == {
                "requirements-fixture",
                "planning-fixture",
                "review-fixture",
            }
            product = directory / "product"
            unpack(directory / "download.zip", product)
            env = clean_env({"PRODUCT_DATA_DIR": str(directory / "product-data")})
            subprocess.run(
                [sys.executable, "manage.py", "init"],
                cwd=product,
                env=env,
                check=True,
                capture_output=True,
                timeout=60,
            )
            product_port = free_port()
            config["product"] = f"http://127.0.0.1:{product_port}"
            write_json(evidence, config)
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "app:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(product_port),
                    "--no-access-log",
                ],
                cwd=product,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **process_options(),
            )
            try:
                for _ in range(100):
                    try:
                        if (
                            httpx.get(config["product"] + "/health", trust_env=False).status_code
                            == 200
                        ):
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.1)
                second = subprocess.run(
                    [
                        "node",
                        str(ROOT / "scripts/guided_browser.cjs"),
                        "product",
                        str(evidence),
                        str(browser),
                    ],
                    cwd=ROOT,
                    env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
                    text=True,
                    capture_output=True,
                    timeout=120,
                )
                (reports / "product.log").write_text(
                    second.stdout + second.stderr, encoding="utf-8"
                )
                assert second.returncode == 0, second.stderr
            finally:
                stop_process(process)
            write_json(
                reports / "summary.json",
                {
                    "passed": True,
                    "model_mode": "explicit-local-http-fixtures",
                    "model_calls": calls,
                    "real_browser": True,
                    "smart_without_further_questions": True,
                    "generated_news_search_filter": True,
                    "reported_boundary_list_regression": True,
                    "explicit_facts_preserved": True,
                },
            )
        finally:
            server.should_exit = True
            thread.join(timeout=30)
            provider.shutdown()
            provider.server_close()


if __name__ == "__main__":
    main()
