# tests/test_capability_browser_activation_review.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `raw_receipt`（L11–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L13遍历`policy.RAW_CHECKS`。 调用`name.endswith`、`name.startswith`、`dict.fromkeys`。 返回路径：L26的`{ "protocol": "browser-seccomp-transport-v1", "architecture": "native-amd64", "expected_pr…`。
- `test_claimed_pass_cannot_override_contradictory_raw_evidence`（L46–L52）：接收`case`、`changes`。 控制顺序：L48断言`policy.require_raw_probe(receipt) is True`。 调用`raw_receipt`、`policy.require_raw_probe`、`copy.deepcopy`、`changed["observations"][case].update`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_same_runc_version_different_build_is_not_compiler_provenance`（L55–L104）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`object`、`iter`、`next`、`SimpleNamespace`、`( "runc version 1.2.5\ncommit: " + "b" * 40 + "\nspec: 1.2.0\nlib…`、`pytest.raises`、`policy.runtime_identity`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_browser_activation_review.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L104。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3702`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_browser_activation_review.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "65424164b15859b1ac374071fc22c1ed2c0215f3244660683f9a475b83b040f2"} -->
````python
# tests/test_capability_browser_activation_review.py
"""Independent activation regressions; mocked provenance only, no live syscalls."""

import copy
from types import SimpleNamespace

import pytest

from workbench import capability_browser_policy as policy


def raw_receipt():
    observations = {}
    for name in policy.RAW_CHECKS:
        killed = name.endswith("_killed")
        positive = name.startswith("native_")
        error = 38 if name == "clone3_enosys" else 1
        observations[name] = {
            "returned": not killed,
            "return": 0 if killed or positive else -error,
            "errno": 0 if killed or positive else error,
            "signal": 31 if killed else 0,
            "exit_status": 0 if name.startswith(("clone_user", "clone_pid", "unshare_")) else -1,
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


@pytest.mark.parametrize(
    "case,changes",
    [
        ("vsock_socket_one_high_word", {"return": 7, "errno": 0}),
        ("x32_socket_killed", {"returned": True, "return": 7, "signal": 0}),
        ("clone3_enosys", {"return": -22, "errno": 22}),
        ("clone_user_extra_mount_denied", {"exit_status": 101}),
        ("native_unix_socketpair", {"return": 7}),
    ],
)
def test_claimed_pass_cannot_override_contradictory_raw_evidence(case, changes):
    receipt = raw_receipt()
    assert policy.require_raw_probe(receipt) is True
    changed = copy.deepcopy(receipt)
    changed["observations"][case].update(changes)
    with pytest.raises(ValueError):
        policy.require_raw_probe(changed)


def test_same_runc_version_different_build_is_not_compiler_provenance(monkeypatch):
    image_id = "sha256:" + "a" * 64
    monkeypatch.setattr(policy, "selected_policy", lambda: object())
    records = iter(
        [
            {
                "Server": {
                    "Version": "28.0.4",
                    "Os": "linux",
                    "Arch": "amd64",
                    "KernelVersion": "6.17.0-1022-azure",
                    "Components": [
                        {"Name": "runc", "Version": "1.2.5", "Details": {"GitCommit": "a" * 40}},
                        {"Name": "containerd", "Version": "1.7.25"},
                    ],
                }
            },
            {
                "OSType": "linux",
                "Architecture": "x86_64",
                "DefaultRuntime": "runc",
                "DockerRootDir": "/var/lib/docker",
                "SecurityOptions": ["name=apparmor", "name=seccomp,profile=builtin"],
                "Runtimes": {"runc": {"path": "runc", "runtimeArgs": []}},
            },
            [
                {
                    "Id": image_id,
                    "Os": "linux",
                    "Architecture": "amd64",
                    "Config": {"User": "1000:1000"},
                }
            ],
        ]
    )
    monkeypatch.setattr(policy, "_read_json", lambda args: next(records))
    monkeypatch.setattr(policy.platform, "system", lambda: "Linux")
    monkeypatch.setattr(policy.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        policy.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(
            returncode=0,
            stdout=(
                "runc version 1.2.5\ncommit: " + "b" * 40 + "\nspec: 1.2.0\nlibseccomp: 2.5.5\n"
            ).encode(),
        ),
    )
    with pytest.raises(ValueError):
        policy.runtime_identity(image_id)
````
