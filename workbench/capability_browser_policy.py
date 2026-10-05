"""Fixed, explicitly approved Actions-only browser policy selection.

Environment values select one reviewed policy; they never supply policy content
or paths. The created container's inline policy is checked before any start.
"""

import hashlib
import json
import os
import platform
import re
import subprocess
from pathlib import Path

from workbench.settings import ROOT
from workbench.tools import clean_env

POLICY_SHA256 = "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"
POLICY_SOURCE = "tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json"
DOCKER = ["docker", "--host", "unix:///var/run/docker.sock"]
WORKFLOWS = {
    "Offline candidate browser isolation",
    "Fixed authored SQLite isolation profile",
    "Authored native PostgreSQL isolation profile",
}


def selected_policy():
    selected = os.environ.get("CAPABILITY_BROWSER_APPROVED_POLICY", "")
    if not selected:
        return None
    if (
        selected != POLICY_SHA256
        or os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REPOSITORY") != "Live-yum/ai-rnd-foundation-learning"
        or os.environ.get("GITHUB_WORKFLOW") not in WORKFLOWS
        or not re.fullmatch(r"[1-9][0-9]{0,19}", os.environ.get("GITHUB_RUN_ID", ""))
    ):
        raise ValueError("Reviewed browser policy requires its approved Actions scope")
    path = ROOT / POLICY_SOURCE
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != POLICY_SHA256:
        raise ValueError("Reviewed browser policy bytes changed")
    return path


def _read_json(args):
    value = subprocess.run([*DOCKER, *args], capture_output=True, timeout=10, env=clean_env())
    if value.returncode or len(value.stdout) > 100000:
        raise ValueError("Browser runtime provenance unavailable")
    return json.loads(value.stdout)


def _text(value):
    return isinstance(value, str) and bool(re.fullmatch(r"[a-zA-Z0-9._+ /()-]{1,160}", value))


def validate_target(version, info, image, expected_image):
    server = version.get("Server", {}) if isinstance(version, dict) else {}
    if not isinstance(info, dict) or not isinstance(image, list) or len(image) != 1:
        raise ValueError("Browser runtime provenance missing")
    metadata = image[0]
    components = server.get("Components", [])
    versions = {
        part.get("Name"): part.get("Version") for part in components if isinstance(part, dict)
    }
    details = {
        part.get("Name"): part.get("Details", {}) for part in components if isinstance(part, dict)
    }
    runc_commit = details.get("runc", {}).get("GitCommit")
    runtime_config = info.get("Runtimes", {}).get("runc", {})
    options = info.get("SecurityOptions", [])
    if (
        server.get("Version") != "28.0.4"
        or server.get("Os") != "linux"
        or server.get("Arch") != "amd64"
        or info.get("OSType") != "linux"
        or info.get("Architecture") not in {"x86_64", "amd64"}
        or info.get("DefaultRuntime") != "runc"
        or runtime_config.get("path") not in {"runc", "/usr/bin/runc"}
        or runtime_config.get("runtimeArgs")
        or runtime_config.get("runtimeType") not in {None, "", "io.containerd.runc.v2"}
        or not _text(runc_commit)
        or info.get("DockerRootDir") != "/var/lib/docker"
        or not isinstance(options, list)
        or "name=apparmor" not in options
        or "name=seccomp,profile=builtin" not in options
        or any("rootless" in str(v) for v in options)
        or metadata.get("Id") != expected_image
        or metadata.get("Os") != "linux"
        or metadata.get("Architecture") != "amd64"
        or metadata.get("Config", {}).get("User") != "1000:1000"
        or platform.system() != "Linux"
        or platform.machine() != "x86_64"
        or not _text(server.get("KernelVersion"))
        or not _text(versions.get("runc"))
        or not _text(versions.get("containerd"))
    ):
        raise ValueError("Unsupported browser runtime; no policy fallback")
    # Engine version pins its profile compiler; runc/containerd/kernel are
    # observed, not inferred from runner image inventory. Docker does not expose
    # libseccomp's version here, so no independent library-version claim is made.
    return {
        "policy_sha256": POLICY_SHA256,
        "engine": "28.0.4",
        "daemon_arch": "amd64",
        "image_arch": "amd64",
        "controller_abi": "x86_64",
        "playwright": "1.56.1",
        "chromium": "141.0.7390.37",
        "kernel": server["KernelVersion"],
        "runc": versions["runc"],
        "runc_reported_commit": runc_commit,
        "runc_configured_path": runtime_config["path"],
        "containerd": versions["containerd"],
        "apparmor": "docker-default",
        "libseccomp": "not-exposed-by-docker-api",
    }


def runtime_identity(image):
    if selected_policy() is None:
        return {"policy_sha256": None, "mode": "docker-default"}
    identity = validate_target(
        _read_json(["version", "--format", "{{json .}}"]),
        _read_json(["info", "--format", "{{json .}}"]),
        _read_json(["image", "inspect", image]),
        image,
    )
    version = subprocess.run(
        ["/usr/bin/runc", "--version"], capture_output=True, timeout=10, env=clean_env()
    )
    if version.returncode or len(version.stdout) > 4096:
        raise ValueError("Runtime compiler provenance unavailable")
    text = version.stdout.decode("ascii", errors="strict")
    runtime = re.search(r"(?m)^runc version ([a-zA-Z0-9.+_-]+)$", text)
    commit = re.search(r"(?m)^commit: ([a-zA-Z0-9.+_-]+)$", text)
    library = re.search(r"(?m)^libseccomp: ([0-9]+\.[0-9]+\.[0-9]+)$", text)
    if (
        not runtime
        or not library
        or not commit
        or commit[1] != identity["runc_reported_commit"]
        or runtime[1].removeprefix("v") != identity["runc"].removeprefix("v")
    ):
        raise ValueError("Runtime compiler provenance mismatch")
    binary = Path("/usr/bin/runc")
    if not 0 < binary.stat().st_size <= 32 * 1024 * 1024:
        raise ValueError("Runtime executable provenance exceeds bound")
    identity["runc_observed_binary_sha256"] = hashlib.sha256(binary.read_bytes()).hexdigest()
    identity["runc_observed_binary_path"] = "/usr/bin/runc"
    identity["libseccomp_observed_matching_build"] = library[1]
    identity["libseccomp"] = "daemon-linkage-not-exposed-by-docker-api"
    return identity


def security_options_match(options):
    path = selected_policy()
    if path is None:
        return options == ["no-new-privileges:true"]
    if not isinstance(options, list) or len(options) != 3:
        return False
    if (
        options.count("no-new-privileges:true") != 1
        or options.count("apparmor=docker-default") != 1
    ):
        return False
    selected = [v for v in options if isinstance(v, str) and v.startswith("seccomp=")]
    if len(selected) != 1:
        return False
    try:
        # Docker normalizes the selected file to inline JSON in HostConfig.
        # Comparing parsed content binds the effective policy after file reading;
        # a changed file during create cannot authorize a container start.
        return json.loads(selected[0][8:]) == json.loads(path.read_bytes())
    except ValueError, OSError:
        return False


RAW_CHECKS = {
    "native_inet_socket",
    "native_unix_socket",
    "native_unix_socketpair",
    *(
        f"vsock_{operation}_{word}_high_word"
        for operation in ("socket", "socketpair")
        for word in ("zero", "one", "sign", "max")
    ),
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


def require_raw_probe(value):
    if (
        not isinstance(value, dict)
        or set(value)
        != {
            "protocol",
            "architecture",
            "expected_profile_sha256",
            "passed",
            "checks",
            "observations",
        }
        or value.get("protocol") != "browser-seccomp-transport-v1"
        or value.get("architecture") != "native-amd64"
        or value.get("expected_profile_sha256") != POLICY_SHA256
        or value.get("passed") is not True
        or not isinstance(value.get("checks"), dict)
        or set(value["checks"]) != RAW_CHECKS
        or any(v is not True for v in value["checks"].values())
        or not isinstance(value.get("observations"), dict)
        or set(value["observations"]) != RAW_CHECKS
    ):
        raise ValueError("Live raw-syscall policy proof incomplete")
    for name, observation in value["observations"].items():
        if (
            not isinstance(observation, dict)
            or set(observation)
            != {"returned", "return", "errno", "signal", "exit_status", "setup_errno", "timed_out"}
            or type(observation["returned"]) is not bool
            or observation["timed_out"] is not False
            or any(
                type(observation[k]) is not int or abs(observation[k]) > 2**63
                for k in ("return", "errno", "signal", "exit_status", "setup_errno")
            )
            or observation["setup_errno"] != 0
        ):
            raise ValueError("Live raw-syscall observations invalid")
        if name.endswith("_killed"):
            meaningful = (
                observation["returned"] is False
                and observation["signal"] == 31
                and observation["exit_status"] == -1
                and observation["return"] == 0
                and observation["errno"] == 0
            )
        else:
            expected_errno = (
                0 if name.startswith("native_") else 38 if name == "clone3_enosys" else 1
            )
            meaningful = (
                observation["returned"] is True
                and observation["signal"] == 0
                and observation["errno"] == expected_errno
                and (name != "native_unix_socketpair" or observation["return"] == 0)
                and (
                    observation["return"] >= 0
                    if expected_errno == 0
                    else observation["return"] == -expected_errno
                )
                and observation["exit_status"] == (0 if "extra_" in name else -1)
            )
        if not meaningful:
            raise ValueError("Raw-syscall result does not prove expected denial or success")
    return True
