"""Static review-artifact checks; never load seccomp or launch containers."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from workbench.capability_browser_isolation import worker_command

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "tools/browser/review-only"
BASELINE_SHA256 = "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76"
PROPOSAL_SHA256 = "f62d10d5ce466dfd0714d61891ef7b94445367c8a6a303302f4c3956687f3504"


def read(name):
    return json.loads((DIRECTORY / name).read_text())


def added_rule(name, value=None):
    rule = {
        "names": [name],
        "action": "SCMP_ACT_ALLOW",
        "includes": {"arches": ["amd64"]},
        "excludes": {"caps": ["CAP_SYS_ADMIN"]},
    }
    if value is not None:
        rule["args"] = [{"index": 0, "value": value, "op": "SCMP_CMP_EQ"}]
    return rule


EXPECTED_DELTA = [
    added_rule("clone", 0x10000011),
    added_rule("clone", 0x70000011),
    added_rule("clone", 0x20000011),
    added_rule("unshare", 0x10000000),
    added_rule("chroot"),
]


def profiles():
    return read("moby-v28.0.4-default.json"), read("chromium141-docker28-amd64.proposal.json")


def test_pinned_provenance_hashes_and_inactive_status():
    manifest = read("proposal-manifest.json")
    assert manifest["status"] == "inactive-review-only"
    assert manifest["activation_authorized"] is False
    assert manifest["live_validation"] is False
    assert manifest["scope"]["initial_capability_bounding_set"] == []
    for key, expected in (("baseline", BASELINE_SHA256), ("proposal", PROPOSAL_SHA256)):
        record = manifest[key]
        assert hashlib.sha256((DIRECTORY / record["file"]).read_bytes()).hexdigest() == expected
        assert record["sha256"] == expected
    assert manifest["baseline"]["upstream_commit"] == "6430e49a55babd9b8f4d08e70ecb2b68900770fe"
    assert len(manifest["chromium_sources"]) == 4
    assert all(
        "9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e" in s["url"] for s in manifest["chromium_sources"]
    )
    assert "Apache License" in (DIRECTORY / manifest["upstream_license"]).read_text()


def test_exact_append_only_delta_preserves_every_baseline_rule_and_property():
    base, proposal = profiles()
    expected = copy.deepcopy(base)
    expected["syscalls"].extend(EXPECTED_DELTA)
    assert proposal == expected
    patch = read("proposal-manifest.json")["json_patch"]
    assert patch == [{"op": "add", "path": "/syscalls/-", "value": r} for r in EXPECTED_DELTA]
    replay = copy.deepcopy(base)
    for operation in patch:
        replay["syscalls"].append(operation["value"])
    assert replay == proposal
    assert {n for r in EXPECTED_DELTA for n in r["names"]} == {"clone", "unshare", "chroot"}


def applies(rule, host_arch="amd64", caps=()):
    """Moby host filtering only; not a kernel/seccomp emulator or ABI proof."""
    inc, exc = rule.get("includes", {}), rule.get("excludes", {})
    return (
        (not inc.get("arches") or host_arch in inc["arches"])
        and host_arch not in exc.get("arches", [])
        and all(c in caps for c in inc.get("caps", []))
        and not any(c in caps for c in exc.get("caps", []))
    )


def decision(profile, name, arg0=0, host_arch="amd64"):
    """Evaluate the explicit scalar rules used by these negative test cases."""
    for rule in profile["syscalls"]:
        if name not in rule["names"] or not applies(rule, host_arch):
            continue
        matches = True
        for arg in rule.get("args") or []:
            assert arg["index"] == 0  # Non-amd64 clone layouts are not simulated.
            op, value = arg["op"], arg["value"]
            if op == "SCMP_CMP_EQ":
                matches &= arg0 == value
            elif op == "SCMP_CMP_NE":
                matches &= arg0 != value
            elif op == "SCMP_CMP_MASKED_EQ":
                matches &= arg0 & value == arg.get("valueTwo", 0)
            else:
                raise AssertionError("Untested argument operation")
        if matches:
            return rule["action"], rule.get("errnoRet")
    return profile["defaultAction"], profile["defaultErrnoRet"]


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone", 0x10000011),
        ("clone", 0x70000011),
        ("clone", 0x20000011),
        ("unshare", 0x10000000),
        ("chroot", 12345),
    ],
)
def test_only_source_justified_calls_become_allowed(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg)[0] == "SCMP_ACT_ERRNO"
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone3", 0),
        ("setns", 0),
        ("setns", 0x10000000),
        ("io_uring_setup", 0),
        ("io_uring_enter", 0),
        ("io_uring_register", 0),
        ("socket", 40),
        ("mount", 0),
        ("pivot_root", 0),
        ("unshare", 0),
        ("unshare", 0x40000000),
        ("unshare", 0x20000),
        ("unshare", 0x70000000),
        ("unshare", 0x10000001),
        ("clone", 0x30000011),
        ("clone", 0x50000011),
        ("clone", 0x10000000),
        ("clone", 0x10000009),
        ("clone", 0x10020011),
        ("clone", 0x18000011),
        ("clone", 0x70000111),
        ("clone", 0x70000211),
        ("clone", 0x70010011),
        ("clone", 0x170000011),
    ],
)
def test_forbidden_calls_extra_flags_and_alternate_signals_stay_denied(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ERRNO"
    if name == "clone3":
        assert decision(proposal, name, arg) == ("SCMP_ACT_ERRNO", 38)


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone", 0x84311),
        ("clone", 17),
        ("socket", 2),
        ("landlock_create_ruleset", 0),
        ("openat2", 0),
        ("close_range", 0),
    ],
)
def test_unrelated_baseline_allowances_are_preserved(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"


@pytest.mark.parametrize("name,arg", [("socketcall", 1), ("socket", 0x100000028)])
def test_inherited_vsock_limits_do_not_claim_complete_abi_containment(name, arg):
    # Static rule matching only: neither compiled BPF nor successful socket
    # creation is established. The full-word comparison precedes kernel int
    # truncation; socketcall remains relevant to inherited compatibility ABIs.
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"
    assert decision(proposal, "socket", 40)[0] == "SCMP_ACT_ERRNO"
    compat = next(row for row in proposal["archMap"] if row["architecture"] == "SCMP_ARCH_X86_64")
    assert {"SCMP_ARCH_X86", "SCMP_ARCH_X32"} <= set(compat["subArchitectures"])


def test_proposal_is_not_selected_copied_or_part_of_existing_acceptance():
    command = worker_command("sha256:" + "a" * 64, "rnd-browser-" + "b" * 32)
    assert [c for c in command if c.startswith("--security-opt")] == [
        "--security-opt=no-new-privileges:true"
    ]
    assert "--cap-drop=ALL" in command
    for path in [
        ROOT / "tools/browser/Dockerfile",
        *ROOT.glob(".github/workflows/*.yml"),
        *ROOT.glob("workbench/*.py"),
        *ROOT.glob("scripts/*.py"),
    ]:
        text = path.read_text()
        assert "chromium141-docker28-amd64.proposal.json" not in text
        assert "tools/browser/review-only/" not in text
    assert all(not applies(r, "arm64") for r in EXPECTED_DELTA)
    assert all(not applies(r, caps=("CAP_SYS_ADMIN",)) for r in EXPECTED_DELTA)
