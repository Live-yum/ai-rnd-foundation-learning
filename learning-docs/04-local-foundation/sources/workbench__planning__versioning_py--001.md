# workbench/planning/versioning.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.planning.contracts`、`workbench.planning.feature_planner`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `compile_v2`（L7–L43）：接收`design`、`executor`、`max_steps`。 控制顺序：L8按`design.outline.version == 2`分支；L9遍历`design.outline.modules`；L11按`module.executor != expected or module.max_steps != ( max_steps if expected == "mini_s…`分支；L14抛异常，停止当前正常路径；L20遍历`data["outline"]["modules"]`；L32按`data["implementation"]`分支；L36遍历`data["implementation"]["tasks"]`；L39按`module is None or any(module[key] != value for key, value in old.items())`分支。后续分支沿下方源码相同行号继续阅读。 调用`ValueError`、`FeatureDesign.model_validate`、`design.model_dump`、`module.update`、`PlannedModuleV2.model_validate`、`modules.get`、`any`、`old.items`、`tasks.append`。 返回路径：L17的`FeatureDesign.model_validate(design.model_dump())`；L43的`FeatureDesign.model_validate(data)`。
- `version_for_run`（L46–L47）：接收`run`。 调用`run.get("options", {}).get`、`run.get`。 返回路径：L47的`run.get("options", {}).get("production_version", 1)`。

</details>

**创建路径：** `workbench/planning/versioning.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L47。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2203`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/planning/versioning.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cbe6fc20854f3c986788fccf969753ff416528a9539ccf90d12d2bf929e72c9a"} -->
````python
# workbench/planning/versioning.py
"""Explicit new-run compilation; persisted V1 gates are never migrated in place."""

from workbench.planning.contracts import CapabilityTaskV2
from workbench.planning.feature_planner import FeatureDesign, PlannedModuleV2


def compile_v2(design, *, executor="bounded_edit", max_steps=8):
    if design.outline.version == 2:
        for module in design.outline.modules:
            expected = executor if module.extension == "approved-source-module" else "bounded_edit"
            if module.executor != expected or module.max_steps != (
                max_steps if expected == "mini_swe" else 1
            ):
                raise ValueError(
                    "planner cannot expand the run's configured executor or step budget"
                )
        return FeatureDesign.model_validate(design.model_dump())
    data = design.model_dump()
    data["outline"]["version"] = 2
    for module in data["outline"]["modules"]:
        engine = executor if module["extension"] == "approved-source-module" else "bounded_edit"
        module.update(
            version=2,
            task_id=module["id"],
            executor=engine,
            requirement_ids=module["requirements"],
            allowed_paths=module["files"],
            acceptance_ids=module["scenarios"],
            max_steps=max_steps if engine == "mini_swe" else 1,
        )
        PlannedModuleV2.model_validate(module)
    if data["implementation"]:
        data["implementation"]["version"] = 2
        modules = {module["id"]: module for module in data["outline"]["modules"]}
        tasks = []
        for old in data["implementation"]["tasks"]:
            # Validate V1 equivalence BEFORE projecting a module into an execution task.
            module = modules.get(old["id"])
            if module is None or any(module[key] != value for key, value in old.items()):
                raise ValueError("planner module and execution task disagree")
            tasks.append({key: module[key] for key in CapabilityTaskV2.model_fields})
        data["implementation"]["tasks"] = tasks
    return FeatureDesign.model_validate(data)


def version_for_run(run):
    return run.get("options", {}).get("production_version", 1)
````
