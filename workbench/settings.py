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


def validate_model_url(value: str) -> str:
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
        if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
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

    def validate_endpoint(self):
        try:
            validate_model_url(self.base_url)
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

    def redact(self, text: str) -> str:
        # Retain old process-local keys for in-flight calls after a settings edit.
        # An invalid file must never stop error-path redaction from working.
        try:
            self.model_configuration()
        except ValueError:
            pass
        with self._model_keys_lock:
            known_keys = tuple(self._model_keys)
        for secret in sorted(known_keys, key=len, reverse=True):
            text = text.replace(secret, "[redacted]")
        for field in (
            "api_key",
            "product_postgres_url",
            "embedding_api_key",
            "daytona_api_key",
            *(stage + "_api_key" for stage in STAGES),
        ):
            secret = getattr(self, field).get_secret_value()
            if secret:
                text = text.replace(secret, "[redacted]")
        return text
