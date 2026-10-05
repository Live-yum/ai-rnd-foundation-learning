# tests/test_container_diagnostic_review.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_instance_shadowed_allowlists_cannot_release_strings`（L16–L28）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L21断言`result == { "container_rejection": "resource_limits", "network_mode": "other", "memor…`；L28断言`ContainerInspectionRejected.diagnostic(error) == {}`。 调用`ContainerInspectionRejected`、`ContainerInspectionRejected.diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_mutated_malformed_facts_preserve_only_finite_category`（L32–L37）：接收`facts`。 控制顺序：L35断言`ContainerInspectionRejected.diagnostic(error) == { "container_rejection": "resource_l…`。 调用`ContainerInspectionRejected`、`ContainerInspectionRejected.diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_all_diagnostic_fields_are_bounded_and_type_strict`（L40–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52断言`len(json.dumps(result)) < 1500`；L53断言`"secret" not in json.dumps(result)`；L54遍历`ContainerInspectionRejected._NUMBERS`；L55遍历`[True, 1.0, 2**63, -(2**63) - 1, "secret"]`；L57断言`error.diagnostic()[name] is None`。 调用`ContainerInspectionRejected`、`dict.fromkeys`、`error.diagnostic`、`len`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_rejected_facts_do_not_replace_trusted_category`（L61–L72）：接收`request`、`case`。 控制顺序：L63按`case == "binary_mounts"`分支；L71断言`diagnostic["container_rejection"] == case`；L72断言`"secret" not in json.dumps(diagnostic)`。 调用`request.getfixturevalue`、`pytest.raises`、`profile.inspect_created_sandbox`、`caught.value.diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_container_diagnostic_review.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L72。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2903`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_container_diagnostic_review.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "c20cbc5b319faaecc4e8dd2074be18a9522898dfea1b228418c929baf38ef90b"} -->
````python
# tests/test_container_diagnostic_review.py
"""Independent bounded-diagnostic regressions; no container execution."""

import json

import pytest

from scripts import daytona_capability_profile as profile
from tests.test_daytona_capability_profile import (  # noqa: F401
    SANDBOX,
    execution_inspection,
    inspection,
)
from workbench.capability_isolation import ContainerInspectionRejected


def test_instance_shadowed_allowlists_cannot_release_strings():
    error = ContainerInspectionRejected("secret message", category="resource_limits")
    error._NETWORK_MODES = {"secret network"}
    error._facts = {"network_mode": "secret network", "memory": "secret memory"}
    result = ContainerInspectionRejected.diagnostic(error)
    assert result == {
        "container_rejection": "resource_limits",
        "network_mode": "other",
        "memory": None,
    }
    error._CATEGORIES = {"secret category"}
    error._category = "secret category"
    assert ContainerInspectionRejected.diagnostic(error) == {}


@pytest.mark.parametrize("facts", [None, [], "memory secret", 123, True])
def test_mutated_malformed_facts_preserve_only_finite_category(facts):
    error = ContainerInspectionRejected("secret message", category="resource_limits")
    error._facts = facts
    assert ContainerInspectionRejected.diagnostic(error) == {
        "container_rejection": "resource_limits"
    }


def test_all_diagnostic_fields_are_bounded_and_type_strict():
    error = ContainerInspectionRejected(
        "secret message",
        category="resource_limits",
        facts={
            **dict.fromkeys(ContainerInspectionRejected._NUMBERS, -(2**63)),
            **dict.fromkeys(ContainerInspectionRejected._FLAGS, False),
            "network_mode": "host",
            "unknown": "secret",
        },
    )
    result = error.diagnostic()
    assert len(json.dumps(result)) < 1500
    assert "secret" not in json.dumps(result)
    for name in ContainerInspectionRejected._NUMBERS:
        for value in [True, 1.0, 2**63, -(2**63) - 1, "secret"]:
            error._facts[name] = value
            assert error.diagnostic()[name] is None


@pytest.mark.parametrize("case", ["binary_mounts", "runner_bridge"])
def test_malformed_rejected_facts_do_not_replace_trusted_category(request, case):
    directory, _, inner, _ = request.getfixturevalue("execution_inspection")
    if case == "binary_mounts":
        inner["Mounts"] = [{"Type": "bind", "Destination": [], "Source": "secret", "RW": False}]
    else:
        inner["bridge_inspect"][0]["Driver"] = "unexpected"
        inner["bridge_inspect"][0]["IPAM"] = {"Config": [{"Subnet": ["secret"]}]}
    with pytest.raises(ContainerInspectionRejected) as caught:
        profile.inspect_created_sandbox(directory, SANDBOX, require_resources=True)
    diagnostic = caught.value.diagnostic()
    assert diagnostic["container_rejection"] == case
    assert "secret" not in json.dumps(diagnostic)
````
