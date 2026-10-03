# scripts/capability_guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_guard；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `Ruleset`（L23–L28）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Port`（L31–L32）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `restrict_tcp`（L35–L81）：接收`bind_ports`、`connect_ports`。 控制顺序：L36按`sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}`分支；L37抛异常，停止当前正常路径；L38按`any( not 1024 <= port <= 65535 or port in FORBIDDEN_PORTS for port in bind_ports \| c…`分支；L41抛异常，停止当前正常路径；L45按`abi < 6`分支；L46抛异常，停止当前正常路径；L47按`libc.prctl(38, 1, 0, 0, 0)`分支；L48抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`platform.machine`、`RuntimeError`、`any`、`ctypes.CDLL`、`libc.syscall`、`libc.prctl`、`Ruleset`、`ctypes.byref`、`ctypes.sizeof`等。 返回路径：L81的`int(abi)`。
- `daemon_denied`（L84–L105）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85遍历`[ (socket.AF_INET, ("127.0.0.1", 2280)), (socket.AF_INET6, ("::1"…`；L94按`exc.errno == errno.EACCES`分支；L97按`family == socket.AF_INET6 and exc.errno in { errno.EAFNOSUPPORT, errno.EPROTONOSUPPOR…`分支；L102抛异常，停止当前正常路径；L105抛异常，停止当前正常路径。 调用`socket.socket`、`connection.settimeout`、`connection.connect`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L108–L130）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L109按`len(sys.argv) < 4`分支；L110抛异常，停止当前正常路径；L115按`sys.argv[3:] == ["--probe"]`分支；L128按`sys.argv[3] != "--" or len(sys.argv) < 5`分支；L129抛异常，停止当前正常路径。 调用`len`、`RuntimeError`、`int`、`sys.argv[1].split`、`sys.argv[2].split`、`restrict_tcp`、`daemon_denied`、`print`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/capability_guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L140。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5300`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3170b777d2d0f37396a5470fa34cea8f13c448d1121c08dba3385965631f8b53"} -->
````python
# scripts/capability_guard.py
"""Trusted child-process TCP restriction, before any generated command executes.

Run under the dedicated unprivileged product UID with no_new_privs and no
capabilities. Requires Linux Landlock ABI 6+, never silently degrades. This
module is copied into the disposable sandbox by trusted control code, not
imported from the product. Root callers must use the system Python with -I -S.
"""

import ctypes
import errno
import json
import os
import platform
import socket
import stat
import sys

CREATE, ADD, RESTRICT = 444, 445, 446
BIND, CONNECT = 1, 2
FORBIDDEN_PORTS = {2280}  # pinned Daytona daemon control API, not a product port


class Ruleset(ctypes.Structure):
    _fields_ = [
        ("filesystem", ctypes.c_uint64),
        ("network", ctypes.c_uint64),
        ("scoped", ctypes.c_uint64),
    ]


class Port(ctypes.Structure):
    _fields_ = [("access", ctypes.c_uint64), ("port", ctypes.c_uint64)]


def restrict_tcp(bind_ports, connect_ports):
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise RuntimeError("Unsupported isolated kernel architecture")
    if any(
        not 1024 <= port <= 65535 or port in FORBIDDEN_PORTS for port in bind_ports | connect_ports
    ):
        raise RuntimeError("Reserved or invalid isolated port")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    abi = libc.syscall(CREATE, 0, 0, 1)
    if abi < 6:
        raise RuntimeError("Landlock TCP and abstract Unix restrictions require ABI 6 or newer")
    if libc.prctl(38, 1, 0, 0, 0):  # PR_SET_NO_NEW_PRIVS
        raise RuntimeError("Cannot enforce no_new_privs")
    attributes = Ruleset(0, BIND | CONNECT, 3)  # abstract Unix and signal scope
    descriptor = libc.syscall(CREATE, ctypes.byref(attributes), ctypes.sizeof(attributes), 0)
    if descriptor < 0:
        raise RuntimeError("Cannot create TCP restrictions")
    try:
        for port in sorted(bind_ports | connect_ports):
            rule = Port(
                (BIND if port in bind_ports else 0) | (CONNECT if port in connect_ports else 0),
                port,
            )
            if libc.syscall(ADD, descriptor, 2, ctypes.byref(rule), 0):
                raise RuntimeError("Cannot configure isolated TCP ports")
        if libc.syscall(RESTRICT, descriptor, 0):
            raise RuntimeError("Cannot enforce TCP restrictions")
    finally:
        os.close(descriptor)
    # No socket/control descriptor inherited from the launcher may bypass connect.
    for name in os.listdir("/proc/self/fd"):
        descriptor = int(name)
        if descriptor < 3:
            mode = os.fstat(descriptor).st_mode
            # No controlling TTY or arbitrary device inherited from root sessions.
            if os.isatty(descriptor) or stat.S_ISSOCK(mode):
                raise RuntimeError("Terminal/socket standard stream is not an isolated launch")
            if stat.S_ISCHR(mode) and os.readlink(f"/proc/self/fd/{descriptor}") != "/dev/null":
                raise RuntimeError("Unexpected character device in isolated standard streams")
        else:
            try:
                os.close(descriptor)
            except OSError as exc:
                if exc.errno != errno.EBADF:
                    raise
    return int(abi)


def daemon_denied():
    for family, destination in [
        (socket.AF_INET, ("127.0.0.1", 2280)),
        (socket.AF_INET6, ("::1", 2280)),
    ]:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as connection:
                connection.settimeout(1)
                connection.connect(destination)
        except OSError as exc:
            if exc.errno == errno.EACCES:
                continue
            # A disabled IPv6 stack has no reachable IPv6 daemon surface.
            if family == socket.AF_INET6 and exc.errno in {
                errno.EAFNOSUPPORT,
                errno.EPROTONOSUPPORT,
            }:
                continue
            raise RuntimeError(
                "Daemon denial must come from access control, not refused routing"
            ) from None
        raise RuntimeError("Product can reach the sandbox control daemon")


def main():
    if len(sys.argv) < 4:
        raise RuntimeError("Guard requires explicit port policy and command")
    bind_ports = {int(value) for value in sys.argv[1].split(",") if value}
    connect_ports = {int(value) for value in sys.argv[2].split(",") if value}
    abi = restrict_tcp(bind_ports, connect_ports)
    daemon_denied()
    if sys.argv[3:] == ["--probe"]:
        print(
            json.dumps(
                {
                    "landlock_abi": abi,
                    "daemon_tcp_denied": True,
                    "no_new_privs": True,
                    "inherited_fds_closed": True,
                    "standard_streams_detached": True,
                }
            )
        )
        return
    if sys.argv[3] != "--" or len(sys.argv) < 5:
        raise RuntimeError("Missing isolated command separator")
    os.execvpe(sys.argv[4], sys.argv[4:], os.environ)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(
            "Isolated command guard unavailable; no product command was executed", file=sys.stderr
        )
        sys.exit(78)
````
