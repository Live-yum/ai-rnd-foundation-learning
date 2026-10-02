# tests/test_business_native_schema.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.native_modules`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_business_native_schema_has_real_foreign_keys`（L14–L32）：接收`template`。 控制顺序：L20断言`isinstance(request.c.customer_id.type, Integer)`；L21断言`isinstance(request.c.resolved_at.type, DateTime)`；L22断言`next(iter(request.c.customer_id.foreign_keys)).target_fullname == names["customers"] …`；L26断言`next(iter(request.c.assignee_id.foreign_keys)).target_fullname == user + ".id"`；L28断言`ordered.index(names["customers"]) < ordered.index(names["requests"])`；L30断言`"ON DELETE RESTRICT" in ddl`；L31按`template == "yudao-vben"`分支；L32断言`isinstance(request.c.customer_id.type, BigInteger)`。 调用`Plan.model_validate`、`business_plan`、`native_metadata`、`next`、`isinstance`、`iter`、`ordered.index`、`str`、`CreateTable(request).compile`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fastapi_business_indexes_match_original_mixins`（L35–L59）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L42遍历`tables`；L46断言`indexes[("uuid",)] is True`；L47断言`{ ("id",), ("is_deleted",), ("created_time",), ("created_id",), ("updated_id",), ("de…`；L55断言`not any( getattr(constraint, "__visit_name__", "") == "unique_constraint" and [c.name…`。 调用`native_metadata`、`Plan.model_validate`、`business_plan`、`tuple`、`indexes.keys`、`any`、`getattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_business_native_schema.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L59。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2427`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_business_native_schema.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "79b29118f6bbb6064c486eed40d8c00063b6afe91f4477f8d783a82c140fb36d"} -->
````python
# tests/test_business_native_schema.py
"""Business references retain real native physical identity types and ordered DDL."""

import pytest
from sqlalchemy import BigInteger, DateTime, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from test_business_contracts import business_plan

from workbench.domain import Plan
from workbench.native_modules import native_metadata


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_business_native_schema_has_real_foreign_keys(template):
    plan = Plan.model_validate(business_plan())
    metadata, tables, names = native_metadata(
        template, plan, "postgresql+psycopg://native:lab@127.0.0.1/native_codegen", "business"
    )
    request = next(t for t in tables if t.name == names["requests"])
    assert isinstance(request.c.customer_id.type, Integer)
    assert isinstance(request.c.resolved_at.type, DateTime)
    assert (
        next(iter(request.c.customer_id.foreign_keys)).target_fullname == names["customers"] + ".id"
    )
    user = "sys_user" if template == "fastapiadmin" else "system_users"
    assert next(iter(request.c.assignee_id.foreign_keys)).target_fullname == user + ".id"
    ordered = [t.name for t in metadata.sorted_tables]
    assert ordered.index(names["customers"]) < ordered.index(names["requests"])
    ddl = str(CreateTable(request).compile(dialect=postgresql.dialect()))
    assert "ON DELETE RESTRICT" in ddl
    if template == "yudao-vben":
        assert isinstance(request.c.customer_id.type, BigInteger)


def test_fastapi_business_indexes_match_original_mixins():
    metadata, tables, _ = native_metadata(
        "fastapiadmin",
        Plan.model_validate(business_plan()),
        "postgresql+psycopg://native:lab@127.0.0.1/native_codegen",
        "indexed",
    )
    for table in tables:
        indexes = {
            tuple(column.name for column in index.columns): index.unique for index in table.indexes
        }
        assert indexes[("uuid",)] is True
        assert {
            ("id",),
            ("is_deleted",),
            ("created_time",),
            ("created_id",),
            ("updated_id",),
            ("deleted_id",),
        } <= indexes.keys()
        assert not any(
            getattr(constraint, "__visit_name__", "") == "unique_constraint"
            and [c.name for c in constraint.columns] == ["uuid"]
            for constraint in table.constraints
        )
````
