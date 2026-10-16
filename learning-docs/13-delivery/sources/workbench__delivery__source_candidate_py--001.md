# workbench/delivery/source_candidate.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__delivery__source_candidate_py--002.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `continuation_step`（L17–L23）：接收`template`。 返回路径：L19的`"先下载并保留本候选；在已配置原生工具的 Linux/WSL 操作台新建运行，或执行 " f"uv run rnd chat --template {template} --fro…`。
- `source_snapshot`（L26–L403）：接收`destination`。 源码说明：Retain source; claim a commit only after independently checking its tree.。 控制顺序：L259按`base.exists()`分支；L262按`not receipt_path.is_file() or not work.is_dir() or not metadata.is_dir()`分支；L263抛异常，停止当前正常路径；L270抛异常，停止当前正常路径；L272按`not isinstance(commit, str) or not re.fullmatch( r"(?:[0-9a-f]{40}\|[0-9a-f]{64})", c…`分支；L275抛异常，停止当前正常路径；L276按`receipt != expected_receipt(commit) or manifest(work) != listing`分支；L277抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`manifest`、`digest`、`inside`、`base.exists`、`receipt_path.is_file`、`work.is_dir`、`metadata.is_dir`、`PrerequisiteError`等。 返回路径：L279的`unavailable()`；L308的`receipt`；L310的`unavailable()`。
- `source_snapshot.SnapshotResourceUnavailable`（L37–L38）：继承`OSError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `source_snapshot.journal_git`（L40–L44）：接收`work`、`home`、`*args`。 调用`git`。 返回路径：L44的`git(work, home, "-c", "core.longpaths=true", *args)`。
- `source_snapshot.unavailable`（L52–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L53的`{ "status": "unavailable", "git_available": False, "source_digest": identity, "note": "Git…`。
- `source_snapshot.expected_receipt`（L60–L68）：接收`commit`。 返回路径：L61的`{ "status": "committed", "git_available": True, "commit": commit, "source_digest": identit…`。
- `source_snapshot.check_metadata`（L70–L112）：接收`work`。 控制顺序：L77抛异常，停止当前正常路径；L90按`config.defaults() or any( section not in allowed or set(config[section]) - allowed[se…`分支；L94抛异常，停止当前正常路径；L98按`config.has_option("core", "symlinks") and config.get( "core", "symlinks" ).casefold()…`分支；L101抛异常，停止当前正常路径；L102按`any( (work / ".git" / name).exists() for name in ( "commondir", "shallow", "info/graf…`分支；L112抛异常，停止当前正常路径。 调用`configparser.ConfigParser`、`config.read_string`、`(work / ".git/config").read_text`、`PrerequisiteError`、`config.defaults`、`any`、`set`、`config.sections`、`config.has_option`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.inventory`（L114–L141）：接收`root`。 源码说明：Unfiltered bounded evidence, including every Git directory and byte.。 控制顺序：L121遍历`os.walk(root, followlinks=False, onerror=failed)`；L122遍历`[Path(directory), *(Path(directory) / name for name in sorted(nam…`；L126按`stat.S_ISDIR(info.st_mode)`分支；L128按`stat.S_ISREG(info.st_mode)`分支；L130按`info.st_size > 512_000_000 or total > 1_000_000_000`分支；L131抛异常，停止当前正常路径；L134抛异常，停止当前正常路径；L136按`len(result) > 100_000`分支。后续分支沿下方源码相同行号继续阅读。 调用`os.walk`、`Path`、`sorted`、`path.relative_to(root).as_posix`、`path.relative_to`、`inside`、`path.lstat`、`stat.S_ISDIR`、`stat.S_IMODE`等。 返回路径：L141的`result`。
- `source_snapshot.inventory.failed`（L118–L119）：接收`error`。 控制顺序：L119抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.source_inventory`（L143–L155）：接收`work`。 控制顺序：L146遍历`listing`；L148遍历`result.items()`；L149按`name == ".git" or name.startswith(".git/")`分支；L151按`(entry[0] == "file" and name not in listing) or ( entry[0] == "directory" and name no…`分支；L154抛异常，停止当前正常路径。 调用`inventory`、`allowed_dirs.update`、`parent.as_posix`、`Path`、`result.items`、`name.startswith`、`PrerequisiteError`。 返回路径：L155的`result`。
- `source_snapshot.copy_bound`（L157–L179）：接收`source`、`target`、`expected`。 源码说明：Copy approved regular paths, preserving bytes/modes, never Git-clone.。 控制顺序：L161遍历`sorted(expected.items())`；L162按`name == "."`分支；L165按`entry[0] == "directory"`分支；L169遍历`sorted(expected.items(), reverse=True)`；L170按`entry[0] == "directory"`分支；L174按`inventory(source) != expected or inventory(target) != expected`分支；L175抛异常，停止当前正常路径；L177抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`target.mkdir`、`sorted`、`expected.items`、`inside`、`copied.mkdir`、`shutil.copy2`、`shutil.copystat`、`inventory`、`PrerequisiteError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.check_short_root`（L181–L186）：接收`root`。 控制顺序：L185按`len(str(root.resolve()).encode("utf-16-le")) // 2 > 160`分支；L186抛异常，停止当前正常路径。 调用`len`、`str(root.resolve()).encode`、`str`、`root.resolve`、`SnapshotResourceUnavailable`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.verify`（L188–L257）：接收`work`、`home`、`receipt`。 控制顺序：L206按`not Path(query("rev-parse", "--show-toplevel")).samefile(work)`分支；L207抛异常，停止当前正常路径；L208按`not Path(query("rev-parse", "--absolute-git-dir")).samefile(work / ".git")`分支；L209抛异常，停止当前正常路径；L211按`algorithm not in {"sha1", "sha256"}`分支；L212抛异常，停止当前正常路径；L214按`receipt != expected_receipt(commit)`分支；L215抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`check_metadata`、`Path(query("rev-parse", "--show-toplevel")).samefile`、`Path`、`query`、`PrerequisiteError`、`Path(query("rev-parse", "--absolute-git-dir")).samefile`、`expected_receipt`、`files`、`path.stat`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.verify.query`（L194–L202）：接收`*args`。 控制顺序：L200按`args[0] == "rev-parse" and len(output.splitlines()) != 1`分支；L201抛异常，停止当前正常路径。 调用`journal_git( work, home, "--no-replace-objects", "-c", "core.fsmo…`、`journal_git`、`len`、`output.splitlines`、`PrerequisiteError`。 返回路径：L202的`output`。
- `source_snapshot.verify.object_hash`（L217–L220）：接收`kind`、`data`。 调用`hashlib.new( algorithm, kind + b" " + str(len(data)).encode() + b…`、`hashlib.new`、`str(len(data)).encode`、`str`、`len`。 返回路径：L218的`hashlib.new( algorithm, kind + b" " + str(len(data)).encode() + b"\0" + data ).digest()`。
- `source_snapshot.verify.tree_hash`（L234–L247）：接收`node`。 控制顺序：L236遍历`node.items()`。 调用`node.items`、`isinstance`、`os.fsencode`、`tree_hash`、`entries.append`、`object_hash`、`b"".join`、`sorted`。 返回路径：L247的`object_hash(b"tree", b"".join(body for _, body in sorted(entries)))`。
- `candidate_status`（L421–L425）：接收`receipt`。 控制顺序：L423按`"source_derivation" in receipt`分支。 调用`receipt.get`。 返回路径：L425的`status`。
- `check_status_binding`（L428–L453）：接收`destination`、`receipt`。 源码说明：A mutable generation receipt cannot upgrade the saved controller statement.。 控制顺序：L434按`receipt.get("preserve_runtime_files")`分支；L435按`statement.exists() or not retained.is_file()`分支；L436抛异常，停止当前正常路径；L439按`evidence != { "status": expected, "source_digest": digest(receipt.get("files", {})), …`分支；L444抛异常，停止当前正常路径；L445按`not statement.is_file() or json.loads(statement.read_text(encoding="utf-8")) != expec…`分支；L446抛异常，停止当前正常路径；L447按`expected["runtime_verified"] is not False or expected["production_ready"] is not Fals…`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`inside`、`candidate_status`、`receipt.get`、`statement.exists`、`retained.is_file`、`PrerequisiteError`、`json.loads`、`retained.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `refresh_candidate`（L456–L508）：接收`destination`、`receipt`、`pending_steps`、`generated_files`、`generation_status`。 源码说明：Bind controller-approved source edits to a new unaccepted source snapshot.。 控制顺序：L461按`receipt.get("execution") != "source-candidate"`分支；L462抛异常，停止当前正常路径；L465按`"files" in receipt or inside(destination, "SOURCE-STATUS.json").exists() or inside(de…`分支；L473遍历`( ("pending_steps", pending_steps), ("generated_files", generated…`；L478按`value is not None`分支；L490按`receipt["verification_status"] not in {"unverified", "failed"}`分支；L491抛异常，停止当前正常路径；L493按`not receipt.get("preserve_runtime_files")`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`receipt.get`、`PrerequisiteError`、`inside`、`saved_path.is_file`、`json.loads`、`saved_path.read_text`、`inside(destination, "SOURCE-STATUS.json").exists`、`inside(destination.parent, "source-candidate-status.json").exists`等。 返回路径：L508的`receipt`。
- `derive_candidate`（L511–L602）：接收`source`、`edited`、`destination`、`base_receipt`、`edit_receipt`、`derivation`、`pending_steps`、`generated_files`。 源码说明：Atomically publish an independently bound draft; never alter recovery source.。 控制顺序：L525按`destination.absolute() != expected_destination.absolute()`分支；L526抛异常，停止当前正常路径；L531按`edit_receipt.get("before") != original or edit_receipt.get("files") != raw_files`分支；L532抛异常，停止当前正常路径；L540按`derivation != expected or not isinstance(expected["approved_files"], list)`分支；L541抛异常，停止当前正常路径；L544按`any(name.casefold() in reserved for name in approved) or { name for name in set(origi…`分支；L553抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`inside`、`destination.absolute`、`expected_destination.absolute`、`PrerequisiteError`、`verify_candidate`、`manifest`、`edit_receipt.get`、`digest`等。 返回路径：L568的`saved`；L602的`result`。
- `write_status`（L605–L619）：接收`destination`、`status`。 调用`write_json`、`atomic_text`、`"".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `retain_failed_candidate`（L622–L667）：接收`template`、`plan`、`destination`、`sources`、`error_type`。 源码说明：Keep the runtime workspace byte-for-byte so recovery evidence stays valid.。 控制顺序：L626按`not listing`分支；L627抛异常，停止当前正常路径；L630按`recovery and recovery.get("files") != listing`分支；L631抛异常，停止当前正常路径；L634遍历`sources`；L635按`digest(manifest(source["path"])) != source["source_digest"]`分支；L636抛异常，停止当前正常路径。 调用`Path`、`manifest`、`PrerequisiteError`、`checkpoint.is_file`、`json.loads`、`checkpoint.read_text`、`recovery.get`、`bool`、`digest`等。 返回路径：L667的`refresh_candidate(destination, receipt)`。
- `_publish_new`（L670–L703）：接收`source`、`target`。 源码说明：Atomic no-replace publication; unsupported systems must fail closed.。 控制顺序：L676按`os.name == "nt"`分支；L680按`sys.platform == "linux"`分支；L682按`function is None`分支；L683抛异常，停止当前正常路径；L692按`sys.platform == "darwin"`分支；L694按`function is None`分支；L695抛异常，停止当前正常路径；L699抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`os.rename`、`ctypes.CDLL`、`getattr`、`PrerequisiteError`、`os.fsencode`、`function`、`ctypes.get_errno`、`OSError`、`os.strerror`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_transaction_tree`（L706–L735）：接收`root`。 源码说明：Bind every byte and mode, including Git metadata and excluded filenames.。 控制顺序：L712按`not root.is_dir()`分支；L713抛异常，停止当前正常路径；L719遍历`os.walk(root, followlinks=False, onerror=denied)`；L720遍历`sorted(dirs + names)`；L724按`stat.S_ISDIR(info.st_mode)`分支；L726按`stat.S_ISREG(info.st_mode)`分支；L728按`info.st_size > 512_000_000 or total > 1_000_000_000`分支；L729抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`inside`、`Path`、`root.is_dir`、`PrerequisiteError`、`os.walk`、`sorted`、`(Path(directory) / name).relative_to(root).as_posix`、`(Path(directory) / name).relative_to`、`path.lstat`等。 返回路径：L735的`result`。
- `_transaction_tree.denied`（L716–L717）：接收`error`。 控制顺序：L717抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `recover_candidate`（L738–L859）：接收`template`、`plan`、`destination`。 源码说明：Resume only a complete, identity-bound source publication transaction.。 控制顺序：L742按`not transaction.exists()`分支；L754按`not isinstance(seal, dict) or set(seal) != {*expected, "tree", "receipt"} or any(seal…`分支；L759抛异常，停止当前正常路径；L761按`before != seal["tree"]`分支；L762抛异常，停止当前正常路径；L764按`receipt != seal["receipt"] or receipt.get("template") != template or receipt.get("spe…`分支；L769抛异常，停止当前正常路径；L775按`product_files != set(receipt.get("files", {}))`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`inside`、`transaction.exists`、`seal_path.read_bytes`、`json.loads`、`digest`、`plan.model_dump`、`isinstance`、`set`等。 返回路径：L743的`None`；L859的`receipt`。
- `recover_candidate.matches`（L792–L807）：接收`name`、`target`。 控制顺序：L793按`target.is_dir()`分支；L799按`not target.is_file()`分支；L800抛异常，停止当前正常路径。 调用`target.is_dir`、`target.stat`、`actual.update`、`_transaction_tree(target).items`、`_transaction_tree`、`target.is_file`、`PrerequisiteError`、`sha`、`before.items`等。 返回路径：L807的`actual == wanted`。

</details>

**创建路径：** `workbench/delivery/source_candidate.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L861。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`38880`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/delivery/source_candidate.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "b6e349917a0ebbd878573a77dd77d43cd6b1a86abe8a17229e2acc7eeed6eaf4"} -->
````python
# workbench/delivery/source_candidate.py
"""Retain source without claiming execution, acceptance, or deployment.

Only trusted controllers call these helpers. They never execute product code.
Local Git history is a source journal, not a successful validation receipt.
"""

import json
import shutil
import tempfile
from pathlib import Path

from workbench.core.contracts import digest
from workbench.filesystem import atomic_text, files, inside, manifest, pack_source, sha, write_json
from workbench.generation.python_basic import PrerequisiteError


def continuation_step(template):
    frontend = "fastapiadmin-vue" if template == "fastapiadmin" else "vben-antd"
    return (
        "先下载并保留本候选；在已配置原生工具的 Linux/WSL 操作台新建运行，或执行 "
        f"uv run rnd chat --template {template} --frontend {frontend} --database postgresql。"
        "新运行重新确认需求，可能调用模型；不会自动导入或覆盖本候选，已有改动需人工对照集成。"
    )


def source_snapshot(destination):
    """Retain source; claim a commit only after independently checking its tree."""
    import configparser
    import hashlib
    import os
    import re
    import stat

    from workbench.coding.aider import git
    from workbench.infrastructure.processes.tools import ToolFailure

    class SnapshotResourceUnavailable(OSError):
        """Local temporary storage cannot support a new Git journal."""

    def journal_git(work, home, *args):
        # Git for Windows otherwise rejects journal paths beyond MAX_PATH even
        # when Python can access them. Apply to every command, including reads
        # after atomic publication; never persist a global/repository setting.
        return git(work, home, "-c", "core.longpaths=true", *args)

    destination = Path(destination)
    listing = manifest(destination)
    identity = digest(listing)
    base = inside(destination.parent, "source-revisions/" + identity)
    receipt_path = inside(base, "commit.json")

    def unavailable():
        return {
            "status": "unavailable",
            "git_available": False,
            "source_digest": identity,
            "note": "Git 不可用；源码文件和摘要已保存，无法验证 Git 提交",
        }

    def expected_receipt(commit):
        return {
            "status": "committed",
            "git_available": True,
            "commit": commit,
            "source_digest": identity,
            "journal": "source-revisions/" + identity + "/source",
            "runtime_verified": False,
        }

    def check_metadata(work):
        # A journal is standalone: no config includes, remote/promisor object
        # fetching, alternates, linked worktrees, or executable extensions.
        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read_string((work / ".git/config").read_text(encoding="utf-8"))
        except (configparser.Error, UnicodeError) as exc:
            raise PrerequisiteError("保留 Git 配置损坏") from exc
        allowed = {
            "core": {
                "repositoryformatversion",
                "filemode",
                "bare",
                "logallrefupdates",
                "ignorecase",
                "precomposeunicode",
                "symlinks",
            },
            "extensions": {"objectformat"},
        }
        if config.defaults() or any(
            section not in allowed or set(config[section]) - allowed[section]
            for section in config.sections()
        ):
            raise PrerequisiteError("保留 Git 配置包含未授权扩展或外部依赖")
        # git init probes filesystem link support and writes this on Windows.
        # It is repository metadata, not permission to retain actual symlinks:
        # files()/inside() and the byte-exact regular-file tree still reject them.
        if config.has_option("core", "symlinks") and config.get(
            "core", "symlinks"
        ).casefold() not in {"true", "false"}:
            raise PrerequisiteError("保留 Git core.symlinks 必须为布尔值")
        if any(
            (work / ".git" / name).exists()
            for name in (
                "commondir",
                "shallow",
                "info/grafts",
                "objects/info/alternates",
                "objects/info/http-alternates",
            )
        ) or any((work / ".git/objects").rglob("*.promisor")):
            raise PrerequisiteError("保留 Git 对象依赖外部仓库")

    def inventory(root):
        """Unfiltered bounded evidence, including every Git directory and byte."""
        result, total = {}, 0

        def failed(error):
            raise error

        for directory, dirs, names in os.walk(root, followlinks=False, onerror=failed):
            for path in [Path(directory), *(Path(directory) / name for name in sorted(names))]:
                relative = path.relative_to(root).as_posix()
                path = inside(root, relative)
                info = path.lstat()
                if stat.S_ISDIR(info.st_mode):
                    value = ("directory", stat.S_IMODE(info.st_mode))
                elif stat.S_ISREG(info.st_mode):
                    total += info.st_size
                    if info.st_size > 512_000_000 or total > 1_000_000_000:
                        raise PrerequisiteError("保留 Git 文件超过验证大小限制")
                    value = ("file", stat.S_IMODE(info.st_mode), info.st_size, sha(path))
                else:
                    raise PrerequisiteError("保留 Git 快照只允许普通文件和目录")
                result[relative] = value
                if len(result) > 100_000:
                    raise PrerequisiteError("保留 Git 文件数量超过验证限制")
            # Check children before os.walk can traverse any Windows junction.
            for name in dirs:
                inside(root, (Path(directory) / name).relative_to(root).as_posix())
        return result

    def source_inventory(work):
        result = inventory(work)
        allowed_dirs = {"."}
        for name in listing:
            allowed_dirs.update(parent.as_posix() for parent in Path(name).parents)
        for name, entry in result.items():
            if name == ".git" or name.startswith(".git/"):
                continue
            if (entry[0] == "file" and name not in listing) or (
                entry[0] == "directory" and name not in allowed_dirs
            ):
                raise PrerequisiteError("保留源码包含未纳入交付的额外文件或目录")
        return result

    def copy_bound(source, target, expected):
        """Copy approved regular paths, preserving bytes/modes, never Git-clone."""
        try:
            target.mkdir()
            for name, entry in sorted(expected.items()):
                if name == ".":
                    continue
                original, copied = inside(source, name), inside(target, name)
                if entry[0] == "directory":
                    copied.mkdir()
                else:
                    shutil.copy2(original, copied, follow_symlinks=False)
            for name, entry in sorted(expected.items(), reverse=True):
                if entry[0] == "directory":
                    shutil.copystat(
                        inside(source, name), inside(target, name), follow_symlinks=False
                    )
            if inventory(source) != expected or inventory(target) != expected:
                raise PrerequisiteError("保留 Git 快照在复制期间发生变化")
        except PermissionError:
            raise
        except OSError as exc:
            raise SnapshotResourceUnavailable("无法完整复制保留 Git 快照") from exc

    def check_short_root(root):
        # Git accesses objects/config before core.longpaths is initialized. Its
        # subprocess cwd also has a Windows MAX_PATH limit. Never change host
        # settings or create aliases; require a private shallow system temp.
        if len(str(root.resolve()).encode("utf-16-le")) // 2 > 160:
            raise SnapshotResourceUnavailable("系统临时目录过深，无法安全验证本机 Git 快照")

    def verify(work, home, receipt):
        # Do not trust the index, status, receipt, replace refs, or ignored .git
        # contents to bind a commit to the filtered source bytes.
        try:
            check_metadata(work)

            def query(*args):
                output = journal_git(
                    work, home, "--no-replace-objects", "-c", "core.fsmonitor=false", *args
                )["log"].strip()
                # The shared runner combines stderr with stdout. Warnings must
                # never be discarded to manufacture a trusted path/object ID.
                if args[0] == "rev-parse" and len(output.splitlines()) != 1:
                    raise PrerequisiteError("Git 身份查询包含警告或非单行输出")
                return output

            # Windows can expose the same directory through long-path/8.3 names.
            # Compare filesystem identity, not the spelling returned by Git.
            if not Path(query("rev-parse", "--show-toplevel")).samefile(work):
                raise PrerequisiteError("源码提交不属于独立保留仓库")
            if not Path(query("rev-parse", "--absolute-git-dir")).samefile(work / ".git"):
                raise PrerequisiteError("源码提交 Git 目录不匹配")
            algorithm = query("rev-parse", "--show-object-format")
            if algorithm not in {"sha1", "sha256"}:
                raise PrerequisiteError("源码提交使用未知对象格式")
            commit = query("rev-parse", "--verify", "HEAD^{commit}")
            if receipt != expected_receipt(commit):
                raise PrerequisiteError("源码提交回执与 HEAD 或摘要不匹配")

            def object_hash(kind, data):
                return hashlib.new(
                    algorithm, kind + b" " + str(len(data)).encode() + b"\0" + data
                ).digest()

            tree = {}
            for name, path in files(work):
                # copyfile creates non-executable journal files. On POSIX, a
                # later mode change must not be hidden by the content manifest.
                if os.name != "nt" and path.stat().st_mode & 0o111:
                    raise PrerequisiteError("保留源码文件执行权限已被修改")
                node = tree
                parts = name.split("/")
                for part in parts[:-1]:
                    node = node.setdefault(part, {})
                node[parts[-1]] = object_hash(b"blob", path.read_bytes())

            def tree_hash(node):
                entries = []
                for name, value in node.items():
                    directory = isinstance(value, dict)
                    mode = b"40000" if directory else b"100644"
                    encoded = os.fsencode(name)
                    oid = tree_hash(value) if directory else value
                    entries.append(
                        (
                            encoded + (b"/" if directory else b""),
                            mode + b" " + encoded + b"\0" + oid,
                        )
                    )
                return object_hash(b"tree", b"".join(body for _, body in sorted(entries)))

            if query("rev-parse", "--verify", "HEAD^{tree}") != tree_hash(tree).hex():
                raise PrerequisiteError("源码提交树与过滤源码内容不匹配")
            query("fsck", "--strict", "--no-reflogs", "--no-dangling", commit)
            if manifest(work) != listing or manifest(destination) != listing:
                raise PrerequisiteError("源码在保留提交期间发生变化")
        except PermissionError:
            raise
        except (OSError, ToolFailure) as exc:
            raise PrerequisiteError("无法验证保留 Git 仓库的完整性") from exc

    if base.exists():
        work = inside(base, "source")
        metadata = inside(work, ".git")
        if not receipt_path.is_file() or not work.is_dir() or not metadata.is_dir():
            raise PrerequisiteError("保留源码提交缺少回执或独立 Git 仓库")
        before = source_inventory(work)
        check_metadata(work)
        receipt_bytes = receipt_path.read_bytes()
        try:
            receipt = json.loads(receipt_bytes)
        except (ValueError, UnicodeError) as exc:
            raise PrerequisiteError("保留源码提交回执损坏") from exc
        commit = receipt.get("commit") if isinstance(receipt, dict) else None
        if not isinstance(commit, str) or not re.fullmatch(
            r"(?:[0-9a-f]{40}|[0-9a-f]{64})", commit
        ):
            raise PrerequisiteError("保留源码提交回执无效")
        if receipt != expected_receipt(commit) or manifest(work) != listing:
            raise PrerequisiteError("保留源码提交已被修改，拒绝复用")
        if not shutil.which("git"):
            return unavailable()
        anchors = [
            (path.stat().st_dev, path.stat().st_ino) for path in (work, metadata, receipt_path)
        ]
        # Validate an exact copy in a shallow directory: Git's startup accesses
        # can precede long-path configuration. The original is never rewritten.
        try:
            with tempfile.TemporaryDirectory(prefix="rnd-git-") as temporary:
                root = Path(temporary)
                check_short_root(root)
                clone, home = root / "source", root / "home"
                home.mkdir()
                atomic_text(home / "empty", "")
                copy_bound(work, clone, before)
                verify(clone, home, receipt)
                inside(base, "source")
                inside(work, ".git")
                inside(base, "commit.json")
                if inventory(clone) != before or source_inventory(work) != before:
                    raise PrerequisiteError("保留 Git 快照在验证期间发生变化")
                if receipt_path.read_bytes() != receipt_bytes or anchors != [
                    (path.stat().st_dev, path.stat().st_ino)
                    for path in (work, metadata, receipt_path)
                ]:
                    raise PrerequisiteError("保留 Git 原始目录或回执在验证期间发生变化")
                if manifest(destination) != listing:
                    raise PrerequisiteError("源码在保留提交期间发生变化")
        except SnapshotResourceUnavailable as exc:
            raise PrerequisiteError("临时存储不可用，无法验证保留 Git 快照") from exc
        return receipt
    if not shutil.which("git"):
        return unavailable()

    base.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="rnd-git-") as temporary:
            root = Path(temporary)
            check_short_root(root)
            work, home = root / "source", root / "home"
            work.mkdir()
            home.mkdir()
            atomic_text(home / "empty", "")
            for name, source in files(destination):
                target = inside(work, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            journal_git(work, home, "-c", "core.autocrlf=false", "init", "-q")
            # Highest-precedence attributes prevent source-controlled .gitattributes
            # from transforming bytes or requesting clean/encoding filters.
            atomic_text(
                work / ".git/info/attributes", "* -text -filter -ident -working-tree-encoding\n"
            )
            journal_git(
                work,
                home,
                "-c",
                "core.autocrlf=false",
                "-c",
                "core.fsmonitor=false",
                "add",
                "-f",
                "--",
                ".",
            )
            journal_git(
                work,
                home,
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--allow-empty",
                "-qm",
                "Retained source candidate: NOT runtime verified or accepted",
            )
            commit = journal_git(work, home, "rev-parse", "HEAD")["log"].strip()
            receipt = expected_receipt(commit)
            if manifest(work) != listing or manifest(destination) != listing:
                raise PrerequisiteError("源码在保留提交期间发生变化")
            verified_inventory = source_inventory(work)
            verify(work, home, receipt)
            if source_inventory(work) != verified_inventory:
                raise PrerequisiteError("Git 快照在验证期间发生变化")
            write_json(root / "commit.json", receipt)
            publication = inventory(root)
            receipt_data = (
                json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
            ).encode("utf-8")
            publication["commit.json"] = (
                "file",
                publication["commit.json"][1],
                len(receipt_data),
                hashlib.sha256(receipt_data).hexdigest(),
            )
            # Never bless a changed source by sampling a fresh publication tree.
            publication = {
                name: entry
                for name, entry in publication.items()
                if name != "source" and not name.startswith("source/")
            }
            publication.update(
                {
                    "source" if name == "." else "source/" + name: entry
                    for name, entry in verified_inventory.items()
                }
            )
            # Publish on the destination volume only after byte/mode verification;
            # system temp and the permanent journal may be on different drives.
            with tempfile.TemporaryDirectory(
                prefix="snapshot-publish-", dir=base.parent
            ) as publish:
                staging = Path(publish) / "journal"
                copy_bound(root, staging, publication)
                if manifest(destination) != listing:
                    raise PrerequisiteError("源码在保留提交期间发生变化")
                staging.replace(base)
            return receipt
    except PermissionError:
        raise
    except (OSError, ToolFailure) as exc:
        return {
            "status": "failed",
            "git_available": True,
            "source_digest": identity,
            "note": "源码已保存，Git 提交未成功：" + type(exc).__name__,
        }


_STATUS_KEYS = (
    "template",
    "spec_digest",
    "execution",
    "generation_status",
    "verification_status",
    "pending_steps",
    "runtime_unavailable_reason",
    "runtime_verified",
    "production_ready",
    "acceptance_passed",
    "validation_level",
)


def candidate_status(receipt):
    status = {key: receipt.get(key) for key in _STATUS_KEYS}
    if "source_derivation" in receipt:
        status["source_derivation"] = receipt["source_derivation"]
    return status


def check_status_binding(destination, receipt):
    """A mutable generation receipt cannot upgrade the saved controller statement."""
    destination = Path(destination)
    statement = inside(destination, "SOURCE-STATUS.json")
    retained = inside(destination.parent, "source-candidate-status.json")
    expected = candidate_status(receipt)
    if receipt.get("preserve_runtime_files"):
        if statement.exists() or not retained.is_file():
            raise PrerequisiteError("保留运行源码的状态证据缺失或模式不匹配")
        evidence = json.loads(retained.read_text(encoding="utf-8"))
        checkpoint = inside(destination.parent, "native-evidence/recovery.json")
        if evidence != {
            "status": expected,
            "source_digest": digest(receipt.get("files", {})),
            "recovery_sha256": sha(checkpoint) if checkpoint.is_file() else None,
        }:
            raise PrerequisiteError("保留运行源码的状态或恢复证据不一致")
    elif not statement.is_file() or json.loads(statement.read_text(encoding="utf-8")) != expected:
        raise PrerequisiteError("候选源码状态声明与生成回执不一致")
    if (
        expected["runtime_verified"] is not False
        or expected["production_ready"] is not False
        or expected["acceptance_passed"] is not False
        or expected["validation_level"] != "source"
    ):
        raise PrerequisiteError("候选源码不能声明运行或生产验收通过")


def refresh_candidate(
    destination, receipt, *, pending_steps=None, generated_files=None, generation_status=None
):
    """Bind controller-approved source edits to a new unaccepted source snapshot."""
    destination = Path(destination)
    if receipt.get("execution") != "source-candidate":
        raise PrerequisiteError("不能把运行验收回执降级为候选源码")
    saved_path = inside(destination.parent, "native-generation.json")
    saved = json.loads(saved_path.read_text(encoding="utf-8")) if saved_path.is_file() else {}
    if (
        "files" in receipt
        or inside(destination, "SOURCE-STATUS.json").exists()
        or inside(destination.parent, "source-candidate-status.json").exists()
        or saved.get("execution") == "source-candidate"
    ):
        check_status_binding(destination, receipt)
    receipt = dict(receipt)
    for key, value in (
        ("pending_steps", pending_steps),
        ("generated_files", generated_files),
        ("generation_status", generation_status),
    ):
        if value is not None:
            receipt[key] = value
    receipt.update(
        validation_level="source",
        runtime_verified=False,
        production_ready=False,
        acceptance_passed=False,
    )
    receipt["pending_steps"] = list(
        dict.fromkeys([*receipt.get("pending_steps", []), continuation_step(receipt["template"])])
    )
    receipt.setdefault("verification_status", "unverified")
    if receipt["verification_status"] not in {"unverified", "failed"}:
        raise PrerequisiteError("候选源码不能带有运行验证通过状态")
    status = candidate_status(receipt)
    if not receipt.get("preserve_runtime_files"):
        write_status(destination, status)
    receipt["files"] = manifest(destination)
    if receipt.get("preserve_runtime_files"):
        checkpoint = inside(destination.parent, "native-evidence/recovery.json")
        write_json(
            inside(destination.parent, "source-candidate-status.json"),
            {
                "status": status,
                "source_digest": digest(receipt["files"]),
                "recovery_sha256": sha(checkpoint) if checkpoint.is_file() else None,
            },
        )
    receipt["source_commit"] = source_snapshot(destination)
    write_json(destination.parent / "native-generation.json", receipt)
    return receipt


def derive_candidate(
    source,
    edited,
    destination,
    base_receipt,
    edit_receipt,
    *,
    derivation,
    pending_steps,
    generated_files,
):
    """Atomically publish an independently bound draft; never alter recovery source."""
    source, edited, destination = Path(source), Path(edited), Path(destination)
    expected_destination = inside(edited.parent, "source/product")
    if destination.absolute() != expected_destination.absolute():
        raise PrerequisiteError("派生候选目标不属于本次编辑的独立目录")
    destination = expected_destination
    verify_candidate(source, base_receipt)
    original = manifest(source)
    raw_files = manifest(edited)
    if edit_receipt.get("before") != original or edit_receipt.get("files") != raw_files:
        raise PrerequisiteError("派生候选与已验证父源码或原始编辑回执不一致")
    expected = {
        "parent_receipt_digest": digest(base_receipt),
        "edit_identity": edit_receipt.get("identity"),
        "task": edit_receipt.get("task"),
        "approved_files": derivation.get("approved_files"),
        "candidate_edit_files_digest": digest(raw_files),
    }
    if derivation != expected or not isinstance(expected["approved_files"], list):
        raise PrerequisiteError("派生候选任务身份不一致")
    approved = set(expected["approved_files"])
    reserved = {"source-status.json", "source-status.md", "rnd-source-scope.json"}
    if (
        any(name.casefold() in reserved for name in approved)
        or {
            name
            for name in set(original) | set(raw_files)
            if original.get(name) != raw_files.get(name)
        }
        - approved
    ):
        raise PrerequisiteError("派生候选修改超出批准文件范围")
    bound = {
        **derivation,
        "pending_steps_digest": digest(pending_steps),
        "generated_files_digest": digest(generated_files),
    }
    target = destination.parent
    if target.exists():
        saved_path = inside(target, "native-generation.json")
        if not saved_path.is_file():
            raise PrerequisiteError("派生候选缺少完整发布回执")
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        if saved.get("source_derivation") != bound:
            raise PrerequisiteError("持久化派生候选与父源码或任务身份不一致")
        verify_candidate(destination, saved)
        return saved
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="source-derive-", dir=target.parent) as temporary:
        stage = Path(temporary) / "published"
        product = stage / destination.name
        product.mkdir(parents=True)
        for name, path in files(edited):
            output = inside(product, name)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, output)
        if manifest(product) != raw_files:
            raise PrerequisiteError("派生候选复制过程中发生变化")
        # These statements are controller-owned, already checked against the
        # parent manifest. Only the new temporary draft receives a new statement.
        for name in ("SOURCE-STATUS.json", "SOURCE-STATUS.md"):
            inside(product, name).unlink(missing_ok=True)
        fresh = {
            key: value
            for key, value in base_receipt.items()
            if key not in {"files", "source_commit", "preserve_runtime_files", "source_derivation"}
        }
        fresh["source_derivation"] = bound
        result = refresh_candidate(
            product,
            fresh,
            pending_steps=pending_steps,
            generated_files=generated_files,
        )
        verify_candidate(product, result)
        # Recheck both inputs immediately before publishing a complete directory.
        verify_candidate(source, base_receipt)
        if manifest(edited) != raw_files:
            raise PrerequisiteError("原始编辑候选在发布期间发生变化")
        stage.replace(target)
    return result


def write_status(destination, status):
    write_json(destination / "SOURCE-STATUS.json", status)
    atomic_text(
        destination / "SOURCE-STATUS.md",
        "# 未验收源码候选\n\n"
        + ("生成尚未完成。\n" if status["generation_status"] == "partial" else "源码已生成。\n")
        + (
            "运行验证失败。\n"
            if status["verification_status"] == "failed"
            else "尚未进行运行验证。\n"
        )
        + "保存、提交或下载不代表验收通过，也没有部署。\n\n"
        + "待完成事项：\n"
        + "".join("- " + item + "\n" for item in status["pending_steps"]),
    )


def retain_failed_candidate(template, plan, destination, sources, error_type):
    """Keep the runtime workspace byte-for-byte so recovery evidence stays valid."""
    destination = Path(destination)
    listing = manifest(destination)
    if not listing:
        raise PrerequisiteError("运行失败且尚未生成源码；没有可保留的候选")
    checkpoint = destination.parent / "native-evidence/recovery.json"
    recovery = json.loads(checkpoint.read_text(encoding="utf-8")) if checkpoint.is_file() else {}
    if recovery and recovery.get("files") != listing:
        raise PrerequisiteError("失败现场与恢复检查点不一致，拒绝将其作为源码候选")
    generated = bool(recovery.get("targets")) and recovery.get("stage") == "validation-interrupted"
    baseline = {}
    for source in sources:
        if digest(manifest(source["path"])) != source["source_digest"]:
            raise PrerequisiteError("原始模板源码已被修改，拒绝保留为可交付候选")
        prefix = (
            ""
            if template == "fastapiadmin"
            else ("backend/" if source["slot"] == "backend" else "frontend-product/")
        )
        baseline.update({prefix + name: value for name, value in manifest(source["path"]).items()})
    receipt = {
        "template": template,
        "execution": "source-candidate",
        "spec_digest": digest(plan.model_dump()),
        "sources": [{k: v for k, v in item.items() if k != "path"} for item in sources],
        "generation_status": "complete" if generated and not plan.custom_rules else "partial",
        "verification_status": "failed" if generated else "unverified",
        "runtime_unavailable_reason": "原生运行流程未完成（"
        + error_type
        + "）；源码已保留，原始诊断在本机运行证据中",
        "pending_steps": [
            "检查本机原生运行失败证据",
            "在具备能力且获授权的环境恢复生成和运行验收",
            *[
                "Implement/review and runtime-verify approved custom rule "
                + rule.entity
                + ": "
                + rule.description
                for rule in plan.custom_rules
            ],
        ],
        "generated_files": [name for name, value in listing.items() if baseline.get(name) != value],
        "preserve_runtime_files": True,
    }
    return refresh_candidate(destination, receipt)


def _publish_new(source, target):
    """Atomic no-replace publication; unsupported systems must fail closed."""
    import ctypes
    import os
    import sys

    if os.name == "nt":
        os.rename(source, target)  # Windows never replaces an existing target.
        return
    library = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "linux":
        function = getattr(library, "renameat2", None)
        if function is None:
            raise PrerequisiteError("系统缺少安全的不覆盖发布能力")
        function.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        args = (-100, os.fsencode(source), -100, os.fsencode(target), 1)
    elif sys.platform == "darwin":
        function = getattr(library, "renamex_np", None)
        if function is None:
            raise PrerequisiteError("系统缺少安全的不覆盖发布能力")
        function.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        args = (os.fsencode(source), os.fsencode(target), 4)
    else:
        raise PrerequisiteError("当前系统不支持安全的不覆盖发布")
    function.restype = ctypes.c_int
    if function(*args):
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))


def _transaction_tree(root):
    """Bind every byte and mode, including Git metadata and excluded filenames."""
    import os
    import stat

    root = inside(Path(root).parent, Path(root).name)
    if not root.is_dir():
        raise PrerequisiteError("源码事务目录缺失")
    result, total = {}, 0

    def denied(error):
        raise error

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=denied):
        for name in sorted(dirs + names):
            path = inside(root, (Path(directory) / name).relative_to(root).as_posix())
            info = path.lstat()
            relative = path.relative_to(root).as_posix()
            if stat.S_ISDIR(info.st_mode):
                result[relative] = ["directory", stat.S_IMODE(info.st_mode)]
            elif stat.S_ISREG(info.st_mode):
                total += info.st_size
                if info.st_size > 512_000_000 or total > 1_000_000_000:
                    raise PrerequisiteError("源码事务超过验证大小限制")
                result[relative] = ["file", stat.S_IMODE(info.st_mode), info.st_size, sha(path)]
            else:
                raise PrerequisiteError("源码事务只允许普通文件和目录")
            if len(result) > 100_000:
                raise PrerequisiteError("源码事务超过验证文件数量限制")
    return result


def recover_candidate(template, plan, destination):
    """Resume only a complete, identity-bound source publication transaction."""
    destination = Path(destination)
    transaction = inside(destination.parent, ".source-candidate-transaction")
    if not transaction.exists():
        return None
    seal_path = inside(transaction, "transaction.json")
    stage = inside(transaction, "candidate")
    seal_bytes = seal_path.read_bytes()
    seal = json.loads(seal_bytes)
    expected = {
        "version": 1,
        "template": template,
        "spec_digest": digest(plan.model_dump()),
        "product": destination.name,
    }
    if (
        not isinstance(seal, dict)
        or set(seal) != {*expected, "tree", "receipt"}
        or any(seal.get(key) != value for key, value in expected.items())
    ):
        raise PrerequisiteError("源码事务与批准设计或目标不匹配")
    before = _transaction_tree(stage)
    if before != seal["tree"]:
        raise PrerequisiteError("源码事务内容已改变，拒绝恢复")
    receipt = json.loads(inside(stage, "native-generation.json").read_text(encoding="utf-8"))
    if (
        receipt != seal["receipt"]
        or receipt.get("template") != template
        or receipt.get("spec_digest") != expected["spec_digest"]
    ):
        raise PrerequisiteError("源码事务回执不匹配")
    product_files = {
        name[len(destination.name) + 1 :]
        for name, entry in before.items()
        if name.startswith(destination.name + "/") and entry[0] == "file"
    }
    if product_files != set(receipt.get("files", {})):
        raise PrerequisiteError("源码事务包含未纳入交付的额外文件")
    product = inside(stage, destination.name)
    if (
        json.loads(inside(product, "approved-spec.json").read_text(encoding="utf-8"))
        != plan.model_dump()
    ):
        raise PrerequisiteError("源码事务批准设计不匹配")
    verify_candidate(product, receipt, persist=False)
    names = {Path(name).parts[0] for name in before}
    allowed = {destination.name, "native-generation.json", "verification.json", "source-revisions"}
    if (
        names - allowed
        or not {destination.name, "native-generation.json", "verification.json"} <= names
    ):
        raise PrerequisiteError("源码事务包含未知发布项")

    def matches(name, target):
        if target.is_dir():
            actual = {name: ["directory", target.stat().st_mode & 0o7777]}
            actual.update(
                {name + "/" + key: value for key, value in _transaction_tree(target).items()}
            )
        else:
            if not target.is_file():
                raise PrerequisiteError("源码事务发布目标不是普通文件")
            actual = {
                name: ["file", target.stat().st_mode & 0o7777, target.stat().st_size, sha(target)]
            }
        wanted = {
            key: value for key, value in before.items() if key == name or key.startswith(name + "/")
        }
        return actual == wanted

    # Preflight every destination before publishing any item. Matching bytes are
    # already-published evidence after a crash, never permission to overwrite.
    for name in names:
        target = inside(destination.parent, name)
        if target.exists() and not matches(name, target):
            raise PrerequisiteError("已有内容不属于本次源码事务，拒绝覆盖")
    for name in sorted(names, key=lambda value: (value == "native-generation.json", value)):
        target = inside(destination.parent, name)
        if target.exists():
            if not matches(name, target):
                raise PrerequisiteError("源码事务发布目标已改变")
            continue
        original = inside(stage, name)
        with tempfile.TemporaryDirectory(
            prefix="source-publish-", dir=destination.parent
        ) as temporary:
            copied = Path(temporary) / name
            if original.is_dir():
                copied.mkdir()
                for relative, entry in sorted(_transaction_tree(original).items()):
                    source, output = inside(original, relative), inside(copied, relative)
                    if entry[0] == "directory":
                        output.mkdir()
                    else:
                        shutil.copy2(source, output, follow_symlinks=False)
                for relative, entry in sorted(_transaction_tree(original).items(), reverse=True):
                    if entry[0] == "directory":
                        shutil.copystat(inside(original, relative), inside(copied, relative))
                shutil.copystat(original, copied)
            else:
                shutil.copy2(original, copied, follow_symlinks=False)
            if _transaction_tree(stage) != before or not matches(name, copied):
                raise PrerequisiteError("源码事务复制期间发生变化")
            if inside(destination.parent, name).exists():
                raise PrerequisiteError("源码事务目标被其他内容占用")
            _publish_new(copied, target)
    if (
        _transaction_tree(stage) != before
        or inside(transaction, "transaction.json").read_bytes() != seal_bytes
    ):
        raise PrerequisiteError("源码事务在发布期间发生变化")
    if any(not matches(name, inside(destination.parent, name)) for name in names):
        raise PrerequisiteError("已发布源码事务内容发生变化")
    verify_candidate(destination, receipt, persist=False)
    # Retire the recovery marker atomically only after all published evidence
    # validates. A later bounded edit must not be compared to this old snapshot.
    with tempfile.TemporaryDirectory(
        prefix="source-completed-", dir=destination.parent
    ) as temporary:
        _publish_new(transaction, Path(temporary) / "transaction")
    return receipt


````
