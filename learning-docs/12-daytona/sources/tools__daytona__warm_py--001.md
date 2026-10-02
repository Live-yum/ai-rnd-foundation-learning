# tools/daytona/warm.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本机Daytona的预热镜像。** Dockerfile逐层准备Python运行时和产品锁定依赖；只在显式构建时下载软件。网络封锁后的沙箱使用已有缓存离线安装，创建的是本机镜像而非云端工作区。

**对应关系：** scripts.daytona_local snapshot-image → 本机Registry → scripts.daytona_bootstrap snapshot。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run`（L12–L13）：接收`argv`、`cwd`。 调用`subprocess.run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tools/daytona/warm.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L48。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1587`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/daytona/warm.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "06b6517f01cb686e60ef65311e16f06de51544448bad9f45fac7c29c1cf430bc"} -->
````python
# tools/daytona/warm.py
"""Prewarm only locked build dependencies; this is not runtime acceptance evidence."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/opt/rnd")
profile = json.loads((ROOT / "profile.json").read_text())
product = ROOT / "prewarm/product"


def run(argv, cwd):
    subprocess.run(argv, cwd=cwd, check=True, timeout=1800)


if profile["template"] == "python-basic":
    run(
        ["uv", "sync", "--locked", "--no-dev", "--extra", "postgres", "--python", "3.14.7"], product
    )
else:
    import sys

    sys.path.insert(0, str(product / "deployment"))
    from workbench.native_environment import install_backend, native_environment
    from workbench.native_frontend import build_frontend, frontend_environment

    template = profile["template"]
    backend = product / "backend"
    frontend = product / ("frontend/web" if template == "fastapiadmin" else "frontend-product")
    native_environment(
        template,
        backend,
        "postgresql+psycopg://warm:unused@127.0.0.1:5432/warm_codegen",
        8001 if template == "fastapiadmin" else 48080,
    )
    run(["uv", "sync", "--locked", "--python", "3.14.7"], product / "deployment")
    install_backend(template, backend, ROOT / "warm-reports")
    build_frontend(
        template,
        frontend,
        frontend_environment(
            template,
            "http://127.0.0.1:48080" if template == "yudao-vben" else "http://127.0.0.1:8001",
        ),
        ROOT / "warm-reports",
        prepared=True,
    )
print("Locked native dependencies prepared; no runtime result asserted.")
````
