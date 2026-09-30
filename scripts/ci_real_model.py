"""Opt-in real provider acceptance; only allowlisted evidence leaves the isolated job.

No model fixtures, provider substitutions, secret discovery, or automatic scheduling.
Generated source, databases and raw logs are never artifacts. A bounded, validated,
secret-scanned approved customer Plan can be retained for deterministic replay.
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
        self.receipts.append(
            response_receipt(
                response.status_code, bytes(body_bytes), self.current_stage, self.current_schema
            )
        )
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


def response_receipt(status, data, stage, schema=None):
    from pydantic import ValidationError

    receipt = {"http_status": status, "stage": stage}
    try:
        envelope = json.loads(data)
        choice = envelope["choices"][0]
        reason = choice.get("finish_reason")
        receipt["finish_reason"] = (
            reason if reason in {"stop", "length", "content_filter", "tool_calls"} else "unknown"
        )
        content = choice["message"].get("content")
        receipt["content_present"] = isinstance(content, str) and bool(content.strip())
        receipt["reasoning_present"] = bool(choice["message"].get("reasoning_content"))
        receipt["usage"] = {
            key: value
            for key, value in envelope.get("usage", {}).items()
            if key in {"prompt_tokens", "completion_tokens", "total_tokens"}
            and type(value) is int
            and 0 <= value <= 100_000_000
        }
        if schema is not None and isinstance(content, str):
            content = content.strip()
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            try:
                schema.model_validate_json(content)
                receipt["schema_valid"] = True
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
                        "field_path": [
                            part if type(part) is int or part in names else "additional_field"
                            for part in e["loc"]
                        ],
                    }
                    for e in errors[:20]
                ]
    except ValueError, KeyError, IndexError, TypeError:
        receipt["response_envelope_valid"] = False
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
            r"(?i)(?:\b(?:api[_ -]?key|access[_ -]?token|refresh[_ -]?token|password|passwd|secret|credential|authorization|token)\b|密码|口令|密钥|令牌)[\"']?\s*[:：=]\s*[^\r\n]*",
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


def preserve_approved_customer_plan(native_reports, destination, text_budget):
    """Retain only a validated, credential-free, synthetic approved Plan.

    native_lab writes approved-spec.json only after the design approval gate.
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


def safe_workflow_details(store, run_id, traces, *, text_budget=None, native_reports=None):
    text_budget = text_budget or DiagnosticTextBudget()
    details = {"model_stages": traces}
    if run_id:
        run = store.get_run(run_id)
        state = run.get("status")
        details["terminal_state"] = (
            state
            if state in {"READY", "SOURCE_READY", "FAILED", "BLOCKED", "PAUSED_LIMIT", "REJECTED"}
            else "not_terminal"
        )
        # Reserve the shared text budget for the actual runtime failure before
        # lower-priority coverage/model wording can exhaust it.
        details["runtime_diagnostics"] = safe_runtime_details(
            run.get("error") or "", native_reports, text_budget
        )
        pending = run.get("pending") or {}
        stage = pending.get("stage")
        details["pending_stage"] = (
            stage if stage in {"clarification", "requirements", "design", "delivery"} else None
        )
        details["model_calls"] = run.get("model_calls", 0)
        requirement = (store.latest_revision(run_id, "requirements") or {}).get("requirement", {})
        plan = (store.latest_revision(run_id, "design") or {}).get("plan", {})
        details["valid_plan_present"] = bool(plan)
        business = plan.get("business") or {}
        details["business_contract_present"] = bool(business)
        details["business_counts"] = {
            key: len(business.get(key, []))
            for key in (
                "roles",
                "resources",
                "relations",
                "permissions",
                "workflows",
                "notifications",
                "metrics",
            )
            if isinstance(business.get(key, []), list)
        }
        details["plan_contract"] = contract_snapshot(plan)
        details["requirement_contract"] = contract_snapshot(requirement, requirement=True)
        details["unsupported_excerpts"] = text_budget.excerpts(plan.get("unsupported", []))
        if requirement and plan:
            from workbench.domain import Plan, Requirement
            from workbench.requirement_coverage import coverage_gaps

            details["coverage_reason_excerpts"] = text_budget.excerpts(
                coverage_gaps(Requirement.model_validate(requirement), Plan.model_validate(plan))
            )
            details["coverage_sources"] = safe_coverage_details(
                requirement, plan, text_budget=text_budget
            )
            if run.get("template") in {"fastapiadmin", "yudao-vben"}:
                details["native_plan_validation"] = safe_native_plan_details(plan)
        error = run.get("error") or ""
        categories = {
            "model_schema_invalid": ("结构化契约",),
            "context_limit": ("上下文过大",),
            "provider_error": ("模型鉴权", "模型地址", "模型请求被拒绝", "模型服务超时"),
            "requirement_coverage": ("设计未覆盖", "已确认字段", "已确认条件", "覆盖不足"),
            "tool_failure": ("工具执行失败",),
            "browser_acceptance": ("浏览器", "browser"),
            "model_budget": ("调用次数", "模型调用预算"),
        }
        details["error_categories"] = [
            code for code, tokens in categories.items() if any(t in error for t in tokens)
        ]
        blocked = (pending.get("data") or {}).get("blocked", [])
        details["coverage_block_count"] = len(blocked) if isinstance(blocked, list) else 0
        diagnostic_kinds = {
            "missing_or_ambiguous": "缺失或映射不唯一",
            "legacy_missing_field": "缺少对应字段",
            "required": "必填",
            "optional": "可选",
            "max_length": "长度上限",
            "min_length": "最小长度",
            "date_kind": "真实日期类型",
            "uncovered_operation": "设计未覆盖已确认的",
            "constraint_mismatch": "设计不一致",
            "missing_metric_predicate": "业务指标缺少已确认的筛选条件",
            "business_capability": "业务设计缺少",
        }
        attributes = (
            "kind",
            "required",
            "searchable",
            "filterable",
            "date_range",
            "min_length",
            "max_length",
            "choices",
        )
        known_names = {
            field["name"] for entity in details["plan_contract"] for field in entity["fields"]
        }
        sources = (pending.get("data") or {}).get("block_sources", [])
        known_sources = {
            "planner_unsupported",
            "template_field_kind",
            "requirement_coverage",
            "business_coverage",
            "business_contract",
            "coding_disabled",
            "native_coding_engine",
            "native_validation_or_runtime",
            "sandbox_configuration",
        }
        details["coverage_diagnostics"] = [
            {
                "codes": (
                    [DESIGN_REASON_CODES[reason]]
                    if reason in DESIGN_REASON_CODES
                    else [code for code, marker in diagnostic_kinds.items() if marker in reason]
                    or (
                        ["planner_unsupported"]
                        if reason in plan.get("unsupported", [])
                        else ["unclassified_design_block"]
                    )
                ),
                "origin": sources[index]
                if index < len(sources) and sources[index] in known_sources
                else "not_recorded",
                "attributes": [attribute for attribute in attributes if attribute in reason],
                "fields": sorted(
                    name
                    for name in known_names
                    if name != "unrecognized"
                    and re.search(r"(?<![a-z0-9_])" + re.escape(name) + r"(?![a-z0-9_])", reason)
                ),
            }
            for index, reason in enumerate((blocked if isinstance(blocked, list) else [])[:40])
            if isinstance(reason, str)
        ]
        details["unsupported_diagnostics"] = [
            {
                "index": index,
                "topics": [
                    code
                    for code, pattern in (
                        ("search", r"搜索|检索|search"),
                        ("filter", r"筛选|过滤|filter"),
                        ("date_range", r"日期范围|日期区间|date.?range"),
                        ("capability", r"模板|能力|capabilit"),
                        ("external_service", r"外部|短信|邮件|支付|采集|external"),
                        ("business", r"角色|关系|流程|统计|business"),
                    )
                    if re.search(pattern, reason, re.I)
                ],
            }
            for index, reason in enumerate(plan.get("unsupported", [])[:40])
            if isinstance(reason, str)
        ]
        paths = {f["name"] for e in details["plan_contract"] for f in e["fields"]}
        details["coverage_fields"] = (
            sorted(
                name
                for name in paths
                if name != "unrecognized"
                and any(name in reason for reason in blocked if isinstance(reason, str))
            )
            if isinstance(blocked, list)
            else []
        )
    return details


def smoke(config, transport):
    """A single bounded genuine request. Provider error bodies are never emitted."""
    try:
        with httpx.Client(
            transport=transport, timeout=120, follow_redirects=False, trust_env=False
        ) as client:
            with client.stream(
                "POST",
                config.base_url + "/chat/completions",
                headers={"Authorization": "Bearer " + config.key.get_secret_value()},
                json=SMOKE_PAYLOAD,
            ) as response:
                status = response.status_code
                if status != 200:
                    code = "model_unavailable" if status == 404 else "provider_rejected"
                    raise SafeFailure(code, status)
                data = bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data) > 131072:
                        raise SafeFailure("smoke_response_too_large", status)
        content = json.loads(data)["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise SafeFailure("invalid_smoke_response", status)
    except httpx.HTTPError:
        raise SafeFailure("provider_transport_failure") from None
    except ValueError, KeyError, IndexError, TypeError:
        raise SafeFailure("invalid_smoke_response") from None
    return {"passed": True, "http_status": status, "actual_provider_request": True}


BROWSER_DRIVER = r"""
const fs = require('node:fs');
const [file, modulePath] = process.argv.slice(2);
const cfg = JSON.parse(fs.readFileSync(file, 'utf8'));
async function main() {
  const {chromium} = require(modulePath);
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  const errors=[];
  page.on('pageerror', () => errors.push('page_error'));
  try {
    await page.goto(cfg.platform);
    await page.locator('#token').fill(cfg.token);
    await page.locator('#connect button').click();
    await page.locator('#template').selectOption(cfg.template);
    await page.locator('#frontend').selectOption(cfg.frontend);
    await page.locator('#database').selectOption(cfg.database);
    await page.locator('#choose').click();
    await page.locator('#project-title').fill('真实 DeepSeek 客服完整验收');
    await page.locator('#requirement').fill(cfg.requirement);
    // Exactly one initial delegation, no subsequent approval or retry clicks.
    await page.locator('#initial-smart').check();
    await page.locator('#new-run button').click();
    await page.waitForFunction(() => ['READY','SOURCE_READY','FAILED','BLOCKED','PAUSED_LIMIT','REJECTED']
      .some(s=>document.querySelector('#status').textContent === '状态：'+s), null, {timeout:6900000});
    const state=(await page.locator('#status').innerText()).replace('状态：','');
    const runId=(await page.locator('#run-title').innerText()).split(' ').at(-1);
    fs.writeFileSync(cfg.result, JSON.stringify({state,run_id:runId,page_errors:errors.length}));
    if(state!=='READY' || errors.length) throw new Error('workflow_not_ready');
    const download=page.waitForEvent('download');
    await page.locator('#download').click();
    await (await download).saveAs(cfg.download);
  } finally { await browser.close(); }
}
main().catch(()=> { console.error('real-model browser acceptance did not complete'); process.exitCode=1; });
"""


def customer_request():
    from workbench.settings import ROOT

    return "\n\n".join(
        (ROOT / "examples/requirements" / name).read_text(encoding="utf-8")
        for name in (
            "customer-service.md",
            "customer-service-decisions.md",
            "customer-service-contract.md",
        )
    )


def require_customer_spec(spec):
    from workbench.business_capabilities import business_gaps
    from workbench.domain import Plan, Requirement

    try:
        plan = Plan.model_validate(spec)
        assert plan.business is not None and plan.data_scope == "shared" and not plan.unsupported
        assert {e.name for e in plan.entities} == {"customers", "requests", "tasks"}
        assert {r.name for r in plan.business.roles} == {"manager", "service", "employee"}
        requirement = Requirement(
            summary=customer_request(),
            users=["管理人员", "服务人员", "普通员工"],
            features=[],
            acceptance=[],
            data_scope="shared",
        )
        assert not business_gaps(requirement, plan)

        # Match the public metric meanings, never provider-selected names/labels.
        # Extra supported metrics remain valid, but cannot substitute for these five.
        def resolved_only(metric):
            return bool(metric.filters) and all(
                rule.field == "request_state"
                and (
                    (rule.op == "eq" and rule.value == "resolved")
                    or (rule.op == "in" and rule.value == ["resolved"])
                )
                for rule in metric.filters
            )

        metrics = plan.business.metrics
        assert any(
            metric.entity == "requests" and metric.kind == "count" and not metric.filters
            for metric in metrics
        )
        assert any(
            metric.entity == "requests" and metric.kind == "count" and resolved_only(metric)
            for metric in metrics
        )
        assert any(
            metric.entity == "requests"
            and metric.kind == "average_duration"
            and metric.start_field == "created_at"
            and metric.end_field == "resolved_at"
            and (not metric.filters or resolved_only(metric))
            for metric in metrics
        )
        assert any(
            metric.entity == "customers"
            and metric.kind == "group_count"
            and metric.group_by == "category"
            and not metric.filters
            for metric in metrics
        )
        assert any(
            metric.entity == "requests"
            and metric.kind == "time_count"
            and metric.time_field == "created_at"
            and not metric.filters
            for metric in metrics
        )
        notices = plan.business.notifications
        for entity in ("requests", "tasks"):
            for event, transition, due_field in (
                ("assigned", None, None),
                ("note_added", None, None),
                ("transitioned", "start", None),
                ("transitioned", "resolve", None),
                ("due", None, "due_at"),
            ):
                assert any(
                    notice.entity == entity
                    and notice.event == event
                    and notice.transition == transition
                    and notice.due_field == due_field
                    for notice in notices
                )
        assert any(
            notice.entity == "requests"
            and notice.event == "transitioned"
            and notice.transition == "resolve"
            and notice.recipient == "creator"
            for notice in notices
        )
        assert not plan.custom_rules
        entities = {
            entity.name: {field.name: field for field in entity.fields} for entity in plan.entities
        }
        expected = {
            "customers": {"name", "organization", "contact", "category"},
            "requests": {
                "title",
                "detail",
                "customer_id",
                "assignee_id",
                "request_state",
                "resolved_at",
                "due_at",
                "priority",
            },
            "tasks": {
                "title",
                "detail",
                "request_id",
                "assignee_id",
                "task_state",
                "resolved_at",
                "due_at",
            },
        }
        assert all(set(entities[name]) == fields for name, fields in expected.items())
        assert all(field.label for fields in entities.values() for field in fields.values())
        for entity, field_name in (("requests", "request_state"), ("tasks", "task_state")):
            field = entities[entity][field_name]
            assert set(field.choice_labels) == set(field.choices)
            assert all(field.choice_labels[value] != value for value in field.choices)
        assert set(entities["customers"]["category"].choices) == {"企业", "个人", "合作伙伴"}
        assert set(entities["requests"]["priority"].choices) == {"普通", "紧急"}
        relations = {(r.entity, r.field, r.target_entity) for r in plan.business.relations}
        assert {
            ("requests", "customer_id", "customers"),
            ("tasks", "request_id", "requests"),
            ("requests", "assignee_id", "$users"),
            ("tasks", "assignee_id", "$users"),
        } <= relations
        assert plan.business.bootstrap_role == "manager"
        assert set(plan.business.role_admin_roles) == {"manager"}
        assert (
            plan.business.registration.enabled
            and plan.business.registration.default_role == "employee"
        )
        policies = {(p.role, p.entity): p for p in plan.business.permissions}
        # Minimum capabilities explicitly promised for this customer case.
        # Keep optional actions separate from these obligations; query access alone
        # must neither imply a grant nor excuse a missing processing action.
        customer_manager_actions = {"create", "read", "update", "archive", "read_audit"}
        processing_actions = {
            "read",
            "update",
            "add_note",
            "transition",
            "read_history",
            "read_audit",
        }
        manager_processing_actions = processing_actions | {"create", "archive", "assign"}
        required_actions = {
            ("manager", "customers"): customer_manager_actions,
            ("manager", "requests"): manager_processing_actions,
            ("manager", "tasks"): manager_processing_actions,
            ("service", "requests"): processing_actions,
            ("service", "tasks"): processing_actions,
            ("employee", "requests"): {"create", "read"},
        }
        for identity, actions in required_actions.items():
            assert actions <= set(policies[identity].actions)
        assert all(policies[("manager", entity)].scope == "all" for entity in expected)
        assert all(
            not {"create", "assign"} & set(policy.actions)
            for policy in plan.business.permissions
            if policy.entity == "tasks" and policy.role != "manager"
        )
        for role in ("manager", "service"):
            for entity in ("customers", "requests"):
                assert {"read", "read_metrics"} <= set(policies[(role, entity)].actions)
        for role in ("service", "employee"):
            customer_policy = policies[(role, "customers")]
            assert customer_policy.scope == "all" and "read" in customer_policy.actions
            assert not {"create", "update", "archive", "add_note", "read_audit"} & set(
                customer_policy.actions
            )
        resources = {resource.entity: resource for resource in plan.business.resources}
        assert all(resources[entity].audit for entity in ("customers", "requests", "tasks"))
        for entity in ("requests", "tasks"):
            assert resources[entity].notes and resources[entity].archive
            assert resources[entity].assignee_field == "assignee_id"
            if ("employee", entity) in policies:
                assert policies[("employee", entity)].scope == "own"
                assert not {"assign", "transition"} & set(policies[("employee", entity)].actions)
            else:
                assert entity == "tasks"
            assert policies[("service", entity)].scope == "assigned"
            workflow = next(w for w in plan.business.workflows if w.entity == entity)
            transitions = {t.name: t for t in workflow.transitions}
            assert all(transition.label for transition in workflow.transitions)
            assert workflow.initial == "new"
            assert (
                workflow.status_field
                == {"requests": "request_state", "tasks": "task_state"}[entity]
            )
            assert all(
                set(transition.roles) == {"manager", "service"}
                for transition in transitions.values()
            )
            assert (
                transitions["start"].from_states == ["new"]
                and transitions["start"].to_state == "active"
            )
            assert (
                transitions["resolve"].from_states == ["active"]
                and transitions["resolve"].to_state == "resolved"
            )
            assert transitions["resolve"].set_timestamp == "resolved_at"
        assert all(
            "read_metrics" not in policy.actions
            for policy in plan.business.permissions
            if policy.role == "employee"
        )
    except ValueError, KeyError, TypeError, AssertionError, StopIteration:
        raise SafeFailure("explicit_customer_obligation_not_preserved") from None


def acceptance_settings(config, directory):
    from workbench.settings import STAGES, Settings

    return Settings(
        data_dir=directory / "private-platform",
        database_url="",
        checkpoint_url="",
        base_url=config.base_url,
        api_key=config.key,
        MODE=config.model,
        **{
            stage + suffix: value
            for stage in STAGES
            for suffix, value in (
                ("_base_url", config.base_url),
                ("_api_key", config.key),
                ("_model", config.model),
            )
        },
        install_products=True,
        tool_timeout=600,
        model_review=True,
        llm_timeout=180,
        max_model_calls=MAX_WORKFLOW_CALLS,
        max_rounds=5,
        max_repair_attempts=1,
        coding_engine="bounded",
        repo_map_provider="symbols",
        retrieval_engine="local",
        embedding_enabled=False,
        sandbox_provider="local",
        _env_file=None,
    )


def run_acceptance(config, transport, directory, template="python-basic"):
    import uvicorn

    from workbench.api import create_app
    from workbench.filesystem import unpack, write_json
    from workbench.llm import ModelGateway
    from workbench.settings import ROOT
    from workbench.tools import clean_env
    from workbench.verification import product_interpreter, require_browser_evidence, run_probe

    settings = acceptance_settings(config, directory)
    from workbench.catalog import Selection

    selection = Selection(template=template)
    if template != "python-basic":
        from workbench.native_delivery import runtime_path

        settings.prepare()
        write_json(
            runtime_path(settings, template),
            {
                "database_url_env": "NATIVE_TEST_DATABASE_URL",
                "initialize_empty_database": True,
            },
        )
    traces = []
    diagnostic_text = DiagnosticTextBudget(secrets=(config.key.get_secret_value(),))

    class ObservedGateway(ModelGateway):
        def complete(self, run_id, key, instruction, payload, schema):
            stage = key.split(":")[0]
            stage = (
                stage
                if stage in {"requirement", "recommend", "plan", "coding", "review"}
                else "unknown"
            )
            transport.current_schema, transport.current_stage = schema, stage
            trace = {"stage": stage, "completed": False}
            traces.append(trace)
            value = super().complete(run_id, key, instruction, payload, schema)
            trace.update(completed_stage_details(value, diagnostic_text))
            return value

    application = create_app(
        settings, gateway_factory=lambda store: ObservedGateway(settings, store, transport)
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            application, host="127.0.0.1", port=port, log_level="critical", access_log=False
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    try:
        for _ in range(150):
            if server.started:
                break
            time.sleep(0.1)
        else:
            raise SafeFailure("platform_start_failed")
        driver = directory / "browser.cjs"
        driver.write_text(BROWSER_DRIVER, encoding="utf-8")
        result_path, archive = directory / "browser-result.json", directory / "download.zip"
        cfg = directory / "browser-private.json"
        write_json(
            cfg,
            {
                "platform": f"http://127.0.0.1:{port}",
                "token": application.state.token,
                "requirement": customer_request(),
                "template": template,
                "frontend": selection.frontend,
                "database": selection.database,
                "download": str(archive),
                "result": str(result_path),
            },
        )
        module = os.environ.get(
            "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
        )
        process = subprocess.run(
            ["node", str(driver), str(cfg), module],
            cwd=ROOT,
            env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
            capture_output=True,
            timeout=6960,
            check=False,
        )
        if process.returncode or not result_path.is_file():
            last = next((s for s in reversed(transport.statuses) if s >= 400), None)
            run_id = None
            if result_path.is_file():
                run_id = json.loads(result_path.read_text(encoding="utf-8")).get("run_id")
            native_reports = (
                settings.data_dir / "runs" / run_id / "native-evidence"
                if template != "python-basic"
                and isinstance(run_id, str)
                and re.fullmatch(r"[a-zA-Z0-9_-]{1,100}", run_id)
                else None
            )
            details = safe_workflow_details(
                application.state.store,
                run_id,
                traces,
                text_budget=diagnostic_text,
                native_reports=native_reports,
            )
            details["approved_plan_replay"] = preserve_approved_customer_plan(
                native_reports,
                ROOT / "reports/real-model/approved-plan-replay.json",
                diagnostic_text,
            )
            raise SafeFailure("workflow_not_ready", last, details)
        browser = json.loads(result_path.read_text(encoding="utf-8"))
        run = application.state.store.get_run(browser["run_id"])
        if run["status"] != "READY" or not run["auto_mode"] or not archive.is_file():
            raise SafeFailure("delivery_not_ready")
        if hashlib.sha256(archive.read_bytes()).hexdigest() != run["result"]["sha256"]:
            raise SafeFailure("download_integrity_failed")
        product = directory / "downloaded-product"
        unpack(archive, product)
        screenshot_dir = ROOT / "reports/real-model/screenshots"
        if template == "python-basic":
            spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
            require_customer_spec(spec)
            if not run["result"]["cleanroom"].get("passed"):
                raise SafeFailure("pipeline_cleanroom_failed")
            require_browser_evidence(product, run["result"]["cleanroom"])
            python = product_interpreter(product, settings)
            probe = directory / "downloaded-product-verification.json"
            run_probe(product, python, probe, settings, business_screenshots=screenshot_dir)
            evidence = json.loads(probe.read_text(encoding="utf-8"))
            require_browser_evidence(product, evidence)
            if evidence.get("passed") is not True or evidence.get("restart") is not True:
                raise SafeFailure("downloaded_cleanroom_failed")
        else:
            from workbench.portable import verify_native_delivery

            manifest = json.loads(
                (product / "deployment/manifest.json").read_text(encoding="utf-8")
            )
            require_customer_spec(manifest["plan"])
            evidence = verify_native_delivery(
                product, os.environ["NATIVE_TEST_DATABASE_URL"], directory / "downloaded-evidence"
            )
            if (
                evidence.get("passed") is not True
                or evidence.get("fresh_database") is not True
                or evidence.get("restart") is not True
                or evidence.get("restart_preserved_records") is not True
            ):
                raise SafeFailure("downloaded_cleanroom_failed")
            # Only allowlisted synthetic UI PNGs, never full logs, credentials or product archives.
            import shutil

            native_reports = settings.data_dir / "runs" / browser["run_id"] / "native-evidence"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            for screenshot in native_reports.rglob("*.png"):
                if screenshot.is_symlink() or screenshot.stat().st_size > 12_000_000:
                    raise SafeFailure("invalid_screenshot_artifact")
                if not re.fullmatch(r"[a-zA-Z0-9_-]+\.png", screenshot.name):
                    raise SafeFailure("invalid_screenshot_name")
                if not screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                    raise SafeFailure("invalid_screenshot_png")
                shutil.copyfile(screenshot, screenshot_dir / screenshot.name)
            if not list(screenshot_dir.glob("*.png")):
                raise SafeFailure("missing_native_screenshots")
        return {
            "passed": True,
            "real_model": True,
            "single_initial_smart_consent": True,
            "explicit_customer_obligations_preserved": True,
            "template": template,
            "ready": True,
            "ui_download": True,
            "download_hash_matches": True,
            "independent_database": True,
            "real_browser": True,
            "restart": True,
            "model_calls": run["model_calls"],
            "page_errors": browser["page_errors"],
            "aider_edit": "not_exercised",
            "continue_native_index": "not_exercised",
            "daytona": "not_exercised",
            "old_blocked_recovery": "not_exercised_in_real_run",
        }
    finally:
        server.should_exit = True
        thread.join(timeout=120)


def verified_smoke_receipt(path, config, env):
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["passed"] is True and saved["acceptance_scope"] == "smoke_only"
        assert saved["smoke"] == {
            "passed": True,
            "http_status": 200,
            "actual_provider_request": True,
        }
        assert saved["actual_http_calls"] == 1 and saved["provider_statuses"] == [200]
        assert saved["model"] == config.model and saved["endpoint"] == config.base_url
        assert saved["run_identity"] == [
            env.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
        ]
        return saved["smoke"]
    except OSError, ValueError, KeyError, AssertionError, TypeError:
        raise SafeFailure("missing_matching_successful_smoke") from None


def main():
    import argparse

    from workbench.settings import ROOT

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "full"], required=True)
    parser.add_argument(
        "--template", choices=["python-basic", "fastapiadmin", "yudao-vben"], default="python-basic"
    )
    args = parser.parse_args()
    mode = args.phase
    destination = ROOT / "reports/real-model"
    summary = destination / "summary.json"
    result = {
        "passed": False,
        "real_provider_attempted": False,
        "acceptance_scope": "smoke_only" if mode == "smoke" else "full_workflow",
    }
    transport = None
    config = None
    phase = "configuration"
    prior_calls = 0
    try:
        trusted_dispatch(os.environ)
        config = configuration(os.environ)
        # Never inherit the provider credential into browser/uv/product child processes.
        os.environ.pop("API_KEY", None)
        result.update(
            model=config.model,
            endpoint=config.base_url,
            run_identity=[
                os.environ.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
            ],
        )
        if mode == "full":
            (destination / "approved-plan-replay.json").unlink(missing_ok=True)
            result["smoke"] = verified_smoke_receipt(summary, config, os.environ)
            prior_calls = 1
        transport = BoundedRealTransport(config)
        with tempfile.TemporaryDirectory(prefix="rnd-real-model-") as private:
            # Suppress raw application/provider tracebacks and model-generated text.
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as quiet:
                logging.disable(logging.CRITICAL)
                with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                    result["real_provider_attempted"] = True
                    if mode == "smoke":
                        phase = "smoke"
                        result["smoke"] = smoke(config, transport)
                    else:
                        phase = "workflow"
                        result["workflow"] = run_acceptance(
                            config, transport, Path(private), args.template
                        )
        result["passed"] = True
    except SafeFailure as exc:
        result.update(failure_phase=phase, failure_code=exc.code)
        if exc.status is not None:
            result["provider_status"] = exc.status
        if exc.details is not None:
            result["configuration_checks" if "configuration" in exc.code else "failure_details"] = (
                exc.details
            )
    except Exception:
        result.update(failure_phase=phase, failure_code="acceptance_execution_failed")
    finally:
        if transport:
            result["actual_http_calls"] = prior_calls + transport.calls
            result["provider_statuses"] = ([200] if prior_calls else []) + transport.statuses
            result["provider_receipts"] = transport.receipts
            with contextlib.suppress(Exception):
                transport.shutdown()
        destination.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(result, indent=2)
        if config is not None:
            rendered = rendered.replace(config.key.get_secret_value(), "[REDACTED]")
        summary.write_text(rendered, encoding="utf-8")
    print(rendered)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
