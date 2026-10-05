# tests/test_capability_browser_seccomp_v2.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_browser_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `baseline`（L24–L30）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L26断言`hashlib.sha256(path.read_bytes()).hexdigest() == "9c1025c88ccaa517b648da571961838744e…`。 调用`hashlib.sha256(path.read_bytes()).hexdigest`、`hashlib.sha256`、`path.read_bytes`、`json.loads`、`path.read_text`。 返回路径：L30的`json.loads(path.read_text())`。
- `proposal`（L33–L36）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L35断言`hashlib.sha256(data).hexdigest() == PROPOSAL_SHA`。 调用`(DIRECTORY / "chromium141-docker28-native-amd64.proposal.json").r…`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`、`json.loads`。 返回路径：L36的`json.loads(data)`。
- `test_exact_restrictive_transport_abi_delta_and_namespace_allowances`（L39–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L41断言`value == review.build_profile(base)`；L42断言`value["defaultAction"] == base["defaultAction"] == "SCMP_ACT_ERRNO"`；L43断言`value["defaultErrnoRet"] == base["defaultErrnoRet"] == 1`；L44断言`value["archMap"] == [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]`；L48遍历`base["syscalls"]`；L49按`row["names"] == ["socket"]`分支；L54断言`value["syscalls"][: len(original)] == original`；L55断言`value["syscalls"][len(original) :] == review.namespace_rules() + review.transport_rul…`。后续分支沿下方源码相同行号继续阅读。 调用`baseline`、`proposal`、`review.build_profile`、`json.loads`、`json.dumps`、`original.append`、`len`、`review.namespace_rules`、`review.transport_rules`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_review_target_rejects_other_arch_abi_caps_version_or_unknown`（L79–L89）：接收`change`。 调用`dict`、`review.require_target`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bpf`（L93–L103）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L99按`not available`分支；L100按`os.getenv("RND_REQUIRE_SECCOMP_BPF") == "1"`分支。 调用`platform.system`、`platform.machine`、`ctypes.util.find_library`、`os.getenv`、`pytest.fail`、`pytest.skip`、`review.compile_bpf`、`proposal`、`pytest.fixture`。 返回路径：L103的`review.compile_bpf(proposal())`。
- `test_compiled_low32_vsock_denial_covers_socket_and_socketpair`（L106–L115）：接收`bpf`。 控制顺序：L109遍历`(41, 53)`；L110遍历`highs`；L111断言`review.evaluate_bpf(bpf, number, args=((high << 32) \| 40,)) == review.ERRNO \| 1`；L112遍历`[*range(128), 0x7FFFFFFF, 0xFFFFFFFF]`；L113遍历`(0, 1, 0xFFFFFFFF)`；L115断言`review.evaluate_bpf(bpf, number, args=((high << 32) \| low,)) == expected`。 调用`random.Random`、`randoms.getrandbits`、`range`、`review.evaluate_bpf`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compiled_x86_socketcall_and_direct_socket_abis_fail_closed`（L119–L120）：接收`bpf`、`number`、`args`。 控制顺序：L120断言`review.evaluate_bpf(bpf, number, arch=0x40000003, args=args) in {0, 0x80000000}`。 调用`review.evaluate_bpf`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compiled_x32_syscall_bit_fails_closed`（L124–L125）：接收`bpf`、`number`。 控制顺序：L125断言`review.evaluate_bpf(bpf, 0x40000000 \| number, args=(40,)) in {0, 0x80000000}`。 调用`review.evaluate_bpf`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compiled_other_audit_architectures_fail_closed`（L129–L130）：接收`bpf`、`arch`。 控制顺序：L130断言`review.evaluate_bpf(bpf, 41, arch=arch, args=(2,)) in {0, 0x80000000}`。 调用`review.evaluate_bpf`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compiled_only_justified_namespace_calls_allow_and_other_guards_hold`（L133–L144）：接收`bpf`。 控制顺序：L134遍历`(0x10000011, 0x70000011, 0x20000011, 17, 0x84311)`；L135断言`review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ALLOW`；L136遍历`(0x10000009, 0x30000011, 0x50000011, 0x70000111, 0x10020011, 0x17…`；L137断言`review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ERRNO \| 1`；L138断言`review.evaluate_bpf(bpf, 272, args=(0x10000000,)) == review.ALLOW`；L139遍历`(0, 0x40000000, 0x70000000, 0x10000001)`；L140断言`review.evaluate_bpf(bpf, 272, args=(flags,)) == review.ERRNO \| 1`；L141断言`review.evaluate_bpf(bpf, 161, args=(12345,)) == review.ALLOW`。后续分支沿下方源码相同行号继续阅读。 调用`review.evaluate_bpf`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_offline_export_symbols_are_used`（L147–L171）：接收`monkeypatch`、`bpf`。 控制顺序：L170断言`review.compile_bpf(proposal()) == bpf`；L171断言`observed == allowed`。 调用`set`、`monkeypatch.setattr`、`review.compile_bpf`、`proposal`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_offline_export_symbols_are_used.Proxy`（L160–L167）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_only_offline_export_symbols_are_used.Proxy.__init__`（L161–L162）：接收`path`。 调用`real`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_offline_export_symbols_are_used.Proxy.__getattr__`（L164–L167）：接收`name`。 控制顺序：L165断言`name in allowed`。 调用`observed.add`、`getattr`。 返回路径：L167的`getattr(self.inner, name)`。
- `test_v2_requires_explicit_approved_actions_selection`（L174–L183）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L176断言`manifest["status"] == "approved-actions-only-pending-live-proof"`；L177断言`manifest["activation_authorized"] is True`；L178断言`manifest["live_validation"] is False`；L179断言`manifest["proposal_sha256"] == PROPOSAL_SHA`；L181断言`[word for word in command if word.startswith("--security-opt")] == [ "--security-opt=…`。 调用`json.loads`、`(DIRECTORY / "proposal-manifest.json").read_text`、`worker_command`、`word.startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_seccomp_v2.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L183。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7317`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_seccomp_v2.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c891bb904484051fde354f2ef2a0d4dbbad4620dcc6f8087b6575500d79d7b7d"} -->
````python
# tests/test_capability_browser_seccomp_v2.py
"""Fixed policy validation: static artifacts and offline BPF; no filter is loaded."""

import ctypes.util
import hashlib
import importlib.util
import json
import os
import platform
import random
from pathlib import Path

import pytest

from workbench.capability_browser_isolation import worker_command

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "tools/browser/review-only-v2"
SPEC = importlib.util.spec_from_file_location("review_profile", DIRECTORY / "review_profile.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)
PROPOSAL_SHA = "9e4d4398b47e0bdbd937121091aa846ebdba68e758561b417951d9a56bd4c69f"


def baseline():
    path = ROOT / "tools/browser/review-only/moby-v28.0.4-default.json"
    assert (
        hashlib.sha256(path.read_bytes()).hexdigest()
        == "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76"
    )
    return json.loads(path.read_text())


def proposal():
    data = (DIRECTORY / "chromium141-docker28-native-amd64.proposal.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == PROPOSAL_SHA
    return json.loads(data)


def test_exact_restrictive_transport_abi_delta_and_namespace_allowances():
    base, value = baseline(), proposal()
    assert value == review.build_profile(base)
    assert value["defaultAction"] == base["defaultAction"] == "SCMP_ACT_ERRNO"
    assert value["defaultErrnoRet"] == base["defaultErrnoRet"] == 1
    assert value["archMap"] == [{"architecture": "SCMP_ARCH_X86_64", "subArchitectures": []}]
    # Baseline rule order/properties preserved except the explicitly removed
    # native socket allowance and two names removed from the broad allow group.
    original = []
    for row in base["syscalls"]:
        if row["names"] == ["socket"]:
            continue
        row = json.loads(json.dumps(row))
        row["names"] = [name for name in row["names"] if name not in {"socketcall", "socketpair"}]
        original.append(row)
    assert value["syscalls"][: len(original)] == original
    assert value["syscalls"][len(original) :] == review.namespace_rules() + review.transport_rules()
    assert len(review.namespace_rules()) == 5
    assert len(review.transport_rules()) == 64
    assert all("socketcall" not in row["names"] for row in value["syscalls"])
    assert not any(
        row["names"] == ["socket"] and row.get("args", [{}])[0].get("op") == "SCMP_CMP_NE"
        for row in value["syscalls"]
    )


@pytest.mark.parametrize(
    "change",
    [
        {"daemon_arch": "arm64"},
        {"daemon_arch": None},
        {"image_arch": "arm64"},
        {"docker_version": "28.0.5"},
        {"process_abi": "x86"},
        {"process_abi": "x32"},
        {"initial_caps": ["CAP_SYS_ADMIN"]},
        {"initial_caps": None},
        {"initial_caps": ()},
    ],
)
def test_review_target_rejects_other_arch_abi_caps_version_or_unknown(change):
    data = dict(
        daemon_arch="amd64",
        image_arch="amd64",
        docker_version="28.0.4",
        initial_caps=[],
        process_abi="x86_64",
    )
    review.require_target(**data)
    with pytest.raises(ValueError, match="no fallback"):
        review.require_target(**{**data, **change})


@pytest.fixture(scope="module")
def bpf():
    available = (
        platform.system() == "Linux"
        and platform.machine() == "x86_64"
        and ctypes.util.find_library("seccomp")
    )
    if not available:
        if os.getenv("RND_REQUIRE_SECCOMP_BPF") == "1":
            pytest.fail("Native Linux amd64/libseccomp offline compilation is mandatory")
        pytest.skip("Offline compiler unavailable; this is not live acceptance")
    return review.compile_bpf(proposal())


def test_compiled_low32_vsock_denial_covers_socket_and_socketpair(bpf):
    randoms = random.Random(14128)
    highs = [0, 1, 0x7FFFFFFF, 0xFFFFFFFF, *[randoms.getrandbits(32) for _ in range(100)]]
    for number in (41, 53):
        for high in highs:
            assert review.evaluate_bpf(bpf, number, args=((high << 32) | 40,)) == review.ERRNO | 1
        for low in [*range(128), 0x7FFFFFFF, 0xFFFFFFFF]:
            for high in (0, 1, 0xFFFFFFFF):
                expected = review.ERRNO | 1 if low == 40 else review.ALLOW
                assert review.evaluate_bpf(bpf, number, args=((high << 32) | low,)) == expected


@pytest.mark.parametrize("number,args", [(102, (1,)), (102, (8,)), (359, (40,)), (360, (40,))])
def test_compiled_x86_socketcall_and_direct_socket_abis_fail_closed(bpf, number, args):
    assert review.evaluate_bpf(bpf, number, arch=0x40000003, args=args) in {0, 0x80000000}


@pytest.mark.parametrize("number", [41, 53, 56, 161, 272, 435])
def test_compiled_x32_syscall_bit_fails_closed(bpf, number):
    assert review.evaluate_bpf(bpf, 0x40000000 | number, args=(40,)) in {0, 0x80000000}


@pytest.mark.parametrize("arch", [0xC00000B7, 0x40000028, 0, 0xFFFFFFFF])
def test_compiled_other_audit_architectures_fail_closed(bpf, arch):
    assert review.evaluate_bpf(bpf, 41, arch=arch, args=(2,)) in {0, 0x80000000}


def test_compiled_only_justified_namespace_calls_allow_and_other_guards_hold(bpf):
    for flags in (0x10000011, 0x70000011, 0x20000011, 17, 0x84311):
        assert review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ALLOW
    for flags in (0x10000009, 0x30000011, 0x50000011, 0x70000111, 0x10020011, 0x170000011):
        assert review.evaluate_bpf(bpf, 56, args=(flags,)) == review.ERRNO | 1
    assert review.evaluate_bpf(bpf, 272, args=(0x10000000,)) == review.ALLOW
    for flags in (0, 0x40000000, 0x70000000, 0x10000001):
        assert review.evaluate_bpf(bpf, 272, args=(flags,)) == review.ERRNO | 1
    assert review.evaluate_bpf(bpf, 161, args=(12345,)) == review.ALLOW
    assert review.evaluate_bpf(bpf, 435) == review.ERRNO | 38
    for number in (308, 425, 426, 427, 165, 155):
        assert review.evaluate_bpf(bpf, number) == review.ERRNO | 1


def test_only_offline_export_symbols_are_used(monkeypatch, bpf):
    # Recompile through a symbol-restricted proxy. No policy-loading symbol is
    # reachable through this helper; export writes bytes to a temporary file.
    real = review.ctypes.CDLL
    observed = set()
    allowed = {
        "seccomp_init",
        "seccomp_release",
        "seccomp_syscall_resolve_name",
        "seccomp_rule_add_array",
        "seccomp_export_bpf",
    }

    class Proxy:
        def __init__(self, path):
            self.inner = real(path)

        def __getattr__(self, name):
            assert name in allowed
            observed.add(name)
            return getattr(self.inner, name)

    monkeypatch.setattr(review.ctypes, "CDLL", Proxy)
    assert review.compile_bpf(proposal()) == bpf
    assert observed == allowed


def test_v2_requires_explicit_approved_actions_selection():
    manifest = json.loads((DIRECTORY / "proposal-manifest.json").read_text())
    assert manifest["status"] == "approved-actions-only-pending-live-proof"
    assert manifest["activation_authorized"] is True
    assert manifest["live_validation"] is False
    assert manifest["proposal_sha256"] == PROPOSAL_SHA
    command = worker_command("sha256:" + "a" * 64, "rnd-browser-" + "b" * 32)
    assert [word for word in command if word.startswith("--security-opt")] == [
        "--security-opt=no-new-privileges:true"
    ]
````
