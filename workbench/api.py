"""Local operator API. Authentication protects every data endpoint, including downloads."""

import hashlib
import hmac
import json
import threading
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
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

    def auth(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not credentials or not hmac.compare_digest(
            credentials.credentials, request.app.state.token
        ):
            raise HTTPException(401, "需要本机访问令牌；执行 uv run rnd token 查看")
        return request.app.state.store

    @app.exception_handler(Conflict)
    async def conflict_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(Missing)
    async def missing_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.get("/", include_in_schema=False)
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
        result = []
        for stage in STAGES:
            try:
                profile = settings.model_for(stage)
                row = profile.public()
                profile.validate_endpoint()
                row["valid"] = True
            except ValueError as exc:
                row = {"stage": stage, "valid": False, "error": settings.redact(str(exc))}
            row["enabled"] = stage != "review" or settings.review_enabled
            result.append(row)
        return result

    @app.get("/runs/{run_id}/models")
    def run_models(run_id: str, store=Depends(auth)):
        return store.model_records(run_id)

    @app.post("/runs/{run_id}/automation", status_code=202)
    def automation(
        run_id: str, body: AutomationInput, idempotency_key: str = Header(), store=Depends(auth)
    ):
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

    @app.post("/projects/{project_id}/runs", status_code=202)
    def create_run(
        project_id: str, body: RunInput, idempotency_key: str = Header(), store=Depends(auth)
    ):
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
        return store.submit(run_id, body.model_dump(), idempotency_key)

    @app.post("/runs/{run_id}/retry", status_code=202)
    def retry(run_id: str, idempotency_key: str = Header(), store=Depends(auth)):
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

    return app


app = create_app()
