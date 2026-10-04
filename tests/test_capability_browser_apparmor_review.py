"""Independent exact-label/guard regressions; no policy or live-probe execution."""

import json
import shutil
import subprocess

import pytest

from tests.test_capability_browser_policy import IMAGE, approved, worker_inspection
from workbench import capability_browser_isolation as isolation


@pytest.mark.parametrize(
    "environment",
    [
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=0"],
        ["CAPABILITY_BROWSER_REQUIRE_APPARMOR=1", "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1"],
        "CAPABILITY_BROWSER_REQUIRE_APPARMOR=1",
    ],
)
def test_ambiguous_guard_environment_is_rejected(monkeypatch, environment):
    approved(monkeypatch)
    value = worker_inspection()
    value[0]["Config"]["Env"] = environment
    with pytest.raises(ValueError):
        isolation.require_worker_inspection(value, IMAGE)


@pytest.mark.parametrize(
    "suffix,high_bit",
    [(b"\0extra", False), (b"", True)],
)
def test_kernel_label_requires_exact_bytes(suffix, high_bit):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node unavailable; required by the supported review job")
    data = bytearray(b"docker-default (enforce)" + suffix)
    if high_bit:
        data[0] |= 128
    harness = """
const {requireAppArmor} = require(process.argv[1]);
const input = Buffer.from(JSON.parse(process.argv[2]));
const api = {openSync:()=>3, closeSync:()=>{}, readSync:(_fd,b)=>{input.copy(b);return input.length}};
let passed=false;try{passed=requireAppArmor(api)}catch{}
process.stdout.write(JSON.stringify({passed}));
"""
    result = subprocess.run(
        [
            node,
            "-e",
            harness,
            str(isolation.ROOT / "scripts/capability_browser_apparmor.cjs"),
            json.dumps(list(data)),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"passed": False}
