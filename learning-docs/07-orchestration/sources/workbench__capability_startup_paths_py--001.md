# workbench/capability_startup_paths.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_isolation`、`workbench.daytona_sessions`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `startup_target`（L23–L49）：接收`plan`、`command`、`port`、`health_path`。 源码说明：Bind diagnostics to the exact registered command before translation.。 控制顺序：L31按`getattr(plan.selection, "template", "") == "fastapiadmin"`分支；L34按`original == frontend_start_command()`分支；L36按`type(expected_port) is not int or not 1 <= expected_port <= 65535 or (port is not Non…`分支；L42抛异常，停止当前正常路径。 调用`readonly_start_command`、`getattr`、`frontend_start_command`、`type`、`CheckFailure`。 返回路径：L43的`translated, { "role": role, "interpreter": "node" if role == "frontend" else "python", "po…`。
- `bounded_output_bytes`（L216–L218）：接收`output`、`limit`。 源码说明：Cap raw UTF-8 bytes before normalization; never refill from later text.。 调用`output[:limit].encode`。 返回路径：L218的`output[:limit].encode("utf-8", errors="replace")[:limit]`。
- `normalize_sgr`（L221–L223）：接收`output`。 源码说明：Remove only bounded numeric SGR, never OSC or arbitrary terminal commands.。 调用`SGR.sub`。 返回路径：L223的`SGR.sub("", output)`。
- `exception_lines`（L226–L244）：接收`output`。 源码说明：Only bounded indentation and a single known Rich panel border unwrap. Use only for the terminal exception hint, never to join traceback frames for the stricter multiprocessing component classifier.。 控制顺序：L233遍历`output.split("\n")`；L237按`line.startswith("│ ") and line.endswith(" │")`分支。 调用`output.split`、`re.fullmatch`、`line.startswith`、`line.endswith`、`lines.append`、`"\n".join`。 返回路径：L244的`"\n".join(lines)`。
- `public_exception`（L247–L249）：接收`name`。 源码说明：Return only literal, reviewed exception names, never an unknown suffix.。 调用`FRAMEWORK_EXCEPTIONS.get`。 返回路径：L249的`name if name in BUILTIN_EXCEPTIONS else FRAMEWORK_EXCEPTIONS.get(name, "unknown")`。
- `_json_unique`（L252–L261）：接收`text`。 调用`json.loads`。 返回路径：L261的`json.loads(text, object_pairs_hook=pairs)`。
- `_json_unique.pairs`（L253–L259）：接收`values`。 控制顺序：L255遍历`values`；L256按`key in result`分支；L257抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L259的`result`。
- `output_shapes`（L264–L295）：接收`output`。 源码说明：Untrusted format hints, with no captured message or dynamic path.。 控制顺序：L266按`type(output) is not str`分支。 调用`type`、`bounded_output_bytes(output).decode`、`bounded_output_bytes`、`normalize_sgr`、`patterns.items`、`re.search`。 返回路径：L267的`[]`；L291的`[ label for label, pattern in patterns.items() if re.search(pattern, raw if label == "ansi…`。
- `node_failure_facts`（L298–L356）：接收`output`。 源码说明：Finite Node 22 hints from one bounded, closed error record only.。 控制顺序：L301按`type(output) is not str`分支；L312按`not headers`分支；L317按`end is None`分支；L321按`not re.fullmatch( r"[ \t\r\n]*(?:Node\.js v[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[ \t\r\n…`分支；L328按`header.startswith("SystemError [ERR_SYSTEM_ERROR]: ")`分支；L332按`match is None`分支；L336按`outer_codes != [code]`分支；L339按`code == "ERR_SYSTEM_ERROR"`分支。后续分支沿下方源码相同行号继续阅读。 调用`type`、`normalize_sgr`、`bounded_output_bytes(output, NATIVE_TAIL_LIMIT).decode`、`bounded_output_bytes`、`list`、`re.finditer`、`headers[-1].start`、`re.search`、`re.fullmatch`等。 返回路径：L302的`unknown`；L313的`unknown`；L318的`unknown`。
- `native_startup_smoke`（L375–L437）：接收`sandbox`、`plan`、`database`、`identity_options`、`timeout`、`role`。 源码说明：Exercise the same isolated launcher, without importing candidate code.。 控制顺序：L378按`type(role) is not str or role not in {"backend", "frontend"}`分支；L411按`type(result.exit_code) is int and 0 <= result.exit_code <= 255`分支；L416按`type(output) is not str or len(output.encode()) > SMOKE_OUTPUT_LIMIT`分支；L419按`receipt["exit_status"] == "zero"`分支；L421按`type(value) is dict and set(value) == { "version_matches", "executable_matches", "cwd…`分支。 调用`type`、`time.monotonic`、`min`、`_DEADLINE.set`、`redirected_command`、`product_argv`、`control_exec`、`shlex.join`、`remaining`等。 返回路径：L379的`receipt`；L417的`receipt`；L433的`receipt`。
- `native_startup_smoke.remaining`（L384–L390）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L388按`value < 1`分支；L389抛异常，停止当前正常路径。 调用`int`、`time.monotonic`、`TimeoutError`。 返回路径：L390的`value`。
- `native_startup_paths`（L566–L620）：接收`sandbox`、`timeout`、`role`。 源码说明：Return a fresh finite receipt or unknown; never serialize probe failures.。 控制顺序：L569按`type(role) is not str or role not in {"backend", "frontend"}`分支；L574按`budget < 1`分支；L578按`type(result.exit_code) is not int or result.exit_code != 0`分支；L580按`type(result.result) is not str or len(result.result.encode()) > 2048`分支；L583按`type(value) is not dict or set(value) != {"paths", "native_binary"}`分支；L587按`type(paths) is not dict or set(paths) != set(expected_roles)`分支；L589遍历`paths.values()`；L590按`type(row) is not dict or set(row) != {"entry", "target", "dac_read", "dac_exec"}`分支。后续分支沿下方源码相同行号继续阅读。 调用`type`、`_DEADLINE.set`、`time.monotonic`、`min`、`int`、`control_exec`、`len`、`result.result.encode`、`_json_unique`等。 返回路径：L570的`unknown`；L575的`unknown`；L579的`unknown`。

</details>

**创建路径：** `workbench/capability_startup_paths.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L620。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`23492`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_startup_paths.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b10dde2d8952fe1e0841aabec1c3cb624bc9e174eb1234863c3d28b55097ba32"} -->
````python
# workbench/capability_startup_paths.py
"""Failure-only fixed launch metadata and isolated, source-free interpreter smoke."""

import json
import re
import shlex
import time

from workbench.capability_isolation import (
    control_exec,
    product_argv,
    read_command_output,
    redirected_command,
)
from workbench.daytona_sessions import _DEADLINE

PATH_OUTPUT_LIMIT = 2048
SMOKE_OUTPUT_LIMIT = 512
NATIVE_TAIL_LIMIT = 8000 - PATH_OUTPUT_LIMIT - SMOKE_OUTPUT_LIMIT
SGR = re.compile(r"\x1b\[[0-9;]{0,32}m")
OTHER_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


def startup_target(plan, command=None, port=None, health_path=None):
    """Bind diagnostics to the exact registered command before translation."""
    from workbench.capability_dependencies import readonly_start_command
    from workbench.capability_verification import CheckFailure

    original = plan.runtime.start if command is None else command
    translated = readonly_start_command(plan, command)
    role, expected_port, expected_path = "backend", plan.runtime.port, plan.runtime.health_path
    if getattr(plan.selection, "template", "") == "fastapiadmin":
        from workbench.capability_native_runtime import FRONTEND_PORT, frontend_start_command

        if original == frontend_start_command():
            role, expected_port, expected_path = "frontend", FRONTEND_PORT, "/"
    if (
        type(expected_port) is not int
        or not 1 <= expected_port <= 65535
        or (port is not None and (type(port) is not int or port != expected_port))
        or (health_path is not None and health_path != expected_path)
    ):
        raise CheckFailure("启动诊断目标必须匹配登记的命令、端口和健康端点")
    return translated, {
        "role": role,
        "interpreter": "node" if role == "frontend" else "python",
        "port": expected_port,
        "health_endpoint": "frontend-root" if role == "frontend" else "plan-health",
        "registered_command_bound": True,
    }


# Literal public vocabulary only. Never discover classes from candidate output
# or import the candidate/application to classify its traceback.
BUILTIN_EXCEPTIONS = frozenset(
    {
        "ArithmeticError",
        "AssertionError",
        "AttributeError",
        "BaseException",
        "BaseExceptionGroup",
        "BlockingIOError",
        "BrokenPipeError",
        "BufferError",
        "ChildProcessError",
        "ConnectionAbortedError",
        "ConnectionError",
        "ConnectionRefusedError",
        "ConnectionResetError",
        "EOFError",
        "Exception",
        "ExceptionGroup",
        "FileExistsError",
        "FileNotFoundError",
        "FloatingPointError",
        "GeneratorExit",
        "ImportError",
        "IndentationError",
        "IndexError",
        "InterruptedError",
        "IsADirectoryError",
        "KeyError",
        "KeyboardInterrupt",
        "LookupError",
        "MemoryError",
        "ModuleNotFoundError",
        "NameError",
        "NotADirectoryError",
        "NotImplementedError",
        "OSError",
        "OverflowError",
        "PermissionError",
        "ProcessLookupError",
        "PythonFinalizationError",
        "RecursionError",
        "ReferenceError",
        "RuntimeError",
        "StopAsyncIteration",
        "StopIteration",
        "SyntaxError",
        "SystemError",
        "SystemExit",
        "TabError",
        "TimeoutError",
        "TypeError",
        "UnboundLocalError",
        "UnicodeDecodeError",
        "UnicodeEncodeError",
        "UnicodeError",
        "UnicodeTranslateError",
        "ValueError",
        "ZeroDivisionError",
    }
)
# Public non-Warning exception inventory verified as source data against native
# SQLAlchemy 2.0.51, Pydantic 2.12.5 and pydantic-core 2.41.5. The same names
# exist in controller versions 2.0.54, 2.13.5 and 2.46.5. No runtime discovery.
# Rich emits short headings; these hints do not prove the originating package.
FRAMEWORK_EXCEPTION_NAMES = {
    "sqlalchemy.exc": (
        "AmbiguousForeignKeysError",
        "ArgumentError",
        "AwaitRequired",
        "CircularDependencyError",
        "CompileError",
        "ConstraintColumnNotFoundError",
        "DBAPIError",
        "DataError",
        "DatabaseError",
        "DisconnectionError",
        "DuplicateColumnError",
        "IdentifierError",
        "IllegalStateChangeError",
        "IntegrityError",
        "InterfaceError",
        "InternalError",
        "InvalidRequestError",
        "InvalidatePoolError",
        "MissingGreenlet",
        "MultipleResultsFound",
        "NoForeignKeysError",
        "NoInspectionAvailable",
        "NoReferenceError",
        "NoReferencedColumnError",
        "NoReferencedTableError",
        "NoResultFound",
        "NoSuchColumnError",
        "NoSuchModuleError",
        "NoSuchTableError",
        "NotSupportedError",
        "ObjectNotExecutableError",
        "OperationalError",
        "PendingRollbackError",
        "ProgrammingError",
        "ResourceClosedError",
        "SQLAlchemyError",
        "StatementError",
        "TimeoutError",
        "UnboundExecutionError",
        "UnreflectableTableError",
        "UnsupportedCompilationError",
    ),
    "sqlalchemy.orm.exc": (
        "DetachedInstanceError",
        "FlushError",
        "LoaderStrategyException",
        "MappedAnnotationError",
        "ObjectDeletedError",
        "ObjectDereferencedError",
        "StaleDataError",
        "UnmappedClassError",
        "UnmappedColumnError",
        "UnmappedError",
        "UnmappedInstanceError",
    ),
    "pydantic.errors": (
        "PydanticForbiddenQualifier",
        "PydanticImportError",
        "PydanticInvalidForJsonSchema",
        "PydanticSchemaGenerationError",
        "PydanticUndefinedAnnotation",
        "PydanticUserError",
    ),
    "pydantic_core._pydantic_core": (
        "PydanticCustomError",
        "PydanticKnownError",
        "PydanticOmit",
        "PydanticSerializationError",
        "PydanticSerializationUnexpectedValue",
        "PydanticUseDefault",
        "SchemaError",
        "ValidationError",
    ),
}
FRAMEWORK_EXCEPTIONS = {
    alias: name
    for module, names in FRAMEWORK_EXCEPTION_NAMES.items()
    for name in names
    for alias in (name, module + "." + name)
}
FRAMEWORK_EXCEPTIONS.update(
    {
        **{"pydantic." + name: name for name in FRAMEWORK_EXCEPTION_NAMES["pydantic.errors"]},
        **{
            "pydantic_core." + name: name
            for name in FRAMEWORK_EXCEPTION_NAMES["pydantic_core._pydantic_core"]
        },
        "pydantic.ValidationError": "ValidationError",
        "ConcurrentModificationError": "StaleDataError",
        "sqlalchemy.orm.exc.ConcurrentModificationError": "StaleDataError",
        "sqlalchemy.orm.exc.NoResultFound": "NoResultFound",
        "sqlalchemy.orm.exc.MultipleResultsFound": "MultipleResultsFound",
    }
)


def bounded_output_bytes(output, limit=8000):
    """Cap raw UTF-8 bytes before normalization; never refill from later text."""
    return output[:limit].encode("utf-8", errors="replace")[:limit]


def normalize_sgr(output):
    """Remove only bounded numeric SGR, never OSC or arbitrary terminal commands."""
    return SGR.sub("", output)


def exception_lines(output):
    """Only bounded indentation and a single known Rich panel border unwrap.

    Use only for the terminal exception hint, never to join traceback frames
    for the stricter multiprocessing component classifier.
    """
    lines = []
    for line in output.split("\n"):
        # Do not strip arbitrary Unicode, terminal controls or dynamic prefixes.
        match = re.fullmatch(r"[ \t]{0,32}(│ .* │|[A-Za-z_].*)", line)
        line = match[1] if match else line
        if line.startswith("│ ") and line.endswith(" │"):
            line = line[2:-2]
            # Rich pads empty-message class headings to the panel width. Trim
            # only this bounded ASCII padding inside a complete known border.
            match = re.fullmatch(r"[ \t]{0,32}([A-Za-z_].*?) {0,512}", line)
            line = match[1] if match else line
        lines.append(line)
    return "\n".join(lines)


def public_exception(name):
    """Return only literal, reviewed exception names, never an unknown suffix."""
    return name if name in BUILTIN_EXCEPTIONS else FRAMEWORK_EXCEPTIONS.get(name, "unknown")


def _json_unique(text):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError("Duplicate diagnostic key")
            result[key] = value
        return result

    return json.loads(text, object_pairs_hook=pairs)


def output_shapes(output):
    """Untrusted format hints, with no captured message or dynamic path."""
    if type(output) is not str:
        return []
    output = bounded_output_bytes(output).decode("utf-8", errors="ignore")
    raw = output
    output = normalize_sgr(output)
    patterns = {
        "env-launcher": r"(?m)^(?:/usr/bin/)?env:",
        "setsid-launcher": r"(?m)^(?:/usr/bin/)?setsid:",
        "setpriv-launcher": r"(?m)^(?:/usr/bin/)?setpriv:",
        "shell-launcher": r"(?m)^(?:/bin/)?(?:sh|bash):",
        "system-python-launcher": r"(?m)^/usr/bin/python3:",
        "python-file-open": r"(?m)^[^\n]{0,512}python(?:3(?:\.14)?)?: can't open file ",
        "elf-loader": r"error while loading shared libraries:",
        "shared-library-open": r"cannot open shared object file:",
        "guard-rejection": r"(?m)^Isolated command guard unavailable; no product command was executed$",
        "python-traceback": r"Traceback \(most recent call last\):",
        "rich-traceback": r"(?m)^[ \t]{0,32}╭─{1,512} Traceback \(most recent call last\) ─{1,512}╮[ \t]*$",
        "cli-usage": r"(?m)^[ \t]{0,32}[Uu]sage: [^\n]{1,512}$",
        "cli-error": r"(?m)^(?:[A-Za-z0-9_./ -]{1,128}: error: |Error: )",
        "pydantic-validation": r"https://errors\.pydantic\.dev/[0-9]{1,2}\.[0-9]{1,2}/v/[a-z_]{1,64}(?:\s|$)",
        "sqlalchemy-error": r"https://sqlalche\.me/e/[0-9]{2}/[a-z0-9]{4}\)",
        "file-not-found-type": r"FileNotFoundError:",
        "vendor-loguru": r"(?m)^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \| (?:DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*\|",
        "ansi-control": r"\x1b\[[0-9;]{0,32}m",
    }
    return [
        label
        for label, pattern in patterns.items()
        if re.search(pattern, raw if label == "ansi-control" else output)
    ]


def node_failure_facts(output):
    """Finite Node 22 hints from one bounded, closed error record only."""
    unknown = {"error_code": "unknown", "errno": None, "syscall": "unknown", "component": "unknown"}
    if type(output) is not str:
        return unknown
    text = normalize_sgr(
        bounded_output_bytes(output, NATIVE_TAIL_LIMIT).decode("utf-8", errors="ignore")
    )
    headers = list(
        re.finditer(
            r"(?m)^[A-Za-z_][A-Za-z0-9_.]{0,127}(?: \[[A-Za-z0-9_.-]{1,64}\])?:[^\n]{0,1024}\n",
            text,
        )
    )
    if not headers:
        return unknown
    # A later unknown error must not borrow an earlier error's structured data.
    record = text[headers[-1].start() :]
    end = re.search(r"(?m)^}[ \t]*$", record)
    if end is None:
        return unknown
    # Unknown or truncated terminal records must not inherit an earlier hint.
    # Only the actual uncaught-error footer and whitespace may follow the object.
    if not re.fullmatch(
        r"[ \t\r\n]*(?:Node\.js v[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}[ \t\r\n]*)?",
        record[end.end() :],
    ):
        return unknown
    record = record[: end.end()]
    header = record.split("\n", 1)[0]
    if header.startswith("SystemError [ERR_SYSTEM_ERROR]: "):
        code = "ERR_SYSTEM_ERROR"
    else:
        match = re.match(r"Error: (EACCES|ENOENT|EMFILE): ", header)
        if match is None:
            return unknown
        code = match[1]
    outer_codes = re.findall(r"(?m)^ {2}code: '([A-Z_]{1,40})',?$", record)
    if outer_codes != [code]:
        return unknown
    result = {**unknown, "error_code": code}
    if code == "ERR_SYSTEM_ERROR":
        blocks = re.findall(r"(?m)^ {2}info: \{\n((?: {4}[^\n]{0,512}\n){1,8}) {2}\},?\n", record)
        if len(blocks) != 1:
            return result
        info = blocks[0]
        errnos = re.findall(r"(?m)^ {4}errno: (-?[0-9]{1,4}),?$", info)
        calls = re.findall(r"(?m)^ {4}syscall: '([^'\n]{1,64})',?$", info)
        if errnos == ["1"] and calls == ["uv_interface_addresses"]:
            result.update(
                errno=1, syscall="uv_interface_addresses", component="node-interface-enumeration"
            )
    else:
        expected = {"EACCES": "-13", "ENOENT": "-2", "EMFILE": "-24"}[code]
        if re.findall(r"(?m)^ {2}errno: (-?[0-9]{1,4}),?$", record) == [expected]:
            result["errno"] = int(expected)
        if re.findall(r"(?m)^ {2}syscall: '([^'\n]{1,64})',?$", record) == ["open"]:
            result["syscall"] = "open"
    return result


SMOKE = (
    "import json,os,sys;print(json.dumps({'version_matches':sys.version_info[:3]==(3,14,7),"
    "'executable_matches':sys.executable=='/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python',"
    "'cwd_matches':os.getcwd()=='/tmp/rnd-capability/product/backend',"
    "'isolated':sys.flags.isolated==1}))"
)
NODE_SMOKE = (
    "console.log(JSON.stringify({version_matches:process.versions.node==='22.23.2',"
    "executable_matches:process.execPath==='/usr/local/bin/node',"
    "cwd_matches:process.cwd()==='/tmp/rnd-capability/product/frontend/web',"
    "no_preload:process.execArgv.length===3&&process.execArgv[0]==='--input-type=module'"
    "&&process.execArgv[1]==='--eval'"
    "&&[undefined,'--max-old-space-size=3072'].includes(process.env.NODE_OPTIONS)}))"
)


def native_startup_smoke(sandbox, plan, database, identity_options, timeout, *, role="backend"):
    """Exercise the same isolated launcher, without importing candidate code."""
    receipt = {"exit_status": "unknown", "output_shapes": [], "checks": None}
    if type(role) is not str or role not in {"backend", "frontend"}:
        return receipt
    deadline = time.monotonic() + min(timeout, 5)
    token = _DEADLINE.set(deadline)
    try:

        def remaining():
            # Pinned ExecuteRequest.timeout is StrictInt. Its HTTP timeout is
            # larger, so the shared transport deadline remains authoritative.
            value = int(deadline - time.monotonic())
            if value < 1:
                raise TimeoutError("Startup interpreter diagnostic deadline")
            return value

        interpreter = (
            ["/usr/local/bin/node", "--input-type=module", "--eval", NODE_SMOKE]
            if role == "frontend"
            else ["/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python", "-I", "-S", "-c", SMOKE]
        )
        cwd = "frontend/web" if role == "frontend" else "backend"
        argv, path = redirected_command(
            product_argv(
                plan,
                interpreter,
                database,
                **identity_options,
            )
        )
        result = control_exec(
            sandbox,
            ["/bin/sh", "-c", "cd /tmp/rnd-capability/product/" + cwd + " && " + shlex.join(argv)],
            remaining(),
        )
        if type(result.exit_code) is int and 0 <= result.exit_code <= 255:
            receipt["exit_status"] = "zero" if result.exit_code == 0 else "nonzero"
        output = read_command_output(
            sandbox, path, remaining(), limit=SMOKE_OUTPUT_LIMIT, tail=True
        )
        if type(output) is not str or len(output.encode()) > SMOKE_OUTPUT_LIMIT:
            return receipt
        receipt["output_shapes"] = output_shapes(output)
        if receipt["exit_status"] == "zero":
            value = _json_unique(output)
            if (
                type(value) is dict
                and set(value)
                == {
                    "version_matches",
                    "executable_matches",
                    "cwd_matches",
                    "no_preload" if role == "frontend" else "isolated",
                }
                and all(type(v) is bool for v in value.values())
            ):
                receipt["checks"] = value
        return receipt
    except Exception:
        return receipt
    finally:
        _DEADLINE.reset(token)


PATH_ROLES = (
    "shell",
    "env",
    "setsid",
    "setpriv",
    "system_python",
    "native_python",
    "guard",
    "backend",
    "app",
    "null",
    "elf_loader",
)
KINDS = {"regular", "directory", "character", "symlink", "other", "missing", "unknown"}

# No source-supplied path, argv or environment enters this program. It only
# observes the already selected native launch chain after health has failed.
# Native dependencies are data here, not imported or executed as controller UID.
COMMON_PATHS = {
    "shell": "/bin/sh",
    "env": "/usr/bin/env",
    "setsid": "/usr/bin/setsid",
    "setpriv": "/usr/bin/setpriv",
    "system_python": "/usr/bin/python3",
    "guard": "/tmp/rnd-module-control/guard.py",
    "null": "/dev/null",
    "elf_loader": "/lib64/ld-linux-x86-64.so.2",
}
BACKEND_PATHS = {
    **COMMON_PATHS,
    "native_python": "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python",
    "backend": "/tmp/rnd-capability/product/backend",
    "app": "/tmp/rnd-capability/product/backend/app/__init__.py",
}
FRONTEND_PATHS = {
    **COMMON_PATHS,
    "native_node": "/usr/local/bin/node",
    "vite_entry": "/opt/rnd/runtime/fastapiadmin/frontend/node_modules/vite/dist/node/index.js",
    "frontend": "/tmp/rnd-capability/product/frontend/web",
    "dist_index": "/tmp/rnd-capability/product/frontend/web/dist/index.html",
    "preview_launcher": "/tmp/rnd-module-control/native-preview.mjs",
}
NODE_PATH_ROLES = tuple(FRONTEND_PATHS)
_PATH_PROBE = r"""
def kind(s):
 for check,label in ((stat.S_ISREG,'regular'),(stat.S_ISDIR,'directory'),
                     (stat.S_ISCHR,'character'),(stat.S_ISLNK,'symlink')):
  if check(s.st_mode):return label
 return 'other'
def inspect(path):
 result={'entry':'unknown','target':'unknown','dac_read':None,'dac_exec':None}
 try:result['entry']=kind(os.lstat(path))
 except FileNotFoundError:result['entry']='missing'
 except OSError:return result
 try:
  info=os.stat(path);result['target']=kind(info)
  bits=(info.st_mode>>(6 if info.st_uid==20000 else 3 if info.st_gid==20000 else 0))&7
  traversal=True
  # Account for both lexical and resolved directory chains. The app has no
  # supplementary groups or capabilities; root's os.access would be misleading.
  for start in (os.path.abspath(path),os.path.realpath(path,strict=True)):
   parent=os.path.dirname(start)
   for _ in range(64):
    current=os.stat(parent)
    access=(current.st_mode>>(6 if current.st_uid==20000 else 3 if current.st_gid==20000 else 0))&7
    traversal=traversal and stat.S_ISDIR(current.st_mode) and bool(access&1)
    if parent=='/':break
    parent=os.path.dirname(parent)
   else:traversal=False
  result['dac_read']=traversal and bool(bits&4)
  result['dac_exec']=traversal and bool(bits&1)
 except FileNotFoundError:result['target']='missing'
 except OSError:pass
 return result
def executable_format(path):
 result={'format':'unknown','loader':'unknown'}
 try:
  fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK)
  try:
   if not stat.S_ISREG(os.fstat(fd).st_mode):return result
   data=os.read(fd,65536)
  finally:os.close(fd)
  if data.startswith(b'#!'):
   result['format']='script';return result
  if not data.startswith(b'\x7fELF'):
   result['format']='other';return result
  result['format']='elf'
  if len(data)<64 or data[4]!=2 or data[5] not in (1,2):return result
  endian='<' if data[5]==1 else '>'
  offset=struct.unpack_from(endian+'Q',data,32)[0]
  size,count=struct.unpack_from(endian+'HH',data,54)
  if size!=56 or count>128 or offset+size*count>len(data):return result
  interpreters=[]
  for i in range(count):
   position=offset+i*size
   if struct.unpack_from(endian+'I',data,position)[0]!=3:continue
   start=struct.unpack_from(endian+'Q',data,position+8)[0]
   length=struct.unpack_from(endian+'Q',data,position+32)[0]
   if not 1<=length<=256 or start+length>len(data):return result
   interpreters.append(data[start:start+length])
  if not interpreters:result['loader']='none'
  elif interpreters==[b'/lib64/ld-linux-x86-64.so.2\0']:
   result['loader']='present' if os.path.isfile(paths['elf_loader']) else 'missing'
  else:result['loader']='unexpected'
 except (OSError,ValueError,struct.error):pass
 return result
result={'paths':{role:inspect(path) for role,path in paths.items()},
        'native_binary':executable_format(binary_path)}
output=json.dumps(result,separators=(',',':'))
assert len(output.encode())<=2048
print(output)
"""
PROBE = (
    "import json,os,stat,struct\npaths="
    + repr(BACKEND_PATHS)
    + "\nbinary_path=paths['native_python']\n"
    + _PATH_PROBE
)
NODE_PROBE = (
    "import json,os,stat,struct\npaths="
    + repr(FRONTEND_PATHS)
    + "\nbinary_path=paths['native_node']\n"
    + _PATH_PROBE
)


def native_startup_paths(sandbox, timeout, *, role="backend"):
    """Return a fresh finite receipt or unknown; never serialize probe failures."""
    unknown = {"status": "unknown"}
    if type(role) is not str or role not in {"backend", "frontend"}:
        return unknown
    token = _DEADLINE.set(time.monotonic() + min(timeout, 5))
    try:
        budget = int(min(timeout, 5))
        if budget < 1:
            return unknown
        probe = NODE_PROBE if role == "frontend" else PROBE
        result = control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", probe], budget)
        if type(result.exit_code) is not int or result.exit_code != 0:
            return unknown
        if type(result.result) is not str or len(result.result.encode()) > 2048:
            return unknown
        value = _json_unique(result.result)
        if type(value) is not dict or set(value) != {"paths", "native_binary"}:
            return unknown
        paths = value["paths"]
        expected_roles = NODE_PATH_ROLES if role == "frontend" else PATH_ROLES
        if type(paths) is not dict or set(paths) != set(expected_roles):
            return unknown
        for row in paths.values():
            if type(row) is not dict or set(row) != {"entry", "target", "dac_read", "dac_exec"}:
                return unknown
            if any(type(row[k]) is not str or row[k] not in KINDS for k in ("entry", "target")):
                return unknown
            if any(
                row[k] is not None and type(row[k]) is not bool for k in ("dac_read", "dac_exec")
            ):
                return unknown
        binary = value["native_binary"]
        if type(binary) is not dict or set(binary) != {"format", "loader"}:
            return unknown
        if type(binary["format"]) is not str or binary["format"] not in {
            "elf",
            "script",
            "other",
            "unknown",
        }:
            return unknown
        if type(binary["loader"]) is not str or binary["loader"] not in {
            "present",
            "missing",
            "unexpected",
            "none",
            "unknown",
        }:
            return unknown
        return {"status": "observed", **value}
    except Exception:
        return unknown
    finally:
        _DEADLINE.reset(token)
````
