"""Local configuration and optional per-stage model profiles; no secrets in run receipts."""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import AliasChoices, BaseModel, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from workbench.local_only import local_database_url, local_http_url

ROOT = Path(__file__).resolve().parent.parent
Stage = Literal["requirements", "planning", "coding", "review"]
STAGES = ("requirements", "planning", "coding", "review")


class ModelProfile(BaseModel):
    stage: str
    base_url: str
    model: str
    api_key: SecretStr

    def validate_endpoint(self):
        url = urlsplit(self.base_url)
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username
            or url.password
            or url.query
            or url.fragment
        ):
            raise ValueError(f"{self.stage}: BASE_URL 必须是无凭据/查询参数的 HTTP(S) API 根地址")
        if url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise ValueError(f"{self.stage}: 远程模型必须使用 HTTPS")
        if not self.model or not self.api_key.get_secret_value():
            raise ValueError(f"{self.stage}: 请填写 MODE/模型名称及 API_KEY")
        if self.base_url.rstrip("/").endswith("/chat/completions"):
            raise ValueError(f"{self.stage}: BASE_URL 只填 API 根地址，不要重复 /chat/completions")
        return self

    def public(self):
        return {
            "stage": self.stage,
            "base_url": self.base_url,
            "model": self.model,
            "api_key": "configured" if self.api_key.get_secret_value() else "missing",
        }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    base_url: str = ""
    api_key: SecretStr = SecretStr("")
    model: str = Field(default="", validation_alias=AliasChoices("MODE", "MODEL", "model"))
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

    def model_for(self, stage: Stage) -> ModelProfile:
        if stage not in STAGES:
            raise ValueError("未知模型阶段")
        endpoint = getattr(self, stage + "_base_url") or self.base_url
        key = getattr(self, stage + "_api_key")
        if not key.get_secret_value():
            if endpoint.rstrip("/") != self.base_url.rstrip("/"):
                raise ValueError(
                    f"{stage}: 更换服务商地址时必须单独配置 {stage.upper()}_API_KEY，禁止发送默认密钥到新地址"
                )
            key = self.api_key
        return ModelProfile(
            stage=stage,
            base_url=endpoint.rstrip("/"),
            model=getattr(self, stage + "_model") or self.model,
            api_key=key,
        )

    def require_model(self) -> None:
        for stage in STAGES[:3]:
            self.model_for(stage).validate_endpoint()
        if self.review_enabled:
            self.model_for("review").validate_endpoint()

    @property
    def review_enabled(self) -> bool:
        return bool(
            self.model_review
            or self.review_model
            or self.review_base_url
            or self.review_api_key.get_secret_value()
        )

    def redact(self, text: str) -> str:
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
