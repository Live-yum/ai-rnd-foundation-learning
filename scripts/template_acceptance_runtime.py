"""Run source-authored HTTP scenarios and Chromium views on a clean delivered product.

Cases contain only HTTP requests, JSON assertions, and UI expectations. No case can
execute commands, supply a Plan, replace a model response, or invent evidence.
"""

import copy
import json
import os
import re
import secrets
import socket
import subprocess
import time
from datetime import datetime
from pathlib import Path

import httpx

from scripts.template_acceptance_cases import (
    AcceptanceFailure,
    require,
    require_scenario_checks,
    same_obligation,
)
from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, stop_process

REFERENCE = re.compile(r"\$\{([a-zA-Z0-9_.]+)\}")


def reference(values, path):
    result = values
    for part in path.split("."):
        result = result[int(part)] if isinstance(result, list) else result[part]
    return copy.deepcopy(result)


def resolve(value, values):
    if isinstance(value, dict):
        return {key: resolve(item, values) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, values) for item in value]
    if not isinstance(value, str):
        return value
    match = REFERENCE.fullmatch(value)
    if match:
        return reference(values, match.group(1))
    return REFERENCE.sub(lambda match: str(reference(values, match.group(1))), value)


def check_json(value, assertion, location):
    if "where" in assertion:
        require(isinstance(value, list), "assertion_collection", location)
        value = [item for item in value if same_obligation(item, assertion["where"])]
    if assertion.get("one"):
        require(isinstance(value, list) and len(value) == 1, "assertion_one", location)
        value = value[0]
    for key in assertion.get("path", []):
        value = value[key]
    if "equals" in assertion:
        require(
            json.dumps(value, sort_keys=True) == json.dumps(assertion["equals"], sort_keys=True),
            "assertion_equals",
            location,
        )
    if "count" in assertion:
        require(
            isinstance(value, list) and len(value) == assertion["count"],
            "assertion_count",
            location,
        )
    if "ids" in assertion:
        require(
            isinstance(value, list)
            and sorted(item["id"] for item in value) == sorted(assertion["ids"]),
            "assertion_ids",
            location,
        )
    if "contains" in assertion:
        require(
            isinstance(value, list)
            and any(same_obligation(item, assertion["contains"]) for item in value),
            "assertion_contains",
            location,
        )
    if "gte" in assertion:
        require(
            type(value) in {int, float} and value >= assertion["gte"], "assertion_minimum", location
        )
    if assertion.get("timestamp"):
        require(
            isinstance(value, str)
            and datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None,
            "assertion_timestamp",
            location,
        )


class LocalProduct:
    """Own one fresh database and real product process, never the platform's database."""

    def __init__(self, case, product, python, directory):
        self.case, self.product, self.python = case, Path(product), str(python)
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.env = clean_env({"PRODUCT_DATA_DIR": str(self.directory / "database")})
        self.password = secrets.token_urlsafe(24)
        self.actors, self.process, self.client = {}, None, None
        self.http_calls = 0

    def command(self, args, *, stdin=None):
        result = subprocess.run(
            [self.python, *args],
            cwd=self.product,
            env=self.env,
            input=stdin,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=90,
        )
        require(result.returncode == 0, "product_command_failed")

    def start(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        self.process = subprocess.Popen(
            [
                self.python,
                "-m",
                "uvicorn",
                "app:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "critical",
            ],
            cwd=self.product,
            env=self.env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **process_options(),
        )
        self.client = httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=20, trust_env=False, follow_redirects=False
        )
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            require(self.process.poll() is None, "product_start_failed")
            try:
                if self.client.get("/health", timeout=1).status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(0.1)
        raise AcceptanceFailure("product_start_timeout")

    def stop(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.process:
            stop_process(self.process)
            self.process = None

    def request(self, actor, method, path, *, expected=200, location="setup", **kwargs):
        require(method in {"GET", "POST", "PUT", "DELETE"}, "request_method")
        require(
            path.startswith(("/api/", "/business/", "/auth/")) and ".." not in path, "request_path"
        )
        headers = {"Authorization": "Bearer " + self.actors[actor]["token"]} if actor else {}
        response = self.client.request(method, path, headers=headers, **kwargs)
        self.http_calls += 1
        require(
            response.status_code == expected,
            "http_status_mismatch",
            f"{location}/expected_{expected}/actual_{response.status_code}",
        )
        return response.json() if response.content else None

    def __enter__(self):
        try:
            self.command(["manage.py", "init"])
            business = self.case.contract.get("business")
            if business:
                bootstrap = next(
                    name
                    for name, item in self.case.actors.items()
                    if item["role"] == business["bootstrap_role"]
                )
                self.command(
                    [
                        "-c",
                        "import sys,json,getpass; data=json.load(sys.stdin); getpass.getpass=lambda _:data['password']; import manage; manage.bootstrap_admin(data['username'])",
                    ],
                    stdin=json.dumps(
                        {"username": "acceptance_" + bootstrap, "password": self.password}
                    ),
                )
            self.start()
            for name, definition in self.case.actors.items():
                credentials = {"username": "acceptance_" + name, "password": self.password}
                identity = {"username": credentials["username"], **definition}
                if not business:
                    auth = self.request(
                        None, "POST", "/auth/register", json=credentials, expected=201
                    )
                else:
                    if name != bootstrap:
                        identity = self.request(
                            bootstrap,
                            "POST",
                            "/business/users",
                            json={**credentials, **definition},
                            expected=201,
                        )
                    auth = self.request(None, "POST", "/auth/login", json=credentials)
                self.actors[name] = {**identity, "token": auth["access_token"]}
                if business:
                    self.actors[name].update(self.request(name, "GET", "/business/me"))
            return self
        except BaseException:
            self.stop()
            raise

    def __exit__(self, *args):
        self.stop()


def run_scenario(case, product, python, directory, screenshots, *, browser=True):
    """The browser=False switch is for explicit offline harness tests only."""
    checks = []
    with LocalProduct(case, product, python, directory) as app:
        values = {"actors": app.actors}
        for block in case.scenario:
            if block.get("restart"):
                app.stop()
                app.start()
            for index, step in enumerate(block["requests"]):
                location = block["id"] + "/" + str(index)
                body = copy.deepcopy(case.fixtures[step["fixture"]]) if "fixture" in step else {}
                body.update(resolve(step.get("json", {}), values))
                response = app.request(
                    step["actor"],
                    step["method"],
                    resolve(step["path"], values),
                    expected=step["status"],
                    location=location,
                    **({"json": body} if "fixture" in step or "json" in step else {}),
                    **({"params": resolve(step["params"], values)} if "params" in step else {}),
                )
                for assertion in step.get("assertions", []):
                    check_json(response, resolve(assertion, values), location)
                if "save" in step:
                    require(step["save"] not in values, "duplicate_saved_response", location)
                    values[step["save"]] = response
            checks.append(block["id"])
        require_scenario_checks(case, checks)
        browser_report = {"passed": False, "real_browser": False, "scope": "offline_http_test_only"}
        if browser:
            module = os.environ.get(
                "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
            )
            require(Path(module).is_dir(), "browser_tooling_missing")
            screenshots = Path(screenshots)
            screenshots.mkdir(parents=True, exist_ok=True)
            cfg, output = (
                Path(directory) / "browser-input.json",
                Path(directory) / "browser-output.json",
            )
            write_json(
                cfg,
                {
                    "case": case.identity,
                    "url": str(app.client.base_url),
                    "actors": {
                        name: {"username": item["username"]} for name, item in app.actors.items()
                    },
                    "password": app.password,
                    "spec": json.loads(
                        (Path(product) / "approved-spec.json").read_text(encoding="utf-8")
                    ),
                    "views": resolve(list(case.browser), values),
                    "screenshots": str(screenshots),
                    "output": str(output),
                },
            )
            result = subprocess.run(
                ["node", str(ROOT / "scripts/template_acceptance_browser.cjs"), str(cfg), module],
                cwd=ROOT,
                env=clean_env(
                    {"PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0")}
                ),
                capture_output=True,
                timeout=240,
            )
            require(result.returncode == 0 and output.is_file(), "scenario_browser_failed")
            browser_report = json.loads(output.read_text(encoding="utf-8"))
            require(
                browser_report.get("passed") is True and browser_report.get("real_browser") is True,
                "scenario_browser_evidence",
            )
            require(
                browser_report.get("views") == len(case.browser)
                and browser_report.get("errors") == [],
                "scenario_browser_incomplete",
            )
        return {
            "passed": True,
            "checks": checks,
            "http_requests": app.http_calls,
            "restart": True,
            "browser": browser_report,
        }
