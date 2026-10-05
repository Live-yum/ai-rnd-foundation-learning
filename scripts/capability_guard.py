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
# WRITE_FILE, REMOVE_FILE, MAKE_REG, REFER, TRUNCATE. In particular, this does
# not admit MAKE_DIR/SYM/CHAR/BLOCK/FIFO/SOCK or REMOVE_DIR. POSIX SemLock needs
# the temporary ordinary file + link/unlink sequence, not just a named prefix.
NATIVE_SHM_ACCESS = sum(1 << bit for bit in (1, 5, 8, 13, 14))
NATIVE_SHM_BYTES = 64 * 1024 * 1024
NATIVE_SHM_EVIDENCE = {
    "profile": "native-private-shm-v1",
    "actual_mount_verified": True,
    "regular_files_only": True,
    "size_bytes": NATIVE_SHM_BYTES,
    "noexec": True,
    "nosuid": True,
    "nodev": True,
    "uid": 0,
    "gid": 0,
    "mode": 0o1777,
}
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


def _read_proc(path):
    with open(path, encoding="ascii") as stream:
        value = stream.read(1024 * 1024 + 1)
    if len(value) > 1024 * 1024:
        raise RuntimeError("Shared memory mount evidence exceeds its bound")
    return value


def _native_shm_mount_identity(descriptor):
    """Bind the opened directory to its own mount, never a matching path alone."""
    identifiers = [
        line.split(":", 1)[1].strip()
        for line in _read_proc(f"/proc/self/fdinfo/{descriptor}").splitlines()
        if line.startswith("mnt_id:")
    ]
    if len(identifiers) != 1 or not identifiers[0].isdecimal() or int(identifiers[0]) <= 0:
        raise RuntimeError("Shared memory descriptor lacks a unique mount identity")
    rows = []
    for line in _read_proc("/proc/self/mountinfo").splitlines():
        sides = line.split(" - ")
        if len(sides) != 2:
            raise RuntimeError("Malformed shared memory mount evidence")
        before, after = sides[0].split(), sides[1].split()
        if len(before) < 6 or len(after) != 3:
            raise RuntimeError("Malformed shared memory mount evidence")
        if before[4] == "/dev/shm" or before[0] == identifiers[0]:
            rows.append((before, after))
        if before[4].startswith("/dev/shm/"):
            raise RuntimeError("Nested shared memory mounts are not admitted")
    if len(rows) != 1:
        raise RuntimeError("Shared memory mount identity is ambiguous")
    before, after = rows[0]
    entry = os.fstat(descriptor)
    if (
        before[0] != identifiers[0]
        or before[2] != f"{os.major(entry.st_dev)}:{os.minor(entry.st_dev)}"
        or before[3] != "/"
        or before[4] != "/dev/shm"
        or after[0] != "tmpfs"
        or not {"rw", "noexec", "nosuid", "nodev"} <= set(before[5].split(","))
        or "ro" in before[5].split(",")
        or "rw" not in after[2].split(",")
        or any(field.startswith(("shared:", "master:", "propagate_from:")) for field in before[6:])
    ):
        raise RuntimeError("Shared memory is not the required private tmpfs mount")
    return tuple(before), tuple(after), entry.st_dev, entry.st_ino


def open_verified_native_shm():
    """Open only actual /dev/shm, with no symlink traversal or mount mutation.

    The trusted launcher separately binds Docker's private IPC and 64 MiB
    policy. Here the unprivileged guard validates the actual mount before any
    additional Landlock right is granted, and uses that very descriptor.
    """
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    device = os.open("/dev", flags)
    try:
        descriptor = os.open("shm", flags, dir_fd=device)
    finally:
        os.close(device)
    try:
        namespaces = tuple(os.stat(f"/proc/self/ns/{name}") for name in ("mnt", "ipc"))
        identity = _native_shm_mount_identity(descriptor)
        entry, filesystem = os.fstat(descriptor), os.fstatvfs(descriptor)
        required_flags = os.ST_NOEXEC | os.ST_NOSUID | os.ST_NODEV
        if (
            not stat.S_ISDIR(entry.st_mode)
            or entry.st_uid != 0
            or entry.st_gid != 0
            or stat.S_IMODE(entry.st_mode) != 0o1777
            or filesystem.f_frsize <= 0
            or filesystem.f_blocks * filesystem.f_frsize != NATIVE_SHM_BYTES
            or filesystem.f_flag & required_flags != required_flags
            or filesystem.f_flag & os.ST_RDONLY
        ):
            raise RuntimeError("Shared memory mount ownership, size or flags are not admitted")
        if identity != _native_shm_mount_identity(descriptor) or any(
            (before.st_dev, before.st_ino)
            != ((after := os.stat(f"/proc/self/ns/{name}")).st_dev, after.st_ino)
            for name, before in zip(("mnt", "ipc"), namespaces, strict=True)
        ):
            raise RuntimeError("Shared memory mount identity changed during verification")
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def restrict_tcp(
    bind_ports, connect_ports, *, filesystem=False, native_semaphore_storage=False, evidence=None
):
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise RuntimeError("Unsupported isolated kernel architecture")
    if any(
        not 1024 <= port <= 65535 or port in FORBIDDEN_PORTS for port in bind_ports | connect_ports
    ):
        raise RuntimeError("Reserved or invalid isolated port")
    if type(native_semaphore_storage) is not bool or native_semaphore_storage and not filesystem:
        raise RuntimeError("Native shared memory requires an explicit filesystem policy")
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
            if native_semaphore_storage:
                parent = open_verified_native_shm()
                try:
                    rule = PathRule(NATIVE_SHM_ACCESS, parent)
                    if libc.syscall(ADD, descriptor, 1, ctypes.byref(rule), 0):
                        raise RuntimeError("Cannot confine native semaphore files")
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
    if native_semaphore_storage and evidence is not None:
        evidence["native_shared_memory"] = dict(NATIVE_SHM_EVIDENCE)
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
    command = sys.argv[3:]
    native_semaphore_storage = command[:1] == ["--native-shm"]
    if native_semaphore_storage:
        command = command[1:]
    probe_only = command == ["--probe"]
    if not probe_only and (len(command) < 2 or command[0] != "--"):
        raise RuntimeError("Missing isolated command separator")
    evidence = {}
    abi = restrict_tcp(
        bind_ports,
        connect_ports,
        filesystem=not probe_only or native_semaphore_storage,
        native_semaphore_storage=native_semaphore_storage,
        evidence=evidence,
    )
    restrict_resources(native=55433 in connect_ports)
    seccomp = restrict_sockets(allow_tcp_connect=bool(connect_ports))
    daemon_denied()
    if probe_only:
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
                    **evidence,
                }
            )
        )
        return
    os.execvpe(command[1], command[1:], os.environ)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(
            "Isolated command guard unavailable; no product command was executed", file=sys.stderr
        )
        sys.exit(78)
