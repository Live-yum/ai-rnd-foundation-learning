# scripts/ci_aider_workflow.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：基础产品实际Aider编排验收。** 固定响应提出批准业务规则，真实LangGraph调用真实Aider，然后运行独立产品验收。记录工具调用和结果，不能把夹具响应当作付费模型质量证据。

**对应关系：** toolchain验收 → Runtime/ModelGateway替身 → 本机Aider → 基础产品验证。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.aider_tool`、`workbench.domain`、`workbench.runtime`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ApprovedFixture`（L14–L69）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ApprovedFixture.__init__`（L15–L16）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ApprovedFixture.complete`（L18–L69）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L20按`schema is Requirement`分支；L28按`schema is Plan`分支；L29断言`payload["code_context"]["contexts"][0]["repo_map"]["provider"] == "aider-cli-repo-map…`；L33断言`payload["code_context"]["contexts"][0]["retrieval"]["mode"].startswith( "ast+continue…`；L61按`schema is EditBlocks`分支；L69抛异常，停止当前正常路径。 调用`self.calls.append`、`Requirement`、`payload["code_context"]["contexts"][0]["retrieval"]["mode"].start…`、`Plan.model_validate`、`EditBlocks`、`AssertionError`。 返回路径：L21的`Requirement( summary="个人任务", users=["个人"], data_scope="per_user", features=["CRUD", "prior…`；L36的`Plan.model_validate( { "title": "任务", "data_scope": "per_user", "acceptance": ["CRUD与非负校验"…`；L62的`EditBlocks( before_sha256=payload["context"]["files"]["custom_rules.py"]["sha256"], explan…`。
- `verify_workflow`（L72–L142）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L94遍历`("requirements", "design", "delivery")`；L97断言`run["pending"] and run["pending"]["stage"] == stage`；L109断言`result["status"] == "READY"`；L110断言`result["result"]["isolated_dependencies"] is True`；L111断言`result["result"]["cleanroom"]["passed"] is True`；L112断言`result["result"]["cleanroom"]["restart"] is True`；L113断言`fixture.calls == ["requirement:1", "plan:1", "coding:aider:0"]`；L117断言`edit["provider"] == "aider-cli-apply" and edit["before_commit"] != edit["after_commit…`。后续分支沿下方源码相同行号继续阅读。 调用`tempfile.TemporaryDirectory`、`Settings`、`Path`、`Store`、`ApprovedFixture`、`store.migrate`、`store.create_project`、`store.create_run`、`Runtime`等。 返回路径：L121的`{ "ready": True, "isolated_dependencies": True, "cleanroom_passed": True, "restart_passed"…`。

</details>

**创建路径：** `scripts/ci_aider_workflow.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L146。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5850`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_aider_workflow.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "da04a678c3b9af9ba6ea62387dd4db5a568f70e2a627d188ecc9271fe1d00c12"} -->
````python
# scripts/ci_aider_workflow.py
"""Actual LangGraph -> Aider CLI -> independent product verification, fixture LLM only."""

import json
import tempfile
from pathlib import Path

from workbench.aider_tool import EditBlocks
from workbench.domain import Plan, Requirement
from workbench.runtime import Runtime
from workbench.settings import Settings
from workbench.store import Store


class ApprovedFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        self.calls.append(key)
        if schema is Requirement:
            return Requirement(
                summary="个人任务",
                users=["个人"],
                data_scope="per_user",
                features=["CRUD", "priority不能为负"],
                acceptance=["规则和重启"],
            )
        if schema is Plan:
            assert (
                payload["code_context"]["contexts"][0]["repo_map"]["provider"]
                == "aider-cli-repo-map"
            )
            assert payload["code_context"]["contexts"][0]["retrieval"]["mode"].startswith(
                "ast+continue-fts5"
            )
            return Plan.model_validate(
                {
                    "title": "任务",
                    "data_scope": "per_user",
                    "acceptance": ["CRUD与非负校验"],
                    "entities": [
                        {
                            "name": "task",
                            "description": "任务",
                            "fields": [
                                {"name": "title", "kind": "text"},
                                {"name": "priority", "kind": "integer"},
                            ],
                        }
                    ],
                    "custom_rules": [
                        {
                            "description": "priority不能为负",
                            "entity": "task",
                            "accept_examples": [{"title": "ok", "priority": 1}],
                            "reject_examples": [{"title": "bad", "priority": -1}],
                        }
                    ],
                }
            )
        if schema is EditBlocks:
            return EditBlocks(
                before_sha256=payload["context"]["files"]["custom_rules.py"]["sha256"],
                explanation="Explicit fixture, no model API called",
                blocks="custom_rules.py\n<<<<<<< SEARCH\n    return None\n=======\n"
                "    if entity == 'task' and data.get('priority', 0) < 0:\n"
                "        raise ValueError('nonnegative')\n    return None\n>>>>>>> REPLACE\n",
            )
        raise AssertionError(schema)


def verify_workflow():
    with tempfile.TemporaryDirectory(prefix="rnd-aider-flow-") as directory:
        settings = Settings(
            data_dir=Path(directory),
            install_products=True,
            tool_timeout=600,
            coding_engine="aider",
            repo_map_provider="aider",
            retrieval_engine="continue",
            _env_file=None,
        )
        store = Store(settings)
        fixture = ApprovedFixture()
        try:
            store.migrate()
            project = store.create_project("aider-acceptance", "project")
            run_id = store.create_run(
                project["id"],
                {"template": "python-basic", "requirement": "个人任务与非负优先级"},
                "run",
            )["run_id"]
            with Runtime(settings, store, fixture) as worker:
                for stage in ("requirements", "design", "delivery"):
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
            assert result["result"]["cleanroom"]["restart"] is True
            assert fixture.calls == ["requirement:1", "plan:1", "coding:aider:0"], fixture.calls
            edit = json.loads(
                (Path(directory) / "runs" / run_id / "coding-0.json").read_text(encoding="utf-8")
            )
            assert (
                edit["provider"] == "aider-cli-apply"
                and edit["before_commit"] != edit["after_commit"]
            )
            return {
                "ready": True,
                "isolated_dependencies": True,
                "cleanroom_passed": True,
                "restart_passed": True,
                "actual_aider_edit": True,
                "actual_continue_index": True,
                "actual_langgraph": True,
                "model_transport": "explicit-fixture",
                "model_api_calls": 0,
            }
        except Exception:
            directory = Path(directory)
            reports = Path("reports")
            reports.mkdir(exist_ok=True)
            for failure in directory.glob("runs/*/tool-failure.json"):
                text = failure.read_text(encoding="utf-8")
                (reports / "aider-workflow-failure.json").write_text(text, encoding="utf-8")
                print(text, flush=True)
            raise
        finally:
            store.engine.dispose()


if __name__ == "__main__":
    print(json.dumps(verify_workflow(), ensure_ascii=False, indent=2))
````
