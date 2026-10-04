# tests/test_capability_execution_gate.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench`、`workbench.catalog`、`workbench.domain`、`workbench.errors`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `record`（L21–L22）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`profile_record`。 返回路径：L22的`profile_record()`。
- `receipt`（L25–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`execution.verifier_identity`、`execution.profile_binding`、`record`、`Selection().model_dump`、`Selection`、`dict.fromkeys`、`dependency_evidence`、`digest`。 返回路径：L26的`{ "protocol": execution.PROTOCOL, "passed": True, "verifier_identity": execution.verifier_…`。
- `test_old_partial_wrong_scope_or_forged_success_never_admits`（L62–L66）：接收`field`、`value`。 调用`receipt`、`pytest.raises`、`execution.require_security_receipt`、`record`、`pytest.mark.parametrize`、`Selection(template="fastapiadmin").model_dump`、`Selection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_receipt_requires_every_adversarial_check_and_exact_schema`（L69–L80）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L71断言`execution.require_security_receipt(good, record()) == good`；L72遍历`execution.SECURITY_CHECKS`。 调用`receipt`、`execution.require_security_receipt`、`record`、`copy.deepcopy`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_opt_in_is_not_enough_and_missing_gate_does_not_invoke_profile`（L83–L97）：接收`tmp_path`、`monkeypatch`。 控制顺序：L88断言`not settings.capability_execution_enabled`。 调用`monkeypatch.setattr`、`pytest.fail`、`Settings`、`pytest.raises`、`execution.capability_execution_prerequisites`、`Selection().model_dump`、`Selection`、`Selection(template="yudao-vben").model_dump`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preflight_binds_live_profile_and_receipt_then_rejects_drift`（L100–L139）：接收`tmp_path`、`monkeypatch`。 控制顺序：L126断言`execution.capability_execution_prerequisites(settings, Selection().model_dump()) == (…`；L130断言`calls == [(installation, "rnd-python-test")]`；L139断言`len(calls) == 2`。 调用`installation.mkdir`、`path.write_text`、`json.dumps`、`receipt`、`monkeypatch.setattr`、`Settings`、`execution.capability_execution_prerequisites`、`Selection().model_dump`、`Selection`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_preflight_binds_live_profile_and_receipt_then_rejects_drift.verified`（L112–L114）：接收`directory`、`snapshot`。 调用`calls.append`、`record`。 返回路径：L114的`record()`。
- `resources`（L142–L150）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L143的`{ "Memory": 2 * 1024**3, "MemorySwap": 2 * 1024**3, "CpuPeriod": 100000, "CpuQuota": 10000…`。
- `test_actual_resources_cannot_be_unlimited_or_merely_requested`（L167–L172）：接收`field`、`value`。 控制顺序：L169断言`profile.require_execution_resources(host)["tmpfs_bytes"] == 1073741824`。 调用`resources`、`profile.require_execution_resources`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_child_resource_limits_do_not_change_parent_limits`（L176–L194）：接收`tmp_path`。 控制顺序：L189断言`result.returncode == 0`；L191断言`actual["RLIMIT_FSIZE"] == [32 * 1024 * 1024] * 2`；L192断言`actual["RLIMIT_NPROC"][1] <= 128`；L193断言`actual["RLIMIT_NOFILE"][1] <= 256`；L194断言`resource.getrlimit(resource.RLIMIT_NOFILE) == before`。 调用`resource.getrlimit`、`str`、`subprocess.run`、`json.loads`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_package_factory_is_recognized_without_allowing_stack_replacement`（L197–L219）：接收`tmp_path`。 控制顺序：L216断言`inspect_stack(tmp_path, plan)["launcher"] == "uvicorn"`。 调用`entry.parent.mkdir`、`entry.write_text`、`front.mkdir`、`(front / "package.json").write_text`、`(front / "Page.vue").write_text`、`SimpleNamespace`、`Selection`、`inspect_stack`、`plan.runtime.start.argv.remove`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_landlock_denies_symlink_proc_and_inherited_fd_escapes`（L223–L256）：接收`tmp_path`。 控制顺序：L251按`process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1"`分支；L253断言`process.returncode == 0`；L254断言`process.stdout.strip() == "real-kernel-confinement-passed"`；L255断言`outside.read_text() == "original"`；L256断言`(writable / "ordinary").read_text() == "allowed"`。 调用`writable.mkdir`、`outside.write_text`、`(writable / "escape").symlink_to`、`str`、`subprocess.run`、`os.environ.get`、`pytest.skip`、`process.stdout.strip`、`outside.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_libseccomp_blocks_socket_type_flags_and_all_connect_destinations`（L260–L295）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L292按`process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1"`分支；L294断言`process.returncode == 0`；L295断言`process.stdout.strip() == "real-seccomp-passed"`。 调用`str`、`subprocess.run`、`os.environ.get`、`pytest.skip`、`process.stdout.strip`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_execution_gate.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L295。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12030`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_execution_gate.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ad63ebea8a86e42744bfdee4f493a39a722668212415532d49d0b5bfc6682f58"} -->
````python
# tests/test_capability_execution_gate.py
"""Admission contracts; fixtures here never create a live safety attestation."""

import copy
import json
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest
from capability_dependency_fixtures import dependency_evidence, profile_record

from scripts import daytona_capability_profile as profile
from workbench import capability_execution as execution
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.errors import UnsupportedScope
from workbench.settings import ROOT, Settings


def record():
    return profile_record()


def receipt():
    return {
        "protocol": execution.PROTOCOL,
        "passed": True,
        "verifier_identity": execution.verifier_identity(),
        "profile": execution.profile_binding(record()),
        "selection": Selection().model_dump(),
        "checks": dict.fromkeys(execution.SECURITY_CHECKS, True),
        "positive_product": True,
        "cleanup": "deleted",
        "paid_model_calls": 0,
        "restart_kind": "application_process",
        "browser_image": "sha256:" + "5" * 64,
        "preinstalled_dependencies": dependency_evidence(),
        "positive_source_digest": digest({}),
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("passed", 1),
        ("paid_model_calls", False),
        ("paid_model_calls", 1),
        ("verifier_identity", "0" * 64),
        ("checks", {}),
        ("positive_product", False),
        ("cleanup", "pending"),
        ("restart_kind", "container"),
        ("selection", Selection(template="fastapiadmin").model_dump()),
        ("profile", {}),
        ("protocol", "fixed-authored-app"),
        ("protocol", "custom-source-isolation-v1"),
        ("preinstalled_dependencies", {"offline_install": True}),
        ("positive_source_digest", "0" * 64),
    ],
)
def test_old_partial_wrong_scope_or_forged_success_never_admits(field, value):
    candidate = receipt()
    candidate[field] = value
    with pytest.raises(ValueError):
        execution.require_security_receipt(candidate, record())


def test_receipt_requires_every_adversarial_check_and_exact_schema():
    good = receipt()
    assert execution.require_security_receipt(good, record()) == good
    for key in execution.SECURITY_CHECKS:
        bad = copy.deepcopy(good)
        bad["checks"][key] = 1
        with pytest.raises(ValueError):
            execution.require_security_receipt(bad, record())
    bad = copy.deepcopy(good)
    bad["model_says_safe"] = True
    with pytest.raises(ValueError):
        execution.require_security_receipt(bad, record())


def test_opt_in_is_not_enough_and_missing_gate_does_not_invoke_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(
        profile, "require_profile", lambda *args: pytest.fail("Unexpected profile access")
    )
    settings = Settings(_env_file=None, data_dir=tmp_path)
    assert not settings.capability_execution_enabled
    with pytest.raises(UnsupportedScope, match="显式启用"):
        execution.capability_execution_prerequisites(settings, Selection().model_dump())
    settings.capability_execution_enabled = True
    with pytest.raises(UnsupportedScope, match="原技术栈"):
        execution.capability_execution_prerequisites(
            settings, Selection(template="yudao-vben").model_dump()
        )
    with pytest.raises(UnsupportedScope, match="宿主"):
        execution.capability_execution_prerequisites(settings, Selection().model_dump())


def test_preflight_binds_live_profile_and_receipt_then_rejects_drift(tmp_path, monkeypatch):
    import workbench.sandbox as sandbox
    from workbench import capability_browser_isolation as browser

    installation = tmp_path / "owned-installation"
    installation.mkdir()
    path = installation / execution.RECEIPT
    path.write_text(json.dumps(receipt()))
    monkeypatch.setattr(sandbox, "validate_configuration", lambda *args: None)
    monkeypatch.setattr(sandbox, "snapshot_for", lambda *args: "rnd-python-test")
    calls = []

    def verified(directory, snapshot):
        calls.append((directory, snapshot))
        return record()

    monkeypatch.setattr(profile, "require_profile", verified)
    monkeypatch.setattr(browser, "require_browser_acceptance", lambda image: image)
    settings = Settings(
        _env_file=None,
        data_dir=tmp_path / "state",
        sandbox_provider="daytona",
        capability_execution_enabled=True,
        capability_profile_directory=installation,
        capability_browser_image="sha256:" + "5" * 64,
    )
    assert execution.capability_execution_prerequisites(settings, Selection().model_dump()) == (
        installation,
        record(),
    )
    assert calls == [(installation, "rnd-python-test")]
    bad = receipt()
    bad["profile"]["runner_image_id"] = "sha256:" + "9" * 64
    path.write_text(json.dumps(bad))
    with pytest.raises(UnsupportedScope, match="真实安全正反例"):
        execution.capability_execution_prerequisites(settings, Selection().model_dump())
    settings.capability_profile_directory = settings.data_dir / "runs" / "candidate"
    with pytest.raises(UnsupportedScope):
        execution.capability_execution_prerequisites(settings, Selection().model_dump())
    assert len(calls) == 2


def resources():
    return {
        "Memory": 2 * 1024**3,
        "MemorySwap": 2 * 1024**3,
        "CpuPeriod": 100000,
        "CpuQuota": 100000,
        "PidsLimit": 256,
        "Tmpfs": {"/tmp": "rw,nosuid,nodev,size=1073741824,mode=1777"},
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("Memory", 0),
        ("Memory", True),
        ("MemorySwap", -1),
        ("CpuPeriod", 0),
        ("CpuQuota", -1),
        ("CpuQuota", 200000),
        ("PidsLimit", -1),
        ("Tmpfs", {}),
        ("Tmpfs", {"/tmp": "rw,size=0"}),
    ],
)
def test_actual_resources_cannot_be_unlimited_or_merely_requested(field, value):
    host = resources()
    assert profile.require_execution_resources(host)["tmpfs_bytes"] == 1073741824
    host[field] = value
    with pytest.raises(ValueError, match="actual bounded"):
        profile.require_execution_resources(host)


@pytest.mark.skipif(os.name != "posix", reason="Disposable Unix resource limits")
def test_real_child_resource_limits_do_not_change_parent_limits(tmp_path):
    import resource

    before = resource.getrlimit(resource.RLIMIT_NOFILE)
    source = (
        "import runpy,json,resource; "
        f"m=runpy.run_path({str(ROOT / 'scripts/capability_guard.py')!r}); "
        "m['restrict_resources'](); "
        "print(json.dumps({n:resource.getrlimit(getattr(resource,n)) for n in m['RESOURCE_LIMITS']}))"
    )
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, result.stderr
    actual = json.loads(result.stdout)
    assert actual["RLIMIT_FSIZE"] == [32 * 1024 * 1024] * 2
    assert actual["RLIMIT_NPROC"][1] <= 128
    assert actual["RLIMIT_NOFILE"][1] <= 256
    assert resource.getrlimit(resource.RLIMIT_NOFILE) == before


def test_native_package_factory_is_recognized_without_allowing_stack_replacement(tmp_path):
    from workbench.capability_stack import inspect_stack
    from workbench.capability_verification import CheckFailure

    entry = tmp_path / "backend/app/__init__.py"
    entry.parent.mkdir(parents=True)
    entry.write_text("from fastapi import FastAPI\ndef create_app():\n    return FastAPI()\n")
    front = tmp_path / "frontend/web"
    front.mkdir(parents=True)
    (front / "package.json").write_text('{"dependencies":{"vue":"3"}}')
    (front / "Page.vue").write_text("<template><p>fixture only</p></template>")
    plan = SimpleNamespace(
        selection=Selection(template="fastapiadmin"),
        runtime=SimpleNamespace(
            start=SimpleNamespace(
                argv=["python", "-m", "uvicorn", "app:create_app", "--factory"], cwd="backend"
            )
        ),
    )
    assert inspect_stack(tmp_path, plan)["launcher"] == "uvicorn"
    plan.runtime.start.argv.remove("--factory")
    with pytest.raises(CheckFailure, match="原生"):
        inspect_stack(tmp_path, plan)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only kernel confinement")
def test_real_landlock_denies_symlink_proc_and_inherited_fd_escapes(tmp_path):
    writable = tmp_path / "allowed"
    writable.mkdir()
    outside = tmp_path / "outside"
    outside.write_text("original")
    (writable / "escape").symlink_to(outside)
    source = f"""
import ctypes,errno,json,os,runpy,sys
m=runpy.run_path({str(ROOT / "scripts/capability_guard.py")!r})
restrict=m['restrict_tcp'];restrict.__globals__['WRITABLE_ROOT']={str(writable)!r}
inherited=os.open({str(outside)!r},os.O_WRONLY)
libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
if libc.syscall(444,0,0,1)<6:sys.exit(78)
restrict(set(),set(),filesystem=True)
for path in [{str(outside)!r},{str(writable / "escape")!r},'/proc/self/root'+{str(outside)!r}]:
 try:
  with open(path,'w') as f:f.write('escaped')
 except OSError as exc:assert exc.errno in (errno.EACCES,errno.EPERM)
 else:raise AssertionError('write escaped')
try:os.write(inherited,b'escape')
except OSError as exc:assert exc.errno==errno.EBADF
else:raise AssertionError('inherited descriptor escaped')
with open({str(writable / "ordinary")!r},'w') as f:f.write('allowed')
print('real-kernel-confinement-passed')
"""
    process = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=15
    )
    if process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1":
        pytest.skip("Host kernel/security profile cannot run mandatory live Landlock checks")
    assert process.returncode == 0, process.stderr
    assert process.stdout.strip() == "real-kernel-confinement-passed"
    assert outside.read_text() == "original"
    assert (writable / "ordinary").read_text() == "allowed"


@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only per-process seccomp")
def test_real_libseccomp_blocks_socket_type_flags_and_all_connect_destinations():
    source = f"""
import ctypes,errno,runpy,socket,sys
m=runpy.run_path({str(ROOT / "scripts/capability_guard.py")!r})
try:m['restrict_sockets']()
except RuntimeError as error:
 if str(error)=='Kernel refused the socket security filter':sys.exit(78)
 raise
def blocked(operation):
 try:operation()
 except OSError as exc:assert exc.errno==errno.EPERM
 else:raise AssertionError('socket policy bypassed')
for family in (socket.AF_INET,socket.AF_INET6,socket.AF_PACKET):
 for kind in (socket.SOCK_DGRAM,socket.SOCK_RAW):
  for flags in (0,socket.SOCK_CLOEXEC,socket.SOCK_NONBLOCK,socket.SOCK_CLOEXEC|socket.SOCK_NONBLOCK):
   blocked(lambda:socket.socket(family,kind|flags))
for kind in (socket.SOCK_DGRAM,socket.SOCK_SEQPACKET):
 for flags in (0,socket.SOCK_CLOEXEC|socket.SOCK_NONBLOCK):
  blocked(lambda:socket.socketpair(socket.AF_UNIX,kind|flags))
for family,addresses in ((socket.AF_INET,('127.0.0.1','192.0.2.1')),(socket.AF_INET6,('::1','2001:db8::1'))):
 for address in addresses:
  with socket.socket(family,socket.SOCK_STREAM|socket.SOCK_CLOEXEC) as s:
   blocked(lambda:s.connect((address,8123)))
a,b=socket.socketpair();a.send(b'ok');assert b.recv(2)==b'ok';a.close();b.close()
with socket.socket() as s:s.bind(('127.0.0.1',0));s.listen(1)
libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
assert libc.syscall(425,0,0)==-1 and ctypes.get_errno()==errno.EPERM
print('real-seccomp-passed')
"""
    process = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=15
    )
    if process.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1":
        pytest.skip("Host security profile refuses additional child seccomp filters")
    assert process.returncode == 0, process.stderr
    assert process.stdout.strip() == "real-seccomp-passed"
````
