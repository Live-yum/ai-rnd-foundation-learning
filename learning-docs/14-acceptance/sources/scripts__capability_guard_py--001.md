# scripts/capability_guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.capability_guard；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `restrict_resources`（L32–L43）：接收`native`。 源码说明：Lower only this disposable child's limits; never changes host policy.。 控制顺序：L37按`native`分支；L39遍历`limits.items()`。 调用`dict`、`limits.update`、`limits.items`、`getattr`、`resource.getrlimit`、`min`、`resource.setrlimit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Ruleset`（L46–L51）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Port`（L54–L55）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `PathRule`（L58–L60）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SyscallComparison`（L63–L69）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SeccompVersion`（L72–L73）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `restrict_sockets`（L76–L152）：接收`allow_tcp_connect`。 源码说明：libseccomp ABI2: only Unix/TCP stream sockets, no io_uring bypass. Official ABI: github.com/seccomp/libseccomp/blob/v2.5.5/include/seccomp.h.in Only this candidate process and its descendants receive 。 控制顺序：L88按`sys.platform != "linux" or platform.machine() not in architectures or ctypes.sizeof(c…`分支；L93抛异常，停止当前正常路径；L99按`api.seccomp_arch_native() != expected_arch or version.major != 2 or version.minor < 5`分支；L100抛异常，停止当前正常路径；L117按`not context`分支；L118抛异常，停止当前正常路径；L134遍历`("socket", "socketpair")`；L139遍历`(0, 3, 4, 5, 6, 7, 8, 9)`。后续分支沿下方源码相同行号继续阅读。 调用`platform.machine`、`ctypes.sizeof`、`RuntimeError`、`ctypes.CDLL`、`ctypes.POINTER`、`api.seccomp_version`、`api.seccomp_arch_native`、`api.seccomp_init`、`deny`等。 返回路径：L150的`{"major": version.major, "minor": version.minor, "micro": version.micro}`。
- `restrict_sockets.deny`（L121–L132）：接收`name`、`*conditions`。 控制顺序：L123按`number < 0`分支；L124抛异常，停止当前正常路径；L126按`api.seccomp_rule_add_array( context, 0x00050000 \| errno.EPERM, number, len(condition…`分支；L132抛异常，停止当前正常路径。 调用`api.seccomp_syscall_resolve_name`、`name.encode`、`RuntimeError`、`SyscallComparison * len(conditions)`、`len`、`api.seccomp_rule_add_array`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `restrict_tcp`（L155–L209）：接收`bind_ports`、`connect_ports`、`filesystem`。 控制顺序：L156按`sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}`分支；L157抛异常，停止当前正常路径；L158按`any( not 1024 <= port <= 65535 or port in FORBIDDEN_PORTS for port in bind_ports \| c…`分支；L161抛异常，停止当前正常路径；L165按`abi < 6`分支；L166抛异常，停止当前正常路径；L167按`libc.prctl(38, 1, 0, 0, 0)`分支；L168抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`platform.machine`、`RuntimeError`、`any`、`ctypes.CDLL`、`libc.syscall`、`libc.prctl`、`Ruleset`、`ctypes.byref`、`ctypes.sizeof`等。 返回路径：L209的`int(abi)`。
- `daemon_denied`（L212–L233）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L213遍历`[ (socket.AF_INET, ("127.0.0.1", 2280)), (socket.AF_INET6, ("::1"…`；L222按`exc.errno in {errno.EACCES, errno.EPERM}`分支；L225按`family == socket.AF_INET6 and exc.errno in { errno.EAFNOSUPPORT, errno.EPROTONOSUPPOR…`分支；L230抛异常，停止当前正常路径；L233抛异常，停止当前正常路径。 调用`socket.socket`、`connection.settimeout`、`connection.connect`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `main`（L236–L264）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L237按`len(sys.argv) < 4`分支；L238抛异常，停止当前正常路径；L246按`sys.argv[3:] == ["--probe"]`分支；L262按`sys.argv[3] != "--" or len(sys.argv) < 5`分支；L263抛异常，停止当前正常路径。 调用`len`、`RuntimeError`、`int`、`sys.argv[1].split`、`sys.argv[2].split`、`restrict_tcp`、`restrict_resources`、`restrict_sockets`、`bool`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/capability_guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L274。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`11068`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/capability_guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b8c93bf74ff15d770d89adb173eef80a4f976ade46b4e7f139662897187e79c9"} -->
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
WRITABLE_ROOT = "/tmp/rnd-capability"
WRITE_ACCESS = sum(1 << bit for bit in (1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14))
RESOURCE_LIMITS = {
    "RLIMIT_CPU": 300,
    "RLIMIT_FSIZE": 32 * 1024 * 1024,
    "RLIMIT_NPROC": 128,
    "RLIMIT_NOFILE": 256,
    "RLIMIT_CORE": 0,
}


def restrict_resources(*, native=False):
    """Lower only this disposable child's limits; never changes host policy."""
    import resource

    limits = dict(RESOURCE_LIMITS)
    if native:
        limits.update(RLIMIT_CPU=900, RLIMIT_FSIZE=128 * 1024 * 1024, RLIMIT_NPROC=256)
    for name, ceiling in limits.items():
        key = getattr(resource, name)
        soft, hard = resource.getrlimit(key)
        ceiling = min(ceiling, hard) if hard != resource.RLIM_INFINITY else ceiling
        resource.setrlimit(key, (ceiling, ceiling))


class Ruleset(ctypes.Structure):
    _fields_ = [
        ("filesystem", ctypes.c_uint64),
        ("network", ctypes.c_uint64),
        ("scoped", ctypes.c_uint64),
    ]


class Port(ctypes.Structure):
    _fields_ = [("access", ctypes.c_uint64), ("port", ctypes.c_uint64)]


class PathRule(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("access", ctypes.c_uint64), ("parent_fd", ctypes.c_int)]


class SyscallComparison(ctypes.Structure):
    _fields_ = [
        ("arg", ctypes.c_uint),
        ("op", ctypes.c_uint),
        ("datum_a", ctypes.c_uint64),
        ("datum_b", ctypes.c_uint64),
    ]


class SeccompVersion(ctypes.Structure):
    _fields_ = [("major", ctypes.c_uint), ("minor", ctypes.c_uint), ("micro", ctypes.c_uint)]


def restrict_sockets(*, allow_tcp_connect=False):
    """libseccomp ABI2: only Unix/TCP stream sockets, no io_uring bypass.

    Official ABI: github.com/seccomp/libseccomp/blob/v2.5.5/include/seccomp.h.in
    Only this candidate process and its descendants receive the filter. The
    admitted SQLite profile denies connect outright, not merely by destination
    port. A future PostgreSQL profile also needs independent address/egress proof.
    """
    architectures = {
        "x86_64": (0xC000003E, "/lib/x86_64-linux-gnu/libseccomp.so.2"),
        "aarch64": (0xC00000B7, "/lib/aarch64-linux-gnu/libseccomp.so.2"),
    }
    if (
        sys.platform != "linux"
        or platform.machine() not in architectures
        or ctypes.sizeof(ctypes.c_void_p) != 8
    ):
        raise RuntimeError("Unsupported seccomp architecture")
    expected_arch, library = architectures[platform.machine()]
    api = ctypes.CDLL(library, use_errno=True)
    api.seccomp_arch_native.restype = ctypes.c_uint32
    api.seccomp_version.restype = ctypes.POINTER(SeccompVersion)
    version = api.seccomp_version().contents
    if api.seccomp_arch_native() != expected_arch or version.major != 2 or version.minor < 5:
        raise RuntimeError("Unsupported libseccomp ABI")
    api.seccomp_init.argtypes = [ctypes.c_uint32]
    api.seccomp_init.restype = ctypes.c_void_p
    api.seccomp_release.argtypes = [ctypes.c_void_p]
    api.seccomp_load.argtypes = [ctypes.c_void_p]
    api.seccomp_load.restype = ctypes.c_int
    api.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    api.seccomp_syscall_resolve_name.restype = ctypes.c_int
    api.seccomp_rule_add_array.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.POINTER(SyscallComparison),
    ]
    api.seccomp_rule_add_array.restype = ctypes.c_int
    context = api.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW; restricted syscalls below.
    if not context:
        raise RuntimeError("Cannot create seccomp context")
    try:

        def deny(name, *conditions):
            number = api.seccomp_syscall_resolve_name(name.encode("ascii"))
            if number < 0:
                raise RuntimeError("Required network syscall is unknown")
            comparisons = (SyscallComparison * len(conditions))(*conditions)
            if (
                api.seccomp_rule_add_array(
                    context, 0x00050000 | errno.EPERM, number, len(conditions), comparisons
                )
                != 0
            ):
                raise RuntimeError("Cannot install required socket rule")

        for name in ("socket", "socketpair"):
            # libseccomp allows each argument only once in a rule, so deny
            # disjoint domains/types with separate rules rather than a broken
            # multi-comparison allowlist. High socket flags cannot evade mask.
            deny(name, SyscallComparison(0, 6, 10, 0))  # SCMP_CMP_GT
            for domain in (0, 3, 4, 5, 6, 7, 8, 9):
                deny(name, SyscallComparison(0, 4, domain, 0))
            for kind in (0, *range(2, 16)):
                deny(name, SyscallComparison(1, 7, 0xF, kind))
        deny("socketpair", SyscallComparison(0, 1, 1, 0))  # only AF_UNIX
        for name in ("io_uring_setup", "io_uring_enter", "io_uring_register"):
            deny(name)
        if not allow_tcp_connect:
            deny("connect")
        if api.seccomp_load(context) != 0:
            raise RuntimeError("Kernel refused the socket security filter")
        return {"major": version.major, "minor": version.minor, "micro": version.micro}
    finally:
        api.seccomp_release(context)


def restrict_tcp(bind_ports, connect_ports, *, filesystem=False):
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
    attributes = Ruleset(WRITE_ACCESS if filesystem else 0, BIND | CONNECT, 3)
    descriptor = libc.syscall(CREATE, ctypes.byref(attributes), ctypes.sizeof(attributes), 0)
    if descriptor < 0:
        raise RuntimeError("Cannot create TCP restrictions")
    try:
        if filesystem:
            parent = os.open(WRITABLE_ROOT, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                rule = PathRule(WRITE_ACCESS, parent)
                if libc.syscall(ADD, descriptor, 1, ctypes.byref(rule), 0):
                    raise RuntimeError("Cannot restrict candidate filesystem writes")
            finally:
                os.close(parent)
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
            if exc.errno in {errno.EACCES, errno.EPERM}:
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
    probe_only = sys.argv[3:] == ["--probe"]
    abi = restrict_tcp(bind_ports, connect_ports, filesystem=not probe_only)
    restrict_resources(native=55433 in connect_ports)
    seccomp = restrict_sockets(allow_tcp_connect=bool(connect_ports))
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
                    "socket_filter": "libseccomp-stream-only-v1",
                    "socket_filter_enforced": True,
                    "libseccomp": seccomp,
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
