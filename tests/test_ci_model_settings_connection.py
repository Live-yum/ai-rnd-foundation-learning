"""Mock-only acceptance contracts; never certify a real provider."""

import json

import httpx
import pytest

from scripts.ci_model_settings_connection import BoundedTransport, acceptance, safe_result

VALUES = {
    "BASE_URL": "https://provider.example/v1/",
    "API_KEY": "dummy-test-secret",
    "MODE": "test-model",
}


def completion():
    return httpx.Response(
        200,
        json={
            "id": "test",
            "object": "chat.completion",
            "created": 0,
            "model": "test-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": '{"ok":true}'},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17},
        },
    )


def test_env_settings_save_and_one_probe(monkeypatch):
    monkeypatch.setenv("API_KEY", "wrong-process-key")
    monkeypatch.setenv("BASE_URL", "https://wrong.example")
    seen = []

    def handle(request):
        seen.append(request)
        assert request.headers["authorization"] == "Bearer " + VALUES["API_KEY"]
        assert str(request.url) == "https://provider.example/v1/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == VALUES["MODE"]
        assert body.get("max_tokens", body.get("max_completion_tokens")) == 128
        assert body["stream"] is False
        assert all(value <= 20 for value in request.extensions["timeout"].values())
        return completion()

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "passed"
    assert result["settings_lifecycle"] == "passed"
    assert result["real_service"] is False
    assert result["inference_requests"] == len(seen) == 1
    assert result["catalog_requests"] == 0
    assert not any(value in json.dumps(result) for value in VALUES.values())


@pytest.mark.parametrize("status", [404, 405, 501])
def test_unsupported_catalog_does_not_fail_successful_inference(status):
    seen = []

    def handle(request):
        seen.append(request.method)
        return httpx.Response(status) if request.method == "GET" else completion()

    result = acceptance(VALUES, transport=httpx.MockTransport(handle), discover=True)
    assert result["code"] == "passed"
    assert result["catalog"]["ok"] is False
    assert result["catalog"]["http_status"] == status
    if status in (404, 405):
        assert result["catalog"]["code"] == "discovery_unsupported"
    assert result["probe"]["ok"] is True
    assert result["inference_requests"] == result["catalog_requests"] == 1
    assert seen == ["GET", "POST"]


@pytest.mark.parametrize("status", [301, 307, 401, 429, 500])
def test_failure_never_retries_or_redirects(status):
    seen = []

    def handle(request):
        seen.append(str(request.url))
        return httpx.Response(
            status,
            headers={"location": "https://other.example"},
            text="provider error " + VALUES["API_KEY"],
        )

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "probe_failed"
    assert result["inference_requests"] == len(seen) == 1
    assert result["catalog_requests"] == 0
    assert VALUES["API_KEY"] not in json.dumps(result)


@pytest.mark.parametrize(
    "values,code",
    [
        ({**VALUES, "API_KEY": ""}, "missing_configuration"),
        ({**VALUES, "MODE": ""}, "missing_configuration"),
        ({**VALUES, "BASE_URL": "http://provider.example/v1"}, "https_required"),
        ({**VALUES, "BASE_URL": "http://127.0.0.1:9000/v1"}, "https_required"),
        ({**VALUES, "BASE_URL": "https://user:secret@provider.example"}, "invalid_configuration"),
    ],
)
def test_static_configuration_failures_do_not_network(values, code):
    def forbidden(request):
        pytest.fail("network must not be attempted")

    result = acceptance(values, transport=httpx.MockTransport(forbidden), discover=True)
    assert result["code"] == code
    assert result["inference_requests"] == result["catalog_requests"] == 0


def test_transport_hard_budget_and_exact_destination():
    calls = []
    transport = BoundedTransport(
        "https://provider.example/v1",
        inner=httpx.MockTransport(lambda request: calls.append(request) or httpx.Response(200)),
    )
    first = httpx.Request("POST", "https://provider.example/v1/chat/completions")
    transport.handle_request(first)
    with pytest.raises(httpx.RequestError):
        transport.handle_request(first)
    with pytest.raises(httpx.RequestError):
        transport.handle_request(httpx.Request("POST", "https://other.example/chat/completions"))
    assert len(calls) == 1


def test_receipts_exclude_raw_provider_strings():
    result = safe_result({"ok": False, "code": VALUES["API_KEY"], "models": [VALUES["API_KEY"]]})
    assert result == {"ok": False, "code": "other_failure"}


def test_workflow_is_bounded_and_credentials_are_step_scoped():
    from pathlib import Path

    import yaml

    workflow = yaml.safe_load(Path(".github/workflows/model-settings-connection.yml").read_text())
    trigger = workflow.get("on", workflow.get(True))
    assert trigger == {"push": {"branches": ["fix/model-settings-env-connection"]}}
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["connection"]
    assert job["timeout-minutes"] == 10
    assert "github.run_attempt == 1" in job["if"]
    assert "github.event.created == true" in job["if"]
    assert "github.event.before == '0000000000000000000000000000000000000000'" in job["if"]
    assert (
        "contains(github.event.head_commit.message, '[settings-connection-acceptance-20261015]')"
        in job["if"]
    )
    assert "env" not in job and "env" not in workflow
    steps = job["steps"]
    secret_steps = [i for i, step in enumerate(steps) if "secrets.API_KEY" in str(step)]
    assert len(secret_steps) == 1
    index = secret_steps[0]
    assert any("pytest" in step.get("run", "") for step in steps[:index])
    assert any("uv sync --locked" in step.get("run", "") for step in steps[:index])
    assert steps[index]["run"] == "uv run --no-sync python -m scripts.ci_model_settings_connection"
    assert "real-model.yml" not in str(workflow)


def test_dotenv_and_saved_credentials_are_private_and_removed(monkeypatch):
    import os
    import stat
    from pathlib import Path

    from scripts import ci_model_settings_connection as module

    original = module.Settings
    paths = []

    def settings(**kwargs):
        dotenv = Path(kwargs["_env_file"])
        paths.append(dotenv.parent)
        if os.name == "posix":
            assert stat.S_IMODE(dotenv.stat().st_mode) == 0o600
            assert stat.S_IMODE(dotenv.parent.stat().st_mode) == 0o700
        return original(**kwargs)

    monkeypatch.setattr(module, "Settings", settings)
    result = acceptance(VALUES, transport=httpx.MockTransport(lambda request: completion()))
    assert result["code"] == "passed"
    assert paths and not paths[0].exists()


def test_tls_failure_is_static_and_never_retried():
    import ssl

    calls = []

    def handle(request):
        calls.append(request)
        try:
            raise ssl.SSLCertVerificationError("untrusted certificate " + VALUES["API_KEY"])
        except ssl.SSLCertVerificationError as exc:
            raise httpx.ConnectError("TLS failed", request=request) from exc

    result = acceptance(VALUES, transport=httpx.MockTransport(handle))
    assert result["code"] == "probe_failed"
    assert result["probe"]["code"] == "tls_certificate_verification_failed"
    assert result["inference_requests"] == len(calls) == 1
    assert VALUES["API_KEY"] not in json.dumps(result)


def test_browser_job_is_independent_and_has_only_fixture_access():
    from pathlib import Path

    import yaml

    workflow = yaml.safe_load(Path(".github/workflows/model-settings-connection.yml").read_text())
    browser = workflow["jobs"]["browser"]
    assert "environment" not in browser and "needs" not in browser
    assert "secrets." not in str(browser)
    assert "API_KEY" not in str(browser)
    assert browser["timeout-minutes"] == 15
    assert "github.run_attempt == 1" in browser["if"]
    steps = browser["steps"]
    assert any(step.get("with", {}).get("node-version") == "22" for step in steps)
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "playwright@1.56.1" in commands
    assert "npm ci --prefix ui" in commands and "npm run build --prefix ui" in commands
    assert "npm ci --prefix tools/node" in commands
    assert "python -m scripts.ci_guided_browser" in commands
    assert "ci_model_settings_connection" not in commands and "ci_real_model" not in commands
    upload = steps[-1]
    assert upload["if"] == "always()"
    paths = upload["with"]["path"].splitlines()
    assert all(path.startswith("reports/guided-browser/") for path in paths)
    assert not any(".env" in path or "input" in path or "config" in path for path in paths)
