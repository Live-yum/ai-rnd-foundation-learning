"""Real sandboxed controller-browser readiness, never product acceptance.

Run before building Daytona. Only a synthetic loopback page is served; no
application source, credentials, model, AppArmor policy or sysctl is changed.
The same trusted driver, pinned Playwright, channel and sandbox settings as the
product verifier must pass. A bundled-browser failure is retained separately
for diagnosis when the explicitly selected system Chrome passes.
"""

import os
import re
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from workbench.capability_contracts import BrowserStep
from workbench.capability_verification import BrowserFailure, run_browser
from workbench.filesystem import sha, write_json
from workbench.settings import ROOT
from workbench.tools import clean_env

PAGE = b"""<!doctype html><meta charset="utf-8"><title>Browser readiness</title>
<button id="check" onclick="document.querySelector('#result').textContent='Ready'">Check</button>
<p id="result">Waiting</p>"""


class FixturePage(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def log_message(self, *args):
        pass


def readonly_host_facts():
    facts = {}
    for name, filename in {
        "apparmor_enabled": "/sys/module/apparmor/parameters/enabled",
        "apparmor_restrict_unprivileged_userns": "/proc/sys/kernel/apparmor_restrict_unprivileged_userns",
        "unprivileged_userns_clone": "/proc/sys/kernel/unprivileged_userns_clone",
    }.items():
        try:
            value = Path(filename).read_text(encoding="ascii").strip()
        except OSError, UnicodeError:
            value = None
        facts[name] = value if value in {"0", "1", "Y", "N"} else None
    return facts


def probe(url):
    scenario = SimpleNamespace(
        id="controller-browser-readiness",
        browser=[
            BrowserStep(action="open", value="/"),
            BrowserStep(action="text", selector="#result", value="Waiting"),
            BrowserStep(action="click", selector="#check"),
            BrowserStep(action="text", selector="#result", value="Ready"),
        ],
    )
    try:
        checks = run_browser(url, "synthetic-readiness-token", [scenario], {scenario.id: {}}, 60)
    except BrowserFailure as exc:
        return {"passed": False, "browser_diagnostic": exc.diagnostic}
    except Exception:
        # An unexpected infrastructure exception must not leak environment or
        # subprocess text, and must never turn into a passing readiness result.
        return {"passed": False, "error_code": "preflight-infrastructure"}
    return {"passed": True, "checks": checks}


def installed_chrome_version():
    try:
        result = subprocess.run(
            ["/usr/bin/google-chrome", "--product-version"],
            capture_output=True,
            timeout=10,
            env=clean_env(),
        )
        value = result.stdout.decode("ascii").strip()
        if result.returncode == 0 and re.fullmatch(r"[0-9]{1,4}(?:\.[0-9]{1,4}){3}", value):
            return value
    except OSError, UnicodeError, subprocess.TimeoutExpired:
        pass
    return None


def main():
    channel = os.environ.get("PRODUCT_VERIFY_BROWSER_CHANNEL", "")
    report = {
        "passed": False,
        "scope": "controller-browser-readiness-only",
        "product_acceptance": False,
        "channel": channel if channel in {"", "chrome"} else "rejected",
        "playwright_version": "1.56.1",
        "chrome_version": installed_chrome_version() if channel == "chrome" else None,
        "browser_verifier_sha256": sha(ROOT / "scripts/capability_browser.cjs"),
        "host_facts": readonly_host_facts(),
    }
    report_path = ROOT / "reports/capability-browser-preflight.json"
    write_json(report_path, report)
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixturePage)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}"
        if channel == "chrome":
            # Observe the old bundled launch separately. This result never
            # satisfies the mandatory probe for the explicitly chosen channel.
            os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] = ""
            try:
                report["bundled_probe"] = probe(url)
            finally:
                os.environ["PRODUCT_VERIFY_BROWSER_CHANNEL"] = channel
        report["selected_probe"] = probe(url)
        report["passed"] = report["selected_probe"]["passed"] is True
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        write_json(report_path, report)
    if not report["passed"]:
        raise SystemExit(
            "Sandboxed browser preflight FAILED; see capability-browser-preflight.json"
        )
    print("Sandboxed controller browser readiness PASS; product acceptance is still required.")


if __name__ == "__main__":
    main()
