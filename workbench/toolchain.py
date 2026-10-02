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
