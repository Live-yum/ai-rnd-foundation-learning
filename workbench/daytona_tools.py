"""Opt-in Daytona SDK verifier. No cloud default, no key inheritance, no local fallback."""

import json
import uuid
from pathlib import Path
from urllib.parse import urlsplit

from workbench.domain import digest
from workbench.filesystem import files, manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.retrieval import allowed
from workbench.settings import ROOT


class SandboxFailure(PrerequisiteError):
    pass


def require_daytona(settings, template, database):
    if settings.sandbox_backend != "daytona":
        raise SandboxFailure("没有选择Daytona，不创建远程资源")
    if not settings.daytona_upload_authorized:
        raise SandboxFailure("未授权上传源码和创建计费沙箱：DAYTONA_UPLOAD_AUTHORIZED仍为false")
    if template != "python-basic" or database != "sqlite":
        raise SandboxFailure(
            "当前Daytona验收配置仅支持FastAPI基础模板+SQLite；原生模板保持本机完整验收"
        )
    url = urlsplit(settings.daytona_api_url)
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
    ):
        raise SandboxFailure("必须显式配置自己的HTTPS DAYTONA_API_URL，不能继承模型地址")
    if not settings.daytona_api_key.get_secret_value() or not settings.daytona_snapshot:
        raise SandboxFailure("必须独立配置DAYTONA_API_KEY及预热完成的DAYTONA_SNAPSHOT")


def sdk_client(settings):
    try:
        from daytona import Daytona, DaytonaConfig
    except ImportError:
        raise SandboxFailure("先执行 uv sync --locked --extra daytona 安装可选SDK") from None
    return Daytona(
        DaytonaConfig(
            api_key=settings.daytona_api_key.get_secret_value(),
            api_url=settings.daytona_api_url,
            target=settings.daytona_target or None,
            otel_enabled=False,
        )
    )


def sandbox_params(settings, operation):
    from daytona import CreateSandboxFromSnapshotParams

    return CreateSandboxFromSnapshotParams(
        snapshot=settings.daytona_snapshot,
        public=False,
        network_block_all=True,
        auto_stop_interval=5,
        auto_delete_interval=0,
        ttl_minutes=15,
        labels={"rnd-operation": operation},
    )


def verify_daytona(
    product, settings, attempt=0, *, client_factory=sdk_client, params_factory=sandbox_params
):
    """Run the trusted real HTTP/restart harness in a fresh, private, offline snapshot."""
    product = Path(product)
    selection = json.loads((product / "selection.json").read_text(encoding="utf-8"))
    require_daytona(settings, selection["template"], selection["database"])
    current = manifest(product)
    rows = list(files(product))
    if any(not allowed(n) for n, _ in rows) or sum(p.stat().st_size for _, p in rows) > 20_000_000:
        raise SandboxFailure("源码包含不允许上传的工具配置或超过20MB，拒绝上传")
    operation = uuid.uuid4().hex
    evidence_path = product.parent / f"daytona-{attempt}.json"
    evidence = {
        "engine": "daytona-sdk",
        "profile": "python-basic-sqlite-offline-v1",
        "operation": operation,
        "source_digest": digest(current),
        "passed": False,
        "executed": False,
        "cleanup_confirmed": False,
        "snapshot": settings.daytona_snapshot,
        "uploaded_files": sorted(current),
    }
    write_json(evidence_path, evidence)
    client, sandbox = None, None
    failure = None
    try:
        client = client_factory(settings)
        sandbox = client.create(params_factory(settings, operation), timeout=90)
        evidence["sandbox_id"] = sandbox.id
        write_json(evidence_path, evidence)
        root = "/tmp/rnd-" + operation
        destination = root + "/product"
        parents = {
            parent.as_posix()
            for name, _ in rows
            for parent in Path(name).parents
            if parent != Path(".")
        }
        for folder in [
            root,
            destination,
            *[
                destination + "/" + parent
                for parent in sorted(parents, key=lambda p: (p.count("/"), p))
            ],
        ]:
            sandbox.fs.create_folder(folder, "700", request_timeout=30)
        for name, path in rows:
            sandbox.fs.upload_file(path.read_bytes(), destination + "/" + name, timeout=30)
        # Trusted verifier is supplied by the platform, outside editable product files.
        sandbox.fs.upload_file(
            (ROOT / "templates/product/verify.py").read_bytes(),
            root + "/trusted_verify.py",
            timeout=30,
        )
        commands = [
            ("offline_dependencies", "uv sync --locked --offline --no-dev --python 3.14"),
            (
                "http_restart",
                f".venv/bin/python {root}/trusted_verify.py --product {destination} --python {destination}/.venv/bin/python --report {root}/report.json",
            ),
        ]
        evidence["commands"] = []
        for label, command in commands:
            result = sandbox.process.exec(command, cwd=destination, timeout=settings.tool_timeout)
            evidence["commands"].append({"check": label, "exit_code": result.exit_code})
            if result.exit_code != 0:
                raise SandboxFailure("Daytona内固定验收命令失败：" + label)
        # Streaming limit is enforced before accumulating an untrusted remote report.
        chunks, size = [], 0
        for chunk in sandbox.fs.download_file_stream(root + "/report.json", timeout=30):
            size += len(chunk)
            if size > 64000:
                raise SandboxFailure("Daytona验收报告超过64KB")
            chunks.append(chunk)
        report = json.loads(b"".join(chunks))
        if any(report.get(k) is not True for k in ("passed", "http", "restart")):
            raise SandboxFailure("Daytona未通过真实HTTP或重启持久化验收")
        if manifest(product) != current:
            raise SandboxFailure("远程验收期间本机源代码已变化")
        evidence.update(executed=True, report=report)
    except Exception as exc:
        # SDK errors may echo authentication or connection details; keep only safe diagnostics.
        failure = (
            str(exc)
            if isinstance(exc, SandboxFailure)
            else "Daytona工具失败：" + type(exc).__name__
        )
    finally:
        if client is not None and sandbox is not None:
            try:
                client.delete(sandbox, timeout=60, wait=True)
                evidence["cleanup_confirmed"] = True
            except Exception:
                failure = "沙箱删除未获确认；禁止READY。根据回执sandbox_id检查并清理资源"
        if sandbox is None:
            evidence["cleanup_note"] = (
                "未获取沙箱ID；创建超时可能需要按rnd-operation标签查找，15分钟TTL是兜底而非删除证据"
            )
        evidence["passed"] = bool(
            evidence["executed"] and evidence["cleanup_confirmed"] and not failure
        )
        if failure:
            evidence["error"] = failure
        write_json(evidence_path, evidence)
    if not evidence["passed"]:
        raise SandboxFailure(failure or "Daytona验收未完成，保留回执但禁止交付")
    return evidence
