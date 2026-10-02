"""Custom source runs only in a private, network-blocked local Daytona sandbox.

The HTTP verifier remains in the controller process, outside generated code's
filesystem/process namespace. A product-authored JSON report cannot pass a task.
"""

import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import httpx

from workbench.capability_contracts import CapabilityPlan
from workbench.capability_isolation import (
    IsolationUnavailable,
    control_exec,
    prepare_identity,
    product_argv,
    read_command_output,
    redirected_command,
)
from workbench.capability_stack import (
    database_counts,
    database_environment,
    inspect_stack,
    prepare_database,
)
from workbench.capability_verification import CheckFailure, preview_url, run_browser, run_scenarios
from workbench.domain import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.local_only import install_loopback_guard
from workbench.tools import clean_env, process_options, stop_process

REMOTE = "/tmp/rnd-capability"


def verify_capabilities(product, plan, scenarios, settings, *, aggregate, selection=None):
    from workbench.sandbox import validate_configuration

    selection = selection or {"template": "python-basic", "database": "sqlite"}
    if plan.selection.model_dump() != selection:
        raise CheckFailure("隔离验证的技术栈与已批准计划不一致")
    try:
        inspect_stack(product, plan)
    except (CheckFailure, ValueError) as exc:
        return {"passed": False, "kind": "source_contract", "error": str(exc)}
    if settings.sandbox_provider != "daytona":
        raise UnsupportedScope(
            "自定义源码已保存，等待隔离验证环境：请配置本机 Daytona 和对应离线快照。"
            "生成代码不会在平台宿主执行；配置后重试同一运行，不会重做已保存模型响应。"
        )
    try:
        validate_configuration(settings, selection["template"], selection)
    except ValueError, PrerequisiteError:
        raise UnsupportedScope(
            "自定义验证环境尚未就绪；请检查本机 Daytona 授权、技术栈离线快照及配置，再重试同一运行。"
        ) from None
    # The pinned stock daemon exposes an unauthenticated in-sandbox execution
    # channel. A same-container database/tool probe cannot be trusted until the
    # new executor's application and control identities are actually separated.
    raise UnsupportedScope(
        "自定义源码已保存，但当前Daytona镜像的控制通道与数据库验证身份尚未完成隔离验收；"
        "已停止执行，保留原技术栈和同一运行候选，不会将不可信探针标为通过。"
    )
    product = Path(product).resolve()
    receipt_path = product.parent / (
        product.name + ("-aggregate" if aggregate else "-node") + "-verification.json"
    )
    payload = {
        "product": str(product),
        "receipt": str(receipt_path),
        "selection": selection,
        "plan": plan.model_dump(),
        "scenario_ids": [s.id for s in scenarios],
        "aggregate": aggregate,
        "settings": {
            name: getattr(settings, name)
            for name in (
                "sandbox_provider",
                "daytona_allow_local_execution",
                "daytona_api_url",
                "daytona_snapshot",
                "daytona_snapshots",
                "daytona_target",
                "daytona_runtime_timeout",
                "tool_timeout",
            )
        },
    }
    payload["settings"]["daytona_api_key"] = settings.daytona_api_key.get_secret_value()
    body = json.dumps(payload).encode()
    if len(body) > 1_000_000:
        raise PrerequisiteError("自定义验收控制契约超过1MB预算，未创建沙箱")
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            [sys.executable, "-m", "workbench.capability_sandbox"],
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            env=clean_env(
                {
                    "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get("PRODUCT_VERIFY_PLAYWRIGHT", ""),
                    "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
                }
            ),
            **process_options(),
        )
        try:
            process.communicate(
                body, timeout=settings.daytona_runtime_timeout + settings.tool_timeout * 12 + 60
            )
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise PrerequisiteError(
                "自定义隔离验证超时；已保留沙箱名称回执，请在本机确认清理后重试"
            ) from None
        if process.returncode:
            # The child prints only a static classified error. Never echo provider/SDK objects.
            raise PrerequisiteError("自定义隔离验证进程失败；查看该节点的脱敏验证回执")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("cleanup") != "deleted":
        raise PrerequisiteError("自定义隔离环境清理未确认；已阻止交付，请按回执中的沙箱名称检查")
    return receipt


def _verify(product, plan, scenarios, settings, selection, receipt_path, *, client, aggregate):
    from daytona import SessionExecuteRequest

    from workbench.daytona_sessions import run_session_command
    from workbench.sandbox import params_for, source_archive

    before = manifest(product)
    name = "rnd-capability-" + uuid.uuid4().hex
    receipt = {
        "verifier": "controller-http-contract-v2",
        "passed": False,
        "source_digest": digest(before),
        "plan_digest": digest(plan.model_dump()),
        "network_block_all": True,
        "credentials_uploaded": False,
        "scope": "aggregate" if aggregate else "node",
        "checks": [],
        "sandbox_name": name,
        "cleanup": "not-created",
        "restarted": False,
        "stack": inspect_stack(product, plan),
    }
    write_json(receipt_path, receipt)
    sandbox = None
    try:
        parameters = params_for(settings, name, selection["template"], selection)
        parameters.os_user = "root"
        sandbox = client.create(parameters, timeout=settings.tool_timeout)
        receipt.update(sandbox_id=sandbox.id, cleanup="pending")
        write_json(receipt_path, receipt)
        sandbox.fs.create_folder(REMOTE, "700")
        sandbox.fs.upload_file(
            source_archive(product), REMOTE + "/source.zip", timeout=settings.tool_timeout
        )
        result = control_exec(
            sandbox,
            ["/usr/bin/python3", "-I", "-S", "-m", "zipfile", "-e", REMOTE + "/source.zip", REMOTE],
            settings.tool_timeout,
        )
        if result.exit_code != 0:
            raise CheckFailure("自定义产品源码解压失败")
        receipt["execution_isolation"] = prepare_identity(sandbox, plan, settings.tool_timeout)
        database_password = prepare_database(sandbox, plan, settings.tool_timeout)
        if database_password:
            with settings._model_keys_lock:
                settings._model_keys.add(database_password)
        database = database_environment(plan, database_password)
        for index, command in enumerate(plan.runtime.prepare):
            evidence = {}
            guarded_command, command_output = redirected_command(
                product_argv(plan, command.argv, database)
            )
            result = run_session_command(
                sandbox.process,
                guarded_command,
                REMOTE + "/product/" + command.cwd,
                settings.tool_timeout,
                evidence,
            )
            if result.exit_code != 0:
                receipt["build_diagnostic"] = settings.redact(
                    read_command_output(sandbox, command_output, settings.tool_timeout)
                )[-4000:]
                raise CheckFailure(f"第 {index + 1} 个隔离准备/构建命令失败；检查节点构建诊断")

        def start():
            session = "rnd-app-" + uuid.uuid4().hex
            sandbox.process.create_session(session)
            command = plan.runtime.start
            guarded_command, _ = redirected_command(product_argv(plan, command.argv, database))
            response = sandbox.process.execute_session_command(
                session,
                SessionExecuteRequest(
                    command="cd "
                    + shlex.quote(REMOTE + "/product/" + command.cwd)
                    + " && exec "
                    + shlex.join(guarded_command),
                    run_async=True,
                ),
                timeout=settings.tool_timeout,
            )
            if not response.cmd_id:
                raise CheckFailure("隔离应用启动未返回命令标识")
            preview = sandbox.get_preview_link(plan.runtime.port)
            url = preview_url(preview.url, sandbox.id, plan.runtime.port)
            if not isinstance(preview.token, str) or not preview.token:
                raise CheckFailure("私有隔离预览缺少授权标识")
            # The pinned local proxy consumes/strips this token before forwarding.
            http = httpx.Client(
                base_url=url,
                headers={"x-daytona-preview-token": preview.token},
                timeout=15,
                follow_redirects=False,
                trust_env=False,
            )
            try:
                deadline = time.monotonic() + plan.runtime.startup_seconds
                while time.monotonic() < deadline:
                    try:
                        with http.stream("GET", plan.runtime.health_path) as check:
                            if 200 <= check.status_code < 300:
                                return http, url, preview.token
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.2)
                raise CheckFailure("隔离应用未在约定时间内通过健康检查")
            except BaseException:
                http.close()
                raise

        http, url, token = start()
        baseline_counts = database_counts(sandbox, plan, settings.tool_timeout)
        with http:
            if plan.selection.backend in {"fastapi", "fastapiadmin"}:
                with http.stream("GET", "/openapi.json") as response:
                    if response.status_code != 200:
                        raise CheckFailure("实际运行服务没有FastAPI OpenAPI契约，拒绝技术栈替换")
            checks, saved = run_scenarios(http, scenarios)
            receipt["checks"].extend(checks)
        receipt["browser"] = run_browser(url, token, scenarios, saved, settings.tool_timeout)
        counts = database_counts(sandbox, plan, settings.tool_timeout)
        if not any(counts[name] > baseline_counts[name] for name in counts):
            raise CheckFailure(
                "独立物理数据库探针未观察到验收请求写入的数据；静态响应不能替代持久化"
            )
        receipt["database"] = {
            "engine": plan.selection.database,
            "baseline": baseline_counts,
            "after": counts,
            "observed_writes": True,
        }
        if aggregate:
            client.stop(sandbox, timeout=settings.tool_timeout)
            client.start(sandbox, timeout=settings.tool_timeout)
            prepare_database(
                sandbox, plan, settings.tool_timeout, restart=True, password=database_password
            )
            http, _, _ = start()
            with http:
                checks, _ = run_scenarios(http, scenarios, saved=saved, after_restart=True)
                receipt["checks"].extend(checks)
            receipt["restarted"] = True
            restarted = database_counts(sandbox, plan, settings.tool_timeout)
            if any(restarted[name] < counts[name] for name in counts):
                raise CheckFailure("独立数据库重启后丢失已写入的记录")
            receipt["database"]["after_restart"] = restarted
        if manifest(product) != before:
            raise CheckFailure("隔离验收期间宿主源码发生变化")
        receipt["passed"] = True
    except IsolationUnavailable as exc:
        receipt.update(kind="isolation_environment", error=str(exc))
    except CheckFailure as exc:
        receipt["error"] = str(exc)
        receipt["failed_scenario"] = getattr(exc, "scenario_id", None)
    except Exception as exc:
        receipt["error"] = (
            "本机隔离服务未完成验收（" + type(exc).__name__ + "），未使用本机执行回退"
        )
    finally:
        if sandbox is None:
            receipt["cleanup"] = "create-failed-unknown"
            try:
                sandbox = client.get(name)
            except Exception:
                pass
        if sandbox is not None:
            try:
                client.delete(sandbox, timeout=settings.tool_timeout)
                receipt["cleanup"] = "deleted"
            except Exception:
                receipt.update(cleanup="delete-failed", passed=False)
                receipt["error"] = "本机隔离沙箱删除未确认；请按回执名称检查，交付已停止"
        if receipt["cleanup"] != "deleted":
            receipt["passed"] = False
        write_json(receipt_path, receipt)
    return receipt


def main():
    raise UnsupportedScope("生产自定义执行入口尚未完成独立隔离验收，禁止直接启动")
    body = sys.stdin.buffer.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError("自定义验收控制契约过大")
    payload = json.loads(body)
    install_loopback_guard()
    from workbench.sandbox import client_for, close_client
    from workbench.settings import Settings

    settings = Settings(_env_file=None, **payload["settings"])
    plan = CapabilityPlan.model_validate(payload["plan"])
    scenarios = [s for s in plan.scenarios if s.id in payload["scenario_ids"]]
    client = client_for(settings)
    try:
        _verify(
            Path(payload["product"]),
            plan,
            scenarios,
            settings,
            payload["selection"],
            Path(payload["receipt"]),
            client=client,
            aggregate=payload["aggregate"],
        )
    finally:
        close_client(client)


if __name__ == "__main__":
    main()
