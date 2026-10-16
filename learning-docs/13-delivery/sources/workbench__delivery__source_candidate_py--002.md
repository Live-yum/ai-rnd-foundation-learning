# workbench/delivery/source_candidate.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__delivery__source_candidate_py--001.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.core.contracts`、`workbench.filesystem`、`workbench.generation.python_basic`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `generate_candidate`（L862–L931）：接收`settings`、`template`、`plan`、`destination`、`reason`。 控制顺序：L870按`recovered is not None`分支；L872按`destination.exists() or inside(destination.parent, "native-generation.json").exists()`分支；L873抛异常，停止当前正常路径；L882按`template == "fastapiadmin"`分支；L913按`plan.custom_rules`分支；L928按`inside(destination.parent, ".source-candidate-transaction").exists()`分支；L929抛异常，停止当前正常路径。 调用`Path`、`recover_candidate`、`destination.exists`、`inside(destination.parent, "native-generation.json").exists`、`inside`、`PrerequisiteError`、`prepare_sources`、`destination.parent.mkdir`、`tempfile.TemporaryDirectory`等。 返回路径：L871的`recovered`；L931的`recover_candidate(template, plan, destination)`。
- `verify_candidate`（L934–L998）：接收`destination`、`receipt`、`persist`。 控制顺序：L937按`receipt.get("execution") != "source-candidate" or receipt.get("generation_status") no…`分支；L941抛异常，停止当前正常路径；L942按`not current or current != receipt.get("files")`分支；L943抛异常，停止当前正常路径；L944按`receipt.get("runtime_verified") is not False or receipt.get("verification_status") no…`分支；L948抛异常，停止当前正常路径；L951按`not isinstance(claim, dict) or claim.get("status") not in { "committed", "unavailable…`分支；L956抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`manifest`、`receipt.get`、`PrerequisiteError`、`check_status_binding`、`isinstance`、`claim.get`、`inside`、`digest`等。 返回路径：L998的`result`。
- `package_candidate`（L1001–L1033）：接收`destination`、`report`。 控制顺序：L1007按`report != verified`分支；L1008抛异常，停止当前正常路径；L1011按`receipt.get("preserve_runtime_files")`分支；L1014遍历`files(destination)`；L1023按`manifest(destination) != receipt["files"]`分支；L1024抛异常，停止当前正常路径。 调用`Path`、`json.loads`、`(destination.parent / "native-generation.json").read_text`、`verify_candidate`、`PrerequisiteError`、`manifest`、`receipt.get`、`tempfile.TemporaryDirectory`、`files`等。 返回路径：L1033的`result`。

</details>

**创建路径：** `workbench/delivery/source_candidate.py`；**本文件共有 2 段**。本段覆盖源文件 L862–L1033。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7487`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/delivery/source_candidate.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "a9fd84a062ff095cf320e841262f55d80a8dc33341423d843d3e309406f1808d"} -->
````python
# workbench/delivery/source_candidate.py
def generate_candidate(settings, template, plan, destination, reason):
    from workbench.generation.native.offline import generate_offline
    from workbench.generation.native.service import prepare_sources
    from workbench.infrastructure.native.environment import copy_source
    from workbench.templates.standards import write_coding_standard

    destination = Path(destination)
    recovered = recover_candidate(template, plan, destination)
    if recovered is not None:
        return recovered
    if destination.exists() or inside(destination.parent, "native-generation.json").exists():
        raise PrerequisiteError("已有源码不能被离线生成覆盖；请保留当前运行并创建新的运行")
    sources = prepare_sources(settings, template)
    slots = {item["slot"]: Path(item["path"]) for item in sources}
    destination.parent.mkdir(parents=True, exist_ok=True)
    transaction = inside(destination.parent, ".source-candidate-transaction")
    with tempfile.TemporaryDirectory(prefix="source-initial-", dir=destination.parent) as temporary:
        root = Path(temporary) / "transaction"
        stage = root / "candidate"
        product = stage / destination.name
        if template == "fastapiadmin":
            copy_source(slots["fastapiadmin"], product)
        else:
            copy_source(slots["backend"], product / "backend")
            copy_source(slots["frontend"], product / "frontend-product")
        write_json(product / "approved-spec.json", plan.model_dump())
        write_coding_standard(product, template)
        generated = generate_offline(template, plan, product, sources)
        receipt = {
            "template": template,
            "execution": "source-candidate",
            "spec_digest": digest(plan.model_dump()),
            "sources": [{k: v for k, v in item.items() if k != "path"} for item in sources],
            "verification_status": "unverified",
            "runtime_unavailable_reason": reason,
            **generated,
        }
        receipt["pending_steps"] = list(
            dict.fromkeys(
                [
                    *receipt.get("pending_steps", []),
                    *[
                        "Implement/review and runtime-verify approved custom rule "
                        + rule.entity
                        + ": "
                        + rule.description
                        for rule in plan.custom_rules
                    ],
                ]
            )
        )
        if plan.custom_rules:
            receipt["generation_status"] = "partial"
        receipt = refresh_candidate(product, receipt)
        verify_candidate(product, receipt)
        write_json(
            root / "transaction.json",
            {
                "version": 1,
                "template": template,
                "spec_digest": digest(plan.model_dump()),
                "product": destination.name,
                "receipt": receipt,
                "tree": _transaction_tree(stage),
            },
        )
        if inside(destination.parent, ".source-candidate-transaction").exists():
            raise PrerequisiteError("已有源码事务，拒绝覆盖")
        _publish_new(root, transaction)
    return recover_candidate(template, plan, destination)


def verify_candidate(destination, receipt, *, persist=True):
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
    if persist:
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
