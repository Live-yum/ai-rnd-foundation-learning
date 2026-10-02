# scripts/ci_daytona_local.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：真实本机Daytona中的资讯端到端验收。** 先用明确模型夹具完成智能资讯工作流，再创建实际本机沙箱并执行离线产品检查，确认删除和独立ZIP复验；SDK模拟测试不是这份报告。

**对应关系：** daytona-local工作流 → Runtime/本机工具/Daytona → daytona-local.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.news_fixture`、`workbench.filesystem`、`workbench.runtime`、`workbench.sandbox`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L15–L93）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L27按`settings.sandbox_provider != "daytona"`分支；L28抛异常，停止当前正常路径；L49断言`worker.tick()`；L51断言`run["status"] == "WAITING_CLARIFICATION"`；L52断言`run["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS`；L54断言`worker.tick()`；L56断言`run["status"] == "READY"`；L58断言`snapshot.values["sandbox"]["enabled"] is True`。后续分支沿下方源码相同行号继续阅读。 调用`tempfile.TemporaryDirectory`、`Settings`、`Path`、`validate_configuration`、`ValueError`、`Store`、`NewsFixture`、`store.migrate`、`store.create_project`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_daytona_local.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L97。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4373`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_daytona_local.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8607eff3445c34286886e8f09fc47a84a93b3fdefc4db6d194f4be60bb82a696"} -->
````python
# scripts/ci_daytona_local.py
"""Real smart-news workflow through all local tools and Daytona, fixture LLM only."""

import json
import tempfile
from pathlib import Path

from scripts.news_fixture import LIMITATIONS, ORIGINAL_REQUEST, NewsFixture
from workbench.filesystem import write_json
from workbench.runtime import Runtime
from workbench.sandbox import validate_configuration
from workbench.settings import ROOT, Settings
from workbench.store import Store


def main():
    report = {"passed": False, "model_transport": "explicit-fixture", "model_api_calls": 0}
    with tempfile.TemporaryDirectory(prefix="rnd-daytona-workflow-") as temp:
        settings = Settings(
            data_dir=Path(temp),
            install_products=True,
            tool_timeout=600,
            repo_map_provider="aider",
            retrieval_engine="continue",
            _env_file=ROOT / ".data/daytona-local/workbench.env",
        )
        validate_configuration(settings, "python-basic", {"database": "sqlite"})
        if settings.sandbox_provider != "daytona":
            raise ValueError("Acceptance requires explicit local Daytona configuration")
        store = Store(settings)
        fixture = NewsFixture()
        run_id = None
        try:
            store.migrate()
            project = store.create_project("泰拉瑞亚游戏小助手", "project")
            run_id = store.create_run(
                project["id"],
                {
                    "template": "python-basic",
                    "selection": {
                        "template": "python-basic",
                        "frontend": "simple-admin",
                        "database": "sqlite",
                    },
                    "requirement": ORIGINAL_REQUEST,
                },
                "run",
            )["run_id"]
            with Runtime(settings, store, fixture) as worker:
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "WAITING_CLARIFICATION", run
                assert run["pending"]["data"]["requirement"]["unsupported"] == LIMITATIONS
                store.set_automation(run_id, True, "authorize-once")
                assert worker.tick()
                run = store.get_run(run_id)
                assert run["status"] == "READY", run
                snapshot = worker.graph.get_state({"configurable": {"thread_id": run_id}})
                assert snapshot.values["sandbox"]["enabled"] is True
            assert run["auto_mode"] and not run["pending"] and not run["error"]
            result = run["result"]
            assert result["isolated_dependencies"] is True
            assert result["cleanroom"]["passed"] is True and result["cleanroom"]["restart"] is True
            assert (settings.data_dir / "runs" / run_id / "delivery.zip").is_file()
            assert fixture.calls == ["requirement:1", "recommend:2", "plan:2"], fixture.calls
            assert [row["content"] for row in store.messages(run_id)] == [ORIGINAL_REQUEST]
            report.update(
                passed=True,
                status="READY",
                initial_status="WAITING_CLARIFICATION",
                smart_authorizations=1,
                subsequent_manual_actions=0,
                explicit_facts_preserved=True,
                reported_boundary_list_regression=True,
                actual_continue_index=True,
                actual_aider_repo_map=True,
                isolated_dependencies=True,
                independent_zip=True,
                cleanroom=result["cleanroom"],
                model_fixture_calls=fixture.calls,
            )
        finally:
            if run_id:
                run = store.get_run(run_id)
                report["last_status"] = run["status"]
                report["error"] = settings.redact(run["error"] or "")
                root = settings.data_dir / "runs" / run_id
                for name in ("daytona-verification.json", "tool-failure.json"):
                    path = root / name
                    if path.is_file():
                        report[name] = json.loads(settings.redact(path.read_text(encoding="utf-8")))
            write_json(ROOT / "reports/daytona-local.json", report)
            store.engine.dispose()
    print(json.dumps({"passed": report["passed"], "status": report["last_status"]}))


if __name__ == "__main__":
    main()
````
