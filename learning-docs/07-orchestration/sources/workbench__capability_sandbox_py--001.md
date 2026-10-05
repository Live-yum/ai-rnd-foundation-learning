# workbench/capability_sandbox.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__capability_sandbox_py--002.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_stack`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.local_only`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `startup_command_exit_facts`（L54–L76）：接收`process`、`session`、`command_id`、`timeout`。 源码说明：Read one bounded SDK status, without exposing commands, IDs or exceptions.。 控制顺序：L59按`any(type(value) is not str or not 1 <= len(value) <= 128 for value in (session, comma…`分支；L66按`command.id == command_id and type(command.exit_code) is int`分支；L67按`0 <= command.exit_code <= 255`分支。 调用`any`、`type`、`len`、`_DEADLINE.set`、`time.monotonic`、`min`、`process.get_session_command`、`_DEADLINE.reset`。 返回路径：L60的`unknown`；L68的`{ "command_exit_status": "zero" if command.exit_code == 0 else "nonzero", "command_exit_co…`；L76的`unknown`。
- `startup_command_exit_status`（L79–L81）：接收`process`、`session`、`command_id`、`timeout`。 源码说明：Compatibility view of the same single-query, bounded SDK facts.。 调用`startup_command_exit_facts`。 返回路径：L81的`startup_command_exit_facts(process, session, command_id, timeout)["command_exit_status"]`。
- `startup_failure_diagnostic`（L84–L248）：接收`output`、`http_status`、`http_error`、`tmpfs_noexec`、`command_exit_status`、`command_exit_code`、`output_limit`。 源码说明：Candidate output supplies hints only; no raw output, path or token escapes.。 控制顺序：L105按`type(output_limit) is not int or not 1 <= output_limit <= 8000`分支；L179按`exceptions and len(raw_bytes) == output_limit and not output.endswith(("\n", " │")) a…`分支；L190按`exception not in {"PermissionError", "FileNotFoundError", "OSError", "TimeoutError"}`分支；L196遍历`re.split(r"(?m)^Traceback \(most recent call last\):\n", output)[…`；L198按`not trace_errors`分支；L202按`failure[1] in {"PermissionError", "OSError"} and failure[2] in {"1", "13"} and frame(…`分支；L211按`"Waiting for application startup." in output or "Application startup failed." in outp…`分支；L213按`frame("app/__init__.py", "create_app")`分支。后续分支沿下方源码相同行号继续阅读。 调用`type`、`bounded_output_bytes`、`raw_bytes.decode`、`normalize_sgr`、`patterns.items`、`any`、`re.compile`、`exception_lines`、`exceptions_in`等。 返回路径：L222的`{ "phase": "health_deadline", "http_status": http_status if type(http_status) is int and 1…`。
- `startup_failure_diagnostic.frame`（L133–L144）：接收`path`、`function`、`trace`。 调用`re.search`、`re.escape`。 返回路径：L134的`re.search( r'(?m)^\s*File "[^"\n]{1,512}/' + re.escape(path) + r'", line [0-9]{1,7}, in ' …`。
- `startup_failure_diagnostic.exceptions_in`（L153–L174）：接收`trace`、`terminal`。 调用`pattern.finditer`、`item[1].endswith`、`public_exception`、`trace.startswith`、`item.end`、`trace[item.end() :].strip`、`re.fullmatch`。 返回路径：L155的`[ item for item in pattern.finditer(trace) if item[1].endswith(("Error", "Exception")) or …`。
- `restart_application_identity`（L251–L301）：接收`sandbox`、`port`、`timeout`、`extra_ports`。 源码说明：Stop only this sandbox's dedicated application UID, then prove closure. Bounded tmpfs survives this process restart, not a container restart. The controller and independent database identity are never。 控制顺序：L300按`result.exit_code != 0`分支；L301抛异常，停止当前正常路径。 调用`control_exec`、`str`、`min`、`CheckFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `verify_capabilities`（L304–L394）：接收`product`、`plan`、`scenarios`、`settings`、`aggregate`、`selection`、`trusted_oracle`。 控制顺序：L310按`plan.selection.model_dump() != selection`分支；L311抛异常，停止当前正常路径；L320按`selection["template"] == "fastapiadmin"`分支；L323按`dependency_identity(product) != profile["dependency_identity"]`分支；L324抛异常，停止当前正常路径；L360按`len(body) > 1_000_000`分支；L361抛异常，停止当前正常路径；L383抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`plan.selection.model_dump`、`CheckFailure`、`inspect_stack`、`str`、`capability_execution_prerequisites`、`require_dependency_descriptors`、`dependency_identity`、`PrerequisiteError`、`Path(product).resolve`等。 返回路径：L315的`{"passed": False, "kind": "source_contract", "error": str(exc)}`；L394的`receipt`。

</details>

**创建路径：** `workbench/capability_sandbox.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L396。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`16673`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_sandbox.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "9808a7d478c850801100e68878c1c603517223b2c62d13b9923beadabb0a7793"} -->
````python
# workbench/capability_sandbox.py
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


````
