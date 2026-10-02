# workbench/daytona_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：本次自有沙箱的有界启动诊断。** 创建失败后仅按确切随机名称和UUID读取固定本机Runner内的状态及日志尾部；限制单项与总时间、过滤秘密后限长保存。不枚举其他容器、不改配置，诊断失败不阻止原清理，成功不替代验收。

**对应关系：** sandbox失败创建路径的显式可选开关 → capture_startup → startup_diagnostics回执 → 原沙箱删除路径。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `capture_startup`（L25–L126）：接收`sandbox_id`、`sandbox_name`、`settings`。 源码说明：Only called after SDK lookup by this attempt's unpredictable exact name.。 控制顺序：L29按`str(uuid.UUID(sandbox_id)) != sandbox_id or not re.fullmatch( r"rnd-verify-[0-9a-f]{3…`分支；L32抛异常，停止当前正常路径；L42按`not compose.is_file() or compose.is_symlink()`分支；L45遍历`("credentials.json", "api-key.json")`；L47按`path.is_file() and not path.is_symlink() and path.stat().st_size <= 16384`分支；L50按`isinstance(values, dict)`分支；L106遍历`commands.items()`；L108按`remaining <= 0`分支。 调用`str`、`uuid.UUID`、`re.fullmatch`、`ValueError`、`compose.is_file`、`compose.is_symlink`、`path.is_file`、`path.is_symlink`、`path.stat`等。 返回路径：L43的`{**report, "status": "fixed-local-compose-unavailable"}`；L126的`{**report, "status": "collected-before-delete"}`。
- `capture_startup.redact`（L55–L66）：接收`text`。 控制顺序：L57遍历`sorted(secrets, key=len, reverse=True)`。 调用`settings.redact`、`sorted`、`text.replace`、`re.sub`。 返回路径：L66的`text[-MAX_CHARS:]`。

</details>

**创建路径：** `workbench/daytona_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L126。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4774`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/daytona_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e47d5e40fdcb1568189568edab083544a44748e6d78b9fd35aa1fdc6dead4dec"} -->
````python
# workbench/daytona_diagnostics.py
"""Optional, bounded startup diagnostics for one owned local sandbox before deletion.

Never enumerate containers, dump environment variables, alter the failed sandbox,
change network settings, or turn failed creation into successful acceptance.
"""

import json
import re
import time
import uuid

from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command

MAX_CHARS = 8192
TOTAL_SECONDS = 15
STATE_FORMAT = (
    '{"Status":{{json .State.Status}},"Running":{{json .State.Running}},'
    '"OOMKilled":{{json .State.OOMKilled}},"ExitCode":{{json .State.ExitCode}},'
    '"Error":{{json .State.Error}},"StartedAt":{{json .State.StartedAt}},'
    '"FinishedAt":{{json .State.FinishedAt}},"RestartCount":{{json .RestartCount}}}'
)


def capture_startup(sandbox_id, sandbox_name, settings):
    """Only called after SDK lookup by this attempt's unpredictable exact name."""
    from scripts.daytona_local import HOME, PROJECT

    if str(uuid.UUID(sandbox_id)) != sandbox_id or not re.fullmatch(
        r"rnd-verify-[0-9a-f]{32}", sandbox_name
    ):
        raise ValueError("Startup diagnostics require the exact owned sandbox UUID and name")
    compose = HOME / "compose.lock.yaml"
    report = {
        "sandbox_id": sandbox_id,
        "sandbox_name": sandbox_name,
        "scope": "exact-owned-local-sandbox",
        "passed": False,
        "affects_acceptance": False,
        "diagnostics": {},
    }
    if not compose.is_file() or compose.is_symlink():
        return {**report, "status": "fixed-local-compose-unavailable"}
    secrets = []
    for filename in ("credentials.json", "api-key.json"):
        path = HOME / filename
        if path.is_file() and not path.is_symlink() and path.stat().st_size <= 16384:
            try:
                values = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(values, dict):
                    secrets.extend(v for v in values.values() if isinstance(v, str) and len(v) > 5)
            except OSError, UnicodeError, json.JSONDecodeError:
                pass

    def redact(text):
        text = settings.redact(text)
        for secret in sorted(secrets, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        text = re.sub(r"(?i)(bearer\s+)[^\s\"']+", r"\1[REDACTED]", text)
        text = re.sub(
            r"(?i)((?:[\"']?)(?:password|api[_-]?key|auth[_-]?token|access[_-]?token|token|authorization|secret)(?:[\"']?)\s*[=:]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
            r"\1[REDACTED]",
            text,
        )
        text = re.sub(r"(://[^/@:\s]+:)[^@\s]+@", r"\1[REDACTED]@", text)
        return text[-MAX_CHARS:]

    # run_command pins the outer Docker CLI to this machine's local socket.
    # Compose exec must also pin the inner CLI to the runner's own DinD socket;
    # explicit fixed values override its environment without a shell or a remote
    # context. Do not pass --host through the generic command policy.
    prefix = [
        "docker",
        "compose",
        "-p",
        PROJECT,
        "-f",
        str(compose),
        "exec",
        "-T",
        "-e",
        "DOCKER_HOST=unix:///var/run/docker.sock",
        "-e",
        "DOCKER_CONTEXT=",
        "-e",
        "DOCKER_TLS=",
        "-e",
        "DOCKER_TLS_VERIFY=",
        "-e",
        "DOCKER_CERT_PATH=",
        "runner",
        "docker",
    ]
    commands = {
        "state": ["inspect", "--format", STATE_FORMAT, sandbox_id],
        "daemon_stdout": ["logs", "--tail", "80", sandbox_id],
        "daemon_file": [
            "exec",
            sandbox_id,
            "tail",
            "--bytes=" + str(MAX_CHARS),
            "/tmp/daytona-daemon.log",
        ],
    }
    deadline = time.monotonic() + TOTAL_SECONDS
    for label, argv in commands.items():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            report["diagnostics"][label] = {"status": "diagnostic-budget-exhausted"}
            continue
        try:
            result = run_command(prefix + argv, ROOT, timeout=min(5, remaining))
            report["diagnostics"][label] = {"status": "captured", "text": redact(result["log"])}
        except ToolFailure as exc:
            report["diagnostics"][label] = {
                "status": "unavailable",
                "error_type": type(exc).__name__,
                "text": redact(getattr(exc, "log", "")),
            }
        except Exception as exc:
            # Do not serialize unexpected exception messages that may contain secrets.
            report["diagnostics"][label] = {
                "status": "unavailable",
                "error_type": type(exc).__name__,
            }
    return {**report, "status": "collected-before-delete"}
````
