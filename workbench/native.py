"""Pinned upstream sources + their real HTTP code generators.

Native exports are SOURCE_READY, never runtime-verified just because a ZIP exists.
Only dedicated *_codegen databases may be used for metadata generation.
"""

import ast
import json
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit

import httpx
from dotenv import dotenv_values
from filelock import FileLock
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    inspect,
)
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateTable

from workbench.domain import digest
from workbench.filesystem import atomic_text, files, inside, manifest, sha, unpack, write_json
from workbench.generator import PrerequisiteError
from workbench.knowledge import build_index
from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command

SOURCES = {
    "fastapiadmin": [
        {
            "slot": "fastapiadmin",
            "sha": "1cd12c726ad9032c17ef85ce805ce991be60fbdf",
            "urls": ["https://github.com/fastapiadmin/FastapiAdmin.git"],
            "required": [
                "backend/pyproject.toml",
                "backend/app/modules/generator/gencode/controller.py",
                "LICENSE",
            ],
        }
    ],
    "yudao-vben": [
        {
            "slot": "backend",
            "sha": "47f8f6cfabc5017a8eac4654c7ba4c14aaa6a7be",
            "urls": [
                "https://gitee.com/yudaocode/yudao-cloud-mini.git",
                "https://github.com/yudaocode/yudao-cloud-mini.git",
            ],
            "required": ["pom.xml", "yudao-module-infra", "LICENSE"],
        },
        {
            "slot": "frontend",
            "sha": "1b14e889f529e245fd620daa720dcea6de0cc5e7",
            "urls": [
                "https://gitee.com/yudaocode/yudao-ui-admin-vben.git",
                "https://github.com/yudaocode/yudao-ui-admin-vben.git",
            ],
            "required": ["package.json", "pnpm-lock.yaml", "LICENSE"],
        },
    ],
}


class NativeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    base_url: str
    openapi_path: str
    token_env: str
    database_url_env: str
    allow_create_tables: bool = False
    data_source_config_id: int = Field(default=1, ge=1)
    front_type: int = 40
    tenant_id: str = "1"


def catalog(settings):
    result = [
        {
            "id": "python-basic",
            "level": "runtime",
            "requires": ["Python 3.14", "uv"],
            "capabilities": ["typed-crud", "per-user-isolation", "bounded-record-validation"],
            "not_supported": [
                "relations",
                "shared-data",
                "business-rbac",
                "cross-table-transactions",
            ],
        }
    ]
    for name, sources in SOURCES.items():
        managed = (settings.data_dir / "native" / f"{name}.runtime.json").is_file()
        result.append(
            {
                "id": name,
                "level": "managed-runtime" if managed else "native-source-export",
                "sources": sources,
                "configured": managed or (settings.data_dir / "native" / f"{name}.json").exists(),
                "configuration_is_not_acceptance": True,
                "requires": [
                    "git",
                    "native server",
                    "native admin token",
                    "dedicated codegen database",
                ],
                "runtime_verified": False,
            }
        )
    return result


def write_config_example(settings, template):
    if template not in SOURCES:
        raise ValueError("未知原生模板")
    settings.prepare()
    path = settings.data_dir / "native" / f"{template}.json"
    if path.exists():
        raise FileExistsError("原生配置已存在，不覆盖")
    prefix = "NATIVE_FASTAPIADMIN" if template == "fastapiadmin" else "NATIVE_YUDAO"
    write_json(
        path,
        {
            "base_url": "http://127.0.0.1:8001"
            if template == "fastapiadmin"
            else "http://127.0.0.1:48080",
            "openapi_path": "/openapi.json" if template == "fastapiadmin" else "/v3/api-docs",
            "token_env": prefix + "_TOKEN",
            "database_url_env": prefix + "_DATABASE_URL",
            "allow_create_tables": False,
            "data_source_config_id": 1,
            "front_type": 40,
            "tenant_id": "1",
        },
    )
    return path


def load_config(settings, template):
    path = settings.data_dir / "native" / f"{template}.json"
    if template not in SOURCES or not path.exists():
        raise PrerequisiteError("先执行 rnd native config-example TEMPLATE 并配置原生服务")
    config = NativeConfig.model_validate_json(path.read_text(encoding="utf-8"))
    url = urlsplit(config.base_url)
    if (
        url.scheme not in {"http", "https"}
        or url.hostname not in {"127.0.0.1", "localhost", "::1"}
        or url.username
        or url.query
        or url.fragment
    ):
        raise PrerequisiteError("原生生成器只允许本机服务地址")
    if not config.openapi_path.startswith("/") or config.openapi_path.startswith("//"):
        raise PrerequisiteError("OpenAPI 必须是本机相对路径")
    env = {**dotenv_values(ROOT / ".env"), **os.environ}
    for key in (config.token_env, config.database_url_env):
        if not re.fullmatch(r"NATIVE_[A-Z0-9_]+", key) or not env.get(key):
            raise PrerequisiteError("原生服务的 NATIVE_* 环境变量未配置")
    if not config.allow_create_tables:
        raise PrerequisiteError("尚未明确允许在专用 codegen 数据库创建表")
    if template == "yudao-vben" and config.front_type not in {40, 41}:
        raise PrerequisiteError("当前固定前端使用 Vben5 Ant Design Vue，front_type 只能为 40 或 41")
    return config, SecretStr(env[config.token_env]), SecretStr(env[config.database_url_env])


def prepare_sources(settings, template, prefer_github=False):
    if template not in SOURCES:
        raise PrerequisiteError("未知原生模板")
    settings.prepare()
    receipts = []
    with FileLock(str(settings.data_dir / "sources" / f"{template}.lock"), timeout=30):
        for entry in SOURCES[template]:
            path = settings.data_dir / "sources" / template / entry["slot"] / entry["sha"]
            path.parent.mkdir(parents=True, exist_ok=True)
            used_url = None
            if not (path / ".git").exists():
                for url in sorted(
                    entry["urls"], key=lambda u: prefer_github and "github.com" not in u
                ):
                    if path.exists():
                        shutil.rmtree(path)
                    path.mkdir()
                    try:
                        run_command(["git", "init", "--quiet"], path)
                        run_command(
                            ["git", "fetch", "--depth", "1", url, entry["sha"]],
                            path,
                            settings.tool_timeout,
                            {"GIT_TERMINAL_PROMPT": "0"},
                        )
                        run_command(["git", "checkout", "--detach", "FETCH_HEAD"], path)
                        used_url = url
                        break
                    except ToolFailure:
                        continue
                if used_url is None:
                    shutil.rmtree(path)
                    raise PrerequisiteError("无法取得已锁定的原生模板提交；未改用未知版本")
            head = run_command(["git", "rev-parse", "HEAD"], path)["log"].strip()
            dirty = run_command(["git", "status", "--porcelain"], path)["log"].strip()
            if head != entry["sha"] or dirty:
                raise PrerequisiteError("模板源码提交不匹配或已被修改；请保留原目录并重新准备")
            for required in entry["required"]:
                if not inside(path, required).exists():
                    raise PrerequisiteError("固定模板缺少必要源码路径")
            record_path = path.parent / (entry["sha"] + ".json")
            if used_url is None and record_path.exists():
                used_url = json.loads(record_path.read_text(encoding="utf-8")).get("url")
            record = {
                "template": template,
                "slot": entry["slot"],
                "sha": head,
                "url": used_url,
                "path": str(path),
                "dirty": False,
            }
            write_json(record_path, record)
            build_index(
                path, settings.data_dir / "knowledge" / template / entry["slot"] / head, head
            )
            receipts.append(record)
    return receipts


def create_codegen_tables(plan, url, run_id):
    parsed = make_url(url)
    if parsed.get_backend_name() not in {"sqlite", "postgresql"}:
        raise PrerequisiteError("自动 codegen 建表只支持 SQLite/PostgreSQL 专用数据库")
    if parsed.get_backend_name() == "sqlite":
        if (
            not (parsed.database or "").endswith("-codegen.db")
            or not Path(parsed.database).is_absolute()
        ):
            raise PrerequisiteError("SQLite 原生生成库必须是绝对路径并以 -codegen.db 结尾")
    elif not (parsed.database or "").endswith("_codegen") or parsed.host not in {
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise PrerequisiteError("PostgreSQL 原生生成库必须位于本机且名称以 _codegen 结尾")
    engine = create_engine(url)
    try:
        metadata = MetaData()
        mapping = {}
        prefix = "wb_" + digest(run_id)[:8] + "_"
        for entity in plan.entities:
            name = prefix + entity.name
            columns = [
                Column(
                    "id",
                    BigInteger().with_variant(Integer, "sqlite"),
                    primary_key=True,
                    autoincrement=True,
                )
            ]
            for field in entity.fields:
                kind = {
                    "text": String(field.max_length),
                    "integer": Integer(),
                    "boolean": Boolean(),
                }[field.kind]
                columns.append(
                    Column(field.name, kind, nullable=not field.required, comment=field.name)
                )
            Table(name, metadata, *columns, comment=entity.description[:200])
            mapping[entity.name] = name
        with engine.begin() as connection:
            inspector = inspect(connection)
            for table in metadata.tables.values():
                if inspector.has_table(table.name):
                    actual = {c["name"] for c in inspector.get_columns(table.name)}
                    if actual != set(table.c.keys()):
                        raise PrerequisiteError("已有 codegen 表结构与批准规格不同，拒绝覆盖")
            metadata.create_all(connection)
        ddl = "\n".join(
            str(CreateTable(t).compile(dialect=engine.dialect)) + ";"
            for t in metadata.sorted_tables
        )
        return mapping, ddl
    finally:
        engine.dispose()


class NativeClient:
    def __init__(self, config, token, transport=None):
        self.config = config
        self.client = httpx.Client(
            base_url=config.base_url,
            timeout=60,
            follow_redirects=False,
            trust_env=False,
            transport=transport,
            headers={"Authorization": "Bearer " + token, "tenant-id": config.tenant_id},
        )
        self.paths = self._read("GET", config.openapi_path).json()["paths"]

    def _read(self, method, path, **kwargs):
        with self.client.stream(method, path, **kwargs) as response:
            if response.status_code >= 300:
                raise PrerequisiteError(f"原生生成器 HTTP {response.status_code}，请核对登录与权限")
            payload = bytearray()
            for chunk in response.iter_bytes():
                payload.extend(chunk)
                if len(payload) > 30_000_000:
                    raise PrerequisiteError("原生生成器响应超过 30 MB 限制")
            return httpx.Response(
                response.status_code,
                headers={
                    k: v
                    for k, v in response.headers.items()
                    if k.lower() not in {"content-encoding", "content-length", "transfer-encoding"}
                },
                content=bytes(payload),
                request=response.request,
            )

    def endpoint(self, suffix, method):
        matches = [
            p
            for p, operations in self.paths.items()
            if p.endswith(suffix) and method.lower() in operations
        ]
        if len(matches) != 1:
            raise PrerequisiteError("OpenAPI 无法唯一定位原生生成器操作：" + suffix)
        return matches[0]

    def request(self, method, suffix, replace=None, **kwargs):
        path = self.endpoint(suffix, method)
        for name, value in (replace or {}).items():
            path = path.replace("{" + name + "}", str(value))
        return self._read(method, path, **kwargs)

    @staticmethod
    def payload(response):
        value = response.json()
        if value.get("code", 200) not in {0, 200}:
            raise PrerequisiteError(
                f"原生生成器拒绝请求 (code={value.get('code')})；未公开含凭据的上游响应"
            )
        return value.get("data", value)

    def close(self):
        self.client.close()


def native_export(client, template, mapping, plan):
    """Invoke the upstream's import/update/download APIs, returning actual ZIP bytes."""
    tables = list(mapping.values())
    exports = []
    if template == "fastapiadmin":
        page = client.payload(
            client.request(
                "GET",
                "/gencode/list",
                params={"table_name": tables[0].split("_")[1], "page_size": 100},
            )
        )
        rows = page.get("items", page.get("list", [])) if isinstance(page, dict) else page
        known = {row["table_name"]: row for row in rows}
        missing = [t for t in tables if t not in known]
        if missing:
            client.payload(client.request("POST", "/gencode/import", json=missing))
        page = client.payload(
            client.request(
                "GET",
                "/gencode/list",
                params={"table_name": tables[0].split("_")[1], "page_size": 100},
            )
        )
        rows = page.get("items", page.get("list", [])) if isinstance(page, dict) else page
        known = {row["table_name"]: row for row in rows}
        for entity in plan.entities:
            row = known.get(mapping[entity.name])
            if not row:
                raise PrerequisiteError("原生生成器没有导入预期业务表")
            table_id = row["id"]
            detail = client.payload(
                client.request("GET", "/gencode/detail/{table_id}", replace={"table_id": table_id})
            )
            fields = {c["column_name"] for c in detail.get("columns", [])}
            if not {f.name for f in entity.fields}.issubset(fields):
                raise PrerequisiteError("原生生成器字段与批准规格不同")
            update = {k: detail[k] for k in ("table_name", "columns")}
            update.update(
                module_name=entity.name,
                package_name="module_rnd",
                business_name=entity.name,
                class_name="".join(p.title() for p in entity.name.split("_")),
                function_name=entity.description[:200],
                table_comment=entity.description[:200],
            )
            client.payload(
                client.request(
                    "PUT", "/gencode/update/{table_id}", replace={"table_id": table_id}, json=update
                )
            )
        response = client.request("PATCH", "/gencode/batch/output", json=tables)
        if response.headers.get("X-Skipped-Tables"):
            raise PrerequisiteError("原生生成器跳过了部分表，不接受部分成功")
        exports.append(("fastapiadmin", response.content))
    else:
        rows = client.payload(
            client.request(
                "GET",
                "/infra/codegen/table/list",
                params={"dataSourceConfigId": client.config.data_source_config_id},
            )
        )
        known = {row["tableName"]: row["id"] for row in rows}
        missing = [t for t in tables if t not in known]
        if missing:
            ids = client.payload(
                client.request(
                    "POST",
                    "/infra/codegen/create-list",
                    json={
                        "dataSourceConfigId": client.config.data_source_config_id,
                        "tableNames": missing,
                    },
                )
            )
            if len(ids) != len(missing):
                raise PrerequisiteError("芋道没有导入全部表")
            known.update(zip(missing, ids, strict=True))
        for entity in plan.entities:
            table_id = known[mapping[entity.name]]
            detail = client.payload(
                client.request("GET", "/infra/codegen/detail", params={"tableId": table_id})
            )
            detail["table"]["frontType"] = client.config.front_type
            if not {f.name for f in entity.fields}.issubset(
                {c["columnName"] for c in detail["columns"]}
            ):
                raise PrerequisiteError("芋道生成字段与批准规格不一致")
            client.payload(
                client.request(
                    "PUT",
                    "/infra/codegen/update",
                    json={"table": detail["table"], "columns": detail["columns"]},
                )
            )
            response = client.request(
                "GET", "/infra/codegen/download", params={"tableId": table_id}
            )
            exports.append((entity.name, response.content))
    return exports


def generate_native(settings, template, plan, destination):
    from workbench.native_delivery import managed_generate, runtime_enabled

    if runtime_enabled(settings, template):
        return managed_generate(settings, template, plan, destination)
    config, token, db_url = load_config(settings, template)
    if plan.custom_rules or plan.unsupported:
        raise PrerequisiteError("原生源码导出不接受未实现的定制规则")
    sources = prepare_sources(settings, template)
    mapping, ddl = create_codegen_tables(plan, db_url.get_secret_value(), destination.parent.name)
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "approved-spec.json", plan.model_dump())
    atomic_text(destination / "business-schema.sql", ddl)
    client = NativeClient(config, token.get_secret_value())
    try:
        exports = native_export(client, template, mapping, plan)
    finally:
        client.close()
    for name, data in exports:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "source.zip"
            archive.write_bytes(data)
            unpack(archive, destination / "generated" / name)
    for source in sources:
        target = destination / "upstream" / source["slot"]
        for name, path in files(source["path"]):
            output = inside(target, name)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, output)
    atomic_text(
        destination / "INTEGRATION.md",
        "# 原生生成器源码导出\n\n"
        "upstream/ 是锁定的上游源码；generated/ 是原生生成器真实输出，未自动覆盖到上游。\n"
        "先按原生生成器说明检查目录映射、鉴权、菜单和迁移，在开发分支合入，再执行框架原生测试。\n"
        "本包不声称经过完整启动验收，不等于任意业务需求已完成，也不自动部署。\n",
    )
    receipt = {
        "template": template,
        "sources": [{k: v for k, v in s.items() if k != "path"} for s in sources],
        "tables": mapping,
        "spec_digest": digest(plan.model_dump()),
        "files": manifest(destination),
        "validation_level": "source",
        "runtime_verified": False,
    }
    write_json(destination.parent / "native-generation.json", receipt)
    return receipt


def verify_native(destination):
    receipt = json.loads(
        (destination.parent / "native-generation.json").read_text(encoding="utf-8")
    )
    if receipt.get("execution") == "managed-runtime":
        from workbench.native_delivery import managed_verify

        return managed_verify(destination, receipt)
    current = manifest(destination)
    if current != receipt["files"] or not any(p.startswith("generated/") for p in current):
        raise PrerequisiteError("原生生成产物不完整或已被修改")
    for name, path in files(destination / "generated"):
        if name.endswith(".py"):
            ast.parse(path.read_text(encoding="utf-8"))
    result = {
        "passed": True,
        "source_digest": digest(current),
        "validation_level": "source",
        "runtime_verified": False,
        "checks": ["source-manifest", "archive-safety", "generated-python-syntax"],
    }
    write_json(destination.parent / "verification.json", result)
    return result


def package_native(destination, report):
    if report.get("validation_level") == "runtime":
        from workbench.native_delivery import managed_package

        return managed_package(destination, report)
    listing = manifest(destination)
    if report.get("passed") is not True or digest(listing) != report["source_digest"]:
        raise PrerequisiteError("原生源码包在验证后发生变化")
    path = destination.parent / "native-source.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, source in files(destination):
            z.write(source, name)
    result = {
        "package": path.name,
        "sha256": sha(path),
        "files": listing,
        "validation_level": "source",
        "runtime_verified": False,
        "production_ready": False,
    }
    write_json(destination.parent / "delivery.json", result)
    return result
