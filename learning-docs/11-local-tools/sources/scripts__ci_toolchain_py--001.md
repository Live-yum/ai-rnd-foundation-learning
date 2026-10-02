# scripts/ci_toolchain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：实际解析、Continue、MCP和Aider串联验收。** 准备固定真实源码，建立符号/全文索引、启动只读MCP并执行真实Aider入口；每类工具的输出单独验证，再运行受控业务规则流程。

**对应关系：** toolchain工作流 → 本脚本 → 本机工具报告；模型输出为明确夹具。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.aider_tool`、`workbench.context_mcp`、`workbench.filesystem`、`workbench.knowledge`、`workbench.retrieval`、`workbench.settings`、`workbench.tools`、`workbench.vendor`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `mcp_roundtrip`（L20–L38）：接收`source`、`index`。 控制顺序：L34断言`names == {"search_code", "repository_map"}`；L36断言`not result.isError`；L37断言`".java" in str(result.content)`。 调用`StdioServerParameters`、`str`、`stdio_client`、`ClientSession`、`session.initialize`、`session.list_tools`、`session.call_tool`、`sorted`。 返回路径：L38的`{"protocol": "real-stdio", "tools": sorted(names), "query_passed": True}`。
- `main`（L41–L124）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L53断言`json.loads(ready["log"])["packaged_encodings_verified"] is True`；L75断言`java["matches"] and vue["matches"]`；L76断言`any(hit["path"].endswith(".vue") for hit in vue["matches"])`；L82断言`".java" in java_map["text"]`；L91断言`"Article" in mapped["text"]`；L104断言`"nonnegative" in rule.read_text(encoding="utf-8")`；L105断言`edited["before_commit"] != edited["after_commit"]`。 调用`run_command`、`executable`、`Settings`、`str`、`json.loads`、`print`、`verify_workflow`、`tempfile.TemporaryDirectory`、`Path`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_toolchain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L132。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5580`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_toolchain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e71deb3b0fb07c9666618188725b6a615fe4b3761f62f06073ef0aa601a51c03"} -->
````python
# scripts/ci_toolchain.py
"""Real Aider CLI + real MCP stdio + real bundled Java/Vue sources, no model key."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from workbench.aider_tool import EditBlocks, apply_blocks, executable, repo_map
from workbench.context_mcp import export_continue
from workbench.filesystem import sha, write_json
from workbench.knowledge import build_index
from workbench.retrieval import query
from workbench.settings import ROOT, Settings
from workbench.tools import ToolFailure, run_command
from workbench.vendor import prepare


async def mcp_roundtrip(source, index):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "workbench.cli", "tools", "context-server", str(source), str(index)],
        cwd=str(ROOT),
        env={**os.environ, "PYTHONUTF8": "1", "RETRIEVAL_ENGINE": "continue"},
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            names = {tool.name for tool in (await session.list_tools()).tools}
            assert names == {"search_code", "repository_map"}
            result = await session.call_tool("search_code", {"question": "RestController"})
            assert not result.isError
            assert ".java" in str(result.content)
            return {"protocol": "real-stdio", "tools": sorted(names), "query_passed": True}


def main():
    from scripts.ci_aider_workflow import verify_workflow

    ready = run_command(
        [
            executable(Settings(_env_file=None)),
            str(ROOT / "tools/aider/offline_runner.py"),
            "--check-local-deps",
        ],
        ROOT,
        60,
    )
    assert json.loads(ready["log"])["packaged_encodings_verified"] is True
    print("Run actual Aider LangGraph delivery", flush=True)
    workflow = verify_workflow()
    with tempfile.TemporaryDirectory(prefix="rnd-tools-ci-") as temporary:
        root = Path(temporary)
        settings = Settings(data_dir=root / "state", retrieval_engine="continue", _env_file=None)
        print("Index bundled Java/Vue source", flush=True)
        rows = prepare(settings, "yudao-vben")
        backend = Path(next(row["path"] for row in rows if row["slot"] == "backend"))
        frontend = Path(next(row["path"] for row in rows if row["slot"] == "frontend"))
        bindex, findex = root / "backend-index", root / "frontend-index"
        build_index(backend, bindex)
        build_index(frontend, findex)
        java = query(backend, bindex, "RestController", settings=settings)
        vue = query(
            frontend,
            findex,
            "useVbenForm",
            file_suffix=".vue",
            path_prefix="apps/web-antd/",
            settings=settings,
        )
        assert java["matches"] and vue["matches"]
        assert any(hit["path"].endswith(".vue") for hit in vue["matches"]), vue
        export_continue(root, backend, bindex)
        print("Run real MCP stdio roundtrip", flush=True)
        protocol = asyncio.run(mcp_roundtrip(backend, bindex))
        print("Run real Aider maps and bounded Git edit", flush=True)
        java_map = repo_map(backend, bindex, settings)
        assert ".java" in java_map["text"], java_map
        source = root / "aider-source"
        source.mkdir()
        (source / "sample.py").write_text(
            "class Article:\n    def get_title(self):\n        return 'hello'\n", encoding="utf-8"
        )
        amap = root / "aider-index"
        build_index(source, amap)
        mapped = repo_map(source, amap, settings)
        assert "Article" in mapped["text"], mapped
        product = root / "product"
        product.mkdir()
        rule = product / "custom_rules.py"
        rule.write_text("def validate(entity, data):\n    return None\n", encoding="utf-8")
        value = EditBlocks(
            before_sha256=sha(rule),
            explanation="explicit CI edit, not an LLM",
            blocks="custom_rules.py\n<<<<<<< SEARCH\n    return None\n=======\n"
            "    if data.get('priority', 0) < 0:\n        raise ValueError('nonnegative')\n"
            "    return None\n>>>>>>> REPLACE\n",
        )
        edited = apply_blocks(product, value, settings)
        assert "nonnegative" in rule.read_text(encoding="utf-8")
        assert edited["before_commit"] != edited["after_commit"]
        evidence = {
            "passed": True,
            "aider_langgraph_delivery": workflow,
            "native_java_hits": len(java["matches"]),
            "native_vben_hits": len(vue["matches"]),
            "continue_mcp": protocol,
            "continue_upstream_index": json.loads(
                (findex / "continue-index.json").read_text(encoding="utf-8")
            ),
            "aider_cli_map": True,
            "aider_native_java_map": True,
            "aider_cli_edit": True,
            "git_commits": True,
            "model_calls": 0,
            "daytona_self_hosted_service_tested": False,
            "daytona_note": "Local service acceptance is a separate workflow; this report does not claim it passed",
        }
        write_json(ROOT / "reports/toolchain.json", evidence)
        print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ToolFailure as exc:
        print(exc.log)  # Isolated CI tool processes receive no real model credentials.
        raise
````
