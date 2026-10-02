# pyproject.toml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `pyproject.toml`；**本文件共有 1 段**。本段覆盖源文件 L1–L56。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1745`。本段原文以LF换行结束。

<!-- learning-source: {"path": "pyproject.toml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0425e8a1eadcc35d5204ed6f5fa6107d8e88dbaf6cc42ae34e63617cec4ed900"} -->
````toml
# pyproject.toml
[project]
name = "ai-rnd-workbench"
version = "0.1.0"
description = "Local-first, approval-gated AI software delivery workbench"
requires-python = ">=3.14,<3.15"
dependencies = [
  "fastapi>=0.128,<1",
  "uvicorn>=0.38,<1",
  "sqlalchemy>=2.0.45,<2.1",
  "alembic>=1.18,<2",
  "pydantic>=2.12,<3",
  "pydantic-settings>=2.12,<3",
  "httpx>=0.28,<0.29",
  "python-dotenv>=1,<2",
  "langgraph>=1.0,<2",
  "langgraph-checkpoint-sqlite>=3,<4",
  "tree-sitter==0.25.2",
  "tree-sitter-java==0.23.5",
  "tree-sitter-typescript==0.23.2",
  "tree-sitter-javascript==0.25.0",
  "tree-sitter-html==0.23.2",
  "mcp>=1.25,<2",
  "PyYAML==6.0.3",
  "bcrypt==5.0.0",
  "jinja2>=3.1.6,<4",
  "filelock>=3.20,<4",
  "typer>=0.20,<1",
  "langchain-openai>=1.1,<2",
  "langchain-deepseek>=1.1,<2",
]
[project.optional-dependencies]
postgres = ["psycopg[binary,pool]>=3.2.12,<4", "langgraph-checkpoint-postgres>=3,<4"]
daytona = ["daytona==0.190.0"]
[dependency-groups]
dev = ["pytest>=9,<10", "pytest-cov>=7,<8", "ruff>=0.14,<1"]
[project.scripts]
rnd = "workbench.cli:app"
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"
[tool.hatch.build.targets.wheel]
packages = ["workbench"]
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-ra --strict-markers"
markers = ["postgres: PostgreSQL integration requires TEST_DATABASE_URL", "node_tools: real optional local Node tools; required in toolchain CI"]
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F", "I"]

[tool.ruff.format]
# Source excerpts preserve exact bytes, including chunk-boundary blank lines.
# The complete underlying Python files are still formatted and linted normally.
exclude = ["learning-docs/**/sources/**"]
````
