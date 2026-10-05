# workbench/capability_startup_paths.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_isolation`、`workbench.daytona_sessions`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `normalize_sgr`（L22–L24）：接收`output`。 源码说明：Remove only bounded numeric SGR, never OSC or arbitrary terminal commands.。 调用`SGR.sub`。 返回路径：L24的`SGR.sub("", output)`。
- `_json_unique`（L27–L36）：接收`text`。 调用`json.loads`。 返回路径：L36的`json.loads(text, object_pairs_hook=pairs)`。
- `_json_unique.pairs`（L28–L34）：接收`values`。 控制顺序：L30遍历`values`；L31按`key in result`分支；L32抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L34的`result`。
- `output_shapes`（L39–L65）：接收`output`。 源码说明：Untrusted format hints, with no captured message or dynamic path.。 控制顺序：L41按`type(output) is not str`分支。 调用`type`、`normalize_sgr`、`patterns.items`、`re.search`。 返回路径：L42的`[]`；L61的`[ label for label, pattern in patterns.items() if re.search(pattern, raw if label == "ansi…`。
- `native_startup_smoke`（L76–L125）：接收`sandbox`、`plan`、`database`、`identity_options`、`timeout`。 源码说明：Exercise the same isolated launcher, without importing candidate code.。 控制顺序：L104按`type(result.exit_code) is int and 0 <= result.exit_code <= 255`分支；L109按`type(output) is not str or len(output.encode()) > SMOKE_OUTPUT_LIMIT`分支；L112按`receipt["exit_status"] == "zero"`分支；L114按`type(value) is dict and set(value) == {"version_matches", "executable_matches", "cwd_…`分支。 调用`time.monotonic`、`min`、`_DEADLINE.set`、`redirected_command`、`product_argv`、`control_exec`、`shlex.join`、`remaining`、`type`等。 返回路径：L110的`receipt`；L121的`receipt`；L123的`receipt`。
- `native_startup_smoke.remaining`（L83–L89）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L87按`value < 1`分支；L88抛异常，停止当前正常路径。 调用`int`、`time.monotonic`、`TimeoutError`。 返回路径：L89的`value`。
- `native_startup_paths`（L227–L277）：接收`sandbox`、`timeout`。 源码说明：Return a fresh finite receipt or unknown; never serialize probe failures.。 控制顺序：L233按`budget < 1`分支；L236按`type(result.exit_code) is not int or result.exit_code != 0`分支；L238按`type(result.result) is not str or len(result.result.encode()) > 2048`分支；L241按`type(value) is not dict or set(value) != {"paths", "native_binary"}`分支；L244按`type(paths) is not dict or set(paths) != set(PATH_ROLES)`分支；L246遍历`paths.values()`；L247按`type(row) is not dict or set(row) != {"entry", "target", "dac_read", "dac_exec"}`分支；L249按`any(type(row[k]) is not str or row[k] not in KINDS for k in ("entry", "target"))`分支。后续分支沿下方源码相同行号继续阅读。 调用`_DEADLINE.set`、`time.monotonic`、`min`、`int`、`control_exec`、`type`、`len`、`result.result.encode`、`_json_unique`等。 返回路径：L234的`unknown`；L237的`unknown`；L239的`unknown`。

</details>

**创建路径：** `workbench/capability_startup_paths.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L277。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10653`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_startup_paths.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1597478308b4480ec90a0600b15d5b9af7f4999c13f146f1f052c652563d49b6"} -->
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


def normalize_sgr(output):
    """Remove only bounded numeric SGR, never OSC or arbitrary terminal commands."""
    return SGR.sub("", output)


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
    output = output[:8000]
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
````
