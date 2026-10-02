# templates/product/fields.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 按批准字段规则验证新增/修改载荷：必填、整数与布尔、文本长度、日期和枚举各自处理；可选空值不等于整数0或布尔False。业务规则在结构校验之后执行。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `date_string`（L9–L13）：接收`value`。 控制顺序：L10按`not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value)`分支；L11抛异常，停止当前正常路径。 调用`isinstance`、`re.fullmatch`、`ValueError`、`date.fromisoformat`。 返回路径：L13的`value`。
- `input_model`（L16–L48）：接收`entity`。 控制顺序：L18遍历`entity["fields"]`；L29按`kind in {"text", "enum", "date", "datetime"}`分支；L38按`kind == "integer"`分支。 调用`max`、`field.get`、`Field`、`create_model`、`ConfigDict`。 返回路径：L44的`create_model( entity["name"] + "Input", __config__=ConfigDict(extra="forbid", str_strip_wh…`。
- `validate_options`（L51–L62）：接收`entity`、`values`。 控制顺序：L52遍历`entity["fields"]`；L54按`value is None`分支；L56按`field["kind"] == "date"`分支；L58按`field["kind"] == "datetime"`分支；L60按`field["kind"] == "enum" and value not in field["choices"]`分支；L61抛异常，停止当前正常路径。 调用`values.get`、`date_string`、`datetime_string`、`ValueError`。 返回路径：L62的`values`。
- `filter_value`（L65–L89）：接收`field`、`value`。 控制顺序：L66按`len(value) > max(field["max_length"], 100)`分支；L67抛异常，停止当前正常路径；L70按`not re.fullmatch(r"-?[0-9]+", value)`分支；L71抛异常，停止当前正常路径；L73按`not -9223372036854775808 <= number <= 9223372036854775807`分支；L74抛异常，停止当前正常路径；L77按`value not in {"true", "false"}`分支；L78抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`len`、`max`、`ValueError`、`re.fullmatch`、`int`、`date_string`、`datetime_string`。 返回路径：L75的`number`；L79的`value == "true"`；L81的`date_string(value)`。
- `datetime_string`（L92–L98）：接收`value`。 控制顺序：L93按`not isinstance(value, str)`分支；L94抛异常，停止当前正常路径；L96按`parsed.tzinfo is None`分支；L97抛异常，停止当前正常路径。 调用`isinstance`、`ValueError`、`datetime.fromisoformat`、`value.replace`、`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds"…`、`parsed.astimezone(timezone.utc).isoformat`、`parsed.astimezone`。 返回路径：L98的`parsed.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")`。

</details>

**创建路径：** `templates/product/fields.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L98。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3497`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/fields.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5bb5ed2677bcecc68749b0410a65f4c5b04e5b564d4ddf38f65f62788e832c42"} -->
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
            if not -9223372036854775808 <= number <= 9223372036854775807:
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
