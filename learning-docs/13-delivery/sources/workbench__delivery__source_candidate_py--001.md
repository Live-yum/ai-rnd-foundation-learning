# workbench/delivery/source_candidate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `continuation_step`（L17–L23）：接收`template`。 返回路径：L19的`"先下载并保留本候选；在已配置原生工具的 Linux/WSL 操作台新建运行，或执行 " f"uv run rnd chat --template {template} --fro…`。
- `source_snapshot`（L26–L96）：接收`destination`。 源码说明：Commit an immutable, filtered source copy; absence of Git cannot lose work.。 控制顺序：L33按`receipt_path.is_file()`分支；L35按`manifest(base / "source") != listing`分支；L36抛异常，停止当前正常路径；L38按`not shutil.which("git")`分支；L56遍历`files(destination)`；L81按`manifest(work) != listing or manifest(destination) != listing`分支；L82抛异常，停止当前正常路径；L87抛异常，停止当前正常路径。 调用`Path`、`manifest`、`digest`、`receipt_path.is_file`、`json.loads`、`receipt_path.read_text`、`PrerequisiteError`、`shutil.which`、`base.parent.mkdir`等。 返回路径：L37的`receipt`；L39的`{ "status": "unavailable", "git_available": False, "source_digest": identity, "note": "未安装…`；L85的`receipt`。
- `refresh_candidate`（L99–L144）：接收`destination`、`receipt`、`pending_steps`、`generated_files`、`generation_status`。 源码说明：Bind controller-approved source edits to a new unaccepted source snapshot.。 控制顺序：L104按`receipt.get("execution") != "source-candidate"`分支；L105抛异常，停止当前正常路径；L107遍历`( ("pending_steps", pending_steps), ("generated_files", generated…`；L112按`value is not None`分支；L124按`receipt["verification_status"] not in {"unverified", "failed"}`分支；L125抛异常，停止当前正常路径；L139按`not receipt.get("preserve_runtime_files")`分支。 调用`Path`、`receipt.get`、`PrerequisiteError`、`dict`、`receipt.update`、`list`、`dict.fromkeys`、`continuation_step`、`receipt.setdefault`等。 返回路径：L144的`receipt`。
- `write_status`（L147–L161）：接收`destination`、`status`。 调用`write_json`、`atomic_text`、`"".join`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `retain_failed_candidate`（L164–L199）：接收`template`、`plan`、`destination`、`sources`、`error_type`。 源码说明：Keep the runtime workspace byte-for-byte so recovery evidence stays valid.。 控制顺序：L168按`not listing`分支；L169抛异常，停止当前正常路径；L172按`recovery and recovery.get("files") != listing`分支；L173抛异常，停止当前正常路径；L176遍历`sources`；L177按`digest(manifest(source["path"])) != source["source_digest"]`分支；L178抛异常，停止当前正常路径。 调用`Path`、`manifest`、`PrerequisiteError`、`checkpoint.is_file`、`json.loads`、`checkpoint.read_text`、`recovery.get`、`bool`、`digest`等。 返回路径：L199的`refresh_candidate(destination, receipt)`。
- `generate_candidate`（L202–L230）：接收`settings`、`template`、`plan`、`destination`、`reason`。 控制顺序：L209按`destination.exists()`分支；L210抛异常，停止当前正常路径；L213按`template == "fastapiadmin"`分支。 调用`Path`、`destination.exists`、`PrerequisiteError`、`prepare_sources`、`copy_source`、`write_json`、`plan.model_dump`、`write_coding_standard`、`generate_offline`等。 返回路径：L230的`refresh_candidate(destination, receipt)`。
- `verify_candidate`（L233–L270）：接收`destination`、`receipt`。 控制顺序：L236按`receipt.get("execution") != "source-candidate" or receipt.get("generation_status") no…`分支；L240抛异常，停止当前正常路径；L241按`not current or current != receipt.get("files")`分支；L242抛异常，停止当前正常路径；L243按`receipt.get("runtime_verified") is not False or receipt.get("verification_status") no…`分支；L247抛异常，停止当前正常路径。 调用`Path`、`manifest`、`receipt.get`、`PrerequisiteError`、`result.update`、`digest`、`write_json`。 返回路径：L270的`result`。
- `package_candidate`（L273–L305）：接收`destination`、`report`。 控制顺序：L279按`report != verified`分支；L280抛异常，停止当前正常路径；L283按`receipt.get("preserve_runtime_files")`分支；L286遍历`files(destination)`；L295按`manifest(destination) != receipt["files"]`分支；L296抛异常，停止当前正常路径。 调用`Path`、`json.loads`、`(destination.parent / "native-generation.json").read_text`、`verify_candidate`、`PrerequisiteError`、`manifest`、`receipt.get`、`tempfile.TemporaryDirectory`、`files`等。 返回路径：L305的`result`。

</details>

**创建路径：** `workbench/delivery/source_candidate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L305。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12878`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/delivery/source_candidate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d2e61610236ed2314019148d79a54261a9164fc39c41112ebf54867bd868f90d"} -->
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
````
