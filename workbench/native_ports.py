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
