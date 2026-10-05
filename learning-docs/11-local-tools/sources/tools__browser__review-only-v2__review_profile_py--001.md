# tools/browser/review-only-v2/review_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `require_target`（L15–L22）：接收`daemon_arch`、`image_arch`、`docker_version`、`initial_caps`、`process_abi`。 控制顺序：L16按`(daemon_arch, image_arch, docker_version, process_abi) != ("amd64", "amd64", "28.0.4"…`分支；L22抛异常，停止当前正常路径。 调用`type`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `namespace_rules`（L25–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L34遍历`values`；L41按`value is not None`分支。 调用`result.append`。 返回路径：L44的`result`。
- `transport_rules`（L47–L69）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`range`。 返回路径：L52的`[ { "names": [name], "action": "SCMP_ACT_ALLOW", "args": [ { "index": 0, "value": 1 << bit…`。
- `build_profile`（L72–L98）：接收`baseline`。 控制顺序：L74断言`profile["archMap"][0] == { "architecture": "SCMP_ARCH_X86_64", "subArchitectures": ["…`；L83遍历`profile["syscalls"]`；L84按`"socket" in rule["names"]`分支；L85断言`rule == { "names": ["socket"], "action": "SCMP_ACT_ALLOW", "args": [{"index": 0, "val…`；L92按`"socketpair" in rule["names"] or "socketcall" in rule["names"]`分支；L93断言`rule["action"] == "SCMP_ACT_ALLOW" and not rule.get("args")`；L96断言`removed_socket == 1`。 调用`copy.deepcopy`、`rule.get`、`rules.append`、`namespace_rules`、`transport_rules`。 返回路径：L98的`profile`。
- `_applies`（L101–L113）：接收`rule`。 控制顺序：L103遍历`(inc, exc)`；L104按`set(condition) - {"arches", "caps", "minKernel"}`分支；L105抛异常，停止当前正常路径。 调用`rule.get`、`set`、`ValueError`、`tuple`、`map`、`inc.get("minKernel", "0").split`、`inc.get`、`exc.get`。 返回路径：L107的`not inc.get("caps") and not (inc.get("arches") and "amd64" not in inc["arches"]) and "amd6…`。
- `compile_bpf`（L116–L184）：接收`profile`。 源码说明：Export with installed libseccomp, without seccomp_load or child execution. Models the reviewed amd64/empty-initial-capability/kernel-6.17 conditions. This is not proof of the CI runtime's compiler, Ap。 控制顺序：L122按`platform.system() != "Linux" or platform.machine() != "x86_64"`分支；L123抛异常，停止当前正常路径；L124按`profile["archMap"] != [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]`分支；L125抛异常，停止当前正常路径；L127按`not library`分支；L128抛异常，停止当前正常路径；L153按`profile["defaultAction"] != "SCMP_ACT_ERRNO"`分支；L154抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`platform.system`、`platform.machine`、`ValueError`、`ctypes.util.find_library`、`ctypes.CDLL`、`ctypes.POINTER`、`lib.seccomp_init`、`_applies`、`rule.get`等。 返回路径：L182的`output`。
- `compile_bpf.Arg`（L137–L143）：继承`ctypes.Structure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `evaluate_bpf`（L187–L219）：接收`program`、`number`、`arch`、`args`。 源码说明：Interpret exported classic BPF against synthetic seccomp_data only.。 控制顺序：L189按`len(args) > 6`分支；L190抛异常，停止当前正常路径；L194遍历`range(len(code) + 1)`；L195按`not 0 <= pc < len(code)`分支；L196抛异常，停止当前正常路径；L198按`operation == 0x20`分支；L199按`value > len(data) - 4`分支；L200抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`len`、`ValueError`、`struct.pack`、`struct.unpack`、`range`、`struct.unpack_from`、`bool`。 返回路径：L215的`value`。

</details>

**创建路径：** `tools/browser/review-only-v2/review_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L219。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`8421`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/browser/review-only-v2/review_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "960682500404ac0f4f34e519c0c448f0509c3b944fb9105b9c41cbc4d76b002b"} -->
````python
# tools/browser/review-only-v2/review_profile.py
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
````
