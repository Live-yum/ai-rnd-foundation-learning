"""Custom source runs only in a private, network-blocked local Daytona sandbox.

The HTTP verifier remains in the controller process, outside generated code's
filesystem/process namespace. A product-authored JSON report cannot pass a task.
"""

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import closing
from pathlib import Path

import httpx

from workbench.capability_contracts import CapabilityPlan
from workbench.capability_isolation import (
    ContainerInspectionRejected,
    IsolationUnavailable,
    control_exec,
    prepare_identity,
    product_argv,
    read_command_output,
    redirected_command,
    require_container_evidence,
)
from workbench.capability_stack import (
    database_counts,
    database_environment,
    inspect_stack,
    prepare_database,
)
from workbench.capability_verification import (
    BrowserFailure,
    CheckFailure,
    preview_url,
    run_browser,
    run_scenarios,
)
from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.generator import PrerequisiteError
from workbench.local_only import install_loopback_guard
from workbench.tools import clean_env, process_options, stop_process

REMOTE = "/tmp/rnd-capability"


def startup_command_exit_facts(process, session, command_id, timeout):
    """Read one bounded SDK status, without exposing commands, IDs or exceptions."""
    from workbench.daytona_sessions import _DEADLINE

    unknown = {"command_exit_status": "unknown", "command_exit_code": None}
    if any(type(value) is not str or not 1 <= len(value) <= 128 for value in (session, command_id)):
        return unknown
    token = _DEADLINE.set(time.monotonic() + min(timeout, 5))
    try:
        # Pinned SDK 0.190.0 documents exit_code only for completed commands.
        # Its optional/default None cannot distinguish running from absent data.
        command = process.get_session_command(session, command_id)
        if command.id == command_id and type(command.exit_code) is int:
            if 0 <= command.exit_code <= 255:
                return {
                    "command_exit_status": "zero" if command.exit_code == 0 else "nonzero",
                    "command_exit_code": command.exit_code,
                }
    except Exception:
        pass
    finally:
        _DEADLINE.reset(token)
    return unknown


def startup_command_exit_status(process, session, command_id, timeout):
    """Compatibility view of the same single-query, bounded SDK facts."""
    return startup_command_exit_facts(process, session, command_id, timeout)["command_exit_status"]


def startup_failure_diagnostic(
    output,
    http_status,
    http_error,
    tmpfs_noexec=None,
    command_exit_status="unknown",
    *,
    command_exit_code=None,
    output_limit=8000,
):
    """Candidate output supplies hints only; no raw output, path or token escapes."""
    from workbench.capability_startup_paths import (
        OTHER_CONTROL,
        bounded_output_bytes,
        exception_lines,
        normalize_sgr,
        output_shapes,
        public_exception,
    )

    readable = type(output) is str
    if type(output_limit) is not int or not 1 <= output_limit <= 8000:
        output_limit = 8000
    raw_bytes = bounded_output_bytes(output, output_limit) if readable else b""
    # Dropping an incomplete terminal codepoint cannot create extra scan bytes.
    output = raw_bytes.decode("utf-8", errors="ignore")
    # Bound raw bytes BEFORE stripping already observed color sequences. Never
    # refill the budget with text beyond the original read or interpret OSC.
    raw_output = output
    output = normalize_sgr(output)
    patterns = {
        "permission-denied": ("PermissionError", "Permission denied", "Operation not permitted"),
        "missing-module": ("ModuleNotFoundError", "No module named"),
        "import-error": ("ImportError",),
        "native-library-mapping": ("failed to map segment from shared object",),
        "missing-file": ("No such file or directory",),
        "address-in-use": ("Address already in use", "address already in use"),
        "readonly-filesystem": ("Read-only file system",),
        "storage-full": ("No space left on device",),
        "memory-error": ("MemoryError", "out of memory"),
        "syntax-error": ("SyntaxError",),
        "executable-format": ("Exec format error",),
    }
    categories = [key for key, markers in patterns.items() if any(m in output for m in markers)]
    modules = ("uvicorn", "fastapi", "sqlalchemy", "pydantic", "app", "access")
    known = [module for module in modules if "No module named '" + module + "'" in output]

    # These are untrusted, bounded traceback hints, never kernel evidence or an
    # acceptance signal. Do not return captured paths, messages or class names.
    def frame(path, function, trace=output):
        return (
            re.search(
                r'(?m)^\s*File "[^"\n]{1,512}/'
                + re.escape(path)
                + r'", line [0-9]{1,7}, in '
                + re.escape(function)
                + r"\s*$",
                trace,
            )
            is not None
        )

    exception_pattern = re.compile(
        r"(?m)^([A-Za-z_][A-Za-z0-9_.]{0,127}):(?: \[Errno ([0-9]{1,10})\])?"
    )
    terminal_exception_pattern = re.compile(
        r"(?m)^([A-Za-z_][A-Za-z0-9_.<>]{0,255})(?::(?: \[Errno ([0-9]{1,10})\])?|[ \t]{0,32}$)"
    )

    def exceptions_in(trace, *, terminal=False):
        pattern = terminal_exception_pattern if terminal else exception_pattern
        return [
            item
            for item in pattern.finditer(trace)
            if item[1].endswith(("Error", "Exception"))
            or (
                terminal
                and (
                    public_exception(item[1]) != "unknown"
                    # Wrapped documentation URLs are not exception headings.
                    or (":" in item[0] and not trace.startswith("//", item.end()))
                    # Unknown empty headings may use lowercase names too.
                    # Ignore bare words inside a longer exception message.
                    or not trace[item.end() :].strip()
                    or re.fullmatch(
                        r"[ \t\r\n]*(?:╰─{1,512}╯|└─{1,512}┘)[ \t\r\n]*",
                        trace[item.end() :],
                    )
                )
            )
        ]

    terminal_output = exception_lines(output)
    exceptions = exceptions_in(terminal_output, terminal=True)
    exception, number = exceptions[-1].groups() if exceptions else ("unknown", "")
    if (
        exceptions
        and len(raw_bytes) == output_limit
        and not output.endswith(("\n", " │"))
        and exceptions[-1].end() == len(terminal_output)
        and ":" not in exceptions[-1][0]
    ):
        # A cut TypeErrorPrivate must not become a known empty TypeError.
        exception, number = "unknown", None
    exception = public_exception(exception)
    exception_errno = int(number) if number in {"1", "2", "13", "28", "30"} else None
    if exception not in {"PermissionError", "FileNotFoundError", "OSError", "TimeoutError"}:
        exception_errno = None
    # A cleanup traceback may follow the primary error. Keep that final error's
    # type/errno above, but associate constructor frames with their OWN error.
    # Neither a separate denial nor a truncated traceback can complete a match.
    semaphore = False
    for trace in re.split(r"(?m)^Traceback \(most recent call last\):\n", output)[1:]:
        trace_errors = exceptions_in(trace)
        if not trace_errors:
            continue
        failure = trace_errors[0]
        frames = trace[: failure.start()]
        if (
            failure[1] in {"PermissionError", "OSError"}
            and failure[2] in {"1", "13"}
            and frame("concurrent/futures/process.py", "__init__", frames)
            and frame("multiprocessing/synchronize.py", "__init__", frames)
            and "_multiprocessing.SemLock(" in frames
        ):
            semaphore = True
    startup_phase = "unknown"
    if "Waiting for application startup." in output or "Application startup failed." in output:
        startup_phase = "lifespan"
    elif frame("app/__init__.py", "create_app"):
        startup_phase = "factory"
    elif frame("uvicorn/importer.py", "import_from_string"):
        startup_phase = "import"
    errors = {"none", "connect", "timeout", "protocol", "other"}
    if type(command_exit_code) is not int or not 0 <= command_exit_code <= 255:
        command_exit_code = None
    else:
        command_exit_status = "zero" if command_exit_code == 0 else "nonzero"
    return {
        "phase": "health_deadline",
        "http_status": http_status
        if type(http_status) is int and 100 <= http_status <= 599
        else None,
        "http_error": http_error if type(http_error) is str and http_error in errors else "other",
        "output_readable": readable,
        "output_nonempty": bool(raw_bytes),
        "output_raw_bytes": len(raw_bytes) if readable else None,
        "output_normalized_bytes": len(output.encode("utf-8")) if readable else None,
        "output_normalized_nonspace": bool(output.strip()) if readable else None,
        "output_read_limit_reached": len(raw_bytes) == output_limit if readable else None,
        "output_has_non_sgr_control": bool(OTHER_CONTROL.search(output)) if readable else None,
        "output_hints": categories,
        "output_shapes": output_shapes(raw_output),
        "known_missing_modules": known,
        "startup_phase_hint": startup_phase,
        "failure_component": "multiprocessing-semaphore" if semaphore else "unknown",
        "exception_type": exception,
        "exception_errno": exception_errno,
        "application_startup_reported": "Application startup complete" in output,
        "tmpfs_noexec": tmpfs_noexec if type(tmpfs_noexec) is bool else None,
        "command_exit_status": command_exit_status
        if type(command_exit_status) is str and command_exit_status in {"zero", "nonzero"}
        else "unknown",
        "command_exit_code": command_exit_code,
    }


def restart_application_identity(sandbox, port, timeout, *, extra_ports=()):
    """Stop only this sandbox's dedicated application UID, then prove closure.

    Bounded tmpfs survives this process restart, not a container restart. The
    controller and independent database identity are never selected by the kill.
    """
    script = """import os,pathlib,signal,sys,time
uid=20000;ports={int(value) for value in sys.argv[1:]};end=time.monotonic()+10
def live():
 result=[]
 entries=list(pathlib.Path('/proc').glob('[0-9]*/task/[0-9]*/status'))
 if len(entries)>4096:raise RuntimeError('Process inventory limit exceeded')
 for path in entries:
  try:
   fields=dict(line.split(':',1) for line in path.read_text().splitlines())
   if uid in [int(v) for v in fields['Uid'].split()] and not fields['State'].strip().startswith('Z'):
    result.append(int(path.parents[2].name))
  except FileNotFoundError:pass
 return sorted(set(result))
while True:
 active=live()
 if not active:
  time.sleep(.05)
  if not live():break
 for pid in active:
  try:
   fd=os.pidfd_open(pid)
   try:
    fields=dict(line.split(':',1) for line in pathlib.Path('/proc',str(pid),'status').read_text().splitlines())
    if uid in [int(v) for v in fields['Uid'].split()]:signal.pidfd_send_signal(fd,signal.SIGKILL)
   finally:os.close(fd)
  except ProcessLookupError:pass
  except FileNotFoundError:pass
 if time.monotonic()>=end:raise SystemExit(1)
 time.sleep(.05)
for name in ('tcp','tcp6'):
 path=pathlib.Path('/proc/net')/name
 if not path.exists():continue
 with path.open() as f:lines=f.read(4000001)
 if len(lines)>4000000:raise SystemExit(1)
 for line in lines.splitlines()[1:]:
  fields=line.split()
  if len(fields)>3 and int(fields[1].rsplit(':',1)[1],16) in ports and fields[3]=='0A':raise SystemExit(1)
"""
    result = control_exec(
        sandbox,
        ["/usr/bin/python3", "-I", "-S", "-c", script, str(port), *(str(p) for p in extra_ports)],
        min(timeout, 15),
    )
    if result.exit_code != 0:
        raise CheckFailure("应用身份仍有存活进程或旧端口未关闭，拒绝伪造重启成功")


def verify_capabilities(
    product, plan, scenarios, settings, *, aggregate, selection=None, trusted_oracle=None
):
    from workbench.capability_execution import capability_execution_prerequisites

    selection = selection or {"template": "python-basic", "database": "sqlite"}
    if plan.selection.model_dump() != selection:
        raise CheckFailure("隔离验证的技术栈与已批准计划不一致")
    try:
        inspect_stack(product, plan)
    except (CheckFailure, ValueError) as exc:
        return {"passed": False, "kind": "source_contract", "error": str(exc)}
    directory, profile = capability_execution_prerequisites(settings, selection)
    from workbench.capability_dependencies import require_dependency_descriptors

    require_dependency_descriptors(product, plan, profile)
    if selection["template"] == "fastapiadmin":
        from workbench.daytona_profiles import dependency_identity

        if dependency_identity(product) != profile["dependency_identity"]:
            raise PrerequisiteError("原生候选依赖与已验收快照不一致，未执行或更换技术栈")
    product = Path(product).resolve()
    receipt_path = product.parent / (
        product.name + ("-aggregate" if aggregate else "-node") + "-verification.json"
    )
    # Never adopt an older successful attempt if the verifier dies before
    # writing its own fresh report.
    write_json(receipt_path, {"passed": False, "cleanup": "not-started"})
    payload = {
        "product": str(product),
        "receipt": str(receipt_path),
        "selection": selection,
        "plan": plan.model_dump(),
        "scenario_ids": [s.id for s in scenarios],
        "aggregate": aggregate,
        "trusted_oracle": trusted_oracle,
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
                "daytona_snapshots",
                "capability_execution_enabled",
                "capability_browser_image",
            )
        },
    }
    payload["settings"]["capability_profile_directory"] = str(directory)
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
                    "CAPABILITY_BROWSER_IMAGE": settings.capability_browser_image,
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
    if receipt_path.stat().st_size > 1_000_000:
        raise PrerequisiteError("自定义隔离验证回执超过大小上限，已阻止交付")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("cleanup") != "deleted":
        raise PrerequisiteError("自定义隔离环境清理未确认；已阻止交付，请按回执中的沙箱名称检查")
    return receipt


def _verify(
    product,
    plan,
    scenarios,
    settings,
    selection,
    receipt_path,
    *,
    client,
    aggregate,
    control_observer=None,
    security_probe=None,
    trusted_oracle=None,
    profile_record=None,
):
    from daytona import SessionExecuteRequest

    from workbench.capability_dependencies import (
        prepare_readonly_dependencies,
        readonly_prepare_commands,
        readonly_start_command,
        require_dependency_descriptors,
        verify_readonly_dependencies,
    )
    from workbench.capability_execution import (
        VERIFIER,
        require_preinstalled_evidence,
        require_profile_container_binding,
    )
    from workbench.catalog import Selection
    from workbench.daytona_sessions import run_session_command
    from workbench.sandbox import params_for, source_archive

    # Even a direct caller rejected during admission must not leave a prior
    # successful receipt available at the requested output path.
    write_json(receipt_path, {"passed": False, "cleanup": "not-created", "verifier": VERIFIER})
    if trusted_oracle not in (None, "contest-business-v2"):
        raise CheckFailure("未知控制端业务oracle，拒绝候选自定义验证器")
    if trusted_oracle and (
        not aggregate or selection["template"] != "fastapiadmin" or security_probe is None
    ):
        raise CheckFailure("独立竞赛oracle必须使用原生完整隔离验收")
    # This boundary is shared by production and certification callers. Neither
    # direct calls nor a missing outer CLI preflight can waive exact provenance.
    if selection != plan.selection.model_dump() or selection not in (
        Selection(template="python-basic").model_dump(),
        Selection(template="fastapiadmin").model_dump(),
    ):
        raise CheckFailure("隔离验证的技术栈与已批准计划或登记的只读依赖profile不一致")
    if (
        not isinstance(profile_record, dict)
        or profile_record.get("selection", Selection(template="python-basic").model_dump())
        != selection
    ):
        raise CheckFailure("只读依赖镜像profile没有绑定当前技术栈")
    require_dependency_descriptors(product, plan, profile_record)
    commands = readonly_prepare_commands(plan)
    readonly_start_command(plan)
    dependency_profile = profile_record["snapshot"]["dependency_manifest"]
    before = manifest(product)
    native = selection["template"] == "fastapiadmin"
    prefix = "rnd-source-native-" if native else "rnd-source-"
    name = (prefix if security_probe is not None else "rnd-capability-") + uuid.uuid4().hex
    receipt = {
        "verifier": VERIFIER,
        "dependency_profile": dependency_profile,
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
    oracle_adapter = None
    try:
        parameters = params_for(settings, name, selection["template"], selection)
        parameters.os_user = "root"
        if aggregate:
            # SDK 0.190.0 uses 0 for delete-on-stop, so the ordinary disposable
            # policy destroys the database before aggregate restart acceptance.
            # Keep only this owned sandbox for a finite stop/start window; the
            # mandatory finally deletion and all isolation gates still apply.
            parameters.auto_delete_interval = (2 * settings.tool_timeout + 59) // 60 + 1
        sandbox = client.create(parameters, timeout=settings.tool_timeout)
        receipt.update(sandbox_id=sandbox.id, cleanup="pending")
        write_json(receipt_path, receipt)
        if security_probe is not None:
            sandbox.refresh_data()
            if sandbox.network_block_all is not True or sandbox.public is not False:
                raise IsolationUnavailable("实际沙箱未确认私有且禁止网络出口，未上传或执行源码")
        if control_observer is None:
            raise IsolationUnavailable("缺少可信控制面的实际容器检查，未上传或执行源码")
        try:
            receipt["container_isolation"] = require_container_evidence(
                control_observer(sandbox.id), sandbox.id
            )
            require_profile_container_binding(profile_record, receipt["container_isolation"])
            if native and receipt["container_isolation"].get("profile") != (
                "native-fastapiadmin-postgresql-v1"
            ):
                raise ValueError("Native execution requires its exact container profile")
        except ContainerInspectionRejected as exc:
            raise IsolationUnavailable(
                "实际容器不符合已批准的非特权策略，未上传或执行源码",
                evidence=ContainerInspectionRejected.diagnostic(exc),
            ) from None
        except ValueError:
            raise IsolationUnavailable(
                "实际容器不符合已批准的非特权策略，未上传或执行源码"
            ) from None
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
        identity_options = {"native_semaphore_storage": True} if native else {}
        receipt["execution_isolation"] = prepare_identity(
            sandbox, plan, settings.tool_timeout, **identity_options
        )
        receipt["preinstalled_dependencies"] = require_preinstalled_evidence(
            prepare_readonly_dependencies(
                sandbox,
                plan,
                settings.tool_timeout,
                expected=dependency_profile,
                source_inventory=before,
            ),
            dependency_profile,
            source_digest=receipt["source_digest"],
        )
        database_password = prepare_database(sandbox, plan, settings.tool_timeout)
        if database_password:
            with settings._model_keys_lock:
                settings._model_keys.add(database_password)
        from workbench.capability_services import prepare_native_services

        services = prepare_native_services(sandbox, plan, settings.tool_timeout)
        if services:
            with settings._model_keys_lock:
                settings._model_keys.update(services.values())
        database = database_environment(plan, database_password, services)
        if trusted_oracle:
            from workbench.capability_stack import owned_database_identity

            oracle_database_ownership = owned_database_identity(sandbox, settings.tool_timeout)
        if security_probe is not None:
            receipt["security_checks"] = security_probe(
                sandbox, plan, settings.tool_timeout, receipt["container_isolation"], database
            )
        for index, command in enumerate(commands):
            evidence = {}
            guarded_command, command_output = redirected_command(
                product_argv(plan, command.argv, database, **identity_options)
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
        if native:
            from workbench.capability_native_runtime import verify_and_freeze_native_sources

            restart_application_identity(
                sandbox, plan.runtime.port, settings.tool_timeout, extra_ports=(5173,)
            )
            verify_and_freeze_native_sources(sandbox, before, settings.tool_timeout)
            receipt["native_build"] = {
                "preinstalled_dependencies_verified": True,
                "frontend_build": True,
                "frontend_typecheck": True,
                "source_frozen": True,
            }

        def start(command=None, port=None, health_path=None):
            from workbench.capability_startup_paths import startup_target

            command, target = startup_target(plan, command, port, health_path)
            if target["role"] == "backend":
                receipt["backend_health_observed"] = False
            require_preinstalled_evidence(
                verify_readonly_dependencies(
                    sandbox,
                    plan,
                    settings.tool_timeout,
                    expected=dependency_profile,
                    source_inventory=before,
                ),
                dependency_profile,
                source_digest=receipt["source_digest"],
            )
            port = target["port"]
            health_path = "/" if target["role"] == "frontend" else plan.runtime.health_path
            session = "rnd-app-" + uuid.uuid4().hex
            sandbox.process.create_session(session)
            guarded_command, command_output = redirected_command(
                product_argv(plan, command.argv, database, **identity_options)
            )
            response = sandbox.process.execute_session_command(
                session,
                SessionExecuteRequest(
                    command="cd "
                    + shlex.quote(REMOTE + "/product/" + command.cwd)
                    + " && "
                    + shlex.join(guarded_command),
                    run_async=True,
                ),
                timeout=settings.tool_timeout,
            )
            if not response.cmd_id:
                raise CheckFailure("隔离应用启动未返回命令标识")
            preview = sandbox.get_preview_link(port)
            url = preview_url(preview.url, sandbox.id, port)
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
                last_http_status, last_http_error = None, "none"
                while time.monotonic() < deadline:
                    try:
                        with http.stream("GET", health_path) as check:
                            last_http_status, last_http_error = check.status_code, "none"
                            if 200 <= check.status_code < 300:
                                if target["role"] == "backend":
                                    receipt["backend_health_observed"] = True
                                return http, url, preview.token
                    except httpx.HTTPError as exc:
                        last_http_error = (
                            "timeout"
                            if isinstance(exc, httpx.TimeoutException)
                            else "connect"
                            if isinstance(exc, httpx.ConnectError)
                            else "protocol"
                            if isinstance(exc, httpx.ProtocolError)
                            else "other"
                        )
                    time.sleep(0.2)
                try:
                    from workbench.capability_startup_paths import NATIVE_TAIL_LIMIT

                    startup_output = read_command_output(
                        sandbox,
                        command_output,
                        min(settings.tool_timeout, 5),
                        limit=NATIVE_TAIL_LIMIT if native else 8000,
                        tail=True,
                    )
                except Exception:
                    startup_output = None
                tmpfs_noexec = None
                try:
                    mode = control_exec(
                        sandbox,
                        [
                            "/usr/bin/python3",
                            "-I",
                            "-S",
                            "-c",
                            "import os; print(int(bool(os.statvfs('/tmp').f_flag & os.ST_NOEXEC)))",
                        ],
                        min(settings.tool_timeout, 5),
                    )
                    value = mode.result.strip() if type(mode.result) is str else ""
                    if type(mode.exit_code) is int and mode.exit_code == 0 and value in {"0", "1"}:
                        tmpfs_noexec = value == "1"
                except Exception:
                    pass
                receipt["startup_diagnostic"] = startup_failure_diagnostic(
                    startup_output,
                    last_http_status,
                    last_http_error,
                    tmpfs_noexec,
                    **startup_command_exit_facts(
                        sandbox.process, session, response.cmd_id, min(settings.tool_timeout, 5)
                    ),
                    output_limit=NATIVE_TAIL_LIMIT if native else 8000,
                )
                receipt["startup_diagnostic"]["target"] = {
                    **target,
                    "backend_health_observed": receipt.get("backend_health_observed") is True,
                }
                if target["role"] == "frontend":
                    from workbench.capability_startup_paths import node_failure_facts

                    receipt["startup_diagnostic"]["node_error"] = node_failure_facts(startup_output)
                if native:
                    from workbench.capability_startup_paths import (
                        native_startup_paths,
                        native_startup_smoke,
                    )

                    receipt["startup_diagnostic"]["launch_paths"] = {"status": "unknown"}
                    receipt["startup_diagnostic"]["interpreter_probe"] = {
                        "exit_status": "unknown",
                        "output_shapes": [],
                        "checks": None,
                    }
                    try:
                        receipt["startup_diagnostic"]["launch_paths"] = native_startup_paths(
                            sandbox, min(settings.tool_timeout, 5), role=target["role"]
                        )
                    except Exception:
                        pass
                    try:
                        receipt["startup_diagnostic"]["interpreter_probe"] = native_startup_smoke(
                            sandbox,
                            plan,
                            database,
                            identity_options,
                            min(settings.tool_timeout, 5),
                            role=target["role"],
                        )
                    except Exception:
                        pass
                raise CheckFailure("隔离应用未在约定时间内通过健康检查")
            except BaseException:
                http.close()
                raise

        http, url, token = start()
        browser_url, browser_token = url, token
        # The health request already opened this client; entering it again is
        # invalid. Own its close even when the independent baseline probe fails.
        with closing(http):
            if native:
                from workbench.capability_native_runtime import (
                    FRONTEND_PORT,
                    frontend_start_command,
                )

                frontend_http, browser_url, browser_token = start(
                    frontend_start_command(), FRONTEND_PORT, "/"
                )
                frontend_http.close()
                receipt["native_frontend_started"] = True
            baseline_counts = database_counts(sandbox, plan, settings.tool_timeout)
            if plan.selection.backend in {"fastapi", "fastapiadmin"}:
                with http.stream("GET", "/openapi.json") as response:
                    if response.status_code != 200:
                        raise CheckFailure("实际运行服务没有FastAPI OpenAPI契约，拒绝技术栈替换")
            if trusted_oracle:
                from scripts.extension_oracles import contest
                from workbench.capability_contest_oracle import ContestOracleAdapter

                oracle_adapter = ContestOracleAdapter(url, token, sandbox, settings.tool_timeout)
                oracle_state, oracle_witnesses = contest.initial(
                    oracle_adapter.http,
                    oracle_adapter.probe,
                    oracle_adapter.actor_ids,
                    uuid.uuid4().hex,
                )
                receipt["business_oracle"] = {
                    "protocol": trusted_oracle,
                    "witnesses": oracle_witnesses,
                    "full_request_complete": False,
                    "remaining_obligations": list(contest.REMAINING),
                }
            checks, saved = run_scenarios(http, scenarios)
            receipt["checks"].extend(checks)
        if security_probe is not None:
            from workbench.capability_browser_isolation import run_isolated_browser

            receipt["browser"] = run_isolated_browser(
                browser_url,
                browser_token,
                scenarios,
                saved,
                settings.tool_timeout,
                image=settings.capability_browser_image,
            )
            receipt["browser_image"] = settings.capability_browser_image
        else:
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
            if security_probe is not None:
                restart_application_identity(
                    sandbox,
                    plan.runtime.port,
                    settings.tool_timeout,
                    extra_ports=(5173,) if native else (),
                )
                receipt["restart_kind"] = "application_process"
            else:
                client.stop(sandbox, timeout=settings.tool_timeout)
                client.start(sandbox, timeout=settings.tool_timeout)
                receipt["restart_kind"] = "container"
            if security_probe is not None:
                restarted_container = require_container_evidence(
                    control_observer(sandbox.id), sandbox.id
                )
                require_profile_container_binding(profile_record, restarted_container)
                receipt["restart_preinstalled_dependencies"] = require_preinstalled_evidence(
                    verify_readonly_dependencies(
                        sandbox,
                        plan,
                        settings.tool_timeout,
                        expected=dependency_profile,
                        source_inventory=before,
                    ),
                    dependency_profile,
                    source_digest=receipt["source_digest"],
                )
                receipt["restart_security_checks"] = security_probe(
                    sandbox, plan, settings.tool_timeout, restarted_container, database
                )
            if security_probe is None:
                receipt["restart_preinstalled_dependencies"] = require_preinstalled_evidence(
                    verify_readonly_dependencies(
                        sandbox,
                        plan,
                        settings.tool_timeout,
                        expected=dependency_profile,
                        source_inventory=before,
                    ),
                    dependency_profile,
                    source_digest=receipt["source_digest"],
                )
                prepare_database(
                    sandbox, plan, settings.tool_timeout, restart=True, password=database_password
                )
            http, _, _ = start()
            with closing(http):
                if native:
                    frontend_http, _, _ = start(frontend_start_command(), FRONTEND_PORT, "/")
                    frontend_http.close()
                    receipt["native_frontend_restart"] = True
                if trusted_oracle:
                    oracle_witnesses.update(
                        contest.after_restart(
                            oracle_adapter.http,
                            oracle_adapter.probe,
                            oracle_state,
                            uuid.uuid4().hex,
                        )
                    )
                checks, _ = run_scenarios(http, scenarios, saved=saved, after_restart=True)
                receipt["checks"].extend(checks)
            receipt["restarted"] = True
            restarted = database_counts(sandbox, plan, settings.tool_timeout)
            if any(restarted[name] < counts[name] for name in counts):
                raise CheckFailure("独立数据库重启后丢失已写入的记录")
            receipt["database"]["after_restart"] = restarted
            if trusted_oracle:
                from workbench.capability_stack import recreate_owned_native_database

                oracle_adapter.close()
                fresh_identity = recreate_owned_native_database(
                    sandbox, plan, settings.tool_timeout, oracle_database_ownership
                )
                from workbench.capability_services import reset_owned_native_cache

                reset_owned_native_cache(sandbox, settings.tool_timeout)
                http, url, token = start()
                http.close()
                frontend_http, _, _ = start(frontend_start_command(), FRONTEND_PORT, "/")
                frontend_http.close()
                oracle_adapter = ContestOracleAdapter(url, token, sandbox, settings.tool_timeout)
                oracle_witnesses.update(contest.fresh_database(oracle_adapter.probe, oracle_state))
                _, replay = contest.initial(
                    oracle_adapter.http,
                    oracle_adapter.probe,
                    oracle_adapter.actor_ids,
                    uuid.uuid4().hex,
                )
                if not all(replay.get(name) is True for name in contest.SEMANTICS[:5]):
                    raise CheckFailure("新库业务请求重放未通过")
                oracle_adapter.close()
                receipt["business_oracle"].update(
                    witnesses=oracle_witnesses,
                    fresh_replay=True,
                    same_cluster=oracle_database_ownership["cluster"] == fresh_identity["cluster"],
                    distinct_database_oid=oracle_database_ownership["database_oid"]
                    != fresh_identity["database_oid"],
                )
        # Drain candidate processes before the final exact tree/link inventory;
        # a successful live response cannot hide additional executable modules.
        restart_application_identity(
            sandbox,
            plan.runtime.port,
            settings.tool_timeout,
            extra_ports=(5173,) if native else (),
        )
        receipt["final_preinstalled_dependencies"] = require_preinstalled_evidence(
            verify_readonly_dependencies(
                sandbox,
                plan,
                settings.tool_timeout,
                expected=dependency_profile,
                source_inventory=before,
            ),
            dependency_profile,
            source_digest=receipt["source_digest"],
        )
        if manifest(product) != before:
            raise CheckFailure("隔离验收期间宿主源码发生变化")
        receipt["passed"] = True
    except IsolationUnavailable as exc:
        receipt.update(kind="isolation_environment", error=str(exc))
        receipt["isolation_diagnostic"] = exc.evidence
    except CheckFailure as exc:
        receipt["error"] = str(exc)
        receipt["failed_scenario"] = getattr(exc, "scenario_id", None)
        if native:
            from scripts.capability_native_shm_probe import native_shm_cleanup_diagnostic

            cleanup_diagnostic = native_shm_cleanup_diagnostic(exc)
            if cleanup_diagnostic:
                receipt["native_shm_cleanup_diagnostic"] = cleanup_diagnostic
        if isinstance(exc, BrowserFailure):
            receipt["browser_diagnostic"] = exc.diagnostic
    except Exception as exc:
        receipt["error"] = (
            "本机隔离服务未完成验收（" + type(exc).__name__ + "），未使用本机执行回退"
        )
    finally:
        if oracle_adapter is not None:
            try:
                oracle_adapter.close()
            except Exception:
                receipt.update(passed=False, error="可信业务验证器连接清理失败")
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
                receipt["cleanup_error"] = "本机隔离沙箱删除未确认；请按回执名称检查，交付已停止"
                receipt.setdefault("error", receipt["cleanup_error"])
        if receipt["cleanup"] != "deleted":
            receipt["passed"] = False
        write_json(receipt_path, receipt)
    return receipt


def main():
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
    if (
        len(scenarios) != len(payload["scenario_ids"])
        or not scenarios
        or type(payload["aggregate"]) is not bool
        or payload["selection"] != plan.selection.model_dump()
    ):
        raise ValueError("自定义验证输入未绑定准确场景、技术栈或验收模式")
    from scripts.capability_security_probe import security_probe_for_profile
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.capability_execution import capability_execution_prerequisites

    directory, record = capability_execution_prerequisites(settings, payload["selection"])
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
            control_observer=lambda sandbox_id: inspect_created_sandbox(
                directory, sandbox_id, require_resources=True, selection=payload["selection"]
            ),
            security_probe=security_probe_for_profile(
                directory, record, client=client, settings=settings
            ),
            trusted_oracle=payload.get("trusted_oracle"),
            profile_record=record,
        )
    finally:
        close_client(client)


if __name__ == "__main__":
    main()
