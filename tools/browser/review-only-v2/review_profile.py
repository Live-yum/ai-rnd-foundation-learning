"""Offline review helper: build/export/evaluate BPF; NEVER load a filter."""

import copy
import ctypes
import ctypes.util
import platform
import struct
import tempfile

ALLOW = 0x7FFF0000
ERRNO = 0x00050000
NATIVE_ARCH = 0xC000003E


def require_target(daemon_arch, image_arch, docker_version, initial_caps, process_abi):
    if (
        (daemon_arch, image_arch, docker_version, process_abi)
        != ("amd64", "amd64", "28.0.4", "x86_64")
        or type(initial_caps) is not list
        or initial_caps
    ):
        raise ValueError("Review profile supports only native amd64 Docker 28.0.4; no fallback")


def namespace_rules():
    values = [
        ("clone", 0x10000011),
        ("clone", 0x70000011),
        ("clone", 0x20000011),
        ("unshare", 0x10000000),
        ("chroot", None),
    ]
    result = []
    for name, value in values:
        rule = {
            "names": [name],
            "action": "SCMP_ACT_ALLOW",
            "includes": {"arches": ["amd64"]},
            "excludes": {"caps": ["CAP_SYS_ADMIN"]},
        }
        if value is not None:
            rule["args"] = [{"index": 0, "value": value, "op": "SCMP_CMP_EQ"}]
        result.append(rule)
    return result


def transport_rules():
    # OR of bit mismatches is exactly (arg0 & 0xffffffff) != AF_VSOCK.
    # Do not append an overlapping deny: libseccomp can retain the earlier
    # broad allow. These disjoint-from-VSOCK allowances reach default EPERM
    # for every high-word variant of family 40, including socketpair.
    return [
        {
            "names": [name],
            "action": "SCMP_ACT_ALLOW",
            "args": [
                {
                    "index": 0,
                    "value": 1 << bit,
                    "valueTwo": (40 ^ (1 << bit)) & (1 << bit),
                    "op": "SCMP_CMP_MASKED_EQ",
                }
            ],
            "includes": {"arches": ["amd64"]},
            "excludes": {"caps": ["CAP_SYS_ADMIN"]},
        }
        for name in ("socket", "socketpair")
        for bit in range(32)
    ]


def build_profile(baseline):
    profile = copy.deepcopy(baseline)
    assert profile["archMap"][0] == {
        "architecture": "SCMP_ARCH_X86_64",
        "subArchitectures": ["SCMP_ARCH_X86", "SCMP_ARCH_X32"],
    }
    # Explicit ABI restriction. Unsupported daemon/image targets must also be
    # rejected by require_target BEFORE any future container creation.
    profile["archMap"] = [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]
    rules = []
    removed_socket = 0
    for rule in profile["syscalls"]:
        if "socket" in rule["names"]:
            assert rule == {
                "names": ["socket"],
                "action": "SCMP_ACT_ALLOW",
                "args": [{"index": 0, "value": 40, "op": "SCMP_CMP_NE"}],
            }
            removed_socket += 1
            continue
        if "socketpair" in rule["names"] or "socketcall" in rule["names"]:
            assert rule["action"] == "SCMP_ACT_ALLOW" and not rule.get("args")
            rule["names"] = [n for n in rule["names"] if n not in {"socketpair", "socketcall"}]
        rules.append(rule)
    assert removed_socket == 1
    profile["syscalls"] = rules + namespace_rules() + transport_rules()
    return profile


def _applies(rule):
    inc, exc = rule.get("includes", {}), rule.get("excludes", {})
    for condition in (inc, exc):
        if set(condition) - {"arches", "caps", "minKernel"}:
            raise ValueError("Unsupported review condition")
    minimum = tuple(map(int, inc.get("minKernel", "0").split(".")))
    return (
        not inc.get("caps")
        and not (inc.get("arches") and "amd64" not in inc["arches"])
        and "amd64" not in exc.get("arches", [])
        and minimum <= (6, 17)
        and not exc.get("minKernel")
    )


def compile_bpf(profile):
    """Export with installed libseccomp, without seccomp_load or child execution.

    Models the reviewed amd64/empty-initial-capability/kernel-6.17 conditions.
    This is not proof of the CI runtime's compiler, AppArmor, or live behavior.
    """
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("Offline BPF compiler requires native Linux x86_64")
    if profile["archMap"] != [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]:
        raise ValueError("Only native ABI review is supported")
    library = ctypes.util.find_library("seccomp")
    if not library:
        raise ValueError("libseccomp unavailable")
    lib = ctypes.CDLL(library)
    lib.seccomp_init.argtypes, lib.seccomp_init.restype = [ctypes.c_uint32], ctypes.c_void_p
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.seccomp_export_bpf.restype = ctypes.c_int

    class Arg(ctypes.Structure):
        _fields_ = [
            ("arg", ctypes.c_uint),
            ("op", ctypes.c_uint),
            ("a", ctypes.c_uint64),
            ("b", ctypes.c_uint64),
        ]

    lib.seccomp_rule_add_array.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_int,
        ctypes.c_uint,
        ctypes.POINTER(Arg),
    ]
    lib.seccomp_rule_add_array.restype = ctypes.c_int
    if profile["defaultAction"] != "SCMP_ACT_ERRNO":
        raise ValueError("Unexpected default action")
    context = lib.seccomp_init(ERRNO | profile["defaultErrnoRet"])
    if not context:
        raise ValueError("Cannot allocate review filter")
    op = {"SCMP_CMP_NE": 1, "SCMP_CMP_EQ": 4, "SCMP_CMP_MASKED_EQ": 7}
    try:
        for rule in profile["syscalls"]:
            if not _applies(rule):
                continue
            action = ALLOW if rule["action"] == "SCMP_ACT_ALLOW" else ERRNO | rule["errnoRet"]
            args = rule.get("args", [])
            array = (Arg * len(args))(
                *(Arg(a["index"], op[a["op"]], a["value"], a.get("valueTwo", 0)) for a in args)
            )
            for name in rule["names"]:
                number = lib.seccomp_syscall_resolve_name(name.encode())
                if number < 0:  # Non-native ABI names cannot be reached in this filter.
                    continue
                result = lib.seccomp_rule_add_array(context, action, number, len(args), array)
                if result != 0:
                    raise ValueError(f"BPF rule compilation failed: {name} ({result})")
        with tempfile.TemporaryFile() as stream:
            if lib.seccomp_export_bpf(context, stream.fileno()) != 0:
                raise ValueError("Cannot export review BPF")
            stream.seek(0)
            output = stream.read(32769)
            if len(output) > 32768 or len(output) % 8:
                raise ValueError("Unexpected BPF size")
            return output
    finally:
        lib.seccomp_release(context)


def evaluate_bpf(program, number, arch=NATIVE_ARCH, args=()):
    """Interpret exported classic BPF against synthetic seccomp_data only."""
    if len(args) > 6:
        raise ValueError("Too many syscall arguments")
    data = struct.pack("<iIQ6Q", number, arch, 0, *args, *([0] * (6 - len(args))))
    code = [struct.unpack("<HBBI", program[i : i + 8]) for i in range(0, len(program), 8)]
    pc, accumulator = 0, 0
    for _ in range(len(code) + 1):
        if not 0 <= pc < len(code):
            raise ValueError("Invalid BPF jump")
        operation, yes, no, value = code[pc]
        if operation == 0x20:
            if value > len(data) - 4:
                raise ValueError("Invalid BPF load")
            accumulator = struct.unpack_from("<I", data, value)[0]
        elif operation == 0x54:
            accumulator &= value
        elif operation == 0x05:
            pc += value
        elif operation in {0x15, 0x25, 0x35, 0x45}:
            condition = {
                0x15: accumulator == value,
                0x25: accumulator > value,
                0x35: accumulator >= value,
                0x45: bool(accumulator & value),
            }[operation]
            pc += yes if condition else no
        elif operation == 0x06:
            return value
        else:
            raise ValueError(f"Unsupported BPF instruction: {operation}")
        pc += 1
    raise ValueError("BPF step bound exceeded")
