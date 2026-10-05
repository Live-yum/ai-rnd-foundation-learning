"""Same-default AppArmor binding regressions; no live security policy changes."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.test_capability_browser_policy import IMAGE, NAME, approved, worker_inspection
from workbench import capability_browser_isolation as isolation
from workbench import capability_browser_policy as policy


@pytest.mark.parametrize("state", ["created", "running"])
def test_explicit_default_required_in_both_lifecycle_states(monkeypatch, state):
    approved(monkeypatch)
    monkeypatch.setattr(isolation, "runtime_identity", lambda image: {})
    command = isolation.worker_command(IMAGE, NAME)
    assert "--security-opt=apparmor=docker-default" in command
    assert "--env=CAPABILITY_BROWSER_REQUIRE_APPARMOR=1" in command
    value = worker_inspection()
    value[0]["State"] = {"Status": state, "Running": state == "running"}
    isolation.require_worker_inspection(value, IMAGE)
    for label in ("", None, "unconfined", "different"):
        value[0]["AppArmorProfile"] = label
        with pytest.raises(ValueError, match="apparmor-config"):
            isolation.require_worker_inspection(value, IMAGE)


def test_apparmor_option_and_runtime_guard_cannot_be_dropped(monkeypatch):
    approved(monkeypatch)
    value = worker_inspection()
    value[0]["HostConfig"]["SecurityOpt"].remove("apparmor=docker-default")
    with pytest.raises(ValueError, match="security-options"):
        isolation.require_worker_inspection(value, IMAGE)
    value = worker_inspection()
    value[0]["Config"]["Env"] = []
    with pytest.raises(ValueError, match="apparmor-runtime-guard"):
        isolation.require_worker_inspection(value, IMAGE)


@pytest.mark.parametrize(
    "label",
    [
        "docker-default (enforce)",
        "docker-default (enforce)\n",
        "",
        "unconfined\n",
        "docker-default (complain)\n",
        "other (enforce)\n",
        " docker-default (enforce)\n",
        "docker-default (enforce)\nextra",
        "docker-default (enforce)\x00extra",
        "\u00e4ocker-default (enforce)",
        None,
    ],
)
def test_actual_kernel_label_must_be_exact_enforce(label):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node tooling unavailable; mandatory on Actions")
    script = Path(__file__).resolve().parents[1] / "scripts/capability_browser_apparmor.cjs"
    harness = """
const {requireAppArmor} = require(process.argv[1])
const input = JSON.parse(process.argv[2]);let closed=0
const api = {
 openSync: (path, mode) => {if(path!='/proc/self/attr/current'||mode!='r')throw Error('path');if(input===null)throw Error('unreadable');return 3},
 readSync: (_fd,b,_o,size,_p) => {if(size!==128)throw Error('bound');return b.write(input)},
 closeSync:()=>closed++,
}
let passed=false;try{passed=requireAppArmor(api)}catch{}
process.stdout.write(JSON.stringify({passed,closed}))
"""
    result = subprocess.run(
        [node, "-e", harness, str(script), json.dumps(label)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "passed": label in {"docker-default (enforce)", "docker-default (enforce)\n"},
        "closed": 0 if label is None else 1,
    }


def test_raw_probe_checks_label_before_any_syscall_case():
    source = (
        Path(__file__).resolve().parents[1] / "scripts/capability_browser_seccomp_probe.c"
    ).read_text()
    main = source[source.index("int main(void)") :]
    assert main.index("if (!apparmor_enforced())") < main.index('socket_case("native_inet_socket"')
    assert (
        policy.POLICY_SHA256 == "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"
    )


@pytest.mark.parametrize(
    "env",
    [
        None,
        "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1",
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=0"],
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1"],
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", None],
    ],
)
def test_runtime_guard_environment_is_unique(monkeypatch, env):
    approved(monkeypatch)
    value = worker_inspection()
    value[0]["Config"]["Env"] = env
    with pytest.raises(ValueError, match="apparmor-runtime-guard"):
        isolation.require_worker_inspection(value, IMAGE)
