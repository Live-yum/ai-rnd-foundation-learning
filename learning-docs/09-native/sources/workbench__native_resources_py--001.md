# workbench/native_resources.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：为一次运行分配隔离资源。** free_port从本机取得可用端口，for_run按run_id产生独立的数据库/Redis等资源配置和回执。资源名和范围不能从任意用户文本拼接，避免碰到既有业务数据。

**对应关系：** native_delivery → 每次运行隔离资源；test_native_managed。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `free_port`（L12–L15）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L15的`sock.getsockname()[1]`。
- `for_run`（L18–L58）：接收`settings`、`run_id`。 控制顺序：L22按`not path.exists()`分支。 调用`folder.mkdir`、`path.exists`、`write_json`、`secrets.token_urlsafe`、`secrets.token_hex`、`free_port`、`path.chmod`、`json.loads`、`path.read_text`等。 返回路径：L55的`( f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_cod…`。

</details>

**创建路径：** `workbench/native_resources.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L58。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1651`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_resources.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "08410fef921e89c257dee75f43de78d868dec1e209e674b7ce072486087aab45"} -->
````python
# workbench/native_resources.py
"""Per-run Docker services, created only after an operator chooses/approves a native stack."""

import json
import secrets
import socket

from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import run_command


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def for_run(settings, run_id):
    folder = settings.data_dir / "native-services" / run_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "services.json"
    if not path.exists():
        write_json(
            path,
            {
                "password": secrets.token_urlsafe(32),
                "project": "rnd" + secrets.token_hex(8),
                "pg_port": free_port(),
                "redis_port": free_port(),
            },
        )
        path.chmod(0o600)
    data = json.loads(path.read_text(encoding="utf-8"))
    env = folder / "services.env"
    env.write_text(
        f"POSTGRES_PASSWORD={data['password']}\nPG_PORT={data['pg_port']}\nREDIS_PORT={data['redis_port']}\nCOMPOSE_PROJECT_NAME={data['project']}\n",
        encoding="utf-8",
    )
    env.chmod(0o600)
    run_command(
        [
            "docker",
            "compose",
            "--env-file",
            str(env),
            "-f",
            str(ROOT / "templates/deployment/services.yaml"),
            "up",
            "-d",
            "--wait",
        ],
        folder,
        300,
    )
    return (
        f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_codegen",
        data["redis_port"],
    )
````
