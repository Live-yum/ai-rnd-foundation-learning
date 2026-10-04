"""Independent activation regressions; mocked provenance only, no live syscalls."""

import copy
from types import SimpleNamespace

import pytest

from workbench import capability_browser_policy as policy


def raw_receipt():
    observations = {}
    for name in policy.RAW_CHECKS:
        killed = name.endswith("_killed")
        positive = name.startswith("native_")
        error = 38 if name == "clone3_enosys" else 1
        observations[name] = {
            "returned": not killed,
            "return": 0 if killed or positive else -error,
            "errno": 0 if killed or positive else error,
            "signal": 31 if killed else 0,
            "exit_status": 0 if name.startswith(("clone_user", "clone_pid", "unshare_")) else -1,
            "setup_errno": 0,
            "timed_out": False,
        }
    return {
        "protocol": "browser-seccomp-transport-v1",
        "architecture": "native-amd64",
        "expected_profile_sha256": policy.POLICY_SHA256,
        "passed": True,
        "checks": dict.fromkeys(policy.RAW_CHECKS, True),
        "observations": observations,
    }


@pytest.mark.parametrize(
    "case,changes",
    [
        ("vsock_socket_one_high_word", {"return": 7, "errno": 0}),
        ("x32_socket_killed", {"returned": True, "return": 7, "signal": 0}),
        ("clone3_enosys", {"return": -22, "errno": 22}),
        ("clone_user_extra_mount_denied", {"exit_status": 101}),
        ("native_unix_socketpair", {"return": 7}),
    ],
)
def test_claimed_pass_cannot_override_contradictory_raw_evidence(case, changes):
    receipt = raw_receipt()
    assert policy.require_raw_probe(receipt) is True
    changed = copy.deepcopy(receipt)
    changed["observations"][case].update(changes)
    with pytest.raises(ValueError):
        policy.require_raw_probe(changed)


def test_same_runc_version_different_build_is_not_compiler_provenance(monkeypatch):
    image_id = "sha256:" + "a" * 64
    monkeypatch.setattr(policy, "selected_policy", lambda: object())
    records = iter(
        [
            {
                "Server": {
                    "Version": "28.0.4",
                    "Os": "linux",
                    "Arch": "amd64",
                    "KernelVersion": "6.17.0-1022-azure",
                    "Components": [
                        {"Name": "runc", "Version": "1.2.5", "Details": {"GitCommit": "a" * 40}},
                        {"Name": "containerd", "Version": "1.7.25"},
                    ],
                }
            },
            {
                "OSType": "linux",
                "Architecture": "x86_64",
                "DefaultRuntime": "runc",
                "DockerRootDir": "/var/lib/docker",
                "SecurityOptions": ["name=apparmor", "name=seccomp,profile=builtin"],
                "Runtimes": {"runc": {"path": "runc", "runtimeArgs": []}},
            },
            [
                {
                    "Id": image_id,
                    "Os": "linux",
                    "Architecture": "amd64",
                    "Config": {"User": "1000:1000"},
                }
            ],
        ]
    )
    monkeypatch.setattr(policy, "_read_json", lambda args: next(records))
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0,
            stdout=(
                "runc version 1.2.5\ncommit: " + "b" * 40 + "\nspec: 1.2.0\nlibseccomp: 2.5.5\n"
            ).encode(),
        ),
    )
    with pytest.raises(ValueError):
        policy.runtime_identity(image_id)
