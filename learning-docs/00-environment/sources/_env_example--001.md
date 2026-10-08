# .env.example · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `.env.example`；**本文件共有 1 段**。本段覆盖源文件 L1–L82。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3430`。本段原文以LF换行结束。

<!-- learning-source: {"path": ".env.example", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a0a9581675464892544ad62089954fc07f685bde5c412a4d29b1dae42b87b9b1"} -->
````text
# .env.example
# Default model: MODE is the provider's model ID, not dev/prod or reasoning mode.
BASE_URL=
API_KEY=
MODE=
# Keep false unless you explicitly use a trusted HTTP model gateway.
# HTTP sends credentials without transport encryption; HTTPS remains the default.
# ALLOW_INSECURE_MODEL_HTTP=false
# Structured output uses the shared LangChain with_structured_output JSON-mode pipeline.
# PROVIDER=auto  # auto, openai, deepseek, compatible; explicit provider useful for proxies
# OUTPUT_MODE=auto  # auto or json_object
# MAX_OUTPUT_TOKENS=16384  # defaults: DeepSeek 65536, others 16384

# Optional stage overrides. Omitted fields inherit the default.
# A DIFFERENT BASE_URL requires the stage's OWN API_KEY (no cross-provider key leakage).
# REQUIREMENTS_BASE_URL=
# REQUIREMENTS_API_KEY=
# REQUIREMENTS_MODE=
# PLANNING_BASE_URL=
# PLANNING_API_KEY=
# PLANNING_MODE=
# CODING_BASE_URL=
# CODING_API_KEY=
# CODING_MODE=
# REVIEW_BASE_URL=
# REVIEW_API_KEY=
# REVIEW_MODE=
# Every stage also supports *_PROVIDER, *_OUTPUT_MODE, *_MAX_OUTPUT_TOKENS.
# Example: PLANNING_PROVIDER=deepseek; PLANNING_OUTPUT_MODE=json_object
# See docs/provider-structured-outputs.md; no real OpenAI validation is implied.
# MODEL_REVIEW=false

# 0 = no cumulative manual-conversation/model-call limit.
# HTTP attempts and automatic code repair remain bounded independently.
MAX_ROUNDS=0
MAX_MODEL_CALLS=0
# MAX_CONTEXT_CHARS=100000
# MAX_REPAIR_ATTEMPTS=2
# LLM_TIMEOUT=90
# TOOL_TIMEOUT=180
# ENABLE_CODING=true
# PORT=8000
# DATA_DIR=.data

# Platform control database only (default SQLite, no server).
# DATABASE_URL=postgresql+psycopg://user:password@127.0.0.1:5432/workbench
# CHECKPOINT_URL=

# Optional local PostgreSQL admin URL used for disposable generated-product TEST databases.
# Omit to let selected PostgreSQL product validation use Docker.
# PRODUCT_POSTGRES_URL=postgresql+psycopg://user:password@127.0.0.1:5432/postgres

# Native platform-run overrides are optional. By default create owned per-run Docker services.
# Follow the handbook before authorizing an existing dedicated EMPTY *_codegen database.
# NATIVE_FASTAPIADMIN_DATABASE_URL=postgresql+psycopg://native:password@127.0.0.1:5432/project_codegen
# NATIVE_YUDAO_DATABASE_URL=postgresql+psycopg://native:password@127.0.0.1:5432/project_codegen

# 本地上下文默认不调用模型；Aider在独立Python3.12环境安装
REPO_MAP_PROVIDER=symbols
REPO_MAP_CHARS=12000
CODING_ENGINE=bounded
AIDER_EXECUTABLE=
# 可选向量模型必须在本机；默认不计算向量，AST/FTS5始终在本地工作
EMBEDDING_BASE_URL=http://127.0.0.1:11434/v1
EMBEDDING_API_KEY=local-no-auth
EMBEDDING_MODE=
EMBEDDING_ENABLED=false
EMBEDDING_MAX_CHUNKS=500
# 本机直接验证始终执行。Daytona仅为附加的本机自托管关卡
SANDBOX_PROVIDER=local
DAYTONA_API_URL=http://127.0.0.1:3000/api
DAYTONA_API_KEY=
DAYTONA_TARGET=local
DAYTONA_SNAPSHOT=
DAYTONA_ALLOW_LOCAL_EXECUTION=false

# Optional actual Continue FTS component (local by default: no Node required).
# Install/build tools/node first, then select continue to combine its FTS with AST/vector retrieval.
RETRIEVAL_ENGINE=local

# 每个技术栈使用自己的本机离线快照；值来自 snapshot-image.json，不能填云端地址。
# DAYTONA_SNAPSHOTS={"python-basic/postgresql":"实际快照名","fastapiadmin/postgresql":"实际快照名","yudao-vben/postgresql":"实际快照名"}
DAYTONA_RUNTIME_TIMEOUT=3600
````
