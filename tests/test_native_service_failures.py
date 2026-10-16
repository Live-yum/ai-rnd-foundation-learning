"""Docker errors after successful process spawn must not bypass authorization."""

import sys
from types import SimpleNamespace

import pytest
from test_source_candidate_delivery import native_plan

from workbench.delivery import native
from workbench.infrastructure.native import resources
from workbench.infrastructure.processes import tools


@pytest.mark.parametrize(
    "diagnostic,expected",
    [
        ("permission denied while trying to connect to the Docker daemon socket", PermissionError),
        ("Cannot connect to the Docker daemon: access is denied", PermissionError),
        ("Cannot connect to the Docker daemon: operation not permitted", PermissionError),
        (
            "Cannot connect to the Docker daemon. Is the docker daemon running?",
            resources.NativeServiceUnavailable,
        ),
        (
            "docker: 'compose' is not a docker command.\nSee 'docker --help'",
            resources.NativeServiceUnavailable,
        ),
        (
            'docker: unknown command "compose" for "docker"',
            resources.NativeServiceUnavailable,
        ),
        (
            "docker: 'compose' is not a docker command.\nPermission denied",
            PermissionError,
        ),
        (
            'unknown command "compose" for "docker"\nAccess is denied',
            PermissionError,
        ),
        ('unknown command "up" for "docker compose"', tools.ToolFailure),
        ("unknown shorthand flag: 'f' in -f", tools.ToolFailure),
        ("compose plugin failed to execute", tools.ToolFailure),
        ("unclassified server failure", tools.ToolFailure),
    ],
)
def test_service_exit_classification_uses_real_tool_failure(
    tmp_path, monkeypatch, diagnostic, expected
):
    def command(*args):
        return tools.run_command(
            [sys.executable, "-c", f"import sys; print({diagnostic!r}); sys.exit(1)"], tmp_path
        )

    monkeypatch.setattr(resources, "run_command", command)
    with pytest.raises(expected) as failure:
        resources.start_services(["docker", "compose"], tmp_path)
    assert type(failure.value) is expected


@pytest.mark.parametrize("known_unavailable", [False, True])
def test_managed_generation_only_downgrades_classified_service_unavailability(
    settings, monkeypatch, known_unavailable
):
    from workbench.delivery import source_candidate

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    error = (
        resources.NativeServiceUnavailable("daemon stopped")
        if known_unavailable
        else tools.ToolFailure("unknown failure")
    )

    def fail(*args):
        raise error

    monkeypatch.setattr(resources, "for_run", fail)
    calls = []
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *args: calls.append(args) or {"candidate": True},
    )
    product = settings.data_dir / "runs/service-error/product"
    if known_unavailable:
        assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == {
            "candidate": True
        }
        assert len(calls) == 1
    else:
        with pytest.raises(tools.ToolFailure):
            native.managed_generate(settings, "fastapiadmin", native_plan(), product)
        assert calls == []


def rule_plan():
    from workbench.core.contracts import CustomRule

    plan = native_plan()
    plan.custom_rules = [
        CustomRule(
            entity="task",
            description="Title must start with ok",
            accept_examples=[{"title": "ok task"}],
            reject_examples=[{"title": "bad task"}],
        )
    ]
    return plan


@pytest.mark.parametrize(
    "engine,enabled", [("bounded", True), ("bounded", False), ("aider", False)]
)
def test_unavailable_rule_coder_retains_source_before_any_runtime_effect(
    settings, monkeypatch, engine, enabled
):
    from workbench.delivery import source_candidate

    settings.coding_engine, settings.enable_coding = engine, enabled
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})

    def forbidden(*args):
        raise AssertionError("runtime services or coder must not execute")

    monkeypatch.setattr(resources, "for_run", forbidden)
    monkeypatch.setattr(native, "runtime_config", forbidden)
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    product = settings.data_dir / "runs/rule-capability/product"
    result = native.managed_generate(
        settings, "fastapiadmin", rule_plan(), product, customization=forbidden
    )
    assert result["execution"] == "source-candidate"
    assert result["generation_status"] == "partial"
    assert result["runtime_verified"] is False
    assert "CODING_ENGINE=aider" in result["runtime_unavailable_reason"]
    assert result["pending_steps"]


def test_available_rule_coder_reaches_strict_runtime_path(settings, monkeypatch):
    from workbench.coding import aider

    monkeypatch.setattr(aider, "executable", lambda settings: "configured-locked-interpreter")
    settings.coding_engine, settings.enable_coding = "aider", True
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )

    def reached(*args):
        raise PermissionError("runtime service authorization remains required")

    monkeypatch.setattr(resources, "for_run", reached)
    product = settings.data_dir / "runs/rule-runtime/product"
    with pytest.raises(PermissionError):
        native.managed_generate(settings, "fastapiadmin", rule_plan(), product)
    assert not product.exists()


def test_missing_docker_has_no_service_filesystem_side_effect(settings, monkeypatch):
    monkeypatch.setattr(resources.shutil, "which", lambda name: None)
    with pytest.raises(resources.NativeServiceUnavailable):
        resources.for_run(settings, "missing-docker")
    assert not (settings.data_dir / "native-services/missing-docker").exists()


def test_existing_managed_receipt_cannot_be_downgraded_for_missing_rule_coder(
    settings, monkeypatch
):
    from workbench.core.contracts import digest
    from workbench.filesystem import write_json
    from workbench.generation.python_basic import PrerequisiteError

    settings.coding_engine = "bounded"
    plan = rule_plan()
    product = settings.data_dir / "runs/existing-runtime/product"
    write_json(
        product.parent / "native-generation.json",
        {
            "execution": "managed-runtime",
            "template": "fastapiadmin",
            "spec_digest": digest(plan.model_dump()),
        },
    )
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    with pytest.raises(PrerequisiteError, match="不能自动降级"):
        native.managed_generate(settings, "fastapiadmin", plan, product)
    assert not product.exists()


def test_missing_aider_tool_environment_stays_source_only(settings, monkeypatch):
    from workbench.coding import aider
    from workbench.delivery import source_candidate

    settings.coding_engine, settings.enable_coding = "aider", True
    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})

    def missing(settings):
        raise ValueError("missing interpreter")

    monkeypatch.setattr(aider, "executable", missing)
    monkeypatch.setattr(source_candidate, "generate_candidate", lambda *args: {"reason": args[-1]})
    product = settings.data_dir / "runs/missing-aider/product"
    result = native.managed_generate(settings, "fastapiadmin", rule_plan(), product)
    assert "Aider" in result["reason"]
    assert not (settings.data_dir / "native-services").exists()


@pytest.mark.parametrize("command", [["docker", "inspect"], ["other", "compose"]])
def test_missing_compose_diagnostic_requires_compose_command(tmp_path, monkeypatch, command):
    def failed(*args):
        error = tools.ToolFailure("failed")
        error.log = "docker: 'compose' is not a docker command."
        raise error

    monkeypatch.setattr(resources, "run_command", failed)
    with pytest.raises(tools.ToolFailure) as failure:
        resources.start_services(command, tmp_path)
    assert type(failure.value) is tools.ToolFailure


def test_missing_compose_reaches_source_fallback(settings, monkeypatch):
    from workbench.delivery import source_candidate

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    monkeypatch.setattr(resources.shutil, "which", lambda name: "docker")

    def missing_plugin(command, folder, timeout):
        assert command[:2] == ["docker", "compose"]
        return tools.run_command(
            [
                sys.executable,
                "-c",
                "import sys; print(\"docker: 'compose' is not a docker command.\"); sys.exit(1)",
            ],
            folder,
        )

    monkeypatch.setattr(resources, "run_command", missing_plugin)
    calls = []
    monkeypatch.setattr(
        source_candidate,
        "generate_candidate",
        lambda *args: calls.append(args) or {"execution": "source-candidate"},
    )
    product = settings.data_dir / "runs/missing-compose/product"
    result = native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert result == {"execution": "source-candidate"}
    assert len(calls) == 1
    assert not product.exists()
