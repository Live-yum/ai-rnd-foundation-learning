# tests/test_native_optional_acceptance.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.native_acceptance`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_optional_only_entity_uses_type_constraint_without_inventing_required_field`（L5–L14）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L12断言`value == {"score": {"invalid_scalar": True}}`；L13断言`kind == "type"`；L14断言`entity.fields[0].required is False`。 调用`Entity`、`invalid_record`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_boolean_only_entity_is_supported_by_acceptance_sampler`（L17–L22）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L22断言`kind == "type" and value["approved"] == {"invalid_scalar": True}`。 调用`Entity`、`invalid_record`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_optional_acceptance.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L22。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`876`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_optional_acceptance.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f48ee8b31e489affc992e7febf9a09b65e1319709ff55e5b8b034dc5c9dadd71"} -->
````python
# tests/test_native_optional_acceptance.py
from workbench.domain import Entity
from workbench.native_acceptance import invalid_record


def test_optional_only_entity_uses_type_constraint_without_inventing_required_field():
    entity = Entity(
        name="review",
        description="评审",
        fields=[{"name": "score", "kind": "integer", "required": False}],
    )
    value, kind = invalid_record(entity, {"score": 7}, "fastapiadmin")
    assert value == {"score": {"invalid_scalar": True}}
    assert kind == "type"
    assert entity.fields[0].required is False


def test_boolean_only_entity_is_supported_by_acceptance_sampler():
    entity = Entity(
        name="review", description="评审", fields=[{"name": "approved", "kind": "boolean"}]
    )
    value, kind = invalid_record(entity, {"approved": True}, "fastapiadmin")
    assert kind == "type" and value["approved"] == {"invalid_scalar": True}
````
