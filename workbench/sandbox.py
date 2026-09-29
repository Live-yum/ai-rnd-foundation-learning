"""Opt-in Daytona verification. Credentials stay on the control plane.

Local trusted acceptance is never skipped. A remote build is additional evidence,
not a substitute for database, RBAC, browser or clean-delivery acceptance.
"""

import io
import json
import shlex
import zipfile
from importlib.metadata import version
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.settings import ModelProfile, ROOT

REMOTE = "/tmp/rnd-verification"


def validate_configuration(settings, template, selection=None):
    if settings.sandbox_provider != "daytona":
        return
    if not settings.daytona_allow_upload:
        raise PrerequisiteError("Daytona需要明确配置 DAYTONA_ALLOW_UPLOAD=true；不会默认上传项目或产生云端费用")
    ModelProfile(stage="daytona", base_url=settings.daytona_api_url, model="sandbox",
                 api_key=settings.daytona_api_key).validate_endpoint()
    if not settings.daytona_snapshot or not settings.daytona_target:
        raise PrerequisiteError("请配置已安装构建工具的 DAYTONA_SNAPSHOT 和 DAYTONA_TARGET")
    if template == "python-basic" and (selection or {}).get("database", "sqlite") != "sqlite":
        raise PrerequisiteError("Daytona的Python运行复验当前只支持独立SQLite；不会把本机PostgreSQL凭据上传云端")


def client_for(settings):
    from daytona import Daytona, DaytonaConfig

    return Daytona(DaytonaConfig(api_key=settings.daytona_api_key.get_secret_value(),
                                 api_url=settings.daytona_api_url,
                                 target=settings.daytona_target))


def params_for(settings):
    from daytona import CreateSandboxFromSnapshotParams

    return CreateSandboxFromSnapshotParams(
        snapshot=settings.daytona_snapshot, public=False,
        auto_stop_interval=5, auto_delete_interval=0,
        env_vars={"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        labels={"managed-by": "rnd-toolchain", "purpose": "disposable-verification"},
    )


def checks_for(template):
    if template == "python-basic":
        return [
            ("locked-install", ["uv", "sync", "--locked", "--no-dev", "--python", "3.14"], "product"),
            ("migration-http-crud-restart", ["./.venv/bin/python", "../trusted-verify.py",
             "--product", ".", "--python", "./.venv/bin/python", "--report", "../runtime.json"], "product"),
        ]
    if template == "yudao-vben":
        return [
            ("maven-test", ["mvn", "-B", "test"], "product/backend"),
            ("frontend-install", ["pnpm", "install", "--frozen-lockfile"], "product/frontend-product"),
            ("frontend-types", ["pnpm", "--dir", "apps/web-antd", "exec", "vue-tsc", "--noEmit", "--skipLibCheck"], "product/frontend-product"),
        ]
    if template == "fastapiadmin":
        return [
            ("python-syntax", ["python3", "-m", "compileall", "-q", "app"], "product/backend"),
            ("frontend-install", ["pnpm", "install", "--frozen-lockfile"], "product/frontend/web"),
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
    if settings.sandbox_provider != "daytona":
        raise PrerequisiteError("没有启用Daytona，拒绝创建远程资源")
    product = Path(product)
    selected = json.loads((product / "selection.json").read_text(encoding="utf-8")) if (product / "selection.json").exists() else {}
    validate_configuration(settings, template, selected)
    checks = checks_for(template)
    before = manifest(product)
    archive = source_archive(product)
    receipt = {"provider": "daytona", "sdk_version": version("daytona"), "passed": False,
               "source_digest": digest(before), "template": template, "checks": [],
               "credentials_uploaded": False, "cleanup": "not-created",
               "scope": "independent-runtime" if template == "python-basic" else "additional-build-checks"}
    owned = client is None
    client = client or client_for(settings)
    sandbox = None
    error = None
    try:
        sandbox = client.create(params_for(settings), timeout=settings.tool_timeout)
        receipt.update(sandbox_id=sandbox.id, cleanup="pending")
        sandbox.fs.create_folder(REMOTE, "700")
        sandbox.fs.upload_file(archive, REMOTE + "/source.zip", timeout=settings.tool_timeout)
        sandbox.fs.upload_file((ROOT / "templates/product/verify.py").read_bytes(),
                               REMOTE + "/trusted-verify.py", timeout=settings.tool_timeout)
        extraction = sandbox.process.exec("python3 -m zipfile -e " + REMOTE + "/source.zip " + REMOTE,
                                           timeout=settings.tool_timeout)
        if extraction.exit_code != 0:
            raise PrerequisiteError("Daytona源码解压失败")
        for name, argv, relative in checks:
            result = sandbox.process.exec(shlex.join(argv), cwd=REMOTE + "/" + relative,
                                           timeout=settings.tool_timeout)
            receipt["checks"].append({"name": name, "argv": argv, "exit_code": result.exit_code,
                                      "log": settings.redact(result.result or "")[:8000]})
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
        receipt["error_type"] = type(exc).__name__
        error = PrerequisiteError("Daytona未通过，已保留脱敏检查回执；不会回退为本机成功")
    finally:
        if sandbox is not None:
            try:
                client.delete(sandbox, timeout=settings.tool_timeout)
                receipt["cleanup"] = "deleted"
            except Exception:
                receipt.update(cleanup="delete-failed", passed=False)
                error = PrerequisiteError("Daytona删除失败，请按sandbox_id在控制台清理；交付已阻止")
        if owned and hasattr(client, "close"):
            try:
                client.close()
            except Exception:
                receipt["client_close"] = "failed"
        write_json(product.parent / "daytona-verification.json", receipt)
    if error:
        raise error
    return receipt
