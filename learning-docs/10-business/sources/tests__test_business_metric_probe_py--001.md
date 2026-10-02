# tests/test_business_metric_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.business_probe`、`workbench.domain`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture`（L10–L66）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate_json`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Client`。 返回路径：L66的`Client(), plan, values`。
- `fixture.Client`（L56–L64）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `fixture.Client.rows`（L60–L61）：接收`entity`、`**kwargs`。 返回路径：L61的`rows[entity]`。
- `fixture.Client.call`（L63–L64）：接收`*args`、`**kwargs`。 调用`values.items`。 返回路径：L64的`[{"name": name, "value": value} for name, value in values.items()]`。
- `test_independent_metric_values_use_authorized_http_rows`（L69–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L71断言`len(verify_scoped_metrics(client, plan)) == len(plan.business.metrics) == 7`。 调用`fixture`、`len`、`verify_scoped_metrics`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_broken_metric_values_do_not_count_as_functional_acceptance`（L87–L91）：接收`name`、`value`。 调用`fixture`、`deepcopy`、`pytest.raises`、`verify_scoped_metrics`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_service_cannot_silently_lose_its_approved_metrics`（L94–L98）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`fixture`、`values.pop`、`pytest.raises`、`verify_scoped_metrics`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_oracle_accepts_provider_names_and_yudao_wire_format`（L101–L114）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L103遍历`enumerate(plan.business.metrics)`；L114断言`len(verify_scoped_metrics(client, plan)) == len(values)`。 调用`fixture`、`enumerate`、`values.pop`、`wire_name`、`row.items`、`original_rows`、`len`、`verify_scoped_metrics`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_metric_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L114。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3888`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_metric_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6b0bbac106272e58b67e38cc36d93b7b28917ae74bbbef86a6766b54156eda94"} -->
````python
# tests/test_business_metric_probe.py
from copy import deepcopy

import pytest

from workbench.business_probe import verify_scoped_metrics
from workbench.domain import Plan
from workbench.settings import ROOT


def fixture():
    plan = Plan.model_validate_json(
        (ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8")
    )
    rows = {
        "customers": [
            {"id": "1", "category": "企业"},
            {"id": "2", "category": "企业"},
            {"id": "3", "category": "个人"},
        ],
        "requests": [
            {
                "id": "4",
                "customer_id": "1",
                "request_state": "resolved",
                "created_at": "2026-01-01T00:00:00Z",
                "resolved_at": "2026-01-01T00:01:00Z",
            },
            {
                "id": "5",
                "customer_id": "1",
                "request_state": "resolved",
                "created_at": "2026-01-02T00:00:00Z",
                "resolved_at": "2026-01-02T00:03:00Z",
            },
            {
                "id": "6",
                "customer_id": "3",
                "request_state": "new",
                "created_at": "2026-01-02T00:00:00Z",
                "resolved_at": None,
            },
        ],
    }
    values = {
        "total": {"value": 3},
        "resolved_total": {"value": 2},
        "resolution": {"value": 120, "samples": 2},
        "by_customer": {"groups": [{"key": "1", "count": 2}, {"key": "3", "count": 1}]},
        "daily": {"groups": [{"day": "2026-01-01", "count": 1}, {"day": "2026-01-02", "count": 2}]},
        "customer_total": {"value": 3},
        "customer_categories": {
            "groups": [{"key": "企业", "count": 2}, {"key": "个人", "count": 1}]
        },
    }

    class Client:
        template = "fastapiadmin"
        prefix = "/business"

        def rows(self, entity, **kwargs):
            return rows[entity]

        def call(self, *args, **kwargs):
            return [{"name": name, "value": value} for name, value in values.items()]

    return Client(), plan, values


def test_independent_metric_values_use_authorized_http_rows():
    client, plan, _ = fixture()
    assert len(verify_scoped_metrics(client, plan)) == len(plan.business.metrics) == 7


@pytest.mark.parametrize(
    "name,value",
    [
        ("total", {"value": True}),
        ("total", {"value": 2}),
        ("resolved_total", {"value": 3}),
        ("resolution", {"value": 60, "samples": 2}),
        ("resolution", {"value": 120, "samples": 3}),
        ("by_customer", {"groups": [{"key": "other", "count": 3}]}),
        ("customer_categories", {"groups": [{"key": "企业", "count": 3}]}),
        ("daily", {"groups": [{"day": "2026-01-02", "count": 3}]}),
    ],
)
def test_broken_metric_values_do_not_count_as_functional_acceptance(name, value):
    client, plan, values = fixture()
    values[name] = deepcopy(value)
    with pytest.raises(AssertionError):
        verify_scoped_metrics(client, plan)


def test_service_cannot_silently_lose_its_approved_metrics():
    client, plan, values = fixture()
    values.pop("resolution")
    with pytest.raises(AssertionError, match="Metric set"):
        verify_scoped_metrics(client, plan, "service")


def test_metric_oracle_accepts_provider_names_and_yudao_wire_format():
    client, plan, values = fixture()
    for number, metric in enumerate(plan.business.metrics):
        values[f"provider_metric_{number}"] = values.pop(metric.name)
        metric.name = f"provider_metric_{number}"
    original_rows = client.rows
    from workbench.business_probe import wire_name

    client.template = "yudao-vben"
    client.rows = lambda entity, **kwargs: [
        {wire_name(client.template, key): value for key, value in row.items()}
        for row in original_rows(entity)
    ]
    assert len(verify_scoped_metrics(client, plan)) == len(values)
````
