"""Configuration is relative to the checkout, never the current working directory."""
from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    base_url: str = ""
    api_key: SecretStr = SecretStr("")
    model: str = Field(default="", validation_alias=AliasChoices("MODE", "MODEL", "model"))
    data_dir: Path = ROOT / ".data"
    database_url: str = ""
    llm_timeout: float = Field(default=90, gt=0, le=600)
    max_model_calls: int = Field(default=16, ge=1, le=100)
    max_rounds: int = Field(default=10, ge=1, le=30)
    enable_coding: bool = False

    @field_validator("data_dir", mode="after")
    @classmethod
    def absolute_data_dir(cls, value: Path) -> Path:
        return (value if value.is_absolute() else ROOT / value).resolve()

    @property
    def db_url(self) -> str:
        return self.database_url or f"sqlite:///{(self.data_dir / 'workbench.db').as_posix()}"

    def prepare(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        for name in ("runs", "sources", "knowledge", "native"):
            (self.data_dir / name).mkdir(exist_ok=True)

    def require_model(self) -> None:
        from urllib.parse import urlsplit
        url = urlsplit(self.base_url)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username:
            raise ValueError("BASE_URL 必须是有效的 HTTP(S) API 根地址，不包含用户名/密码")
        if not self.api_key.get_secret_value() or not self.model:
            raise ValueError("请在 .env 填写 BASE_URL、API_KEY、MODE；MODE 是模型名称")
        if url.query or url.fragment:
            raise ValueError("BASE_URL 不得包含查询参数或片段")
