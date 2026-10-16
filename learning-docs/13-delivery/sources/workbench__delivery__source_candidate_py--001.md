# workbench/delivery/source_candidate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `continuation_step`（L17–L23）：接收`template`。 返回路径：L19的`"先下载并保留本候选；在已配置原生工具的 Linux/WSL 操作台新建运行，或执行 " f"uv run rnd chat --template {template} --fro…`。
- `source_snapshot`（L26–L255）：接收`destination`。 源码说明：Retain source; claim a commit only after independently checking its tree.。 控制顺序：L168按`base.exists()`分支；L171按`not receipt_path.is_file() or not work.is_dir() or not metadata.is_dir()`分支；L172抛异常，停止当前正常路径；L175遍历`metadata.rglob("*")`；L180抛异常，停止当前正常路径；L182按`not isinstance(commit, str) or not re.fullmatch( r"(?:[0-9a-f]{40}\|[0-9a-f]{64})", c…`分支；L185抛异常，停止当前正常路径；L186按`receipt != expected_receipt(commit) or manifest(work) != listing`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`manifest`、`digest`、`inside`、`base.exists`、`receipt_path.is_file`、`work.is_dir`、`metadata.is_dir`、`PrerequisiteError`等。 返回路径：L189的`unavailable()`；L195的`receipt`；L197的`unavailable()`。
- `source_snapshot.unavailable`（L42–L48）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L43的`{ "status": "unavailable", "git_available": False, "source_digest": identity, "note": "Git…`。
- `source_snapshot.expected_receipt`（L50–L58）：接收`commit`。 返回路径：L51的`{ "status": "committed", "git_available": True, "commit": commit, "source_digest": identit…`。
- `source_snapshot.verify`（L60–L166）：接收`work`、`home`、`receipt`。 控制顺序：L70抛异常，停止当前正常路径；L83按`config.defaults() or any( section not in allowed or set(config[section]) - allowed[se…`分支；L87抛异常，停止当前正常路径；L91按`config.has_option("core", "symlinks") and config.get( "core", "symlinks" ).casefold()…`分支；L94抛异常，停止当前正常路径；L95按`any( (work / ".git" / name).exists() for name in ( "commondir", "shallow", "info/graf…`分支；L105抛异常，停止当前正常路径；L112按`Path(query("rev-parse", "--show-toplevel")).resolve() != work.resolve()`分支。后续分支沿下方源码相同行号继续阅读。 调用`configparser.ConfigParser`、`config.read_string`、`(work / ".git/config").read_text`、`PrerequisiteError`、`config.defaults`、`any`、`set`、`config.sections`、`config.has_option`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_snapshot.verify.query`（L107–L110）：接收`*args`。 调用`git(work, home, "--no-replace-objects", "-c", "core.fsmonitor=fal…`、`git`。 返回路径：L108的`git(work, home, "--no-replace-objects", "-c", "core.fsmonitor=false", *args)[ "log" ].stri…`。
- `source_snapshot.verify.object_hash`（L126–L129）：接收`kind`、`data`。 调用`hashlib.new( algorithm, kind + b" " + str(len(data)).encode() + b…`、`hashlib.new`、`str(len(data)).encode`、`str`、`len`。 返回路径：L127的`hashlib.new( algorithm, kind + b" " + str(len(data)).encode() + b"\0" + data ).digest()`。
- `source_snapshot.verify.tree_hash`（L143–L156）：接收`node`。 控制顺序：L145遍历`node.items()`。 调用`node.items`、`isinstance`、`os.fsencode`、`tree_hash`、`entries.append`、`object_hash`、`b"".join`、`sorted`。 返回路径：L156的`object_hash(b"tree", b"".join(body for _, body in sorted(entries)))`。
- `candidate_status`（L273–L274）：接收`receipt`。 调用`receipt.get`。 返回路径：L274的`{key: receipt.get(key) for key in _STATUS_KEYS}`。
- `check_status_binding`（L277–L302）：接收`destination`、`receipt`。 源码说明：A mutable generation receipt cannot upgrade the saved controller statement.。 控制顺序：L283按`receipt.get("preserve_runtime_files")`分支；L284按`statement.exists() or not retained.is_file()`分支；L285抛异常，停止当前正常路径；L288按`evidence != { "status": expected, "source_digest": digest(receipt.get("files", {})), …`分支；L293抛异常，停止当前正常路径；L294按`not statement.is_file() or json.loads(statement.read_text(encoding="utf-8")) != expec…`分支；L295抛异常，停止当前正常路径；L296按`expected["runtime_verified"] is not False or expected["production_ready"] is not Fals…`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`inside`、`candidate_status`、`receipt.get`、`statement.exists`、`retained.is_file`、`PrerequisiteError`、`json.loads`、`retained.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `refresh_candidate`（L305–L357）：接收`destination`、`receipt`、`pending_steps`、`generated_files`、`generation_status`。 源码说明：Bind controller-approved source edits to a new unaccepted source snapshot.。 控制顺序：L310按`receipt.get("execution") != "source-candidate"`分支；L311抛异常，停止当前正常路径；L314按`"files" in receipt or inside(destination, "SOURCE-STATUS.json").exists() or inside(de…`分支；L322遍历`( ("pending_steps", pending_steps), ("generated_files", generated…`；L327按`value is not None`分支；L339按`receipt["verification_status"] not in {"unverified", "failed"}`分支；L340抛异常，停止当前正常路径；L342按`not receipt.get("preserve_runtime_files")`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`receipt.get`、`PrerequisiteError`、`inside`、`saved_path.is_file`、`json.loads`、`saved_path.read_text`、`inside(destination, "SOURCE-STATUS.json").exists`、`inside(destination.parent, "source-candidate-status.json").exists`等。 返回路径：L357的`receipt`。
- `write_status`（L360–L374）：接收`destination`、`status`。 调用`write_json`、`atomic_text`、`"".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `retain_failed_candidate`（L377–L412）：接收`template`、`plan`、`destination`、`sources`、`error_type`。 源码说明：Keep the runtime workspace byte-for-byte so recovery evidence stays valid.。 控制顺序：L381按`not listing`分支；L382抛异常，停止当前正常路径；L385按`recovery and recovery.get("files") != listing`分支；L386抛异常，停止当前正常路径；L389遍历`sources`；L390按`digest(manifest(source["path"])) != source["source_digest"]`分支；L391抛异常，停止当前正常路径。 调用`Path`、`manifest`、`PrerequisiteError`、`checkpoint.is_file`、`json.loads`、`checkpoint.read_text`、`recovery.get`、`bool`、`digest`等。 返回路径：L412的`refresh_candidate(destination, receipt)`。
- `generate_candidate`（L415–L443）：接收`settings`、`template`、`plan`、`destination`、`reason`。 控制顺序：L422按`destination.exists()`分支；L423抛异常，停止当前正常路径；L426按`template == "fastapiadmin"`分支。 调用`Path`、`destination.exists`、`PrerequisiteError`、`prepare_sources`、`copy_source`、`write_json`、`plan.model_dump`、`write_coding_standard`、`generate_offline`等。 返回路径：L443的`refresh_candidate(destination, receipt)`。
- `verify_candidate`（L446–L509）：接收`destination`、`receipt`。 控制顺序：L449按`receipt.get("execution") != "source-candidate" or receipt.get("generation_status") no…`分支；L453抛异常，停止当前正常路径；L454按`not current or current != receipt.get("files")`分支；L455抛异常，停止当前正常路径；L456按`receipt.get("runtime_verified") is not False or receipt.get("verification_status") no…`分支；L460抛异常，停止当前正常路径；L463按`not isinstance(claim, dict) or claim.get("status") not in { "committed", "unavailable…`分支；L468抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`manifest`、`receipt.get`、`PrerequisiteError`、`check_status_binding`、`isinstance`、`claim.get`、`inside`、`digest`等。 返回路径：L509的`result`。
- `package_candidate`（L512–L544）：接收`destination`、`report`。 控制顺序：L518按`report != verified`分支；L519抛异常，停止当前正常路径；L522按`receipt.get("preserve_runtime_files")`分支；L525遍历`files(destination)`；L534按`manifest(destination) != receipt["files"]`分支；L535抛异常，停止当前正常路径。 调用`Path`、`json.loads`、`(destination.parent / "native-generation.json").read_text`、`verify_candidate`、`PrerequisiteError`、`manifest`、`receipt.get`、`tempfile.TemporaryDirectory`、`files`等。 返回路径：L544的`result`。

</details>

**创建路径：** `workbench/delivery/source_candidate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L544。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`24019`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/delivery/source_candidate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a31d99282ad1d9caa68c5fcdd8078d1f074e3f60171d6e12347b131d5f2b249b"} -->
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

    from workbench.coding.aider import git
    from workbench.infrastructure.processes.tools import ToolFailure

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

    def verify(work, home, receipt):
        # Do not trust the index, status, receipt, replace refs, or ignored .git
        # contents to bind a commit to the filtered source bytes.
        try:
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

            def query(*args):
                return git(work, home, "--no-replace-objects", "-c", "core.fsmonitor=false", *args)[
                    "log"
                ].strip()

            if Path(query("rev-parse", "--show-toplevel")).resolve() != work.resolve():
                raise PrerequisiteError("源码提交不属于独立保留仓库")
            if (
                Path(query("rev-parse", "--absolute-git-dir")).resolve()
                != (work / ".git").resolve()
            ):
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
        # Git metadata is omitted by manifest(), so enforce its path boundary
        # separately before Git can follow a redirected ref/object/config path.
        for path in metadata.rglob("*"):
            inside(work, path.relative_to(work).as_posix())
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
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
        # Never reuse cached HOME/config: it is mutable metadata too.
        with tempfile.TemporaryDirectory(prefix="snapshot-verify-") as temporary:
            home = Path(temporary)
            atomic_text(home / "empty", "")
            verify(work, home, receipt)
        return receipt
    if not shutil.which("git"):
        return unavailable()

    base.parent.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix="snapshot-", dir=base.parent) as temporary:
            root = Path(temporary)
            work, home = root / "source", root / "home"
            work.mkdir()
            home.mkdir()
            atomic_text(home / "empty", "")
            for name, source in files(destination):
                target = inside(work, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            git(work, home, "-c", "core.autocrlf=false", "init", "-q")
            # Highest-precedence attributes prevent source-controlled .gitattributes
            # from transforming bytes or requesting clean/encoding filters.
            atomic_text(
                work / ".git/info/attributes", "* -text -filter -ident -working-tree-encoding\n"
            )
            git(
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
            git(
                work,
                home,
                "-c",
                "commit.gpgsign=false",
                "commit",
                "--allow-empty",
                "-qm",
                "Retained source candidate: NOT runtime verified or accepted",
            )
            commit = git(work, home, "rev-parse", "HEAD")["log"].strip()
            receipt = expected_receipt(commit)
            if manifest(work) != listing or manifest(destination) != listing:
                raise PrerequisiteError("源码在保留提交期间发生变化")
            verify(work, home, receipt)
            write_json(root / "commit.json", receipt)
            root.replace(base)
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
    return {key: receipt.get(key) for key in _STATUS_KEYS}


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
        "pending_steps": ["检查本机原生运行失败证据", "在具备能力且获授权的环境恢复生成和运行验收"],
        "generated_files": [name for name, value in listing.items() if baseline.get(name) != value],
        "preserve_runtime_files": True,
    }
    return refresh_candidate(destination, receipt)


def generate_candidate(settings, template, plan, destination, reason):
    from workbench.generation.native.offline import generate_offline
    from workbench.generation.native.service import prepare_sources
    from workbench.infrastructure.native.environment import copy_source
    from workbench.templates.standards import write_coding_standard

    destination = Path(destination)
    if destination.exists():
        raise PrerequisiteError("已有源码不能被离线生成覆盖；请保留当前运行并创建新的运行")
    sources = prepare_sources(settings, template)
    slots = {item["slot"]: Path(item["path"]) for item in sources}
    if template == "fastapiadmin":
        copy_source(slots["fastapiadmin"], destination)
    else:
        copy_source(slots["backend"], destination / "backend")
        copy_source(slots["frontend"], destination / "frontend-product")
    write_json(destination / "approved-spec.json", plan.model_dump())
    write_coding_standard(destination, template)
    generated = generate_offline(template, plan, destination, sources)
    receipt = {
        "template": template,
        "execution": "source-candidate",
        "spec_digest": digest(plan.model_dump()),
        "sources": [{k: v for k, v in item.items() if k != "path"} for item in sources],
        "verification_status": "unverified",
        "runtime_unavailable_reason": reason,
        **generated,
    }
    return refresh_candidate(destination, receipt)


def verify_candidate(destination, receipt):
    destination = Path(destination)
    current = manifest(destination)
    if receipt.get("execution") != "source-candidate" or receipt.get("generation_status") not in {
        "complete",
        "partial",
    }:
        raise PrerequisiteError("候选源码身份或生成状态无效")
    if not current or current != receipt.get("files"):
        raise PrerequisiteError("候选源码与保存摘要不一致，拒绝打包")
    if receipt.get("runtime_verified") is not False or receipt.get("verification_status") not in {
        "unverified",
        "failed",
    }:
        raise PrerequisiteError("候选源码的运行状态无效")
    check_status_binding(destination, receipt)
    claim = receipt.get("source_commit")
    if not isinstance(claim, dict) or claim.get("status") not in {
        "committed",
        "unavailable",
        "failed",
    }:
        raise PrerequisiteError("候选源码提交声明无效")
    if claim["status"] == "committed":
        # Verification must never repair or recreate a missing journal. Its path
        # comes from current source identity, never from the mutable receipt.
        journal = inside(destination.parent, "source-revisions/" + digest(current))
        if not journal.is_dir():
            raise PrerequisiteError("候选源码提交记录缺失，拒绝宣称已提交")
        checked_commit = source_snapshot(destination)
        if checked_commit["status"] == "committed" and checked_commit != claim:
            raise PrerequisiteError("候选源码提交声明与实际 Git 证据不一致")
    else:
        # Non-commit receipts cannot smuggle arbitrary commit IDs/journal paths
        # into delivery reports. Do not create a new Git history during verification.
        checked_commit = {
            "status": claim["status"],
            "source_digest": digest(current),
            "note": "没有已验证的 Git 提交；仅保留源码及摘要",
        }
    result = {
        key: receipt[key]
        for key in (
            "execution",
            "generation_status",
            "verification_status",
            "pending_steps",
            "runtime_unavailable_reason",
        )
    }
    result.update(
        source_commit=checked_commit,
        passed=False,
        source_checks_passed=True,
        validation_level="source",
        runtime_verified=False,
        production_ready=False,
        acceptance_passed=False,
        source_digest=digest(current),
        checks=["source-manifest"]
        + (["source-git-journal"] if checked_commit["status"] == "committed" else []),
    )
    write_json(destination.parent / "verification.json", result)
    return result


def package_candidate(destination, report):
    destination = Path(destination)
    receipt = json.loads(
        (destination.parent / "native-generation.json").read_text(encoding="utf-8")
    )
    verified = verify_candidate(destination, receipt)
    if report != verified:
        raise PrerequisiteError("候选源码报告不匹配")
    package = destination.parent / "native-source.zip"
    listing = manifest(destination)
    if receipt.get("preserve_runtime_files"):
        with tempfile.TemporaryDirectory(prefix="source-package-", dir=destination.parent) as temp:
            root = Path(temp)
            for name, path in files(destination):
                target = inside(root, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            write_status(root, verified)
            archive = pack_source(root, package, template=receipt["template"])
            listing = manifest(root)
    else:
        archive = pack_source(destination, package, template=receipt["template"])
    if manifest(destination) != receipt["files"]:
        raise PrerequisiteError("源码在打包期间发生变化，拒绝发布")
    result = {
        **verified,
        "package": package.name,
        "sha256": sha(package),
        "files": listing,
        "archive": archive,
    }
    write_json(destination.parent / "delivery.json", result)
    return result
````
