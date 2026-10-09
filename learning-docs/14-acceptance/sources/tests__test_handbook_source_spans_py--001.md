# tests/test_handbook_source_spans.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`、`scripts.handbook_notes`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_cached_spans_match_standard_ast_for_every_located_node`（L26–L35）：接收`source`。 控制顺序：L28遍历`ast.walk(tree)`；L29断言`source_segment(source, node) == ast.get_source_segment(source, node)`；L32遍历`(0, 1, 65, 110)`；L33断言`segment(source, node, limit) == ( expected if len(expected) <= limit else expected[:l…`。 调用`ast.parse`、`ast.walk`、`source_segment`、`ast.get_source_segment`、`type`、`" ".join(expected.split()).replace`、`" ".join`、`expected.split`、`segment`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_source_spans_keep_the_node_name_fallback`（L49–L51）：接收`node`。 控制顺序：L50断言`source_segment("value = 1", node) is None`；L51断言`segment("value = 1", node) == type(node).__name__`。 调用`source_segment`、`segment`、`type`、`pytest.mark.parametrize`、`ast.Constant`、`ast.Name`、`ast.Load`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_an_empty_span_keeps_the_existing_node_name_fallback`（L55–L58）：接收`source`。 控制顺序：L57断言`source_segment(source, node) == ast.get_source_segment(source, node) == ""`；L58断言`segment(source, node) == "Constant"`。 调用`ast.Constant`、`source_segment`、`ast.get_source_segment`、`segment`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_changing_the_source_never_reuses_another_files_lines`（L61–L64）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L62遍历`("first = '甲'", "other = '乙'", "first = '甲'")`；L64断言`source_segment(source, node) == ast.get_source_segment(source, node)`。 调用`ast.parse`、`source_segment`、`ast.get_source_segment`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_base64_lines_preserve_the_existing_format_and_original_bytes`（L68–L71）：接收`content`。 控制顺序：L70断言`encoded_lines(content) == expected`；L71断言`base64.b64decode(encoded_lines(content)) == content`。 调用`"\n".join`、`textwrap.wrap`、`base64.b64encode(content).decode`、`base64.b64encode`、`encoded_lines`、`base64.b64decode`、`pytest.mark.parametrize`、`bytes`、`range`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook_source_spans.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L71。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2889`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook_source_spans.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "634a10d86cc3bd8e0b71ef6a43e5eedcf06c2d016f7d6245cbe9786ed7660a1d"} -->
````python
# tests/test_handbook_source_spans.py
"""Book rendering keeps exact AST/source and Base64 semantics with linear extraction."""

import ast
import base64
import textwrap

import pytest

from scripts.build_handbook import encoded_lines
from scripts.handbook_notes import segment, source_segment


@pytest.mark.parametrize(
    "source",
    [
        "客户 = '城市🙂'\n结果 = 客户 + '甲|乙'\n",
        "value = (\r\n    'north' +\r\n    'south'\r\n)\r\n",
        "value = 'first'\rnext_value = value\r",
        "\fvalue = 'page'\n\fresult = value + 'break'\n",
        "values = {\n    '客户': ['甲', '乙'],\n    'result': (1 + 2),\n}",
        "text = 'inside\u2028a\u2029literal\v\f'\nresult = text\n",
        "value = '''first\n第二行\nthird'''\nresult = value",
        "first = 1; second = first + 2",
    ],
)
def test_cached_spans_match_standard_ast_for_every_located_node(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        assert source_segment(source, node) == ast.get_source_segment(source, node)
        expected = ast.get_source_segment(source, node) or type(node).__name__
        expected = " ".join(expected.split()).replace("|", "\\|")
        for limit in (0, 1, 65, 110):
            assert segment(source, node, limit) == (
                expected if len(expected) <= limit else expected[:limit] + "…"
            )


@pytest.mark.parametrize(
    "node",
    [
        ast.Constant(value=1),
        ast.Name(id="value", ctx=ast.Load(), lineno=1, col_offset=0),
        ast.Name(
            id="value", ctx=ast.Load(), lineno=1, col_offset=0, end_lineno=1, end_col_offset=None
        ),
        ast.Name(id="value", ctx=ast.Load(), lineno=1, col_offset=0, end_lineno=None),
    ],
)
def test_missing_source_spans_keep_the_node_name_fallback(node):
    assert source_segment("value = 1", node) is None
    assert segment("value = 1", node) == type(node).__name__


@pytest.mark.parametrize("source", ["value = 1", ""])
def test_an_empty_span_keeps_the_existing_node_name_fallback(source):
    node = ast.Constant(value="", lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)
    assert source_segment(source, node) == ast.get_source_segment(source, node) == ""
    assert segment(source, node) == "Constant"


def test_changing_the_source_never_reuses_another_files_lines():
    for source in ("first = '甲'", "other = '乙'", "first = '甲'"):
        node = ast.parse(source).body[0].value
        assert source_segment(source, node) == ast.get_source_segment(source, node)


@pytest.mark.parametrize("content", [b"", b"x", b"x" * 57, b"x" * 58, bytes(range(256)) * 300])
def test_base64_lines_preserve_the_existing_format_and_original_bytes(content):
    expected = "\n".join(textwrap.wrap(base64.b64encode(content).decode("ascii"), 76))
    assert encoded_lines(content) == expected
    assert base64.b64decode(encoded_lines(content)) == content
````
