# tests/test_capability_native_egress.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `setup`（L13–L51）：接收`monkeypatch`、`label`、`denied`。 调用`monkeypatch.setattr`、`json.dumps`。 返回路径：L51的`commands`。
- `setup.docker`（L24–L48）：接收`*args`、`**kwargs`。 控制顺序：L26按`"curl" in args`分支；L29按`tail[0] == "run"`分支；L32按`tail[:2] == ("container", "inspect")`分支；L46按`tail[0] == "rm"`分支；L48抛异常，停止当前正常路径。 调用`commands.append`、`tail.index`、`json.dumps`、`AssertionError`。 返回路径：L27的`"rnd-owned-egress-peer"`；L31的`"b" * 64`；L33的`json.dumps( [ { "Id": "b" * 64, "Name": "/" + name[0], "Config": {"Labels": {"rnd-owned-sa…`。
- `execute`（L54–L63）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`probe.verify_native_egress`、`SimpleNamespace`、`Selection`。 返回路径：L55的`probe.verify_native_egress( None, {"snapshot": {"image_id": "sha256:" + "c" * 64}}, Simple…`。
- `test_peer_is_bounded_unpublished_and_removed_after_positive_controls`（L66–L82）：接收`monkeypatch`。 控制顺序：L68断言`execute() == {"native_egress_denied_same_ports": True}`；L70遍历`( "--read-only", "--cap-drop", "--security-opt", "--memory", "--m…`；L79断言`flag in launch`；L80断言`"--publish" not in launch and "-p" not in launch and "--privileged" not in launch`；L81断言`sum("curl" in c for c in commands) == 6`；L82断言`commands[-1][-3:] == ("rm", "--force", "b" * 64)`。 调用`setup`、`execute`、`next`、`sum`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_denial_still_removes_only_owned_peer`（L85–L89）：接收`monkeypatch`。 控制顺序：L89断言`commands[-1][-3:] == ("rm", "--force", "b" * 64)`。 调用`setup`、`pytest.raises`、`execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_identity_mismatch_never_removes_another_container`（L92–L96）：接收`monkeypatch`。 控制顺序：L96断言`not any("rm" in c for c in commands)`。 调用`setup`、`pytest.raises`、`execute`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_egress.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L96。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3171`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_egress.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cf8e5848ec556e9c47c328c0c8bdf6b4ed6283292887f290fd73f559557e439d"} -->
````python
# tests/test_capability_native_egress.py
"""Peer lifecycle contract tests; these mocks do not certify actual egress."""

import json
from types import SimpleNamespace

import pytest

from scripts import capability_native_egress as probe
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection


def setup(monkeypatch, *, label="owned", denied=True):
    commands = []
    name = [""]
    monkeypatch.setattr(probe, "compose", lambda *a: "a" * 64)
    monkeypatch.setattr(probe, "product_argv", lambda plan, argv, env: argv)
    monkeypatch.setattr(
        probe,
        "run_guarded_control",
        lambda *a: (0 if denied else 1, json.dumps({"native_egress_denied_same_ports": denied})),
    )

    def docker(*args, **kwargs):
        commands.append(args)
        if "curl" in args:
            return "rnd-owned-egress-peer"
        tail = args[5:]
        if tail[0] == "run":
            name[0] = tail[tail.index("--name") + 1]
            return "b" * 64
        if tail[:2] == ("container", "inspect"):
            return json.dumps(
                [
                    {
                        "Id": "b" * 64,
                        "Name": "/" + name[0],
                        "Config": {"Labels": {"rnd-owned-sandbox": label}},
                        "Image": "sha256:" + "c" * 64,
                        "NetworkSettings": {
                            "Networks": {"runner-bridge": {"IPAddress": "172.20.0.42"}}
                        },
                    }
                ]
            )
        if tail[0] == "rm":
            return "b" * 64
        raise AssertionError(args)

    monkeypatch.setattr(probe.local, "docker", docker)
    return commands


def execute():
    return probe.verify_native_egress(
        None,
        {"snapshot": {"image_id": "sha256:" + "c" * 64}},
        SimpleNamespace(id="owned"),
        SimpleNamespace(
            selection=Selection(template="fastapiadmin"), runtime=SimpleNamespace(port=8000)
        ),
        30,
    )


def test_peer_is_bounded_unpublished_and_removed_after_positive_controls(monkeypatch):
    commands = setup(monkeypatch)
    assert execute() == {"native_egress_denied_same_ports": True}
    launch = next(c for c in commands if "run" in c)
    for flag in (
        "--read-only",
        "--cap-drop",
        "--security-opt",
        "--memory",
        "--memory-swap",
        "--cpus",
        "--pids-limit",
    ):
        assert flag in launch
    assert "--publish" not in launch and "-p" not in launch and "--privileged" not in launch
    assert sum("curl" in c for c in commands) == 6
    assert commands[-1][-3:] == ("rm", "--force", "b" * 64)


def test_failed_denial_still_removes_only_owned_peer(monkeypatch):
    commands = setup(monkeypatch, denied=False)
    with pytest.raises(CheckFailure, match="同端口"):
        execute()
    assert commands[-1][-3:] == ("rm", "--force", "b" * 64)


def test_identity_mismatch_never_removes_another_container(monkeypatch):
    commands = setup(monkeypatch, label="someone-else")
    with pytest.raises(CheckFailure, match="清理未确认"):
        execute()
    assert not any("rm" in c for c in commands)
````
