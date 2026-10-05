# tests/test_capability_native_preview_patch.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `patch_tree`（L26–L36）：接收`tmp_path`、`monkeypatch`。 控制顺序：L27按`os.name == "nt"`分支。 调用`pytest.skip`、`target.parent.mkdir`、`target.write_bytes`、`(root / "vite").symlink_to`、`monkeypatch.setattr`。 返回路径：L36的`root, target`。
- `fixture_patch`（L39–L47）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`hashlib.sha256(b"patched fixture").hexdigest`、`hashlib.sha256`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `fixture_patch.transform`（L40–L42）：接收`raw`。 控制顺序：L41断言`raw == b"original fixture"`。 返回路径：L42的`b"patched fixture"`。
- `test_patch_and_collector_independently_bind_the_installed_file`（L50–L60）：接收`patch_tree`、`monkeypatch`。 控制顺序：L54断言`target.read_bytes() == b"patched fixture"`；L55断言`record["relative_path"] == PACKAGE + build.VITE_PREVIEW_SUFFIX`；L56断言`build.native_preview_patch_provenance() == [record]`；L60断言`(root / "vite").readlink().as_posix() == PACKAGE`。 调用`fixture_patch`、`build.patch_native_preview`、`target.read_bytes`、`build.native_preview_patch_provenance`、`target.write_bytes`、`pytest.raises`、`(root / "vite").readlink().as_posix`、`(root / "vite").readlink`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_patch_requires_nonroot_before_opening_any_target`（L63–L69）：接收`patch_tree`、`monkeypatch`。 控制顺序：L69断言`target.read_bytes() == b"original fixture"`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`build.patch_native_preview`、`target.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_upstream_is_rejected_without_mutation`（L72–L76）：接收`patch_tree`。 控制顺序：L76断言`target.read_bytes() == b"original fixture"`。 调用`pytest.raises`、`build.patch_native_preview`、`target.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsafe_targets_are_rejected_before_writing_outside_sentinel`（L84–L120）：接收`patch_tree`、`monkeypatch`、`tmp_path`、`kind`。 控制顺序：L92按`kind == "root-link"`分支；L96按`kind == "store-link"`分支；L101按`kind == "ancestor-link"`分支；L106按`kind == "leaf-link"`分支；L109按`kind == "hardlink"`分支；L112按`kind == "setid"`分支；L120断言`sentinel.read_bytes() == b"do not modify"`。 调用`outside.mkdir`、`sentinel.write_bytes`、`alias.symlink_to`、`monkeypatch.setattr`、`store.rename`、`store.symlink_to`、`parent.rename`、`parent.symlink_to`、`target.unlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_package_link_must_match_the_pinned_lexical_scope`（L126–L132）：接收`patch_tree`、`link`。 控制顺序：L132断言`target.read_bytes() == b"original fixture"`。 调用`(root / "vite").unlink`、`(root / "vite").symlink_to`、`pytest.raises`、`build.patch_native_preview`、`target.read_bytes`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_transform_rejects_missing_or_ambiguous_anchors`（L136–L144）：接收`monkeypatch`、`count`。 调用`monkeypatch.setattr`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`、`pytest.raises`、`build.adapt_native_preview_source`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_official_vite`（L147–L160）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L149按`not value and os.environ.get("RND_NATIVE_TEST_NODE_MODULES")`分支；L151按`not value`分支；L152按`os.environ.get("RND_REQUIRE_NATIVE_VITE_TESTS") == "1"`分支；L157断言`(descriptor["name"], descriptor["version"]) == ("vite", "7.3.3")`；L159断言`hashlib.sha256(source.read_bytes()).hexdigest() == build.VITE_PREVIEW_UPSTREAM_SHA256`。 调用`os.environ.get`、`str`、`Path`、`pytest.fail`、`pytest.skip`、`Path(value).resolve`、`json.loads`、`(package / "package.json").read_bytes`、`hashlib.sha256(source.read_bytes()).hexdigest`等。 返回路径：L160的`package`。
- `test_mandatory_vite_preview_cannot_skip_missing_or_invalid_tool_tree`（L163–L171）：接收`monkeypatch`、`tmp_path`。 调用`monkeypatch.setenv`、`monkeypatch.delenv`、`pytest.raises`、`require_official_vite`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_ci_requires_preview_matrix_with_existing_pinned_tool_tree`（L174–L181）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L178断言`"RND_REQUIRE_NATIVE_VITE_TESTS: '1'" in step`；L179断言`"RND_REQUIRE_NODE_TESTS: '1'" in step`；L180断言`"${{ github.workspace }}/.native/tool-product/frontend/web/node_modules" in step`；L181断言`"tests/test_capability_native_preview_patch.py" in step`。 调用`(ROOT / ".github/workflows/native-capability-profile.yml").read_t…`、`workflow.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `official_vite`（L185–L199）：接收`tmp_path`。 控制顺序：L186按`os.name == "nt"`分支；L195遍历`package.parent.iterdir()`；L196按`dependency.name != "vite"`分支。 调用`pytest.skip`、`require_official_vite`、`destination.parent.mkdir`、`shutil.copytree`、`package.parent.iterdir`、`(destination.parent / dependency.name).symlink_to`、`dependency.resolve`、`(modules / "vite").symlink_to`。 返回路径：L199的`package, modules, destination`。
- `test_exact_official_patch_hash_and_package_descriptors_preserved`（L202–L217）：接收`official_vite`、`monkeypatch`、`tmp_path`。 控制顺序：L209断言`record["upstream_sha256"] == build.VITE_PREVIEW_UPSTREAM_SHA256`；L210断言`record["patched_sha256"] == build.VITE_PREVIEW_PATCHED_SHA256`；L211断言`(copied / "package.json").read_bytes() == before`；L212断言`hashlib.sha256((original / "dist/node/chunks/config.js").read_bytes()).hexdigest() ==…`；L215断言`build.native_preview_patch_provenance() == [record]`。 调用`(copied / "package.json").read_bytes`、`monkeypatch.setattr`、`build.patch_native_preview`、`hashlib.sha256((original / "dist/node/chunks/config.js").read_byt…`、`hashlib.sha256`、`(original / "dist/node/chunks/config.js").read_bytes`、`build.native_preview_patch_provenance`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_derived_hash_mismatch_fails_before_mutating_official_source`（L220–L228）：接收`official_vite`、`monkeypatch`。 控制顺序：L228断言`target.read_bytes() == before`。 调用`target.read_bytes`、`monkeypatch.setattr`、`pytest.raises`、`build.patch_native_preview`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_patched_function_rethrows_non_eperm_and_non_preview_cases`（L231–L290）：接收`official_vite`、`monkeypatch`、`tmp_path`。 控制顺序：L289断言`result.returncode == 0 and not result.stderr`；L290断言`json.loads(result.stdout) == {"passed": True, "count": 17}`。 调用`monkeypatch.setattr`、`build.patch_native_preview`、`script.write_text`、`subprocess.run`、`shutil.which`、`str`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_vite_before_after_and_forged_hook_failures_under_original_filter`（L338–L395）：接收`official_vite`、`monkeypatch`、`tmp_path`。 控制顺序：L343断言`node`；L371遍历`cases`；L386断言`result.returncode == 0 and not result.stderr`；L388断言`receipt["success"] is expected`；L389断言`receipt["listenCalls"] == 1 and receipt["exactRequest"] is True`；L390按`expected`分支；L391断言`receipt["sameServer"] and receipt["noOsPatch"] and receipt["postHook"]`；L392断言`receipt["middlewares"] == 7`。后续分支沿下方源码相同行号继续阅读。 调用`shutil.which`、`monkeypatch.setattr`、`build.patch_native_preview`、`(project / "dist").mkdir`、`(project / "vite.config.mjs").write_text`、`probe.write_text`、`str`、`subprocess.run`、`os.environ.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_preview_patch.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L395。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`17151`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_preview_patch.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0773a99a93059d77e76ab038b2b5d24fcdafd5cad1f1a8fc0a0bda8a6562bbf7"} -->
````python
# tests/test_capability_native_preview_patch.py
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
````
