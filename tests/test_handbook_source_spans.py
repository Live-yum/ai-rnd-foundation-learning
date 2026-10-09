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
