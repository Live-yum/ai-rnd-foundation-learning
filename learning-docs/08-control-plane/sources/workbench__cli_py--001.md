# workbench/cli.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：终端入口和运维命令。** Typer把Python函数映射为rnd子命令。init建立本机数据和索引，start启动网页，chat/recommend调用与网页相同的API；index/tools等工具命令是独立的本机诊断入口。token只供本机使用，不应贴进公开日志。

**对应关系：** pyproject的project.scripts → cli.app → api/runtime/toolchain；test_tools_cli。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.conversation`、`workbench.settings`、`workbench.store`、`workbench.toolchain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 先在终端A保持rnd start运行，终端B的chat/show等才是HTTP客户端。client用contextmanager管理连接，按Settings.port取得地址，在进入模板或项目问题前先请求/health；初次或后续ConnectError都转成中文启动/PORT提示并以退出码1结束，连接仍会关闭。健康请求只能证明服务可连，不能代替/ready、批准关卡或产品验收。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `echo`（L25–L26）：接收`value`。 调用`typer.echo`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `client`（L30–L54）：接收`url`。 控制顺序：L33按`urlsplit(base).hostname not in {"127.0.0.1", "localhost", "::1"}`分支；L34抛异常，停止当前正常路径；L36按`not path.exists()`分支；L37抛异常，停止当前正常路径；L54抛异常，停止当前正常路径。 调用`Settings`、`urlsplit`、`typer.BadParameter`、`path.exists`、`httpx.Client`、`path.read_text().strip`、`path.read_text`、`api_call`、`typer.echo`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `api_call`（L57–L63）：接收`c`、`method`、`path`、`body`。 控制顺序：L60按`response.is_error`分支；L62抛异常，停止当前正常路径。 调用`str`、`uuid.uuid4`、`c.request`、`typer.echo`、`typer.Exit`、`response.json`。 返回路径：L63的`response.json()`。
- `init`（L67–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：首次创建 .env；不覆盖配置、不打印密钥。。 控制顺序：L70按`not target.exists()`分支；L80遍历`("fastapiadmin", "yudao-vben")`。 调用`target.exists`、`target.write_text`、`(ROOT / ".env.example").read_text`、`Store`、`Settings`、`store.migrate`、`store.token`、`store.engine.dispose`、`prepare`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `start`（L88–L107）：接收`no_worker`。 源码说明：迁移数据库并启动 API，默认内置一个持久 Worker。。 控制顺序：L95按`not settings.models_ready()`分支；L97按`settings.host not in {"127.0.0.1", "localhost", "::1"}`分支；L98抛异常，停止当前正常路径。 调用`Settings`、`settings.models_ready`、`typer.echo`、`typer.BadParameter`、`uvicorn.run`、`create_app`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `worker`（L111–L125）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：API 使用 --no-worker 时，单独运行 Worker；不能重复启动。。 调用`Settings`、`settings.require_model`、`Store`、`store.migrate`、`Runtime`、`runtime.loop`、`store.engine.dispose`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `token`（L129–L134）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：显示本机访问令牌供 Swagger Authorize；不要分享或提交到 Git。。 控制顺序：L132按`not path.exists()`分支；L133抛异常，停止当前正常路径。 调用`Settings`、`path.exists`、`typer.BadParameter`、`typer.echo`、`path.read_text(encoding="utf-8").strip`、`path.read_text`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `doctor`（L138–L161）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：检查解释器和配置；不调用模型、不打印 API Key。。 调用`Settings`、`settings.model_configuration`、`configuration.default.public`、`configuration.require_model`、`str`、`echo`、`sys.version.split`、`settings.db_url.startswith`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `templates`（L165–L169）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：查看模板能力和本机原生生成器配置状态。。 调用`echo`、`catalog`、`Settings`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `chat`（L173–L301）：接收`run`、`template`、`frontend`、`database`、`smart`。 源码说明：创建并体验整个流程，或用 --run 恢复已有运行。。 控制顺序：L178按`not run`分支；L180按`not template`分支；L182遍历`enumerate(available, 1)`；L185按`not 1 <= index <= len(available)`分支；L186抛异常，停止当前正常路径；L189按`item is None`分支；L190抛异常，停止当前正常路径；L191按`not frontend`分支。后续分支沿下方源码相同行号继续阅读。 调用`client`、`selections`、`typer.echo`、`enumerate`、`typer.prompt`、`len`、`typer.BadParameter`、`next`、`", ".join`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `recommend`（L305–L308）：接收`run`。 源码说明：授权当前运行的后续未明确需求使用AI建议；不绕过测试与技术前提。。 调用`client`、`echo`、`api_call`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `manual`（L312–L315）：接收`run`。 源码说明：关闭后续自动决定；下一道门恢复人工确认。。 调用`client`、`echo`、`api_call`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `models`（L319–L326）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：显示各阶段实际模型选择，不显示密钥；单模型配置自动回退。。 控制顺序：L322遍历`STAGES`。 调用`Settings`、`echo`、`settings.model_for(stage).public`、`settings.model_for`、`settings.redact`、`str`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `show`（L330–L332）：接收`run`。 调用`client`、`echo`、`api_call`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `retry`（L336–L338）：接收`run`。 调用`client`、`echo`、`api_call`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `download`（L342–L353）：接收`run`、`output`。 控制顺序：L347按`target.exists()`分支；L348抛异常，停止当前正常路径。 调用`Path`、`output.mkdir`、`str`、`uuid.UUID`、`target.exists`、`typer.BadParameter`、`client`、`c.get`、`response.raise_for_status`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `index`（L357–L361）：接收`source`、`output`。 源码说明：在源码目录外创建增量 AST/文件哈希知识包。。 调用`echo`、`build_index`、`app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_prepare`（L365–L369）：接收`template`。 源码说明：校验并展开仓库内固定源码归档，建立原生模板源码知识包；不在线克隆。。 调用`echo`、`prepare_sources`、`Settings`、`native_app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `config_example`（L373–L377）：接收`template`。 源码说明：创建本机原生服务配置示例，不覆盖已有配置。。 调用`typer.echo`、`str`、`write_config_example`、`Settings`、`native_app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_runtime_config`（L381–L385）：接收`template`。 源码说明：创建原生全栈运行配置；必须显式授权专用空 PostgreSQL 库。。 调用`typer.echo`、`str`、`write_runtime_example`、`Settings`、`native_app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_serve`（L389–L396）：接收`run`。 源码说明：重新打开已验收原生产品；复用开发库，不删库、不重新生成。。 调用`serve_managed`、`Settings`、`typer.echo`、`native_app.command`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/cli.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L400。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15534`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/cli.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cfd88374504b521efdc92de06642093512ad18785a2f66642c96b5ca6bbd9023"} -->
````python
# workbench/cli.py
"""Operator commands: init/start/chat/show/download/index/native. No custom UI needed."""

import json
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import typer

from workbench.catalog import Selection, selections
from workbench.conversation import command_word
from workbench.settings import ROOT, STAGES, Settings
from workbench.store import Store
from workbench.toolchain import app as tools_app

app = typer.Typer(no_args_is_help=True, help="本地 AI 研发平台（Python 3.14）")
native_app = typer.Typer(no_args_is_help=True)
app.add_typer(native_app, name="native")
app.add_typer(tools_app, name="tools")


def echo(value):
    typer.echo(json.dumps(value, ensure_ascii=False, indent=2, default=str))


@contextmanager
def client(url=None):
    settings = Settings()
    base = url or f"http://127.0.0.1:{settings.port}"
    if urlsplit(base).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise typer.BadParameter("本地 CLI 仅连接本机平台，避免把访问令牌发给远端")
    path = settings.data_dir / "access-token"
    if not path.exists():
        raise typer.BadParameter("先执行 uv run rnd start")
    try:
        with httpx.Client(
            base_url=base,
            headers={"Authorization": "Bearer " + path.read_text().strip()},
            timeout=30,
            trust_env=False,
        ) as c:
            api_call(c, "GET", "/health")
            yield c
    except httpx.ConnectError:
        typer.echo(
            f"无法连接本机平台 {base}。\n"
            "请在同一项目目录的另一个终端执行 uv run rnd start，并保持服务运行。\n"
            "若已启动，请检查 .env 的 PORT 配置和启动日志，再重试当前命令。",
            err=True,
        )
        raise typer.Exit(1) from None


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
    from workbench.vendor import prepare

    for template in ("fastapiadmin", "yudao-vben"):
        prepare(Settings(), template)
    typer.echo(
        "已初始化数据库、令牌并从本仓库解压全部模板。请填写 .env 的 BASE_URL、API_KEY、MODE。"
    )


@app.command()
def start(no_worker: bool = False):
    """迁移数据库并启动 API，默认内置一个持久 Worker。"""
    import uvicorn

    from workbench.api import create_app

    settings = Settings()
    if not settings.models_ready():
        typer.echo("模型尚未配置完成；请打开操作台的模型设置。保存有效配置后即可开始运行。")
    if settings.host not in {"127.0.0.1", "localhost", "::1"}:
        raise typer.BadParameter("此版本只供本机体验，不绑定公网地址")
    typer.echo(
        f"操作台：http://127.0.0.1:{settings.port}/  接口文档：/docs；令牌用 uv run rnd token 查看。CLI：uv run rnd chat"
    )
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
    model = {"model": "", "api_key": "unavailable"}
    try:
        configuration = settings.model_configuration()
        model = configuration.default.public()
        configuration.require_model()
        model_config = "configured"
    except ValueError as exc:
        model_config = str(exc)
    echo(
        {
            "python": sys.version.split()[0],
            "data_dir": str(settings.data_dir),
            "database": "sqlite" if settings.db_url.startswith("sqlite:") else "postgresql",
            "model": model["model"],
            "model_config": model_config,
            "api_key": model["api_key"],
            "validation_scope": "format_only",
        }
    )


@app.command()
def templates():
    """查看模板能力和本机原生生成器配置状态。"""
    from workbench.native import catalog

    echo(catalog(Settings()))


@app.command()
def chat(
    run: str = "", template: str = "", frontend: str = "", database: str = "", smart: bool = False
):
    """创建并体验整个流程，或用 --run 恢复已有运行。"""
    with client() as c:
        if not run:
            available = selections()
            if not template:
                typer.echo("先选择交付的后端模板，再选择兼容前端与数据库：")
                for i, item in enumerate(available, 1):
                    typer.echo(f"{i}. {item['name']} ({item['template']})")
                index = typer.prompt("模板编号", default=1, type=int)
                if not 1 <= index <= len(available):
                    raise typer.BadParameter("模板编号不存在")
                template = available[index - 1]["template"]
            item = next((x for x in available if x["template"] == template), None)
            if item is None:
                raise typer.BadParameter("未知模板")
            if not frontend:
                frontend = typer.prompt(
                    "前端（" + ", ".join(item["frontends"]) + "）", default=item["frontends"][0]
                )
            if not database:
                database = typer.prompt(
                    "交付数据库（" + ", ".join(item["databases"]) + "）",
                    default=item["databases"][0],
                )
            selection = Selection(template=template, frontend=frontend, database=database)
            echo(selection.model_dump())
            if template != "python-basic":
                typer.echo("原生模板需要Linux/WSL及对应原生运行环境；交付包含初始化/迁移入口。")
            elif database == "postgresql":
                typer.echo(
                    "PostgreSQL产品需要Docker或已配置的独立开发数据库；平台控制库仍可用SQLite。"
                )
            typer.echo(
                "标准案例为内部客户服务管理平台；完整原始需求、默认决策和命名约定见 examples/requirements/customer-service*.md。"
            )
            title = typer.prompt("项目名称")
            requirement = typer.prompt("你希望做什么系统")
            project = api_call(c, "POST", "/projects", {"title": title})
            created = api_call(
                c,
                "POST",
                f"/projects/{project['id']}/runs",
                {
                    "requirement": requirement,
                    "template": template,
                    "selection": selection.model_dump(),
                    "intelligent": smart,
                },
            )
            run = created["run_id"]
        if smart:
            api_call(c, "POST", f"/runs/{run}/automation", {"enabled": True, "accepted": True})
        typer.echo(f"运行 ID：{run}\n中断后使用 uv run rnd chat --run {run} 继续。")
        typer.echo(
            "任意等待阶段输入『智能推荐』：后续未确定细节由AI推荐并自动决定，不再逐项询问；独立验证不能跳过。"
        )
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
                gate = state.get("pending")
                if state["status"] in {"FAILED", "REJECTED", "BLOCKED", "PAUSED_LIMIT"}:
                    typer.echo(state.get("error") or "操作已拒绝")
                    if state["status"] != "BLOCKED" or not gate:
                        if state["status"] != "REJECTED":
                            typer.echo(f"修复原因后重试：uv run rnd retry {run}")
                        break
                    typer.echo(
                        "运行与回答已保存。下面可查看具体阻塞并继续操作，不会自动重试或新建项目。"
                    )
                if not gate:
                    time.sleep(0.5)
                    continue
                echo(gate["data"])
                typer.echo("当前阶段：" + gate["stage"])
                prompt = "答复 / 批准 / 拒绝 / 智能推荐 / 手动 / 退出"
                if state["status"] == "BLOCKED":
                    prompt += " / 重试"
                text = typer.prompt(prompt)
                word = command_word(text)
                if word in {"退出", "quit", "exit"}:
                    typer.echo(f"已保留运行：{run}")
                    break
                if word in {"手动", "manual"}:
                    api_call(
                        c, "POST", f"/runs/{run}/automation", {"enabled": False, "accepted": False}
                    )
                    continue
                if word in {"重试", "retry"}:
                    if state["status"] == "BLOCKED":
                        api_call(c, "POST", f"/runs/{run}/retry")
                    else:
                        typer.echo(
                            "当前为等待确认阶段，请答复或选择智能推荐；控制指令不会发送给模型。"
                        )
                    continue
                if word in {"智能推荐", "推荐", "smart", "recommend"}:
                    api_call(
                        c, "POST", f"/runs/{run}/automation", {"enabled": True, "accepted": True}
                    )
                    continue
                if word in {"批准", "approve"}:
                    payload = {"gate_id": gate["gate_id"], "action": "approve", "approved": True}
                elif word in {"拒绝", "reject"}:
                    payload = {"gate_id": gate["gate_id"], "action": "reject", "approved": False}
                else:
                    action = "answer" if "answer" in gate["actions"] else "revise"
                    payload = {"gate_id": gate["gate_id"], "action": action, "text": text}
                if payload["action"] not in gate["actions"] or (
                    payload["action"] == "approve" and not gate["can_approve"]
                ):
                    typer.echo(
                        "本轮尚有未确定事项：可回答，或输入『智能推荐』让AI决定后续。此次控制指令不会送给模型，也不会消耗轮数。"
                    )
                    continue
                api_call(c, "POST", f"/runs/{run}/resume", payload)
        except KeyboardInterrupt:
            typer.echo(f"已退出交互；运行仍保存。恢复：uv run rnd chat --run {run}")


@app.command()
def recommend(run: str):
    """授权当前运行的后续未明确需求使用AI建议；不绕过测试与技术前提。"""
    with client() as c:
        echo(api_call(c, "POST", f"/runs/{run}/automation", {"enabled": True, "accepted": True}))


@app.command()
def manual(run: str):
    """关闭后续自动决定；下一道门恢复人工确认。"""
    with client() as c:
        echo(api_call(c, "POST", f"/runs/{run}/automation", {"enabled": False, "accepted": False}))


@app.command()
def models():
    """显示各阶段实际模型选择，不显示密钥；单模型配置自动回退。"""
    settings = Settings()
    for stage in STAGES:
        try:
            echo(settings.model_for(stage).public())
        except ValueError as exc:
            echo({"stage": stage, "error": settings.redact(str(exc))})


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
    """校验并展开仓库内固定源码归档，建立原生模板源码知识包；不在线克隆。"""
    from workbench.native import prepare_sources

    echo(prepare_sources(Settings(), template))


@native_app.command("config-example")
def config_example(template: str):
    """创建本机原生服务配置示例，不覆盖已有配置。"""
    from workbench.native import write_config_example

    typer.echo(str(write_config_example(Settings(), template)))


@native_app.command("runtime-config")
def native_runtime_config(template: str):
    """创建原生全栈运行配置；必须显式授权专用空 PostgreSQL 库。"""
    from workbench.native_delivery import write_runtime_example

    typer.echo(str(write_runtime_example(Settings(), template)))


@native_app.command("serve")
def native_serve(run: str):
    """重新打开已验收原生产品；复用开发库，不删库、不重新生成。"""
    from workbench.native_delivery import serve_managed

    try:
        serve_managed(Settings(), run)
    except KeyboardInterrupt:
        typer.echo("原生后端和前端预览已停止。")


if __name__ == "__main__":
    app()
````
