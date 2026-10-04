"""Live Docker-only browser gate; never certifies from mocks or host Chromium."""

import json
import subprocess
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

from workbench.capability_browser_isolation import (
    DOCKER,
    browser_image_identity,
    browser_source_identity,
    require_image_sources,
    require_worker_inspection,
    run_isolated_browser,
    worker_command,
)
from workbench.capability_contracts import BrowserStep
from workbench.capability_verification import BrowserFailure
from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import clean_env


class Page(BaseHTTPRequestHandler):
    def do_GET(self):
        pages = {
            "/": b'<button id="go" onclick="document.querySelector(\'#value\').textContent=\'ok\'">Go</button><p id="value">waiting</p>',
            "/error": b'<script>throw new Error("candidate error")</script><p id="value">error</p>',
            "/abuse": b"<script>while(true){}</script>",
        }
        value = pages.get(self.path, b"missing")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(value)

    def log_message(self, *args):
        pass


def run(args, timeout=30):
    value = subprocess.run(args, capture_output=True, timeout=timeout, env=clean_env())
    if value.returncode or len(value.stdout) > 100000:
        raise RuntimeError("Live browser infrastructure probe failed")
    return value.stdout


def main():
    image = browser_image_identity()
    report = {
        "protocol": "offline-browser-isolation-v2",
        "passed": False,
        "image": image,
        "mocked": False,
        "sources": browser_source_identity(),
        "image_sources": {},
        "checks": {},
    }
    output = ROOT / "reports/capability-browser-isolation.json"
    write_json(output, report)
    name = "rnd-browser-" + uuid.uuid4().hex
    server = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        command = worker_command(image, name)
        command[-1:-1] = ["--entrypoint=node"]
        command.append("/opt/verifier/capability_browser_network_probe.cjs")
        run(command)
        require_worker_inspection(json.loads(run([*DOCKER, "inspect", name])), image)
        report["image_sources"] = require_image_sources(name)
        report["checks"]["kernel_and_network"] = json.loads(run([*DOCKER, "start", "-a", name]))
        run([*DOCKER, "rm", "-f", name])
        # A separate owned worker must be killed by its memory cgroup, not by
        # a JavaScript heap ceiling, and its descendants must still be removed.
        oom_command = worker_command(image, name)
        oom_command[-1:-1] = ["--entrypoint=node"]
        oom_command.extend(["-e", "const a=[];while(true)a.push(Buffer.alloc(16*1024*1024,255))"])
        run(oom_command)
        require_worker_inspection(json.loads(run([*DOCKER, "inspect", name])), image)
        subprocess.run(
            [*DOCKER, "start", "-a", name], capture_output=True, timeout=30, env=clean_env()
        )
        state = json.loads(run([*DOCKER, "inspect", name]))[0]["State"]
        if state.get("OOMKilled") is not True or state.get("Running") is not False:
            raise RuntimeError("Memory cgroup did not stop abusive worker")
        run([*DOCKER, "rm", "-f", name])
        report["checks"]["memory_exhaustion"] = True
        for mode in ("positive", "error", "abuse"):
            path = "/" if mode == "positive" else "/" + mode
            steps = [BrowserStep(action="open", value=path)]
            if mode == "positive":
                steps += [
                    BrowserStep(action="click", selector="#go"),
                    BrowserStep(action="text", selector="#value", value="ok"),
                ]
            scenario = SimpleNamespace(id=mode, browser=steps)
            try:
                checks = run_isolated_browser(
                    f"http://127.0.0.1:{server.server_port}",
                    "synthetic-token",
                    [scenario],
                    {mode: {}},
                    10 if mode == "abuse" else 60,
                )
                if mode != "positive":
                    raise RuntimeError("Hostile browser unexpectedly passed")
                report["checks"][mode] = bool(checks)
            except BrowserFailure as exc:
                if mode == "positive":
                    report["diagnostic"] = exc.diagnostic
                    raise
                if mode == "error" and exc.diagnostic.get("error_code") != "application-error":
                    raise RuntimeError("Unexpected browser error classification") from None
                if mode == "abuse" and exc.diagnostic.get("error_type") != "TimeoutError":
                    raise RuntimeError("Resource-abuse deadline was not observed") from None
                # Failure alone is insufficient: all owned containers must be gone.
                report["checks"][mode] = True
        remaining = run(
            [*DOCKER, "ps", "-a", "--filter", "name=^/rnd-browser-", "--format", "{{.Names}}"]
        )
        if remaining.strip():
            raise RuntimeError("Browser failure left a container")
        report["checks"]["failure_cleanup"] = True
        report["passed"] = True
    finally:
        subprocess.run(
            [*DOCKER, "rm", "-f", name], capture_output=True, timeout=15, env=clean_env()
        )
        server.shutdown()
        server.server_close()
        write_json(output, report)


if __name__ == "__main__":
    main()
