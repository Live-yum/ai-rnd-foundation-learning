"""Native service fallback must not depend on unused Daytona configuration."""

import sys
from types import SimpleNamespace

import pytest
from conftest import requirement
from pydantic import SecretStr

from workbench.delivery import native, source_candidate
from workbench.generation.python_basic import PrerequisiteError
from workbench.infrastructure.native import resources
from workbench.infrastructure.processes.tools import ToolFailure
from workbench.infrastructure.sandbox.daytona import verification
from workbench.production import graph


def configure(settings, sandbox_config):
    settings.sandbox_provider = "daytona"
    settings.daytona_allow_local_execution = sandbox_config == "missing-snapshot"
    settings.daytona_api_url = "http://127.0.0.1:3000/api"
    settings.daytona_api_key = SecretStr("test-only-not-a-credential")
    settings.daytona_target = "local"
    settings.daytona_snapshot = ""
    settings.daytona_snapshots = {}


def design_flow(settings, plan, monkeypatch, template):
    selection = SimpleNamespace(
        capabilities=lambda: {"field_kinds": ["text", "integer", "boolean"]},
        model_dump=lambda: {"template": template},
    )
    monkeypatch.setattr(graph, "options_for_run", lambda run: selection)
    monkeypatch.setattr(graph, "coverage_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "business_gaps", lambda *args, **kwargs: [])
    monkeypatch.setattr(graph, "design_pack", lambda *args, **kwargs: {"tasks": []})
    monkeypatch.setattr(native, "generation_capability", lambda *args: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    flow = graph.Workflow(settings, SimpleNamespace(get_run=lambda run: {}), None)
    gates = []

    def gate(state, stage, data, actions, can_approve=True):
        gates.append((stage, data, actions, can_approve))
        return {"decision": "approve" if can_approve else "reject"}

    flow.gate = gate
    approved = (
        plan if template == "python-basic" else plan.model_copy(update={"data_scope": "shared"})
    )
    state = {
        "run_id": "native-route",
        "template": template,
        "round": 1,
        "plan": approved.model_dump(),
        "requirement": requirement().model_dump(),
    }
    return flow, state, gates, approved


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
@pytest.mark.parametrize("missing", ["docker", "compose", "daemon"])
def test_native_design_allows_later_service_source_fallback(
    settings, plan, monkeypatch, template, sandbox_config, missing
):
    configure(settings, sandbox_config)
    flow, state, gates, approved = design_flow(settings, plan, monkeypatch, template)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    monkeypatch.setattr(
        verification,
        "validate_configuration",
        lambda *args: pytest.fail("Source fallback must not require Daytona configuration"),
    )
    assert flow.design(state)["decision"] == "approve"
    assert gates[0][3] is True
    assert "sandbox_configuration" not in gates[0][1]["block_sources"]
    assert "approve" in gates[0][2]

    monkeypatch.setattr(
        resources.shutil, "which", lambda name: None if missing == "docker" else "docker"
    )

    def unavailable(*args):
        error = ToolFailure("service unavailable")
        error.log = (
            "docker: 'compose' is not a docker command."
            if missing == "compose"
            else "Cannot connect to the Docker daemon"
        )
        raise error

    monkeypatch.setattr(resources, "run_command", unavailable)
    calls = []
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *args: calls.append(args) or {"execution": "source-candidate"},
    )
    result = native.managed_generate(settings, template, approved, flow.product(state))
    assert result["execution"] == "source-candidate"
    assert len(calls) == 1
    state.update(
        native_generation=result, verification={"passed": False, "source_checks_passed": True}
    )
    assert flow.after_verify(state) == "package"


@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
def test_python_design_still_requires_daytona_configuration(
    settings, plan, monkeypatch, sandbox_config
):
    configure(settings, sandbox_config)
    flow, state, gates, _ = design_flow(settings, plan, monkeypatch, "python-basic")
    assert flow.design(state)["decision"] == "reject"
    assert gates[0][3] is False
    assert "sandbox_configuration" in gates[0][1]["block_sources"]


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
@pytest.mark.parametrize("sandbox_config", ["unapproved", "missing-snapshot"])
def test_actual_native_sandbox_revalidates_before_execution(
    settings, monkeypatch, template, sandbox_config
):
    configure(settings, sandbox_config)
    monkeypatch.setattr(
        verification,
        "verify_in_daytona",
        lambda *args: pytest.fail("Sandbox execution must remain gated"),
    )
    flow = graph.Workflow(settings, None, None)
    with pytest.raises(PrerequisiteError):
        flow.sandbox({"run_id": "runtime-route", "template": template})


@pytest.mark.parametrize("available", [None, 0, "yes"])
def test_unknown_native_capability_still_blocks_design(settings, plan, monkeypatch, available):
    configure(settings, "unapproved")
    flow, state, gates, _ = design_flow(settings, plan, monkeypatch, "fastapiadmin")
    monkeypatch.setattr(native, "generation_capability", lambda *args: {"available": available})
    assert flow.design(state)["decision"] == "reject"
    assert "native_validation_or_runtime" in gates[0][1]["block_sources"]
    assert "sandbox_configuration" not in gates[0][1]["block_sources"]
