# workbench/settings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把配置转换为带类型、可校验的运行参数。** BaseSettings从.env/环境变量读字符串，再交给字段类型及验证器转换。ModelProfile负责模型端点，Settings负责目录、预算、工具和数据库；model_for按阶段选模型，更换服务商不能沿用默认密钥。redact统一清理报告中的凭据。

**对应关系：** CLI/API建立Settings → Store/Runtime/ModelGateway/本机工具；test_guided_models及test_local_only。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.local_only`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 默认地址A、默认Key A可以被同服务商的planning阶段继承。若planning只改成地址B而未提供Key B，model_for必须在HTTP之前拒绝；否则会把A的密钥发送给B。public和redact只允许显示模型身份与脱敏诊断，练习时不把秘密打印出来证明它存在。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `validate_model_url`（L28–L71）：接收`value`、`allow_insecure_http`。 源码说明：Only API roots; validate before any model credential can reach a transport.。 控制顺序：L33按`parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username is n…`分支；L44抛异常，停止当前正常路径；L45按`parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"} …`分支；L50抛异常，停止当前正常路径；L52遍历`range(3)`；L54按`decoded == path`分支；L58按`any(part in {"completions", "responses"} for part in segments)`分支；L59抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`urlsplit`、`any`、`ord`、`ValueError`、`range`、`unquote`、`path.lower().replace("\\", "/").split`、`path.lower().replace`、`path.lower`等。 返回路径：L71的`value.rstrip("/")`。
- `ModelProfile`（L74–L104）：继承`BaseModel`。声明的数据项为`stage`、`base_url`、`model`、`api_key`、`provider`、`output_mode`、`max_output_tokens`、`allow_insecure_http`；类型约束/数据库列参数以完整定义为准。
- `ModelProfile.validate_endpoint`（L86–L93）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L90抛异常，停止当前正常路径；L91按`not self.model.strip() or not self.api_key.get_secret_value().strip()`分支；L92抛异常，停止当前正常路径。 调用`validate_model_url`、`ValueError`、`self.model.strip`、`self.api_key.get_secret_value().strip`、`self.api_key.get_secret_value`。 返回路径：L93的`self`。
- `ModelProfile.public`（L95–L104）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.api_key.get_secret_value`。 返回路径：L96的`{ "stage": self.stage, "base_url": self.base_url, "model": self.model, "api_key": "configu…`。
- `Settings`（L107–L314）：继承`BaseSettings`。声明的数据项为`_model_keys`、`_model_keys_lock`、`base_url`、`api_key`、`model`、`provider`、`output_mode`、`max_output_tokens`、`allow_insecure_model_http`、`requirements_provider`、`requirements_output_mode`、`requirements_max_output_tokens`、`planning_provider`、`planning_output_mode`、`planning_max_output_tokens`、`coding_provider`、`coding_output_mode`、`coding_max_output_tokens`、`review_provider`、`review_output_mode`、`review_max_output_tokens`、`requirements_base_url`、`requirements_api_key`、`requirements_model`、`planning_base_url`、`planning_api_key`、`planning_model`、`coding_base_url`、`coding_api_key`、`coding_model`、`review_base_url`、`review_api_key`、`review_model`、`model_review`、`data_dir`、`database_url`、`product_postgres_url`、`llm_timeout`、`max_model_calls`、`max_rounds`、`max_context_chars`、`install_products`、`enable_coding`、`max_repair_attempts`、`tool_timeout`、`coding_engine`、`module_coding_engine`、`aider_executable`、`repo_map_provider`、`retrieval_engine`、`repo_map_chars`、`embedding_base_url`、`embedding_api_key`、`embedding_model`、`embedding_enabled`、`embedding_max_chunks`、`sandbox_provider`、`daytona_api_url`、`daytona_api_key`、`daytona_target`、`daytona_snapshot`、`daytona_snapshots`、`daytona_runtime_timeout`、`daytona_allow_local_execution`、`daytona_capture_startup_diagnostics`、`capability_execution_enabled`、`capability_profile_directory`、`capability_browser_image`、`checkpoint_url`、`host`、`port`；类型约束/数据库列参数以完整定义为准。
- `Settings.only_local_tools`（L199–L200）：接收`value`。 调用`local_http_url`、`field_validator`。 返回路径：L200的`local_http_url(value)`。
- `Settings.only_local_databases`（L204–L205）：接收`value`。 调用`local_database_url`、`field_validator`。 返回路径：L205的`local_database_url(value)`。
- `Settings.absolute_data_dir`（L209–L210）：接收`value`。 调用`(value if value.is_absolute() else ROOT / value).resolve`、`value.is_absolute`、`field_validator`。 返回路径：L210的`(value if value.is_absolute() else ROOT / value).resolve()`。
- `Settings.db_url`（L213–L217）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`local_database_url`、`(self.data_dir / 'workbench.db').as_posix`。 返回路径：L214的`local_database_url(self.database_url) or f"sqlite:///{(self.data_dir / 'workbench.db').as_…`。
- `Settings.prepare`（L219–L222）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L221遍历`("runs", "sources", "knowledge", "native")`。 调用`self.data_dir.mkdir`、`(self.data_dir / name).mkdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Settings.model_configuration`（L224–L229）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`ModelSettingsRepository(self).snapshot`、`ModelSettingsRepository`、`self._remember_model_keys`。 返回路径：L229的`configuration`。
- `Settings._remember_model_keys`（L231–L236）：接收`configuration`。 控制顺序：L233遍历`(configuration.default, *configuration.stages.values())`；L235按`secret`分支。 调用`configuration.stages.values`、`profile.api_key.get_secret_value`、`self._model_keys.add`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Settings.model_for`（L238–L239）：接收`stage`。 调用`self.model_configuration().profile`、`self.model_configuration`。 返回路径：L239的`self.model_configuration().profile(stage)`。
- `Settings.require_model`（L241–L243）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_configuration().require_model`、`self.model_configuration`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Settings.models_ready`（L245–L250）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.require_model`。 返回路径：L249的`False`；L250的`True`。
- `Settings.review_enabled`（L253–L254）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.model_configuration`。 返回路径：L254的`self.model_configuration().review_enabled`。
- `Settings.redaction_secrets`（L256–L274）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L264遍历`( "api_key", "product_postgres_url", "embedding_api_key", "dayton…`；L272按`value`分支。 调用`self.model_configuration`、`set`、`getattr(self, field).get_secret_value`、`getattr`、`values.add`、`sorted`。 返回路径：L274的`sorted((value for value in values if value), key=len, reverse=True)`。
- `Settings.redact`（L276–L279）：接收`text`。 控制顺序：L277遍历`self.redaction_secrets()`。 调用`self.redaction_secrets`、`text.replace`。 返回路径：L279的`text`。
- `Settings.redact_fragments`（L281–L299）：接收`fragments`。 源码说明：Hide all pieces of a newly registered secret in historical SSE replay.。 控制顺序：L285遍历`self.redaction_secrets()`；L287在`start >= 0`成立时循环；L291遍历`fragments`。 调用`"".join`、`self.redaction_secrets`、`joined.find`、`spans.append`、`len`、`result.append`、`any`。 返回路径：L299的`result`。
- `Settings.redact_data`（L301–L314）：接收`value`。 源码说明：Redact JSON string leaves and keys before escaping; preserve inputs.。 控制顺序：L303按`isinstance(value, str)`分支；L305按`isinstance(value, dict)`分支；L310按`isinstance(value, list)`分支；L312按`isinstance(value, tuple)`分支。 调用`isinstance`、`self.redact`、`self.redact_data`、`value.items`、`tuple`。 返回路径：L304的`self.redact(value)`；L306的`{ self.redact(key) if isinstance(key, str) else key: self.redact_data(item) for key, item …`；L311的`[self.redact_data(item) for item in value]`。

</details>

**创建路径：** `workbench/settings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L314。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`12567`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/settings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9e2ffd3dc099dfd980b9040905f0d9af161804028522d956568ae581822074a4"} -->
````python
# workbench/settings.py
"""Local configuration and optional per-stage model profiles; no secrets in run receipts."""

from pathlib import Path
from threading import RLock
from typing import Literal
from urllib.parse import unquote, urlsplit

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    SecretStr,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from workbench.local_only import local_database_url, local_http_url

ROOT = Path(__file__).resolve().parent.parent
Stage = Literal["requirements", "planning", "coding", "review"]
STAGES = ("requirements", "planning", "coding", "review")
Provider = Literal["auto", "openai", "deepseek", "compatible"]
OutputMode = Literal["auto", "json_object"]


def validate_model_url(value: str, *, allow_insecure_http: bool = False) -> str:
    """Only API roots; validate before any model credential can reach a transport."""
    message = "BASE_URL 必须是无凭据/查询参数的 HTTP(S) API 根地址"
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or "?" in value
            or "#" in value
            or "\\" in value
            or any(ord(char) <= 32 or ord(char) == 127 for char in value)
            or parsed.port == 0
        ):
            raise ValueError(message)
        if (
            parsed.scheme == "http"
            and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            and not allow_insecure_http
        ):
            raise ValueError("远程模型必须使用 HTTPS")
        path = parsed.path
        for _ in range(3):
            decoded = unquote(path)
            if decoded == path:
                break
            path = decoded
        segments = path.lower().replace("\\", "/").split("/")
        if any(part in {"completions", "responses"} for part in segments):
            raise ValueError(
                "BASE_URL 只填 API 根地址，不要重复 /chat/completions 或其他推理子路径"
            )
    except ValueError as exc:
        # URL parsers may echo invalid ports/hosts. Return only our fixed messages.
        if str(exc) in {
            message,
            "远程模型必须使用 HTTPS",
            "BASE_URL 只填 API 根地址，不要重复 /chat/completions 或其他推理子路径",
        }:
            raise ValueError(str(exc)) from None
        raise ValueError(message) from None
    return value.rstrip("/")


class ModelProfile(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True)
    stage: str
    base_url: str
    model: str
    api_key: SecretStr
    provider: Provider = "auto"
    output_mode: OutputMode = "auto"
    max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    # Supplied only by the operator's process configuration, never by a model or API patch.
    allow_insecure_http: bool = Field(default=False, exclude=True)

    def validate_endpoint(self):
        try:
            validate_model_url(self.base_url, allow_insecure_http=self.allow_insecure_http)
        except ValueError as exc:
            raise ValueError(f"{self.stage}: {exc}") from None
        if not self.model.strip() or not self.api_key.get_secret_value().strip():
            raise ValueError(f"{self.stage}: 请填写 MODE/模型名称及 API_KEY")
        return self

    def public(self):
        return {
            "stage": self.stage,
            "base_url": self.base_url,
            "model": self.model,
            "api_key": "configured" if self.api_key.get_secret_value() else "missing",
            "provider": self.provider,
            "output_mode": self.output_mode,
            "max_output_tokens": self.max_output_tokens,
        }


class Settings(BaseSettings):
    _model_keys: set[str] = PrivateAttr(default_factory=set)
    _model_keys_lock: RLock = PrivateAttr(default_factory=RLock)
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    base_url: str = ""
    api_key: SecretStr = SecretStr("")
    model: str = Field(default="", validation_alias=AliasChoices("MODE", "MODEL", "model"))
    provider: Provider = "auto"
    output_mode: OutputMode = "auto"
    max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    allow_insecure_model_http: bool = False
    requirements_provider: Provider | None = None
    requirements_output_mode: OutputMode | None = None
    requirements_max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    planning_provider: Provider | None = None
    planning_output_mode: OutputMode | None = None
    planning_max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    coding_provider: Provider | None = None
    coding_output_mode: OutputMode | None = None
    coding_max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    review_provider: Provider | None = None
    review_output_mode: OutputMode | None = None
    review_max_output_tokens: int | None = Field(default=None, ge=1, le=393216)
    requirements_base_url: str = ""
    requirements_api_key: SecretStr = SecretStr("")
    requirements_model: str = Field(
        default="",
        validation_alias=AliasChoices(
            "REQUIREMENTS_MODE", "REQUIREMENTS_MODEL", "requirements_model"
        ),
    )
    planning_base_url: str = ""
    planning_api_key: SecretStr = SecretStr("")
    planning_model: str = Field(
        default="",
        validation_alias=AliasChoices("PLANNING_MODE", "PLANNING_MODEL", "planning_model"),
    )
    coding_base_url: str = ""
    coding_api_key: SecretStr = SecretStr("")
    coding_model: str = Field(
        default="", validation_alias=AliasChoices("CODING_MODE", "CODING_MODEL", "coding_model")
    )
    review_base_url: str = ""
    review_api_key: SecretStr = SecretStr("")
    review_model: str = Field(
        default="", validation_alias=AliasChoices("REVIEW_MODE", "REVIEW_MODEL", "review_model")
    )
    model_review: bool = False
    data_dir: Path = ROOT / ".data"
    database_url: str = ""
    product_postgres_url: SecretStr = SecretStr("")
    llm_timeout: float = Field(default=90, gt=0, le=600)
    # Zero means no lifetime limit; retry safety is separate and remains bounded.
    max_model_calls: int = Field(default=0, ge=0, le=100000)
    max_rounds: int = Field(default=0, ge=0, le=100000)
    max_context_chars: int = Field(default=100000, ge=10000, le=300000)
    install_products: bool = True
    enable_coding: bool = True
    max_repair_attempts: int = Field(default=2, ge=0, le=2)
    tool_timeout: int = Field(default=180, ge=10, le=900)
    coding_engine: Literal["bounded", "aider"] = "bounded"
    module_coding_engine: Literal["structured", "openhands"] = "structured"
    aider_executable: str = ""
    repo_map_provider: Literal["symbols", "aider"] = "symbols"
    retrieval_engine: Literal["local", "continue"] = "local"
    repo_map_chars: int = Field(default=12000, ge=1000, le=40000)
    embedding_base_url: str = "http://127.0.0.1:11434/v1"
    embedding_api_key: SecretStr = SecretStr("local-no-auth")
    embedding_model: str = Field(
        default="", validation_alias=AliasChoices("EMBEDDING_MODE", "embedding_model")
    )
    embedding_enabled: bool = False
    embedding_max_chunks: int = Field(default=500, ge=1, le=40000)
    sandbox_provider: Literal["local", "daytona"] = "local"
    daytona_api_url: str = "http://127.0.0.1:3000/api"
    daytona_api_key: SecretStr = SecretStr("")
    daytona_target: str = "local"
    daytona_snapshot: str = ""
    daytona_snapshots: dict[str, str] = Field(default_factory=dict)
    daytona_runtime_timeout: int = Field(default=3600, ge=60, le=7200)
    daytona_allow_local_execution: bool = False
    daytona_capture_startup_diagnostics: bool = False
    # Controller configuration only; a generated plan cannot enable execution.
    capability_execution_enabled: bool = False
    capability_profile_directory: Path = ROOT / ".data/daytona-capability"
    capability_browser_image: str = ""
    checkpoint_url: str = ""
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1024, le=65535)

    @field_validator("daytona_api_url", "embedding_base_url")
    @classmethod
    def only_local_tools(cls, value: str) -> str:
        return local_http_url(value)

    @field_validator("database_url", "checkpoint_url")
    @classmethod
    def only_local_databases(cls, value: str) -> str:
        return local_database_url(value)

    @field_validator("data_dir", mode="after")
    @classmethod
    def absolute_data_dir(cls, value: Path) -> Path:
        return (value if value.is_absolute() else ROOT / value).resolve()

    @property
    def db_url(self) -> str:
        return (
            local_database_url(self.database_url)
            or f"sqlite:///{(self.data_dir / 'workbench.db').as_posix()}"
        )

    def prepare(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for name in ("runs", "sources", "knowledge", "native"):
            (self.data_dir / name).mkdir(exist_ok=True)

    def model_configuration(self):
        from workbench.model_settings import ModelSettingsRepository

        configuration = ModelSettingsRepository(self).snapshot()
        self._remember_model_keys(configuration)
        return configuration

    def _remember_model_keys(self, configuration):
        with self._model_keys_lock:
            for profile in (configuration.default, *configuration.stages.values()):
                secret = profile.api_key.get_secret_value()
                if secret:
                    self._model_keys.add(secret)

    def model_for(self, stage: Stage) -> ModelProfile:
        return self.model_configuration().profile(stage)

    def require_model(self) -> None:
        # One snapshot for all stages prevents mixing revisions during validation.
        self.model_configuration().require_model()

    def models_ready(self) -> bool:
        try:
            self.require_model()
        except ValueError:
            return False
        return True

    @property
    def review_enabled(self) -> bool:
        return self.model_configuration().review_enabled

    def redaction_secrets(self):
        # Retain old process-local values while in-flight calls finish.
        try:
            self.model_configuration()
        except ValueError:
            pass
        with self._model_keys_lock:
            values = set(self._model_keys)
        for field in (
            "api_key",
            "product_postgres_url",
            "embedding_api_key",
            "daytona_api_key",
            *(stage + "_api_key" for stage in STAGES),
        ):
            value = getattr(self, field).get_secret_value()
            if value:
                values.add(value)
        return sorted((value for value in values if value), key=len, reverse=True)

    def redact(self, text: str) -> str:
        for secret in self.redaction_secrets():
            text = text.replace(secret, "[redacted]")
        return text

    def redact_fragments(self, fragments):
        """Hide all pieces of a newly registered secret in historical SSE replay."""
        joined = "".join(fragments)
        spans = []
        for secret in self.redaction_secrets():
            start = joined.find(secret)
            while start >= 0:
                spans.append((start, start + len(secret)))
                start = joined.find(secret, start + 1)
        result, offset = [], 0
        for fragment in fragments:
            end = offset + len(fragment)
            result.append(
                "[redacted]"
                if any(left < end and right > offset for left, right in spans)
                else fragment
            )
            offset = end
        return result

    def redact_data(self, value):
        """Redact JSON string leaves and keys before escaping; preserve inputs."""
        if isinstance(value, str):
            return self.redact(value)
        if isinstance(value, dict):
            return {
                self.redact(key) if isinstance(key, str) else key: self.redact_data(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self.redact_data(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self.redact_data(item) for item in value)
        return value
````
