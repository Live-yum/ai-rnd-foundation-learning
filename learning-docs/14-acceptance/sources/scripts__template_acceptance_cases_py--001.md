# scripts/template_acceptance_cases.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机维护、构建或集成验收入口。** main或模块入口按顺序调用本文件函数；它不是HTTP接口。ci_脚本连接真实本机工具或进程并保存证据，build/rebuild脚本负责教材一致性，daytona脚本只安装和控制本机开发服务。

**对应关系：** 终端python -m scripts.template_acceptance_cases；完整命令及成功条件见正文对应章节。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `AcceptanceFailure`（L14–L19）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `AcceptanceFailure.__init__`（L17–L19）：接收`code`、`path`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require`（L22–L24）：接收`condition`、`code`、`path`。 控制顺序：L23按`not condition`分支；L24抛异常，停止当前正常路径。 调用`AcceptanceFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ProjectCase`（L28–L39）：继承`object`。声明的数据项为`identity`、`size`、`title`、`requirement`、`contract`、`actors`、`fixtures`、`expected_checks`、`scenario`、`browser`、`source_digest`；类型约束/数据库列参数以完整定义为准。
- `load_case`（L42–L73）：接收`identity`、`root`。 调用`require`、`Path`、`json.loads`、`(folder / "contract.json").read_text`、`(folder / "requirement.md").read_text`、`len`、`set`、`any`、`block.get`等。 返回路径：L61的`ProjectCase( identity=identity, size=document["size"], title=document["title"], requiremen…`。
- `same_obligation`（L76–L95）：接收`actual`、`expected`。 源码说明：Compare declared values without prescribing model-authored display labels/order.。 控制顺序：L78按`isinstance(expected, dict)`分支；L82按`isinstance(expected, list)`分支；L83按`not isinstance(actual, list) or len(actual) != len(expected)`分支；L86遍历`expected`；L91按`found is None`分支。 调用`isinstance`、`all`、`same_obligation`、`expected.items`、`len`、`list`、`next`、`enumerate`、`remaining.pop`等。 返回路径：L79的`isinstance(actual, dict) and all( key in actual and same_obligation(actual[key], value) fo…`；L84的`False`；L92的`False`。
- `require_contract`（L98–L134）：接收`case`、`value`。 源码说明：Check the delivered model contract against source-authored obligations.。 控制顺序：L107遍历`expected["entities"].items()`；L110遍历`fields.items()`；L124按`"business" not in expected`分支；L128遍历`expected["business"].items()`。 调用`Plan.model_validate`、`plan.model_dump`、`require`、`set`、`expected["entities"].items`、`fields.items`、`same_obligation`、`expected["business"].items`、`actual["business"].get`。 返回路径：L134的`plan`。
- `require_scenario_checks`（L137–L141）：接收`case`、`checks`。 调用`require`、`len`、`set`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `suite_cases`（L144–L151）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`load_case`、`require`、`len`。 返回路径：L151的`cases`。

</details>

**创建路径：** `scripts/template_acceptance_cases.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L151。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5555`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/template_acceptance_cases.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "98990eb88c56812228896bec4d81d6ceb779a071205b650cea354ecb2d061a01"} -->
````python
# scripts/template_acceptance_cases.py
"""Independent project obligations; never a replacement for a model-generated Plan."""

import json
from dataclasses import dataclass
from pathlib import Path

from workbench.domain import Plan, digest
from workbench.settings import ROOT

CASE_IDS = ("reading-shelf", "stock-purchasing", "facilities-ops")
CASE_ROOT = ROOT / "examples/acceptance"


class AcceptanceFailure(RuntimeError):
    """Static controller codes, with an optional local obligation path."""

    def __init__(self, code, path=""):
        self.code, self.path = code, path
        super().__init__(code + (":" + path if path else ""))


def require(condition, code, path=""):
    if not condition:
        raise AcceptanceFailure(code, path)


@dataclass(frozen=True)
class ProjectCase:
    identity: str
    size: str
    title: str
    requirement: str
    contract: dict
    actors: dict
    fixtures: dict
    expected_checks: tuple[str, ...]
    scenario: tuple[dict, ...]
    browser: tuple[dict, ...]
    source_digest: str


def load_case(identity, root=CASE_ROOT):
    require(identity in CASE_IDS, "unknown_case")
    folder = Path(root) / identity
    document = json.loads((folder / "contract.json").read_text(encoding="utf-8"))
    requirement = (folder / "requirement.md").read_text(encoding="utf-8")
    require(document["id"] == identity, "case_identity")
    require(0 < len(requirement) <= 20000, "requirement_length")
    require(document["size"] in {"small", "medium", "large"}, "case_size")
    require(document["expected_checks"], "missing_scenario_checks")
    require(
        len(set(document["expected_checks"])) == len(document["expected_checks"]),
        "duplicate_scenario_check",
    )
    require(
        [block["id"] for block in document["scenario"]] == document["expected_checks"],
        "scenario_contract_mismatch",
    )
    require(any(block.get("restart") for block in document["scenario"]), "missing_restart")
    require(bool(document["browser"]), "missing_browser_scenario")
    return ProjectCase(
        identity=identity,
        size=document["size"],
        title=document["title"],
        requirement=requirement,
        contract=document["contract"],
        actors=document["actors"],
        fixtures=document["fixtures"],
        expected_checks=tuple(document["expected_checks"]),
        scenario=tuple(document["scenario"]),
        browser=tuple(document["browser"]),
        source_digest=digest({"requirement": requirement, "contract": document}),
    )


def same_obligation(actual, expected):
    """Compare declared values without prescribing model-authored display labels/order."""
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and same_obligation(actual[key], value) for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        remaining = list(actual)
        for value in expected:
            found = next(
                (i for i, candidate in enumerate(remaining) if same_obligation(candidate, value)),
                None,
            )
            if found is None:
                return False
            remaining.pop(found)
        return True
    return type(actual) is type(expected) and actual == expected


def require_contract(case, value):
    """Check the delivered model contract against source-authored obligations."""
    plan = Plan.model_validate(value)
    actual = plan.model_dump(mode="json")
    expected = case.contract
    require(not plan.unsupported and not plan.custom_rules, "unexpected_implementation_scope")
    require(plan.data_scope == expected["data_scope"], "contract_mismatch", "data_scope")
    entities = {entity["name"]: entity for entity in actual["entities"]}
    require(set(entities) == set(expected["entities"]), "contract_mismatch", "entities")
    for name, fields in expected["entities"].items():
        found = {field["name"]: field for field in entities[name]["fields"]}
        require(set(found) == set(fields), "contract_mismatch", name + ".fields")
        for field, obligation in fields.items():
            require(
                same_obligation(
                    found[field],
                    {
                        "searchable": False,
                        "filterable": False,
                        "date_range": False,
                        **obligation,
                    },
                ),
                "contract_mismatch",
                name + "." + field,
            )
    if "business" not in expected:
        require(plan.business is None, "contract_mismatch", "business")
    else:
        require(plan.business is not None, "contract_mismatch", "business")
        for key, obligation in expected["business"].items():
            require(
                same_obligation(actual["business"].get(key), obligation),
                "contract_mismatch",
                "business." + key,
            )
    return plan


def require_scenario_checks(case, checks):
    require(
        len(checks) == len(set(checks)) and set(checks) == set(case.expected_checks),
        "incomplete_scenario_evidence",
    )


def suite_cases():
    cases = [load_case(identity) for identity in CASE_IDS]
    require([case.size for case in cases] == ["small", "medium", "large"], "suite_sizes")
    require(
        [len(case.contract["entities"]) for case in cases] == [1, 3, 6],
        "suite_entity_counts",
    )
    return cases
````
