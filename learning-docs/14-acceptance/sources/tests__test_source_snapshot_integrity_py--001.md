# tests/test_source_snapshot_integrity.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.delivery.source_candidate`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot`（L14–L26）：接收`tmp_path`。 控制顺序：L15按`not shutil.which("git")`分支；L24断言`receipt["status"] == "committed"`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "binary.dat").write_bytes`、`(product / "source.py").write_text`、`(product / "nested").mkdir`、`(product / "nested/中文 file.txt").write_text`、`source_snapshot`。 返回路径：L26的`product, work, receipt`。
- `git`（L29–L35）：接收`work`、`*args`。 调用`subprocess.run( ["git", "-c", "user.name=Test", "-c", "user.email…`、`subprocess.run`、`str`。 返回路径：L30的`subprocess.run( ["git", "-c", "user.name=Test", "-c", "user.email=test@localhost", "-C", s…`。
- `test_valid_cache_checks_real_binary_and_nested_tree`（L38–L40）：接收`snapshot`。 控制顺序：L40断言`source_snapshot(product) == receipt`。 调用`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_forged_receipt_is_rejected`（L54–L59）：接收`snapshot`、`field`、`value`。 调用`(work.parent / "commit.json").write_text`、`json.dumps`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deleted_git_or_receipt_fails_closed`（L63–L70）：接收`snapshot`、`removal`。 控制顺序：L65按`removal == ".git"`分支。 调用`shutil.rmtree`、`(work.parent / "commit.json").unlink`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_head_moved_to_different_commit_with_same_tree`（L73–L77）：接收`snapshot`。 调用`git`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_forged_commit_for_different_tree_even_when_worktree_matches`（L80–L90）：接收`snapshot`。 调用`(work / "source.py").write_text`、`git`、`(work.parent / "commit.json").write_text`、`json.dumps`、`(work / "source.py").write_bytes`、`(product / "source.py").read_bytes`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_git_directory_is_rejected`（L94–L106）：接收`snapshot`、`tmp_path`、`redirect`。 控制顺序：L98按`redirect == "symlink"`分支。 调用`(work / ".git").rename`、`(work / ".git").symlink_to`、`pytest.skip`、`(work / ".git").write_text`、`str`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_missing_never_reuses_committed_claim`（L109–L116）：接收`snapshot`、`monkeypatch`。 控制顺序：L113断言`result["status"] == "unavailable"`；L114断言`result["git_available"] is False`；L115断言`"commit" not in result`；L116断言`(work / "source.py").read_bytes() == (product / "source.py").read_bytes()`。 调用`monkeypatch.setattr`、`source_snapshot`、`(work / "source.py").read_bytes`、`(product / "source.py").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_is_not_downgraded`（L119–L128）：接收`snapshot`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_is_not_downgraded.denied`（L123–L124）：接收`*args`、`**kwargs`。 控制顺序：L124抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupt_git_object_fails_closed`（L131–L138）：接收`snapshot`。 调用`object_path.unlink`、`object_path.write_bytes`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_snapshot_does_not_apply_source_attributes`（L141–L151）：接收`tmp_path`。 控制顺序：L150断言`receipt["status"] == "committed"`；L151断言`source_snapshot(product) == receipt`。 调用`product.mkdir`、`(product / ".gitattributes").write_text`、`(product / "lines.txt").write_bytes`、`(product / "binary.dat").write_bytes`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_or_executable_git_configuration_fails_closed`（L155–L159）：接收`snapshot`、`setting`。 调用`git`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_object_alternates_fail_closed`（L162–L166）：接收`snapshot`。 调用`(work / ".git/objects/info/alternates").write_text`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_worktree_mode_is_not_hidden_by_manifest`（L169–L177）：接收`snapshot`。 控制顺序：L172按`os.name == "nt"`分支。 调用`pytest.skip`、`(work / "source.py").chmod`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_history_rewriting_metadata_is_rejected_before_git`（L181–L192）：接收`snapshot`、`monkeypatch`、`metadata`。 调用`(journal / ".git" / metadata).write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_history_rewriting_metadata_is_rejected_before_git.forbidden`（L187–L188）：接收`*args`、`**kwargs`。 控制顺序：L188抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_init_filesystem_symlink_probe_metadata_is_portable`（L196–L216）：接收`tmp_path`、`monkeypatch`、`symlinks`。 控制顺序：L213断言`receipt["status"] == "committed"`；L214断言`source_snapshot(product) == receipt`；L216断言`git(work, "config", "--local", "core.symlinks") == symlinks`。 调用`monkeypatch.setattr`、`product.mkdir`、`(product / "中文.txt").write_text`、`source_snapshot`、`git`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_init_filesystem_symlink_probe_metadata_is_portable.git_with_platform_probe`（L201–L206）：接收`work`、`home`、`*args`。 控制顺序：L203按`"init" in args`分支。 调用`original`。 返回路径：L206的`result`。
- `test_symlink_probe_metadata_does_not_allow_invalid_values`（L219–L230）：接收`snapshot`、`monkeypatch`。 调用`git`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlink_probe_metadata_does_not_allow_invalid_values.forbidden`（L225–L226）：接收`*args`、`**kwargs`。 控制顺序：L226抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_snapshot_integrity.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L230。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8430`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_snapshot_integrity.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "675b717f6321cd56d7db72e1e022d09ac937f0db106260ac57e8e895ed5766a7"} -->
````python
# tests/test_source_snapshot_integrity.py
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
````
