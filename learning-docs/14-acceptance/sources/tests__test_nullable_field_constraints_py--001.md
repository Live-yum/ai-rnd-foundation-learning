# tests/test_nullable_field_constraints.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_nullable_and_nonnullable_field_prose_stays_strict`（L13–L52）：接收`phrase`、`required`。 控制顺序：L38断言`coverage_gaps(requirement, plan) == []`；L40断言`[ (item["entity"], item["field"], item["expected"]) for item in source_constraints if…`；L47断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L49断言`len(mismatches) == 1`；L50断言`mismatches[0]["targets"] == [{"entity": "documents", "field": "comment"}]`；L51断言`mismatches[0]["expected"] is required`；L52断言`mismatches[0]["actual"] is not required`。 调用`Requirement`、`FieldRequirement`、`Plan`、`coverage_gaps`、`explicit_legacy_field_constraints`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_nullable_field_constraints.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L52。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2095`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_nullable_field_constraints.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "028d07b7c16bd1b42ff5c868e5dec52b954b6b624afca9bb8920ceea56d49d4b"} -->
````python
# tests/test_nullable_field_constraints.py
"""Nullable prose preserves required flags without reversing non-null prohibitions."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps, explicit_legacy_field_constraints


@pytest.mark.parametrize(
    "phrase,required",
    [("可空", False), ("不可空", True), ("不得为空", True), ("可选", False), ("必填", True)],
)
def test_nullable_and_nonnullable_field_prose_stays_strict(phrase, required):
    text = f"documents 的 comment {phrase}；最大长度600"
    requirement = Requirement(
        summary="文档备注",
        users=["reader"],
        data_scope="per_user",
        features=[text],
        acceptance=[],
        field_requirements=[FieldRequirement(entity="documents", field="comment", kind="text")],
    )
    plan = Plan(
        title="文档备注",
        data_scope="per_user",
        acceptance=["Offline source constraint check"],
        entities=[
            {
                "name": "documents",
                "description": "文档",
                "fields": [
                    {"name": "comment", "kind": "text", "required": required, "max_length": 600},
                    {"name": "headline", "kind": "text", "required": True},
                ],
            }
        ],
    )
    assert coverage_gaps(requirement, plan) == []
    source_constraints = explicit_legacy_field_constraints(requirement)
    assert [
        (item["entity"], item["field"], item["expected"])
        for item in source_constraints
        if item["attribute"] == "required"
    ] == [("documents", "comment", required)]
    plan.entities[0].fields[0].required = not required
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    mismatches = [item for item in diagnostics if item["attribute"] == "required"]
    assert len(mismatches) == 1
    assert mismatches[0]["targets"] == [{"entity": "documents", "field": "comment"}]
    assert mismatches[0]["expected"] is required
    assert mismatches[0]["actual"] is not required
````
