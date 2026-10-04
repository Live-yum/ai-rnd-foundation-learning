# workbench/native_ports.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生后端端口分配与跨重启租约。** 读取本机TCP动态源端口范围，自动选择范围外的空闲非特权端口。产品锁与端口锁覆盖构建、启动、重启和清理，副本路径绑定回执稳定记录端口；显式端口不回退，冲突明确失败，不改主机网络配置。

**对应关系：** native_lab/ci_native_runtime/独立run.py → backend_port_lease → 后端配置、前端构建与验收回执；test_native_ports。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `dynamic_tcp_range`（L27–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Read the IPv4 source-port range; unknown/unreadable hosts fail closed.。 控制顺序：L30按`system == "Linux"`分支；L32按`system == "Darwin"`分支；L39按`system == "Windows"`分支；L47按`len(rows) != 2`分支；L48抛异常，停止当前正常路径；L52抛异常，停止当前正常路径；L53按`len(values) != 2`分支；L54抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`platform.system`、`Path("/proc/sys/net/ipv4/ip_local_port_range").read_text().split`、`Path("/proc/sys/net/ipv4/ip_local_port_range").read_text`、`Path`、`subprocess.check_output( ["sysctl", "-n", f"net.inet.ip.portrange…`、`subprocess.check_output`、`subprocess.check_output( ["netsh", "interface", "ipv4", "show", "…`、`re.findall`、`len`等。 返回路径：L58的`first, last`。
- `_valid_port`（L61–L67）：接收`value`。 控制顺序：L62按`isinstance(value, bool) or not str(value).isascii() or not str(value).isdecimal()`分支；L63抛异常，停止当前正常路径；L65按`not 1024 <= port <= 65535`分支；L66抛异常，停止当前正常路径。 调用`isinstance`、`str(value).isascii`、`str`、`str(value).isdecimal`、`ValueError`、`int`。 返回路径：L67的`port`。
- `saved_backend_port`（L70–L86）：接收`receipt`。 源码说明：Read a bounded path-bound receipt; copies do not inherit port ownership.。 控制顺序：L73按`receipt.is_symlink() or receipt.is_junction()`分支；L74抛异常，停止当前正常路径；L75按`not receipt.exists()`分支；L79按`len(raw) > 4096`分支；L80抛异常，停止当前正常路径；L82按`not isinstance(value, dict) or value.get("format") != 1`分支；L83抛异常，停止当前正常路径；L84按`value.get("owner") != str(receipt.resolve())`分支。 调用`Path`、`receipt.is_symlink`、`receipt.is_junction`、`ValueError`、`receipt.exists`、`receipt.open`、`stream.read`、`len`、`json.loads`等。 返回路径：L76的`None`；L85的`None`；L86的`_valid_port(value.get("port"))`。
- `_bindable`（L89–L101）：接收`port`。 控制顺序：L91按`os.name != "nt"`分支；L93按`hasattr(socket, "SO_EXCLUSIVEADDRUSE")`分支；L98按`error.errno in {errno.EADDRINUSE, errno.EACCES}`分支；L100抛异常，停止当前正常路径。 调用`socket.socket`、`sock.setsockopt`、`hasattr`、`sock.bind`。 返回路径：L99的`False`；L101的`True`。
- `_backend_port_lease`（L105–L163）：接收`receipt`、`explicit`。 源码说明：Keep one selected port stable for this product's entire invocation. Automatic choices persist in runtime-only state. Copied receipts are not adopted by a new path. Explicit configuration always means 。 控制顺序：L117按`not fixed`分支；L119按`selected is not None and dynamic[0] <= selected <= dynamic[1]`分支；L120抛异常，停止当前正常路径；L128按`not stat.S_ISDIR(info.st_mode) or directory.is_junction() or (os.name != "nt" and (in…`分支；L133抛异常，停止当前正常路径；L143按`selected is None`分支；L145遍历`candidates`；L150按`selected is not None`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path(receipt).resolve`、`Path`、`str`、`_valid_port`、`dynamic_tcp_range`、`saved_backend_port`、`ValueError`、`tempfile.gettempdir`、`hasattr`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `backend_port_lease`（L167–L182）：接收`receipt`、`explicit`。 控制顺序：L169按`receipt.is_symlink() or receipt.is_junction()`分支；L170抛异常，停止当前正常路径；L177抛异常，停止当前正常路径。 调用`Path`、`receipt.is_symlink`、`receipt.is_junction`、`ValueError`、`receipt.resolve`、`receipt.parent.mkdir`、`FileLock`、`str`、`product_lock.acquire`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。

</details>

**创建路径：** `workbench/native_ports.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L182。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6848`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_ports.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8ab2d6c94d221f4866d3b97ca9c82f0fc81c7c54e6b09ac3a890c2b532677645"} -->
````python
# workbench/native_ports.py
"""Per-product backend leases outside automatic TCP client source-port ranges.

A bind-and-close check alone cannot reserve an ephemeral port: Java may acquire
that same port for PostgreSQL/Redis before Tomcat binds. Never change host network
settings. Cooperating copies hold a file lease across builds and restarts; an
unrelated process racing the bind still fails closed in running_backend.
"""

import errno
import json
import os
import platform
import random
import re
import socket
import stat
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from filelock import FileLock, Timeout

from workbench.filesystem import write_json


def dynamic_tcp_range():
    """Read the IPv4 source-port range; unknown/unreadable hosts fail closed."""
    system = platform.system()
    if system == "Linux":
        values = Path("/proc/sys/net/ipv4/ip_local_port_range").read_text().split()
    elif system == "Darwin":
        values = [
            subprocess.check_output(
                ["sysctl", "-n", f"net.inet.ip.portrange.{name}"], text=True, timeout=10
            ).strip()
            for name in ("first", "last")
        ]
    elif system == "Windows":
        output = subprocess.check_output(
            ["netsh", "interface", "ipv4", "show", "dynamicport", "tcp"],
            timeout=10,
        ).decode("ascii", errors="replace")
        # Labels are localized, but the final two colon-delimited integers are
        # the start and number of ports on supported Windows versions.
        rows = re.findall(r":\s*(\d+)\s*$", output, re.MULTILINE)
        if len(rows) != 2:
            raise ValueError("Cannot read Windows dynamic TCP port range")
        first, count = map(int, rows)
        values = [first, first + count - 1]
    else:
        raise ValueError("Unknown dynamic TCP port range; configure an explicit backend port")
    if len(values) != 2:
        raise ValueError("Invalid dynamic TCP port range")
    first, last = map(int, values)
    if not 1 <= first <= last <= 65535:
        raise ValueError("Invalid dynamic TCP port range")
    return first, last


def _valid_port(value):
    if isinstance(value, bool) or not str(value).isascii() or not str(value).isdecimal():
        raise ValueError("Invalid native backend port")
    port = int(value)
    if not 1024 <= port <= 65535:
        raise ValueError("Invalid native backend port")
    return port


def saved_backend_port(receipt):
    """Read a bounded path-bound receipt; copies do not inherit port ownership."""
    receipt = Path(receipt)
    if receipt.is_symlink() or receipt.is_junction():
        raise ValueError("Backend port receipt must not be a link")
    if not receipt.exists():
        return None
    with receipt.open("rb") as stream:
        raw = stream.read(4097)
    if len(raw) > 4096:
        raise ValueError("Oversized backend port receipt")
    value = json.loads(raw)
    if not isinstance(value, dict) or value.get("format") != 1:
        raise ValueError("Invalid backend port receipt")
    if value.get("owner") != str(receipt.resolve()):
        return None
    return _valid_port(value.get("port"))


def _bindable(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if os.name != "nt":
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        elif hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError as error:
            if error.errno in {errno.EADDRINUSE, errno.EACCES}:
                return False
            raise
    return True


@contextmanager
def _backend_port_lease(receipt, explicit=None):
    """Keep one selected port stable for this product's entire invocation.

    Automatic choices persist in runtime-only state. Copied receipts are not
    adopted by a new path. Explicit configuration always means that exact port,
    even inside the dynamic range, and never silently falls back on conflict.
    """
    receipt = Path(receipt).resolve()
    owner = str(receipt)
    fixed = explicit is not None
    selected = _valid_port(explicit) if fixed else None
    dynamic = None if fixed else dynamic_tcp_range()
    if not fixed:
        selected = saved_backend_port(receipt)
        if selected is not None and dynamic[0] <= selected <= dynamic[1]:
            raise ValueError("Saved backend port is now inside the dynamic TCP range")
    # Locks only coordinate launches by this user. Foreign users/processes are
    # never stopped; the actual socket check remains authoritative.
    directory = Path(tempfile.gettempdir()) / (
        "rnd-native-ports-" + str(os.getuid() if hasattr(os, "getuid") else "user")
    )
    directory.mkdir(mode=0o700, exist_ok=True)
    info = directory.lstat()
    if (
        not stat.S_ISDIR(info.st_mode)
        or directory.is_junction()
        or (os.name != "nt" and (info.st_uid != os.getuid() or info.st_mode & 0o077))
    ):
        raise ValueError("Unsafe native backend port lock directory")
    candidates = (
        [selected]
        if selected is not None
        else [
            port
            for port in range(1024, 65536)
            if port != 5173 and not dynamic[0] <= port <= dynamic[1]
        ]
    )
    if selected is None:
        random.SystemRandom().shuffle(candidates)
    for port in candidates:
        lock = FileLock(directory / f"{port}.lock")
        try:
            lock.acquire(timeout=0)
        except Timeout:
            if selected is not None:
                raise RuntimeError("Native backend port lease is already in use") from None
            continue
        try:
            if not _bindable(port):
                if selected is not None:
                    raise RuntimeError("Native backend port is already occupied")
                continue
            write_json(receipt, {"format": 1, "owner": owner, "port": port, "explicit": fixed})
            yield port
            return
        finally:
            lock.release()
    raise RuntimeError("No available backend port outside the dynamic TCP range")


@contextmanager
def backend_port_lease(receipt, explicit=None):
    receipt = Path(receipt)
    if receipt.is_symlink() or receipt.is_junction():
        raise ValueError("Backend port receipt must not be a link")
    receipt = receipt.resolve()
    receipt.parent.mkdir(parents=True, exist_ok=True)
    product_lock = FileLock(str(receipt) + ".lock")
    try:
        product_lock.acquire(timeout=0)
    except Timeout:
        raise RuntimeError("Native product port lease is already in use") from None
    try:
        with _backend_port_lease(receipt, explicit) as port:
            yield port
    finally:
        product_lock.release()
````
