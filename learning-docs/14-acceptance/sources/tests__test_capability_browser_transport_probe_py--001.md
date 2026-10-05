# tests/test_capability_browser_transport_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `compiled_probe`（L55–L87）：接收`tmp_path_factory`。 控制顺序：L56按`sys.platform != "linux" or platform.machine().lower() not in {"x86_64", "amd64"} or s…`分支；L63断言`compiler`；L85断言`result.returncode == 0`。 调用`platform.machine().lower`、`platform.machine`、`struct.calcsize`、`pytest.skip`、`shutil.which`、`tmp_path_factory.mktemp`、`subprocess.run`、`str`、`pytest.fixture`。 返回路径：L87的`output`。
- `test_probe_is_static_native_amd64_and_contains_complete_receipt`（L90–L103）：接收`compiled_probe`。 控制顺序：L92断言`data[:6] == b"\x7fELF\x02\x01"`；L93断言`struct.unpack_from("<HH", data, 16) == (2, 62)`；L99断言`not {2, 3} & program_types`；L100遍历`EXPECTED_CHECKS`；L101断言`name.encode() + b"\0" in data`；L102断言`hashlib.sha256(PROFILE.read_bytes()).hexdigest().encode() in data`；L103断言`b"browser-seccomp-transport-v1" in data`。 调用`compiled_probe.read_bytes`、`struct.unpack_from`、`range`、`name.encode`、`hashlib.sha256(PROFILE.read_bytes()).hexdigest().encode`、`hashlib.sha256(PROFILE.read_bytes()).hexdigest`、`hashlib.sha256`、`PROFILE.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compiled_probe_enters_both_raw_syscall_abis`（L106–L121）：接收`compiled_probe`。 控制顺序：L108断言`disassembler`；L115断言`result.returncode == 0`；L118断言`native and re.search(r"\bsyscall\b", native[1])`；L119断言`compat and re.search(r"\bint\s+\$0x80\b", compat[1])`；L121断言`not re.search(r"\bcallq?\b", native[1] + compat[1])`。 调用`shutil.which`、`subprocess.run`、`str`、`re.search`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_probe_case_count_and_bounded_json_contract`（L124–L159）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L134断言`recorded_names == EXPECTED_CHECKS`；L135断言`int(re.search(r"bool passed = result_count == (\d+);", source)[1]) == len( EXPECTED_C…`；L138断言`len(EXPECTED_CHECKS) <= int(re.search(r"#define MAX_RESULTS (\d+)U", source)[1])`；L159断言`len(json.dumps(largest).encode()) < 12_000`。 调用`SOURCE.read_text`、`set`、`re.findall`、`recorded_names.update`、`int`、`re.search`、`len`、`dict.fromkeys`、`json.dumps(largest).encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_native_allow_rules`（L162–L170）：接收`profile`、`syscall`。 控制顺序：L163遍历`profile["syscalls"]`；L165按`include.get("caps") or "amd64" in exclude.get("arches", [])`分支；L167按`include.get("arches") and "amd64" not in include["arches"]`分支；L169按`syscall in rule["names"] and rule["action"] == "SCMP_ACT_ALLOW"`分支。 调用`rule.get`、`include.get`、`exclude.get`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_matches`（L173–L185）：接收`rule`、`argument`。 控制顺序：L174遍历`rule.get("args", [])`；L175断言`predicate["index"] == 0`；L177按`predicate["op"] == "SCMP_CMP_MASKED_EQ"`分支；L178按`argument & value != predicate.get("valueTwo", 0)`分支；L180按`predicate["op"] == "SCMP_CMP_EQ"`分支；L181按`argument != value`分支。 调用`rule.get`、`predicate.get`、`pytest.fail`。 返回路径：L179的`False`；L182的`False`；L185的`True`。
- `test_native_negative_cases_are_outside_every_reviewed_allow_rule`（L188–L209）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L195断言`len(domains) == 4`；L196断言`{value >> 32 for value in domains} == {0, 1, 0x80000000, 0xFFFFFFFF}`；L197断言`all(value & 0xFFFFFFFF == 40 for value in domains)`；L198遍历`("socket", "socketpair")`；L199遍历`domains`；L200断言`not any(_matches(rule, domain) for rule in _native_allow_rules(profile, syscall))`；L202断言`len(namespace_cases) == 5`；L203遍历`namespace_cases`。后续分支沿下方源码相同行号继续阅读。 调用`json.loads`、`PROFILE.read_text`、`SOURCE.read_text`、`int`、`re.findall`、`len`、`all`、`any`、`_matches`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_native_compile_fixture_has_platform_precondition`（L221–L237）：接收`monkeypatch`、`host`、`machine`、`pointer_size`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`pytest.fail`、`pytest.raises`、`compiled_probe.__wrapped__`、`test_probe_case_count_and_bounded_json_contract`、`test_native_negative_cases_are_outside_every_reviewed_allow_rule`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_supported_native_compile_cannot_skip_missing_compiler`（L241–L250）：接收`monkeypatch`、`machine`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`pytest.raises`、`compiled_probe.__wrapped__`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_transport_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L250。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9611`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_transport_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cf83e2e3cba680001ac37348a9bb2cfb3117ba2d6a16453b8bf55432507d3e47"} -->
````python
# tests/test_capability_browser_transport_probe.py
"""Compile/inspect the live probe; NEVER execute it or load a seccomp filter here.

These tests establish build, ABI, case coverage and policy consistency only.
Actual denial/kill receipts must come from the authorized disposable worker.
"""

import hashlib
import json
import platform
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/capability_browser_seccomp_probe.c"
PROFILE = ROOT / "tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json"
EXPECTED_CHECKS = {
    "native_inet_socket",
    "native_unix_socket",
    "native_unix_socketpair",
    "vsock_socket_zero_high_word",
    "vsock_socketpair_zero_high_word",
    "vsock_socket_one_high_word",
    "vsock_socketpair_one_high_word",
    "vsock_socket_sign_high_word",
    "vsock_socketpair_sign_high_word",
    "vsock_socket_max_high_word",
    "vsock_socketpair_max_high_word",
    "io_uring_setup",
    "io_uring_enter",
    "io_uring_register",
    "clone3_enosys",
    "setns_denied",
    "mount_denied",
    "x32_socket_killed",
    "x32_socketpair_killed",
    "i386_socketcall_socket_killed",
    "i386_socketcall_socketpair_killed",
    "i386_socket_killed",
    "i386_socketpair_killed",
    "clone_user_extra_mount_denied",
    "clone_user_pid_net_extra_mount_denied",
    "clone_pid_extra_mount_denied",
    "unshare_user_extra_mount_denied",
    "unshare_user_extra_net_denied",
}


@pytest.fixture(scope="module")
def compiled_probe(tmp_path_factory):
    if (
        sys.platform != "linux"
        or platform.machine().lower() not in {"x86_64", "amd64"}
        or struct.calcsize("P") != 8
    ):
        pytest.skip("ELF/raw-syscall compilation requires native Linux amd64; source contracts run")
    compiler = shutil.which("gcc")
    assert compiler, "Static native-amd64 probe compilation is required; no skipped pass"
    output = tmp_path_factory.mktemp("inspect-only-browser-probe") / "probe-do-not-run"
    result = subprocess.run(
        [
            compiler,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-pedantic",
            "-static",
            "-fno-pie",
            "-no-pie",
            str(SOURCE),
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    # Never invoke output. Read ELF bytes and disassemble only.
    return output


def test_probe_is_static_native_amd64_and_contains_complete_receipt(compiled_probe):
    data = compiled_probe.read_bytes()
    assert data[:6] == b"\x7fELF\x02\x01"  # ELF64, little endian
    assert struct.unpack_from("<HH", data, 16) == (2, 62)  # ET_EXEC, EM_X86_64
    program_offset = struct.unpack_from("<Q", data, 32)[0]
    entry_size, count = struct.unpack_from("<HH", data, 54)
    program_types = {
        struct.unpack_from("<I", data, program_offset + i * entry_size)[0] for i in range(count)
    }
    assert not {2, 3} & program_types  # Neither PT_DYNAMIC nor PT_INTERP
    for name in EXPECTED_CHECKS:
        assert name.encode() + b"\0" in data
    assert hashlib.sha256(PROFILE.read_bytes()).hexdigest().encode() in data
    assert b"browser-seccomp-transport-v1" in data


def test_compiled_probe_enters_both_raw_syscall_abis(compiled_probe):
    disassembler = shutil.which("objdump")
    assert disassembler, "Instruction inspection is required; no skipped pass"
    result = subprocess.run(
        [disassembler, "-d", str(compiled_probe)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    native = re.search(r"<raw_syscall6[^>]*>:\n(.*?)(?=\n\n)", result.stdout, flags=re.DOTALL)
    compat = re.search(r"<raw_i386_syscall4[^>]*>:\n(.*?)(?=\n\n)", result.stdout, flags=re.DOTALL)
    assert native and re.search(r"\bsyscall\b", native[1])
    assert compat and re.search(r"\bint\s+\$0x80\b", compat[1])
    # These functions must enter the kernel directly, without a libc wrapper.
    assert not re.search(r"\bcallq?\b", native[1] + compat[1])


def test_probe_case_count_and_bounded_json_contract():
    source = SOURCE.read_text()
    recorded_names = set(re.findall(r'(?:socket_case|errno_case)\("([a-z0-9_]+)"', source))
    child_rows = re.findall(r'\{"([a-z0-9_]+)",\s*[A-Z0-9_]+,', source)
    domain_rows = re.findall(
        r'\{"(vsock_[a-z_]+)",\s*"(vsock_[a-z_]+)",\s*UINT64_C\((0x[0-9a-f]+)\)',
        source,
    )
    recorded_names.update(child_rows)
    recorded_names.update(name for row in domain_rows for name in row[:2])
    assert recorded_names == EXPECTED_CHECKS
    assert int(re.search(r"bool passed = result_count == (\d+);", source)[1]) == len(
        EXPECTED_CHECKS
    )
    assert len(EXPECTED_CHECKS) <= int(re.search(r"#define MAX_RESULTS (\d+)U", source)[1])
    # Even pessimistic signed-long-sized numeric observations fit the controller's budget.
    largest = {
        "protocol": "browser-seccomp-transport-v1",
        "architecture": "native-amd64",
        "expected_profile_sha256": "f" * 64,
        "passed": False,
        "checks": dict.fromkeys(EXPECTED_CHECKS, False),
        "observations": {
            name: {
                "returned": False,
                "return": -(2**63),
                "errno": 4095,
                "signal": 64,
                "exit_status": 255,
                "setup_errno": 4095,
                "timed_out": False,
            }
            for name in EXPECTED_CHECKS
        },
    }
    assert len(json.dumps(largest).encode()) < 12_000


def _native_allow_rules(profile, syscall):
    for rule in profile["syscalls"]:
        include, exclude = rule.get("includes", {}), rule.get("excludes", {})
        if include.get("caps") or "amd64" in exclude.get("arches", []):
            continue
        if include.get("arches") and "amd64" not in include["arches"]:
            continue
        if syscall in rule["names"] and rule["action"] == "SCMP_ACT_ALLOW":
            yield rule


def _matches(rule, argument):
    for predicate in rule.get("args", []):
        assert predicate["index"] == 0
        value = predicate["value"]
        if predicate["op"] == "SCMP_CMP_MASKED_EQ":
            if argument & value != predicate.get("valueTwo", 0):
                return False
        elif predicate["op"] == "SCMP_CMP_EQ":
            if argument != value:
                return False
        else:
            pytest.fail(f"Unexpected predicate in reviewed syscall: {predicate}")
    return True


def test_native_negative_cases_are_outside_every_reviewed_allow_rule():
    profile = json.loads(PROFILE.read_text())
    source = SOURCE.read_text()
    domains = [
        int(value, 16)
        for value in re.findall(r'"vsock_socketpair_[a-z_]+", UINT64_C\((0x[0-9a-f]+)\)', source)
    ]
    assert len(domains) == 4
    assert {value >> 32 for value in domains} == {0, 1, 0x80000000, 0xFFFFFFFF}
    assert all(value & 0xFFFFFFFF == 40 for value in domains)
    for syscall in ("socket", "socketpair"):
        for domain in domains:
            assert not any(_matches(rule, domain) for rule in _native_allow_rules(profile, syscall))
    namespace_cases = re.findall(r"EXTRA_(CLONE|UNSHARE), UINT64_C\((0x[0-9a-f]+)\)", source)
    assert len(namespace_cases) == 5
    for syscall, value in namespace_cases:
        assert not any(
            _matches(rule, int(value, 16)) for rule in _native_allow_rules(profile, syscall.lower())
        )
    for syscall in ("setns", "mount", "io_uring_setup", "io_uring_enter", "io_uring_register"):
        assert not list(_native_allow_rules(profile, syscall))
    assert profile["defaultAction"] == "SCMP_ACT_ERRNO" and profile["defaultErrnoRet"] == 1


@pytest.mark.parametrize(
    ("host", "machine", "pointer_size"),
    [
        ("win32", "AMD64", 8),
        ("darwin", "x86_64", 8),
        ("linux", "aarch64", 8),
        ("linux", "x86_64", 4),
    ],
)
def test_only_native_compile_fixture_has_platform_precondition(
    monkeypatch, host, machine, pointer_size
):
    from types import SimpleNamespace

    module = sys.modules[__name__]
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform=host))
    monkeypatch.setattr(module, "platform", SimpleNamespace(machine=lambda: machine))
    monkeypatch.setattr(module, "struct", SimpleNamespace(calcsize=lambda _: pointer_size))
    monkeypatch.setattr(
        shutil, "which", lambda _: pytest.fail("compiler queried on unsupported ABI")
    )
    with pytest.raises(pytest.skip.Exception, match="native Linux amd64"):
        compiled_probe.__wrapped__(None)
    # Source/receipt contracts and every policy case remain checked even here.
    test_probe_case_count_and_bounded_json_contract()
    test_native_negative_cases_are_outside_every_reviewed_allow_rule()


@pytest.mark.parametrize("machine", ["x86_64", "AMD64"])
def test_supported_native_compile_cannot_skip_missing_compiler(monkeypatch, machine):
    from types import SimpleNamespace

    module = sys.modules[__name__]
    monkeypatch.setattr(module, "sys", SimpleNamespace(platform="linux"))
    monkeypatch.setattr(module, "platform", SimpleNamespace(machine=lambda: machine))
    monkeypatch.setattr(module, "struct", SimpleNamespace(calcsize=lambda _: 8))
    monkeypatch.setattr(shutil, "which", lambda _: None)
    with pytest.raises(AssertionError, match="compilation is required"):
        compiled_probe.__wrapped__(None)
````
