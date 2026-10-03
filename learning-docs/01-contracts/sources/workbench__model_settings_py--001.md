# workbench/model_settings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机模型配置的版本化保存与密钥边界。** 读取配置只返回模型身份和是否已配置Key；保存需匹配expected_revision。文件锁与原子替换避免并发覆盖，POSIX配置要求600权限。更换服务地址不复用旧密钥，已开始调用使用固定快照，下次调用才读取新版本。

**对应关系：** Vue模型设置 → 受认证且同源的/settings/models → ModelSettingsRepository → Settings.model_for → ModelGateway。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 两个窗口都读到版本R。窗口A保存得到R2后，窗口B仍带expected_revision=R时必须收到409，不能覆盖A。只改模型名称可以保留原地址Key；把地址A改成B必须为B输入新的独立Key。public响应只说是否已配置，真正密钥既不回填输入框，也不随错误返回。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ModelSettingsError`（L28–L29）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `RevisionConflict`（L32–L33）：继承`ModelSettingsError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ProfileConfig`（L36–L74）：继承`BaseModel`。声明的数据项为`base_url`、`model`、`api_key`、`provider`、`output_mode`、`max_output_tokens`；类型约束/数据库列参数以完整定义为准。
- `ProfileConfig.endpoint`（L47–L48）：接收`value`。 调用`validate_model_url`、`field_validator`。 返回路径：L48的`validate_model_url(value) if value else ""`。
- `ProfileConfig.model_name`（L52–L55）：接收`value`。 控制顺序：L53按`any(ord(char) < 32 or ord(char) == 127 for char in value)`分支；L54抛异常，停止当前正常路径。 调用`any`、`ord`、`ValueError`、`value.strip`、`field_validator`。 返回路径：L55的`value.strip()`。
- `ProfileConfig.key`（L59–L65）：接收`value`。 控制顺序：L61按`len(secret) > 8192 or any(ord(char) < 33 or ord(char) == 127 for char in secret)`分支；L62抛异常，停止当前正常路径；L63按`secret in {"configured", "missing", "**********", "[redacted]"}`分支；L64抛异常，停止当前正常路径。 调用`value.get_secret_value`、`len`、`any`、`ord`、`ValueError`、`field_validator`。 返回路径：L65的`value`。
- `ProfileConfig.public`（L67–L71）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_dump`、`self.api_key.get_secret_value`。 返回路径：L68的`{ **self.model_dump(exclude={"api_key"}), "api_key": "configured" if self.api_key.get_secr…`。
- `ProfileConfig.private`（L73–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_dump`、`self.api_key.get_secret_value`。 返回路径：L74的`{**self.model_dump(), "api_key": self.api_key.get_secret_value()}`。
- `ModelConfiguration`（L77–L177）：继承`BaseModel`。声明的数据项为`version`、`revision`、`default`、`stages`、`model_review`；类型约束/数据库列参数以完整定义为准。
- `ModelConfiguration.known_version`（L87–L90）：接收`value`。 控制顺序：L88按`value != 1`分支；L89抛异常，停止当前正常路径。 调用`ValueError`、`field_validator`。 返回路径：L90的`value`。
- `ModelConfiguration.known_stages`（L94–L97）：接收`value`。 控制顺序：L95按`set(value) != set(STAGES)`分支；L96抛异常，停止当前正常路径。 调用`set`、`ValueError`、`field_validator`。 返回路径：L97的`value`。
- `ModelConfiguration.review_enabled`（L100–L107）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`、`review.api_key.get_secret_value`。 返回路径：L102的`bool( self.model_review or review.model or review.base_url or review.api_key.get_secret_va…`。
- `ModelConfiguration.profile`（L109–L134）：接收`stage`。 控制顺序：L110按`stage not in STAGES`分支；L111抛异常，停止当前正常路径；L117按`not key.get_secret_value()`分支；L118按`not same_endpoint`分支；L119抛异常，停止当前正常路径。 调用`ModelSettingsError`、`endpoint.rstrip`、`base.base_url.rstrip`、`key.get_secret_value`、`stage.upper`、`ModelProfile`。 返回路径：L123的`ModelProfile( stage=stage, base_url=endpoint, model=override.model or base.model, api_key=…`。
- `ModelConfiguration.require_model`（L136–L139）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L137遍历`STAGES`；L138按`stage != "review" or self.review_enabled`分支。 调用`self.profile(stage).validate_endpoint`、`self.profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ModelConfiguration.private`（L141–L148）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.default.private`、`config.private`、`self.stages.items`。 返回路径：L142的`{ "version": self.version, "revision": self.revision, "default": self.default.private(), "…`。
- `ModelConfiguration.public`（L150–L177）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L152遍历`STAGES`；L159按`profile.api_key.get_secret_value()`分支。 调用`override.public`、`self.profile`、`profile.public`、`profile.api_key.get_secret_value`、`override.api_key.get_secret_value`、`profile.validate_endpoint`、`row.update`、`str`、`validation.append`等。 返回路径：L168的`{ "revision": self.revision, "default": self.default.public(), "stages": stages, "model_re…`。
- `environment_configuration`（L180–L190）：接收`settings`。 源码说明：Copy current settings, including explicit test/local mutations, without I/O.。 控制顺序：L190抛异常，停止当前正常路径。 调用`getattr`、`ModelConfiguration`、`ModelSettingsError`。 返回路径：L188的`ModelConfiguration(default=values, stages=stages, model_review=settings.model_review)`。
- `ModelSettingsRepository`（L193–L363）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `ModelSettingsRepository.__init__`（L194–L196）：接收`settings`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ModelSettingsRepository.snapshot`（L198–L221）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L202按`self.path.is_symlink()`分支；L203抛异常，停止当前正常路径；L206抛异常，停止当前正常路径；L210按`not stat.S_ISREG(info.st_mode) or self.path.is_symlink()`分支；L211抛异常，停止当前正常路径；L212按`os.name == "posix" and stat.S_IMODE(info.st_mode) & 0o077`分支；L213抛异常，停止当前正常路径；L215按`len(data) > MAX_CONFIG_BYTES`分支。后续分支沿下方源码相同行号继续阅读。 调用`os.open`、`getattr`、`self.path.is_symlink`、`ModelSettingsError`、`environment_configuration`、`os.fdopen`、`os.fstat`、`handle.fileno`、`stat.S_ISREG`等。 返回路径：L204的`environment_configuration(self.settings)`；L217的`ModelConfiguration.model_validate_json(data)`。
- `ModelSettingsRepository.public`（L223–L224）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.snapshot().public`、`self.snapshot`。 返回路径：L224的`self.snapshot().public()`。
- `ModelSettingsRepository.update`（L226–L250）：接收`patch`。 控制顺序：L227按`not isinstance(patch, dict) or set(patch) - { "expected_revision", "default", "stages…`分支；L233抛异常，停止当前正常路径；L234按`not isinstance(patch.get("expected_revision"), str)`分支；L235抛异常，停止当前正常路径；L240按`patch["expected_revision"] != before.revision`分支；L241抛异常，停止当前正常路径；L248抛异常，停止当前正常路径；L250抛异常，停止当前正常路径。 调用`isinstance`、`set`、`ModelSettingsError`、`patch.get`、`self.settings.data_dir.mkdir`、`FileLock`、`str`、`self.path.with_suffix`、`self.snapshot`等。 返回路径：L246的`after.public()`。
- `ModelSettingsRepository._merge`（L252–L289）：接收`before`、`patch`。 控制顺序：L256按`not isinstance(stage_patch, dict) or set(stage_patch) - set(STAGES)`分支；L257抛异常，停止当前正常路径；L259遍历`changes.items()`；L260按`not isinstance(change, dict) or set(change) - PROFILE_FIELDS`分支；L261抛异常，停止当前正常路径；L265按`isinstance(changed_url, str)`分支；L267按`"base_url" in change and changed_url != (before.default if name == "default" else bef…`分支；L272遍历`( ("provider", "auto" if name == "default" else None), ("output_m…`。后续分支沿下方源码相同行号继续阅读。 调用`before.private`、`patch.get`、`isinstance`、`set`、`ModelSettingsError`、`changes.update`、`changes.items`、`target.update`、`change.get`等。 返回路径：L289的`after`。
- `ModelSettingsRepository._check_key_destinations`（L292–L339）：接收`before`、`after`、`changes`。 控制顺序：L296遍历`("default", *STAGES)`；L300按`secret and endpoint`分支；L303遍历`("default", *STAGES)`；L315按`name != "default" and not new_key and new_url == after.default.base_url`分支；L317按`new_key in bindings and new_url and new_url not in bindings[new_key]`分支；L318抛异常，停止当前正常路径；L319按`old_url == new_url`分支；L321按`not new_url`分支。后续分支沿下方源码相同行号继续阅读。 调用`config.api_key.get_secret_value`、`bindings.setdefault(secret, set()).add`、`bindings.setdefault`、`set`、`old.api_key.get_secret_value`、`before.default.api_key.get_secret_value`、`new.api_key.get_secret_value`、`after.default.api_key.get_secret_value`、`ModelSettingsError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `ModelSettingsRepository._atomic_write`（L341–L363）：接收`configuration`。 控制顺序：L342按`self.path.is_symlink()`分支；L343抛异常，停止当前正常路径；L345按`len(payload) > MAX_CONFIG_BYTES`分支；L346抛异常，停止当前正常路径；L350按`os.name == "posix"`分支；L356按`os.name == "posix"`分支。 调用`self.path.is_symlink`、`ModelSettingsError`、`json.dumps(configuration.private(), ensure_ascii=False, indent=2)…`、`json.dumps`、`configuration.private`、`len`、`tempfile.mkstemp`、`os.fdopen`、`os.fchmod`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_same_origin`（L366–L392）：接收`request`。 控制顺序：L368按`request.headers.get("sec-fetch-site") == "cross-site"`分支；L369抛异常，停止当前正常路径；L370按`not origin`分支；L391按`not matches`分支；L392抛异常，停止当前正常路径。 调用`request.headers.get`、`HTTPException`、`urlsplit`、`str`、`default_port`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `_same_origin.default_port`（L376–L377）：接收`value`。 返回路径：L377的`value.port or (443 if value.scheme == "https" else 80)`。
- `register_model_settings_routes`（L395–L442）：接收`app`、`settings`、`auth`。 调用`ModelSettingsRepository`、`ModelConnectionTester`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `register_model_settings_routes.read_models`（L406–L411）：接收`request`、`store`。 控制顺序：L411抛异常，停止当前正常路径。 调用`Depends`、`_same_origin`、`JSONResponse`、`repository.public`、`HTTPException`、`app.get`。 返回路径：L409的`JSONResponse(repository.public(), headers={"Cache-Control": "no-store"})`。
- `register_model_settings_routes.update_models`（L415–L424）：接收`request`、`store`。 控制顺序：L422抛异常，停止当前正常路径；L424抛异常，停止当前正常路径。 调用`Depends`、`_same_origin`、`_model_request_body`、`repository.update`、`JSONResponse`、`HTTPException`、`str`、`app.patch`、`app.put`。 返回路径：L420的`JSONResponse(value, headers={"Cache-Control": "no-store"})`。
- `register_model_settings_routes.test_models`（L427–L442）：接收`request`、`store`。 控制顺序：L433抛异常，停止当前正常路径；L440抛异常，停止当前正常路径；L442抛异常，停止当前正常路径。 调用`Depends`、`_same_origin`、`_model_request_body`、`ConnectionTestRequest.model_validate`、`HTTPException`、`run_in_threadpool`、`JSONResponse`、`str`、`app.post`。 返回路径：L438的`JSONResponse(result, headers={"Cache-Control": "no-store"})`。
- `_model_request_body`（L445–L460）：接收`request`。 控制顺序：L446按`request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "applicat…`分支；L450抛异常，停止当前正常路径；L454按`size > MAX_CONFIG_BYTES`分支；L455抛异常，停止当前正常路径；L460抛异常，停止当前正常路径。 调用`request.headers.get("content-type", "").split(";", 1)[0].strip().…`、`request.headers.get("content-type", "").split(";", 1)[0].strip`、`request.headers.get("content-type", "").split`、`request.headers.get`、`HTTPException`、`request.stream`、`len`、`chunks.append`、`json.loads`等。 返回路径：L458的`json.loads(b"".join(chunks))`。

</details>

**创建路径：** `workbench/model_settings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L460。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19657`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/model_settings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2ae77603cb8c9538a84e409883c761b0c57cf1873542c14ce85a25d3c9a1d469"} -->
````python
# workbench/model_settings.py
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
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, field_validator
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
    def endpoint(cls, value):
        return validate_model_url(value) if value else ""

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
    version: int = 1
    revision: str = Field(default="0", max_length=64)
    default: ProfileConfig
    stages: dict[str, ProfileConfig]
    model_review: bool = False

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
        return ModelConfiguration(default=values, stages=stages, model_review=settings.model_review)
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
            return ModelConfiguration.model_validate_json(data)
        except ValidationError, ValueError, OSError:
            raise ModelSettingsError(
                "本机模型配置无效或不可读取；请检查文件格式和 600 权限"
            ) from None

    def public(self):
        return self.snapshot().public()

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
            after = ModelConfiguration.model_validate(values)
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
````
