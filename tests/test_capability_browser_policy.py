"""Approved Actions selector tests; no daemon or policy is executed."""

import copy
import json
from types import SimpleNamespace

import pytest

from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy

IMAGE = "sha256:" + "a" * 64
NAME = "rnd-browser-" + "b" * 32


@pytest.fixture(autouse=True)
def native_test_controller(monkeypatch):
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")


def approved(monkeypatch):
    for key, value in {
        "CAPABILITY_BROWSER_APPROVED_POLICY": policy.POLICY_SHA256,
        "GITHUB_ACTIONS": "true",
        "GITHUB_REPOSITORY": "Live-yum/ai-rnd-foundation-learning",
        "GITHUB_WORKFLOW": "Offline candidate browser isolation",
        "GITHUB_RUN_ID": "12345",
    }.items():
        monkeypatch.setenv(key, value)


def target():
    return (
        {
            "Server": {
                "Version": "28.0.4",
                "Os": "linux",
                "Arch": "amd64",
                "KernelVersion": "6.17.0-1022-azure",
                "Components": [
                    {"Name": "runc", "Version": "1.2.5", "Details": {"GitCommit": "abc123"}},
                    {"Name": "containerd", "Version": "1.7.25"},
                ],
            }
        },
        {
            "OSType": "linux",
            "Architecture": "x86_64",
            "DefaultRuntime": "runc",
            "Runtimes": {"runc": {"path": "runc"}},
            "DockerRootDir": "/var/lib/docker",
            "SecurityOptions": ["name=apparmor", "name=seccomp,profile=builtin"],
        },
        [{"Id": IMAGE, "Os": "linux", "Architecture": "amd64", "Config": {"User": "1000:1000"}}],
    )


def test_no_implicit_activation(monkeypatch):
    monkeypatch.delenv("CAPABILITY_BROWSER_APPROVED_POLICY", raising=False)
    assert policy.selected_policy() is None
    assert not any("seccomp=" in v for v in isolation.worker_command(IMAGE, NAME))


@pytest.mark.parametrize(
    "key,value",
    [
        ("CAPABILITY_BROWSER_APPROVED_POLICY", "/tmp/arbitrary.json"),
        ("GITHUB_ACTIONS", "false"),
        ("GITHUB_REPOSITORY", "other/repo"),
        ("GITHUB_WORKFLOW", "Python 3.14 acceptance"),
        ("GITHUB_RUN_ID", ""),
        ("GITHUB_RUN_ID", "../1"),
    ],
)
def test_scope_rejects_before_create(monkeypatch, key, value):
    approved(monkeypatch)
    monkeypatch.setenv(key, value)
    monkeypatch.setattr(policy.subprocess, "run", lambda *a, **k: pytest.fail("subprocess reached"))
    with pytest.raises(ValueError):
        isolation.worker_command(IMAGE, NAME)


def test_changed_policy_rejected(monkeypatch, tmp_path):
    approved(monkeypatch)
    path = tmp_path / policy.POLICY_SOURCE
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    monkeypatch.setattr(policy, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="bytes changed"):
        policy.selected_policy()


@pytest.mark.parametrize(
    "section,key,value",
    [
        (0, "Version", "28.0.5"),
        (0, "Arch", "arm64"),
        (0, "Os", "windows"),
        (0, "KernelVersion", None),
        (0, "Components", []),
        (1, "DefaultRuntime", "other"),
        (1, "Architecture", "aarch64"),
        (1, "SecurityOptions", []),
        (1, "DockerRootDir", "/other"),
        (2, "Id", "sha256:" + "b" * 64),
        (2, "Architecture", "arm64"),
        (2, "Config", {"User": "0"}),
    ],
)
def test_unknown_or_wrong_target_rejected(section, key, value):
    values = copy.deepcopy(target())
    selected = values[0]["Server"] if section == 0 else values[1] if section == 1 else values[2][0]
    selected[key] = value
    with pytest.raises(ValueError):
        policy.validate_target(*values, IMAGE)


def test_target_records_observed_versions():
    got = policy.validate_target(*target(), IMAGE)
    assert got["policy_sha256"] == policy.POLICY_SHA256
    assert got["runc"] == "1.2.5" and got["kernel"] == "6.17.0-1022-azure"


def test_command_requires_runtime_before_create(monkeypatch):
    approved(monkeypatch)
    seen = []
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: seen.append(image))
    args = isolation.worker_command(IMAGE, NAME)
    assert seen == [IMAGE]
    assert "--security-opt=seccomp=" + str(policy.selected_policy()) in args
    assert "--network=none" in args and "--cap-drop=ALL" in args


def test_inspect_matches_inline_content_not_path_or_unconfined(monkeypatch):
    approved(monkeypatch)
    content = json.loads(policy.selected_policy().read_bytes())
    good = ["no-new-privileges:true", "seccomp=" + json.dumps(content)]
    assert policy.security_options_match(good)
    for bad in (
        ["no-new-privileges:true"],
        good + ["apparmor=unconfined"],
        ["no-new-privileges:true", "seccomp=unconfined"],
        ["no-new-privileges:true", "seccomp=" + str(policy.selected_policy())],
    ):
        assert not policy.security_options_match(bad)
    content["defaultAction"] = "SCMP_ACT_ALLOW"
    assert not policy.security_options_match([good[0], "seccomp=" + json.dumps(content)])


def test_runtime_requires_matching_compiler_provenance(monkeypatch, tmp_path):
    binary = tmp_path / "runc"
    binary.write_bytes(b"synthetic-runc-build")
    monkeypatch.setattr(policy, "Path", lambda path: binary)
    approved(monkeypatch)
    values = iter(target())
    monkeypatch.setattr(policy, "_read_json", lambda args: next(values))
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0, stdout=b"runc version 1.2.5\ncommit: abc123\nlibseccomp: 2.5.5\n"
        ),
    )
    assert policy.runtime_identity(IMAGE)["libseccomp_observed_matching_build"] == "2.5.5"
    values = iter(target())
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=b"runc version 1.3.0\n"),
    )
    with pytest.raises(ValueError, match="provenance mismatch"):
        policy.runtime_identity(IMAGE)


def worker_inspection():
    return [
        {
            "Image": IMAGE,
            "AppArmorProfile": "docker-default",
            "Config": {"User": "1000:1000"},
            "Mounts": [],
            "HostConfig": {
                "NetworkMode": "none",
                "ReadonlyRootfs": True,
                "Privileged": False,
                "NanoCpus": 1000000000,
                "Memory": 805306368,
                "MemorySwap": 805306368,
                "PidsLimit": 128,
                "IpcMode": "private",
                "CgroupnsMode": "private",
                "ShmSize": 67108864,
                "CapDrop": ["ALL"],
                "CapAdd": [],
                "SecurityOpt": [
                    "no-new-privileges:true",
                    "seccomp=" + policy.selected_policy().read_text(),
                ],
                "Tmpfs": {"/tmp": "rw,nosuid,nodev,noexec,size=134217728,mode=1777"},
                "LogConfig": {"Type": "none"},
            },
        }
    ]


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("record", "AppArmorProfile", "unconfined"),
        ("host", "CapAdd", ["SYS_ADMIN"]),
        ("host", "NetworkMode", "host"),
        ("host", "Privileged", True),
        ("host", "SecurityOpt", ["no-new-privileges:true"]),
        ("host", "Binds", ["/:/host"]),
        ("host", "PidMode", "host"),
    ],
)
def test_effective_policy_and_outer_boundary_required(monkeypatch, section, key, value):
    approved(monkeypatch)
    data = worker_inspection()
    isolation.require_worker_inspection(data, IMAGE)
    record = data[0] if section == "record" else data[0]["HostConfig"]
    record[key] = value
    with pytest.raises(ValueError):
        isolation.require_worker_inspection(data, IMAGE)


def raw_proof():
    observations = {}
    for name in policy.RAW_CHECKS:
        killed = name.endswith("_killed")
        error = 0 if name.startswith("native_") or killed else 38 if name == "clone3_enosys" else 1
        observations[name] = {
            "returned": not killed,
            "return": -error,
            "errno": error,
            "signal": 31 if killed else 0,
            "exit_status": 0 if "extra_" in name else -1,
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


def test_complete_raw_proof():
    assert policy.require_raw_probe(raw_proof()) is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(passed=1),
        lambda r: r.update(expected_profile_sha256="wrong"),
        lambda r: r["checks"].pop("clone3_enosys"),
        lambda r: r["checks"].update(mount_denied=False),
        lambda r: r["checks"].update(mount_denied=1),
        lambda r: r["observations"]["mount_denied"].update(timed_out=True),
        lambda r: r["observations"].pop("mount_denied"),
    ],
)
def test_incomplete_raw_proof_rejected(mutation):
    data = raw_proof()
    mutation(data)
    with pytest.raises(ValueError):
        policy.require_raw_probe(data)


def test_selected_receipt_requires_exact_runtime_and_raw_proof(monkeypatch, tmp_path):
    approved(monkeypatch)
    runtime = policy.validate_target(*target(), IMAGE)
    runtime["libseccomp"] = "2.5.5"
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: runtime)
    path = tmp_path / "receipt.json"
    monkeypatch.setattr(isolation, "BROWSER_ACCEPTANCE", path)
    record = {
        "protocol": "offline-browser-isolation-v3",
        "passed": True,
        "image": IMAGE,
        "mocked": False,
        "runtime": runtime,
        "sources": isolation.browser_source_identity(),
        "image_sources": isolation.image_source_identity(),
        "checks": {
            "kernel_and_network": dict.fromkeys(
                [
                    "passed",
                    "kernel_resource_limits",
                    "network_none",
                    "tmpfs_exhaustion",
                    "pid_exhaustion",
                    "readonly_root",
                    "browser_build",
                ],
                True,
            ),
            **dict.fromkeys(
                [
                    "positive",
                    "error",
                    "abuse",
                    "failure_cleanup",
                    "memory_exhaustion",
                    "raw_syscalls",
                ],
                True,
            ),
        },
    }
    path.write_text(json.dumps(record))
    assert isolation.require_browser_acceptance(IMAGE) == IMAGE
    for mutation in (
        lambda r: r.update(protocol="offline-browser-isolation-v2"),
        lambda r: r["runtime"].update(policy_sha256=None),
        lambda r: r["runtime"].update(kernel="other"),
        lambda r: r["checks"].pop("raw_syscalls"),
        lambda r: r["checks"].update(raw_syscalls=1),
    ):
        bad = copy.deepcopy(record)
        mutation(bad)
        path.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            isolation.require_browser_acceptance(IMAGE)
