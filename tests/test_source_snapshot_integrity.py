"""A cached source receipt is evidence only while its real Git tree still matches."""

import json
import shutil
import subprocess

import pytest

from workbench.delivery.source_candidate import source_snapshot
from workbench.generation.python_basic import PrerequisiteError


@pytest.fixture
def snapshot(tmp_path):
    if not shutil.which("git"):
        pytest.skip("Git is required for repository integrity tests")
    product = tmp_path / "product"
    product.mkdir()
    (product / "binary.dat").write_bytes(b"\x00\xff\r\n")
    (product / "source.py").write_text("value = 3\n", encoding="utf-8")
    (product / "nested").mkdir()
    (product / "nested/中文 file.txt").write_text("保留\n", encoding="utf-8")
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    work = tmp_path / receipt["journal"]
    return product, work, receipt


def git(work, *args):
    return subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@localhost", "-C", str(work), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_valid_cache_checks_real_binary_and_nested_tree(snapshot):
    product, _, receipt = snapshot
    assert source_snapshot(product) == receipt


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_digest", "f" * 64),
        ("journal", "../../forged"),
        ("commit", "f" * 40),
        ("runtime_verified", True),
        ("status", "accepted"),
        ("extra", "forged"),
    ],
)
def test_forged_receipt_is_rejected(snapshot, field, value):
    product, work, receipt = snapshot
    receipt[field] = value
    (work.parent / "commit.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)


@pytest.mark.parametrize("removal", [".git", "receipt"])
def test_deleted_git_or_receipt_fails_closed(snapshot, removal):
    product, work, _ = snapshot
    if removal == ".git":
        shutil.rmtree(work / ".git")
    else:
        (work.parent / "commit.json").unlink()
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)


def test_head_moved_to_different_commit_with_same_tree(snapshot):
    product, work, _ = snapshot
    git(work, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "Different HEAD")
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)


def test_forged_commit_for_different_tree_even_when_worktree_matches(snapshot):
    product, work, receipt = snapshot
    (work / "source.py").write_text("forged = True\n", encoding="utf-8")
    git(work, "add", "source.py")
    git(work, "-c", "commit.gpgsign=false", "commit", "-qm", "Forged tree")
    receipt["commit"] = git(work, "rev-parse", "HEAD")
    (work.parent / "commit.json").write_text(json.dumps(receipt), encoding="utf-8")
    (work / "source.py").write_bytes((product / "source.py").read_bytes())
    git(work, "update-index", "--assume-unchanged", "source.py")
    with pytest.raises(PrerequisiteError, match="提交树"):
        source_snapshot(product)


@pytest.mark.parametrize("redirect", ["symlink", "gitfile"])
def test_external_git_directory_is_rejected(snapshot, tmp_path, redirect):
    product, work, _ = snapshot
    outside = tmp_path / "external.git"
    (work / ".git").rename(outside)
    if redirect == "symlink":
        try:
            (work / ".git").symlink_to(outside, target_is_directory=True)
        except OSError:
            pytest.skip("Host does not permit symlink creation")
    else:
        (work / ".git").write_text("gitdir: " + str(outside) + "\n", encoding="utf-8")
    with pytest.raises((PrerequisiteError, ValueError)):
        source_snapshot(product)


def test_git_missing_never_reuses_committed_claim(snapshot, monkeypatch):
    product, work, _ = snapshot
    monkeypatch.setattr("workbench.delivery.source_candidate.shutil.which", lambda name: None)
    result = source_snapshot(product)
    assert result["status"] == "unavailable"
    assert result["git_available"] is False
    assert "commit" not in result
    assert (work / "source.py").read_bytes() == (product / "source.py").read_bytes()


def test_permission_failure_is_not_downgraded(snapshot, monkeypatch):
    product, _, _ = snapshot
    from workbench.coding import aider

    def denied(*args, **kwargs):
        raise PermissionError("Denied")

    monkeypatch.setattr(aider, "git", denied)
    with pytest.raises(PermissionError):
        source_snapshot(product)


def test_corrupt_git_object_fails_closed(snapshot):
    product, work, receipt = snapshot
    oid = receipt["commit"]
    object_path = work / ".git/objects" / oid[:2] / oid[2:]
    object_path.unlink()
    object_path.write_bytes(b"corrupt")
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)


def test_new_snapshot_does_not_apply_source_attributes(tmp_path):
    product = tmp_path / "product"
    product.mkdir()
    (product / ".gitattributes").write_text(
        "*.txt text eol=lf\n*.dat working-tree-encoding=UTF-16\n", encoding="utf-8"
    )
    (product / "lines.txt").write_bytes(b"first\r\nsecond\r\n")
    (product / "binary.dat").write_bytes(b"\x00\xff")
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    assert source_snapshot(product) == receipt


@pytest.mark.parametrize("setting", ["core.fsmonitor", "include.path", "remote.origin.promisor"])
def test_external_or_executable_git_configuration_fails_closed(snapshot, setting):
    product, work, _ = snapshot
    git(work, "config", "--local", setting, "/untrusted/external")
    with pytest.raises(PrerequisiteError, match="配置"):
        source_snapshot(product)


def test_external_object_alternates_fail_closed(snapshot):
    product, work, _ = snapshot
    (work / ".git/objects/info/alternates").write_text("/untrusted/objects\n", encoding="utf-8")
    with pytest.raises(PrerequisiteError, match="外部"):
        source_snapshot(product)


def test_changed_worktree_mode_is_not_hidden_by_manifest(snapshot):
    import os

    if os.name == "nt":
        pytest.skip("Windows does not preserve POSIX executable modes")
    product, work, _ = snapshot
    (work / "source.py").chmod(0o755)
    with pytest.raises(PrerequisiteError, match="权限"):
        source_snapshot(product)


@pytest.mark.parametrize("metadata", ["info/grafts", "shallow"])
def test_history_rewriting_metadata_is_rejected_before_git(snapshot, monkeypatch, metadata):
    product, journal, receipt = snapshot
    from workbench.coding import aider

    (journal / ".git" / metadata).write_text(receipt["commit"] + "\n", encoding="utf-8")

    def forbidden(*args, **kwargs):
        raise AssertionError("Untrusted Git history metadata must be rejected before Git")

    monkeypatch.setattr(aider, "git", forbidden)
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)
