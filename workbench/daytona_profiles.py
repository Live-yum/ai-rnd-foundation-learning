"""Exact supported sandbox matrix and dependency identity; no cloud fallback."""

import json
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, sha

MATRIX = {"python-basic": {"sqlite", "postgresql"}, "fastapiadmin": {"postgresql"}, "yudao-vben": {"postgresql"}}


def selection_for(product, template):
    root = Path(product)
    if template == "python-basic":
        return json.loads((root / "selection.json").read_text(encoding="utf-8"))
    return {"template": template, "database": "postgresql"}


def profile_key(template, selection=None):
    database = (selection or {}).get("database", "sqlite" if template == "python-basic" else "postgresql")
    if database not in MATRIX.get(template, set()):
        raise ValueError("No registered Daytona template/database acceptance profile")
    return template + "/" + database


def snapshot_for(settings, template, selection=None):
    return settings.daytona_snapshots.get(profile_key(template, selection), settings.daytona_snapshot)


def dependency_identity(product):
    locks = {name: sha(path) for name, path in files(product) if path.name in {"pyproject.toml", "uv.lock", "pnpm-lock.yaml", "package.json", "pom.xml"}}
    if not locks:
        raise ValueError("Sandbox input has no dependency lock identity")
    return digest(locks)


def require_runtime_report(report, template, selection, source_digest):
    database = selection["database"]
    required = ["passed", "http", "restart", "fresh_database", "locked_install", "offline", "services_stopped"]
    if template != "python-basic":
        required += ["frontend_build", "frontend_typecheck", "browser", "permissions", "standalone_launcher", "business_rules"]
    if not isinstance(report, dict) or any(report.get(key) is not True for key in required):
        raise ValueError("Daytona缺少完整的独立数据库/运行/浏览器验收证据")
    if report.get("template") != template or report.get("database") != database or report.get("source_digest") != source_digest:
        raise ValueError("Daytona运行报告与当前源码或技术栈不匹配")
    if report.get("host_credentials_used") is not False or report.get("host_database_used") is not False:
        raise ValueError("Daytona不能复用主机数据库或凭据")
