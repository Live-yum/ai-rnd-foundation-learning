"""A cached source receipt is evidence only while its real Git tree still matches."""

import json
import os
import shutil
import stat
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


@pytest.fixture
def windows_readonly_unlink(monkeypatch):
    """Enforce Windows read-only deletion semantics on POSIX runners too."""
    original = os.unlink

    def unlink(path, *args, **kwargs):
        mode = os.stat(path, dir_fd=kwargs.get("dir_fd"), follow_symlinks=False).st_mode
        if stat.S_ISREG(mode) and not mode & stat.S_IWUSR:
            raise PermissionError("fixture: Windows refuses deletion of read-only files")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)


@pytest.mark.parametrize("removal", [".git", "receipt"])
def test_deleted_git_or_receipt_fails_closed(snapshot, removal, windows_readonly_unlink):
    product, work, _ = snapshot
    if removal == ".git":
        # Git creates read-only objects on Windows. This test deliberately
        # destroys only its own temporary journal before testing fail-closed reuse.
        for path in (work / ".git/objects").rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
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


def test_corrupt_git_object_fails_closed(snapshot, windows_readonly_unlink):
    product, work, receipt = snapshot
    oid = receipt["commit"]
    object_path = work / ".git/objects" / oid[:2] / oid[2:]
    # Prepare the intentional corruption of this fixture-owned read-only object.
    object_path.chmod(object_path.stat().st_mode | stat.S_IWUSR)
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


@pytest.mark.parametrize("symlinks", ["false", "true"])
def test_git_init_filesystem_symlink_probe_metadata_is_portable(tmp_path, monkeypatch, symlinks):
    from workbench.coding import aider

    original = aider.git

    def git_with_platform_probe(work, home, *args):
        result = original(work, home, *args)
        if "init" in args:
            # The exact Git-for-Windows init probe key, also exercised on POSIX CI.
            original(work, home, "config", "--local", "core.symlinks", symlinks)
        return result

    monkeypatch.setattr(aider, "git", git_with_platform_probe)
    product = tmp_path / "product"
    product.mkdir()
    (product / "中文.txt").write_text("保留原字节\n", encoding="utf-8")
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    assert source_snapshot(product) == receipt
    work = tmp_path / receipt["journal"]
    assert git(work, "config", "--local", "core.symlinks") == symlinks


def test_symlink_probe_metadata_does_not_allow_invalid_values(snapshot, monkeypatch):
    from workbench.coding import aider

    product, work, _ = snapshot
    git(work, "config", "--local", "core.symlinks", "untrusted-command")

    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid metadata must be rejected before Git is called")

    monkeypatch.setattr(aider, "git", forbidden)
    with pytest.raises(PrerequisiteError, match="core.symlinks"):
        source_snapshot(product)


@pytest.mark.parametrize("query_name", ["--show-toplevel", "--absolute-git-dir"])
@pytest.mark.parametrize("same_directory", [True, False])
def test_git_reported_directory_uses_filesystem_identity(
    snapshot, tmp_path, monkeypatch, query_name, same_directory
):
    from workbench.coding import aider

    product, work, receipt = snapshot
    expected = work if query_name == "--show-toplevel" else work / ".git"
    other = tmp_path / "different-repository"
    other.mkdir()
    target = expected if same_directory else other
    if os.name == "nt":
        # Exercise Windows' native extended-length alias without changing the
        # controlled repository or granting symlink/long-path configuration rights.
        reported = "\\\\?\\" + str(target.resolve())
    else:
        reported = str(target / ".")
    original_git = aider.git

    def aliased_git(folder, home, *args):
        result = original_git(folder, home, *args)
        if args[-2:] == ("rev-parse", query_name):
            return {**result, "log": reported}
        return result

    monkeypatch.setattr(aider, "git", aliased_git)
    if same_directory:
        assert source_snapshot(product) == receipt
    else:
        with pytest.raises(PrerequisiteError, match="独立保留仓库|Git 目录不匹配"):
            source_snapshot(product)


def test_git_directory_identity_permission_error_is_not_downgraded(snapshot, monkeypatch):
    from pathlib import Path

    product, _, _ = snapshot

    def denied(self, other):
        raise PermissionError("directory identity denied")

    monkeypatch.setattr(Path, "samefile", denied)
    with pytest.raises(PermissionError, match="identity denied"):
        source_snapshot(product)


@pytest.mark.parametrize("query_name", ["--show-toplevel", "--absolute-git-dir"])
def test_git_reported_missing_directory_fails_closed(snapshot, tmp_path, monkeypatch, query_name):
    from workbench.coding import aider

    product, _, _ = snapshot
    original_git = aider.git

    def missing_git(folder, home, *args):
        result = original_git(folder, home, *args)
        if args[-2:] == ("rev-parse", query_name):
            return {**result, "log": str(tmp_path / "missing-repository")}
        return result

    monkeypatch.setattr(aider, "git", missing_git)
    with pytest.raises(PrerequisiteError, match="完整性"):
        source_snapshot(product)


def test_all_journal_git_commands_enable_long_paths_without_persisting_config(
    tmp_path, monkeypatch
):
    if not shutil.which("git"):
        pytest.skip("Git is required for journal command tests")
    from workbench.coding import aider

    original = aider.git
    observed = []

    def checked(work, home, *args):
        assert args[:2] == ("-c", "core.longpaths=true")
        observed.append(args)
        return original(work, home, *args)

    monkeypatch.setattr(aider, "git", checked)
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.txt").write_text("原始字节\n", encoding="utf-8")
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    assert source_snapshot(product) == receipt
    assert all(
        any(command in args for args in observed)
        for command in ("init", "add", "commit", "rev-parse", "fsck")
    )
    config = (tmp_path / receipt["journal"] / ".git/config").read_text(encoding="utf-8")
    assert "longpaths" not in config.casefold()


def test_long_path_snapshot_survives_atomic_publish(tmp_path):
    if not shutil.which("git"):
        pytest.skip("Git is required for the long-path journal test")
    root = tmp_path / ("first-" + "a" * 64) / ("second-" + "b" * 64) / ("third-" + "c" * 64)
    staging = root / "staging"
    product = staging / "product"
    product.mkdir(parents=True)
    assert len(str(product.resolve())) > 260
    (product / "source.txt").write_text("源码长路径\r\n", encoding="utf-8")
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    assert source_snapshot(product) == receipt
    published = root / "published"
    staging.rename(published)
    assert source_snapshot(published / "product") == receipt


@pytest.mark.parametrize("query_name", ["--show-toplevel", "--absolute-git-dir"])
def test_git_warning_is_not_stripped_from_identity_query(snapshot, monkeypatch, query_name):
    from workbench.coding import aider

    product, _, _ = snapshot
    original = aider.git

    def warned(work, home, *args):
        result = original(work, home, *args)
        if args[-2:] == ("rev-parse", query_name):
            return {
                **result,
                "log": "warning: unable to access '.git/objects/info/alternates': Filename too long\n"
                + result["log"],
            }
        return result

    monkeypatch.setattr(aider, "git", warned)
    with pytest.raises(PrerequisiteError, match="警告|非单行"):
        source_snapshot(product)
