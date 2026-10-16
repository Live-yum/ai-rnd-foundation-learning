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
