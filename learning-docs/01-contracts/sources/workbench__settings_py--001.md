# workbench/settings.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：把配置转换为带类型、可校验的运行参数。** BaseSettings从.env/环境变量读字符串，再交给字段类型及验证器转换。ModelProfile负责模型端点，Settings负责目录、预算、工具和数据库；model_for按阶段选模型，更换服务商不能沿用默认密钥。redact统一清理报告中的凭据。

**对应关系：** CLI/API建立Settings → Store/Runtime/ModelGateway/本机工具；test_guided_models及test_local_only。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.local_only`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 默认地址A、默认Key A可以被同服务商的planning阶段继承。若planning只改成地址B而未提供Key B，model_for必须在HTTP之前拒绝；否则会把A的密钥发送给B。public和redact只允许显示模型身份与脱敏诊断，练习时不把秘密打印出来证明它存在。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ModelProfile`（L19–L56）：继承`BaseModel`。声明的数据项为`stage`、`base_url`、`model`、`api_key`、`provider`、`output_mode`、`max_output_tokens`；类型约束/数据库列参数以完整定义为准。
- `ModelProfile.validate_endpoint`（L28–L45）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L30按`url.scheme not in {"http", "https"} or not url.hostname or url.username or url.passwo…`分支；L38抛异常，停止当前正常路径；L39按`url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"}`分支；L40抛异常，停止当前正常路径；L41按`not self.model or not self.api_key.get_secret_value()`分支；L42抛异常，停止当前正常路径；L43按`self.base_url.rstrip("/").endswith("/chat/completions")`分支；L44抛异常，停止当前正常路径。 调用`urlsplit`、`ValueError`、`self.api_key.get_secret_value`、`self.base_url.rstrip("/").endswith`、`self.base_url.rstrip`。 返回路径：L45的`self`。
- `ModelProfile.public`（L47–L56）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`self.api_key.get_secret_value`。 返回路径：L48的`{ "stage": self.stage, "base_url": self.base_url, "model": self.model, "api_key": "configu…`。
- `Settings`（L59–L223）：继承`BaseSettings`。声明的数据项为`base_url`、`api_key`、`model`、`provider`、`output_mode`、`max_output_tokens`、`requirements_provider`、`requirements_output_mode`、`requirements_max_output_tokens`、`planning_provider`、`planning_output_mode`、`planning_max_output_tokens`、`coding_provider`、`coding_output_mode`、`coding_max_output_tokens`、`review_provider`、`review_output_mode`、`review_max_output_tokens`、`requirements_base_url`、`requirements_api_key`、`requirements_model`、`planning_base_url`、`planning_api_key`、`planning_model`、`coding_base_url`、`coding_api_key`、`coding_model`、`review_base_url`、`review_api_key`、`review_model`、`model_review`、`data_dir`、`database_url`、`product_postgres_url`、`llm_timeout`、`max_model_calls`、`max_rounds`、`max_context_chars`、`install_products`、`enable_coding`、`max_repair_attempts`、`tool_timeout`、`coding_engine`、`aider_executable`、`repo_map_provider`、`retrieval_engine`、`repo_map_chars`、`embedding_base_url`、`embedding_api_key`、`embedding_model`、`embedding_enabled`、`embedding_max_chunks`、`sandbox_provider`、`daytona_api_url`、`daytona_api_key`、`daytona_target`、`daytona_snapshot`、`daytona_snapshots`、`daytona_runtime_timeout`、`daytona_allow_local_execution`、`daytona_capture_startup_diagnostics`、`checkpoint_url`、`host`、`port`；类型约束/数据库列参数以完整定义为准。
- `Settings.only_local_tools`（L143–L144）：接收`value`。 调用`local_http_url`、`field_validator`。 返回路径：L144的`local_http_url(value)`。
- `Settings.only_local_databases`（L148–L149）：接收`value`。 调用`local_database_url`、`field_validator`。 返回路径：L149的`local_database_url(value)`。
- `Settings.absolute_data_dir`（L153–L154）：接收`value`。 调用`(value if value.is_absolute() else ROOT / value).resolve`、`value.is_absolute`、`field_validator`。 返回路径：L154的`(value if value.is_absolute() else ROOT / value).resolve()`。
- `Settings.db_url`（L157–L161）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`local_database_url`、`(self.data_dir / 'workbench.db').as_posix`。 返回路径：L158的`local_database_url(self.database_url) or f"sqlite:///{(self.data_dir / 'workbench.db').as_…`。
- `Settings.prepare`（L163–L166）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L165遍历`("runs", "sources", "knowledge", "native")`。 调用`self.data_dir.mkdir`、`(self.data_dir / name).mkdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Settings.model_for`（L168–L195）：接收`stage`。 控制顺序：L169按`stage not in STAGES`分支；L170抛异常，停止当前正常路径；L173按`not key.get_secret_value()`分支；L174按`endpoint.rstrip("/") != self.base_url.rstrip("/")`分支；L175抛异常，停止当前正常路径。 调用`ValueError`、`getattr`、`key.get_secret_value`、`endpoint.rstrip`、`self.base_url.rstrip`、`stage.upper`、`ModelProfile`。 返回路径：L179的`ModelProfile( stage=stage, base_url=endpoint.rstrip("/"), model=getattr(self, stage + "_mo…`。
- `Settings.require_model`（L197–L201）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L198遍历`STAGES[:3]`；L200按`self.review_enabled`分支。 调用`self.model_for(stage).validate_endpoint`、`self.model_for`、`self.model_for("review").validate_endpoint`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Settings.review_enabled`（L204–L210）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`bool`、`self.review_api_key.get_secret_value`。 返回路径：L205的`bool( self.model_review or self.review_model or self.review_base_url or self.review_api_ke…`。
- `Settings.redact`（L212–L223）：接收`text`。 控制顺序：L213遍历`( "api_key", "product_postgres_url", "embedding_api_key", "dayton…`；L221按`secret`分支。 调用`getattr(self, field).get_secret_value`、`getattr`、`text.replace`。 返回路径：L223的`text`。

</details>

**创建路径：** `workbench/settings.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L223。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9354`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/settings.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7df8f5eb535bc8093f45cb057e0345f2e83a5b15638902ea52b3a8bbbefe199d"} -->
````python
# workbench/settings.py
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
Provider = Literal["auto", "openai", "deepseek", "compatible"]
OutputMode = Literal["auto", "json_object"]


class ModelProfile(BaseModel):
    stage: str
    base_url: str
    model: str
    api_key: SecretStr
    provider: Provider = "auto"
    output_mode: OutputMode = "auto"
    max_output_tokens: int | None = Field(default=None, ge=1, le=393216)

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
            "provider": self.provider,
            "output_mode": self.output_mode,
            "max_output_tokens": self.max_output_tokens,
        }


class Settings(BaseSettings):
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
            # An endpoint change must not inherit the previous provider's wire protocol.
            provider=getattr(self, stage + "_provider")
            or (self.provider if endpoint.rstrip("/") == self.base_url.rstrip("/") else "auto"),
            output_mode=getattr(self, stage + "_output_mode")
            or (self.output_mode if endpoint.rstrip("/") == self.base_url.rstrip("/") else "auto"),
            max_output_tokens=getattr(self, stage + "_max_output_tokens")
            or (
                self.max_output_tokens
                if endpoint.rstrip("/") == self.base_url.rstrip("/")
                else None
            ),
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
````
