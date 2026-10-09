"""Authenticated local model configuration, atomic persistence and secret-safe views.

The JSON file is private local credential storage, never an API representation. Each
model call resolves one immutable profile, so edits affect the next call, not an
already running call or its retry. Reads also work in a separate worker process.
"""

import json
import os
import stat
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from filelock import FileLock, Timeout
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    SecretStr,
    ValidationError,
    ValidationInfo,
    field_validator,
)
from starlette.concurrency import run_in_threadpool

from workbench.settings import STAGES, ModelProfile, OutputMode, Provider, validate_model_url

MAX_CONFIG_BYTES = 65536
PROFILE_FIELDS = {"base_url", "model", "api_key", "provider", "output_mode", "max_output_tokens"}


class ModelSettingsError(ValueError):
    """Safe, non-secret diagnostic for both CLI and HTTP callers."""


class RevisionConflict(ModelSettingsError):
    pass


class ProfileConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)
    base_url: str = Field(default="", max_length=2048)
    model: str = Field(default="", max_length=256)
    api_key: SecretStr = SecretStr("")
    provider: Provider | None = None
    output_mode: OutputMode | None = None
    max_output_tokens: int | None = Field(default=None, ge=1, le=393216)

    @field_validator("base_url")
    @classmethod
    def endpoint(cls, value, info: ValidationInfo):
        return (
            validate_model_url(
                value,
                allow_insecure_http=bool(
                    info.context and info.context.get("allow_insecure_model_http")
                ),
            )
            if value
            else ""
        )

    @field_validator("model")
    @classmethod
    def model_name(cls, value):
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError("模型名称不能包含控制字符")
        return value.strip()

    @field_validator("api_key")
    @classmethod
    def key(cls, value):
        secret = value.get_secret_value()
        if len(secret) > 8192 or any(ord(char) < 33 or ord(char) == 127 for char in secret):
            raise ValueError("API Key 格式无效")
        if secret in {"configured", "missing", "**********", "[redacted]"}:
            raise ValueError("请重新输入 API Key，不要提交已配置标记")
        return value

    def public(self):
        return {
            **self.model_dump(exclude={"api_key"}),
            "api_key": "configured" if self.api_key.get_secret_value() else "missing",
        }

    def private(self):
        return {**self.model_dump(), "api_key": self.api_key.get_secret_value()}


class ModelConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)
    _allow_insecure_model_http: bool = PrivateAttr(default=False)
    version: int = 1
    revision: str = Field(default="0", max_length=64)
    default: ProfileConfig
    stages: dict[str, ProfileConfig]
    model_review: bool = False

    def model_post_init(self, context):
        self._allow_insecure_model_http = bool(context and context.get("allow_insecure_model_http"))

    @field_validator("version")
    @classmethod
    def known_version(cls, value):
        if value != 1:
            raise ValueError("不支持的模型配置版本")
        return value

    @field_validator("stages")
    @classmethod
    def known_stages(cls, value):
        if set(value) != set(STAGES):
            raise ValueError("模型配置阶段不完整")
        return value

    @property
    def review_enabled(self):
        review = self.stages["review"]
        return bool(
            self.model_review
            or review.model
            or review.base_url
            or review.api_key.get_secret_value()
        )

    def profile(self, stage):
        if stage not in STAGES:
            raise ModelSettingsError("未知模型阶段")
        override = self.stages[stage]
        base = self.default
        endpoint = override.base_url or base.base_url
        same_endpoint = endpoint.rstrip("/") == base.base_url.rstrip("/")
        key = override.api_key
        if not key.get_secret_value():
            if not same_endpoint:
                raise ModelSettingsError(
                    f"{stage}: 更换服务商地址时必须单独配置 {stage.upper()}_API_KEY，禁止发送默认密钥到新地址"
                )
            key = base.api_key
        return ModelProfile(
            stage=stage,
            base_url=endpoint,
            model=override.model or base.model,
            api_key=key,
            provider=override.provider or (base.provider if same_endpoint else None) or "auto",
            output_mode=override.output_mode
            or (base.output_mode if same_endpoint else None)
            or "auto",
            max_output_tokens=override.max_output_tokens
            or (base.max_output_tokens if same_endpoint else None),
            allow_insecure_http=self._allow_insecure_model_http,
        )

    def require_model(self):
        for stage in STAGES:
            if stage != "review" or self.review_enabled:
                self.profile(stage).validate_endpoint()

    def private(self):
        return {
            "version": self.version,
            "revision": self.revision,
            "default": self.default.private(),
            "stages": {stage: config.private() for stage, config in self.stages.items()},
            "model_review": self.model_review,
        }

    def public(self):
        stages, validation = {}, []
        for stage in STAGES:
            override = self.stages[stage]
            row = {"stage": stage, "enabled": stage != "review" or self.review_enabled}
            stages[stage] = {**override.public(), "effective": None, "key_source": "missing"}
            try:
                profile = self.profile(stage)
                stages[stage]["effective"] = profile.public()
                if profile.api_key.get_secret_value():
                    stages[stage]["key_source"] = (
                        "override" if override.api_key.get_secret_value() else "default"
                    )
                profile.validate_endpoint()
                row["valid"] = True
            except ValueError as exc:
                row.update(valid=False, error=str(exc))
            validation.append(row)
        return {
            "revision": self.revision,
            "default": self.default.public(),
            "stages": stages,
            "model_review": self.model_review,
            "review_enabled": self.review_enabled,
            "ready": all(row["valid"] for row in validation if row["enabled"]),
            "validation_scope": "format_only",
            "validation": validation,
        }


def environment_configuration(settings):
    """Copy current settings, including explicit test/local mutations, without I/O."""
    values = {name: getattr(settings, name) for name in PROFILE_FIELDS}
    stages = {
        stage: {name: getattr(settings, stage + "_" + name) for name in PROFILE_FIELDS}
        for stage in STAGES
    }
    try:
        return ModelConfiguration.model_validate(
            {"default": values, "stages": stages, "model_review": settings.model_review},
            context={"allow_insecure_model_http": settings.allow_insecure_model_http},
        )
    except ValidationError, ValueError:
        raise ModelSettingsError("模型配置格式无效；请检查 BaseURL、模型名称和配置类型") from None


class ModelSettingsRepository:
    def __init__(self, settings):
        self.settings = settings
        self.path = settings.data_dir / "model-settings.json"

    def snapshot(self):
        try:
            fd = os.open(self.path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        except FileNotFoundError:
            if self.path.is_symlink():
                raise ModelSettingsError("模型配置文件不能是符号链接") from None
            return environment_configuration(self.settings)
        except OSError:
            raise ModelSettingsError("无法安全读取本机模型配置文件") from None
        try:
            with os.fdopen(fd, "rb") as handle:
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode) or self.path.is_symlink():
                    raise ModelSettingsError("模型配置必须是本机普通文件")
                if os.name == "posix" and stat.S_IMODE(info.st_mode) & 0o077:
                    raise ModelSettingsError("模型配置文件权限过宽；请将权限设为 600")
                data = handle.read(MAX_CONFIG_BYTES + 1)
            if len(data) > MAX_CONFIG_BYTES:
                raise ModelSettingsError("模型配置文件过大")
            return ModelConfiguration.model_validate_json(data, context=self._validation_context())
        except ValidationError, ValueError, OSError:
            raise ModelSettingsError(
                "本机模型配置无效或不可读取；请检查文件格式和 600 权限"
            ) from None

    def public(self):
        return self.snapshot().public()

    def _validation_context(self):
        return {"allow_insecure_model_http": self.settings.allow_insecure_model_http}

    def update(self, patch):
        if not isinstance(patch, dict) or set(patch) - {
            "expected_revision",
            "default",
            "stages",
            "model_review",
        }:
            raise ModelSettingsError("请求包含未知配置字段")
        if not isinstance(patch.get("expected_revision"), str):
            raise ModelSettingsError("保存前必须提供当前 expected_revision")
        try:
            self.settings.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            with FileLock(str(self.path.with_suffix(".lock")), timeout=5, mode=0o600):
                before = self.snapshot()
                if patch["expected_revision"] != before.revision:
                    raise RevisionConflict("配置已被其他窗口修改；请重新加载后再保存")
                after = self._merge(before, patch)
                self._atomic_write(after)
                self.settings._remember_model_keys(before)
                self.settings._remember_model_keys(after)
                return after.public()
        except Timeout:
            raise ModelSettingsError("模型配置正在保存，请稍后重试") from None
        except OSError:
            raise ModelSettingsError("无法安全保存本机模型配置；请检查目录权限和剩余空间") from None

    def _merge(self, before, patch):
        values = before.private()
        changes = {"default": patch.get("default", {})}
        stage_patch = patch.get("stages", {})
        if not isinstance(stage_patch, dict) or set(stage_patch) - set(STAGES):
            raise ModelSettingsError("请求包含未知模型阶段")
        changes.update(stage_patch)
        for name, change in changes.items():
            if not isinstance(change, dict) or set(change) - PROFILE_FIELDS:
                raise ModelSettingsError("请求包含未知模型字段")
            target = values["default"] if name == "default" else values["stages"][name]
            target.update(change)
            changed_url = change.get("base_url")
            if isinstance(changed_url, str):
                changed_url = changed_url.rstrip("/")
            if (
                "base_url" in change
                and changed_url
                != (before.default if name == "default" else before.stages[name]).base_url
            ):
                for field, fallback in (
                    ("provider", "auto" if name == "default" else None),
                    ("output_mode", "auto" if name == "default" else None),
                    ("max_output_tokens", None),
                ):
                    if field not in change:
                        target[field] = fallback
        if "model_review" in patch:
            values["model_review"] = patch["model_review"]
        values["revision"] = uuid.uuid4().hex
        try:
            after = ModelConfiguration.model_validate(values, context=self._validation_context())
        except ValidationError, ValueError:
            raise ModelSettingsError(
                "模型配置格式无效；请检查 BaseURL、模型名称、API Key 和配置类型"
            ) from None
        self._check_key_destinations(before, after, changes)
        return after

    @staticmethod
    def _check_key_destinations(before, after, changes):
        # Bind every known credential to its prior endpoint, even if it came from
        # another stage. Moving a stage must not repurpose a different old key.
        bindings = {}
        for name in ("default", *STAGES):
            config = before.default if name == "default" else before.stages[name]
            endpoint = config.base_url or before.default.base_url
            secret = config.api_key.get_secret_value()
            if secret and endpoint:
                bindings.setdefault(secret, set()).add(endpoint)
        # Include the default itself even if every stage currently overrides it.
        for name in ("default", *STAGES):
            old = before.default if name == "default" else before.stages[name]
            new = after.default if name == "default" else after.stages[name]
            old_url = old.base_url or (before.default.base_url if name != "default" else "")
            new_url = new.base_url or (after.default.base_url if name != "default" else "")
            old_key = old.api_key.get_secret_value() or (
                before.default.api_key.get_secret_value()
                if name != "default" and old_url == before.default.base_url
                else ""
            )
            new_key = new.api_key.get_secret_value()
            source = name
            if name != "default" and not new_key and new_url == after.default.base_url:
                new_key, source = after.default.api_key.get_secret_value(), "default"
            if new_key in bindings and new_url and new_url not in bindings[new_key]:
                raise ModelSettingsError("该 API Key 已用于其他地址；新地址必须使用独立密钥")
            if old_url == new_url:
                continue
            if not new_url:
                if new_key:
                    raise ModelSettingsError("清空 BaseURL 时也必须清空对应 API Key")
                continue
            # Returning to a default credential already bound to this endpoint is
            # safe. The old stage-specific key must have been explicitly cleared.
            if (
                name != "default"
                and source == "default"
                and new_url == before.default.base_url
                and new_key == before.default.api_key.get_secret_value()
                and new_key
            ):
                continue
            provided = changes.get(source, {}).get("api_key")
            if not provided or not new_key or new_key == old_key:
                raise ModelSettingsError(
                    "更换 BaseURL 时必须同时输入该地址的新独立 API Key，禁止复用旧密钥"
                )

    def _atomic_write(self, configuration):
        if self.path.is_symlink():
            raise ModelSettingsError("模型配置文件不能是符号链接")
        payload = json.dumps(configuration.private(), ensure_ascii=False, indent=2).encode("utf-8")
        if len(payload) > MAX_CONFIG_BYTES:
            raise ModelSettingsError("模型配置过大")
        descriptor, temporary = tempfile.mkstemp(prefix=".model-settings-", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                if os.name == "posix":
                    os.fchmod(handle.fileno(), 0o600)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
            if os.name == "posix":
                directory = os.open(self.path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
        finally:
            Path(temporary).unlink(missing_ok=True)


def _same_origin(request):
    origin = request.headers.get("origin")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "仅允许本机同源操作")
    if not origin:
        return  # Non-browser clients still require the bearer token.
    try:
        candidate = urlsplit(origin)
        current = urlsplit(str(request.url))

        def default_port(value):
            return value.port or (443 if value.scheme == "https" else 80)

        matches = (
            candidate.scheme in {"http", "https"}
            and not candidate.path
            and not candidate.query
            and not candidate.fragment
            and candidate.username is None
            and candidate.password is None
            and (candidate.scheme, candidate.hostname, default_port(candidate))
            == (current.scheme, current.hostname, default_port(current))
        )
    except ValueError:
        matches = False
    if not matches:
        raise HTTPException(403, "仅允许本机同源操作")


def register_model_settings_routes(app, settings, auth):
    from workbench.model_connection import (
        ConnectionTestBusy,
        ConnectionTestRequest,
        ModelConnectionTester,
    )

    repository = ModelSettingsRepository(settings)
    tester = ModelConnectionTester(settings)

    @app.get("/settings/models")
    def read_models(request: Request, store=Depends(auth)):
        _same_origin(request)
        try:
            return JSONResponse(repository.public(), headers={"Cache-Control": "no-store"})
        except ModelSettingsError:
            raise HTTPException(503, "本机模型配置无法安全读取；请检查配置文件权限和格式") from None

    @app.patch("/settings/models")
    @app.put("/settings/models")
    async def update_models(request: Request, store=Depends(auth)):
        _same_origin(request)
        patch = await _model_request_body(request)
        try:
            value = repository.update(patch)
            return JSONResponse(value, headers={"Cache-Control": "no-store"})
        except RevisionConflict as exc:
            raise HTTPException(409, str(exc)) from None
        except ModelSettingsError as exc:
            raise HTTPException(422, str(exc)) from None

    @app.post("/settings/models/test")
    async def test_models(request: Request, store=Depends(auth)):
        _same_origin(request)
        body = await _model_request_body(request)
        try:
            command = ConnectionTestRequest.model_validate(body)
        except ValidationError:
            raise HTTPException(
                422, "请提供已保存的配置版本、有效阶段、测试标识并确认本次模型调用费用"
            ) from None
        try:
            result = await run_in_threadpool(tester.test, command)
            return JSONResponse(result, headers={"Cache-Control": "no-store"})
        except (RevisionConflict, ConnectionTestBusy) as exc:
            raise HTTPException(409, str(exc)) from None
        except ModelSettingsError, OSError:
            raise HTTPException(503, "本机模型配置无法安全读取；请检查配置文件权限和格式") from None


async def _model_request_body(request):
    if (
        request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        != "application/json"
    ):
        raise HTTPException(415, "模型配置必须使用 JSON")
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > MAX_CONFIG_BYTES:
            raise HTTPException(413, "模型配置请求过大")
        chunks.append(chunk)
    try:
        return json.loads(b"".join(chunks))
    except ValueError, UnicodeDecodeError:
        raise HTTPException(422, "模型配置必须是有效 JSON") from None
