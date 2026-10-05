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


SMOKE = (
    "import json,os,sys;print(json.dumps({'version_matches':sys.version_info[:3]==(3,14,7),"
    "'executable_matches':sys.executable=='/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python',"
    "'cwd_matches':os.getcwd()=='/tmp/rnd-capability/product/backend',"
    "'isolated':sys.flags.isolated==1}))"
)


def native_startup_smoke(sandbox, plan, database, identity_options, timeout):
    """Exercise the same isolated launcher, without importing candidate code."""
    receipt = {"exit_status": "unknown", "output_shapes": [], "checks": None}
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

        argv, path = redirected_command(
            product_argv(
                plan,
                ["/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python", "-I", "-S", "-c", SMOKE],
                database,
                **identity_options,
            )
        )
        result = control_exec(
            sandbox,
            ["/bin/sh", "-c", "cd /tmp/rnd-capability/product/backend && " + shlex.join(argv)],
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
                == {"version_matches", "executable_matches", "cwd_matches", "isolated"}
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
PROBE = r"""
import json,os,stat,struct
paths={
 'shell':'/bin/sh','env':'/usr/bin/env','setsid':'/usr/bin/setsid',
 'setpriv':'/usr/bin/setpriv','system_python':'/usr/bin/python3',
 'native_python':'/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python',
 'guard':'/tmp/rnd-module-control/guard.py',
 'backend':'/tmp/rnd-capability/product/backend',
 'app':'/tmp/rnd-capability/product/backend/app/__init__.py',
 'null':'/dev/null','elf_loader':'/lib64/ld-linux-x86-64.so.2',
}
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
        'native_binary':executable_format(paths['native_python'])}
output=json.dumps(result,separators=(',',':'))
assert len(output.encode())<=2048
print(output)
"""


def native_startup_paths(sandbox, timeout):
    """Return a fresh finite receipt or unknown; never serialize probe failures."""
    unknown = {"status": "unknown"}
    token = _DEADLINE.set(time.monotonic() + min(timeout, 5))
    try:
        budget = int(min(timeout, 5))
        if budget < 1:
            return unknown
        result = control_exec(sandbox, ["/usr/bin/python3", "-I", "-S", "-c", PROBE], budget)
        if type(result.exit_code) is not int or result.exit_code != 0:
            return unknown
        if type(result.result) is not str or len(result.result.encode()) > 2048:
            return unknown
        value = _json_unique(result.result)
        if type(value) is not dict or set(value) != {"paths", "native_binary"}:
            return unknown
        paths = value["paths"]
        if type(paths) is not dict or set(paths) != set(PATH_ROLES):
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
