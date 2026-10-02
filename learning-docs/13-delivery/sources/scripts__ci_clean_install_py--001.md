# scripts/ci_clean_install.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立依赖环境与成品干净解压验收。** 显式需求/计划夹具只代替模型响应，Runtime与产品进程实际运行。批准三个关卡后必须READY，且isolated_dependencies、cleanroom真实通过；临时目录退出时清理。

**对应关系：** 双系统clean-install工作流 → Runtime → 生成/验证/解压 → clean-install.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.runtime`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `AcceptanceFixture`（L13–L38）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AcceptanceFixture.complete`（L14–L38）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L15按`schema is Requirement`分支；L23按`schema is Plan`分支；L38抛异常，停止当前正常路径。 调用`Requirement`、`Plan.model_validate`、`AssertionError`。 返回路径：L16的`Requirement( summary="个人便签", users=["个人"], data_scope="per_user", features=["CRUD"], accep…`；L24的`Plan.model_validate( { "title": "便签", "data_scope": "per_user", "entities": [ { "name": "n…`。
- `main`（L41–L81）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L54遍历`["requirements", "design", "delivery"]`；L57断言`run["pending"] and run["pending"]["stage"] == stage`；L69断言`result["status"] == "READY"`；L70断言`result["result"]["isolated_dependencies"] is True`；L71断言`result["result"]["cleanroom"]["passed"] is True`。 调用`tempfile.TemporaryDirectory`、`Settings`、`Path`、`Store`、`store.migrate`、`store.create_project`、`store.create_run`、`Runtime`、`AcceptanceFixture`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_clean_install.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L85。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3244`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_clean_install.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "540003296f3a79daa777f80bcceba607a0e5cfd271cb93fed6eecac3a2d5dfaa"} -->
````python
# scripts/ci_clean_install.py
"""CI acceptance with genuine independent uv environments. Model input is an explicit fixture."""

import json
import tempfile
from pathlib import Path

from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import ROOT, Settings
from workbench.store import Store


class AcceptanceFixture:
    def complete(self, run_id, key, instruction, payload, schema):
        if schema is Requirement:
            return Requirement(
                summary="个人便签",
                users=["个人"],
                data_scope="per_user",
                features=["CRUD"],
                acceptance=["重启和数据隔离"],
            )
        if schema is Plan:
            return Plan.model_validate(
                {
                    "title": "便签",
                    "data_scope": "per_user",
                    "entities": [
                        {
                            "name": "note",
                            "description": "便签",
                            "fields": [{"name": "title", "kind": "text"}],
                        }
                    ],
                    "acceptance": ["CRUD、重启和数据隔离"],
                }
            )
        raise AssertionError("No coding call permitted for CRUD")


def main():
    with tempfile.TemporaryDirectory(prefix="rnd-acceptance-") as directory:
        settings = Settings(
            data_dir=Path(directory), install_products=True, tool_timeout=600, _env_file=None
        )
        store = Store(settings)
        try:
            store.migrate()
            project = store.create_project("acceptance", "project")
            run_id = store.create_run(
                project["id"], {"template": "python-basic", "requirement": "便签 CRUD"}, "run"
            )["run_id"]
            with Runtime(settings, store, AcceptanceFixture()) as worker:
                for stage in ["requirements", "design", "delivery"]:
                    worker.tick()
                    run = store.get_run(run_id)
                    assert run["pending"] and run["pending"]["stage"] == stage, run
                    store.submit(
                        run_id,
                        {
                            "gate_id": run["pending"]["gate_id"],
                            "action": "approve",
                            "approved": True,
                        },
                        stage,
                    )
                worker.tick()
            result = store.get_run(run_id)
            assert result["status"] == "READY", result
            assert result["result"]["isolated_dependencies"] is True
            assert result["result"]["cleanroom"]["passed"] is True
            destination = ROOT / "reports"
            destination.mkdir(exist_ok=True)
            (destination / "clean-install.json").write_text(
                json.dumps(result["result"], ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(
                "PASS: genuine product venv + separate clean-room venv; HTTP CRUD/isolation/restart; fixture model only"
            )
        finally:
            store.engine.dispose()


if __name__ == "__main__":
    main()
````
