# tests/test_capability_browser_seccomp_proposal.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_browser_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `read`（L18–L19）：接收`name`。 调用`json.loads`、`(DIRECTORY / name).read_text`。 返回路径：L19的`json.loads((DIRECTORY / name).read_text())`。
- `added_rule`（L22–L31）：接收`name`、`value`。 控制顺序：L29按`value is not None`分支。 返回路径：L31的`rule`。
- `profiles`（L43–L44）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`read`。 返回路径：L44的`read("moby-v28.0.4-default.json"), read("chromium141-docker28-amd64.proposal.json")`。
- `test_pinned_provenance_hashes_and_inactive_status`（L47–L62）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L49断言`manifest["status"] == "inactive-review-only"`；L50断言`manifest["activation_authorized"] is False`；L51断言`manifest["live_validation"] is False`；L52断言`manifest["scope"]["initial_capability_bounding_set"] == []`；L53遍历`(("baseline", BASELINE_SHA256), ("proposal", PROPOSAL_SHA256))`；L55断言`hashlib.sha256((DIRECTORY / record["file"]).read_bytes()).hexdigest() == expected`；L56断言`record["sha256"] == expected`；L57断言`manifest["baseline"]["upstream_commit"] == "6430e49a55babd9b8f4d08e70ecb2b68900770fe"`。后续分支沿下方源码相同行号继续阅读。 调用`read`、`hashlib.sha256((DIRECTORY / record["file"]).read_bytes()).hexdige…`、`hashlib.sha256`、`(DIRECTORY / record["file"]).read_bytes`、`len`、`all`、`(DIRECTORY / manifest["upstream_license"]).read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_append_only_delta_preserves_every_baseline_rule_and_property`（L65–L76）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L69断言`proposal == expected`；L71断言`patch == [{"op": "add", "path": "/syscalls/-", "value": r} for r in EXPECTED_DELTA]`；L73遍历`patch`；L75断言`replay == proposal`；L76断言`{n for r in EXPECTED_DELTA for n in r["names"]} == {"clone", "unshare", "chroot"}`。 调用`profiles`、`copy.deepcopy`、`expected["syscalls"].extend`、`read`、`replay["syscalls"].append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `applies`（L79–L87）：接收`rule`、`host_arch`、`caps`。 源码说明：Moby host filtering only; not a kernel/seccomp emulator or ABI proof.。 调用`rule.get`、`inc.get`、`exc.get`、`all`、`any`。 返回路径：L82的`(not inc.get("arches") or host_arch in inc["arches"]) and host_arch not in exc.get("arches…`。
- `decision`（L90–L109）：接收`profile`、`name`、`arg0`、`host_arch`。 源码说明：Evaluate the explicit scalar rules used by these negative test cases.。 控制顺序：L92遍历`profile["syscalls"]`；L93按`name not in rule["names"] or not applies(rule, host_arch)`分支；L96遍历`rule.get("args") or []`；L97断言`arg["index"] == 0`；L99按`op == "SCMP_CMP_EQ"`分支；L101按`op == "SCMP_CMP_NE"`分支；L103按`op == "SCMP_CMP_MASKED_EQ"`分支；L106抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`applies`、`rule.get`、`arg.get`、`AssertionError`。 返回路径：L108的`rule["action"], rule.get("errnoRet")`；L109的`profile["defaultAction"], profile["defaultErrnoRet"]`。
- `test_only_source_justified_calls_become_allowed`（L122–L125）：接收`name`、`arg`。 控制顺序：L124断言`decision(base, name, arg)[0] == "SCMP_ACT_ERRNO"`；L125断言`decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"`。 调用`profiles`、`decision`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_forbidden_calls_extra_flags_and_alternate_signals_stay_denied`（L157–L162）：接收`name`、`arg`。 控制顺序：L159断言`decision(base, name, arg) == decision(proposal, name, arg)`；L160断言`decision(proposal, name, arg)[0] == "SCMP_ACT_ERRNO"`；L161按`name == "clone3"`分支；L162断言`decision(proposal, name, arg) == ("SCMP_ACT_ERRNO", 38)`。 调用`profiles`、`decision`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrelated_baseline_allowances_are_preserved`（L176–L179）：接收`name`、`arg`。 控制顺序：L178断言`decision(base, name, arg) == decision(proposal, name, arg)`；L179断言`decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"`。 调用`profiles`、`decision`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inherited_vsock_limits_do_not_claim_complete_abi_containment`（L183–L192）：接收`name`、`arg`。 控制顺序：L188断言`decision(base, name, arg) == decision(proposal, name, arg)`；L189断言`decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"`；L190断言`decision(proposal, "socket", 40)[0] == "SCMP_ACT_ERRNO"`；L192断言`{"SCMP_ARCH_X86", "SCMP_ARCH_X32"} <= set(compat["subArchitectures"])`。 调用`profiles`、`decision`、`next`、`set`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_proposal_is_not_selected_copied_or_part_of_existing_acceptance`（L195–L211）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L197断言`[c for c in command if c.startswith("--security-opt")] == [ "--security-opt=no-new-pr…`；L200断言`"--cap-drop=ALL" in command`；L201遍历`[ ROOT / "tools/browser/Dockerfile", *ROOT.glob(".github/workflow…`；L208断言`"chromium141-docker28-amd64.proposal.json" not in text`；L209断言`"tools/browser/review-only/" not in text`；L210断言`all(not applies(r, "arm64") for r in EXPECTED_DELTA)`；L211断言`all(not applies(r, caps=("CAP_SYS_ADMIN",)) for r in EXPECTED_DELTA)`。 调用`worker_command`、`c.startswith`、`ROOT.glob`、`path.read_text`、`all`、`applies`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_seccomp_proposal.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L211。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7784`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_seccomp_proposal.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c52ebdedbbe3619355d0e3af1e8ad42e92eeca38eba4c0aa88992e382e75339d"} -->
````python
# tests/test_capability_browser_seccomp_proposal.py
"""Static review-artifact checks; never load seccomp or launch containers."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from workbench.capability_browser_isolation import worker_command

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "tools/browser/review-only"
BASELINE_SHA256 = "9c1025c88ccaa517b648da571961838744ea2137f176bfe6a48b21294cae9c76"
PROPOSAL_SHA256 = "f62d10d5ce466dfd0714d61891ef7b94445367c8a6a303302f4c3956687f3504"


def read(name):
    return json.loads((DIRECTORY / name).read_text())


def added_rule(name, value=None):
    rule = {
        "names": [name],
        "action": "SCMP_ACT_ALLOW",
        "includes": {"arches": ["amd64"]},
        "excludes": {"caps": ["CAP_SYS_ADMIN"]},
    }
    if value is not None:
        rule["args"] = [{"index": 0, "value": value, "op": "SCMP_CMP_EQ"}]
    return rule


EXPECTED_DELTA = [
    added_rule("clone", 0x10000011),
    added_rule("clone", 0x70000011),
    added_rule("clone", 0x20000011),
    added_rule("unshare", 0x10000000),
    added_rule("chroot"),
]


def profiles():
    return read("moby-v28.0.4-default.json"), read("chromium141-docker28-amd64.proposal.json")


def test_pinned_provenance_hashes_and_inactive_status():
    manifest = read("proposal-manifest.json")
    assert manifest["status"] == "inactive-review-only"
    assert manifest["activation_authorized"] is False
    assert manifest["live_validation"] is False
    assert manifest["scope"]["initial_capability_bounding_set"] == []
    for key, expected in (("baseline", BASELINE_SHA256), ("proposal", PROPOSAL_SHA256)):
        record = manifest[key]
        assert hashlib.sha256((DIRECTORY / record["file"]).read_bytes()).hexdigest() == expected
        assert record["sha256"] == expected
    assert manifest["baseline"]["upstream_commit"] == "6430e49a55babd9b8f4d08e70ecb2b68900770fe"
    assert len(manifest["chromium_sources"]) == 4
    assert all(
        "9f043f63b0e5b728c8d09f3e3ddfc1681a4bd58e" in s["url"] for s in manifest["chromium_sources"]
    )
    assert "Apache License" in (DIRECTORY / manifest["upstream_license"]).read_text()


def test_exact_append_only_delta_preserves_every_baseline_rule_and_property():
    base, proposal = profiles()
    expected = copy.deepcopy(base)
    expected["syscalls"].extend(EXPECTED_DELTA)
    assert proposal == expected
    patch = read("proposal-manifest.json")["json_patch"]
    assert patch == [{"op": "add", "path": "/syscalls/-", "value": r} for r in EXPECTED_DELTA]
    replay = copy.deepcopy(base)
    for operation in patch:
        replay["syscalls"].append(operation["value"])
    assert replay == proposal
    assert {n for r in EXPECTED_DELTA for n in r["names"]} == {"clone", "unshare", "chroot"}


def applies(rule, host_arch="amd64", caps=()):
    """Moby host filtering only; not a kernel/seccomp emulator or ABI proof."""
    inc, exc = rule.get("includes", {}), rule.get("excludes", {})
    return (
        (not inc.get("arches") or host_arch in inc["arches"])
        and host_arch not in exc.get("arches", [])
        and all(c in caps for c in inc.get("caps", []))
        and not any(c in caps for c in exc.get("caps", []))
    )


def decision(profile, name, arg0=0, host_arch="amd64"):
    """Evaluate the explicit scalar rules used by these negative test cases."""
    for rule in profile["syscalls"]:
        if name not in rule["names"] or not applies(rule, host_arch):
            continue
        matches = True
        for arg in rule.get("args") or []:
            assert arg["index"] == 0  # Non-amd64 clone layouts are not simulated.
            op, value = arg["op"], arg["value"]
            if op == "SCMP_CMP_EQ":
                matches &= arg0 == value
            elif op == "SCMP_CMP_NE":
                matches &= arg0 != value
            elif op == "SCMP_CMP_MASKED_EQ":
                matches &= arg0 & value == arg.get("valueTwo", 0)
            else:
                raise AssertionError("Untested argument operation")
        if matches:
            return rule["action"], rule.get("errnoRet")
    return profile["defaultAction"], profile["defaultErrnoRet"]


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone", 0x10000011),
        ("clone", 0x70000011),
        ("clone", 0x20000011),
        ("unshare", 0x10000000),
        ("chroot", 12345),
    ],
)
def test_only_source_justified_calls_become_allowed(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg)[0] == "SCMP_ACT_ERRNO"
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone3", 0),
        ("setns", 0),
        ("setns", 0x10000000),
        ("io_uring_setup", 0),
        ("io_uring_enter", 0),
        ("io_uring_register", 0),
        ("socket", 40),
        ("mount", 0),
        ("pivot_root", 0),
        ("unshare", 0),
        ("unshare", 0x40000000),
        ("unshare", 0x20000),
        ("unshare", 0x70000000),
        ("unshare", 0x10000001),
        ("clone", 0x30000011),
        ("clone", 0x50000011),
        ("clone", 0x10000000),
        ("clone", 0x10000009),
        ("clone", 0x10020011),
        ("clone", 0x18000011),
        ("clone", 0x70000111),
        ("clone", 0x70000211),
        ("clone", 0x70010011),
        ("clone", 0x170000011),
    ],
)
def test_forbidden_calls_extra_flags_and_alternate_signals_stay_denied(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ERRNO"
    if name == "clone3":
        assert decision(proposal, name, arg) == ("SCMP_ACT_ERRNO", 38)


@pytest.mark.parametrize(
    "name,arg",
    [
        ("clone", 0x84311),
        ("clone", 17),
        ("socket", 2),
        ("landlock_create_ruleset", 0),
        ("openat2", 0),
        ("close_range", 0),
    ],
)
def test_unrelated_baseline_allowances_are_preserved(name, arg):
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"


@pytest.mark.parametrize("name,arg", [("socketcall", 1), ("socket", 0x100000028)])
def test_inherited_vsock_limits_do_not_claim_complete_abi_containment(name, arg):
    # Static rule matching only: neither compiled BPF nor successful socket
    # creation is established. The full-word comparison precedes kernel int
    # truncation; socketcall remains relevant to inherited compatibility ABIs.
    base, proposal = profiles()
    assert decision(base, name, arg) == decision(proposal, name, arg)
    assert decision(proposal, name, arg)[0] == "SCMP_ACT_ALLOW"
    assert decision(proposal, "socket", 40)[0] == "SCMP_ACT_ERRNO"
    compat = next(row for row in proposal["archMap"] if row["architecture"] == "SCMP_ARCH_X86_64")
    assert {"SCMP_ARCH_X86", "SCMP_ARCH_X32"} <= set(compat["subArchitectures"])


def test_proposal_is_not_selected_copied_or_part_of_existing_acceptance():
    command = worker_command("sha256:" + "a" * 64, "rnd-browser-" + "b" * 32)
    assert [c for c in command if c.startswith("--security-opt")] == [
        "--security-opt=no-new-privileges:true"
    ]
    assert "--cap-drop=ALL" in command
    for path in [
        ROOT / "tools/browser/Dockerfile",
        *ROOT.glob(".github/workflows/*.yml"),
        *ROOT.glob("workbench/*.py"),
        *ROOT.glob("scripts/*.py"),
    ]:
        text = path.read_text()
        assert "chromium141-docker28-amd64.proposal.json" not in text
        assert "tools/browser/review-only/" not in text
    assert all(not applies(r, "arm64") for r in EXPECTED_DELTA)
    assert all(not applies(r, caps=("CAP_SYS_ADMIN",)) for r in EXPECTED_DELTA)
````
