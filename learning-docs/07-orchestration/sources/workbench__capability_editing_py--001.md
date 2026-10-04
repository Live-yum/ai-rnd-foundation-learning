# workbench/capability_editing.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.domain`、`workbench.feature_planning`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `task_path_errors`（L13–L31）：接收`task`、`selection`。 控制顺序：L21遍历`task.files`；L23按`name.startswith(("workbench/", "tools/", "scripts/")) or Path(name).name in { "approv…`分支。 调用`PlannedModule`、`task.model_dump`、`module_path_errors`、`source_path`、`name.startswith`、`Path`、`errors.append`。 返回路径：L31的`errors`。
- `copy_source`（L34–L40）：接收`source`、`destination`。 控制顺序：L37遍历`files(source)`。 调用`Path`、`destination.mkdir`、`files`、`inside`、`target.parent.mkdir`、`shutil.copyfile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `apply_candidate`（L43–L140）：接收`product`、`edits`、`task`、`selection`、`destination`、`settings`。 控制顺序：L46按`errors`分支；L47抛异常，停止当前正常路径；L49按`len({name.casefold() for name in names}) != len(names) or set(names) != set(task.file…`分支；L50抛异常，停止当前正常路径；L53按`sum(len(edit.content.encode("utf-8")) for edit in edits.files) > 1_000_000`分支；L54抛异常，停止当前正常路径；L56遍历`edits.files`；L58按`folded.get(edit.path.casefold(), edit.path) != edit.path`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`task_path_errors`、`ValueError`、`"；".join`、`len`、`name.casefold`、`set`、`manifest`、`sum`等。 返回路径：L72的`saved`；L140的`receipt`。

</details>

**创建路径：** `workbench/capability_editing.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L140。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6318`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_editing.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9f711be859d589e12f82265ac2bdf2d7b7fbd73aef923ec686dec496058485da"} -->
````python
# workbench/capability_editing.py
"""Transactional, reviewed business-file edits. Never execute product code on the host."""

import shutil
import tempfile
from pathlib import Path

from workbench.capability_contracts import source_path
from workbench.domain import digest
from workbench.feature_planning import PlannedModule, module_path_errors
from workbench.filesystem import atomic_text, files, inside, manifest, sha, write_json


def task_path_errors(task, selection):
    module = PlannedModule(
        **task.model_dump(),
        adapter=selection["template"],
        extension="approved-source-module",
        interfaces=[task.contract],
    )
    errors = module_path_errors(module)
    for name in task.files:
        source_path(name)
        if name.startswith(("workbench/", "tools/", "scripts/")) or Path(name).name in {
            "approved-spec.json",
            "manifest.json",
            "start.py",
            "verify.py",
            "conftest.py",
        }:
            errors.append("平台、启动、验收及批准文件不能由业务编码器修改：" + name)
    return errors


def copy_source(source, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name, path in files(source):
        target = inside(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def apply_candidate(product, edits, task, selection, destination, settings=None):
    product, destination = Path(product), Path(destination)
    errors = task_path_errors(task, selection)
    if errors:
        raise ValueError("；".join(errors))
    names = [edit.path for edit in edits.files]
    if len({name.casefold() for name in names}) != len(names) or set(names) != set(task.files):
        raise ValueError("候选必须且只能修改当前已批准节点的全部文件，每个文件恰好一次")
    original = manifest(product)
    folded = {name.casefold(): name for name in original}
    if sum(len(edit.content.encode("utf-8")) for edit in edits.files) > 1_000_000:
        raise ValueError("单个代码候选超过1MB预算")
    before = {}
    for edit in edits.files:
        path = inside(product, edit.path)
        if folded.get(edit.path.casefold(), edit.path) != edit.path:
            raise ValueError("候选与既有文件大小写冲突")
        expected = sha(path) if path.is_file() else None
        if edit.before_sha256 != expected:
            raise ValueError("候选前像已过期，未修改产品")
        before[edit.path] = path.read_text(encoding="utf-8") if expected else ""
    identity = digest({"source": original, "task": task.model_dump(), "edits": edits.model_dump()})
    receipt_path = destination.parent / (destination.name + "-edit.json")
    if destination.exists():
        import json

        saved = json.loads(receipt_path.read_text(encoding="utf-8"))
        if saved.get("identity") != identity or saved.get("files") != manifest(destination):
            raise ValueError("持久化候选与本轮源码或修改身份不一致")
        return saved
    destination.parent.mkdir(parents=True, exist_ok=True)
    engine = "bounded-source-files"
    with tempfile.TemporaryDirectory(prefix="module-edit-", dir=destination.parent) as temporary:
        root = Path(temporary)
        candidate = root / "candidate"
        copy_source(product, candidate)
        if settings is not None and settings.coding_engine == "aider":
            from workbench.aider_tool import command, git

            work, home = root / "work", root / "home"
            work.mkdir()
            home.mkdir()
            blocks = []
            for edit in edits.files:
                old = before[edit.path]
                # Whole-file, preimage-bound edits are converted by trusted code,
                # not by a model-authored command or configuration file.
                if any(
                    marker in old + edit.content for marker in ("<<<<<<< SEARCH", ">>>>>>> REPLACE")
                ):
                    raise ValueError("源码包含补丁控制标记，不能通过Aider应用")
                if old and not old.endswith("\n"):
                    raise ValueError("Aider模块前像必须以换行结束")
                if not edit.content.endswith("\n"):
                    raise ValueError("Aider模块候选必须以换行结束")
                if edit.before_sha256 is not None:
                    atomic_text(inside(work, edit.path), old)
                blocks.append(
                    edit.path
                    + "\n<<<<<<< SEARCH\n"
                    + old
                    + "=======\n"
                    + edit.content
                    + ">>>>>>> REPLACE\n"
                )
            git(work, home, "init", "-q")
            git(work, home, "add", ".")
            git(work, home, "commit", "--allow-empty", "-qm", "Reviewed module before image")
            atomic_text(home / "edits.txt", "\n".join(blocks))
            command(settings, work, home, "--apply", str(home / "edits.txt"), *names)
            if set(manifest(work)) != set(names) or any(
                inside(work, edit.path).read_text(encoding="utf-8") != edit.content
                for edit in edits.files
            ):
                raise ValueError("Aider实际输出与已验证候选不一致")
            engine = "aider-cli-apply"
        for edit in edits.files:
            atomic_text(inside(candidate, edit.path), edit.content)
        updated = manifest(candidate)
        if {
            name for name in set(updated) | set(original) if updated.get(name) != original.get(name)
        } - set(names):
            raise ValueError("候选修改超出节点文件清单")
        if manifest(product) != original:
            raise ValueError("基线在编辑期间发生变化")
        receipt = {
            "identity": identity,
            "before": original,
            "files": updated,
            "engine": engine,
            "task": task.id,
            "model_called_by_editor": False,
            "host_execution": False,
        }
        # The receipt is committed first; an interrupted rename can safely replay.
        write_json(receipt_path, receipt)
        candidate.replace(destination)
    return receipt
````
