# tests/test_business_receipt.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.generator`、`workbench.settings`、`workbench.verification`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `receipt`（L14–L27）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L25断言`report.pop("unit_test_fixture_only") is True`。 调用`Plan.model_validate_json( (ROOT / "examples/plans/customer-servic…`、`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`json.loads`、`(ROOT / "tests/fixtures/customer_evidence_receipt_unit_only.json"…`、`report.pop`。 返回路径：L27的`spec, report`。
- `test_complete_business_receipt_and_api_only`（L30–L33）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`receipt`、`require_business_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_wrong_business_evidence_blocks`（L51–L56）：接收`section`、`key`、`value`。 调用`receipt`、`deepcopy`、`pytest.raises`、`require_business_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_receipt.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L56。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1846`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_receipt.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d1bed8321adac00a4cac069eea129b2080c3324d573e3bcbd7fd3e00622abeda"} -->
````python
# tests/test_business_receipt.py
"""Business packaging cannot reuse classic CRUD or mismatched browser evidence."""

import json
from copy import deepcopy

import pytest

from workbench.domain import Plan
from workbench.generator import PrerequisiteError
from workbench.settings import ROOT
from workbench.verification import require_business_evidence


def receipt():
    # This fixture only exercises receipt validation; live generated HTTP/browser
    # tests separately execute the complete workflow and reject injected faults.
    spec = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    ).model_dump()
    report = json.loads(
        (ROOT / "tests/fixtures/customer_evidence_receipt_unit_only.json").read_text(
            encoding="utf-8"
        )
    )
    assert report.pop("unit_test_fixture_only") is True
    report.pop("source")
    return spec, report


def test_complete_business_receipt_and_api_only():
    spec, report = receipt()
    require_business_evidence(spec, report, True)
    require_business_evidence(spec, {"business": report["business"]}, False)


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("business", "passed", 1),
        ("business", "spec_digest", "old"),
        ("business", "resources_checked", []),
        ("business", "roles_checked", []),
        ("business", "checks", []),
        ("browser", "real_browser", 1),
        ("browser", "spec_digest", "old"),
        ("browser", "entities", []),
        ("browser", "errors", ["page error"]),
        ("browser", "checks", []),
    ],
)
def test_missing_or_wrong_business_evidence_blocks(section, key, value):
    spec, report = receipt()
    report = deepcopy(report)
    report[section][key] = value
    with pytest.raises(PrerequisiteError):
        require_business_evidence(spec, report, True)
````
