"""Opt-in mini-SWE wire contract for the reviewed, locked SDK combination."""

import json
from importlib.metadata import version

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from workbench.models.protocol import OutputFailure, load_json

SDK_VERSIONS = {
    "langchain-openai": "1.6.7",
    "openai": "3.22.1",
    "pydantic": "2.13.5",
    "httpx": "0.28.1",
    "jsonschema": "4.26.0",
}


class NativeSchema:
    def __init__(self, profile, schema, settings, *, key, payload, streaming):
        from workbench.coding.ports import AgentTurn

        if (
            streaming
            or profile.provider != "compatible"
            or profile.max_output_tokens != 8192
            or settings.max_context_chars > 40000
            or settings.llm_timeout > 60
            or not key.startswith("coding:mini_swe:")
            or not issubclass(schema, AgentTurn)
            or schema.__name__ != "ApprovedAgentTurn"
            or payload.get("task", {}).get("id") not in {"sla-api", "sla-dashboard"}
        ):
            raise OutputFailure("native_scope_rejected", "原生 strict 仅限批准的 mini-swe-sla 契约")
        try:
            if any(version(name) != pinned for name, pinned in SDK_VERSIONS.items()):
                raise ValueError
            # This private SDK transformation is version-bound and checked again
            # against the actual serialized HTTP request before it can leave.
            from openai.lib._pydantic import to_strict_json_schema

            self.schema = to_strict_json_schema(schema)
            Draft202012Validator.check_schema(self.schema)
            self.validator = Draft202012Validator(self.schema)
        except Exception:
            raise OutputFailure("native_sdk_unsupported", "原生 strict SDK/Schema 不兼容") from None
        self.response_format = {
            "type": "json_schema",
            "json_schema": {"name": schema.__name__, "strict": True, "schema": self.schema},
        }
        self.url = profile.base_url.rstrip("/") + "/chat/completions"
        self.model = profile.model
        self.input_bytes = 4 * settings.max_context_chars
        self.timeout = settings.llm_timeout
        self.request_verified = False
        self.local_conformant = None

    def check_request(self, request):
        try:
            data = request.read()
            if len(data) > self.input_bytes:
                raise ValueError
            body = load_json(data)
            if (
                request.method != "POST"
                or str(request.url) != self.url
                or set(body)
                != {"model", "messages", "stream", "max_completion_tokens", "response_format"}
                or body["model"] != self.model
                or body["stream"] is not False
                or type(body["max_completion_tokens"]) is not int
                or body["max_completion_tokens"] != 8192
                or json.dumps(body["response_format"], sort_keys=True)
                != json.dumps(self.response_format, sort_keys=True)
                or request.extensions.get("timeout")
                != dict.fromkeys(("connect", "read", "write", "pool"), self.timeout)
            ):
                raise ValueError
        except ValueError, TypeError, KeyError:
            raise OutputFailure("native_request_mismatch", "原生 strict 出站契约不匹配") from None
        self.request_verified = True

    def check_content(self, content):
        self.local_conformant = False
        try:
            self.validator.validate(load_json(content))
        except ValueError, TypeError, ValidationError, RecursionError:
            raise OutputFailure(
                "native_schema_violation", "响应违反所请求的 strict Schema"
            ) from None
        self.local_conformant = True


def native_receipt(native=None, *, status=None):
    return {
        "native_strict_requested": True,
        "native_request_verified": native.request_verified if native is not None else False,
        "native_local_conformant": native.local_conformant if native is not None else None,
        "native_provider_enforcement": "unknown",
        "native_http_status": status if type(status) is int and 100 <= status <= 599 else None,
    }
