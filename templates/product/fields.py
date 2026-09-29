"""Deterministic validators shared by CRUD and query filters; no LLM execution."""

import re
from datetime import date

from pydantic import ConfigDict, Field, StrictBool, StrictInt, StrictStr, create_model


def date_string(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("日期格式必须是 YYYY-MM-DD")
    date.fromisoformat(value)
    return value


def input_model(entity):
    fields = {}
    for field in entity["fields"]:
        kind = field["kind"]
        annotation = {
            "text": StrictStr,
            "enum": StrictStr,
            "date": StrictStr,
            "integer": StrictInt,
            "boolean": StrictBool,
        }[kind]
        constraints = {}
        if kind in {"text", "enum", "date"}:
            constraints = {
                "min_length": max(1 if field["required"] else 0, field.get("min_length", 0)),
                "max_length": 10 if kind == "date" else field["max_length"],
            }
        elif kind == "integer":
            constraints = {"ge": -9223372036854775808, "le": 9223372036854775807}
        fields[field["name"]] = (
            annotation if field["required"] else annotation | None,
            Field(default=... if field["required"] else None, **constraints),
        )
    return create_model(
        entity["name"] + "Input",
        __config__=ConfigDict(extra="forbid", str_strip_whitespace=True),
        **fields,
    )


def validate_options(entity, values):
    for field in entity["fields"]:
        value = values.get(field["name"])
        if value is None:
            continue
        if field["kind"] == "date":
            date_string(value)
        elif field["kind"] == "enum" and value not in field["choices"]:
            raise ValueError("分类不在已配置的选项中")
    return values


def filter_value(field, value):
    if len(value) > max(field["max_length"], 100):
        raise ValueError("筛选值过长")
    match field["kind"]:
        case "integer":
            if not re.fullmatch(r"-?[0-9]+", value):
                raise ValueError("整数筛选值无效")
            number = int(value)
            if not -9223372036854775808 <= number <= 9223372036854775807:
                raise ValueError("整数超出范围")
            return number
        case "boolean":
            if value not in {"true", "false"}:
                raise ValueError("布尔筛选值必须是 true 或 false")
            return value == "true"
        case "date":
            return date_string(value)
        case "enum":
            if value not in field["choices"]:
                raise ValueError("筛选值不在枚举中")
            return value
        case _:
            return value
