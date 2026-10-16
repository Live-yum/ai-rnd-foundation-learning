"""Initial source publication survives failures without adopting unknown content."""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from workbench.core.contracts import digest
from workbench.delivery import native
from workbench.delivery import source_candidate as candidate
from workbench.filesystem import manifest
from workbench.generation.python_basic import PrerequisiteError

REAL_WHICH = shutil.which


@pytest.fixture
def initial(tmp_path, monkeypatch, plan):
    from workbench.generation.native import offline, service
    from workbench.templates import standards

    plan = plan.model_copy(update={"data_scope": "shared"})
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    (upstream / "base.txt").write_text("trusted baseline\n", encoding="utf-8")
    source = {
        "slot": "fastapiadmin",
        "path": str(upstream),
        "source_digest": digest(manifest(upstream)),
    }
    monkeypatch.setattr(service, "prepare_sources", lambda *args: [source])
    monkeypatch.setattr(standards, "write_coding_standard", lambda *args: None)
    monkeypatch.setattr(candidate.shutil, "which", lambda _: None)

    def generate(template, plan, destination, sources):
        (destination / "business.py").write_text("value = 42\n", encoding="utf-8")
        return {
            "generation_status": "partial",
            "pending_steps": ["runtime verification"],
            "generated_files": ["business.py"],
        }

    monkeypatch.setattr(offline, "generate_offline", generate)
    product = tmp_path / "run/product"
    product.parent.mkdir()
    (product.parent / "design.json").write_text('{"approved": true}\n', encoding="utf-8")
    return SimpleNamespace(
        product=product, plan=plan, settings=SimpleNamespace(), generate=generate
    )


def build(initial):
    return candidate.generate_candidate(
        initial.settings, "fastapiadmin", initial.plan, initial.product, "no runtime"
    )


@pytest.mark.parametrize("window", ["copy", "generate", "status", "snapshot", "receipt"])
def test_preparation_failure_leaves_no_product_and_retry_succeeds(initial, monkeypatch, window):
    from workbench.generation.native import offline
    from workbench.infrastructure.native import environment

    owner, name = {
        "copy": (environment, "copy_source"),
        "generate": (offline, "generate_offline"),
        "status": (candidate, "write_status"),
        "snapshot": (candidate, "source_snapshot"),
        "receipt": (candidate, "refresh_candidate"),
    }[window]
    original = getattr(owner, name)

    def failed(*args, **kwargs):
        original(*args, **kwargs)
        raise PermissionError("injected preparation failure")

    monkeypatch.setattr(owner, name, failed)
    with pytest.raises(PermissionError):
        build(initial)
    assert not initial.product.exists()
    assert sorted(path.name for path in initial.product.parent.iterdir()) == ["design.json"]
    monkeypatch.setattr(owner, name, original)
    receipt = build(initial)
    assert candidate.verify_candidate(initial.product, receipt)["source_checks_passed"]


@pytest.mark.parametrize("item", ["product", "verification.json", "native-generation.json"])
@pytest.mark.parametrize("after", [False, True])
def test_publication_failure_resumes_before_capability_changes(initial, monkeypatch, item, after):
    original = candidate._publish_new
    raised = False

    def interrupted(path, target):
        nonlocal raised
        if Path(target) == initial.product.parent / item and not raised:
            raised = True
            if after:
                original(path, target)
            raise SystemExit("simulated process interruption")
        return original(path, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)

    def forbidden(*args, **kwargs):
        raise AssertionError("Recovery must precede capability discovery")

    monkeypatch.setattr(native, "generation_capability", forbidden)
    result = native.managed_generate(
        initial.settings, "fastapiadmin", initial.plan, initial.product
    )
    assert result["execution"] == "source-candidate"
    assert not (initial.product.parent / ".source-candidate-transaction").exists()
    assert (
        native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.product)
        == result
    )


def interrupted_transaction(initial, monkeypatch):
    original = candidate._publish_new

    def interrupted(path, target):
        if Path(target) == initial.product:
            raise SystemExit("before first publication")
        return original(path, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)
    return initial.product.parent / ".source-candidate-transaction"


@pytest.mark.parametrize("tamper", ["unknown_product", "extra_secret", "receipt", "plan", "stage"])
def test_recovery_never_adopts_unknown_or_changed_content(initial, monkeypatch, tamper):
    transaction = interrupted_transaction(initial, monkeypatch)
    if tamper == "unknown_product":
        initial.product.mkdir()
        (initial.product / "mine.txt").write_text("user content", encoding="utf-8")
    elif tamper == "extra_secret":
        (transaction / "candidate/product/.env").write_text("PRIVATE=secret", encoding="utf-8")
    elif tamper == "receipt":
        (transaction / "candidate/native-generation.json").write_text("{}", encoding="utf-8")
    elif tamper == "plan":
        initial.plan = initial.plan.model_copy(update={"title": "different approval"})
    else:
        (transaction / "candidate/product/business.py").write_text("tampered", encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        build(initial)
    if tamper == "unknown_product":
        assert (initial.product / "mine.txt").read_text(encoding="utf-8") == "user content"


def test_completed_transaction_does_not_block_legitimate_refresh(initial):
    receipt = build(initial)
    receipt = candidate.refresh_candidate(initial.product, receipt, pending_steps=["new review"])
    assert (
        native.managed_generate(initial.settings, "fastapiadmin", initial.plan, initial.product)
        == receipt
    )
    assert json.loads((initial.product.parent / "design.json").read_text(encoding="utf-8")) == {
        "approved": True
    }


@pytest.mark.parametrize("item", ["product", "verification.json", "native-generation.json"])
def test_real_process_exit_after_publication_can_resume(tmp_path, plan, monkeypatch, item):
    import subprocess
    import sys

    plan = plan.model_copy(update={"data_scope": "shared"})
    root = tmp_path / "child"
    root.mkdir()
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(plan.model_dump_json(), encoding="utf-8")
    script = r"""
import os, runpy, sys
from pathlib import Path
import pytest
from workbench.core.contracts import Plan
ns = runpy.run_path(sys.argv[1])
root = Path(sys.argv[2])
plan = Plan.model_validate_json(Path(sys.argv[3]).read_text(encoding="utf-8"))
fixture = ns["initial"].__wrapped__(root, pytest.MonkeyPatch(), plan)
candidate = ns["candidate"]
original = candidate._publish_new
def crash(path, target):
    result = original(path, target)
    if Path(target) == fixture.product.parent / sys.argv[4]:
        os._exit(73)
    return result
candidate._publish_new = crash
ns["build"](fixture)
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(Path(__file__).resolve()),
            str(root),
            str(plan_path),
            item,
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 73, result.stderr

    def forbidden(*args, **kwargs):
        raise AssertionError("Process recovery must precede runtime selection")

    monkeypatch.setattr(native, "generation_capability", forbidden)
    product = root / "run/product"
    receipt = native.managed_generate(SimpleNamespace(), "fastapiadmin", plan, product)
    assert candidate.verify_candidate(product, receipt)["source_checks_passed"]
    assert not (product.parent / ".source-candidate-transaction").exists()


@pytest.mark.parametrize("directory", [False, True])
def test_no_replace_preserves_existing_even_empty_target(tmp_path, directory):
    source, target = tmp_path / "source", tmp_path / "target"
    if directory:
        source.mkdir()
        target.mkdir()
        (source / "business.txt").write_text("source", encoding="utf-8")
    else:
        source.write_text("source", encoding="utf-8")
        target.write_text("user content", encoding="utf-8")
    with pytest.raises(FileExistsError):
        candidate._publish_new(source, target)
    if directory:
        assert list(target.iterdir()) == []
    else:
        assert target.read_text(encoding="utf-8") == "user content"
    assert source.exists()


@pytest.mark.parametrize("item", ["product", "native-generation.json"])
def test_target_created_after_preflight_is_not_overwritten(initial, monkeypatch, item):
    original = candidate._publish_new

    def raced(source, target):
        if Path(target) == initial.product.parent / item:
            if item == "product":
                Path(target).mkdir()
            else:
                Path(target).write_text("user content", encoding="utf-8")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", raced)
    with pytest.raises(FileExistsError):
        build(initial)
    target = initial.product.parent / item
    assert (
        (list(target.iterdir()) == [])
        if item == "product"
        else target.read_text(encoding="utf-8") == "user content"
    )


@pytest.mark.parametrize("window", ["marker", "retire"])
@pytest.mark.parametrize("after", [False, True])
def test_marker_publication_and_retirement_failures_are_recoverable(
    initial, monkeypatch, window, after
):
    original = candidate._publish_new
    raised = False

    def interrupted(source, target):
        nonlocal raised
        match = (
            (Path(target).name == ".source-candidate-transaction")
            if window == "marker"
            else (Path(source).name == ".source-candidate-transaction")
        )
        if match and not raised:
            raised = True
            if after:
                original(source, target)
            raise SystemExit("marker interruption")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", interrupted)
    with pytest.raises(SystemExit):
        build(initial)
    monkeypatch.setattr(candidate, "_publish_new", original)
    monkeypatch.setattr(
        native, "generation_capability", lambda *args: {"available": False, "reason": "offline"}
    )
    result = native.managed_generate(
        initial.settings, "fastapiadmin", initial.plan, initial.product
    )
    assert result["execution"] == "source-candidate"
    assert not (initial.product.parent / ".source-candidate-transaction").exists()


@pytest.mark.parametrize("after", [False, True])
def test_git_journal_publication_resumes_without_git(initial, monkeypatch, after):
    if not REAL_WHICH("git"):
        pytest.skip("Git is required")
    monkeypatch.setattr(candidate.shutil, "which", REAL_WHICH)
    original = candidate._publish_new
    interrupted = False

    def crash(source, target):
        nonlocal interrupted
        if Path(target) == initial.product.parent / "source-revisions" and not interrupted:
            interrupted = True
            if after:
                original(source, target)
            raise SystemExit("journal interrupted")
        return original(source, target)

    monkeypatch.setattr(candidate, "_publish_new", crash)
    with pytest.raises(SystemExit):
        build(initial)
    transaction = initial.product.parent / ".source-candidate-transaction"
    sealed_report = (transaction / "candidate/verification.json").read_bytes()
    monkeypatch.setattr(candidate, "_publish_new", original)
    monkeypatch.setattr(candidate.shutil, "which", lambda _: None)
    receipt = candidate.recover_candidate("fastapiadmin", initial.plan, initial.product)
    assert receipt["source_commit"]["status"] == "committed"
    assert (initial.product.parent / "verification.json").read_bytes() == sealed_report
    assert (
        candidate.verify_candidate(initial.product, receipt)["source_commit"]["status"]
        == "unavailable"
    )
