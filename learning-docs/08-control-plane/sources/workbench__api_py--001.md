# workbench/api.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：网页及CLI调用的HTTP接口。** create_app是应用工厂，先准备依赖和生命周期，再定义路由。路由校验本机访问令牌和请求合同，调用Store/Runtime；下载与报告只允许受控目录内的文件。内层函数就是具体HTTP处理器，不是另一个服务。

**对应关系：** web/app.js或cli → FastAPI路由 → Store/Runtime；test_api。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.catalog`、`workbench.domain`、`workbench.filesystem`、`workbench.runtime`、`workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `create_app`（L25–L273）：接收`settings`、`gateway_factory`、`start_worker`。定义并返回FastAPI应用对象；内层带路由装饰器的函数在对应HTTP请求到达时调用，而不是定义时立即执行。 调用`Settings`、`FastAPI`、`app.add_middleware`、`HTTPBearer`、`register_model_settings_routes`、`register_streaming_routes`。 返回路径：L273的`app`。
- `create_app.lifespan`（L29–L51）：接收`app`。 控制顺序：L37按`start_worker`分支。 调用`Store`、`store.token`、`FileLock`、`str`、`store.migrate`、`gateway_factory`、`Runtime`、`threading.Thread`、`worker.start`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `create_app.response_security`（L60–L72）：接收`request`、`call_next`。 控制顺序：L65按`request.url.path in {"/", "/ui"} or request.url.path.startswith("/ui/")`分支。 调用`call_next`、`request.url.path.startswith`、`app.middleware`。 返回路径：L72的`response`。
- `create_app.auth`（L74–L79）：接收`request`、`credentials`。核对当前工作台HTTP请求的本机访问令牌；它不是产品用户登录，也不联系Dex或大模型供应商。 控制顺序：L75按`not credentials or not hmac.compare_digest( credentials.credentials, request.app.stat…`分支；L78抛异常，停止当前正常路径。 调用`Depends`、`hmac.compare_digest`、`HTTPException`。 返回路径：L79的`request.app.state.store`。
- `create_app.validation_handler`（L82–L91）：接收`request`、`exc`。 调用`JSONResponse`、`exc.errors`、`app.exception_handler`。 返回路径：L85的`JSONResponse( status_code=422, content={ "detail": "请求字段或格式无效，请检查必填项和当前步骤", "errors": [{"t…`。
- `create_app.conflict_handler`（L94–L95）：接收`request`、`exc`。 调用`JSONResponse`、`str`、`app.exception_handler`。 返回路径：L95的`JSONResponse(status_code=409, content={"detail": str(exc)})`。
- `create_app.missing_handler`（L98–L99）：接收`request`、`exc`。 调用`JSONResponse`、`str`、`app.exception_handler`。 返回路径：L99的`JSONResponse(status_code=404, content={"detail": str(exc)})`。
- `create_app.workspace_page`（L104–L108）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`FileResponse`、`app.get`。 返回路径：L105的`FileResponse( ROOT / "workbench/web/index.html", headers={"Cache-Control": "no-store", "Re…`。
- `create_app.ui_asset`（L111–L114）：接收`asset`。 控制顺序：L112按`asset not in {"app.js", "style.css"}`分支；L113抛异常，停止当前正常路径。 调用`HTTPException`、`FileResponse`、`app.get`。 返回路径：L114的`FileResponse(ROOT / "workbench/web" / asset)`。
- `create_app.catalog`（L117–L118）：接收`store`。 调用`Depends`、`selections`、`app.get`。 返回路径：L118的`selections()`。
- `create_app.models`（L121–L138）：接收`store`。 控制顺序：L125抛异常，停止当前正常路径；L127遍历`STAGES`。 调用`Depends`、`settings.model_configuration`、`HTTPException`、`configuration.profile`、`profile.public`、`profile.validate_endpoint`、`settings.redact`、`str`、`result.append`等。 返回路径：L138的`result`。
- `create_app.run_models`（L141–L142）：接收`run_id`、`store`。 调用`Depends`、`store.model_records`、`app.get`。 返回路径：L142的`store.model_records(run_id)`。
- `create_app.automation`（L145–L150）：接收`run_id`、`body`、`idempotency_key`、`store`。 控制顺序：L148按`body.enabled`分支。 调用`Header`、`Depends`、`require_models`、`store.set_automation`、`app.post`。 返回路径：L150的`store.set_automation(run_id, body.enabled, idempotency_key)`。
- `create_app.health`（L153–L154）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`app.get`。 返回路径：L154的`{"status": "ok"}`。
- `create_app.ready`（L157–L166）：接收`request`。 控制顺序：L162按`start_worker and (worker is None or not worker.is_alive())`分支。 调用`request.app.state.store.engine.connect`、`c.execute`、`text`、`worker.is_alive`、`JSONResponse`、`bool`、`app.get`。 返回路径：L163的`JSONResponse(status_code=503, content={"status": "worker_unavailable"})`；L164的`{"status": "ready", "worker": bool(worker)}`；L166的`JSONResponse(status_code=503, content={"status": "database_unavailable"})`。
- `create_app.create_project`（L169–L170）：接收`body`、`idempotency_key`、`store`。 调用`Header`、`Depends`、`store.create_project`、`app.post`。 返回路径：L170的`store.create_project(body.title, idempotency_key)`。
- `create_app.projects`（L173–L174）：接收`store`。 调用`Depends`、`store.list_projects`、`app.get`。 返回路径：L174的`store.list_projects()`。
- `create_app.project_runs`（L177–L178）：接收`project_id`、`store`。 调用`Depends`、`store.list_runs`、`app.get`。 返回路径：L178的`store.list_runs(project_id)`。
- `create_app.require_models`（L180–L184）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L184抛异常，停止当前正常路径。 调用`settings.require_model`、`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `create_app.create_run`（L187–L191）：接收`project_id`、`body`、`idempotency_key`、`store`。 调用`Header`、`Depends`、`require_models`、`store.create_run`、`body.model_dump`、`app.post`。 返回路径：L191的`store.create_run(project_id, body.model_dump(), idempotency_key)`。
- `create_app.runs`（L194–L195）：接收`store`。 调用`Depends`、`store.list_runs`、`app.get`。 返回路径：L195的`store.list_runs()`。
- `create_app.get_run`（L198–L199）：接收`run_id`、`store`。 调用`Depends`、`store.get_run`、`app.get`。 返回路径：L199的`store.get_run(run_id)`。
- `create_app.messages`（L202–L204）：接收`run_id`、`store`。 调用`Depends`、`store.get_run`、`store.messages`、`app.get`。 返回路径：L204的`store.messages(run_id)`。
- `create_app.resume`（L207–L212）：接收`run_id`、`body`、`idempotency_key`、`store`。 控制顺序：L210按`body.action != "reject"`分支。 调用`Header`、`Depends`、`require_models`、`store.submit`、`body.model_dump`、`app.post`。 返回路径：L212的`store.submit(run_id, body.model_dump(), idempotency_key)`。
- `create_app.retry`（L215–L217）：接收`run_id`、`idempotency_key`、`store`。 调用`Header`、`Depends`、`require_models`、`store.retry`、`app.post`。 返回路径：L217的`store.retry(run_id, idempotency_key)`。
- `create_app.events`（L220–L221）：接收`run_id`、`after`、`store`。 调用`Query`、`Depends`、`store.events`、`app.get`。 返回路径：L221的`store.events(run_id, after)`。
- `create_app.report`（L224–L240）：接收`run_id`、`store`。 控制顺序：L228遍历`( "generation.json", "verification.json", "delivery.json", "nativ…`；L238按`path.is_file()`分支。 调用`Depends`、`store.get_run`、`inside`、`path.is_file`、`json.loads`、`path.read_text`、`app.get`。 返回路径：L240的`result`。
- `create_app.download`（L243–L260）：接收`run_id`、`store`。 控制顺序：L245按`run["status"] not in {"READY", "SOURCE_READY"}`分支；L246抛异常，停止当前正常路径；L248按`not path.is_file()`分支；L249抛异常，停止当前正常路径；L251按`hashlib.sha256(data).hexdigest() != run["result"]["sha256"]`分支；L252抛异常，停止当前正常路径。 调用`Depends`、`store.get_run`、`Conflict`、`inside`、`path.is_file`、`Missing`、`path.read_bytes`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`等。 返回路径：L253的`Response( content=data, media_type="application/zip", headers={ "Content-Disposition": f'a…`。
- `create_app.templates`（L263–L266）：接收`store`。 调用`Depends`、`catalog`、`app.get`。 返回路径：L266的`catalog(settings)`。

</details>

**创建路径：** `workbench/api.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L276。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10811`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/api.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9be76b41042080e1abe5cf5b67456ae181c05f82e68d4d478316c4a77772a6ab"} -->
````python
# workbench/api.py
"""Local operator API. Authentication protects every data endpoint, including downloads."""

import hashlib
import hmac
import json
import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from filelock import FileLock
from sqlalchemy import text
from starlette.middleware.trustedhost import TrustedHostMiddleware

from workbench.catalog import selections
from workbench.domain import AutomationInput, ProjectInput, ResumeInput, RunInput
from workbench.filesystem import inside
from workbench.runtime import Runtime
from workbench.settings import ROOT, STAGES, Settings
from workbench.store import Conflict, Missing, Store


def create_app(settings=None, gateway_factory=None, start_worker=True):
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app):
        store = Store(settings)
        app.state.store = store
        app.state.token = store.token()
        app.state.worker = None
        with FileLock(str(settings.data_dir / "schema.lock"), timeout=30):
            store.migrate()
        try:
            if start_worker:
                gateway = gateway_factory(store) if gateway_factory else None
                with Runtime(settings, store, gateway) as runtime:
                    worker = threading.Thread(target=runtime.loop, name="rnd-worker", daemon=True)
                    app.state.worker = worker
                    worker.start()
                    try:
                        yield
                    finally:
                        runtime.stop.set()
                        worker.join()
            else:
                yield
        finally:
            store.engine.dispose()

    app = FastAPI(title="AI 研发平台 · 本地后端", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"]
    )
    bearer = HTTPBearer(auto_error=False)

    @app.middleware("http")
    async def response_security(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if request.url.path in {"/", "/ui"} or request.url.path.startswith("/ui/"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; "
                "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
            )
            response.headers["X-Frame-Options"] = "DENY"
        return response

    def auth(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not credentials or not hmac.compare_digest(
            credentials.credentials, request.app.state.token
        ):
            raise HTTPException(401, "需要本机访问令牌；执行 uv run rnd token 查看")
        return request.app.state.store

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request, exc):
        # Pydantic's default response includes `input` and may echo credentials.
        # Keep only bounded, input-independent validation categories.
        return JSONResponse(
            status_code=422,
            content={
                "detail": "请求字段或格式无效，请检查必填项和当前步骤",
                "errors": [{"type": error["type"]} for error in exc.errors()[:20]],
            },
        )

    @app.exception_handler(Conflict)
    async def conflict_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(Missing)
    async def missing_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.get("/", include_in_schema=False)
    @app.get("/ui", include_in_schema=False)
    @app.get("/ui/", include_in_schema=False)
    def workspace_page():
        return FileResponse(
            ROOT / "workbench/web/index.html",
            headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"},
        )

    @app.get("/ui/{asset}", include_in_schema=False)
    def ui_asset(asset: str):
        if asset not in {"app.js", "style.css"}:
            raise HTTPException(404)
        return FileResponse(ROOT / "workbench/web" / asset)

    @app.get("/catalog")
    def catalog(store=Depends(auth)):
        return selections()

    @app.get("/models")
    def models(store=Depends(auth)):
        try:
            configuration = settings.model_configuration()
        except ValueError:
            raise HTTPException(503, "本机模型配置无法安全读取，请检查配置格式与权限") from None
        result = []
        for stage in STAGES:
            try:
                profile = configuration.profile(stage)
                row = profile.public()
                profile.validate_endpoint()
                row["valid"] = True
            except ValueError as exc:
                row = {"stage": stage, "valid": False, "error": settings.redact(str(exc))}
            row["enabled"] = stage != "review" or configuration.review_enabled
            row["validation_scope"] = "format_only"
            result.append(row)
        return result

    @app.get("/runs/{run_id}/models")
    def run_models(run_id: str, store=Depends(auth)):
        return store.model_records(run_id)

    @app.post("/runs/{run_id}/automation", status_code=202)
    def automation(
        run_id: str, body: AutomationInput, idempotency_key: str = Header(), store=Depends(auth)
    ):
        if body.enabled:
            require_models()
        return store.set_automation(run_id, body.enabled, idempotency_key)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready")
    def ready(request: Request):
        try:
            with request.app.state.store.engine.connect() as c:
                c.execute(text("SELECT 1"))
            worker = request.app.state.worker
            if start_worker and (worker is None or not worker.is_alive()):
                return JSONResponse(status_code=503, content={"status": "worker_unavailable"})
            return {"status": "ready", "worker": bool(worker)}
        except Exception:
            return JSONResponse(status_code=503, content={"status": "database_unavailable"})

    @app.post("/projects", status_code=201)
    def create_project(body: ProjectInput, idempotency_key: str = Header(), store=Depends(auth)):
        return store.create_project(body.title, idempotency_key)

    @app.get("/projects")
    def projects(store=Depends(auth)):
        return store.list_projects()

    @app.get("/projects/{project_id}/runs")
    def project_runs(project_id: str, store=Depends(auth)):
        return store.list_runs(project_id)

    def require_models():
        try:
            settings.require_model()
        except ValueError:
            raise HTTPException(503, "请先在模型与配置中完成有效配置，再继续当前运行") from None

    @app.post("/projects/{project_id}/runs", status_code=202)
    def create_run(
        project_id: str, body: RunInput, idempotency_key: str = Header(), store=Depends(auth)
    ):
        require_models()
        return store.create_run(project_id, body.model_dump(), idempotency_key)

    @app.get("/runs")
    def runs(store=Depends(auth)):
        return store.list_runs()

    @app.get("/runs/{run_id}")
    def get_run(run_id: str, store=Depends(auth)):
        return store.get_run(run_id)

    @app.get("/runs/{run_id}/messages")
    def messages(run_id: str, store=Depends(auth)):
        store.get_run(run_id)
        return store.messages(run_id)

    @app.post("/runs/{run_id}/resume", status_code=202)
    def resume(
        run_id: str, body: ResumeInput, idempotency_key: str = Header(), store=Depends(auth)
    ):
        if body.action != "reject":
            require_models()
        return store.submit(run_id, body.model_dump(), idempotency_key)

    @app.post("/runs/{run_id}/retry", status_code=202)
    def retry(run_id: str, idempotency_key: str = Header(), store=Depends(auth)):
        require_models()
        return store.retry(run_id, idempotency_key)

    @app.get("/runs/{run_id}/events")
    def events(run_id: str, after: int = Query(default=0, ge=0), store=Depends(auth)):
        return store.events(run_id, after)

    @app.get("/runs/{run_id}/report")
    def report(run_id: str, store=Depends(auth)):
        store.get_run(run_id)
        directory = inside(settings.data_dir / "runs", run_id)
        result = {}
        for name in (
            "generation.json",
            "verification.json",
            "delivery.json",
            "native-generation.json",
            "source-context/context-receipt.json",
            "daytona-verification.json",
            "tool-failure.json",
        ):
            path = inside(directory, name)
            if path.is_file():
                result[name] = json.loads(path.read_text(encoding="utf-8"))
        return result

    @app.get("/runs/{run_id}/download")
    def download(run_id: str, store=Depends(auth)):
        run = store.get_run(run_id)
        if run["status"] not in {"READY", "SOURCE_READY"}:
            raise Conflict("尚未完成验收和人工交付批准")
        path = inside(inside(settings.data_dir / "runs", run_id), run["result"]["package"])
        if not path.is_file():
            raise Missing("交付文件不存在")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != run["result"]["sha256"]:
            raise Conflict("交付包哈希不匹配，拒绝下载")
        return Response(
            content=data,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{run_id}.zip"',
                "X-Artifact-SHA256": run["result"]["sha256"],
            },
        )

    @app.get("/templates")
    def templates(store=Depends(auth)):
        from workbench.native import catalog

        return catalog(settings)

    from workbench.model_settings import register_model_settings_routes
    from workbench.streaming import register_streaming_routes

    register_model_settings_routes(app, settings, auth)
    register_streaming_routes(app, auth)
    return app


app = create_app()
````
