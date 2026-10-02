# templates/deployment/entry.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生独立交付启动器。** 该文件随成品复制，负责本机数据库初始化、业务/菜单SQL恢复和前后端启动。helper文件来自portable.HELPERS的明确清单，不允许从原开发目录隐式导入。

**对应关系：** portable.build_native_delivery → 新目录运行start.py → 新数据库复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**执行顺序：** 本文件没有函数入口，模块导入时按从上到下执行顶层语句。

**创建路径：** `templates/deployment/entry.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L21。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`551`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/deployment/entry.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "620b1d2c46046b776bc6e2de7e424ddf374e7f16da84cb70379842d0932e1545"} -->
````python
# templates/deployment/entry.py
"""Standalone native delivery entrypoint. Requires uv and the original language tools."""

import os
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    args = [
        "uv",
        "run",
        "--locked",
        "--project",
        str(root / "deployment"),
        "python",
        str(root / "deployment/run.py"),
        *sys.argv[1:],
    ]
    result = subprocess.run(args, cwd=root, env=os.environ.copy(), check=False)
    raise SystemExit(result.returncode)
````
