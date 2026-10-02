# templates/product/pyproject.toml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 独立产品的Python依赖清单，与平台环境分开；先由uv按对应uv.lock安装，再启动产品，不能依赖开发平台碰巧装过的库。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/product/pyproject.toml`；**本文件共有 1 段**。本段覆盖源文件 L1–L10。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`340`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/pyproject.toml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "305705f01bf34e59b3525e7b78279ab0f7a09df96209f59971de799d5f6f2fe9"} -->
````toml
# templates/product/pyproject.toml
[project]
name = "generated-business-app"
version = "0.1.0"
requires-python = ">=3.14,<3.15"
dependencies = ["fastapi>=0.128,<1", "uvicorn>=0.38,<1", "sqlalchemy>=2.0.45,<2.1", "alembic>=1.18,<2", "pydantic>=2.12,<3", "httpx>=0.28,<0.29"]
[tool.uv]
package = false

[project.optional-dependencies]
postgres = ["psycopg[binary]>=3.2.12,<4"]
````
