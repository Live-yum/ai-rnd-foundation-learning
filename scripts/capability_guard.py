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
