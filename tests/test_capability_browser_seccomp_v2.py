"""Fixed policy validation: static artifacts and offline BPF; no filter is loaded."""

import ctypes.util
import hashlib
import importlib.util
import json
import os
import platform
import random
from pathlib import Path

import pytest

from workbench.capability_browser_isolation import worker_command

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "tools/browser/review-only-v2"
SPEC = importlib.util.spec_from_file_location("review_profile", DIRECTORY / "review_profile.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)
PROPOSAL_SHA = "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"


def baseline():
    path = ROOT / "tools/browser/review-only/moby-v28.0.4-default.json"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76"
    )
    return json.loads(path.read_text())


def proposal():
    data = (DIRECTORY / "chromium141-docker28-native-amd64.proposal.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PROPOSAL_SHA
    return json.loads(data)


def test_exact_restrictive_transport_abi_delta_and_namespace_allowances():
    base, value = baseline(), proposal()
    assert value == review.build_profile(base)
    assert value["defaultAction"] == base["defaultAction"] == "SCMP_ACT_ERRNO"
    assert value["defaultErrnoRet"] == base["defaultErrnoRet"] == 1
    assert value["archMap"] == [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]
    # Baseline rule order/properties preserved except the explicitly removed
    # native socket allowance and two names removed from the broad allow group.
    original = []
    for row in base["syscalls"]:
        if row["names"] == ["socket"]:
            continue
        row = json.loads(json.dumps(row))
        row["names"] = [name for name in row["names"] if name not in {"socketcall", "socketpair"}]
        original.append(row)
    assert value["syscalls"][: len(original)] == original
    assert value["syscalls"][len(original) :] == review.namespace_rules() + review.transport_rules()
    assert len(review.namespace_rules()) == 5
    assert len(review.transport_rules()) == 64
    assert all("socketcall" not in row["names"] for row in value["syscalls"])
    assert not any(
        row["names"] == ["socket"] and row.get("args", [{}])[0].get("op") == "SCMP_CMP_NE"
        for row in value["syscalls"]
    )


@pytest.mark.parametrize(
    "change",
    [
        {"daemon_arch": "arm64"},
        {"daemon_arch": None},
        {"image_arch": "arm64"},
        {"docker_version": "28.0.5"},
        {"process_abi": "x86"},
        {"process_abi": "x32"},
        {"initial_caps": ["CAP_SYS_ADMIN"]},
        {"initial_caps": None},
        {"initial_caps": ()},
    ],
)
def test_review_target_rejects_other_arch_abi_caps_version_or_unknown(change):
    data = dict(
        daemon_arch="amd64",
        image_arch="amd64",
        docker_version="28.0.4",
        initial_caps=[],
        process_abi="x86_64",
    )
    review.require_target(**data)
    with pytest.raises(ValueError, match="no fallback"):
        review.require_target(**{**data, **change})


@pytest.fixture(scope="module")
def bpf():
    available = (
        platform.system() == "Linux"
        and platform.machine() == "x86_64"
        and ctypes.util.find_library("seccomp")
    )
    if not available:
        if os.getenv("RND_REQUIRE_SECCOMP_BPF") == "1":
            pytest.fail("Native Linux amd64/libseccomp offline compilation is mandatory")
        pytest.skip("Offline compiler unavailable; this is not live acceptance")
    return review.compile_bpf(proposal())


def test_compiled_low32_vsock_denial_covers_socket_and_socketpair(bpf):
    randoms = random.Random(14128)
    highs = [0, 1, 0x7FFFFFFF, 0xFFFFFFFF, *[randoms.getrandbits(32) for _ in range(100)]]
    for number in (41, 53):
        for high in highs:
            assert review.evaluate_bpf(bpf, number, args=((high << 32) | 40,)) == review.ERRNO | 1
        for low in [*range(128), 0x7FFFFFFF, 0xFFFFFFFF]:
            for high in (0, 1, 0xFFFFFFFF):
                expected = review.ERRNO | 1 if low == 40 else review.ALLOW
                assert review.evaluate_bpf(bpf, number, args=((high << 32) | low,)) == expected


@pytest.mark.parametrize("number,args", [(102, (1,)), (102, (8,)), (359, (40,)), (360, (40,))])
def test_compiled_x86_socketcall_and_direct_socket_abis_fail_closed(bpf, number, args):
    assert review.evaluate_bpf(bpf, number, arch=0x40000003, args=args) in {0, 0x80000000}


@pytest.mark.parametrize("number", [41, 53, 56, 161, 272, 435])
def test_compiled_x32_syscall_bit_fails_closed(bpf, number):
    assert review.evaluate_bpf(bpf, 0x40000000 | number, args=(40,)) in {0, 0x80000000}


@pytest.mark.parametrize("arch", [0xC00000B7, 0x40000028, 0, 0xFFFFFFFF])
def test_compiled_other_audit_architectures_fail_closed(bpf, arch):
    assert review.evaluate_bpf(bpf, 41, arch=arch, args=(2,)) in {0, 0x80000000}


def test_compiled_only_justified_namespace_calls_allow_and_other_guards_hold(bpf):
    for flags in (0x10000011, 0x70000011, 0x20000011, 17, 0x84311):
        assert review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ALLOW
    for flags in (0x10000009, 0x30000011, 0x50000011, 0x70000111, 0x10020011, 0x170000011):
        assert review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ERRNO | 1
    assert review.evaluate_bpf(bpf, 272, args=(0x10000000,)) == review.ALLOW
    for flags in (0, 0x40000000, 0x70000000, 0x10000001):
        assert review.evaluate_bpf(bpf, 272, args=(flags,)) == review.ERRNO | 1
    assert review.evaluate_bpf(bpf, 161, args=(12345,)) == review.ALLOW
    assert review.evaluate_bpf(bpf, 435) == review.ERRNO | 38
    for number in (308, 425, 426, 427, 165, 155):
        assert review.evaluate_bpf(bpf, number) == review.ERRNO | 1


def test_only_offline_export_symbols_are_used(monkeypatch, bpf):
    # Recompile through a symbol-restricted proxy. No policy-loading symbol is
    # reachable through this helper; export writes bytes to a temporary file.
    real = review.ctypes.CDLL
    observed = set()
    allowed = {
        "seccomp_init",
        "seccomp_release",
        "seccomp_syscall_resolve_name",
        "seccomp_rule_add_array",
        "seccomp_export_bpf",
    }

    class Proxy:
        def __init__(self, path):
            self.inner = real(path)

        def __getattr__(self, name):
            assert name in allowed
            observed.add(name)
            return getattr(self.inner, name)

    monkeypatch.setattr(review.ctypes, "CDLL", Proxy)
    assert review.compile_bpf(proposal()) == bpf
    assert observed == allowed


def test_v2_requires_explicit_approved_actions_selection():
    manifest = json.loads((DIRECTORY / "proposal-manifest.json").read_text())
    assert manifest["status"] == "approved-actions-only-pending-live-proof"
    assert manifest["activation_authorized"] is True
    assert manifest["live_validation"] is False
    assert manifest["proposal_sha256"] == PROPOSAL_SHA
    command = worker_command("sha256:" + "a" * 64, "rnd-browser-" + "b" * 32)
    assert [word for word in command if word.startswith("--security-opt")] == [
        "--security-opt=no-new-privileges:true"
    ]
