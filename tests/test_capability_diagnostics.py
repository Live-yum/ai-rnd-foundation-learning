"""Exercise verifier child failure through the live artifact filter, offline."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ci_live_modules import verify_with_diagnostics
from workbench.capability_diagnostics import node_diagnostic, record_failure
from workbench.generator import PrerequisiteError


def test_real_child_failure_survives_parent_raise_and_temporary_workspace(
    settings, tmp_path, monkeypatch
):
    import workbench.capability_dependencies as dependencies
    import workbench.capability_execution as execution
    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier

    product = tmp_path / "product"
    plan = fixed_application(product)
    monkeypatch.setattr(execution, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(dependencies, "require_dependency_descriptors", lambda *a: None)
    original = subprocess.Popen
    child = """from workbench import capability_sandbox as v
def fail(payload):
    raise ValueError('private-url key headers prompt candidate-source')
v._execute_payload=fail
v.main()
"""

    def launch(command, **kwargs):
        return original([sys.executable, "-c", child], **kwargs)

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    stale = Path(str(product.parent / "product-node-verification.json") + ".diagnostic.json")
    stale.write_text(json.dumps({"exception_type": "TypeError", "stage": "sandbox_transport"}))
    progress = {}
    with pytest.raises(PrerequisiteError, match="验证进程失败"):
        verify_with_diagnostics(
            verifier.verify_capabilities,
            product,
            plan,
            plan.scenarios,
            settings,
            aggregate=False,
            selection=plan.selection.model_dump(),
            progress=progress,
        )
    receipt = progress["verification_receipts"][0]
    assert receipt["exception_type"] == "ValueError"
    assert receipt["stage"] == "verifier_controller"
    assert receipt["passed"] is False
    assert receipt["cleanup"] == "not-started"
    assert type(receipt["trusted_source_line"]) is int
    for path in tmp_path.glob("*verification.json*"):
        path.unlink()
    assert "private" not in json.dumps(progress)
    assert progress["verification_receipts"][0] == receipt


@pytest.mark.parametrize("corruption", ["missing", "invalid", "oversized", "poisoned"])
def test_node_artifact_whitelist_rejects_content_and_bounds_reads(tmp_path, corruption):
    product = tmp_path / "product"
    path = tmp_path / "product-node-verification.json"
    sidecar = Path(str(path) + ".diagnostic.json")
    raw = {
        "passed": True,
        "cleanup": "private",
        "checks": ["private"] * 2,
        "error": "private-key",
        "build_diagnostic": "private-source",
        "sandbox_name": "private-name",
        "startup_diagnostic": {"headers": "private"},
        "restarted": 1,
    }
    if corruption != "missing":
        path.write_text(
            "!invalid"
            if corruption == "invalid"
            else "x" * 1_000_001
            if corruption == "oversized"
            else json.dumps(raw)
        )
    sidecar.write_text(
        json.dumps(
            {
                "exception_type": "private",
                "stage": "private",
                "trusted_source_line": True,
                "error": "private",
            }
        )
    )
    result = node_diagnostic(product, aggregate=False)
    assert "private" not in json.dumps(result)
    assert "trusted_source_line" not in result
    assert result["restarted"] is None
    assert result["cleanup"] == "other"
    assert result["checks_count"] == (2 if corruption == "poisoned" else None)


def test_record_failure_io_error_preserves_original_exception(tmp_path, monkeypatch):
    import workbench.filesystem as filesystem

    def fail(*args):
        raise PermissionError("private")

    monkeypatch.setattr(filesystem, "write_json", fail)
    error = ValueError("private-original")
    with pytest.raises(ValueError) as found:
        try:
            raise error
        except ValueError as exc:
            record_failure(tmp_path / "receipt.json", exc)
            raise
    assert found.value is error


def test_actual_verifier_child_retains_exact_policy_and_receipt(monkeypatch, tmp_path, settings):
    from test_capability_browser_policy import IMAGE, approved_manual

    import workbench.capability_dependencies as dependencies
    import workbench.capability_execution as execution
    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_browser_isolation as isolation
    from workbench import capability_sandbox as verifier

    approved_manual(monkeypatch)
    monkeypatch.setenv("API_KEY", "private-model-key")
    monkeypatch.setenv("GITHUB_TOKEN", "private-github-token")
    monkeypatch.setenv("HTTP_PROXY", "private-proxy")
    product = tmp_path / "product"
    plan = fixed_application(product)
    browser_receipt = {
        "protocol": "offline-browser-isolation-v3",
        "passed": True,
        "mocked": False,
        "image": IMAGE,
        "runtime": {"fixture_approved_runtime": True},
        "sources": isolation.browser_source_identity(),
        "image_sources": isolation.image_source_identity(),
        "checks": {
            "kernel_and_network": {
                key: True
                for key in (
                    "passed",
                    "kernel_resource_limits",
                    "network_none",
                    "tmpfs_exhaustion",
                    "pid_exhaustion",
                    "readonly_root",
                    "browser_build",
                    "apparmor_enforced",
                )
            },
            **{
                key: True
                for key in (
                    "positive",
                    "error",
                    "abuse",
                    "failure_cleanup",
                    "memory_exhaustion",
                    "raw_syscalls",
                )
            },
        },
    }
    (tmp_path / "browser.json").write_text(json.dumps(browser_receipt))
    monkeypatch.setattr(execution, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(dependencies, "require_dependency_descriptors", lambda *a: None)
    original = subprocess.Popen
    child = """import json, os
from pathlib import Path
from workbench import capability_sandbox as v
from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy
def inspect(payload):
    assert not any(k in os.environ for k in ('API_KEY', 'GITHUB_TOKEN', 'HTTP_PROXY'))
    path=Path(payload['receipt'])
    isolation.BROWSER_ACCEPTANCE=path.parent/'browser.json'
    isolation.runtime_identity=lambda image: ({'fixture_approved_runtime':True} if policy.selected_policy() else {'policy_sha256':None,'mode':'docker-default'})
    assert isolation.require_browser_acceptance('sha256:'+'a'*64)
    path.write_text(json.dumps({'passed':True,'cleanup':'deleted'}))
v._execute_payload=inspect
v.main()
"""

    def launch(command, **kwargs):
        return original([sys.executable, "-c", child], **kwargs)

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    proof = verifier.verify_capabilities(
        product,
        plan,
        plan.scenarios,
        settings,
        aggregate=False,
        selection=plan.selection.model_dump(),
    )
    assert proof == {"passed": True, "cleanup": "deleted"}  # Mock proof, not product acceptance.


@pytest.mark.parametrize(
    "field,value",
    [
        ("GITHUB_JOB", "other"),
        ("LIVE_SCENARIO", "other"),
        ("GITHUB_RUN_ATTEMPT", "2"),
        ("REVIEWED_SHA", "b" * 40),
        ("GITHUB_WORKFLOW_SHA", "b" * 40),
        ("GITHUB_EVENT_NAME", "pull_request"),
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_WORKFLOW_REF", "other.yml@refs/heads/main"),
    ],
)
def test_verifier_policy_forwarding_rejects_changed_scope(monkeypatch, field, value):
    from test_capability_browser_policy import approved_manual

    from workbench.capability_sandbox import verifier_policy_environment

    approved_manual(monkeypatch)
    monkeypatch.setenv(field, value)
    with pytest.raises(ValueError, match="approved Actions scope"):
        verifier_policy_environment()


def test_verifier_policy_forwarding_is_off_by_default_and_does_not_change_clean_env(monkeypatch):
    from test_capability_browser_policy import approved_manual

    from workbench.capability_sandbox import verifier_policy_environment
    from workbench.tools import clean_env

    approved_manual(monkeypatch)
    assert verifier_policy_environment()["GITHUB_JOB"] == "mini-swe-sla"
    assert "GITHUB_JOB" not in clean_env()
    assert "CAPABILITY_BROWSER_APPROVED_POLICY" not in clean_env()
    monkeypatch.delenv("CAPABILITY_BROWSER_APPROVED_POLICY")
    assert verifier_policy_environment() == {}


def test_stale_diagnostic_cannot_explain_a_new_receipt(tmp_path):
    import os

    product = tmp_path / "product"
    path = tmp_path / "product-node-verification.json"
    sidecar = Path(str(path) + ".diagnostic.json")
    sidecar.write_text(json.dumps({"exception_type": "ValueError", "stage": "verifier_controller"}))
    os.utime(sidecar, ns=(1_000_000_000, 1_000_000_000))
    path.write_text(json.dumps({"passed": False, "cleanup": "not-started"}))
    assert node_diagnostic(product, aggregate=False)["exception_type"] == "other"
