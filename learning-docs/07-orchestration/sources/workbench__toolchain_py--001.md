# workbench/toolchain.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把源码上下文接到实际主流程。** prepare_context不是只为展示准备的CLI：它为选定模板建立索引，按需调用本机embedding，然后检索并生成有预算的Repo Map。其他Typer函数提供同一能力的人工诊断入口。

**对应关系：** flow上下文节点 → prepare_context → knowledge/retrieval/aider_tool；context_server → MCP。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.knowledge`、`workbench.retrieval`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `prepare_context`（L16–L48）：接收`settings`、`template`、`requirement`、`destination`。先确定模板源码位置与摘要，再生成检索上下文；返回的内容在规划节点使用，不是只写报告后丢弃。 控制顺序：L17按`template == "python-basic"`分支；L26遍历`sources`；L29按`settings.repo_map_provider == "aider"`分支；L35按`settings.embedding_enabled`分支。 调用`str`、`prepare`、`" ".join`、`requirement.get`、`query_text.strip`、`Path`、`build_index`、`repo_map`、`compact_map`等。 返回路径：L48的`result`。
- `search_command`（L52–L69）：接收`source`、`index`、`question`、`file_suffix`、`path_prefix`。 源码说明：查询已建立的索引，只使用本机索引与本机向量服务，不默认计算向量。。 调用`typer.echo`、`json.dumps`、`query`、`Settings`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `embed_command`（L73–L77）：接收`source`、`index`。 源码说明：显式启用后建立本机向量索引，不继承聊天模型凭据。。 调用`typer.echo`、`json.dumps`、`add_embeddings`、`Settings`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `map_command`（L81–L91）：接收`source`、`index`。 源码说明：按配置生成本地符号地图或真实Aider Repo Map；不调用LLM。。 控制顺序：L85按`settings.repo_map_provider == "aider"`分支。 调用`Settings`、`build_index`、`repo_map`、`compact_map`、`typer.echo`、`json.dumps`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `continue_command`（L95–L99）：接收`workspace`、`source`、`index`。 源码说明：创建Continue的只读MCP配置；已有配置不覆盖。。 调用`typer.echo`、`json.dumps`、`export_continue`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `context_server`（L103–L107）：接收`source`、`index`。 源码说明：Continue通过stdio启动；stdout专用于MCP协议，不打印日志。。 调用`make_server(source, index, Settings()).run`、`make_server`、`Settings`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/toolchain.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L107。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3845`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/toolchain.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "49de446999cea14d8174ecbc4e4e4daef6d5be18c87354a7bfd09b88267d04cc"} -->
````python
# workbench/toolchain.py
"""Explicit deterministic context/tool stages; not an unconstrained agent loop."""

import json
from pathlib import Path

import typer

from workbench.filesystem import write_json
from workbench.knowledge import build_index
from workbench.retrieval import compact_map, query
from workbench.settings import ROOT, Settings

app = typer.Typer(no_args_is_help=True, help="索引、Continue、Aider和Daytona的受控工具")


def prepare_context(settings, template, requirement, destination):
    if template == "python-basic":
        sources = [{"slot": "product", "path": str(ROOT / "templates/product"), "sha": "bundled"}]
    else:
        from workbench.vendor import prepare

        sources = prepare(settings, template)
    query_text = " ".join([requirement.get("summary", ""), *requirement.get("features", [])])[:1500]
    query_text = query_text.strip() or "Controller Service useVbenForm"
    contexts = []
    for row in sources:
        output = Path(destination) / row["slot"]
        build_index(row["path"], output, row["sha"])
        if settings.repo_map_provider == "aider":
            from workbench.aider_tool import repo_map

            mapping = repo_map(row["path"], output, settings)
        else:
            mapping = compact_map(output, max_chars=settings.repo_map_chars)
        if settings.embedding_enabled:
            from workbench.retrieval import add_embeddings

            add_embeddings(row["path"], output, settings)
        found = query(row["path"], output, query_text, limit=4, max_chars=6000, settings=settings)
        contexts.append({"slot": row["slot"], "repo_map": mapping, "retrieval": found})
    result = {
        "template": template,
        "contexts": contexts,
        "model_calls": 0,
        "source_is_untrusted_data": True,
    }
    write_json(Path(destination) / "context-receipt.json", result)
    return result


@app.command("search")
def search_command(
    source: Path, index: Path, question: str, file_suffix: str = "", path_prefix: str = ""
):
    """查询已建立的索引，只使用本机索引与本机向量服务，不默认计算向量。"""
    typer.echo(
        json.dumps(
            query(
                source,
                index,
                question,
                settings=Settings(),
                file_suffix=file_suffix,
                path_prefix=path_prefix,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("embed")
def embed_command(source: Path, index: Path):
    """显式启用后建立本机向量索引，不继承聊天模型凭据。"""
    from workbench.retrieval import add_embeddings

    typer.echo(json.dumps(add_embeddings(source, index, Settings()), ensure_ascii=False))


@app.command("repo-map")
def map_command(source: Path, index: Path):
    """按配置生成本地符号地图或真实Aider Repo Map；不调用LLM。"""
    settings = Settings()
    build_index(source, index)
    if settings.repo_map_provider == "aider":
        from workbench.aider_tool import repo_map

        result = repo_map(source, index, settings)
    else:
        result = compact_map(index, settings.repo_map_chars)
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("continue-config")
def continue_command(workspace: Path, source: Path, index: Path):
    """创建Continue的只读MCP配置；已有配置不覆盖。"""
    from workbench.context_mcp import export_continue

    typer.echo(json.dumps(export_continue(workspace, source, index), ensure_ascii=False))


@app.command("context-server")
def context_server(source: Path, index: Path):
    """Continue通过stdio启动；stdout专用于MCP协议，不打印日志。"""
    from workbench.context_mcp import make_server

    make_server(source, index, Settings()).run(transport="stdio")
````
