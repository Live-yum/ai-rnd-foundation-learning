# scripts/ci_real_model.py · 1/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](scripts__ci_real_model_py--002.md)

**作用：显式授权的真实模型完整验收。** 可信客服分支的手动任务在rnd中将APK_KEY映射为API_KEY，三个模板各自先Hello再校验同提交同attempt回执。完整需求由原文、默认决策和命名约定构成；真实网页只一次初始智能推荐，随后必须READY、实际下载、新库HTTP/浏览器/重启；公开白名单状态及经过校验的合成页面截图，不输出密钥或模型原文。

**对应关系：** native-probe手动real_model=true+expected_sha，或real-model手动矩阵 → rnd job → ModelGateway真实请求 → 当前模板独立产品 → summary.json与合成PNG；工具矩阵和BLOCKED恢复另验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `SafeFailure`（L54–L59）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `SafeFailure.__init__`（L57–L59）：接收`code`、`status`、`details`。 调用`super().__init__`、`super`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Config`（L63–L66）：继承`object`。声明的数据项为`base_url`、`model`、`key`；类型约束/数据库列参数以完整定义为准。
- `configuration`（L69–L91）：接收`env`。 控制顺序：L82遍历`names`；L83按`not isinstance(raw[name], str)`分支；L84抛异常，停止当前正常路径；L85按`not values[name]`分支；L86抛异常，停止当前正常路径；L87按`not checks["BASE_URL_matches_authorized_destination"]`分支；L88抛异常，停止当前正常路径；L89按`not checks["MODE_matches_authorized_model"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`env.get`、`isinstance`、`value.strip`、`raw.items`、`bool`、`values["BASE_URL"].rstrip`、`SafeFailure`、`Config`、`SecretStr`。 返回路径：L91的`Config(values["BASE_URL"].rstrip("/"), values["MODE"], SecretStr(values["API_KEY"]))`。
- `trusted_dispatch`（L94–L101）：接收`env`。 控制顺序：L95按`env.get("GITHUB_ACTIONS") != "true" or env.get("GITHUB_EVENT_NAME") != "workflow_disp…`分支；L101抛异常，停止当前正常路径。 调用`env.get`、`SafeFailure`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedRealTransport`（L104–L180）：继承`httpx.BaseTransport`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `BoundedRealTransport.__init__`（L107–L115）：接收`config`。 调用`httpx.HTTPTransport`、`DiagnosticTextBudget`、`config.key.get_secret_value`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedRealTransport.handle_request`（L117–L173）：接收`request`。 控制顺序：L118按`request.method != "POST" or str(request.url) != self.config.base_url + "/chat/complet…`分支；L123抛异常，停止当前正常路径；L125按`body.get("model") != self.config.model`分支；L126抛异常，停止当前正常路径；L127按`self.current_schema is not None and body.get("response_format") != { "type": "json_ob…`分支；L130抛异常，停止当前正常路径；L131按`not hmac.compare_digest( request.headers.get("Authorization", ""), "Bearer " + self.c…`分支；L135抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`str`、`SafeFailure`、`json.loads`、`request.read`、`body.get`、`hmac.compare_digest`、`request.headers.get`、`self.config.key.get_secret_value`、`min`等。 返回路径：L171的`httpx.Response( response.status_code, headers=response_headers, content=bytes(body_bytes) …`。
- `BoundedRealTransport.close`（L175–L177）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `BoundedRealTransport.shutdown`（L179–L180）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.transport.close`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `response_receipt`（L183–L275）：接收`status`、`data`、`stage`、`schema`、`text_budget`。 控制顺序：L198按`not isinstance(envelope, dict)`分支；L199抛异常，停止当前正常路径；L201按`not isinstance(choice, dict) or not isinstance(choice.get("message"), dict)`分支；L202抛异常，停止当前正常路径；L218按`schema is not None`分支；L222按`status != 200`分支；L223抛异常，停止当前正常路径；L273按`schema is not None`分支。 调用`DiagnosticTextBudget`、`load_json`、`isinstance`、`TypeError`、`choice.get`、`choice["message"].get`、`bool`、`content.strip`、`envelope.get`等。 返回路径：L275的`receipt`。
- `response_receipt.visit`（L237–L244）：接收`node`。 控制顺序：L238按`isinstance(node, dict)`分支；L240遍历`node.values()`；L242按`isinstance(node, list)`分支；L243遍历`node`。 调用`isinstance`、`names.update`、`node.get`、`node.values`、`visit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DiagnosticTextBudget`（L278–L324）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `DiagnosticTextBudget.__init__`（L281–L283）：接收`secrets`、`limit`。 调用`tuple`、`isinstance`、`min`、`max`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `DiagnosticTextBudget.scrub`（L285–L312）：接收`text`。 源码说明：Scrub complete selected strings before any truncation or persistence.。 控制顺序：L289遍历`sorted(self.secrets, key=len, reverse=True)`。 调用`sorted`、`text.replace`、`re.sub`。 返回路径：L312的`re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)`。
- `DiagnosticTextBudget.excerpt`（L314–L321）：接收`value`。 控制顺序：L315按`not isinstance(value, str) or not self.remaining`分支。 调用`isinstance`、`self.scrub`、`min`、`len`。 返回路径：L316的`""`；L321的`text`。
- `DiagnosticTextBudget.excerpts`（L323–L324）：接收`values`。 调用`self.excerpt`。 返回路径：L324的`[text for value in values[:20] if (text := self.excerpt(value))]`。
- `safe_execution_failure`（L327–L381）：接收`error`、`stage`、`text_budget`。 源码说明：Selected exception headline and frame coordinates, never raw logs/locals.。 控制顺序：L349按`len(headline) > 4096 or headline.lstrip().startswith(("{", "["))`分支；L351按`re.search(r"[\[{]", headline)`分支；L360遍历`traceback.extract_tb(error.__traceback__)[-8:]`。 调用`str`、`message.splitlines`、`len`、`headline.lstrip().startswith`、`headline.lstrip`、`re.search`、`re.split`、`re.sub`、`traceback.extract_tb`等。 返回路径：L376的`{ "stage": stage if stage in stages else "unknown", "exception_type": text_budget.excerpt(…`。
- `completed_stage_details`（L384–L394）：接收`value`、`text_budget`。 源码说明：Keep schema counts and selected review gaps, not complete model responses.。 控制顺序：L387遍历`("questions", "unsupported", "uncovered_requirements", "field_req…`；L388按`hasattr(value, name)`分支；L390按`hasattr(value, "uncovered_requirements")`分支。 调用`hasattr`、`len`、`getattr`、`text_budget.excerpts`。 返回路径：L394的`result`。
- `contract_snapshot`（L397–L429）：接收`data`、`requirement`。 控制顺序：L421按`requirement`分支。 调用`field_summary`、`data.get`、`identifier`、`e.get`。 返回路径：L422的`[field_summary(f) for f in data.get("field_requirements", [])[:128]]`；L423的`[ { "name": identifier(e.get("name")), "fields": [field_summary(f) for f in e.get("fields"…`。
- `contract_snapshot.identifier`（L398–L403）：接收`value`。 调用`isinstance`、`re.fullmatch`。 返回路径：L399的`value if isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", value) else "unr…`。
- `contract_snapshot.field_summary`（L405–L419）：接收`value`。 控制顺序：L407按`requirement`分支；L409遍历`("required", "searchable", "filterable", "date_range")`；L410按`type(value.get(name)) is bool`分支；L412遍历`("min_length", "max_length")`；L413按`type(value.get(name)) is int and 0 <= value[name] <= 20000`分支；L415按`value.get("kind") in {"text", "integer", "boolean", "date", "datetime", "enum"}`分支；L417按`isinstance(value.get("choices"), list)`分支。 调用`identifier`、`value.get`、`type`、`isinstance`、`len`。 返回路径：L419的`result`。
- `safe_coverage_details`（L465–L532）：接收`requirement`、`plan`、`text_budget`。 源码说明：Export executable differences and source references, never requirement prose.。 控制顺序：L509遍历`items[:128]`；L514遍历`("expected", "actual")`；L516按`attribute == "choices" and isinstance(value, list)`分支；L522按`text_budget is not None and type(source.get("index")) is int and 0 <= source["index"]…`分支；L529按`excerpt`分支。 调用`requirement.get`、`list`、`_fact_texts`、`coverage_gaps`、`Requirement.model_validate`、`Plan.model_validate`、`isinstance`、`len`、`scalar`等。 返回路径：L532的`result`。
- `safe_coverage_details.scalar`（L480–L506）：接收`attribute`、`value`。 控制顺序：L481按`attribute in {"fields", "entities"} and isinstance(value, list) and len(value) <= 128`分支；L482按`all( isinstance(item, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", item) for item i…`分支；L488按`type(value) is bool or value is None`分支；L490按`attribute in {"min_length", "max_length"} and type(value) is int and 0 <= value <= 20…`分支；L492按`attribute == "kind" and isinstance(value, str) and value in { "text", "integer", "boo…`分支。 调用`isinstance`、`len`、`all`、`re.fullmatch`、`text_budget.scrub`、`type`。 返回路径：L486的`[text_budget.scrub(item) if text_budget else item for item in value]`；L487的`"not_exported"`；L489的`value`。
- `safe_native_plan_details`（L535–L560）：接收`plan`。 源码说明：Report the actual native-validator failure plus label-shape evidence.。 调用`Plan.model_validate`、`validate_plan`、`DESIGN_REASON_CODES.get`、`str`、`len`、`any`、`bool`、`re.fullmatch`。 返回路径：L546的`{ "code": code, "entity_labels": [ { "entity": entity.name, "length": len(entity.descripti…`。
- `safe_analysis_conflict_details`（L563–L651）：接收`items`、`text_budget`。 源码说明：Retain bounded atomic conflicts even when analysis never produced a Plan.。 控制顺序：L565按`not isinstance(items, list)`分支；L592遍历`items[:20]`；L593按`not isinstance(item, dict) or item.get("code") != "requirement_source_conflict" or no…`分支；L612遍历`item["sources"][:8]`；L613按`not isinstance(source, dict) or not isinstance(source.get("source"), dict)`分支；L616按`not isinstance(ref.get("section"), str) or ref.get("section") not in sections or not …`分支；L631按`attribute == "choices" and isinstance(value, list)`分支；L633按`value is None or type(value) is bool or attribute in {"min_length", "max_length"} and…`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`item.get`、`target.get`、`identifier`、`source.get`、`ref.get`、`position`、`min`、`len`等。 返回路径：L566的`[]`；L651的`result`。
- `safe_analysis_conflict_details.identifier`（L579–L586）：接收`value`。 调用`isinstance`、`re.fullmatch`、`text_budget.scrub`。 返回路径：L580的`value if isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", value) and text_…`。
- `safe_analysis_conflict_details.position`（L588–L589）：接收`value`。 调用`type`。 返回路径：L589的`type(value) is int and 0 <= value <= 100_000`。
- `safe_runtime_details`（L676–L728）：接收`error`、`native_reports`、`text_budget`。 源码说明：Select the runtime error, finite stage and one native exception headline. Never export native logs, environment, response bodies or tracebacks. These fixed local reports are read before the isolated w。 控制顺序：L685按`excerpt := text_budget.excerpt(error)`分支；L687按`native_reports is None`分支；L690按`any(path.is_symlink() for path in (reports, *reports.parents))`分支；L694按`not progress.is_symlink() and progress.is_file() and progress.stat().st_size <= 4096`分支；L696按`isinstance(value, dict)`分支；L697按`value.get("stage") in NATIVE_PROGRESS_STAGES`分支；L699按`value.get("template") in {"fastapiadmin", "yudao-vben"}`分支；L705按`failure.is_symlink() or not failure.is_file()`分支。后续分支沿下方源码相同行号继续阅读。 调用`text_budget.excerpt`、`Path`、`any`、`path.is_symlink`、`progress.is_symlink`、`progress.is_file`、`progress.stat`、`json.loads`、`progress.read_text`等。 返回路径：L688的`result`；L691的`result`；L706的`result`。
- `approved_plan_artifact_directory`（L734–L743）：接收`data_dir`、`run_id`、`template`。 源码说明：Select only a registered generated approval artifact, never a revision.。 控制顺序：L736按`template not in {"python-basic", "fastapiadmin", "yudao-vben"} or not isinstance(run_…`分支。 调用`isinstance`、`re.fullmatch`、`Path`。 返回路径：L741的`None`；L743的`Path(data_dir) / "runs" / run_id / leaf`。
- `preserve_approved_customer_plan`（L746–L818）：接收`native_reports`、`destination`、`text_budget`。 源码说明：Retain only a validated, credential-free, synthetic approved Plan. The Python generator and native_lab write approved-spec.json only after the design approval gate. Reject rather than alter credential。 控制顺序：L757按`native_reports is None`分支；L761按`any( path.is_symlink() for path in (source, *source.parents, destination, *destinatio…`分支；L766按`not source.is_file()`分支；L768按`source.stat().st_size > MAX_REPLAY_PLAN_BYTES`分支；L771按`len(raw) > MAX_REPLAY_PLAN_BYTES`分支；L774按`{entity.name for entity in plan.entities} != {"customers", "requests", "tasks"} or no…`分支；L794按`not credential_free(normalized)`分支；L799按`text_budget.scrub(rendered) != rendered`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`any`、`path.is_symlink`、`source.is_file`、`source.stat`、`source.read_bytes`、`len`、`Plan.model_validate_json`、`plan.model_dump`等。 返回路径：L758的`{"status": "unavailable"}`；L764的`{"status": "unsafe_path"}`；L767的`{"status": "unavailable"}`。
- `preserve_approved_customer_plan.credential_free`（L783–L792）：接收`value`。 控制顺序：L784按`isinstance(value, str)`分支；L786按`isinstance(value, list)`分支；L788按`isinstance(value, dict)`分支。 调用`isinstance`、`text_budget.scrub`、`all`、`credential_free`、`value.items`。 返回路径：L785的`text_budget.scrub(value) == value`；L787的`all(credential_free(item) for item in value)`；L789的`all( credential_free(key) and credential_free(item) for key, item in value.items() )`。

</details>

**创建路径：** `scripts/ci_real_model.py`；**本文件共有 3 段**。本段覆盖源文件 L1–L820。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`33751`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_real_model.py", "part": 1, "parts": 3, "encoding": "utf-8", "sha256": "acc822d0fd67bda168ad33fd57f7c6acbabfe10d550f7cd3ec9df7a497fd6e2d"} -->
````python
# scripts/ci_real_model.py
"""Opt-in real provider acceptance; only allowlisted evidence leaves the isolated job.

No model fixtures, provider substitutions, secret discovery, or automatic scheduling.
Generated source, databases and raw logs are never artifacts. A bounded, validated,
secret-scanned approved customer Plan can be retained for deterministic replay.
Failure-only normalized Requirement/candidate Plan envelopes are diagnostics,
explicitly unapproved and unusable as generation inputs.
"""

import contextlib
import hashlib
import hmac
import json
import logging
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from pydantic import SecretStr

REPOSITORY = "Live-yum/ai-rnd-foundation-learning"
REFS = {
    "refs/heads/main",
    "refs/heads/feat/complete-platform-acceptance",
    "refs/heads/feat/real-model-acceptance",
    "refs/heads/feat/customer-service-acceptance",
}
ENDPOINT = "https://api.deepseek.com"
MODEL = "deepseek-flash"
MAX_WORKFLOW_CALLS = 16
# DeepSeek thinking defaults to 64K; 16K truncated complete customer plans.
# Keep finite call/byte limits and preserve the separate exact smoke request.
MAX_COMPLETION_TOKENS = 65536
SMOKE_PAYLOAD = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
    ],
    "thinking": {"type": "enabled"},
    "reasoning_effort": "high",
    "stream": False,
}


class SafeFailure(RuntimeError):
    """Only a code chosen by this harness and numeric HTTP status can be published."""

    def __init__(self, code, status=None, details=None):
        self.code, self.status, self.details = code, status, details
        super().__init__(code)


@dataclass(frozen=True)
class Config:
    base_url: str
    model: str
    key: SecretStr = field(repr=False)


def configuration(env):
    # Presence/match booleans distinguish missing injection from provider errors;
    # no credential value, length, fragment, hash, or raw configuration is exposed.
    names = ("BASE_URL", "MODE", "API_KEY")
    raw = {name: env.get(name, "") for name in names}
    values = {name: value.strip() if isinstance(value, str) else "" for name, value in raw.items()}
    checks = {
        "BASE_URL_present": bool(values["BASE_URL"]),
        "MODE_present": bool(values["MODE"]),
        "API_KEY_present": bool(values["API_KEY"]),
        "BASE_URL_matches_authorized_destination": values["BASE_URL"].rstrip("/") == ENDPOINT,
        "MODE_matches_authorized_model": values["MODE"] == MODEL,
    }
    for name in names:
        if not isinstance(raw[name], str):
            raise SafeFailure("invalid_configuration_type_" + name, details=checks)
        if not values[name]:
            raise SafeFailure("missing_configuration_" + name, details=checks)
    if not checks["BASE_URL_matches_authorized_destination"]:
        raise SafeFailure("configuration_destination_mismatch", details=checks)
    if not checks["MODE_matches_authorized_model"]:
        raise SafeFailure("configuration_model_mismatch", details=checks)
    return Config(values["BASE_URL"].rstrip("/"), values["MODE"], SecretStr(values["API_KEY"]))


def trusted_dispatch(env):
    if (
        env.get("GITHUB_ACTIONS") != "true"
        or env.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
        or env.get("GITHUB_REPOSITORY") != REPOSITORY
        or env.get("GITHUB_REF") not in REFS
    ):
        raise SafeFailure("untrusted_dispatch")


class BoundedRealTransport(httpx.BaseTransport):
    """Real HTTPS transport with one authorized destination and a hard call/token budget."""

    def __init__(self, config):
        self.config = config
        self.transport = httpx.HTTPTransport(retries=0)
        self.statuses = []
        self.calls = 0
        self.receipts = []
        self.current_schema = None
        self.current_stage = "smoke"
        self.diagnostic_text = DiagnosticTextBudget(secrets=(config.key.get_secret_value(),))

    def handle_request(self, request):
        if (
            request.method != "POST"
            or str(request.url) != self.config.base_url + "/chat/completions"
            or self.calls >= MAX_WORKFLOW_CALLS + 1
        ):
            raise SafeFailure("request_scope_or_budget")
        body = json.loads(request.read())
        if body.get("model") != self.config.model:
            raise SafeFailure("model_substitution_rejected")
        if self.current_schema is not None and body.get("response_format") != {
            "type": "json_object"
        }:
            raise SafeFailure("workflow_json_mode_required")
        if not hmac.compare_digest(
            request.headers.get("Authorization", ""),
            "Bearer " + self.config.key.get_secret_value(),
        ):
            raise SafeFailure("unexpected_authorization_header")
        # Preserve the user's exact compatibility smoke payload, including reasoning flags.
        # Token budgeting applies only to the subsequent schema-driven acceptance workflow.
        if body != SMOKE_PAYLOAD:
            body["max_tokens"] = min(
                body.get("max_tokens", MAX_COMPLETION_TOKENS), MAX_COMPLETION_TOKENS
            )
        headers = dict(request.headers)
        headers.pop("content-length", None)
        bounded = httpx.Request(
            "POST", request.url, headers=headers, json=body, extensions=request.extensions
        )
        self.calls += 1
        response = self.transport.handle_request(bounded)
        self.statuses.append(response.status_code)
        body_bytes = bytearray()
        for chunk in response.iter_bytes():
            body_bytes.extend(chunk)
            if len(body_bytes) > 2_000_000:
                response.close()
                raise SafeFailure("provider_response_too_large", response.status_code)
        response.close()
        receipt = response_receipt(
            response.status_code,
            bytes(body_bytes),
            self.current_stage,
            self.current_schema,
            text_budget=self.diagnostic_text,
        )
        receipt["requested_output_mode"] = (
            "json_object" if self.current_schema is not None else "transport_smoke"
        )
        self.receipts.append(receipt)
        response_headers = dict(response.headers)
        response_headers.pop("content-encoding", None)
        response_headers.pop("content-length", None)
        return httpx.Response(
            response.status_code, headers=response_headers, content=bytes(body_bytes)
        )

    def close(self):
        # ModelGateway creates a Client per attempt; the owning harness closes the pool.
        pass

    def shutdown(self):
        self.transport.close()


def response_receipt(status, data, stage, schema=None, *, text_budget=None):
    from pydantic import ValidationError

    from workbench.model_protocol import (
        OutputContract,
        OutputFailure,
        completion_content,
        load_json,
        validate_content,
    )

    receipt = {"http_status": status, "stage": stage}
    text_budget = text_budget or DiagnosticTextBudget()
    try:
        envelope = load_json(data)
        if not isinstance(envelope, dict):
            raise TypeError("invalid envelope")
        choice = envelope["choices"][0]
        if not isinstance(choice, dict) or not isinstance(choice.get("message"), dict):
            raise TypeError("invalid message")
        reason = choice.get("finish_reason")
        receipt["finish_reason"] = (
            reason if reason in {"stop", "length", "content_filter", "tool_calls"} else "unknown"
        )
        content = choice["message"].get("content")
        receipt["content_present"] = isinstance(content, str) and bool(content.strip())
        receipt["reasoning_present"] = bool(choice["message"].get("reasoning_content"))
        usage = envelope.get("usage")
        receipt["usage"] = {
            key: value
            for key, value in (usage if isinstance(usage, dict) else {}).items()
            if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
            and type(value) is int
            and 0 <= value <= 100_000_000
        }
        if schema is not None:
            try:
                contract = OutputContract("deepseek", "json_object", "provider_json_mode", {})
                content, _, _ = completion_content(envelope, contract)
                if status != 200:
                    raise OutputFailure("http_error", "HTTP status rejected")
                validate_content(content, schema, mode=contract.mode)
                receipt["schema_valid"] = True
                receipt.update(contract.receipt())
            except OutputFailure as exc:
                receipt["schema_valid"] = False
                receipt["response_contract_error"] = exc.code
            except ValidationError as exc:
                receipt["schema_valid"] = False
                # Pydantic error types are library-defined codes, never model text or inputs.
                errors = exc.errors(include_input=False, include_url=False)
                receipt["schema_error_types"] = sorted({e["type"] for e in errors})
                names = set()

                def visit(node):
                    if isinstance(node, dict):
                        names.update(node.get("properties", {}))
                        for value in node.values():
                            visit(value)
                    elif isinstance(node, list):
                        for value in node:
                            visit(value)

                visit(schema.model_json_schema())
                receipt["schema_errors"] = [
                    {
                        "type": e["type"],
                        "message": text_budget.excerpt(e.get("msg", "")),
                        "field_path": [
                            part if type(part) is int or part in names else "additional_field"
                            for part in e["loc"]
                        ],
                    }
                    for e in errors[:20]
                ]
            except ValueError as exc:
                receipt["schema_valid"] = False
                code = str(exc)
                receipt["schema_error_types"] = [
                    code
                    if code
                    in {
                        "duplicate_json_key",
                        "non_finite_json_number",
                        "response_must_be_json_object",
                    }
                    else "json_invalid"
                ]
    except ValueError, KeyError, IndexError, TypeError:
        receipt["response_envelope_valid"] = False
        if schema is not None:
            receipt["schema_valid"] = False
    return receipt


class DiagnosticTextBudget:
    """Bounded, selected validation wording, never full provider payloads/logs."""

    def __init__(self, secrets=(), limit=6000):
        self.secrets = tuple(secret for secret in secrets if isinstance(secret, str) and secret)
        self.remaining = min(max(limit, 0), 6000)

    def scrub(self, text):
        """Scrub complete selected strings before any truncation or persistence."""
        # Replace exact credentials before truncation so a boundary cannot leak
        # a credential fragment. The caller supplies only the authorized key.
        for secret in sorted(self.secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(
            r"(?im)\b(?:authorization|proxy-authorization|cookie|set-cookie|x-api-key)[\"']?\s*:.*$",
            "[REDACTED HEADER]",
            text,
        )
        text = re.sub(
            r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/@]+(?::[^\s/@]*)?@",
            "[REDACTED URL CREDENTIALS]@",
            text,
        )
        text = re.sub(
            r"(?i)(?:\b(?:[a-z][a-z0-9]*[_-])*(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|passwd|secret|credential|authorization|token)\b|密码|口令|密钥|令牌)[\"']?\s*[:：=]\s*[^\r\n]*",
            "[REDACTED CREDENTIAL]",
            text,
        )
        text = re.sub(r"(?i)\bbearer\s+[^\s,;]+", "[REDACTED TOKEN]", text)
        text = re.sub(
            r"\b(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|github_pat_[A-Za-z0-9_]{8,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b",
            "[REDACTED TOKEN]",
            text,
        )
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    def excerpt(self, value):
        if not isinstance(value, str) or not self.remaining:
            return ""
        text = self.scrub(value)
        limit = min(600, self.remaining)
        text = text[:limit]
        self.remaining -= len(text)
        return text

    def excerpts(self, values):
        return [text for value in values[:20] if (text := self.excerpt(value))]


def safe_execution_failure(error, stage, text_budget):
    """Selected exception headline and frame coordinates, never raw logs/locals."""
    stages = {
        "configuration",
        "smoke",
        "workflow",
        "platform_start",
        "smart_delivery_browser",
        "delivery_receipt",
        "download_unpack",
        "approved_contract",
        "downloaded_python_runtime",
        "downloaded_native_runtime",
        "screenshot_export",
        "complete",
    }
    try:
        message = str(error)
    except Exception:
        message = "Exception text unavailable"
    headline = message.splitlines()[0] if message else ""
    # Long exception strings often embed tool/provider output. Do not retain it.
    if len(headline) > 4096 or headline.lstrip().startswith(("{", "[")):
        headline = "Oversized exception headline omitted"
    elif re.search(r"[\[{]", headline):
        # An exception may prefix a complete JSON/tool payload with a sentence.
        # Retain only that sentence, not any structured payload or later values.
        headline = re.split(r"[\[{]", headline, maxsplit=1)[0] + "[structured payload omitted]"
    headline = re.sub(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s]+", "[URL REDACTED]", headline)
    headline = re.sub(
        r"(?:/(?:tmp|home|workspace|Users)/|[A-Za-z]:[\\/])[^\s,;]+", "[PATH]", headline
    )
    frames = []
    for frame in traceback.extract_tb(error.__traceback__)[-8:]:
        filename = Path(frame.filename).name
        function = frame.name
        frames.append(
            {
                "file": filename
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]{0,99}", filename)
                and text_budget.scrub(filename) == filename
                else "unavailable",
                "function": function
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,99}|<module>", function)
                and text_budget.scrub(function) == function
                else "unavailable",
                "line": min(max(frame.lineno, 0), 1_000_000),
            }
        )
    return {
        "stage": stage if stage in stages else "unknown",
        "exception_type": text_budget.excerpt(type(error).__name__),
        "message_excerpt": text_budget.excerpt(headline),
        "frames": frames,
    }


def completed_stage_details(value, text_budget):
    """Keep schema counts and selected review gaps, not complete model responses."""
    result = {"completed": True}
    for name in ("questions", "unsupported", "uncovered_requirements", "field_requirements"):
        if hasattr(value, name):
            result[name + "_count"] = len(getattr(value, name))
    if hasattr(value, "uncovered_requirements"):
        result["uncovered_requirement_excerpts"] = text_budget.excerpts(
            value.uncovered_requirements
        )
    return result


def contract_snapshot(data, requirement=False):
    def identifier(value):
        return (
            value
            if isinstance(value, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", value)
            else "unrecognized"
        )

    def field_summary(value):
        result = {"name": identifier(value.get("field" if requirement else "name"))}
        if requirement:
            result["entity"] = identifier(value.get("entity")) if value.get("entity") else None
        for name in ("required", "searchable", "filterable", "date_range"):
            if type(value.get(name)) is bool:
                result[name] = value[name]
        for name in ("min_length", "max_length"):
            if type(value.get(name)) is int and 0 <= value[name] <= 20000:
                result[name] = value[name]
        if value.get("kind") in {"text", "integer", "boolean", "date", "datetime", "enum"}:
            result["kind"] = value["kind"]
        if isinstance(value.get("choices"), list):
            result["choices_count"] = len(value["choices"])
        return result

    if requirement:
        return [field_summary(f) for f in data.get("field_requirements", [])[:128]]
    return [
        {
            "name": identifier(e.get("name")),
            "fields": [field_summary(f) for f in e.get("fields", [])],
        }
        for e in data.get("entities", [])[:8]
    ]


# Exact validator messages map to finite evidence codes. Never publish exception
# text: prerequisite errors can contain paths, environment values or model prose.
DESIGN_REASON_CODES = {
    "设计改变了已批准的数据归属，必须修改后重新批准": "data_scope",
    "设计使用了当前模板不支持的字段类型": "unsupported_field_kind",
    "共享业务必须有完整关系、角色和动作的 business 契约": "business_contract_required",
    "当前配置已禁用规则编码器": "coding_disabled",
    "原生业务规则需要 CODING_ENGINE=aider；CRUD仍由原生生成器完成": "native_coding_engine",
    "Native runtime does not accept unsupported requirements": "native_unsupported",
    "每个原生实体只能有一个合并后的业务规则及完整正反例": "native_duplicate_rules",
    "Native field uses a reserved runtime name": "native_reserved_runtime_field",
    "Native runtime currently requires explicitly approved shared data with role permissions": "native_data_scope",
    "Native normalized business names collide": "native_entity_collision",
    "Native enum/date/datetime fields require a business contract": "native_business_field_kind",
    "Native pattern constraints require a reviewed cross-language regex adapter": "native_pattern_unsupported",
    "Native numeric bounds require a business contract": "native_numeric_bounds_unsupported",
    "Native adapters do not yet execute searchable/filterable/date_range/min_length; "
    "use a supported template or explicitly revise the requirement": "native_unsupported_field_option",
    "Native runtime requires a required text field in each entity for independent UI acceptance": "native_required_text",
    "Native entity identifiers must be lowercase and at most 20 characters": "native_entity_identifier",
    "Native labels cannot contain code delimiters or multiline text": "native_label_contract",
    "Field conflicts with native framework audit columns": "native_reserved_audit_field",
    "先执行 rnd native runtime-config TEMPLATE 并授权专用空开发库": "native_runtime_config_missing",
    "原生数据库只能读取明确的 NATIVE_* 环境变量": "native_database_env_name",
    "请明确批准仅在自己创建的专用空数据库初始化原生框架": "native_database_not_authorized",
    "原生数据库环境变量未设置": "native_database_env_missing",
    "Native runtime requires a loopback PostgreSQL database": "native_database_not_loopback_postgres",
    "Use a dedicated lowercase database identifier ending in _codegen": "native_database_identifier",
    "本机Daytona需要 DAYTONA_ALLOW_LOCAL_EXECUTION=true；只在本机创建隔离验证环境": "sandbox_not_authorized",
    "请配置当前技术栈的离线DAYTONA_SNAPSHOT或DAYTONA_SNAPSHOTS映射": "sandbox_snapshot_missing",
}


def safe_coverage_details(requirement, plan, *, text_budget=None):
    """Export executable differences and source references, never requirement prose."""
    from workbench.domain import Plan, Requirement
    from workbench.requirement_coverage import _fact_texts, coverage_gaps

    source_texts = {
        "features": requirement.get("features", []),
        "acceptance": requirement.get("acceptance", []),
        "facts": list(_fact_texts(requirement.get("facts", {}))),
    }
    items = []
    coverage_gaps(
        Requirement.model_validate(requirement), Plan.model_validate(plan), diagnostics=items
    )

    def scalar(attribute, value):
        if attribute in {"fields", "entities"} and isinstance(value, list) and len(value) <= 128:
            if all(
                isinstance(item, str) and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", item)
                for item in value
            ):
                return [text_budget.scrub(item) if text_budget else item for item in value]
            return "not_exported"
        if type(value) is bool or value is None:
            return value
        if attribute in {"min_length", "max_length"} and type(value) is int and 0 <= value <= 20000:
            return value
        if (
            attribute == "kind"
            and isinstance(value, str)
            and value
            in {
                "text",
                "integer",
                "boolean",
                "date",
                "datetime",
                "enum",
            }
        ):
            return value
        return "not_exported"

    result = []
    for item in items[:128]:
        entry = {
            key: item[key] for key in ("code", "source", "source_markers", "targets", "attribute")
        }
        attribute = item["attribute"]
        for key in ("expected", "actual"):
            value = item[key]
            if attribute == "choices" and isinstance(value, list):
                entry[key + "_count"] = len(value)
            else:
                entry[key] = scalar(attribute, value)
        source = item["source"]
        texts = source_texts.get(source["section"], [])
        if (
            text_budget is not None
            and type(source.get("index")) is int
            and 0 <= source["index"] < len(texts)
            and (source["section"] != "facts" or source.get("encoding") == "legacy")
        ):
            excerpt = text_budget.excerpt(texts[source["index"]])
            if excerpt:
                entry["source_excerpt"] = excerpt
        result.append(entry)
    return result


def safe_native_plan_details(plan):
    """Report the actual native-validator failure plus label-shape evidence."""
    from workbench.domain import Plan
    from workbench.native_modules import validate_plan

    value = Plan.model_validate(plan)
    try:
        validate_plan(value)
        code = "valid"
    except ValueError as exc:
        code = DESIGN_REASON_CODES.get(str(exc), "unclassified_native_validation")
    return {
        "code": code,
        "entity_labels": [
            {
                "entity": entity.name,
                "length": len(entity.description),
                "single_line": not any(char in entity.description for char in "\r\n\t"),
                "allowed_characters": bool(
                    re.fullmatch(r"[\w\s\-\u4e00-\u9fff]+", entity.description)
                ),
                "valid_length": 1 <= len(entity.description) <= 100,
            }
            for entity in value.entities
        ],
    }


def safe_analysis_conflict_details(items, text_budget):
    """Retain bounded atomic conflicts even when analysis never produced a Plan."""
    if not isinstance(items, list):
        return []
    sections = {"field_requirements", "features", "acceptance", "facts", "user_messages"}
    attributes = {
        "kind",
        "required",
        "searchable",
        "filterable",
        "date_range",
        "min_length",
        "max_length",
        "choices",
    }

    def identifier(value):
        return (
            value
            if isinstance(value, str)
            and re.fullmatch(r"[a-z][a-z0-9_]{0,39}", value)
            and text_budget.scrub(value) == value
            else "unrecognized"
        )

    def position(value):
        return type(value) is int and 0 <= value <= 100_000

    result = []
    for item in items[:20]:
        if (
            not isinstance(item, dict)
            or item.get("code") != "requirement_source_conflict"
            or not isinstance(item.get("attribute"), str)
            or item.get("attribute") not in attributes
            or not isinstance(item.get("target"), dict)
            or not isinstance(item.get("sources"), list)
        ):
            continue
        target = item["target"]
        entry = {
            "code": "requirement_source_conflict",
            "target": {
                "entity": None if target.get("entity") is None else identifier(target["entity"]),
                "field": identifier(target.get("field")),
            },
            "attribute": item["attribute"],
            "sources": [],
        }
        for source in item["sources"][:8]:
            if not isinstance(source, dict) or not isinstance(source.get("source"), dict):
                continue
            ref = source["source"]
            if (
                not isinstance(ref.get("section"), str)
                or ref.get("section") not in sections
                or not position(ref.get("index"))
            ):
                continue
            selected = {
                "source": {"section": ref["section"], "index": ref["index"]},
                "origin": source.get("origin")
                if isinstance(source.get("origin"), str)
                and source.get("origin") in {"previous_requirement", "model_analysis", "user_input"}
                else "not_recorded",
            }
            value = source.get("expected")
            attribute = item["attribute"]
            if attribute == "choices" and isinstance(value, list):
                selected["expected_count"] = min(len(value), 20_000)
            elif (
                value is None
                or type(value) is bool
                or attribute in {"min_length", "max_length"}
                and type(value) is int
                and 0 <= value <= 20_000
                or attribute == "kind"
                and isinstance(value, str)
                and value in {"text", "integer", "boolean", "date", "datetime", "enum"}
            ):
                selected["expected"] = value
            else:
                selected["expected"] = "not_exported"
            excerpt = text_budget.excerpt(source.get("text", source.get("excerpt")))
            if excerpt:
                selected["source_excerpt"] = excerpt
            entry["sources"].append(selected)
        result.append(entry)
    return result


NATIVE_PROGRESS_STAGES = frozenset(
    {
        "bootstrap-empty-database",
        "baseline-install",
        "native-generation",
        "native-business-contract",
        "resume-native-validation",
        "plop-aider-native-business-rules",
        "generated-build",
        "customer-service-http",
        "generated-crud",
        "generated-permissions",
        "native-frontend-build",
        "restart-persistence",
        "native-browser",
        "portable-startup-assets",
        "independent-native-delivery",
        "accepted",
    }
)


def safe_runtime_details(error, native_reports, text_budget):
    """Select the runtime error, finite stage and one native exception headline.

    Never export native logs, environment, response bodies or tracebacks. These
    fixed local reports are read before the isolated work directory is destroyed.
    A headline must match the format written by native_lab; appended tool output
    is deliberately ignored, even when it would explain a subprocess failure.
    """
    result = {}
    if excerpt := text_budget.excerpt(error):
        result["error_excerpt"] = excerpt
    if native_reports is None:
        return result
    reports = Path(native_reports)
    if any(path.is_symlink() for path in (reports, *reports.parents)):
        return result
    progress = reports / "progress.json"
    try:
        if not progress.is_symlink() and progress.is_file() and progress.stat().st_size <= 4096:
            value = json.loads(progress.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                if value.get("stage") in NATIVE_PROGRESS_STAGES:
                    result["native_stage"] = value["stage"]
                if value.get("template") in {"fastapiadmin", "yudao-vben"}:
                    result["native_template"] = value["template"]
    except OSError, ValueError, TypeError:
        pass
    failure = reports / "failure.log"
    try:
        if failure.is_symlink() or not failure.is_file():
            return result
        with failure.open(encoding="utf-8") as source:
            headline = source.readline(65537)
        # Do not truncate prior to secret redaction or publish an arbitrary line.
        if len(headline) > 65536:
            return result
        match = re.fullmatch(
            r"(?P<exception_type>[A-Za-z_][A-Za-z0-9_]{0,79}) at "
            r"(?P<file>[A-Za-z_][A-Za-z0-9_]{0,99}\.py):(?P<line>[0-9]{1,7}) "
            r"\((?P<function>[A-Za-z_][A-Za-z0-9_]{0,99}|<module>)\): (?P<message>[^\r\n]*)\r?\n?",
            headline,
        )
        if match:
            failure_details = {
                key: text_budget.excerpt(match[key])
                for key in ("exception_type", "file", "function")
            }
            failure_details["line"] = int(match["line"])
            failure_details["message_excerpt"] = text_budget.excerpt(match["message"])
            result["native_exception"] = failure_details
    except OSError, ValueError:
        pass
    return result


MAX_REPLAY_PLAN_BYTES = 131072


def approved_plan_artifact_directory(data_dir, run_id, template):
    """Select only a registered generated approval artifact, never a revision."""
    if (
        template not in {"python-basic", "fastapiadmin", "yudao-vben"}
        or not isinstance(run_id, str)
        or not re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", run_id)
    ):
        return None
    leaf = "product" if template == "python-basic" else "native-evidence"
    return Path(data_dir) / "runs" / run_id / leaf


def preserve_approved_customer_plan(native_reports, destination, text_budget):
    """Retain only a validated, credential-free, synthetic approved Plan.

    The Python generator and native_lab write approved-spec.json only after the design approval gate.
    Reject rather than alter credential-bearing contracts: a changed Plan cannot
    truthfully reproduce the failed run. Never fall back to a raw provider reply,
    an unapproved design revision, generated source, a database, or a tool log.
    """
    from workbench.domain import Plan
    from workbench.filesystem import atomic_text

    if native_reports is None:
        return {"status": "unavailable"}
    source = Path(native_reports) / "approved-spec.json"
    destination = Path(destination)
    if any(
        path.is_symlink() for path in (source, *source.parents, destination, *destination.parents)
    ):
        return {"status": "unsafe_path"}
    try:
        if not source.is_file():
            return {"status": "unavailable"}
        if source.stat().st_size > MAX_REPLAY_PLAN_BYTES:
            return {"status": "size_limit"}
        raw = source.read_bytes()
        if len(raw) > MAX_REPLAY_PLAN_BYTES:
            return {"status": "size_limit"}
        plan = Plan.model_validate_json(raw)
        if (
            {entity.name for entity in plan.entities} != {"customers", "requests", "tasks"}
            or not plan.business
            or plan.custom_rules
            or plan.unsupported
        ):
            return {"status": "outside_customer_scope"}
        normalized = plan.model_dump(mode="json")

        def credential_free(value):
            if isinstance(value, str):
                return text_budget.scrub(value) == value
            if isinstance(value, list):
                return all(credential_free(item) for item in value)
            if isinstance(value, dict):
                return all(
                    credential_free(key) and credential_free(item) for key, item in value.items()
                )
            return True

        if not credential_free(normalized):
            return {"status": "secret_scan_rejected"}
        rendered = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
        # Scan structural credential assignments too (e.g. a nested JSON value
        # with a password key), not only individual string values.
        if text_budget.scrub(rendered) != rendered:
            return {"status": "secret_scan_rejected"}
        data = rendered.encode("utf-8")
        if len(data) > MAX_REPLAY_PLAN_BYTES:
            return {"status": "size_limit"}
        # This exact normalized contract regenerates code without paid model calls.
        atomic_text(destination, rendered)
        return {
            "status": "saved",
            "file": "approved-plan-replay.json",
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "exact_normalized_plan": True,
        }
    except FileNotFoundError:
        return {"status": "unavailable"}
    except ValueError:
        return {"status": "invalid_schema"}
    except OSError:
        return {"status": "io_error"}


````
