"""Opt-in self-hosted Daytona verification. No cloud control plane is allowed.

Local trusted acceptance is never skipped. A sandbox build is additional evidence,
not a substitute for database, RBAC, browser or clean-delivery acceptance.
"""

import io
import json
import shlex
import uuid
import zipfile
from contextlib import closing
from importlib.metadata import version
from pathlib import Path

from workbench.daytona_profiles import (
    profile_key,
    require_runtime_report,
    selection_for,
    snapshot_for,
)
from workbench.domain import digest
from workbench.filesystem import files, manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.local_only import DAYTONA_VERSION, local_http_url
from workbench.settings import ROOT, ModelProfile

REMOTE = "/tmp/rnd-verification"
MAX_RUNTIME_REPORT_BYTES = 1_000_000


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
    try:
        profile_key(template, selection)
    except ValueError as exc:
        raise PrerequisiteError(str(exc)) from exc
    if not snapshot_for(settings, template, selection) or not settings.daytona_target:
        raise PrerequisiteError("请配置当前技术栈的离线DAYTONA_SNAPSHOT或DAYTONA_SNAPSHOTS映射")


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
    """Release the exact v0.190.0 HTTPX client and urllib3 connection pools.

    Neither Daytona nor its generated ApiClient exposes close(); ApiClient's
    context-manager exit is also a no-op. The synchronous worker is quiescent
    here. Close every owned pool before clearing it, even when external Python
    references would otherwise delay garbage collection. Sandbox deletion is
    separate and must have been verified before this transport cleanup.
    """
    import sys

    original = sys.exception()
    failures = []

    def attempt(operation):
        try:
            operation()
        except Exception as exc:
            failures.append(type(exc).__name__)

    http = getattr(client, "_http_client", None)
    if http is not None:
        attempt(http.close)
    for name in ("_api_client", "_toolbox_api_client"):
        api = getattr(client, name, None)
        if api is None:
            continue
        try:
            manager = api.rest_client.pool_manager
            with manager.pools.lock:
                for key in manager.pools.keys():
                    attempt(manager.pools[key].close)
                attempt(manager.clear)
        except Exception as exc:
            failures.append(type(exc).__name__)
    if failures:
        message = "本机Daytona传输资源关闭失败：" + ", ".join(failures)
        if original is not None:
            original.add_note(message)
        else:
            raise PrerequisiteError(message)


def params_for(settings, name=None, template="python-basic", selection=None):
    from daytona import CreateSandboxFromSnapshotParams

    return CreateSandboxFromSnapshotParams(
        snapshot=snapshot_for(settings, template, selection),
        name=name,
        network_block_all=True,
        public=False,
        auto_stop_interval=5
        if profile_key(template, selection) == "python-basic/sqlite"
        else settings.daytona_runtime_timeout // 60 + 5,
        auto_delete_interval=0,
        env_vars={"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"},
        labels={"managed-by": "rnd-toolchain", "purpose": "disposable-verification"},
    )


def checks_for(template, selection=None):
    try:
        key = profile_key(template, selection)
    except ValueError as exc:
        raise PrerequisiteError(str(exc)) from exc
    if key == "python-basic/sqlite":
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
    return [
        (
            "independent-database-build-http-browser-restart",
            [
                "env",
                "PYTHONPATH=" + REMOTE + "/harness",
                "/opt/rnd/harness/.venv/bin/python",
                REMOTE + "/harness/scripts/daytona_matrix_probe.py",
                "--template",
                template,
                "--database",
                key.split("/")[1],
            ],
            "product",
        )
    ]


def harness_archive():
    """Only trusted, committed verifier code; never user files, keys or host caches."""
    names = [path.relative_to(ROOT).as_posix() for path in (ROOT / "workbench").glob("*.py")]
    names += [
        "scripts/daytona_matrix_probe.py",
        "scripts/native_browser.cjs",
        "templates/product/verify.py",
    ]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):
            archive.writestr("harness/" + name, (ROOT / name).read_bytes())
    return buffer.getvalue()


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


def read_runtime_report(filesystem, timeout):
    """Read the pinned SDK's real streaming API with a bounded body and deadline.

    In 0.190.0 download_file advertises timeout as a keyword in its overloads,
    but the actual implementation accepts only *args. The streaming method
    really accepts timeout= and lets us enforce the size limit before buffering
    the entire report. Closing the iterator also closes the HTTP response on
    malformed, oversized or interrupted downloads.
    """
    body = bytearray()
    with closing(
        filesystem.download_file_stream(REMOTE + "/runtime.json", timeout=timeout)
    ) as chunks:
        for chunk in chunks:
            if not isinstance(chunk, bytes):
                raise PrerequisiteError("Daytona验收报告不是字节流")
            if len(body) + len(chunk) > MAX_RUNTIME_REPORT_BYTES:
                raise PrerequisiteError("Daytona验收报告过大")
            body.extend(chunk)
    try:
        runtime = json.loads(body)
    except (ValueError, UnicodeError) as exc:
        raise PrerequisiteError("Daytona验收报告不是有效JSON") from exc
    if not isinstance(runtime, dict) or not all(
        runtime.get(key) is True for key in ("passed", "http", "restart")
    ):
        raise PrerequisiteError("Daytona运行报告缺少真实HTTP/重启验收")
    return runtime


def verify_in_daytona(product, template, settings, *, client=None):
    validate_configuration(settings, template, selection_for(product, template))
    if client is None:
        from workbench.daytona_worker import run_isolated

        return run_isolated(product, template, settings)
    return _verify_in_daytona(product, template, settings, client=client)


def _verify_in_daytona(product, template, settings, *, client):
    if settings.sandbox_provider != "daytona":
        raise PrerequisiteError("没有启用本机Daytona，拒绝创建资源")
    product = Path(product)
    selected = selection_for(product, template)
    validate_configuration(settings, template, selected)
    key = profile_key(template, selected)
    checks = checks_for(template, selected)
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
        "scope": "independent-runtime",
        "database": selected["database"],
        "snapshot": snapshot_for(settings, template, selected),
    }
    name = "rnd-verify-" + uuid.uuid4().hex
    receipt["sandbox_name"] = name
    sandbox = None
    error = None
    write_json(product.parent / "daytona-verification.json", receipt)
    try:
        sandbox = client.create(
            params_for(settings, name, template, selected), timeout=settings.tool_timeout
        )
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
        if key != "python-basic/sqlite":
            sandbox.fs.upload_file(
                harness_archive(), REMOTE + "/harness.zip", timeout=settings.tool_timeout
            )
            unpack = sandbox.process.exec(
                "python3 -m zipfile -e " + REMOTE + "/harness.zip " + REMOTE,
                timeout=settings.tool_timeout,
            )
            if unpack.exit_code != 0:
                raise PrerequisiteError("Daytona可信验收器解压失败")
        for name, argv, relative in checks:
            result = sandbox.process.exec(
                shlex.join(argv),
                cwd=REMOTE + "/" + relative,
                timeout=settings.daytona_runtime_timeout
                if key != "python-basic/sqlite"
                else settings.tool_timeout,
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
        receipt["runtime"] = read_runtime_report(sandbox.fs, settings.tool_timeout)
        if key != "python-basic/sqlite":
            require_runtime_report(receipt["runtime"], template, selected, digest(before))
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
