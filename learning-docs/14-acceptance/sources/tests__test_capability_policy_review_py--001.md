# tests/test_capability_policy_review.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`scripts.extension_oracles`、`workbench.capability_contracts`、`workbench.capability_policy`、`workbench.catalog`、`workbench.domain`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `policy_for`（L15–L26）：接收`text`。 控制顺序：L24断言`scope == original`；L25断言`policy["source_units_digest"] == digest(scope["sources"])`。 调用`digest`、`scope_sources`、`deepcopy`、`scope_policy`、`Selection(template="fastapiadmin").model_dump`、`Selection`。 返回路径：L26的`policy`。
- `test_formatting_cannot_downgrade_registered_business_oracle`（L30–L40）：接收`style`。 控制顺序：L32按`style == "bullets"`分支；L34按`style == "numbered"`分支；L36按`style == "wrapped"`分支；L40断言`policy_for("\n".join(lines))["trusted_oracle"] == contest.CONTRACT_VERSION`。 调用`list`、`enumerate`、`line.replace("。", ";").replace`、`line.replace`、`policy_for`、`"\n".join`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `make_contract`（L43–L50）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`make_plan( { "source_units": scope_sources([GOAL]), "source_diges…`、`make_plan`、`scope_sources`、`digest`、`Selection().model_dump`、`Selection`。 返回路径：L44的`make_plan( { "source_units": scope_sources([GOAL]), "source_digest": digest([GOAL]), "sele…`。
- `test_empty_or_status_envelope_is_not_business_acceptance`（L54–L62）：接收`positive`。 控制顺序：L56遍历`raw["scenarios"]`；L62断言`contract_errors(CapabilityPlan.model_validate(raw))`。 调用`make_contract`、`contract_errors`、`CapabilityPlan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_read_after_restart_cannot_count_as_persistence`（L65–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L67遍历`raw["scenarios"]`；L71断言`any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))`。 调用`make_contract`、`any`、`contract_errors`、`CapabilityPlan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrelated_restart_resource_cannot_borrow_written_value`（L74–L80）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L76遍历`raw["scenarios"]`；L77遍历`scenario["after_restart"]`；L78按`step["status"] == 200`分支；L80断言`any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))`。 调用`make_contract`、`any`、`contract_errors`、`CapabilityPlan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_policy_review.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L80。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3104`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_policy_review.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3270e8319fe5d675349fd62682bbff46bf396a018424f168b66fbfac9cfc68cb"} -->
````python
# tests/test_capability_policy_review.py
"""Independent data-only regressions; these do not certify live execution."""

from copy import deepcopy

import pytest

from scripts.capability_fixture import GOAL, make_plan
from scripts.extension_oracles import contest
from workbench.capability_contracts import CapabilityPlan, scope_sources
from workbench.capability_policy import CONTEST_BINDINGS, contract_errors, scope_policy
from workbench.catalog import Selection
from workbench.domain import digest


def policy_for(text):
    messages = [text]
    scope = {
        "messages": messages,
        "source_digest": digest(messages),
        "sources": scope_sources(messages),
    }
    original = deepcopy(scope)
    policy = scope_policy(scope, Selection(template="fastapiadmin").model_dump())
    assert scope == original, "Policy matching must preserve exact original source evidence"
    assert policy["source_units_digest"] == digest(scope["sources"])
    return policy


@pytest.mark.parametrize("style", ["bullets", "numbered", "wrapped", "punctuation"])
def test_formatting_cannot_downgrade_registered_business_oracle(style):
    lines = list(CONTEST_BINDINGS)
    if style == "bullets":
        lines = ["- " + line for line in lines]
    elif style == "numbered":
        lines = [f"{index + 1}. {line}" for index, line in enumerate(lines)]
    elif style == "wrapped":
        lines = [line[:12] + "\n" + line[12:] for line in lines]
    else:
        lines = [line.replace("。", ";").replace("：", ":") for line in lines]
    assert policy_for("\n".join(lines))["trusted_oracle"] == contest.CONTRACT_VERSION


def make_contract():
    return make_plan(
        {
            "source_units": scope_sources([GOAL]),
            "source_digest": digest([GOAL]),
            "selection": Selection().model_dump(),
        }
    ).model_dump()


@pytest.mark.parametrize("positive", [{"absent": ["$.business"]}, {"equals": {"$.ok": True}}])
def test_empty_or_status_envelope_is_not_business_acceptance(positive):
    raw = make_contract()
    for scenario in raw["scenarios"]:
        scenario["steps"] = [
            {"method": "POST", "path": "/probe", "status": 200, **positive},
            {"path": "/nonexistent", "status": 404},
        ]
        scenario["after_restart"] = [{"path": "/probe", "status": 200, **positive}]
    assert contract_errors(CapabilityPlan.model_validate(raw))


def test_failed_read_after_restart_cannot_count_as_persistence():
    raw = make_contract()
    for scenario in raw["scenarios"]:
        scenario["after_restart"] = [
            {"path": "/entries/${entry}", "status": 404, "equals": {"$.detail": "not found"}}
        ]
    assert any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))


def test_unrelated_restart_resource_cannot_borrow_written_value():
    raw = make_contract()
    for scenario in raw["scenarios"]:
        for step in scenario["after_restart"]:
            if step["status"] == 200:
                step["path"] = "/unrelated-static"
    assert any("重启" in error for error in contract_errors(CapabilityPlan.model_validate(raw)))
````
