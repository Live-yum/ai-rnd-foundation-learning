"""Safe actionable provider failures. Never persist provider bodies or input values."""


def failure_diagnostic(code, *, trace_id, attempt=None, details=None):
    phase = "response_validation"
    summary = "模型响应未通过结构校验，未生成可批准结果。"
    hint = "查看字段路径与错误类型；确认模型支持 JSON 结构化输出后，重试当前运行。无需重填已提交的回答。"
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

    collect(schema.model_json_schema())
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
        }
        for error in exc.errors(include_input=False, include_url=False)[:30]
    ]
