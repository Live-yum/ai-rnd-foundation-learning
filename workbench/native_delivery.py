"""Explicitly authorized local native runtime delivery; source export is a separate mode."""

import json
import os
import re
import shutil
import uuid
import zipfile
from contextlib import ExitStack
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, StrictBool

from workbench.domain import digest
from workbench.filesystem import files, manifest, sha, write_json
from workbench.generator import PrerequisiteError
from workbench.native_environment import checked_database, native_environment, running_backend
from workbench.native_frontend import frontend_environment, frontend_preview
from workbench.native_lab import run_acceptance
from workbench.native_modules import validate_plan
from workbench.settings import ROOT


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    database_url_env: str
    initialize_empty_database: StrictBool = False


def runtime_path(settings, template):
    if template not in {"fastapiadmin", "yudao-vben"}:
        raise ValueError("未知原生模板")
    return settings.data_dir / "native" / f"{template}.runtime.json"


def runtime_enabled(settings, template):
    return runtime_path(settings, template).is_file()


def write_runtime_example(settings, template):
    path = runtime_path(settings, template)
    if path.exists():
        raise FileExistsError("原生运行配置已存在，拒绝覆盖")
    settings.prepare()
    prefix = "NATIVE_FASTAPIADMIN" if template == "fastapiadmin" else "NATIVE_YUDAO"
    write_json(path, RuntimeConfig(database_url_env=prefix + "_DATABASE_URL").model_dump())
    return path


def runtime_config(settings, template, *, initialize=True):
    path = runtime_path(settings, template)
    if not path.is_file():
        raise PrerequisiteError("先执行 rnd native runtime-config TEMPLATE 并授权专用空开发库")
    config = RuntimeConfig.model_validate_json(path.read_text(encoding="utf-8"))
    if not re.fullmatch(r"NATIVE_[A-Z0-9_]+", config.database_url_env):
        raise PrerequisiteError("原生数据库只能读取明确的 NATIVE_* 环境变量")
    if initialize and config.initialize_empty_database is not True:
        raise PrerequisiteError("请明确批准仅在自己创建的专用空数据库初始化原生框架")
    env = {**dotenv_values(ROOT / ".env"), **os.environ}
    url = env.get(config.database_url_env)
    if not url:
        raise PrerequisiteError("原生数据库环境变量未设置")
    checked_database(url)
    return config, url


def database_identity(url):
    """Bind a retained product to its database without storing credentials."""
    parsed = checked_database(url)
    return digest({"host": parsed.host, "port": parsed.port or 5432, "database": parsed.database})


def check_database_identity(receipt, url):
    if receipt.get("database_identity") != database_identity(url):
        raise PrerequisiteError(
            "当前原生数据库不是该产品已验证的数据库；恢复原数据库配置，不自动迁移"
        )


def prerequisites(template):
    if os.name == "nt":
        raise PrerequisiteError(
            "原生全栈运行通道请在 WSL 2/Linux 使用；默认 Python 通道支持 Windows"
        )
    commands = ["git", "uv", "node", "pnpm"] + (["java", "mvn"] if template == "yudao-vben" else [])
    for name in commands:
        if not shutil.which(name):
            raise PrerequisiteError(f"缺少原生运行工具：{name}，请按手册原生运行章节安装")
    if not (ROOT / ".native/browser/node_modules/playwright").is_dir():
        raise PrerequisiteError("尚未安装独立 Playwright/Chromium 验证工具，请按手册安装")


def managed_generate(settings, template, plan, destination):
    from workbench.native import prepare_sources

    plan = validate_plan(plan)
    destination = Path(destination).resolve()
    prerequisites(template)
    if runtime_enabled(settings, template):
        _, url = runtime_config(settings, template)
        redis_port = 6379
    else:
        from workbench.native_resources import for_run

        url, redis_port = for_run(settings, destination.parent.name)
    receipt_path = destination.parent / "native-generation.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("execution") == "managed-runtime" and receipt.get("spec_digest") == digest(
            plan.model_dump()
        ):
            check_database_identity(receipt, url)
            managed_verify(destination, receipt)
            return receipt
        raise PrerequisiteError("已有产物不能被另一份设计或执行模式覆盖")
    if destination.exists():
        raise PrerequisiteError(
            "上次原生任务未完成；保留现场，新建运行和新的专用空库，不自动删除数据"
        )
    sources = prepare_sources(settings, template)
    slots = {item["slot"]: Path(item["path"]) for item in sources}
    reports = destination.parent / "native-evidence"
    source = slots["fastapiadmin"] if template == "fastapiadmin" else slots["backend"]
    output = destination if template == "fastapiadmin" else destination / "backend"
    report = run_acceptance(
        template, source, output, slots.get("frontend"), url, reports, plan, redis_port=redis_port
    )
    if report.get("generated_runtime_verified") is not True:
        raise PrerequisiteError("原生运行验收尚未完成")
    receipt = {
        "template": template,
        "execution": "managed-runtime",
        "database_identity": database_identity(url),
        "sources": [{k: v for k, v in item.items() if k != "path"} for item in sources],
        "spec_digest": digest(plan.model_dump()),
        "files": manifest(destination),
        "validation_level": "runtime",
        "runtime_verified": True,
        "evidence_sha256": sha(reports / "acceptance.json"),
        "report": report,
    }
    write_json(receipt_path, receipt)
    return receipt


def managed_verify(destination, receipt):
    destination = Path(destination)
    report_path = destination.parent / "native-evidence/acceptance.json"
    if not report_path.is_file() or sha(report_path) != receipt.get("evidence_sha256"):
        raise PrerequisiteError("原生运行证据丢失或已改变")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    gates = (
        "generated_runtime_verified",
        "native_codegen",
        "automatic_mount",
        "menu_and_permissions",
        "real_crud",
        "restart_persistence",
        "frontend_build",
        "frontend_typecheck",
        "real_browser",
        "source_unmodified",
    )
    if any(report.get(name) is not True for name in gates):
        raise PrerequisiteError("原生运行未满足所有独立验收门槛")
    current = manifest(destination)
    if current != receipt["files"] or report.get("spec_digest") != receipt.get("spec_digest"):
        raise PrerequisiteError("原生源码或设计在验收后发生变化，需要重新验证")
    result = {
        "passed": True,
        "validation_level": "runtime",
        "runtime_verified": True,
        "production_ready": False,
        "source_digest": digest(current),
        "evidence_sha256": receipt["evidence_sha256"],
        "checks": list(gates),
        "database_delivery": "standalone-fresh-database-bootstrap"
        if report.get("portable_restored", {}).get("passed")
        else "existing-dedicated-lab-database-required",
        "startup": "uv run --no-project --python 3.14 python start.py",
    }
    write_json(destination.parent / "verification.json", result)
    return result


def managed_package(destination, report):
    destination = Path(destination)
    receipt = json.loads(
        (destination.parent / "native-generation.json").read_text(encoding="utf-8")
    )
    verified = managed_verify(destination, receipt)
    if report != verified:
        raise PrerequisiteError("交付的原生运行验证报告不匹配")
    listing = manifest(destination)
    package = destination.parent / "native-runtime.zip"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, source in files(destination):
            archive.write(source, name)
    result = {
        "package": package.name,
        "sha256": sha(package),
        "files": listing,
        "validation_level": "runtime",
        "runtime_verified": True,
        "production_ready": False,
        "database_delivery": verified["database_delivery"],
    }
    write_json(destination.parent / "delivery.json", result)
    return result


def serve_managed(settings, run_id):
    run_id = str(uuid.UUID(run_id))
    destination = settings.data_dir / "runs" / run_id / "product"
    receipt_path = destination.parent / "native-generation.json"
    if not receipt_path.is_file():
        raise PrerequisiteError("未找到此运行的原生全栈产品")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("execution") != "managed-runtime":
        raise PrerequisiteError("SOURCE_READY 源码导出不能直接作为已挂载产品启动")
    managed_verify(destination, receipt)
    template = receipt["template"]
    _, url = runtime_config(settings, template, initialize=False)
    check_database_identity(receipt, url)
    backend = destination / "backend"
    frontend = destination / ("frontend/web" if template == "fastapiadmin" else "frontend-product")
    env = native_environment(template, backend, url, 8001 if template == "fastapiadmin" else 48080)
    reports = destination.parent / "native-live"
    with ExitStack() as stack:
        base, _ = stack.enter_context(running_backend(template, backend, env, reports))
        front = stack.enter_context(
            frontend_preview(template, frontend, frontend_environment(template, base), reports)
        )
        print(f"Native backend: {base}; native frontend: {front}; Ctrl+C to stop", flush=True)
        import time

        while True:
            time.sleep(1)
