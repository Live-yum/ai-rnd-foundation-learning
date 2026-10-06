# templates/product/fields.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 按批准字段规则验证新增/修改载荷：必填、整数与布尔、文本长度、日期和枚举各自处理；可选空值不等于整数0或布尔False。业务规则在结构校验之后执行。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `date_string`（L9–L13）：接收`value`。 控制顺序：L10按`not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)`分支；L11抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`ValueError`、`date.fromisoformat`。 返回路径：L13的`value`。
- `integer_bounds`（L16–L27）：接收`field`。 源码说明：Ordinary integers use the same exact int32 domain in JSON, Java and SQL.。 控制顺序：L19按`field.get("minimum") is not None`分支；L21按`field.get("maximum") is not None`分支；L23按`field.get("exclusive_minimum") is not None`分支；L25按`field.get("exclusive_maximum") is not None`分支。 调用`field.get`、`max`、`min`。 返回路径：L27的`low, high`。
- `input_model`（L30–L65）：接收`entity`。 控制顺序：L32遍历`entity["fields"]`；L43按`kind in {"text", "enum", "date", "datetime"}`分支；L52按`kind == "integer"`分支；L55按`kind == "text" and field.get("pattern") is not None`分支。 调用`max`、`field.get`、`integer_bounds`、`Field`、`create_model`、`ConfigDict`。 返回路径：L61的`create_model( entity["name"] + "Input", __config__=ConfigDict(extra="forbid", str_strip_wh…`。
- `validate_options`（L68–L79）：接收`entity`、`values`。 控制顺序：L69遍历`entity["fields"]`；L71按`value is None`分支；L73按`field["kind"] == "date"`分支；L75按`field["kind"] == "datetime"`分支；L77按`field["kind"] == "enum" and value not in field["choices"]`分支；L78抛异常，停止当前正常路径。 调用`values.get`、`date_string`、`datetime_string`、`ValueError`。 返回路径：L79的`values`。
- `filter_value`（L82–L106）：接收`field`、`value`。 控制顺序：L83按`len(value) > max(field["max_length"], 100)`分支；L84抛异常，停止当前正常路径；L87按`not re.fullmatch(r"-?[0-9]+", value)`分支；L88抛异常，停止当前正常路径；L90按`not -(2**31) <= number < 2**31`分支；L91抛异常，停止当前正常路径；L94按`value not in {"true", "false"}`分支；L95抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`len`、`max`、`ValueError`、`re.fullmatch`、`int`、`date_string`、`datetime_string`。 返回路径：L92的`number`；L96的`value == "true"`；L98的`date_string(value)`。
- `datetime_string`（L109–L115）：接收`value`。 控制顺序：L110按`not isinstance(value, str)`分支；L111抛异常，停止当前正常路径；L113按`parsed.tzinfo is None`分支；L114抛异常，停止当前正常路径。 调用`isinstance`、`ValueError`、`datetime.fromisoformat`、`value.replace`、`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds"…`、`parsed.astimezone(timezone.utc).isoformat`、`parsed.astimezone`。 返回路径：L115的`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")`。

</details>

**创建路径：** `templates/product/fields.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L115。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4151`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/fields.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "34506dc5ae704e2c05dbff23e7eabdfb8b9526ecb90430a36eeebd7c4866e143"} -->
````python
# templates/product/fields.py
"""Deterministic validators shared by CRUD and query filters; no LLM execution."""

import re
from datetime import date, datetime, timezone

from pydantic import ConfigDict, Field, StrictBool, StrictInt, StrictStr, create_model


def date_string(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("日期格式必须是 YYYY-MM-DD")
    date.fromisoformat(value)
    return value


def integer_bounds(field):
    """Ordinary integers use the same exact int32 domain in JSON, Java and SQL."""
    low, high = -(2**31), 2**31 - 1
    if field.get("minimum") is not None:
        low = max(low, field["minimum"])
    if field.get("maximum") is not None:
        high = min(high, field["maximum"])
    if field.get("exclusive_minimum") is not None:
        low = max(low, field["exclusive_minimum"] + 1)
    if field.get("exclusive_maximum") is not None:
        high = min(high, field["exclusive_maximum"] - 1)
    return low, high


def input_model(entity):
    fields = {}
    for field in entity["fields"]:
        kind = field["kind"]
        annotation = {
            "text": StrictStr,
            "enum": StrictStr,
            "date": StrictStr,
            "datetime": StrictStr,
            "integer": StrictInt,
            "boolean": StrictBool,
        }[kind]
        constraints = {}
        if kind in {"text", "enum", "date", "datetime"}:
            constraints = {
                "min_length": max(1 if field["required"] else 0, field.get("min_length", 0)),
                "max_length": 10
                if kind == "date"
                else 40
                if kind == "datetime"
                else field["max_length"],
            }
        elif kind == "integer":
            low, high = integer_bounds(field)
            constraints = {"ge": low, "le": high}
        if kind == "text" and field.get("pattern") is not None:
            constraints["pattern"] = field["pattern"]
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
        elif field["kind"] == "datetime":
            values[field["name"]] = datetime_string(value)
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
            if not -(2**31) <= number < 2**31:
                raise ValueError("整数超出范围")
            return number
        case "boolean":
            if value not in {"true", "false"}:
                raise ValueError("布尔筛选值必须是 true 或 false")
            return value == "true"
        case "date":
            return date_string(value)
        case "datetime":
            return datetime_string(value)
        case "enum":
            if value not in field["choices"]:
                raise ValueError("筛选值不在枚举中")
            return value
        case _:
            return value


def datetime_string(value):
    if not isinstance(value, str):
        raise ValueError("时间必须是包含时区的ISO时间")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("时间必须包含时区")
    return parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
````
