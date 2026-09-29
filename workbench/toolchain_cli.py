"""Explicit operator commands; optional tools never install or contact clouds at import time."""

import json
import shutil
from pathlib import Path

import typer

from workbench.code_index import parser_identity
from workbench.settings import Settings

app = typer.Typer(no_args_is_help=True, help="多语言索引、Aider、Continue和显式授权的沙箱工具")


def show(value):
    typer.echo(json.dumps(value, ensure_ascii=False, indent=2, default=str))


@app.command()
def status():
    from workbench.aider_tools import tool_python

    settings = Settings()
    try:
        tool_python()
        installed = True
    except ValueError:
        installed = False
    show(
        {
            "parsers": parser_identity(),
            "aider_installed": installed,
            "coding_engine": settings.coding_engine,
            "repo_map_engine": settings.repo_map_engine,
            "sandbox_backend": settings.sandbox_backend,
            "local_process_is_sandbox": False,
            "daytona_upload_authorized": settings.daytona_upload_authorized,
            "daytona_key": "configured"
            if settings.daytona_api_key.get_secret_value()
            else "missing",
        }
    )


@app.command("install-aider")
def install_aider():
    """显式安装固定Aider到独立Python3.12环境，不改变平台Python3.14。"""
    from workbench.aider_tools import TOOL
    from workbench.tools import run_command

    uv = shutil.which("uv")
    if not uv:
        raise typer.BadParameter("请先安装uv")
    result = run_command(
        [uv, "sync", "--locked", "--project", str(TOOL), "--python", "3.12", "--no-dev"],
        TOOL,
        timeout=900,
    )
    show({"installed": result["returncode"] == 0, "python": "3.12", "platform_python": "3.14"})


@app.command("search")
def search_code(source: Path, index: Path, query: str):
    from workbench.retrieval import search

    show(search(source, index, query))


@app.command("repo-map")
def repo_map(source: Path, index: Path, engine: str = "symbols"):
    from workbench.retrieval import load_current, symbol_map

    load_current(source, index)
    if engine == "aider":
        from workbench.aider_tools import repo_map as aider_map

        show(aider_map(source, Settings()))
    elif engine == "symbols":
        show(symbol_map(source, index))
    else:
        raise typer.BadParameter("engine只能为symbols或aider")


@app.command("continue-config")
def continue_config(source: Path, index: Path):
    from workbench.continue_mcp import config
    from workbench.retrieval import load_current

    load_current(source, index)
    show(config(source, index))
