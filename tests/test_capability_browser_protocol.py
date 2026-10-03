"""Browser subprocess protocol regressions, not evidence of a live browser run.

The CJS driver really runs under Node, but its Playwright module is an explicit
local test double. Nothing from these tests is a product acceptance receipt.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from workbench import capability_verification as verifier
from workbench.capability_contracts import BrowserStep

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/capability_browser.cjs"
TOKEN = "fixture-private-token-do-not-report"
URL = "https://fixture-private-url.invalid"
SELECTOR = '[data-private="fixture-secret-selector"]'
RAW_ERROR = "fixture-raw-error-do-not-report"
SECRET_ERROR = f"{RAW_ERROR} {TOKEN} {URL} {SELECTOR}"
REQUEST_ID = "1234567890abcdef1234567890abcdef"

# A controlled protocol fixture: no browser executable, network, or credentials.
FAKE_PLAYWRIGHT = r"""
const fs = require('node:fs')
const config = JSON.parse(process.env.FIXTURE_CONFIG)
const calls = {}
function record(op, detail = {}) {
  fs.appendFileSync(process.env.FIXTURE_AUDIT, JSON.stringify({op, ...detail}) + '\n')
}
function perform(op, detail = {}) {
  record(op, detail)
  calls[op] = (calls[op] || 0) + 1
  const failure = (config.failures || {})[op]
  if (failure && calls[op] === (failure.atCall || 1)) {
    const error = new Error(failure.message || config.secretError)
    error.name = failure.name || 'Error'
    throw error
  }
}
async function close(op) {
  perform(op)
  if (config.hangClose === op) {
    setInterval(() => {}, 1000)
    await new Promise(() => {})
  }
}
function target() {
  return {
    fill: async (value, options) => perform('fill', options),
    click: async options => perform('click', options),
    waitFor: async options => perform(options.state, options),
    filter: () => ({waitFor: async options => perform('text', options)}),
  }
}
const page = {
  on: (event, callback) => {
    record('listener', {event})
    if (config.pageError) callback(new Error(config.secretError))
  },
  setViewportSize: async options => perform('viewport', options),
  goto: async (url, options) => {
    perform('navigation', options)
    return {status: () => config.status || 200}
  },
  locator: () => target(),
}
const context = {
  route: async () => perform('routing'),
  routeWebSocket: async () => perform('websocket'),
  newPage: async () => {perform('page'); return page},
  close: async () => close('context-close'),
}
const browser = {
  newContext: async options => {
    perform('context', {
      serviceWorkers: options.serviceWorkers,
      acceptDownloads: options.acceptDownloads,
      tokenMatches: options.extraHTTPHeaders['x-daytona-preview-token'] === config.token,
    })
    return context
  },
  close: async () => close('browser-close'),
}
exports.chromium = {
  launch: async options => {perform('launch', options); return browser},
}
"""


def assert_redacted(value):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    for secret in (TOKEN, URL, SELECTOR, "fixture-secret-selector", RAW_ERROR):
        assert secret not in text


def diagnostic(**changes):
    return {
        "phase": "assertion",
        "scenario_index": 0,
        "step_index": 1,
        "action": "visible",
        "navigation_status": 200,
        "error_code": "timeout",
        "error_type": "TimeoutError",
        **changes,
    }


def report(payload, **changes):
    return {
        "protocol": 1,
        "request_id": payload["request_id"],
        "verifier_sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        "passed": True,
        "checks": [
            {
                "id": "fixture-only",
                "passed": True,
                "steps": 2,
                "real_browser": True,
                "browser_os_sandbox": True,
            }
        ],
        **changes,
    }


def failed_report(payload, **changes):
    value = report(payload, passed=False, diagnostic=diagnostic(**changes))
    del value["checks"]
    return value


@pytest.fixture
def cjs_runner(tmp_path):
    node = shutil.which("node")
    if not node:
        if os.environ.get("RND_REQUIRE_NODE_TESTS") == "1":
            pytest.fail("Node is required for the browser protocol regression tests")
        pytest.skip("Node is not installed; no browser protocol test was run")
    module = tmp_path / "explicit-fake-playwright"
    module.mkdir()
    (module / "package.json").write_text('{"version":"1.56.1","main":"index.cjs"}')
    (module / "index.cjs").write_text(FAKE_PLAYWRIGHT)
    audit = tmp_path / "fixture-audit.jsonl"

    def run(
        *,
        steps=None,
        failures=None,
        page_error=False,
        raw=None,
        version="1.56.1",
        hang_close=None,
        scenarios=None,
        channel="",
    ):
        (module / "package.json").write_text(json.dumps({"version": version, "main": "index.cjs"}))
        audit.write_text("")
        payload = {
            "request_id": REQUEST_ID,
            "url": URL,
            "token": TOKEN,
            "scenarios": [
                {
                    "id": "fixture-only",
                    "steps": steps
                    or [
                        {"action": "open", "value": "/private-path"},
                        {"action": "visible", "selector": SELECTOR},
                    ],
                }
            ],
        }
        config = {
            "failures": failures or {},
            "pageError": page_error,
            "secretError": SECRET_ERROR,
            "token": TOKEN,
            "hangClose": hang_close,
        }
        if scenarios is not None:
            payload["scenarios"] = scenarios
        try:
            result = subprocess.run(
                [node, str(SCRIPT)],
                input=json.dumps(payload).encode() if raw is None else raw,
                capture_output=True,
                timeout=2 if hang_close else 10,
                cwd=tmp_path,
                env={
                    # Windows Node/OpenSSL needs its OS loader environment even
                    # in this credential-free protocol fixture. Preserve only
                    # those OS paths, never the caller's general environment.
                    **{
                        key: value
                        for key, value in os.environ.items()
                        if key.upper() in {"SYSTEMROOT", "WINDIR"}
                    },
                    "PATH": str(Path(node).parent),
                    "PRODUCT_VERIFY_PLAYWRIGHT": str(module),
                    "PRODUCT_VERIFY_BROWSER_CHANNEL": channel,
                    "FIXTURE_CONFIG": json.dumps(config),
                    "FIXTURE_AUDIT": str(audit),
                },
            )
        except subprocess.TimeoutExpired as exc:
            if not hang_close:
                raise
            # subprocess.run has killed and reaped the deliberate hanging fixture.
            result = SimpleNamespace(returncode=None, stdout=exc.stdout, stderr=exc.stderr or b"")
        else:
            assert not hang_close, "The deliberate cleanup hang should hit the process deadline"
        assert result.stderr == b""
        assert_redacted(result.stdout.decode())
        value = json.loads(result.stdout)
        assert value["protocol"] == 1
        assert value["verifier_sha256"] == hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
        events = [json.loads(line) for line in audit.read_text().splitlines()]
        return result.returncode, value, events

    return run


@pytest.mark.node_tools
def test_actual_cjs_protocol_success_keeps_sandbox_and_original_action_timeouts(cjs_runner):
    actions = ["fill", "click", "visible", "hidden", "text"]
    steps = [
        {"action": "viewport", "width": 900, "height": 700},
        {"action": "open", "value": "/private-path"},
        *[{"action": action, "selector": SELECTOR, "value": TOKEN} for action in actions],
    ]
    status, value, events = cjs_runner(steps=steps)
    assert status == 0
    assert value == report(
        {"request_id": REQUEST_ID},
        checks=[
            {
                "id": "fixture-only",
                "passed": True,
                "steps": len(steps),
                "real_browser": True,
                "browser_os_sandbox": True,
            }
        ],
    )
    launch = next(event for event in events if event["op"] == "launch")
    assert launch["headless"] is True
    assert launch["chromiumSandbox"] is True
    assert "channel" not in launch
    assert "--no-sandbox" not in launch["args"]
    assert "--force-webrtc-ip-handling-policy=disable_non_proxied_udp" in launch["args"]
    assert next(event for event in events if event["op"] == "context") == {
        "op": "context",
        "serviceWorkers": "block",
        "acceptDownloads": False,
        "tokenMatches": True,
    }
    navigation = next(event for event in events if event["op"] == "navigation")
    assert navigation["timeout"] == 15000
    assert navigation["waitUntil"] == "domcontentloaded"
    assert all(
        next(event for event in events if event["op"] == action)["timeout"] == 10000
        for action in actions
    )
    assert [event["op"] for event in events][-2:] == ["context-close", "browser-close"]


@pytest.mark.node_tools
@pytest.mark.parametrize(
    ("operation", "phase", "action", "index"),
    [
        ("context", "context", None, None),
        ("routing", "routing", None, None),
        ("websocket", "routing", None, None),
        ("page", "page", None, None),
        ("navigation", "navigation", "open", 0),
        ("fill", "action", "fill", 1),
        ("click", "action", "click", 1),
        ("visible", "assertion", "visible", 1),
        ("hidden", "assertion", "hidden", 1),
        ("text", "assertion", "text", 1),
    ],
)
def test_actual_cjs_preserves_primary_failure_when_both_closes_fail(
    cjs_runner, operation, phase, action, index
):
    steps = [
        {"action": "open", "value": "/private-path"},
        {"action": action or "visible", "selector": SELECTOR, "value": TOKEN},
    ]
    status, value, events = cjs_runner(
        steps=steps,
        failures={
            operation: {"name": "TimeoutError"},
            "context-close": {"name": "TypeError"},
            "browser-close": {"name": "ReferenceError"},
        },
    )
    assert status == 1
    assert value == failed_report(
        {"request_id": REQUEST_ID},
        phase=phase,
        action=action,
        step_index=index,
        navigation_status=200 if index == 1 else None,
    )
    assert events[-1]["op"] == "browser-close"
    if operation != "context":
        assert events[-2]["op"] == "context-close"


@pytest.mark.node_tools
@pytest.mark.parametrize(
    ("message", "code"),
    [
        ("No usable sandbox", "sandbox-unavailable"),
        ("Failed to move to new namespace", "sandbox-unavailable"),
        ("Running as root without --no-sandbox", "sandbox-unavailable"),
        ("Executable doesn't exist", "browser-missing"),
        ("Chromium distribution 'chrome' is not found", "browser-missing"),
        ("error while loading shared libraries", "browser-dependency"),
        ("unrecognized launch failure", "operation-failed"),
    ],
)
def test_actual_cjs_launch_failure_returns_only_classification(cjs_runner, message, code):
    status, value, events = cjs_runner(
        failures={"launch": {"message": f"{message}: {SECRET_ERROR}"}}
    )
    assert status == 1
    assert value == failed_report(
        {"request_id": REQUEST_ID},
        phase="launch",
        scenario_index=None,
        step_index=None,
        action=None,
        navigation_status=None,
        error_code=code,
        error_type="Error",
    )
    assert [event["op"] for event in events] == ["launch"]


@pytest.mark.node_tools
def test_system_chrome_channel_keeps_sandbox_and_does_not_retry(cjs_runner):
    status, _, events = cjs_runner(channel="chrome")
    assert status == 0
    launch = next(event for event in events if event["op"] == "launch")
    assert launch["channel"] == "chrome"
    assert launch["chromiumSandbox"] is True
    assert "executablePath" not in launch
    assert "--no-sandbox" not in launch["args"]
    status, value, events = cjs_runner(
        channel="chrome", failures={"launch": {"message": "No usable sandbox: " + SECRET_ERROR}}
    )
    assert status == 1
    assert value["diagnostic"]["error_code"] == "sandbox-unavailable"
    assert [event["op"] for event in events] == ["launch"]


@pytest.mark.node_tools
@pytest.mark.parametrize("channel", ["msedge", "--no-sandbox", "/tmp/private-browser", TOKEN])
def test_unknown_browser_channel_fails_before_launch_without_leaking_input(cjs_runner, channel):
    status, value, events = cjs_runner(channel=channel)
    assert status == 1
    assert value["diagnostic"]["phase"] == "tool"
    assert value["diagnostic"]["error_code"] == "browser-channel-rejected"
    assert events == []


@pytest.mark.node_tools
@pytest.mark.parametrize(
    ("message", "code"),
    [
        ("net::ERR_NAME_NOT_RESOLVED", "name-resolution"),
        ("net::ERR_CONNECTION_REFUSED", "connection-refused"),
        ("net::ERR_CONNECTION_RESET", "navigation-network"),
    ],
)
def test_actual_cjs_navigation_failure_does_not_leak_url(cjs_runner, message, code):
    status, value, _ = cjs_runner(
        failures={"navigation": {"message": f"{message}: {SECRET_ERROR}"}}
    )
    assert status == 1
    assert value["diagnostic"] == diagnostic(
        phase="navigation",
        step_index=0,
        action="open",
        navigation_status=None,
        error_code=code,
        error_type="Error",
    )


@pytest.mark.node_tools
def test_actual_cjs_failed_second_navigation_cannot_reuse_prior_status(cjs_runner):
    status, value, events = cjs_runner(
        steps=[{"action": "open", "value": "/first"}, {"action": "open", "value": "/second"}],
        failures={
            "navigation": {"atCall": 2, "message": "net::ERR_CONNECTION_REFUSED: " + SECRET_ERROR}
        },
    )
    assert status == 1
    assert value["diagnostic"] == diagnostic(
        phase="navigation",
        step_index=1,
        action="open",
        navigation_status=None,
        error_code="connection-refused",
        error_type="Error",
    )
    assert sum(event["op"] == "navigation" for event in events) == 2


@pytest.mark.node_tools
@pytest.mark.parametrize("first_close", ["context-close", "browser-close"])
def test_actual_cjs_successful_actions_do_not_hide_cleanup_failure(cjs_runner, first_close):
    failures = {first_close: {"name": "TypeError"}}
    if first_close == "context-close":
        failures["browser-close"] = {"name": "ReferenceError"}
    status, value, events = cjs_runner(failures=failures)
    assert status == 1
    assert value == failed_report(
        {"request_id": REQUEST_ID},
        phase=first_close,
        error_code="operation-failed",
        error_type="TypeError",
    )
    assert events[-1]["op"] == "browser-close"


@pytest.mark.node_tools
def test_actual_cjs_application_error_survives_cleanup_and_unknown_error_name(cjs_runner):
    status, value, _ = cjs_runner(
        page_error=True, failures={"context-close": {"name": SECRET_ERROR}}
    )
    assert status == 1
    assert value["diagnostic"] == diagnostic(
        phase="application", error_code="application-error", error_type="Error"
    )
    status, value, _ = cjs_runner(failures={"visible": {"name": SECRET_ERROR}})
    assert status == 1
    assert value["diagnostic"]["error_type"] == "Other"


@pytest.mark.node_tools
def test_actual_cjs_rejects_cross_origin_navigation_before_goto(cjs_runner):
    status, value, events = cjs_runner(
        steps=[{"action": "open", "value": "https://other-fixture-origin.invalid/private"}]
    )
    assert status == 1
    assert value["diagnostic"] == diagnostic(
        phase="navigation",
        action="open",
        step_index=0,
        navigation_status=None,
        error_code="origin-rejected",
        error_type="Error",
    )
    assert "navigation" not in [event["op"] for event in events]


@pytest.mark.node_tools
def test_actual_cjs_rejects_wrong_playwright_version_before_launch(cjs_runner):
    status, value, events = cjs_runner(version="0.0.0-fixture")
    assert status == 1
    assert value["diagnostic"] == diagnostic(
        phase="tool",
        scenario_index=None,
        step_index=None,
        action=None,
        navigation_status=None,
        error_code="tool-version",
        error_type="Error",
    )
    assert events == []


@pytest.mark.node_tools
@pytest.mark.parametrize("hang_close", ["context-close", "browser-close"])
def test_actual_cjs_emits_first_failure_once_before_cleanup_can_hang(cjs_runner, hang_close):
    status, value, events = cjs_runner(
        failures={"visible": {"name": "TimeoutError"}}, hang_close=hang_close
    )
    assert status is None
    assert value == failed_report({"request_id": REQUEST_ID})
    assert events[-1]["op"] == hang_close


@pytest.mark.node_tools
def test_actual_cjs_identifies_later_scenario_without_returning_partial_success(cjs_runner):
    scenarios = [
        {"id": name, "steps": [{"action": "open", "value": "/private-path"}]}
        for name in ("fixture-one", "fixture-two")
    ]
    status, value, _ = cjs_runner(
        scenarios=scenarios, failures={"navigation": {"name": "TimeoutError", "atCall": 2}}
    )
    assert status == 1
    assert value == failed_report(
        {"request_id": REQUEST_ID},
        phase="navigation",
        scenario_index=1,
        step_index=0,
        action="open",
        navigation_status=None,
    )


@pytest.mark.node_tools
@pytest.mark.parametrize(
    ("raw", "code", "error_type"),
    [
        (b'{"request_id": "bad",', "operation-failed", "SyntaxError"),
        (b'{"request_id": "bad"}', "operation-failed", "Error"),
        pytest.param(b"x" * 1000001, "contract-too-large", "Error", id="oversized-contract"),
    ],
)
def test_actual_cjs_rejects_damaged_input_before_loading_browser(cjs_runner, raw, code, error_type):
    status, value, events = cjs_runner(raw=raw)
    assert status == 1
    assert value == failed_report(
        {"request_id": None},
        phase="contract",
        scenario_index=None,
        step_index=None,
        action=None,
        navigation_status=None,
        error_code=code,
        error_type=error_type,
    )
    assert events == []


@pytest.fixture
def browser_process(monkeypatch):
    """Deterministic subprocess boundary fixture; does not launch a browser."""
    instances = []
    monkeypatch.setattr(verifier.shutil, "which", lambda name: "/fixture/node")

    def install(response=None, *, returncode=0, timeout=False, cleanup_error=False):
        class Process:
            def __init__(self, command, **options):
                self.command = command
                self.options = options
                self.returncode = returncode
                self.stopped = False
                instances.append(self)

            def communicate(self, raw, *, timeout):
                self.payload = json.loads(raw)
                self.timeout = timeout
                value = response(self.payload) if callable(response) else response
                if value is None:
                    value = report(self.payload)
                self.options["stdout"].write(
                    value if isinstance(value, bytes) else json.dumps(value).encode()
                )
                if self.should_timeout:
                    raise subprocess.TimeoutExpired(self.command, timeout, output=SECRET_ERROR)

            should_timeout = timeout

        def stop(process):
            process.stopped = True
            if cleanup_error:
                raise OSError(SECRET_ERROR)

        monkeypatch.setattr(verifier.subprocess, "Popen", Process)
        monkeypatch.setattr(verifier, "stop_process", stop)
        return instances

    return install


def run_fixture_browser():
    scenario = SimpleNamespace(
        id="fixture-only",
        browser=[
            BrowserStep(action="open", value="/private-path"),
            BrowserStep(action="fill", selector=SELECTOR, value="${private_value}"),
        ],
    )
    return verifier.run_browser(
        URL, TOKEN, [scenario], {"fixture-only": {"private_value": TOKEN}}, 23
    )


def capture_failure():
    with pytest.raises(verifier.BrowserFailure) as raised:
        run_fixture_browser()
    assert_redacted(str(raised.value))
    assert_redacted(raised.value.diagnostic)
    return raised.value.diagnostic


def test_python_success_binds_request_sha_and_keeps_secrets_off_command_line(browser_process):
    instances = browser_process()
    checks = run_fixture_browser()
    first = instances[0]
    assert checks == report(first.payload)["checks"]
    assert first.command == ["/fixture/node", str(SCRIPT)]
    assert re.fullmatch(r"[a-f0-9]{32}", first.payload["request_id"])
    assert first.payload["token"] == TOKEN
    assert first.payload["scenarios"][0]["steps"][1]["value"] == TOKEN
    assert first.timeout == 23
    assert first.options["stdin"] == subprocess.PIPE
    assert first.options["stderr"] == subprocess.STDOUT
    assert TOKEN not in json.dumps(first.options["env"])
    assert first.options["stdout"].closed
    assert first.stopped is False
    run_fixture_browser()
    assert first.payload["request_id"] != instances[1].payload["request_id"]


def test_python_passes_only_selected_channel_without_inheriting_browser_arguments(
    browser_process, monkeypatch
):
    monkeypatch.setenv("PRODUCT_VERIFY_BROWSER_CHANNEL", "chrome")
    monkeypatch.setenv("PRODUCT_VERIFY_BROWSER_ARGS", "--no-sandbox")
    monkeypatch.setenv("PRODUCT_VERIFY_BROWSER_EXECUTABLE", "/tmp/private-browser")
    monkeypatch.setenv("CLOUD_PRIVATE_TOKEN", TOKEN)
    instances = browser_process()
    run_fixture_browser()
    env = instances[0].options["env"]
    assert env["PRODUCT_VERIFY_BROWSER_CHANNEL"] == "chrome"
    assert "PRODUCT_VERIFY_BROWSER_ARGS" not in env
    assert "PRODUCT_VERIFY_BROWSER_EXECUTABLE" not in env
    assert "CLOUD_PRIVATE_TOKEN" not in env


@pytest.mark.parametrize("returncode", [0, 1, -9])
def test_python_valid_failure_diagnostic_is_retained(browser_process, returncode):
    browser_process(failed_report, returncode=returncode)
    assert capture_failure() == {**diagnostic(), "exit_code": returncode}


@pytest.mark.parametrize("cleanup_error", [False, True])
def test_python_timeout_preserves_primary_error_even_when_cleanup_fails(
    browser_process, cleanup_error
):
    instances = browser_process(SECRET_ERROR.encode(), timeout=True, cleanup_error=cleanup_error)
    assert capture_failure() == {
        "phase": "python-timeout",
        "error_code": "timeout",
        "cleanup": "failed" if cleanup_error else "stopped",
    }
    assert instances[0].stopped is True
    assert instances[0].options["stdout"].closed


@pytest.mark.parametrize("cleanup_error", [False, True])
def test_python_timeout_keeps_prior_bound_failure_when_browser_cleanup_hangs(
    browser_process, cleanup_error
):
    instances = browser_process(failed_report, timeout=True, cleanup_error=cleanup_error)
    assert capture_failure() == {
        **diagnostic(),
        "termination": "python-timeout",
        "cleanup": "failed" if cleanup_error else "stopped",
    }
    assert instances[0].stopped is True
    assert instances[0].options["stdout"].closed


@pytest.mark.parametrize(
    "prior_report", ["success", "wrong-request", "wrong-verifier", "malformed"]
)
def test_python_timeout_does_not_adopt_unbound_or_malformed_prior_report(
    browser_process, prior_report
):
    def response(payload):
        if prior_report == "success":
            return report(payload)
        value = failed_report(payload)
        if prior_report == "wrong-request":
            value["request_id"] = "f" * 32
        elif prior_report == "wrong-verifier":
            value["verifier_sha256"] = "0" * 64
        else:
            value["diagnostic"]["phase"] = {"message": SECRET_ERROR}
        return value

    browser_process(response, timeout=True)
    assert capture_failure() == {
        "phase": "python-timeout",
        "error_code": "timeout",
        "cleanup": "stopped",
    }


@pytest.mark.parametrize(
    ("response", "category"),
    [
        (SECRET_ERROR.encode(), "invalid-json"),
        (b'{"protocol":1', "invalid-json"),
        (b"\xff\xfe\x00", "invalid-json"),
        pytest.param(b"x" * 100001, "report-too-large", id="oversized-report"),
        ([], "invalid-schema"),
        (lambda payload: report(payload, protocol=True), "invalid-schema"),
        (lambda payload: report(payload, protocol=2), "invalid-schema"),
        (lambda payload: report(payload, request_id="f" * 32), "wrong-verifier-or-request"),
        (lambda payload: report(payload, verifier_sha256="0" * 64), "wrong-verifier-or-request"),
        (lambda payload: report(payload, diagnostic=SECRET_ERROR), "invalid-schema"),
        (lambda payload: report(payload, checks={}), "invalid-schema"),
        (lambda payload: report(payload, passed=1), "invalid-diagnostic"),
    ],
)
@pytest.mark.parametrize("returncode", [0, 7])
def test_python_rejects_damaged_oversized_or_unbound_reports(
    browser_process, response, category, returncode
):
    browser_process(response, returncode=returncode)
    assert capture_failure() == {
        "phase": "python-exit" if returncode else "python-report",
        "error_code": "nonzero-exit" if returncode else "invalid-report",
        "exit_code": returncode,
        "report_error": category,
    }


@pytest.mark.parametrize("returncode", [0, 7])
def test_python_deep_json_report_is_rejected_without_recursion_escape(browser_process, returncode):
    browser_process(b"[" * 2000 + b"0" + b"]" * 2000, returncode=returncode)
    value = capture_failure()
    # JSON decoder recursion limits differ between supported Python builds.
    assert value.pop("report_error") in {"invalid-json", "invalid-schema"}
    assert value == {
        "phase": "python-exit" if returncode else "python-report",
        "error_code": "nonzero-exit" if returncode else "invalid-report",
        "exit_code": returncode,
    }


@pytest.mark.parametrize("returncode", [1, -9, None, False, "0"])
def test_python_rejects_success_with_nonzero_or_invalid_exit(browser_process, returncode):
    browser_process(returncode=returncode)
    assert capture_failure() == {
        "phase": "python-exit",
        "error_code": "success-with-invalid-exit",
        "exit_code": returncode if type(returncode) is int else None,
    }


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("id", []),
        ("id", "different-scenario"),
        ("steps", True),
        ("steps", 2.0),
        ("steps", "2"),
        ("steps", 0),
        ("passed", False),
        ("real_browser", 1),
        ("browser_os_sandbox", False),
        ("message", SECRET_ERROR),
    ],
)
def test_python_success_checks_must_match_current_plan_and_exact_schema(
    browser_process, field, value
):
    def response(payload):
        result = report(payload)
        result["checks"][0][field] = value
        return result

    browser_process(response)
    assert capture_failure() == {"phase": "python-report", "error_code": "invalid-checks"}


@pytest.mark.parametrize("kind", ["missing", "duplicate", "null", "string", "missing-field"])
def test_python_success_checks_reject_missing_duplicate_or_damaged_entries(browser_process, kind):
    def response(payload):
        result = report(payload)
        if kind == "missing":
            result["checks"] = []
        elif kind == "duplicate":
            result["checks"] *= 2
        elif kind == "missing-field":
            del result["checks"][0]["steps"]
        else:
            result["checks"] = [None if kind == "null" else SECRET_ERROR]
        return result

    browser_process(response)
    assert capture_failure() == {"phase": "python-report", "error_code": "invalid-checks"}


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("phase", SECRET_ERROR),
        ("error_code", SECRET_ERROR),
        ("error_type", SECRET_ERROR),
        ("action", SECRET_ERROR),
        ("scenario_index", True),
        ("scenario_index", -1),
        ("scenario_index", 10001),
        ("step_index", 0.5),
        ("step_index", "1"),
        ("step_index", {}),
        ("navigation_status", True),
        ("navigation_status", 99),
        ("navigation_status", 600),
        ("navigation_status", []),
        *[
            (field, value)
            for field in ("phase", "error_code", "error_type", "action")
            for value in ([], {})
        ],
    ],
)
def test_python_malformed_diagnostic_including_unhashable_values_fails_closed(
    browser_process, field, bad_value
):
    browser_process(lambda payload: failed_report(payload, **{field: bad_value}), returncode=1)
    assert capture_failure() == {
        "phase": "python-exit",
        "error_code": "nonzero-exit",
        "exit_code": 1,
        "report_error": "invalid-diagnostic",
    }


@pytest.mark.parametrize("mutation", ["missing-field", "extra-field", "not-object"])
def test_python_diagnostic_requires_exact_schema(browser_process, mutation):
    def response(payload):
        value = failed_report(payload)
        if mutation == "missing-field":
            del value["diagnostic"]["action"]
        elif mutation == "extra-field":
            value["diagnostic"]["message"] = SECRET_ERROR
        else:
            value["diagnostic"] = [SECRET_ERROR]
        return value

    browser_process(response, returncode=1)
    assert capture_failure()["report_error"] == "invalid-diagnostic"


def test_python_missing_node_and_spawn_failure_are_redacted(monkeypatch):
    monkeypatch.setattr(verifier.shutil, "which", lambda name: None)
    assert capture_failure() == {"phase": "python-spawn", "error_code": "node-missing"}
    monkeypatch.setattr(verifier.shutil, "which", lambda name: "/fixture/node")

    def fail(*args, **kwargs):
        raise OSError(SECRET_ERROR)

    monkeypatch.setattr(verifier.subprocess, "Popen", fail)
    assert capture_failure() == {"phase": "python-spawn", "error_code": "spawn-failed"}


def test_python_missing_verifier_fails_before_process_spawn(monkeypatch, tmp_path):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    monkeypatch.setattr(verifier.shutil, "which", lambda name: "/fixture/node")

    def unexpected(*args, **kwargs):
        pytest.fail("No process may start without the trusted verifier's current SHA")

    monkeypatch.setattr(verifier.subprocess, "Popen", unexpected)
    assert capture_failure() == {"phase": "python-spawn", "error_code": "verifier-unavailable"}


def test_python_without_browser_scenarios_does_not_spawn(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("No browser subprocess should be started without browser scenarios")

    monkeypatch.setattr(verifier.subprocess, "Popen", unexpected)
    assert verifier.run_browser(URL, TOKEN, [SimpleNamespace(browser=[])], {}, 23) == []
