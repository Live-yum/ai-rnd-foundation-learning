"""Native Vite patch safety and optional real-Vite fake-listener component proof.

Native CI requires the component matrix against its prepared Vite 7.3.3 tree.
For local use, set RND_NATIVE_VITE_PACKAGE or RND_NATIVE_TEST_NODE_MODULES.
No candidate config, real socket, or OS permission change is used. Full
Landlock/listener/business acceptance belongs to native CI.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import daytona_dependency_build as build

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ".pnpm/vite@7.3.3/node_modules/vite"


@pytest.fixture
def patch_tree(tmp_path, monkeypatch):
    if os.name == "nt":
        pytest.skip("Native image file mutation requires POSIX directory descriptors")
    root = tmp_path / "node_modules"
    target = root / (PACKAGE + build.VITE_PREVIEW_SUFFIX)
    target.parent.mkdir(parents=True)
    target.write_bytes(b"original fixture")
    (root / "vite").symlink_to(PACKAGE)
    monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", root)
    monkeypatch.setattr(build.os, "geteuid", lambda: 1000)
    return root, target


def fixture_patch(monkeypatch):
    def transform(raw):
        assert raw == b"original fixture"
        return b"patched fixture"

    monkeypatch.setattr(build, "adapt_native_preview_source", transform)
    monkeypatch.setattr(
        build, "VITE_PREVIEW_PATCHED_SHA256", hashlib.sha256(b"patched fixture").hexdigest()
    )


def test_patch_and_collector_independently_bind_the_installed_file(patch_tree, monkeypatch):
    root, target = patch_tree
    fixture_patch(monkeypatch)
    record = build.patch_native_preview()
    assert target.read_bytes() == b"patched fixture"
    assert record["relative_path"] == PACKAGE + build.VITE_PREVIEW_SUFFIX
    assert build.native_preview_patch_provenance() == [record]
    target.write_bytes(b"changed after patch")
    with pytest.raises(ValueError, match="missing or stale"):
        build.native_preview_patch_provenance()
    assert (root / "vite").readlink().as_posix() == PACKAGE


def test_patch_requires_nonroot_before_opening_any_target(patch_tree, monkeypatch):
    _, target = patch_tree
    monkeypatch.setattr(build.os, "geteuid", lambda: 0)
    monkeypatch.setattr(build.os, "open", lambda *a, **kw: pytest.fail("opened as root"))
    with pytest.raises(ValueError, match="non-root"):
        build.patch_native_preview()
    assert target.read_bytes() == b"original fixture"


def test_unknown_upstream_is_rejected_without_mutation(patch_tree):
    _, target = patch_tree
    with pytest.raises(ValueError, match="upstream source hash"):
        build.patch_native_preview()
    assert target.read_bytes() == b"original fixture"


@pytest.mark.skipif(os.name == "nt", reason="Native image uses POSIX directory descriptors")
@pytest.mark.parametrize(
    "kind",
    ["root-link", "store-link", "ancestor-link", "leaf-link", "hardlink", "setid", "fifo"],
)
def test_unsafe_targets_are_rejected_before_writing_outside_sentinel(
    patch_tree, monkeypatch, tmp_path, kind
):
    root, target = patch_tree
    outside = tmp_path / "outside"
    outside.mkdir()
    sentinel = outside / "sentinel"
    sentinel.write_bytes(b"do not modify")
    if kind == "root-link":
        alias = tmp_path / "alias"
        alias.symlink_to(root, target_is_directory=True)
        monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", alias)
    elif kind == "store-link":
        store = root / ".pnpm"
        moved = tmp_path / "moved-store"
        store.rename(moved)
        store.symlink_to(moved, target_is_directory=True)
    elif kind == "ancestor-link":
        parent = target.parent
        moved = tmp_path / "moved-chunks"
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
    elif kind == "leaf-link":
        target.unlink()
        target.symlink_to(sentinel)
    elif kind == "hardlink":
        target.unlink()
        os.link(sentinel, target)
    elif kind == "setid":
        target.chmod(0o4755)
    else:
        target.unlink()
        os.mkfifo(target)
    fixture_patch(monkeypatch)
    with pytest.raises((OSError, ValueError)):
        build.patch_native_preview()
    assert sentinel.read_bytes() == b"do not modify"


@pytest.mark.parametrize(
    "link", ["../outside", "/tmp/outside", ".pnpm/vite@7.3.30/node_modules/vite", "vite"]
)
def test_package_link_must_match_the_pinned_lexical_scope(patch_tree, link):
    root, target = patch_tree
    (root / "vite").unlink()
    (root / "vite").symlink_to(link)
    with pytest.raises(ValueError, match="pinned scope"):
        build.patch_native_preview()
    assert target.read_bytes() == b"original fixture"


@pytest.mark.parametrize("count", [0, 2])
def test_source_transform_rejects_missing_or_ambiguous_anchors(monkeypatch, count):
    raw = (
        b"function resolveServerUrls(server, options$1, hostname, httpsOptions, config$2) {\n"
        * count
        + b"owned inert fixture"
    )
    monkeypatch.setattr(build, "VITE_PREVIEW_UPSTREAM_SHA256", hashlib.sha256(raw).hexdigest())
    with pytest.raises(ValueError, match="anchor"):
        build.adapt_native_preview_source(raw)


def require_official_vite():
    value = os.environ.get("RND_NATIVE_VITE_PACKAGE")
    if not value and os.environ.get("RND_NATIVE_TEST_NODE_MODULES"):
        value = str(Path(os.environ["RND_NATIVE_TEST_NODE_MODULES"]) / "vite")
    if not value:
        if os.environ.get("RND_REQUIRE_NATIVE_VITE_TESTS") == "1":
            pytest.fail("Native Vite preview tool tree is required by this job")
        pytest.skip("Optional real-Vite component requires RND_NATIVE_VITE_PACKAGE")
    package = Path(value).resolve(strict=True)
    descriptor = json.loads((package / "package.json").read_bytes())
    assert (descriptor["name"], descriptor["version"]) == ("vite", "7.3.3")
    source = package / "dist/node/chunks/config.js"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == build.VITE_PREVIEW_UPSTREAM_SHA256
    return package


def test_mandatory_vite_preview_cannot_skip_missing_or_invalid_tool_tree(monkeypatch, tmp_path):
    monkeypatch.setenv("RND_REQUIRE_NATIVE_VITE_TESTS", "1")
    monkeypatch.delenv("RND_NATIVE_VITE_PACKAGE", raising=False)
    monkeypatch.delenv("RND_NATIVE_TEST_NODE_MODULES", raising=False)
    with pytest.raises(pytest.fail.Exception, match="required"):
        require_official_vite()
    monkeypatch.setenv("RND_NATIVE_TEST_NODE_MODULES", str(tmp_path))
    with pytest.raises(OSError):
        require_official_vite()


def test_native_ci_requires_preview_matrix_with_existing_pinned_tool_tree():
    workflow = (ROOT / ".github/workflows/native-capability-profile.yml").read_text()
    start = workflow.index("- name: Require bounded native Vite scheduling")
    step = workflow[start : workflow.index("      - name:", start + 1)]
    assert "RND_REQUIRE_NATIVE_VITE_TESTS: '1'" in step
    assert "RND_REQUIRE_NODE_TESTS: '1'" in step
    assert "${{ github.workspace }}/.native/tool-product/frontend/web/node_modules" in step
    assert "tests/test_capability_native_preview_patch.py" in step


@pytest.fixture
def official_vite(tmp_path):
    if os.name == "nt":
        pytest.skip("Native image component uses POSIX links and directory descriptors")
    package = require_official_vite()
    modules = tmp_path / "node_modules"
    destination = modules / PACKAGE
    destination.parent.mkdir(parents=True)
    shutil.copytree(package, destination, symlinks=True)
    # Official dependency siblings stay read-only input to this component test.
    # Only the owned Vite copy is mutated; this is not a sealed image graph.
    for dependency in package.parent.iterdir():
        if dependency.name != "vite":
            (destination.parent / dependency.name).symlink_to(dependency.resolve())
    (modules / "vite").symlink_to(PACKAGE)
    return package, modules, destination


def test_exact_official_patch_hash_and_package_descriptors_preserved(
    official_vite, monkeypatch, tmp_path
):
    original, modules, copied = official_vite
    before = (copied / "package.json").read_bytes()
    monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", modules)
    record = build.patch_native_preview()
    assert record["upstream_sha256"] == build.VITE_PREVIEW_UPSTREAM_SHA256
    assert record["patched_sha256"] == build.VITE_PREVIEW_PATCHED_SHA256
    assert (copied / "package.json").read_bytes() == before
    assert hashlib.sha256((original / "dist/node/chunks/config.js").read_bytes()).hexdigest() == (
        build.VITE_PREVIEW_UPSTREAM_SHA256
    )
    assert build.native_preview_patch_provenance() == [record]
    with pytest.raises(ValueError, match="upstream source hash"):
        build.patch_native_preview()


def test_derived_hash_mismatch_fails_before_mutating_official_source(official_vite, monkeypatch):
    _, modules, copied = official_vite
    target = copied / "dist/node/chunks/config.js"
    before = target.read_bytes()
    monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", modules)
    monkeypatch.setattr(build, "VITE_PREVIEW_PATCHED_SHA256", "0" * 64)
    with pytest.raises(ValueError, match="derived source hash"):
        build.patch_native_preview()
    assert target.read_bytes() == before


def test_exact_patched_function_rethrows_non_eperm_and_non_preview_cases(
    official_vite, monkeypatch, tmp_path
):
    _, modules, copied = official_vite
    monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", modules)
    build.patch_native_preview()
    script = tmp_path / "predicate.mjs"
    # A local VM object supplies error inputs to the exact patched function.
    # It does not replace Node's os module or fabricate host interfaces.
    script.write_text(r"""
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(process.argv[2],'utf8');
const start=source.indexOf('function resolveServerUrls(');
const end=source.indexOf('\nfunction ',start+1);
const body=source.slice(start,end);
const cases=['valid','not-preview','code','syscall','errno','missing-info','options-identity',
 'host','hostname','port','strict-port','open','https','listening','address','family','address-port'];
const rows=[];
for(const name of cases){
 const error={code:'ERR_SYSTEM_ERROR',info:{syscall:'uv_interface_addresses',errno:1}};
 const options={host:'0.0.0.0',port:5173,strictPort:true,open:false};
 const hostname={host:'0.0.0.0',name:'localhost'};
 const address={address:'0.0.0.0',family:'IPv4',port:5173};
 const server={listening:true,address:()=>address};
 const config={preview:options,rawBase:'/fixture/'};
 if(name==='code')error.code='EPERM';
 if(name==='syscall')error.info.syscall='listen';
 if(name==='errno')error.info.errno=13;
 if(name==='missing-info')delete error.info;
 if(name==='options-identity')config.preview={...options};
 if(name==='host')options.host='::';
 if(name==='hostname')hostname.host='::';
 if(name==='port')options.port=5174;
 if(name==='strict-port')options.strictPort=false;
 if(name==='open')options.open=true;
 if(name==='https')options.https={};
 if(name==='listening')server.listening=false;
 if(name==='address')address.address='127.0.0.1';
 if(name==='family')address.family='IPv6';
 if(name==='address-port')address.port=5174;
 const context=vm.createContext({os:{networkInterfaces(){throw error}},
  wildcardHosts:new Set(['0.0.0.0','::']),loopbackHosts:new Set(['localhost','127.0.0.1']),
  extractHostnamesFromCerts(){return []}});
 const resolve=vm.runInContext(`${body}\nresolveServerUrls`,context);
 try{
  const urls=resolve(server,options,hostname,undefined,config,name!=='not-preview');
  rows.push(name==='valid'&&JSON.stringify(urls)==='{"local":["http://127.0.0.1:5173/fixture/"],"network":[]}');
 }catch(value){rows.push(name!=='valid'&&value===error)}
}
console.log(JSON.stringify({passed:rows.every(Boolean),count:rows.length}));
""")
    result = subprocess.run(
        [shutil.which("node"), str(script), str(copied / "dist/node/chunks/config.js")],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0 and not result.stderr
    assert json.loads(result.stdout) == {"passed": True, "count": 17}


INERT_CONFIG = r"""
const caseName=process.env.RND_PROOF_CASE;
globalThis.fixtureReceipt={listenCalls:0,postHook:false};
function forged(){
 const error=Object.assign(new Error('owned inert error'),{
  code:'ERR_SYSTEM_ERROR',info:{syscall:'uv_interface_addresses',errno:1}});
 error.stack=`SystemError\n    at Object.networkInterfaces (node:os:218:16)\n    at resolveServerUrls (${process.env.RND_PROOF_URL}:2393:26)\n    at preview (${process.env.RND_PROOF_URL}:35176:24)`;
 return error;
}
export default {logLevel:'silent',plugins:[{name:'owned-inert-http',configurePreviewServer(server){
 globalThis.fixtureServer=server;
 const http=server.httpServer, receipt=globalThis.fixtureReceipt;
 http.listen=(port,host,callback)=>{
  receipt.listenCalls++;receipt.exactRequest=port===5173&&host==='0.0.0.0';
  receipt.middlewares=server.middlewares.stack.length;
  if(caseName==='port-conflict'){
   queueMicrotask(()=>http.emit('error',Object.assign(new Error('owned conflict'),{code:'EADDRINUSE'})));return http;
  }
  if(caseName==='listen-forged'){queueMicrotask(()=>http.emit('error',forged()));return http}
  http._handle={getsockname(out){Object.assign(out,{address:caseName==='wrong-address'?'127.0.0.1':'0.0.0.0',family:'IPv4',port:5173});return 0}};
  queueMicrotask(()=>{http.emit('listening');callback?.()});return http;
 };
 http.close=(callback)=>{http._handle=null;queueMicrotask(()=>{http.emit('close');callback?.()});return http};
 if(caseName==='plugin-forged'){http.listen(5173,'0.0.0.0');throw forged()}
 return ()=>{receipt.postHook=true;if(caseName==='post-hook-forged'){http.listen(5173,'0.0.0.0');throw forged()}};
}}]};
"""

PROBE = r"""
import os from 'node:os';
const original=os.networkInterfaces;
const {preview}=await import(process.env.RND_PROOF_ENTRY);
let result;
try{
 const server=await preview({root:process.env.RND_PROOF_ROOT,mode:'production',preview:{host:'0.0.0.0',port:5173,strictPort:true,open:false}});
 result={success:true,sameServer:server===globalThis.fixtureServer,urls:server.resolvedUrls,
  noOsPatch:os.networkInterfaces===original,...globalThis.fixtureReceipt};
}catch(error){
 result={success:false,systemError:error.code==='ERR_SYSTEM_ERROR',syscall:error.info?.syscall==='uv_interface_addresses',errno:error.info?.errno,...globalThis.fixtureReceipt};
}finally{if(globalThis.fixtureServer)await globalThis.fixtureServer.close()}
console.log(JSON.stringify(result));
"""


@pytest.mark.skipif(sys.platform != "linux", reason="Original seccomp component is Linux-only")
def test_real_vite_before_after_and_forged_hook_failures_under_original_filter(
    official_vite, monkeypatch, tmp_path
):
    original, modules, copied = official_vite
    node = shutil.which("node")
    assert node
    monkeypatch.setattr(build, "NATIVE_FRONTEND_MODULES", modules)
    build.patch_native_preview()
    project = tmp_path / "inert-project"
    (project / "dist").mkdir(parents=True)
    (project / "vite.config.mjs").write_text(INERT_CONFIG)
    probe = tmp_path / "probe.mjs"
    probe.write_text(PROBE)
    runner = (
        "import os,runpy,sys;"
        f"m=runpy.run_path({str(ROOT / 'scripts/capability_guard.py')!r});"
        "m['restrict_resources'](native=True);m['restrict_sockets']();"
        "os.execv(sys.argv[1],sys.argv[1:])"
    )
    cases = [
        (original, "normal", False),
        (copied, "normal", True),
        *(
            (copied, name, False)
            for name in (
                "plugin-forged",
                "post-hook-forged",
                "listen-forged",
                "port-conflict",
                "wrong-address",
            )
        ),
    ]
    for package, case, expected in cases:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", runner, node, str(probe)],
            env={
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "HOME": str(tmp_path),
                "RND_PROOF_CASE": case,
                "RND_PROOF_ROOT": str(project),
                "RND_PROOF_ENTRY": (package / "dist/node/index.js").as_uri(),
                "RND_PROOF_URL": (package / "dist/node/chunks/config.js").as_uri(),
            },
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0 and not result.stderr
        receipt = json.loads(result.stdout)
        assert receipt["success"] is expected, case
        assert receipt["listenCalls"] == 1 and receipt["exactRequest"] is True
        if expected:
            assert receipt["sameServer"] and receipt["noOsPatch"] and receipt["postHook"]
            assert receipt["middlewares"] == 7
            assert receipt["urls"] == {"local": ["http://127.0.0.1:5173/"], "network": []}
        elif case != "port-conflict":
            assert receipt["systemError"] and receipt["syscall"] and receipt["errno"] == 1
