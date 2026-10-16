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
    """Commit an immutable, filtered source copy; absence of Git cannot lose work."""
    destination = Path(destination)
    listing = manifest(destination)
    identity = digest(listing)
    base = destination.parent / "source-revisions" / identity
    receipt_path = base / "commit.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if manifest(base / "source") != listing:
            raise PrerequisiteError("保留源码提交已被修改，拒绝复用")
        return receipt
    if not shutil.which("git"):
        return {
            "status": "unavailable",
            "git_available": False,
            "source_digest": identity,
            "note": "未安装 Git；源码文件和摘要已保存，尚未创建 Git 提交",
        }
    from workbench.coding.aider import git
    from workbench.infrastructure.processes.tools import ToolFailure

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
            git(work, home, "init", "-q")
            git(work, home, "add", "-f", "--", ".")
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
            receipt = {
                "status": "committed",
                "git_available": True,
                "commit": commit,
                "source_digest": identity,
                "journal": "source-revisions/" + identity + "/source",
                "runtime_verified": False,
            }
            if manifest(work) != listing or manifest(destination) != listing:
                raise PrerequisiteError("源码在保留提交期间发生变化")
            write_json(root / "commit.json", receipt)
            root.replace(base)
            return receipt
    except PermissionError:
        raise
    except (OSError, ToolFailure) as exc:
        # Source files are already durable. A missing/broken Git installation is
        # neither permission to discard them nor evidence that a commit exists.
        return {
            "status": "failed",
            "git_available": True,
            "source_digest": identity,
            "note": "源码已保存，Git 提交未成功：" + type(exc).__name__,
        }


def refresh_candidate(
    destination, receipt, *, pending_steps=None, generated_files=None, generation_status=None
):
    """Bind controller-approved source edits to a new unaccepted source snapshot."""
    destination = Path(destination)
    if receipt.get("execution") != "source-candidate":
        raise PrerequisiteError("不能把运行验收回执降级为候选源码")
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
    status = {
        key: receipt[key]
        for key in (
            "execution",
            "generation_status",
            "verification_status",
            "pending_steps",
            "runtime_unavailable_reason",
            "runtime_verified",
            "production_ready",
            "acceptance_passed",
        )
    }
    if not receipt.get("preserve_runtime_files"):
        write_status(destination, status)
    receipt["files"] = manifest(destination)
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
    result = {
        key: receipt[key]
        for key in (
            "execution",
            "generation_status",
            "verification_status",
            "pending_steps",
            "runtime_unavailable_reason",
            "source_commit",
        )
    }
    result.update(
        passed=False,
        source_checks_passed=True,
        validation_level="source",
        runtime_verified=False,
        production_ready=False,
        acceptance_passed=False,
        source_digest=digest(current),
        checks=["source-manifest"],
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
