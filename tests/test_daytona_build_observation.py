import hashlib
import json
import os
import shutil
import subprocess

import pytest

from scripts import daytona_build as build
from scripts.daytona_build_observation import observation, retain
from workbench.tools import clean_env

OBSERVER = build.ROOT / "tools/daytona/yarn-observer.cjs"


def marker(value):
    return "#14 20.1 RND_BUILD_OBSERVATION " + json.dumps({"session": "a" * 16, **value}) + "\n"


def test_projection_drops_private_values_bounds_fields_and_keeps_session_separation():
    item = {
        "id": "1" * 64,
        "script": "postinstall",
        "package": "private-name",
        "version": "private-version",
        "elapsed_seconds": 90,
        "command": "private-command",
        "env": "private-env",
    }
    log = "#5 [builder 1/18] FROM docker.io/library/node:24-slim@sha256:" + "b" * 64 + "\n"
    log += marker(
        {
            "event": "tools",
            "node": "24.21.0",
            "yarn": "4.13.0",
            "corepack": "private-token",
            "headers": "private-header",
        }
    )
    log += marker(
        {
            "event": "pending",
            "started": True,
            "completed": -1,
            "active_count": 300,
            "overflow": False,
            "scripts": [item] * 40,
        }
    )
    log += marker(
        {
            "session": "b" * 16,
            "event": "pending",
            "started": 0,
            "completed": 0,
            "active_count": 0,
            "scripts": [],
        }
    )
    log += marker({"event": "end", **item, "state": "private-state", "exit_code": True})
    value = observation(log)
    assert value["bases"] == {"builder": "sha256:" + "b" * 64}
    current = value["sessions"]["a" * 16]
    assert current["tools"] == {"node": "24.21.0", "yarn": "4.13.0", "corepack": "unknown"}
    assert current["pending"]["started"] is None
    assert len(current["pending"]["scripts"]) == 32
    assert current["pending"]["scripts"][0]["state"] == "awaiting_script_exit"
    assert value["sessions"]["b" * 16]["pending"]["active_count"] == 0
    assert value["events"][0]["exit_code"] is None
    assert "private" not in json.dumps(value)
    assert observation("RND_BUILD_OBSERVATION {bad}")["events"] == []
    assert observation(marker({"event": "start", "id": ["private"]}))["events"] == []


def test_only_exact_api_recipe_gets_observer_and_immutable_installs_remain(tmp_path, monkeypatch):
    raw = b"FROM node:24-slim AS builder\nENV CI=true\nRUN yarn install --immutable\nFROM node:24-slim AS daytona\nENV CI=true\nRUN yarn install --immutable\n"
    path = tmp_path / "apps/api/Dockerfile"
    path.parent.mkdir(parents=True)
    path.write_bytes(raw)
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    monkeypatch.setitem(build.SOURCE_RECIPES, "api", ("daytona", digest))
    _, text = build.recipe("api", tmp_path)
    assert text.count("yarn install --immutable") == 2
    assert text.count("YARN_PLUGINS=/opt/rnd-build-observe/yarn-observer.cjs") == 2
    assert hashlib.sha256(OBSERVER.read_bytes()).hexdigest() in text
    assert (tmp_path / ".rnd-build-observe/yarn-observer.cjs").read_bytes() == OBSERVER.read_bytes()
    assert path.read_bytes() == raw
    path.write_bytes(raw + b"# drift\n")
    with pytest.raises(ValueError):
        build.recipe("api", tmp_path)


def test_diagnostic_write_failure_is_nonfatal(tmp_path):
    (tmp_path / "api-build-observation.json").mkdir()
    retain(tmp_path, marker({"event": "tools", "yarn": "4.13.0"}))


def test_artifact_includes_only_the_exact_sanitized_hidden_diagnostic():
    import yaml

    workflow = yaml.safe_load((build.ROOT / ".github/workflows/real-model.yml").read_text())
    upload = next(
        step
        for step in workflow["jobs"]["mini-swe-sla"]["steps"]
        if step.get("uses") == "actions/upload-artifact@v4"
    )
    assert upload["with"]["include-hidden-files"] is True
    assert set(upload["with"]["path"].splitlines()) == {
        "reports/live-modules/summary.json",
        "reports/live-tls.json",
        "reports/capability-browser-isolation.json",
        "reports/capability-browser-memory-diagnostic.json",
        ".data/daytona-capability/api-build-observation.json",
    }


def test_real_node_hook_waiting_throw_logger_failure_and_once_only_execution():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node is required for the actual hook contract")
    script = r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
let clock = 0, tick, writes = [], failed = false, calls = 0, intervals = 0;
const context = {module:{exports:{}}, process:{versions:{node:'24.21.0'}, hrtime:{bigint:()=>BigInt(clock)*1000000000n}},
 setInterval(fn, ms) { assert.equal(ms,30000); tick=fn; intervals++; return {unref(){}}; }};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'), context);
const load = name => name === '@yarnpkg/core' ? {YarnVersion:'4.13.0'} :
 name === 'node:fs' ? {writeSync(fd,text){assert.equal(fd,1); if(failed) throw Error('private-output'); writes.push(JSON.parse(text.split('RND_BUILD_OBSERVATION ')[1]));}} :
 name === 'node:child_process' ? {spawnSync(command,args,opts){assert.equal(command,'corepack');assert.deepEqual(Array.from(args),['--version']);assert.equal(opts.timeout,2000);return {status:0,stdout:Buffer.from('0.34.6')}}} : require(name);
(async()=>{
 const plugin=context.module.exports.factory(load);
 assert.equal(context.module.exports.factory(load),plugin); assert.equal(intervals,1);
 const project={storedPackages:new Map([['opaque',{name:'nx',version:'21.4.1'}]])};
 const locator={locatorHash:'opaque'};
 const extra=new Proxy({}, {get(){throw Error('must-not-read-private-script-env-path')}});
 let finish;
 const run=await plugin.hooks.wrapScriptExecution(()=>{calls++;return new Promise(resolve=>finish=resolve)},project,locator,'postinstall',extra);
 const pending=run(); clock=90; tick();
 const snapshot=writes.filter(x=>x.event==='pending').at(-1);
 assert.equal(snapshot.scripts[0].state,'awaiting_script_exit'); assert.equal(snapshot.scripts[0].elapsed_seconds,90);
 assert.equal(snapshot.active_count,1); finish(7); assert.equal(await pending,7); assert.equal(calls,1);
 const original=Error('private-original');
 const reject=await plugin.hooks.wrapScriptExecution(()=>{throw original},project,locator,'install',extra);
 await assert.rejects(reject(), error=>error===original);
 assert.equal(writes.filter(x=>x.event==='end').at(-1).state,'threw');
 failed=true; const success=await plugin.hooks.wrapScriptExecution(()=>Promise.resolve(0),project,locator,'install',extra);
 assert.equal(await success(),0); tick();
 const untouched=()=>0; assert.equal(await plugin.hooks.wrapScriptExecution(untouched,project,locator,'build',extra),untouched);
 assert(!JSON.stringify(writes).includes('private')); console.log('observer-contracts-passed');
})().catch(()=>process.exitCode=1);
"""
    result = subprocess.run(
        [node, "-e", script, str(OBSERVER)],
        capture_output=True,
        text=True,
        env=clean_env(),
        timeout=10,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "observer-contracts-passed"


def test_api_build_timeout_keeps_original_failure_and_does_not_inspect_image(tmp_path, monkeypatch):
    from workbench.tools import ToolFailure

    context = tmp_path / "source"
    context.mkdir()
    monkeypatch.setattr(build, "patch_api_image_reference", lambda *_: {})
    monkeypatch.setattr(build, "download_runner", lambda *_: None)
    monkeypatch.setattr(build, "recipe", lambda *_: ("daytona", "FROM node:24-slim\n"))
    original = ToolFailure("original timeout")
    original.timed_out = True
    original.log = marker({"event": "tools", "yarn": "4.13.0"})

    def timeout(command, cwd, **kwargs):
        assert kwargs == {"timeout": 2400, "heartbeat": "Local Daytona api"}
        assert command[:3] == ["docker", "build", "--progress=plain"]
        raise original

    monkeypatch.setattr(build, "run_command", timeout)
    with pytest.raises(ToolFailure) as caught:
        build.build_exported(
            tmp_path, context, lambda *_: pytest.fail("no image admission after timeout")
        )
    assert caught.value is original and caught.value.timed_out
    value = json.loads((tmp_path / "api-build-observation.json").read_text())
    assert value["sessions"]["a" * 16]["tools"]["yarn"] == "4.13.0"


@pytest.mark.parametrize("exit_code", [0, 7])
def test_actual_yarn_413_offline_install_preserves_result_and_immutable_inputs(tmp_path, exit_code):
    yarn = os.environ.get("RND_TEST_YARN_CLI")
    node = shutil.which("node")
    if not yarn or not node:
        pytest.skip("Requires an explicitly supplied Yarn 4.13.0 CLI for offline integration")
    assert subprocess.check_output([node, yarn, "--version"], text=True).strip() == "4.13.0"
    package = {
        "name": "nx",
        "version": "21.4.1",
        "packageManager": "yarn@4.13.0",
        "scripts": {"postinstall": f'node -e "process.exit({exit_code})"'},
    }
    (tmp_path / "package.json").write_text(json.dumps(package))
    (tmp_path / ".yarnrc.yml").write_text(
        "nodeLinker: node-modules\nenableNetwork: false\nenableTelemetry: false\nglobalFolder: ./.global\nenableGlobalCache: false\n"
    )
    env = clean_env()
    command = [node, yarn, "install"]
    setup = subprocess.run(
        [*command, "--mode=update-lockfile"], cwd=tmp_path, env=env, capture_output=True, timeout=15
    )
    assert setup.returncode == 0
    protected = {
        name: (tmp_path / name).read_bytes()
        for name in ("package.json", "yarn.lock", ".yarnrc.yml")
    }
    baseline = subprocess.run(
        [*command, "--immutable"], cwd=tmp_path, env=env, capture_output=True, timeout=15
    )
    # Remove only this test's generated state to exercise the script a second time.
    shutil.rmtree(tmp_path / "node_modules")
    (tmp_path / ".yarn/install-state.gz").unlink()
    result = subprocess.run(
        [*command, "--immutable"],
        cwd=tmp_path,
        env={**env, "YARN_PLUGINS": str(OBSERVER)},
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == baseline.returncode == (0 if exit_code == 0 else 1)
    value = observation(result.stdout)
    assert len(value["sessions"]) == 1
    current = next(iter(value["sessions"].values()))
    assert current["tools"]["yarn"] == "4.13.0"
    assert [e["event"] for e in value["events"]] == ["start", "end"]
    assert value["events"][-1]["exit_code"] == exit_code
    for name, content in protected.items():
        assert (tmp_path / name).read_bytes() == content


def test_actual_yarn_pending_script_emits_30_second_snapshot_then_completes(tmp_path):
    from workbench.tools import run_command

    yarn, node = os.environ.get("RND_TEST_YARN_CLI"), shutil.which("node")
    if not yarn or not node:
        pytest.skip("Requires explicitly supplied Yarn 4.13.0; no download in tests")
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "nx",
                "version": "21.4.1",
                "packageManager": "yarn@4.13.0",
                "scripts": {"postinstall": 'node -e "setTimeout(()=>{},31000)"'},
            }
        )
    )
    (tmp_path / ".yarnrc.yml").write_text(
        "nodeLinker: node-modules\nenableNetwork: false\nenableTelemetry: false\nglobalFolder: ./.global\nenableGlobalCache: false\n"
    )
    run_command([node, yarn, "install", "--mode=update-lockfile"], tmp_path, timeout=15)
    result = run_command(
        [node, yarn, "install", "--immutable"],
        tmp_path,
        timeout=40,
        extra_env={"YARN_PLUGINS": str(OBSERVER)},
    )
    events = [
        json.loads(line.split("RND_BUILD_OBSERVATION ", 1)[1])
        for line in result["log"].splitlines()
        if line.startswith("RND_BUILD_OBSERVATION ")
    ]
    pending = [
        event for event in events if event["event"] == "pending" and event["active_count"] == 1
    ]
    assert pending and pending[0]["scripts"][0]["package"] == "nx"
    assert pending[0]["scripts"][0]["state"] == "awaiting_script_exit"
    assert 28 <= pending[0]["scripts"][0]["elapsed_seconds"] <= 31
    assert result["returncode"] == 0
    assert [event for event in events if event["event"] == "end"][0]["exit_code"] == 0
