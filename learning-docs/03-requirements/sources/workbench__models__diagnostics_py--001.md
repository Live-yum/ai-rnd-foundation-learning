# workbench/models/diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.models.protocol`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `response_failure_facts`（L11–L28）：接收`value`。 源码说明：Re-filter optional response facts without retaining any provider text.。 控制顺序：L13按`not isinstance(value, dict)`分支；L26按`type(status) is int and 100 <= status <= 599`分支。 调用`isinstance`、`value.get`、`type`。 返回路径：L14的`{}`；L28的`result`。
- `transport_category`（L31–L55）：接收`exc`。 源码说明：Finite typed classification only; never inspect error strings or requests.。 控制顺序：L47遍历`range(12)`；L48按`exc is None or id(exc) in seen`分支；L51遍历`kinds`；L52按`isinstance(exc, kind)`分支。 调用`set`、`range`、`id`、`seen.add`、`isinstance`。 返回路径：L53的`label`；L55的`"other"`。
- `transport_failure`（L58–L79）：接收`exc`。 源码说明：Classify typed causes only; never parse or expose exception/provider text.。 控制顺序：L62遍历`range(12)`；L63按`exc is None or id(exc) in seen`分支；L66按`isinstance(exc, ssl.SSLCertVerificationError)`分支；L71按`isinstance(exc, httpx.ProxyError)`分支；L74按`proxy`分支。 调用`set`、`range`、`id`、`seen.add`、`isinstance`。 返回路径：L67的`( "tls_certificate_verification_failed", "TLS 证书校验失败；请检查证书有效期、信任链及地址与证书名称是否匹配，不能关闭校验", )`；L75的`( "proxy_connection_failed", "代理连接或隧道失败；请检查代理访问策略。这不能证明目标服务证书或 API Key 无效", )`；L79的`None`。
- `json_failure_facts`（L109–L136）：接收`details`。 源码说明：Project the single JSON diagnostic into bounded, text-free receipt facts.。 控制顺序：L111按`not isinstance(details, list) or len(details) != 1 or not isinstance(details[0], dict…`分支；L115按`type(category) is not str or category not in JSON_DIAGNOSTIC_CATEGORIES or category =…`分支；L122遍历`( ("position", {"line": (1, 1), "column": (1, 1), "offset": (0, 0…`；L127按`not isinstance(source, dict)`分支；L130遍历`fields.items()`；L132按`type(value) is int and minimum <= value <= MAX_MODEL_CONTENT_BYTES + extra`分支；L134按`safe`分支。 调用`isinstance`、`len`、`detail.get`、`type`、`fields.items`、`source.get`。 返回路径：L112的`{}`；L120的`{}`；L136的`result`。
- `json_syntax_category`（L139–L145）：接收`exc`。 控制顺序：L141按`category == "extra_data"`分支；L143按`tail.strip(" \t\r\n") and not set(tail).difference("}] \t\r\n")`分支。 调用`JSON_SYNTAX_CATEGORIES.get`、`tail.strip`、`set(tail).difference`、`set`。 返回路径：L144的`"extra_closing_delimiters"`；L145的`category`。
- `failure_diagnostic`（L148–L234）：接收`code`、`trace_id`、`attempt`、`details`。 控制顺序：L152按`code.startswith("http_") or code in { "transport_error", "tls_certificate_verificatio…`分支；L160按`code in {"http_401", "http_403"}`分支；L162按`code == "http_429"`分支；L164按`code == "tls_certificate_verification_failed"`分支；L166按`code == "proxy_connection_failed"`分支；L168按`code in {"interrupted", "worker_interrupted", "abandoned_attempt"}`分支；L172按`code in {"refusal", "content_filter"}`分支；L175按`code == "unexpected_model_error"`分支。后续分支沿下方源码相同行号继续阅读。 调用`code.startswith`。 返回路径：L226的`{ "phase": phase, "code": code, "trace_id": trace_id, "attempt": attempt, "summary": summa…`。
- `json_diagnostics`（L237–L283）：接收`exc`、`content`。 源码说明：Expose syntax locations and static guard names, never parser docs or snippets.。 控制顺序：L241按`isinstance(exc, json.JSONDecodeError)`分支；L267按`isinstance(exc, UnicodeDecodeError)`分支。 调用`isinstance`、`json_lengths`、`json_syntax_category`、`len`、`str`、`JSON_GUARD_MESSAGES.get`。 返回路径：L255的`[ { "type": "json_syntax", "category": category, "path": [], "position": {"line": exc.line…`；L270的`[ { "type": code, "category": code, "path": [], "lengths": lengths, "message": JSON_GUARD_…`。
- `_schema_nodes`（L286–L317）：接收`document`、`path`。 源码说明：Resolve only schema-owned properties/items through local refs and unions.。 控制顺序：L306遍历`path`；L308遍历`nodes`；L309遍历`expand(node)`；L310按`isinstance(part, int)`分支；L314按`isinstance(child, dict)`分支。 调用`expand`、`isinstance`、`candidate.get`、`candidate.get("properties", {}).get`、`children.append`。 返回路径：L317的`[candidate for node in nodes for candidate in expand(node)]`。
- `_schema_nodes.expand`（L289–L303）：接收`node`、`seen`。 控制顺序：L290按`not isinstance(node, dict)`分支；L294按`isinstance(ref, str) and ref.startswith("#/") and ref not in seen`分支；L296遍历`ref[2:].split("/")`；L297按`not isinstance(target, dict)`分支；L301遍历`("anyOf", "oneOf", "allOf")`；L302遍历`node.get(key, [])`。 调用`frozenset`、`isinstance`、`node.get`、`ref.startswith`、`ref[2:].split`、`target.get`、`part.replace("~1", "/").replace`、`part.replace`、`expand`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_constraint_hint`（L320–L350）：接收`document`、`error`。 控制顺序：L328按`error["type"] not in rules or len(error["loc"]) > 20`分支；L332按`not matches or any(node[key] != matches[0][key] for node in matches)`分支；L335按`not ( (key == "pattern" and isinstance(constraint, str) and len(constraint) <= 200) o…`分支；L341按`isinstance(node.get("description"), str)`分支；L348按`examples`分支。 调用`len`、`_schema_nodes`、`any`、`isinstance`、`type`、`message.format`、`node.get`、`"、".join`。 返回路径：L329的`None`；L333的`None`；L339的`None`。
- `schema_diagnostics`（L353–L423）：接收`exc`、`schema`。 源码说明：Only schema-owned path segments and validator type, never arbitrary model values. Pydantic root validator messages and extra-field locations can contain the raw response or credentials; neither is saf。 控制顺序：L410遍历`errors`。 调用`set`、`schema.model_json_schema`、`collect`、`exc.errors`、`document.get`、`tuple`、`safe_message`、`error["type"].replace("_", "").isalnum`、`error["type"].replace`等。 返回路径：L412的`[ { "message": safe_message(error), "type": error["type"] if error["type"].replace("_", ""…`。
- `schema_diagnostics.collect`（L361–L368）：接收`node`。 控制顺序：L362按`isinstance(node, dict)`分支；L364遍历`node.values()`；L366按`isinstance(node, list)`分支；L367遍历`node`。 调用`isinstance`、`allowed.update`、`node.get`、`node.values`、`collect`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `schema_diagnostics.safe_message`（L402–L404）：接收`error`。 调用`error["msg"].removeprefix`。 返回路径：L404的`value if value in safe_messages else "字段结构或类型不符合约定"`。

</details>

**创建路径：** `workbench/models/diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L423。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19092`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/models/diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "dfef91fb3409f4d62944c37ea1361a43a3b36e448fe8aa7686da89bea6bdf5a1"} -->
````python
# workbench/models/diagnostics.py
"""Safe actionable provider failures. Never persist provider bodies or input values."""

import json
import ssl

import httpx

from workbench.models.protocol import MAX_MODEL_CONTENT_BYTES, JSONGuardFailure, json_lengths


def response_failure_facts(value):
    """Re-filter optional response facts without retaining any provider text."""
    if not isinstance(value, dict):
        return {}
    phase = value.get("phase")
    finish = value.get("finish_reason")
    result = {
        "phase": phase
        if type(phase) is str and phase in {"envelope_decode", "content_decode"}
        else "unknown",
        "finish_reason": finish
        if type(finish) is str and finish in {"stop", "unknown"}
        else "unknown",
    }
    status = value.get("http_status")
    if type(status) is int and 100 <= status <= 599:
        result["http_status"] = status
    return result


def transport_category(exc):
    """Finite typed classification only; never inspect error strings or requests."""
    kinds = (
        (httpx.ConnectTimeout, "connect_timeout"),
        (httpx.ReadTimeout, "read_timeout"),
        (httpx.WriteTimeout, "write_timeout"),
        (httpx.PoolTimeout, "pool_timeout"),
        (httpx.TimeoutException, "timeout"),
        (httpx.ProxyError, "proxy_error"),
        (httpx.ConnectError, "connect_error"),
        (httpx.ReadError, "read_error"),
        (httpx.WriteError, "write_error"),
        (httpx.RemoteProtocolError, "remote_protocol_error"),
        (httpx.LocalProtocolError, "local_protocol_error"),
    )
    seen = set()
    for _ in range(12):
        if exc is None or id(exc) in seen:
            break
        seen.add(id(exc))
        for kind, label in kinds:
            if isinstance(exc, kind):
                return label
        exc = exc.__cause__ or (None if exc.__suppress_context__ else exc.__context__)
    return "other"


def transport_failure(exc):
    """Classify typed causes only; never parse or expose exception/provider text."""
    seen = set()
    proxy = False
    for _ in range(12):
        if exc is None or id(exc) in seen:
            break
        seen.add(id(exc))
        if isinstance(exc, ssl.SSLCertVerificationError):
            return (
                "tls_certificate_verification_failed",
                "TLS 证书校验失败；请检查证书有效期、信任链及地址与证书名称是否匹配，不能关闭校验",
            )
        if isinstance(exc, httpx.ProxyError):
            proxy = True
        exc = exc.__cause__ or (None if exc.__suppress_context__ else exc.__context__)
    if proxy:
        return (
            "proxy_connection_failed",
            "代理连接或隧道失败；请检查代理访问策略。这不能证明目标服务证书或 API Key 无效",
        )
    return None


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
    | {"json_syntax", "json_encoding", "invalid_json", "extra_closing_delimiters"}
)


def json_failure_facts(details):
    """Project the single JSON diagnostic into bounded, text-free receipt facts."""
    if not isinstance(details, list) or len(details) != 1 or not isinstance(details[0], dict):
        return {}
    detail = details[0]
    category = detail.get("category")
    if (
        type(category) is not str
        or category not in JSON_DIAGNOSTIC_CATEGORIES
        or category == "langchain_structured_output_parsing_failed"
    ):
        return {}
    result = {"category": category}
    for group, fields in (
        ("position", {"line": (1, 1), "column": (1, 1), "offset": (0, 0)}),
        ("lengths", {"characters": (0, 0), "bytes": (0, 0)}),
    ):
        source = detail.get(group)
        if not isinstance(source, dict):
            continue
        safe = {}
        for key, (minimum, extra) in fields.items():
            value = source.get(key)
            if type(value) is int and minimum <= value <= MAX_MODEL_CONTENT_BYTES + extra:
                safe[key] = value
        if safe:
            result[group] = safe
    return result


def json_syntax_category(exc):
    category = JSON_SYNTAX_CATEGORIES.get(exc.msg, "json_syntax")
    if category == "extra_data":
        tail = exc.doc[exc.pos :]
        if tail.strip(" \t\r\n") and not set(tail).difference("}] \t\r\n"):
            return "extra_closing_delimiters"
    return category


def failure_diagnostic(code, *, trace_id, attempt=None, details=None):
    phase = "response_validation"
    summary = "模型响应未通过结构校验，未生成可批准结果。"
    hint = "按字段路径与约束提示检查该阶段的模型和规划契约，再重试当前运行；JSON 对象模式不保证符合 Schema。无需重填已提交的回答。"
    if code.startswith("http_") or code in {
        "transport_error",
        "tls_certificate_verification_failed",
        "proxy_connection_failed",
    }:
        phase = "provider_request"
        summary = "模型请求失败，尚未取得有效响应。"
        hint = "先在模型与配置中测试该阶段连接，检查网络、服务额度与模型权限，再重试当前运行。"
        if code in {"http_401", "http_403"}:
            hint = "检查该阶段的密钥与模型访问权限，保存后测试连接；不要把密钥放入对话。"
        elif code == "http_429":
            hint = "检查服务商额度或限流状态，稍后手动重试当前运行。"
        elif code == "tls_certificate_verification_failed":
            hint = "检查证书有效期、信任链及地址与证书名称是否匹配；不能关闭校验。修复后测试连接，再手动重试当前运行。"
        elif code == "proxy_connection_failed":
            hint = "检查代理访问策略和隧道连接；该错误不能证明目标服务证书或 API Key 无效。修复后测试连接，再手动重试当前运行。"
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
    elif code in {
        "native_scope_rejected",
        "native_sdk_unsupported",
        "native_request_mismatch",
        "native_format_rejected",
    }:
        phase = "provider_request"
        summary = "原生 strict 兼容性或请求契约检查失败，已停止。"
        hint = "检查批准范围、锁定 SDK 和服务格式支持；不自动降级格式或新增兼容性重试。"
    elif code == "native_schema_violation":
        summary = "响应违反所请求的原生 strict Schema，已停止。"
        hint = "保留客户端及业务守卫；HTTP 成功状态不能证明服务端强制执行了 strict。"
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
        category = json_syntax_category(exc)
        correction = (
            "第一个 JSON 值之后只剩多余的闭合括号和 JSON 空白。"
            "逐层核对括号，根对象只闭合一次；用缩进和换行标明层级。"
            "若提供未批准的修复候选，仍须核对原始需求、全部业务字段与 Schema，重新返回完整合法对象。"
            if category == "extra_closing_delimiters"
            else "解析器已读完第一个 JSON 值，此位置起仍有额外内容。"
            "若根对象提前闭合，剩余字段必须放回同一根对象的最后一个 } 之前；"
            "不要在对象外追加字段、第二个对象或说明。"
            "根据原始需求和 Schema 重写整个对象，保留全部业务字段，不能只返回尾部补丁或截掉内容。"
            if category == "extra_data"
            else "返回一个完整对象，正确转义字符串并闭合括号，不要附加 Markdown 围栏或说明文字。"
        )
        return [
            {
                "type": "json_syntax",
                "category": category,
                "path": [],
                "position": {"line": exc.lineno, "column": exc.colno, "offset": exc.pos},
                "lengths": lengths,
                "message": f"JSON 解析器报告 {category}，位于第 {exc.lineno} 行、第 {exc.colno} 列，"
                f"字符偏移 {exc.pos}（从 0 开始），全文 {len(exc.doc)} 个字符；" + correction,
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

    errors = exc.errors(include_input=False, include_url=False)
    # Pydantic inserts schema-owned union branch names into locations. They are
    # not JSON object fields; remove only known definitions, never input text.
    definitions = set(document.get("$defs", {})) - allowed
    for error in errors:
        error["loc"] = tuple(part for part in error["loc"] if part not in definitions)
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
        for error in errors[:30]
    ]
````
