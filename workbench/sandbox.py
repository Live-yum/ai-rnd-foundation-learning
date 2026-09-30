"""Opt-in self-hosted Daytona verification. No cloud control plane is allowed.

Local trusted acceptance is never skipped. A sandbox build is additional evidence,
not a substitute for database, RBAC, browser or clean-delivery acceptance.
"""

import io
import json
import shlex
import uuid
import zipfile
from importlib.metadata import version
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.local_only import DAYTONA_VERSION, local_http_url
from workbench.settings import ROOT, ModelProfile

REMOTE = "/tmp/rnd-verification"


def validate_configuration(settings, template, selection=None):
    if settings.sandbox_provider != "daytona":
        return
    if not settings.daytona_allow_local_execution:
        raise PrerequisiteError(
            "本机Daytona需要 DAYTONA_ALLOW_LOCAL_EXECUTION=true；只在本机创建隔离验证环境"
        )
    ModelProfile(
        stage="daytona",
        base_url=local_http_url(settings.daytona_api_url, "Daytona"),
        model="sandbox",
        api_key=settings.daytona_api_key,
    ).validate_endpoint()
    if not settings.daytona_snapshot or not settings.daytona_target:
        raise PrerequisiteError("请配置已安装构建工具的 DAYTONA_SNAPSHOT 和 DAYTONA_TARGET")
    if template == "python-basic" and (selection or {}).get("database", "sqlite") != "sqlite":
        raise PrerequisiteError(
            "Daytona的Python运行复验当前只支持独立SQLite；不会把本机PostgreSQL凭据复制进沙箱"
        )


def client_for(settings):
    from daytona import Daytona, DaytonaConfig

    if version("daytona") != DAYTONA_VERSION:
        raise PrerequisiteError("请使用锁定的Daytona SDK " + DAYTONA_VERSION)
    return Daytona(
        DaytonaConfig(
            api_key=settings.daytona_api_key.get_secret_value(),
            api_url=local_http_url(settings.daytona_api_url, "Daytona"),
            target=settings.daytona_target,
            otel_enabled=False,
        )
    )


def close_client(client):
    """Close owned transports of the pinned SDK, which has no Daytona.close().

    These names belong to our fixed SDK adapter, not a guessed public API.
    Sandbox deletion is separate and must complete before transport shutdown.
    All callers run in a bounded child process as an additional resource boundary.
    """
    import sys

    original = sys.exception()
    failures = []
    for name in ("_http_client", "_api_client", "_toolbox_api_client"):
        transport = getattr(client, name, None)
        if transport is not None:
            try:
                transport.close()
            except Exception as exc:
                failures.append(type(exc).__name__)
    if failures:
        message = "本机Daytona传输资源关闭失败：" + ", ".join(failures)
        if original is not None:
            original.add_note(message)
        else:
            raise PrerequisiteError(message)


def params_for(settings, name=None):
    from daytona import CreateSandboxFromSnapshotParams

    return CreateSandboxFromSnapshotParams(
        snapshot=settings.daytona_snapshot,
        name=name,
        network_block_all=True,
        public=False,
        auto_stop_interval=5,
        auto_delete_interval=0,
        env_vars={"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        labels={"managed-by": "rnd-toolchain", "purpose": "disposable-verification"},
    )


def checks_for(template):
    if template == "python-basic":
        return [
            (
                "locked-install",
                ["uv", "sync", "--locked", "--offline", "--no-dev", "--python", "3.14"],
                "product",
            ),
            (
                "migration-http-crud-restart",
                [
                    "./.venv/bin/python",
                    "../trusted-verify.py",
                    "--product",
                    ".",
                    "--python",
                    "./.venv/bin/python",
                    "--report",
                    "../runtime.json",
                ],
                "product",
            ),
        ]
    if template == "yudao-vben":
        return [
            ("maven-test", ["mvn", "-B", "-o", "test"], "product/backend"),
            (
                "frontend-install",
                ["pnpm", "install", "--offline", "--frozen-lockfile"],
                "product/frontend-product",
            ),
            (
                "frontend-types",
                ["pnpm", "--dir", "apps/web-antd", "exec", "vue-tsc", "--noEmit", "--skipLibCheck"],
                "product/frontend-product",
            ),
        ]
    if template == "fastapiadmin":
        return [
            ("python-syntax", ["python3", "-m", "compileall", "-q", "app"], "product/backend"),
            (
                "frontend-install",
                ["pnpm", "install", "--offline", "--frozen-lockfile"],
                "product/frontend/web",
            ),
            ("frontend-types", ["pnpm", "exec", "vue-tsc", "--noEmit"], "product/frontend/web"),
        ]
    raise PrerequisiteError("没有这个模板的已登记Daytona检查；不接受任意shell命令")


def source_archive(product):
    rows = list(files(product))
    if len(rows) > 20000 or sum(p.stat().st_size for _, p in rows) > 150_000_000:
        raise PrerequisiteError("源码超过Daytona上传预算；未创建沙箱")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, path in rows:
            if Path(name).name == ".npmrc":
                text = path.read_text(encoding="utf-8")
                if any(word in text.lower() for word in ("_auth", "password", "username", "${")):
                    raise PrerequisiteError(".npmrc含认证配置，拒绝上传；请使用无凭据构建配置")
            archive.writestr("product/" + name, path.read_bytes())
    return buffer.getvalue()


def verify_in_daytona(product, template, settings, *, client=None):
    validate_configuration(settings, template)
    if client is None:
        from workbench.daytona_worker import run_isolated

        return run_isolated(product, template, settings)
    return _verify_in_daytona(product, template, settings, client=client)


def _verify_in_daytona(product, template, settings, *, client):
    if settings.sandbox_provider != "daytona":
        raise PrerequisiteError("没有启用本机Daytona，拒绝创建资源")
    product = Path(product)
    selected = (
        json.loads((product / "selection.json").read_text(encoding="utf-8"))
        if (product / "selection.json").exists()
        else {}
    )
    validate_configuration(settings, template, selected)
    checks = checks_for(template)
    before = manifest(product)
    archive = source_archive(product)
    receipt = {
        "provider": "daytona",
        "deployment": "self-hosted-loopback",
        "api_url": local_http_url(settings.daytona_api_url, "Daytona"),
        "network_block_all": True,
        "sdk_version": version("daytona"),
        "passed": False,
        "source_digest": digest(before),
        "template": template,
        "checks": [],
        "credentials_uploaded": False,
        "cleanup": "not-created",
        "scope": "independent-runtime" if template == "python-basic" else "additional-build-checks",
    }
    name = "rnd-verify-" + uuid.uuid4().hex
    receipt["sandbox_name"] = name
    sandbox = None
    error = None
    write_json(product.parent / "daytona-verification.json", receipt)
    try:
        sandbox = client.create(params_for(settings, name), timeout=settings.tool_timeout)
        receipt.update(sandbox_id=sandbox.id, cleanup="pending")
        write_json(product.parent / "daytona-verification.json", receipt)
        sandbox.fs.create_folder(REMOTE, "700")
        sandbox.fs.upload_file(archive, REMOTE + "/source.zip", timeout=settings.tool_timeout)
        sandbox.fs.upload_file(
            (ROOT / "templates/product/verify.py").read_bytes(),
            REMOTE + "/trusted-verify.py",
            timeout=settings.tool_timeout,
        )
        extraction = sandbox.process.exec(
            "python3 -m zipfile -e " + REMOTE + "/source.zip " + REMOTE,
            timeout=settings.tool_timeout,
        )
        if extraction.exit_code != 0:
            raise PrerequisiteError("Daytona源码解压失败")
        for name, argv, relative in checks:
            result = sandbox.process.exec(
                shlex.join(argv), cwd=REMOTE + "/" + relative, timeout=settings.tool_timeout
            )
            receipt["checks"].append(
                {
                    "name": name,
                    "argv": argv,
                    "exit_code": result.exit_code,
                    "log": settings.redact(result.result or "")[:8000],
                }
            )
            if result.exit_code != 0:
                raise PrerequisiteError("Daytona检查失败：" + name)
        if template == "python-basic":
            raw = sandbox.fs.download_file(REMOTE + "/runtime.json", timeout=settings.tool_timeout)
            if len(raw) > 1_000_000:
                raise PrerequisiteError("Daytona验收报告过大")
            runtime = json.loads(raw)
            if not all(runtime.get(k) is True for k in ("passed", "http", "restart")):
                raise PrerequisiteError("Daytona运行报告缺少真实HTTP/重启验收")
            receipt["runtime"] = runtime
        if manifest(product) != before:
            raise PrerequisiteError("Daytona验收期间本机源码改变")
        receipt["passed"] = True
    except Exception as exc:
        if sandbox is None:
            # A timeout may occur after the API created the resource. Look up only
            # our unpredictable name; never delete another user's sandbox.
            receipt["cleanup"] = "create-failed-unknown"
            try:
                sandbox = client.get(name)
            except Exception:
                pass
        receipt["error_type"] = type(exc).__name__
        receipt["error_detail"] = settings.redact(str(exc))[:2000]
        receipt["passed"] = False
        error = PrerequisiteError("Daytona未通过，已保留脱敏检查回执；不会回退为本机成功")
    finally:
        if sandbox is not None:
            try:
                client.delete(sandbox, timeout=settings.tool_timeout)
                receipt["cleanup"] = "deleted"
            except Exception:
                receipt.update(cleanup="delete-failed", passed=False)
                error = PrerequisiteError(
                    "Daytona删除失败，请按sandbox_id在本机控制台清理；交付已阻止"
                )
        write_json(product.parent / "daytona-verification.json", receipt)
    if error:
        raise error
    return receipt
