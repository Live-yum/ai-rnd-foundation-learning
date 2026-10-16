"""Derived source drafts publish complete evidence without touching recovery sources."""

import json
import shutil

import pytest

from tests.test_source_candidate_delivery import minimal_candidate, native_plan
from workbench.core.contracts import digest
from workbench.delivery import source_candidate as candidates
from workbench.filesystem import manifest, write_json
from workbench.generation.python_basic import PrerequisiteError


def prepared(tmp_path, monkeypatch, retained):
    if retained:
        source = tmp_path / "product"
        source.mkdir()
        (source / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
        write_json(
            tmp_path / "native-evidence/recovery.json",
            {
                "files": manifest(source),
                "targets": [1],
                "stage": "validation-interrupted",
            },
        )
        monkeypatch.setattr(candidates.shutil, "which", lambda name: None)
        base = candidates.retain_failed_candidate(
            "fastapiadmin",
            native_plan(),
            source,
            [],
            "ToolFailure",
        )
    else:
        source, base = minimal_candidate(tmp_path, monkeypatch)
    edited = tmp_path / "attempt/product"
    shutil.copytree(source, edited)
    (edited / "example.py").write_text("VALUE = 2\n", encoding="utf-8")
    edit = {
        "before": manifest(source),
        "files": manifest(edited),
        "identity": "e" * 64,
        "task": "edit",
    }
    derivation = {
        "parent_receipt_digest": digest(base),
        "edit_identity": edit["identity"],
        "task": "edit",
        "approved_files": ["example.py"],
        "candidate_edit_files_digest": digest(edit["files"]),
    }
    args = (source, edited, tmp_path / "attempt/source/product", base, edit)
    kwargs = {
        "derivation": derivation,
        "pending_steps": ["运行验收"],
        "generated_files": ["example.py"],
    }
    return args, kwargs


@pytest.mark.parametrize("retained", [False, True])
@pytest.mark.parametrize("crash", [None, "status", "receipt"])
def test_derivation_atomic_recovery_and_replay(tmp_path, monkeypatch, retained, crash):
    args, kwargs = prepared(tmp_path, monkeypatch, retained)
    source, edited, destination, base, edit = args
    original = manifest(source)
    checkpoint = tmp_path / "native-evidence/recovery.json"
    before_checkpoint = checkpoint.read_bytes() if checkpoint.exists() else None
    raw_edit = manifest(edited)
    original_refresh = candidates.refresh_candidate
    original_status = candidates.write_status

    if crash == "status":

        def interrupted(*values):
            original_status(*values)
            raise RuntimeError("injected crash after status write")

        monkeypatch.setattr(candidates, "write_status", interrupted)
    elif crash == "receipt":

        def interrupted(*values, **options):
            original_refresh(*values, **options)
            raise RuntimeError("injected crash after native receipt write")

        monkeypatch.setattr(candidates, "refresh_candidate", interrupted)
    if crash:
        with pytest.raises(RuntimeError, match="injected crash"):
            candidates.derive_candidate(*args, **kwargs)
        assert not destination.parent.exists()
        monkeypatch.setattr(candidates, "refresh_candidate", original_refresh)
        monkeypatch.setattr(candidates, "write_status", original_status)
    result = candidates.derive_candidate(*args, **kwargs)
    assert candidates.derive_candidate(*args, **kwargs) == result
    candidates.verify_candidate(destination, result)
    assert result.get("preserve_runtime_files") is None
    assert result["verification_status"] == base["verification_status"]
    assert result["generation_status"] == base["generation_status"]
    assert result["source_derivation"]["parent_receipt_digest"] == digest(base)
    assert manifest(source) == original
    assert manifest(edited) == raw_edit
    if before_checkpoint is not None:
        assert checkpoint.read_bytes() == before_checkpoint
    assert not (destination.parent / "native-evidence/recovery.json").exists()


@pytest.mark.parametrize("retained", [False, True])
@pytest.mark.parametrize("attack", ["source", "raw-edit", "derived", "receipt"])
def test_derivation_never_adopts_unapproved_tampering(tmp_path, monkeypatch, retained, attack):
    args, kwargs = prepared(tmp_path, monkeypatch, retained)
    source, edited, destination, _, _ = args
    if attack in {"derived", "receipt"}:
        candidates.derive_candidate(*args, **kwargs)
    if attack == "receipt":
        path = destination.parent / "native-generation.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["source_derivation"]["task"] = "forged"
        write_json(path, value)
    else:
        target = {"source": source, "raw-edit": edited, "derived": destination}[attack]
        (target / "unapproved.py").write_text("UNAPPROVED = True\n", encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        candidates.derive_candidate(*args, **kwargs)


def test_published_derivation_git_journal_remains_valid_after_atomic_move(tmp_path, monkeypatch):
    if not shutil.which("git"):
        pytest.skip("Git not installed")
    args, kwargs = prepared(tmp_path, monkeypatch, False)
    monkeypatch.undo()
    from workbench.coding import aider

    original_git = aider.git
    paths = []

    def observed_git(work, home, *arguments):
        result = original_git(work, home, *arguments)
        if arguments[-2:] in {
            ("rev-parse", "--show-toplevel"),
            ("rev-parse", "--absolute-git-dir"),
        }:
            # Owned temporary paths only: diagnose real-platform spelling without
            # dumping config, command environments, product content or credentials.
            paths.append(
                {"query": arguments[-1], "reported": result["log"][:1200], "work": str(work)}
            )
        return result

    monkeypatch.setattr(aider, "git", observed_git)
    try:
        result = candidates.derive_candidate(*args, **kwargs)
    except PrerequisiteError as exc:
        exc.add_note(
            "Owned Git directory diagnostics: " + json.dumps(paths[-4:], ensure_ascii=True)
        )
        raise
    assert result["source_commit"]["status"] == "committed"
    assert candidates.verify_candidate(args[2], result)["source_commit"] == result["source_commit"]
    assert candidates.derive_candidate(*args, **kwargs) == result


def test_derivation_rejects_redirected_publish_directory(tmp_path, monkeypatch):
    args, kwargs = prepared(tmp_path, monkeypatch, False)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        args[2].parent.symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Directory symlinks are unavailable")
    with pytest.raises(ValueError, match="符号链接|junction"):
        candidates.derive_candidate(*args, **kwargs)
    assert list(outside.iterdir()) == []
