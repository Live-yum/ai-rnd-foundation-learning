# workbench/infrastructure/native/resources.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：为一次运行分配隔离资源。** free_port从本机取得可用端口，for_run按run_id产生独立的数据库/Redis等资源配置和回执。资源名和范围不能从任意用户文本拼接，避免碰到既有业务数据。

**对应关系：** native_delivery → 每次运行隔离资源；test_native_managed。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.infrastructure.processes.tools`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `NativeServiceUnavailable`（L13–L14）：继承`ToolFailure`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `start_services`（L17–L45）：接收`command`、`folder`。 控制顺序：L25按`any( marker in diagnostic for marker in ( "permission denied", "access is denied", "a…`分支；L37抛异常，停止当前正常路径；L40按`"cannot connect to the docker daemon" in diagnostic or "is the docker daemon running?…`分支；L44抛异常，停止当前正常路径；L45抛异常，停止当前正常路径。 调用`run_command`、`getattr(exc, "log", "").casefold`、`getattr`、`any`、`PermissionError`、`NativeServiceUnavailable`。 返回路径：L19的`run_command(command, folder, 300)`。
- `free_port`（L48–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L51的`sock.getsockname()[1]`。
- `for_run`（L54–L95）：接收`settings`、`run_id`。 控制顺序：L55按`not shutil.which("docker")`分支；L56抛异常，停止当前正常路径；L60按`not path.exists()`分支。 调用`shutil.which`、`NativeServiceUnavailable`、`folder.mkdir`、`path.exists`、`write_json`、`secrets.token_urlsafe`、`secrets.token_hex`、`free_port`、`path.chmod`等。 返回路径：L92的`( f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_cod…`。

</details>

**创建路径：** `workbench/infrastructure/native/resources.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L95。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3110`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/infrastructure/native/resources.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "939a30ede4a4ca92f27f76d107360458de7de65ac95c4cbacc0f1db379594ab2"} -->
````python
# workbench/infrastructure/native/resources.py
"""Per-run Docker services, created only after an operator chooses/approves a native stack."""

import json
import secrets
import shutil
import socket

from workbench.filesystem import write_json
from workbench.infrastructure.processes.tools import ToolFailure, run_command
from workbench.settings import ROOT


class NativeServiceUnavailable(ToolFailure):
    """A known local service availability failure, never an authorization failure."""


def start_services(command, folder):
    try:
        return run_command(command, folder, 300)
    except ToolFailure as exc:
        # Docker often reports socket authorization errors after a successful spawn.
        # Its CLI has no structured error protocol: classify only known availability
        # diagnostics and fail closed for unknown/localized failures.
        diagnostic = getattr(exc, "log", "").casefold()
        if any(
            marker in diagnostic
            for marker in (
                "permission denied",
                "access is denied",
                "access denied",
                "operation not permitted",
                "unauthorized",
                "forbidden",
                "authentication required",
            )
        ):
            raise PermissionError(
                "Docker service access denied; source fallback is prohibited"
            ) from exc
        if (
            "cannot connect to the docker daemon" in diagnostic
            or "is the docker daemon running?" in diagnostic
        ):
            raise NativeServiceUnavailable("Local Docker daemon is unavailable") from exc
        raise


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def for_run(settings, run_id):
    if not shutil.which("docker"):
        raise NativeServiceUnavailable("Local Docker executable is unavailable")
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
    start_services(
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
    )
    return (
        f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_codegen",
        data["redis_port"],
    )
````
