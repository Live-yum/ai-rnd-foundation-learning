# tests/test_source_snapshot_integrity.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.delivery.source_candidate`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `snapshot`（L16–L28）：接收`tmp_path`。 控制顺序：L17按`not shutil.which("git")`分支；L26断言`receipt["status"] == "committed"`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "binary.dat").write_bytes`、`(product / "source.py").write_text`、`(product / "nested").mkdir`、`(product / "nested/中文 file.txt").write_text`、`source_snapshot`。 返回路径：L28的`product, work, receipt`。
- `git`（L31–L37）：接收`work`、`*args`。 调用`subprocess.run( ["git", "-c", "user.name=Test", "-c", "user.email…`、`subprocess.run`、`str`。 返回路径：L32的`subprocess.run( ["git", "-c", "user.name=Test", "-c", "user.email=test@localhost", "-C", s…`。
- `test_valid_cache_checks_real_binary_and_nested_tree`（L40–L42）：接收`snapshot`。 控制顺序：L42断言`source_snapshot(product) == receipt`。 调用`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_forged_receipt_is_rejected`（L56–L61）：接收`snapshot`、`field`、`value`。 调用`(work.parent / "commit.json").write_text`、`json.dumps`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `windows_readonly_unlink`（L65–L75）：接收`monkeypatch`。 源码说明：Enforce Windows read-only deletion semantics on POSIX runners too.。 调用`monkeypatch.setattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `windows_readonly_unlink.unlink`（L69–L73）：接收`path`、`*args`、`**kwargs`。 控制顺序：L71按`stat.S_ISREG(mode) and not mode & stat.S_IWUSR`分支；L72抛异常，停止当前正常路径。 调用`os.stat`、`kwargs.get`、`stat.S_ISREG`、`PermissionError`、`original`。 返回路径：L73的`original(path, *args, **kwargs)`。
- `test_deleted_git_or_receipt_fails_closed`（L79–L91）：接收`snapshot`、`removal`、`windows_readonly_unlink`。 控制顺序：L81按`removal == ".git"`分支；L84遍历`(work / ".git/objects").rglob("*")`；L85按`path.is_file()`分支。 调用`(work / ".git/objects").rglob`、`path.is_file`、`path.chmod`、`path.stat`、`shutil.rmtree`、`(work.parent / "commit.json").unlink`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_head_moved_to_different_commit_with_same_tree`（L94–L98）：接收`snapshot`。 调用`git`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_forged_commit_for_different_tree_even_when_worktree_matches`（L101–L111）：接收`snapshot`。 调用`(work / "source.py").write_text`、`git`、`(work.parent / "commit.json").write_text`、`json.dumps`、`(work / "source.py").write_bytes`、`(product / "source.py").read_bytes`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_git_directory_is_rejected`（L115–L127）：接收`snapshot`、`tmp_path`、`redirect`。 控制顺序：L119按`redirect == "symlink"`分支。 调用`(work / ".git").rename`、`(work / ".git").symlink_to`、`pytest.skip`、`(work / ".git").write_text`、`str`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_missing_never_reuses_committed_claim`（L130–L137）：接收`snapshot`、`monkeypatch`。 控制顺序：L134断言`result["status"] == "unavailable"`；L135断言`result["git_available"] is False`；L136断言`"commit" not in result`；L137断言`(work / "source.py").read_bytes() == (product / "source.py").read_bytes()`。 调用`monkeypatch.setattr`、`source_snapshot`、`(work / "source.py").read_bytes`、`(product / "source.py").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_is_not_downgraded`（L140–L149）：接收`snapshot`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_permission_failure_is_not_downgraded.denied`（L144–L145）：接收`*args`、`**kwargs`。 控制顺序：L145抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupt_git_object_fails_closed`（L152–L161）：接收`snapshot`、`windows_readonly_unlink`。 调用`object_path.chmod`、`object_path.stat`、`object_path.unlink`、`object_path.write_bytes`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_snapshot_does_not_apply_source_attributes`（L164–L174）：接收`tmp_path`。 控制顺序：L173断言`receipt["status"] == "committed"`；L174断言`source_snapshot(product) == receipt`。 调用`product.mkdir`、`(product / ".gitattributes").write_text`、`(product / "lines.txt").write_bytes`、`(product / "binary.dat").write_bytes`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_or_executable_git_configuration_fails_closed`（L178–L182）：接收`snapshot`、`setting`。 调用`git`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_external_object_alternates_fail_closed`（L185–L189）：接收`snapshot`。 调用`(work / ".git/objects/info/alternates").write_text`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changed_worktree_mode_is_not_hidden_by_manifest`（L192–L200）：接收`snapshot`。 控制顺序：L195按`os.name == "nt"`分支。 调用`pytest.skip`、`(work / "source.py").chmod`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_history_rewriting_metadata_is_rejected_before_git`（L204–L215）：接收`snapshot`、`monkeypatch`、`metadata`。 调用`(journal / ".git" / metadata).write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_history_rewriting_metadata_is_rejected_before_git.forbidden`（L210–L211）：接收`*args`、`**kwargs`。 控制顺序：L211抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_init_filesystem_symlink_probe_metadata_is_portable`（L219–L239）：接收`tmp_path`、`monkeypatch`、`symlinks`。 控制顺序：L236断言`receipt["status"] == "committed"`；L237断言`source_snapshot(product) == receipt`；L239断言`git(work, "config", "--local", "core.symlinks") == symlinks`。 调用`monkeypatch.setattr`、`product.mkdir`、`(product / "中文.txt").write_text`、`source_snapshot`、`git`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_init_filesystem_symlink_probe_metadata_is_portable.git_with_platform_probe`（L224–L229）：接收`work`、`home`、`*args`。 控制顺序：L226按`"init" in args`分支。 调用`original`。 返回路径：L229的`result`。
- `test_symlink_probe_metadata_does_not_allow_invalid_values`（L242–L253）：接收`snapshot`、`monkeypatch`。 调用`git`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlink_probe_metadata_does_not_allow_invalid_values.forbidden`（L248–L249）：接收`*args`、`**kwargs`。 控制顺序：L249抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_reported_directory_uses_filesystem_identity`（L258–L284）：接收`snapshot`、`tmp_path`、`monkeypatch`、`query_name`、`same_directory`。 控制顺序：L280按`same_directory`分支；L281断言`source_snapshot(product) == receipt`。 调用`other.mkdir`、`monkeypatch.setattr`、`source_snapshot`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_reported_directory_uses_filesystem_identity.aliased_git`（L268–L277）：接收`folder`、`home`、`*args`。 控制顺序：L270按`args[-2:] == ("rev-parse", query_name)`分支；L274按`os.name == "nt"`分支。 调用`original_git`、`str`、`target.resolve`。 返回路径：L276的`{**result, "log": reported}`；L277的`result`。
- `test_git_directory_identity_permission_error_is_not_downgraded`（L287–L297）：接收`snapshot`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_directory_identity_permission_error_is_not_downgraded.denied`（L292–L293）：接收`other`。 控制顺序：L293抛异常，停止当前正常路径。 调用`PermissionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_reported_missing_directory_fails_closed`（L301–L315）：接收`snapshot`、`tmp_path`、`monkeypatch`、`query_name`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_reported_missing_directory_fails_closed.missing_git`（L307–L311）：接收`folder`、`home`、`*args`。 控制顺序：L309按`args[-2:] == ("rev-parse", query_name)`分支。 调用`original_git`、`str`。 返回路径：L310的`{**result, "log": str(tmp_path / "missing-repository")}`；L311的`result`。
- `test_all_journal_git_commands_enable_long_paths_without_persisting_config`（L318–L345）：接收`tmp_path`、`monkeypatch`。 控制顺序：L321按`not shutil.which("git")`分支；L338断言`receipt["status"] == "committed"`；L339断言`source_snapshot(product) == receipt`；L340断言`all( any(command in args for args in observed) for command in ("init", "add", "commit…`；L345断言`"longpaths" not in config.casefold()`。 调用`shutil.which`、`pytest.skip`、`monkeypatch.setattr`、`product.mkdir`、`(product / "source.txt").write_text`、`source_snapshot`、`all`、`any`、`(tmp_path / receipt["journal"] / ".git/config").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_journal_git_commands_enable_long_paths_without_persisting_config.checked`（L328–L331）：接收`work`、`home`、`*args`。 控制顺序：L329断言`args[:2] == ("-c", "core.longpaths=true")`。 调用`observed.append`、`original`。 返回路径：L331的`original(work, home, *args)`。
- `test_long_path_snapshot_survives_atomic_publish`（L348–L362）：接收`tmp_path`。 控制顺序：L349按`not shutil.which("git")`分支；L355断言`len(str(product.resolve())) > 260`；L358断言`receipt["status"] == "committed"`；L359断言`source_snapshot(product) == receipt`；L362断言`source_snapshot(published / "product") == receipt`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`len`、`str`、`product.resolve`、`(product / "source.txt").write_text`、`source_snapshot`、`staging.rename`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_warning_is_not_stripped_from_identity_query`（L366–L384）：接收`snapshot`、`monkeypatch`、`query_name`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_warning_is_not_stripped_from_identity_query.warned`（L372–L380）：接收`work`、`home`、`*args`。 控制顺序：L374按`args[-2:] == ("rev-parse", query_name)`分支。 调用`original`。 返回路径：L375的`{ **result, "log": "warning: unable to access '.git/objects/info/alternates': Filename too…`；L380的`result`。
- `test_cache_copy_binds_original_bytes_and_identity`（L388–L417）：接收`snapshot`、`monkeypatch`、`changed`。 控制顺序：L417断言`altered`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cache_copy_binds_original_bytes_and_identity.raced`（L395–L412）：接收`source`、`target`、`**kwargs`。 控制顺序：L398按`not altered`分支；L400按`changed == "metadata"`分支；L403按`changed == "receipt"`分支；L406按`changed == "source"`分支。 调用`original`、`path.write_text`、`path.write_bytes`、`path.read_bytes`、`(work / "source.py").write_text`、`(work / ".git").rename`、`shutil.copytree`。 返回路径：L412的`result`。
- `test_cache_excluded_extra_file_is_never_copied`（L420–L431）：接收`snapshot`、`monkeypatch`。 调用`(work / ".env").write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cache_excluded_extra_file_is_never_copied.forbidden`（L426–L427）：接收`*args`、`**kwargs`。 控制顺序：L427抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_always_runs_in_private_system_temp`（L434–L459）：接收`tmp_path`、`monkeypatch`。 控制顺序：L440按`not shutil.which("git")`分支；L457断言`receipt["status"] == "committed"`；L458断言`source_snapshot(product) == receipt`；L459断言`len(set(seen)) == 2`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "source.txt").write_text`、`monkeypatch.setattr`、`source_snapshot`、`len`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_git_always_runs_in_private_system_temp.shallow`（L448–L453）：接收`folder`、`home`、`*args`。 控制顺序：L450断言`folder.parent.parent.samefile(Path(tempfile.gettempdir()))`；L451断言`folder.parent.name.startswith("rnd-git-")`；L452断言`not folder.is_relative_to(tmp_path)`。 调用`seen.append`、`folder.parent.parent.samefile`、`Path`、`tempfile.gettempdir`、`folder.parent.name.startswith`、`folder.is_relative_to`、`original`。 返回路径：L453的`original(folder, home, *args)`。
- `test_new_snapshot_metadata_change_after_verification_is_rejected`（L462–L481）：接收`tmp_path`、`monkeypatch`。 控制顺序：L465按`not shutil.which("git")`分支；L481断言`not list((tmp_path / "source-revisions").glob("*/commit.json"))`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "source.txt").write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`list`、`(tmp_path / "source-revisions").glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_snapshot_metadata_change_after_verification_is_rejected.raced`（L472–L476）：接收`folder`、`home`、`*args`。 控制顺序：L474按`"fsck" in args`分支。 调用`original`、`(folder / ".git/description").write_text`。 返回路径：L476的`result`。
- `test_missing_git_never_copies_cached_journal`（L484–L494）：接收`snapshot`、`monkeypatch`。 控制顺序：L494断言`source_snapshot(product)["status"] == "unavailable"`。 调用`monkeypatch.setattr`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_git_never_copies_cached_journal.forbidden`（L490–L491）：接收`*args`、`**kwargs`。 控制顺序：L491抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cached_temp_failure_never_reuses_committed`（L498–L508）：接收`snapshot`、`monkeypatch`、`error`。 调用`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cached_temp_failure_never_reuses_committed.denied`（L503–L504）：接收`*args`、`**kwargs`。 控制顺序：L504抛异常，停止当前正常路径。 调用`error`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversized_git_metadata_rejected_before_copy`（L511–L523）：接收`snapshot`、`monkeypatch`。 调用`(work / ".git/oversized-pack").open`、`stream.truncate`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_oversized_git_metadata_rejected_before_copy.forbidden`（L518–L519）：接收`*args`、`**kwargs`。 控制顺序：L519抛异常，停止当前正常路径。 调用`AssertionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_snapshot_resource_failure_is_honest`（L528–L557）：接收`snapshot`、`tmp_path`、`monkeypatch`、`cached`、`failure`。 控制顺序：L532按`not cached`分支；L536按`failure == "deep_temp"`分支；L552按`cached`分支；L556断言`source_snapshot(product)["status"] == "failed"`；L557断言`(product / "new.txt").read_text(encoding="utf-8") == "new source\n"`。 调用`product.mkdir`、`(product / "new.txt").write_text`、`deep.mkdir`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`(product / "new.txt").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_snapshot_resource_failure_is_honest.temporary`（L541–L543）：接收`*args`、`**kwargs`。 调用`original`。 返回路径：L543的`original(*args, **kwargs)`。
- `test_snapshot_resource_failure_is_honest.unavailable`（L548–L549）：接收`*args`、`**kwargs`。 控制顺序：L549抛异常，停止当前正常路径。 调用`OSError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_snapshot_receipt_change_before_publication_is_rejected`（L560–L578）：接收`tmp_path`、`monkeypatch`。 控制顺序：L563按`not shutil.which("git")`分支；L578断言`not list((tmp_path / "source-revisions").glob("*/commit.json"))`。 调用`shutil.which`、`pytest.skip`、`product.mkdir`、`(product / "source.txt").write_text`、`monkeypatch.setattr`、`pytest.raises`、`source_snapshot`、`list`、`(tmp_path / "source-revisions").glob`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_snapshot_receipt_change_before_publication_is_rejected.raced`（L570–L573）：接收`path`、`value`。 控制顺序：L572按`path.name == "commit.json"`分支。 调用`original`、`path.write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_source_snapshot_integrity.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L578。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`21416`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_source_snapshot_integrity.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f9c495bc620dfc457b92fe319a3191200766e92ccf8535fea74331bad45253bb"} -->
````python
# tests/test_source_snapshot_integrity.py
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
    other = tmp_path / "different-repository"
    other.mkdir()
    original_git = aider.git

    def aliased_git(folder, home, *args):
        result = original_git(folder, home, *args)
        if args[-2:] == ("rev-parse", query_name):
            expected = folder if query_name == "--show-toplevel" else folder / ".git"
            target = expected if same_directory else other
            reported = str(target / ".")
            if os.name == "nt":
                reported = "\\\\?\\" + str(target.resolve())
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


@pytest.mark.parametrize("changed", ["metadata", "receipt", "source", "identity"])
def test_cache_copy_binds_original_bytes_and_identity(snapshot, monkeypatch, changed):
    from workbench.delivery import source_candidate

    product, work, _ = snapshot
    original = shutil.copy2
    altered = False

    def raced(source, target, **kwargs):
        nonlocal altered
        result = original(source, target, **kwargs)
        if not altered:
            altered = True
            if changed == "metadata":
                path = work / ".git/description"
                path.write_text("changed\n", encoding="utf-8")
            elif changed == "receipt":
                path = work.parent / "commit.json"
                path.write_bytes(path.read_bytes() + b"\n")
            elif changed == "source":
                (work / "source.py").write_text("changed = True\n", encoding="utf-8")
            else:
                previous = work.parent / "old-metadata"
                (work / ".git").rename(previous)
                shutil.copytree(previous, work / ".git", copy_function=original)
        return result

    monkeypatch.setattr(source_candidate.shutil, "copy2", raced)
    with pytest.raises(PrerequisiteError):
        source_snapshot(product)
    assert altered


def test_cache_excluded_extra_file_is_never_copied(snapshot, monkeypatch):
    from workbench.delivery import source_candidate

    product, work, _ = snapshot
    (work / ".env").write_text("PRIVATE=excluded\n", encoding="utf-8")

    def forbidden(*args, **kwargs):
        raise AssertionError("Extra source must be rejected before copying")

    monkeypatch.setattr(source_candidate.shutil, "copy2", forbidden)
    with pytest.raises(PrerequisiteError, match="额外"):
        source_snapshot(product)


def test_git_always_runs_in_private_system_temp(tmp_path, monkeypatch):
    import tempfile
    from pathlib import Path

    from workbench.coding import aider

    if not shutil.which("git"):
        pytest.skip("Git is required")
    product = tmp_path / ("deep" * 20) / ("journal" * 15) / "product"
    product.mkdir(parents=True)
    (product / "source.txt").write_text("CRLF\r\n中文\n", encoding="utf-8")
    original = aider.git
    seen = []

    def shallow(folder, home, *args):
        seen.append(folder)
        assert folder.parent.parent.samefile(Path(tempfile.gettempdir()))
        assert folder.parent.name.startswith("rnd-git-")
        assert not folder.is_relative_to(tmp_path)
        return original(folder, home, *args)

    monkeypatch.setattr(aider, "git", shallow)
    receipt = source_snapshot(product)
    assert receipt["status"] == "committed"
    assert source_snapshot(product) == receipt
    assert len(set(seen)) == 2


def test_new_snapshot_metadata_change_after_verification_is_rejected(tmp_path, monkeypatch):
    from workbench.coding import aider

    if not shutil.which("git"):
        pytest.skip("Git is required")
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.txt").write_text("source\n", encoding="utf-8")
    original = aider.git

    def raced(folder, home, *args):
        result = original(folder, home, *args)
        if "fsck" in args:
            (folder / ".git/description").write_text("changed\n", encoding="utf-8")
        return result

    monkeypatch.setattr(aider, "git", raced)
    with pytest.raises(PrerequisiteError, match="验证期间"):
        source_snapshot(product)
    assert not list((tmp_path / "source-revisions").glob("*/commit.json"))


def test_missing_git_never_copies_cached_journal(snapshot, monkeypatch):
    from workbench.delivery import source_candidate

    product, _, _ = snapshot
    monkeypatch.setattr(source_candidate.shutil, "which", lambda _: None)

    def forbidden(*args, **kwargs):
        raise AssertionError("Do not copy a journal when Git is unavailable")

    monkeypatch.setattr(source_candidate.shutil, "copy2", forbidden)
    assert source_snapshot(product)["status"] == "unavailable"


@pytest.mark.parametrize("error", [PermissionError, OSError])
def test_cached_temp_failure_never_reuses_committed(snapshot, monkeypatch, error):
    from workbench.delivery import source_candidate

    product, _, _ = snapshot

    def denied(*args, **kwargs):
        raise error("private temporary storage unavailable")

    monkeypatch.setattr(source_candidate.tempfile, "TemporaryDirectory", denied)
    with pytest.raises(error):
        source_snapshot(product)


def test_oversized_git_metadata_rejected_before_copy(snapshot, monkeypatch):
    from workbench.delivery import source_candidate

    product, work, _ = snapshot
    with (work / ".git/oversized-pack").open("wb") as stream:
        stream.truncate(512_000_001)

    def forbidden(*args, **kwargs):
        raise AssertionError("Oversized metadata must not be copied")

    monkeypatch.setattr(source_candidate.shutil, "copy2", forbidden)
    with pytest.raises(PrerequisiteError, match="大小限制"):
        source_snapshot(product)


@pytest.mark.parametrize("cached", [False, True])
@pytest.mark.parametrize("failure", ["deep_temp", "copy_io"])
def test_snapshot_resource_failure_is_honest(snapshot, tmp_path, monkeypatch, cached, failure):
    from workbench.delivery import source_candidate

    product, _, _ = snapshot
    if not cached:
        product = tmp_path / "new-product"
        product.mkdir()
        (product / "new.txt").write_text("new source\n", encoding="utf-8")
    if failure == "deep_temp":
        original = source_candidate.tempfile.TemporaryDirectory
        deep = tmp_path / ("temp" * 30) / ("deep" * 20)
        deep.mkdir(parents=True)

        def temporary(*args, **kwargs):
            kwargs["dir"] = deep
            return original(*args, **kwargs)

        monkeypatch.setattr(source_candidate.tempfile, "TemporaryDirectory", temporary)
    else:

        def unavailable(*args, **kwargs):
            raise OSError("copy storage unavailable")

        monkeypatch.setattr(source_candidate.shutil, "copy2", unavailable)
    if cached:
        with pytest.raises(PrerequisiteError, match="临时存储"):
            source_snapshot(product)
    else:
        assert source_snapshot(product)["status"] == "failed"
        assert (product / "new.txt").read_text(encoding="utf-8") == "new source\n"


def test_new_snapshot_receipt_change_before_publication_is_rejected(tmp_path, monkeypatch):
    from workbench.delivery import source_candidate

    if not shutil.which("git"):
        pytest.skip("Git is required")
    product = tmp_path / "product"
    product.mkdir()
    (product / "source.txt").write_text("source\n", encoding="utf-8")
    original = source_candidate.write_json

    def raced(path, value):
        original(path, value)
        if path.name == "commit.json":
            path.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(source_candidate, "write_json", raced)
    with pytest.raises(PrerequisiteError, match="复制期间"):
        source_snapshot(product)
    assert not list((tmp_path / "source-revisions").glob("*/commit.json"))
````
