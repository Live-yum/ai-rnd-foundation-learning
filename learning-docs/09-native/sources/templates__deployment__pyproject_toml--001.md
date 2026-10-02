# templates/deployment/pyproject.toml · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生独立交付启动器。** 该文件随成品复制，负责本机数据库初始化、业务/菜单SQL恢复和前后端启动。helper文件来自portable.HELPERS的明确清单，不允许从原开发目录隐式导入。

**对应关系：** portable.build_native_delivery → 新目录运行start.py → 新数据库复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/deployment/pyproject.toml`；**本文件共有 1 段**。本段覆盖源文件 L1–L7。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`309`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/deployment/pyproject.toml", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fa23811d541059d3346cdc3d397829925436ee59eda37cbeca54facbb58a3bbe"} -->
````toml
# templates/deployment/pyproject.toml
[project]
name = "native-product-launcher"
version = "0.1.0"
requires-python = ">=3.14,<3.15"
dependencies = ["sqlalchemy>=2.0.45,<2.1", "psycopg[binary]>=3.2.12,<4", "httpx>=0.28,<0.29", "pydantic>=2.12,<3", "pydantic-settings>=2.12,<3", "filelock>=3.20,<4", "python-dotenv>=1,<2"]
[tool.uv]
package = false
````
