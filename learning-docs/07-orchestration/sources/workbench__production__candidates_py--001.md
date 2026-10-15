# workbench/production/candidates.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance.capability_verification`、`workbench.core.contracts`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ProductLedger`（L17–L126）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ProductLedger.__init__`（L18–L24）：接收`directory`、`plan`。 调用`Path`、`self.directory.mkdir`、`digest`、`plan.model_dump`、`FileLock`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ProductLedger._load`（L26–L32）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L28按`value["plan_digest"] != self.identity`分支；L29抛异常，停止当前正常路径；L30按`manifest(value["product"]) != value["files"]`分支；L31抛异常，停止当前正常路径。 调用`json.loads`、`self.pointer.read_text`、`ValueError`、`manifest`。 返回路径：L32的`value`。
- `ProductLedger.baseline`（L34–L50）：接收`product`。 控制顺序：L36按`self.pointer.exists()`分支。 调用`self.pointer.exists`、`self._load`、`str`、`Path(product).resolve`、`Path`、`manifest`、`write_json`。 返回路径：L37的`self._load()`；L50的`value`。
- `ProductLedger.promote`（L52–L99）：接收`product`、`task`、`proof`、`expected_before`。 控制顺序：L65按`task.id in current["completed_tasks"]`分支；L66按`current["task_id"] == task.id and current["files"] == inventory and current["evidence…`分支；L72抛异常，停止当前正常路径；L73按`current["files"] != expected_before or not set(task.depends_on) <= set( current["comp…`分支；L76抛异常，停止当前正常路径；L80按`task.id not in approved or approved[task.id].model_dump() != task.model_dump()`分支；L81抛异常，停止当前正常路径。 调用`manifest`、`require_evidence`、`digest`、`self.plan.selection.model_dump`、`self._load`、`ValueError`、`set`、`approved[task.id].model_dump`、`task.model_dump`等。 返回路径：L71的`current`；L99的`value`。
- `ProductLedger.verified`（L101–L126）：接收`product`、`proof`。 控制顺序：L113按`set(current["completed_tasks"]) != {t.id for t in self.plan.tasks} or current[ "files…`分支；L116抛异常，停止当前正常路径。 调用`require_evidence`、`digest`、`manifest`、`self.plan.selection.model_dump`、`self._load`、`set`、`ValueError`、`write_json`。 返回路径：L126的`value`。

</details>

**创建路径：** `workbench/production/candidates.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L126。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/production/candidates.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e54ae3b70f657d882ae38bdf446a72707bad2be7d176ffcdcfb9ddbc4e38497d"} -->
````python
# workbench/production/candidates.py
"""Immutable version manifests and atomic promotion, bound to independent proof.

This journals file candidates, not arbitrary shell side effects. An interrupted
external execution must be cleaned up and verified again by its owner.
"""

import json
from pathlib import Path

from filelock import FileLock

from workbench.acceptance.capability_verification import require_evidence
from workbench.core.contracts import digest
from workbench.filesystem import manifest, write_json


class ProductLedger:
    def __init__(self, directory, plan):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.plan = plan
        self.identity = digest(plan.model_dump())
        self.pointer = self.directory / "current.json"
        self.lock = FileLock(str(self.directory / "promotion.lock"), timeout=0)

    def _load(self):
        value = json.loads(self.pointer.read_text())
        if value["plan_digest"] != self.identity:
            raise ValueError("product ledger belongs to a different plan")
        if manifest(value["product"]) != value["files"]:
            raise ValueError("frozen product version changed")
        return value

    def baseline(self, product):
        with self.lock:
            if self.pointer.exists():
                return self._load()
            value = {
                "version": 0,
                "kind": "baseline",
                "plan_digest": self.identity,
                "source_digest": self.plan.source_digest,
                "product": str(Path(product).resolve()),
                "files": manifest(product),
                "completed_tasks": [],
                "implementation_verified": False,
            }
            write_json(self.directory / "v0.json", value)
            write_json(self.pointer, value)
            return value

    def promote(self, product, task, proof, expected_before):
        scenarios = [s for s in self.plan.scenarios if s.id in task.scenarios]
        inventory = manifest(product)
        require_evidence(
            proof,
            source_digest=digest(inventory),
            plan_digest=self.identity,
            scenarios=scenarios,
            selection=self.plan.selection.model_dump(),
            database_tables=self.plan.runtime.database_tables,
        )
        with self.lock:
            current = self._load()
            if task.id in current["completed_tasks"]:
                if (
                    current["task_id"] == task.id
                    and current["files"] == inventory
                    and current["evidence_digest"] == digest(proof)
                ):
                    return current
                raise ValueError("duplicate task has different candidate or evidence")
            if current["files"] != expected_before or not set(task.depends_on) <= set(
                current["completed_tasks"]
            ):
                raise ValueError(
                    "promotion requires the exact verified predecessor and dependencies"
                )
            approved = {t.id: t for t in self.plan.tasks}
            if task.id not in approved or approved[task.id].model_dump() != task.model_dump():
                raise ValueError("task is not part of the approved plan")
            value = {
                "version": current["version"] + 1,
                "kind": "candidate",
                "plan_digest": self.identity,
                "source_digest": self.plan.source_digest,
                "product": str(Path(product).resolve()),
                "files": inventory,
                "before_digest": digest(expected_before),
                "task_id": task.id,
                "completed_tasks": [*current["completed_tasks"], task.id],
                "evidence": proof,
                "evidence_digest": digest(proof),
                "implementation_verified": False,
            }
            # Version receipt first; the atomic pointer is the single publication point.
            write_json(self.directory / f"v{value['version']}.json", value)
            write_json(self.pointer, value)
            return value

    def verified(self, product, proof):
        require_evidence(
            proof,
            source_digest=digest(manifest(product)),
            plan_digest=self.identity,
            scenarios=self.plan.scenarios,
            selection=self.plan.selection.model_dump(),
            database_tables=self.plan.runtime.database_tables,
            aggregate=True,
        )
        with self.lock:
            current = self._load()
            if set(current["completed_tasks"]) != {t.id for t in self.plan.tasks} or current[
                "files"
            ] != manifest(product):
                raise ValueError("aggregate proof must cover every promoted module")
            value = {
                **current,
                "kind": "verified-product",
                "implementation_verified": True,
                "aggregate_evidence": proof,
                "aggregate_evidence_digest": digest(proof),
            }
            write_json(self.directory / "verified.json", value)
            write_json(self.pointer, value)
            return value
````
