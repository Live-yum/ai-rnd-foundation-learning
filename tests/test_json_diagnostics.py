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
