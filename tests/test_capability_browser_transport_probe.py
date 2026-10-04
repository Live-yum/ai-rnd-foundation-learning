"""Compile/inspect the live probe; NEVER execute it or load a seccomp filter here.

These tests establish build, ABI, case coverage and policy consistency only.
Actual denial/kill receipts must come from the authorized disposable worker.
"""

import hashlib
import json
import re
import shutil
import struct
import subprocess
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
