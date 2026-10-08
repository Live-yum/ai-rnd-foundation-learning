# tests/test_json_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.model_diagnostics`、`workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_diagnostics_keep_strict_json_guards_and_safe_facts`（L29–L45）：接收`content`、`kind`、`category`。 控制顺序：L34断言`detail["type"] == kind`；L35断言`detail["category"] == category`；L36断言`detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}`；L37按`kind == "json_syntax"`分支；L38断言`detail["position"] == { "line": caught.value.lineno, "column": caught.value.colno, "o…`；L44断言`"position" not in detail`；L45断言`"private-json-canary" not in json.dumps(details)`。 调用`pytest.raises`、`validate_content`、`json_diagnostics`、`len`、`content.encode`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_resource_failures_keep_static_codes_and_size_only`（L48–L65）：接收`monkeypatch`。 控制顺序：L57断言`json_diagnostics(caught.value)[0]["lengths"]["characters"] == 2`；L58断言`"private-" not in json.dumps(json_diagnostics(caught.value))`；L60按`digit_limit`分支；L64断言`json_diagnostics(caught.value)[0]["category"] == "json_integer_limit"`；L65断言`json_diagnostics(caught.value)[0]["lengths"]["characters"] == len(integer)`。 调用`monkeypatch.context`、`patch.setattr`、`pytest.raises`、`load_json`、`json_diagnostics`、`json.dumps`、`sys.get_int_max_str_digits`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_resource_failures_keep_static_codes_and_size_only.exhausted_parser`（L49–L50）：接收`*args`、`**kwargs`。 控制顺序：L50抛异常，停止当前正常路径。 调用`RecursionError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_parser_messages_are_never_exposed`（L68–L72）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L71断言`detail["category"] == "json_syntax"`；L72断言`"private-" not in json.dumps(detail)`。 调用`json.JSONDecodeError`、`json_diagnostics`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_extra_data_feedback_rebuilds_one_object_without_guessing_tail_contents`（L79–L94）：接收`tail`。 控制顺序：L84断言`detail["category"] == "extra_data"`；L85断言`detail["position"]["offset"] == len('{"summary":"first value"}') + ( len(tail) - len(…`；L88断言`detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}`；L89断言`"第一个 JSON 值" in detail["message"]`；L90断言`"若根对象提前闭合" in detail["message"]`；L91断言`"同一根对象的最后一个 } 之前" in detail["message"]`；L92断言`"保留全部业务字段" in detail["message"]`；L93断言`"不能只返回尾部补丁或截掉内容" in detail["message"]`。后续分支沿下方源码相同行号继续阅读。 调用`pytest.raises`、`load_json`、`json_diagnostics`、`len`、`tail.lstrip`、`content.encode`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_json_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L94。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4210`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_json_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0d0f94f5909ef7086d4d1f5a57f52d90f98476828588007eea7e16256a9be46f"} -->
````python
# tests/test_json_diagnostics.py
"""Strict JSON rejection emits facts, never response excerpts or duplicate key names."""

import json
import sys

import pytest

from workbench.domain import Requirement
from workbench.model_diagnostics import json_diagnostics
from workbench.model_protocol import load_json, validate_content


@pytest.mark.parametrize(
    "content,kind,category",
    [
        ('{"private-json-canary": "unfinished', "json_syntax", "unterminated_string"),
        ('{"private-json-canary": 1 "next": 2}', "json_syntax", "expected_comma"),
        ('{"private-json-canary": 1} {}', "json_syntax", "extra_data"),
        (
            '{"private-json-canary":1,"private-json-canary":2}',
            "duplicate_json_key",
            "duplicate_json_key",
        ),
        ('{"private-json-canary":NaN}', "non_finite_json_number", "non_finite_json_number"),
        ('{"private-json-canary":1e9999}', "non_finite_json_number", "non_finite_json_number"),
        ('["private-json-canary"]', "response_must_be_json_object", "response_must_be_json_object"),
    ],
)
def test_diagnostics_keep_strict_json_guards_and_safe_facts(content, kind, category):
    with pytest.raises(ValueError) as caught:
        validate_content(content, Requirement, mode="json_object")
    details = json_diagnostics(caught.value, content)
    detail = details[0]
    assert detail["type"] == kind
    assert detail["category"] == category
    assert detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}
    if kind == "json_syntax":
        assert detail["position"] == {
            "line": caught.value.lineno,
            "column": caught.value.colno,
            "offset": caught.value.pos,
        }
    else:
        assert "position" not in detail  # A duplicate-key hook has no reliable token position.
    assert "private-json-canary" not in json.dumps(details)


def test_local_resource_failures_keep_static_codes_and_size_only(monkeypatch):
    def exhausted_parser(*args, **kwargs):
        raise RecursionError("private-recursion-canary")

    # JSON recursion thresholds vary by Python implementation/version.
    with monkeypatch.context() as patch:
        patch.setattr("workbench.model_protocol.json.loads", exhausted_parser)
        with pytest.raises(ValueError, match="json_nesting_limit") as caught:
            load_json("{}")
    assert json_diagnostics(caught.value)[0]["lengths"]["characters"] == 2
    assert "private-" not in json.dumps(json_diagnostics(caught.value))
    digit_limit = sys.get_int_max_str_digits()
    if digit_limit:
        integer = "1" * (digit_limit + 1)
        with pytest.raises(ValueError, match="json_integer_limit") as caught:
            load_json(integer)
        assert json_diagnostics(caught.value)[0]["category"] == "json_integer_limit"
        assert json_diagnostics(caught.value)[0]["lengths"]["characters"] == len(integer)


def test_unknown_parser_messages_are_never_exposed():
    error = json.JSONDecodeError("private-error-canary", "private-response-canary", 0)
    detail = json_diagnostics(error)[0]
    assert detail["category"] == "json_syntax"
    assert "private-" not in json.dumps(detail)


@pytest.mark.parametrize(
    "tail",
    [',"private-tail-canary":false}', ' {"private-tail-canary":true}', " private-tail-canary"],
)
def test_extra_data_feedback_rebuilds_one_object_without_guessing_tail_contents(tail):
    content = '{"summary":"first value"}' + tail
    with pytest.raises(json.JSONDecodeError) as caught:
        load_json(content)
    detail = json_diagnostics(caught.value)[0]
    assert detail["category"] == "extra_data"
    assert detail["position"]["offset"] == len('{"summary":"first value"}') + (
        len(tail) - len(tail.lstrip())
    )
    assert detail["lengths"] == {"characters": len(content), "bytes": len(content.encode())}
    assert "第一个 JSON 值" in detail["message"]
    assert "若根对象提前闭合" in detail["message"]
    assert "同一根对象的最后一个 } 之前" in detail["message"]
    assert "保留全部业务字段" in detail["message"]
    assert "不能只返回尾部补丁或截掉内容" in detail["message"]
    assert "private-tail-canary" not in json.dumps(detail)
````
