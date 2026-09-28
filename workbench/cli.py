"""Operator commands: init/start/chat/show/download/index/native. No custom UI needed."""

import json
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import typer

from workbench.settings import ROOT, Settings
from workbench.store import Store

app = typer.Typer(no_args_is_help=True, help="本地 AI 研发平台（Python 3.14）")
native_app = typer.Typer(no_args_is_help=True)
app.add_typer(native_app, name="native")


def echo(value):
    typer.echo(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def client(url=None):
    settings = Settings()
    base = url or f"http://127.0.0.1:{settings.port}"
    if urlsplit(base).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise typer.BadParameter("本地 CLI 仅连接本机平台，避免把访问令牌发给远端")
    path = settings.data_dir / "access-token"
    if not path.exists():
        raise typer.BadParameter("先执行 uv run rnd start")
    return httpx.Client(
        base_url=base,
        headers={"Authorization": "Bearer " + path.read_text().strip()},
        timeout=30,
        trust_env=False,
    )


def api_call(c, method, path, body=None):
    headers = {"Idempotency-Key": str(uuid.uuid4())}
    response = c.request(method, path, json=body, headers=headers)
    if response.is_error:
        typer.echo(f"HTTP {response.status_code}: {response.text}", err=True)
        raise typer.Exit(1)
    return response.json()


@app.command()
def init():
    """首次创建 .env；不覆盖配置、不打印密钥。"""
    target = ROOT / ".env"
    if not target.exists():
        target.write_text((ROOT / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
    store = Store(Settings())
    try:
        store.migrate()
        store.token()
    finally:
        store.engine.dispose()
    typer.echo("已初始化 SQLite 和访问令牌。请填写 .env 的 BASE_URL、API_KEY、MODE。")


@app.command()
def start(no_worker: bool = False):
    """迁移数据库并启动 API，默认内置一个持久 Worker。"""
    import uvicorn

    from workbench.api import create_app

    settings = Settings()
    try:
        settings.require_model()
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from None
    if settings.host not in {"127.0.0.1", "localhost", "::1"}:
        raise typer.BadParameter("此版本只供本机体验，不绑定公网地址")
    typer.echo(f"接口调试页：http://127.0.0.1:{settings.port}/docs；另开终端执行 uv run rnd chat")
    uvicorn.run(
        create_app(settings, start_worker=not no_worker),
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


@app.command()
def worker():
    """API 使用 --no-worker 时，单独运行 Worker；不能重复启动。"""
    from workbench.runtime import Runtime

    settings = Settings()
    settings.require_model()
    store = Store(settings)
    store.migrate()
    try:
        with Runtime(settings, store) as runtime:
            runtime.loop()
    except KeyboardInterrupt:
        pass
    finally:
        store.engine.dispose()


@app.command()
def token():
    """显示本机访问令牌供 Swagger Authorize；不要分享或提交到 Git。"""
    path = Settings().data_dir / "access-token"
    if not path.exists():
        raise typer.BadParameter("先执行 rnd init 或 rnd start")
    typer.echo(path.read_text(encoding="utf-8").strip())


@app.command()
def doctor():
    """检查解释器和配置；不调用模型、不打印 API Key。"""
    import sys

    settings = Settings()
    try:
        settings.require_model()
        model_config = "configured"
    except ValueError as exc:
        model_config = str(exc)
    echo(
        {
            "python": sys.version.split()[0],
            "data_dir": str(settings.data_dir),
            "database": "sqlite" if settings.db_url.startswith("sqlite:") else "postgresql",
            "model": settings.model,
            "model_config": model_config,
            "api_key": "configured" if settings.api_key.get_secret_value() else "missing",
        }
    )


@app.command()
def templates():
    """查看模板能力和本机原生生成器配置状态。"""
    from workbench.native import catalog

    echo(catalog(Settings()))


@app.command()
def chat(run: str = "", template: str = "python-basic"):
    """创建并体验整个流程，或用 --run 恢复已有运行。"""
    with client() as c:
        if not run:
            title = typer.prompt("项目名称")
            requirement = typer.prompt("你希望做什么系统")
            project = api_call(c, "POST", "/projects", {"title": title})
            created = api_call(
                c,
                "POST",
                f"/projects/{project['id']}/runs",
                {"requirement": requirement, "template": template},
            )
            run = created["run_id"]
        typer.echo(f"运行 ID：{run}\n中断后使用 uv run rnd chat --run {run} 继续。")
        previous = None
        try:
            while True:
                state = api_call(c, "GET", f"/runs/{run}")
                if state["status"] != previous:
                    typer.echo("状态：" + state["status"])
                    previous = state["status"]
                if state["status"] in {"READY", "SOURCE_READY"}:
                    typer.echo(f"完成。下载命令：uv run rnd download {run}")
                    if state["status"] == "SOURCE_READY":
                        typer.echo("这是原生源码导出，不是已通过完整运行验收的产品。")
                    break
                if state["status"] in {"FAILED", "REJECTED"}:
                    typer.echo(state.get("error") or "操作已拒绝")
                    break
                gate = state.get("pending")
                if not gate:
                    time.sleep(0.5)
                    continue
                echo(gate["data"])
                typer.echo("当前阶段：" + gate["stage"])
                text = typer.prompt("填写回答/修改意见；批准请输入“批准”，拒绝请输入“拒绝”")
                if text == "批准":
                    payload = {"gate_id": gate["gate_id"], "action": "approve", "approved": True}
                elif text == "拒绝":
                    payload = {"gate_id": gate["gate_id"], "action": "reject", "approved": False}
                else:
                    action = "answer" if "answer" in gate["actions"] else "revise"
                    payload = {"gate_id": gate["gate_id"], "action": action, "text": text}
                if payload["action"] not in gate["actions"] or (
                    payload["action"] == "approve" and not gate["can_approve"]
                ):
                    typer.echo("当前条件不允许此动作，请先回答问题或修改范围。")
                    continue
                api_call(c, "POST", f"/runs/{run}/resume", payload)
        except KeyboardInterrupt:
            typer.echo(f"已退出交互；运行仍保存。恢复：uv run rnd chat --run {run}")


@app.command()
def show(run: str):
    with client() as c:
        echo(api_call(c, "GET", f"/runs/{run}"))


@app.command()
def retry(run: str):
    with client() as c:
        echo(api_call(c, "POST", f"/runs/{run}/retry"))


@app.command()
def download(run: str, output: Path = Path("deliveries")):
    output.mkdir(parents=True, exist_ok=True)
    # UUID validation prevents a run value from becoming an arbitrary output path.
    run = str(uuid.UUID(run))
    target = output / f"{run}.zip"
    if target.exists():
        raise typer.BadParameter("目标 ZIP 已存在，请选择新目录")
    with client() as c:
        response = c.get(f"/runs/{run}/download")
        response.raise_for_status()
        target.write_bytes(response.content)
    typer.echo(str(target.resolve()))


@app.command()
def index(source: Path, output: Path):
    """在源码目录外创建增量 AST/文件哈希知识包。"""
    from workbench.knowledge import build_index

    echo(build_index(source, output))


@native_app.command("prepare")
def native_prepare(template: str):
    """克隆白名单中的固定开源提交，建立原生模板源码知识包。"""
    from workbench.native import prepare_sources

    echo(prepare_sources(Settings(), template))


@native_app.command("config-example")
def config_example(template: str):
    """创建本机原生服务配置示例，不覆盖已有配置。"""
    from workbench.native import write_config_example

    typer.echo(str(write_config_example(Settings(), template)))


if __name__ == "__main__":
    app()
