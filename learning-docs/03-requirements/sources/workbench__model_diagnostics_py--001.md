# workbench/model_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.model_protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `failure_diagnostic`（L34–L100）：接收`code`、`trace_id`、`attempt`、`details`。 控制顺序：L38按`code.startswith("http_") or code == "transport_error"`分支；L42按`code in {"http_401", "http_403"}`分支；L44按`code == "http_429"`分支；L46按`code in {"interrupted", "worker_interrupted", "abandoned_attempt"}`分支；L50按`code in {"refusal", "content_filter"}`分支；L53按`code == "unexpected_model_error"`分支；L57按`code == "invalid_json"`分支；L60按`code == "structured_parser_disagreement"`分支。后续分支沿下方源码相同行号继续阅读。 调用`code.startswith`。 返回路径：L92的`{ "phase": phase, "code": code, "trace_id": trace_id, "attempt": attempt, "summary": summa…`。
- `json_diagnostics`（L103–L138）：接收`exc`、`content`。 源码说明：Expose syntax locations and static guard names, never parser docs or snippets.。 控制顺序：L107按`isinstance(exc, json.JSONDecodeError)`分支；L122按`isinstance(exc, UnicodeDecodeError)`分支。 调用`isinstance`、`json_lengths`、`JSON_SYNTAX_CATEGORIES.get`、`len`、`str`、`JSON_GUARD_MESSAGES.get`。 返回路径：L109的`[ { "type": "json_syntax", "category": category, "path": [], "position": {"line": exc.line…`；L125的`[ { "type": code, "category": code, "path": [], "lengths": lengths, "message": JSON_GUARD_…`。
- `_schema_nodes`（L141–L172）：接收`document`、`path`。 源码说明：Resolve only schema-owned properties/items through local refs and unions.。 控制顺序：L161遍历`path`；L163遍历`nodes`；L164遍历`expand(node)`；L165按`isinstance(part, int)`分支；L169按`isinstance(child, dict)`分支。 调用`expand`、`isinstance`、`candidate.get`、`candidate.get("properties", {}).get`、`children.append`。 返回路径：L172的`[candidate for node in nodes for candidate in expand(node)]`。
- `_schema_nodes.expand`（L144–L158）：接收`node`、`seen`。 控制顺序：L145按`not isinstance(node, dict)`分支；L149按`isinstance(ref, str) and ref.startswith("#/") and ref not in seen`分支；L151遍历`ref[2:].split("/")`；L152按`not isinstance(target, dict)`分支；L156遍历`("anyOf", "oneOf", "allOf")`；L157遍历`node.get(key, [])`。 调用`frozenset`、`isinstance`、`node.get`、`ref.startswith`、`ref[2:].split`、`target.get`、`part.replace("~1", "/").replace`、`part.replace`、`expand`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_constraint_hint`（L175–L205）：接收`document`、`error`。 控制顺序：L183按`error["type"] not in rules or len(error["loc"]) > 20`分支；L187按`not matches or any(node[key] != matches[0][key] for node in matches)`分支；L190按`not ( (key == "pattern" and isinstance(constraint, str) and len(constraint) <= 200) o…`分支；L196按`isinstance(node.get("description"), str)`分支；L203按`examples`分支。 调用`len`、`_schema_nodes`、`any`、`isinstance`、`type`、`message.format`、`node.get`、`"、".join`。 返回路径：L184的`None`；L188的`None`；L194的`None`。
- `schema_diagnostics`（L208–L272）：接收`exc`、`schema`。 源码说明：Only schema-owned path segments and validator type, never arbitrary model values. Pydantic root validator messages and extra-field locations can contain the raw response or credentials; neither is saf。 调用`set`、`schema.model_json_schema`、`collect`、`safe_message`、`error["type"].replace("_", "").isalnum`、`error["type"].replace`、`isinstance`、`_constraint_hint`、`exc.errors`。 返回路径：L261的`[ { "message": safe_message(error), "type": error["type"] if error["type"].replace("_", ""…`。
- `schema_diagnostics.collect`（L216–L223）：接收`node`。 控制顺序：L217按`isinstance(node, dict)`分支；L219遍历`node.values()`；L221按`isinstance(node, list)`分支；L222遍历`node`。 调用`isinstance`、`allowed.update`、`node.get`、`node.values`、`collect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `schema_diagnostics.safe_message`（L257–L259）：接收`error`。 调用`error["msg"].removeprefix`。 返回路径：L259的`value if value in safe_messages else "字段结构或类型不符合约定"`。

</details>

**创建路径：** `workbench/model_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L272。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12629`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8c4d874d2450d45595593d9a7570bad84b134023b67be49d15fd59e81e77c4ad"} -->
````python
# workbench/model_diagnostics.py
"""Safe actionable provider failures. Never persist provider bodies or input values."""

import json

from workbench.model_protocol import JSONGuardFailure, json_lengths

JSON_SYNTAX_CATEGORIES = {
    "Expecting value": "expected_value",
    "Expecting property name enclosed in double quotes": "expected_property_name",
    "Expecting ':' delimiter": "expected_colon",
    "Expecting ',' delimiter": "expected_comma",
    "Unterminated string starting at": "unterminated_string",
    "Invalid \\escape": "invalid_escape",
    "Invalid \\uXXXX escape": "invalid_unicode_escape",
    "Invalid control character at": "invalid_control_character",
    "Extra data": "extra_data",
    "Unexpected UTF-8 BOM (decode using utf-8-sig)": "unexpected_bom",
}
JSON_GUARD_MESSAGES = {
    "duplicate_json_key": "JSON 对象中不能出现重复字段名；保留需求并为每个字段返回唯一值。",
    "non_finite_json_number": "JSON 数字必须有限；不能包含 NaN、Infinity 或溢出的数字。",
    "json_nesting_limit": "JSON 嵌套超过本地解析器限制；按给定 Schema 返回对象。",
    "json_integer_limit": "JSON 整数字面量超过本地解析器位数限制；按 Schema 返回数字。",
    "response_must_be_json_object": "JSON 顶层必须是一个对象，不能是数组、字符串或空值。",
    "langchain_structured_output_parsing_failed": "本地严格 JSON 与 Schema 校验已通过，但 LangChain 结构化解析未通过；不能据此认定 JSON 语法错误。",
}
JSON_DIAGNOSTIC_CATEGORIES = (
    frozenset(JSON_SYNTAX_CATEGORIES.values())
    | frozenset(JSON_GUARD_MESSAGES)
    | {"json_syntax", "json_encoding", "invalid_json"}
)


def failure_diagnostic(code, *, trace_id, attempt=None, details=None):
    phase = "response_validation"
    summary = "模型响应未通过结构校验，未生成可批准结果。"
    hint = "按字段路径与约束提示检查该阶段的模型和规划契约，再重试当前运行；JSON 对象模式不保证符合 Schema。无需重填已提交的回答。"
    if code.startswith("http_") or code == "transport_error":
        phase = "provider_request"
        summary = "模型请求失败，尚未取得有效响应。"
        hint = "先在模型与配置中测试该阶段连接，检查网络、服务额度与模型权限，再重试当前运行。"
        if code in {"http_401", "http_403"}:
            hint = "检查该阶段的密钥与模型访问权限，保存后测试连接；不要把密钥放入对话。"
        elif code == "http_429":
            hint = "检查服务商额度或限流状态，稍后手动重试当前运行。"
    elif code in {"interrupted", "worker_interrupted", "abandoned_attempt"}:
        phase = "response_stream"
        summary = "响应在完成前中断，已保留历史回答。"
        hint = "确认服务与网络恢复后，重试当前运行；不会把未完成响应当作已批准方案。"
    elif code in {"refusal", "content_filter"}:
        summary = "模型拒绝处理或触发内容过滤。"
        hint = "检查请求是否适合该服务；不要通过重试绕过服务商的安全限制。"
    elif code == "unexpected_model_error":
        phase = "model_execution"
        summary = "模型调用发生未预期错误，未生成可批准结果。"
        hint = "使用追踪 ID 定位服务端日志，检查模型适配器和配置；修复后重试当前运行。"
    elif code == "invalid_json":
        summary = "服务已响应，但返回内容不是可接受的完整 JSON 对象。"
        hint = "检查服务是否支持 JSON 对象输出；保留严格校验，调整模型或配置后重试当前运行。"
    elif code == "structured_parser_disagreement":
        phase = "model_execution"
        summary = "本地严格 JSON 与 Schema 校验已通过，但 LangChain 结构化解析未通过。"
        hint = "按追踪 ID 检查结构化适配器；保留两层校验，不将解析器差异当作 JSON 语法错误。"
    elif code in {
        "length",
        "truncated",
        "response_too_large",
        "response_byte_limit",
        "stream_wire_limit",
    }:
        summary = "模型响应超过长度限制，无法作为完整结果。"
        hint = "检查模型输出限制与本轮范围，调整后重试；保留原始需求与已提交回答。"
        if code == "stream_wire_limit":
            phase = "response_stream"
            summary = "模型流的传输字节超过安全上限；正文与流式封装分别计量。"
    elif code in {
        "request_destination_rejected",
        "request_count_limit",
        "request_byte_limit",
        "request_not_json",
        "model_substitution_rejected",
        "authorization_header_mismatch",
        "structured_output_required",
        "output_budget_missing_or_exceeded",
        "monetary_budget_exceeded",
        "provider_reported_usage_exceeds_reserved_bounds",
        "harness_internal_error",
    }:
        phase = "request_guard"
        summary = "验收请求被安全或预算保护停止，未自动重试。"
        hint = "使用追踪 ID 和安全回执中的错误代码定位原因；重新实测前核对剩余预算与授权。"
    return {
        "phase": phase,
        "code": code,
        "trace_id": trace_id,
        "attempt": attempt,
        "summary": summary,
        "retry_hint": hint,
        "details": details or [],
    }


def json_diagnostics(exc, content=None):
    """Expose syntax locations and static guard names, never parser docs or snippets."""
    source = exc.doc if isinstance(exc, json.JSONDecodeError) else content
    lengths = exc.lengths if isinstance(exc, JSONGuardFailure) else json_lengths(source)
    if isinstance(exc, json.JSONDecodeError):
        category = JSON_SYNTAX_CATEGORIES.get(exc.msg, "json_syntax")
        return [
            {
                "type": "json_syntax",
                "category": category,
                "path": [],
                "position": {"line": exc.lineno, "column": exc.colno, "offset": exc.pos},
                "lengths": lengths,
                "message": f"JSON 解析器报告 {category}，位于第 {exc.lineno} 行、第 {exc.colno} 列，"
                f"字符偏移 {exc.pos}（从 0 开始），全文 {len(exc.doc)} 个字符；"
                "返回一个完整对象，正确转义字符串并闭合括号，不要附加 Markdown 围栏或说明文字。",
            }
        ]
    code = str(exc) if str(exc) in JSON_GUARD_MESSAGES else "invalid_json"
    if isinstance(exc, UnicodeDecodeError):
        code = "json_encoding"
        lengths = {"bytes": len(exc.object)}
    return [
        {
            "type": code,
            "category": code,
            "path": [],
            "lengths": lengths,
            "message": JSON_GUARD_MESSAGES.get(
                code,
                "响应编码无法解码为 JSON 文本。"
                if code == "json_encoding"
                else "只返回符合给定 Schema 的一个完整 JSON 对象。",
            ),
        }
    ]


def _schema_nodes(document, path):
    """Resolve only schema-owned properties/items through local refs and unions."""

    def expand(node, seen=frozenset()):
        if not isinstance(node, dict):
            return
        yield node
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/") and ref not in seen:
            target = document
            for part in ref[2:].split("/"):
                if not isinstance(target, dict):
                    break
                target = target.get(part.replace("~1", "/").replace("~0", "~"), {})
            yield from expand(target, seen | {ref})
        for key in ("anyOf", "oneOf", "allOf"):
            for branch in node.get(key, []):
                yield from expand(branch, seen)

    nodes = [document]
    for part in path:
        children = []
        for node in nodes:
            for candidate in expand(node):
                if isinstance(part, int):
                    child = candidate.get("items")
                else:
                    child = candidate.get("properties", {}).get(part)
                if isinstance(child, dict):
                    children.append(child)
        nodes = children
    return [candidate for node in nodes for candidate in expand(node)]


def _constraint_hint(document, error):
    rules = {
        "string_pattern_mismatch": ("pattern", "文本必须匹配格式：{}。"),
        "string_too_long": ("maxLength", "文本最多允许 {} 个字符。"),
        "string_too_short": ("minLength", "文本至少需要 {} 个字符。"),
        "too_long": ("maxItems", "列表最多允许 {} 项。"),
        "too_short": ("minItems", "列表至少需要 {} 项。"),
    }
    if error["type"] not in rules or len(error["loc"]) > 20:
        return None
    key, message = rules[error["type"]]
    matches = [node for node in _schema_nodes(document, error["loc"]) if key in node]
    if not matches or any(node[key] != matches[0][key] for node in matches):
        return None
    node, constraint = matches[0], matches[0][key]
    if not (
        (key == "pattern" and isinstance(constraint, str) and len(constraint) <= 200)
        or (key != "pattern" and type(constraint) is int and constraint >= 0)
    ):
        return None
    text = message.format(constraint)
    if isinstance(node.get("description"), str):
        text += " " + node["description"][:400]
    examples = [
        value
        for value in node.get("examples", [])[:3]
        if isinstance(value, str) and len(value) <= 100
    ]
    if examples:
        text += " 示例：" + "、".join(examples)
    return {"message": text, "constraints": {key: constraint}}


def schema_diagnostics(exc, schema):
    """Only schema-owned path segments and validator type, never arbitrary model values.

    Pydantic root validator messages and extra-field locations can contain the
    raw response or credentials; neither is safe to expose verbatim.
    """
    allowed = set()

    def collect(node):
        if isinstance(node, dict):
            allowed.update(node.get("properties", {}))
            for value in node.values():
                collect(value)
        elif isinstance(node, list):
            for value in node:
                collect(value)

    document = schema.model_json_schema()
    collect(document)
    safe_messages = {
        "字段清单不能包含重复名称",
        "文本问题不能包含选择项",
        "选择问题至少包含两个不同选项",
        "同一个问题的选项标识不能重复",
        "同一个问题的选项文字不能重复",
        "问题标识不能重复",
        "问题文字不能重复",
        "结构化问题必须逐字完整对应 questions 中的全部真实阻塞问题",
        "同一实体不能重复声明字段清单",
        "最小长度不得大于最大长度",
        "枚举必须有不重复的选项",
        "只有 enum 类型可以声明 choices",
        "关键词搜索只能使用文本/枚举字段",
        "日期范围只支持 date 类型",
        "字段名属于保留名称",
        "字段名称必须唯一",
        "实体名称重复或为保留名称",
        "自定义规则引用未知实体",
        "仅受控模块路由引用准确module_id",
        "阻塞路由须明确缺少的环境或授权，其他路由不能隐藏阻塞",
        "批量导入模块必须有准确实体、重复策略和行数配置；其他模块不能混用",
        "功能ID不能重复",
        "功能依赖必须引用本轮明确功能",
        "功能依赖不能形成循环",
        "模块ID不能重复",
        "每个模块必须逐个关联所保留的功能，不能有遗漏或孤立模块",
        "模块依赖必须引用本计划模块且不能形成循环",
    }

    def safe_message(error):
        value = error["msg"].removeprefix("Value error, ")
        return value if value in safe_messages else "字段结构或类型不符合约定"

    return [
        {
            "message": safe_message(error),
            "type": error["type"] if error["type"].replace("_", "").isalnum() else "validation",
            "path": [
                part if isinstance(part, int) or part in allowed else "[field]"
                for part in error["loc"][:20]
            ],
            **(_constraint_hint(document, error) or {}),
        }
        for error in exc.errors(include_input=False, include_url=False)[:30]
    ]
````
