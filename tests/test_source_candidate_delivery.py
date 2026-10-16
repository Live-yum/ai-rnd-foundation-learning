"""Source preservation is portable; no runtime acceptance is inferred from a ZIP/commit."""

import json
import subprocess
import sys
import zipfile
from types import SimpleNamespace

import pytest

from workbench.core.contracts import Plan, digest
from workbench.delivery import native, source_candidate
from workbench.filesystem import manifest, write_json
from workbench.generation.native.service import package_native, verify_native
from workbench.generation.python_basic import PrerequisiteError


def native_plan():
    return Plan(
        title="任务",
        data_scope="shared",
        acceptance=["CRUD"],
        entities=[
            {"name": "task", "description": "任务", "fields": [{"name": "title", "kind": "text"}]}
        ],
    )


def minimal_candidate(tmp_path, monkeypatch, verification="unverified"):
    product = tmp_path / "product"
    product.mkdir()
    (product / "example.py").write_text("def add(a, b):\n    return a + b\n")
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    receipt = source_candidate.refresh_candidate(
        product,
        {
            "template": "fastapiadmin",
            "execution": "source-candidate",
            "spec_digest": digest(native_plan().model_dump()),
            "generation_status": "partial",
            "verification_status": verification,
            "pending_steps": ["运行验收"],
            "runtime_unavailable_reason": "无执行环境",
            "generated_files": ["example.py"],
        },
    )
    return product, receipt


@pytest.mark.parametrize("verification", ["unverified", "failed"])
def test_candidate_package_keeps_truth_and_filters_secrets(tmp_path, monkeypatch, verification):
    product, receipt = minimal_candidate(tmp_path, monkeypatch, verification)
    (product / ".env").write_text("SECRET=not-for-export")
    (product / "credentials.json").write_text("secret")
    (product / "logs").mkdir()
    (product / "logs/private.log").write_text("secret")
    report = verify_native(product)
    assert report["passed"] is False
    assert report["source_checks_passed"] is True
    delivery = package_native(product, report)
    assert delivery["verification_status"] == verification
    assert delivery["runtime_verified"] is delivery["production_ready"] is False
    assert delivery["source_commit"]["status"] == "unavailable"
    with zipfile.ZipFile(product.parent / delivery["package"]) as archive:
        assert not {".env", "credentials.json", "logs/private.log"} & set(archive.namelist())
        status = json.loads(archive.read("SOURCE-STATUS.json"))
        assert status["verification_status"] == verification
        assert status["generation_status"] == "partial"


def test_changed_sources_and_forged_runtime_report_fail_closed(tmp_path, monkeypatch):
    product, _ = minimal_candidate(tmp_path, monkeypatch)
    report = verify_native(product)
    with pytest.raises(PrerequisiteError):
        package_native(product, {**report, "passed": True})
    (product / "example.py").write_text("changed")
    with pytest.raises(PrerequisiteError):
        verify_native(product)


def test_candidate_retry_reuses_receipt_without_generation(tmp_path, monkeypatch, settings):
    product, receipt = minimal_candidate(tmp_path, monkeypatch)

    def forbidden(*args, **kwargs):
        raise AssertionError("Replay must not execute or regenerate")

    monkeypatch.setattr(native, "runtime_capability", forbidden)
    assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt


def test_failed_runtime_sources_and_recovery_checkpoint_remain_unchanged(tmp_path, monkeypatch):
    product = tmp_path / "product"
    product.mkdir()
    (product / "actual.py").write_text("print('generated business source')\n")
    before = manifest(product)
    checkpoint = tmp_path / "native-evidence/recovery.json"
    write_json(
        checkpoint,
        {
            "files": before,
            "targets": [{"entity": "task"}],
            "stage": "validation-interrupted",
            "resumable": True,
        },
    )
    raw = checkpoint.read_bytes()
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    receipt = source_candidate.retain_failed_candidate(
        "fastapiadmin", native_plan(), product, [], "ToolFailure"
    )
    assert receipt["verification_status"] == "failed"
    assert receipt["generation_status"] == "complete"
    assert manifest(product) == before
    assert checkpoint.read_bytes() == raw
    delivery = package_native(product, verify_native(product))
    with zipfile.ZipFile(tmp_path / delivery["package"]) as archive:
        assert json.loads(archive.read("SOURCE-STATUS.json"))["verification_status"] == "failed"
    assert manifest(product) == before


def test_runtime_integrity_error_not_reclassified(tmp_path, monkeypatch):
    product = tmp_path / "product"
    product.mkdir()
    (product / "changed.py").write_text("modified\n")
    write_json(tmp_path / "native-evidence/recovery.json", {"files": {}, "targets": [1]})
    with pytest.raises(PrerequisiteError):
        source_candidate.retain_failed_candidate(
            "fastapiadmin", native_plan(), product, [], "ToolFailure"
        )
    assert not (tmp_path / "native-generation.json").exists()


def test_real_git_snapshot_is_traceable_and_replayed(tmp_path):
    if not source_candidate.shutil.which("git"):
        pytest.skip("Git not installed")
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.py").write_text("value = 3\n")
    first = source_candidate.source_snapshot(product)
    assert first["status"] == "committed"
    assert source_candidate.source_snapshot(product) == first
    journal = tmp_path / first["journal"]
    result = subprocess.run(
        ["git", "-C", str(journal), "show", first["commit"] + ":source.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == "value = 3\n"


def test_git_snapshot_integrity_race_is_not_a_git_failure(tmp_path, monkeypatch):
    from workbench.coding import aider

    product = tmp_path / "product"
    product.mkdir()
    (product / "source.py").write_text("original\n")
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: "git")

    def raced_git(work, home, *args):
        if args[0] == "rev-parse":
            (product / "source.py").write_text("raced\n")
        return {"log": "a" * 40}

    monkeypatch.setattr(aider, "git", raced_git)
    with pytest.raises(PrerequisiteError, match="发生变化"):
        source_candidate.source_snapshot(product)


@pytest.mark.parametrize("error", [PermissionError("denied"), AssertionError("unclassified")])
def test_unclassified_or_permission_runtime_failure_cannot_become_candidate(
    settings, monkeypatch, error
):
    from workbench.generation.native import service

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: True)
    monkeypatch.setattr(
        native, "runtime_config", lambda *args: (None, "postgresql://localhost/test_codegen")
    )
    source = settings.data_dir / "source"
    source.mkdir(parents=True)
    (source / "code.py").write_text("source\n")
    monkeypatch.setattr(
        service, "prepare_sources", lambda *args: [{"slot": "fastapiadmin", "path": str(source)}]
    )

    def fail(*args, **kwargs):
        raise error

    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=fail)
    )
    product = settings.data_dir / "runs/failure/product"
    with pytest.raises(type(error)):
        native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert not (product.parent / "native-generation.json").exists()


def test_permission_failure_of_services_does_not_generate_fallback(settings, monkeypatch):
    from workbench.infrastructure.native import resources

    monkeypatch.setattr(native, "runtime_capability", lambda template: {"available": True})
    monkeypatch.setitem(
        sys.modules, "workbench.acceptance.native_lab", SimpleNamespace(run_acceptance=None)
    )
    monkeypatch.setattr(native, "runtime_enabled", lambda *args: False)

    def denied(*args):
        raise PermissionError("denied")

    monkeypatch.setattr(resources, "for_run", denied)
    product = settings.data_dir / "runs/failure/product"
    with pytest.raises(PermissionError):
        native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert not product.exists()


def test_fixed_tool_runner_preserves_actual_process_permission_denial(tmp_path, monkeypatch):
    from workbench.infrastructure.processes import tools

    def denied(*args, **kwargs):
        raise PermissionError("process permission denied")

    monkeypatch.setattr(tools.subprocess, "Popen", denied)
    with pytest.raises(PermissionError):
        tools.run_command(["git", "--version"], tmp_path)


@pytest.mark.parametrize("platform", ["win32", "darwin", "linux"])
def test_missing_runtime_generates_actual_sources_without_processes(
    settings, monkeypatch, platform
):
    # Native host tests also run this file in the CI OS matrix; these simulated
    # capability cases are not a substitute for actual Windows/macOS execution.
    monkeypatch.setattr(native, "sys", SimpleNamespace(platform=platform))
    monkeypatch.setattr(
        native, "os", SimpleNamespace(name="nt" if platform == "win32" else "posix")
    )

    def unavailable(name):
        raise ImportError(name)

    monkeypatch.setattr(native, "import_module", unavailable)
    monkeypatch.setattr(source_candidate.shutil, "which", lambda name: None)
    from workbench.infrastructure.processes import tools

    def no_execution(*args, **kwargs):
        raise AssertionError("No command or product code may run in source generation")

    monkeypatch.setattr(tools, "run_command", no_execution)
    product = settings.data_dir / "runs/offline/product"
    receipt = native.managed_generate(settings, "fastapiadmin", native_plan(), product)
    assert receipt["execution"] == "source-candidate"
    assert receipt["verification_status"] == "unverified"
    assert receipt["generation_status"] == "partial"
    assert (product / "backend/app/plugin/module_rnd/task/controller.py").is_file()
    assert len(receipt["generated_files"]) >= 8
    assert native.managed_generate(settings, "fastapiadmin", native_plan(), product) == receipt
