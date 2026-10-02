# tests/test_business_capabilities.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_capabilities`、`workbench.catalog`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `customer`（L9–L17）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`(ROOT / "examples/requirements/customer-service.md").read_text`、`Requirement`。 返回路径：L11的`Requirement( summary=prose, users=["管理人员", "服务人员", "普通员工"], data_scope="shared", features=…`。
- `test_customer_contract_satisfies_recognized_required_business_behaviors`（L20–L24）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L24断言`business_gaps(customer(), plan) == []`。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`business_gaps`、`customer`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_requested_metric_cannot_be_replaced_by_crud_or_other_aggregate`（L28–L33）：接收`kind`。 控制顺序：L33断言`business_gaps(customer(), Plan.model_validate(raw))`。 调用`__import__("json").loads`、`__import__`、`(ROOT / "examples/plans/customer-service.json").read_text`、`business_gaps`、`customer`、`Plan.model_validate`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_plain_crud_does_not_satisfy_customer_case`（L36–L41）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L41断言`business_gaps(customer(), Plan.model_validate(raw))`。 调用`__import__("json").loads`、`__import__`、`(ROOT / "examples/plans/customer-service.json").read_text`、`raw.pop`、`business_gaps`、`customer`、`Plan.model_validate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_catalog_separates_default_crud_from_declarative_business_mode`（L44–L49）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L45遍历`["python-basic", "fastapiadmin", "yudao-vben"]`；L47断言`"shared" in capabilities["scopes"]`；L48断言`capabilities["business_contract"]["scope"] == "shared"`；L49断言`"datetime" in capabilities["business_contract"]["field_kinds"]`。 调用`Selection(template=template).capabilities`、`Selection`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_capabilities.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L49。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1941`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_capabilities.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "54d80b3db9afea6d35e98044cb126658058cbd193f94d7aedfef7379a5fc2fc5"} -->
````python
# tests/test_business_capabilities.py
import pytest

from workbench.business_capabilities import business_gaps
from workbench.catalog import Selection
from workbench.domain import Plan, Requirement
from workbench.settings import ROOT


def customer():
    prose = (ROOT / "examples/requirements/customer-service.md").read_text(encoding="utf-8")
    return Requirement(
        summary=prose,
        users=["管理人员", "服务人员", "普通员工"],
        data_scope="shared",
        features=["内部客户服务管理"],
        acceptance=["完整实现原始需求"],
    )


def test_customer_contract_satisfies_recognized_required_business_behaviors():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    assert business_gaps(customer(), plan) == []


@pytest.mark.parametrize("kind", ["count", "average_duration", "group_count", "time_count"])
def test_requested_metric_cannot_be_replaced_by_crud_or_other_aggregate(kind):
    raw = __import__("json").loads(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    raw["business"]["metrics"] = [m for m in raw["business"]["metrics"] if m["kind"] != kind]
    assert business_gaps(customer(), Plan.model_validate(raw))


def test_plain_crud_does_not_satisfy_customer_case():
    raw = __import__("json").loads(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    raw.pop("business")
    assert business_gaps(customer(), Plan.model_validate(raw))


def test_catalog_separates_default_crud_from_declarative_business_mode():
    for template in ["python-basic", "fastapiadmin", "yudao-vben"]:
        capabilities = Selection(template=template).capabilities()
        assert "shared" in capabilities["scopes"]
        assert capabilities["business_contract"]["scope"] == "shared"
        assert "datetime" in capabilities["business_contract"]["field_kinds"]
````
