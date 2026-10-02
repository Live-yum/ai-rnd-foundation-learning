# workbench/daytona_worker.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：SDK专用的本机网络子进程。** 父进程通过stdin传递最少配置，不把Key放进命令行；子进程先安装回环网络钩子再导入SDK。SDK默认云地址、重定向和代理不能绕过连接检查。父进程只接受passed=true且cleanup=deleted的回执。

**对应关系：** sandbox.verify_in_daytona → 子进程main → sandbox.client_for/_verify_in_daytona；test_local_only。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.generator`、`workbench.local_only`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run_isolated`（L14–L61）：接收`product`、`template`、`settings`。 控制顺序：L49抛异常，停止当前正常路径；L52按`process.returncode`分支；L56抛异常，停止当前正常路径；L59按`receipt.get("passed") is not True or receipt.get("cleanup") != "deleted"`分支；L60抛异常，停止当前正常路径。 调用`str`、`Path(product).resolve`、`Path`、`settings.daytona_api_key.get_secret_value`、`tempfile.TemporaryFile`、`subprocess.Popen`、`clean_env`、`process_options`、`process.communicate`等。 返回路径：L61的`receipt`。
- `main`（L64–L91）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L66按`len(data) > 65536`分支；L67抛异常，停止当前正常路径；L89抛异常，停止当前正常路径。 调用`sys.stdin.buffer.read`、`len`、`ValueError`、`json.loads`、`install_loopback_guard`、`Settings`、`validate_configuration`、`selection_for`、`client_for`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/daytona_worker.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L95。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3692`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/daytona_worker.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f15b8fa6a533e3a3ae2131c0de9ab980217e9f8c2cb09d89ac125bec7f48940e"} -->
````python
# workbench/daytona_worker.py
"""Run the pinned Daytona SDK in an isolated, loopback-only child process."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from workbench.generator import PrerequisiteError
from workbench.local_only import install_loopback_guard
from workbench.tools import clean_env, process_options, stop_process


def run_isolated(product, template, settings):
    payload = {
        "product": str(Path(product).resolve()),
        "template": template,
        "settings": {
            "sandbox_provider": settings.sandbox_provider,
            "daytona_allow_local_execution": settings.daytona_allow_local_execution,
            "daytona_capture_startup_diagnostics": settings.daytona_capture_startup_diagnostics,
            "daytona_api_url": settings.daytona_api_url,
            "daytona_api_key": settings.daytona_api_key.get_secret_value(),
            "daytona_snapshot": settings.daytona_snapshot,
            "daytona_snapshots": settings.daytona_snapshots,
            "daytona_runtime_timeout": settings.daytona_runtime_timeout,
            "daytona_target": settings.daytona_target,
            "tool_timeout": settings.tool_timeout,
        },
    }
    # A pipe, never argv, a workflow secret, or a report. The child does not
    # inherit cloud credentials, proxy settings or hosted tracing configuration.
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(
            [sys.executable, "-m", "workbench.daytona_worker"],
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.STDOUT,
            env=clean_env(),
            **process_options(),
        )
        try:
            process.communicate(
                json.dumps(payload).encode(),
                timeout=settings.daytona_runtime_timeout + settings.tool_timeout * 12 + 60,
            )
        except subprocess.TimeoutExpired:
            stop_process(process)
            raise PrerequisiteError(
                "本机Daytona工作进程超时；检查daytona-verification.json中的沙箱名称并在本机清理"
            ) from None
        if process.returncode:
            output.seek(0, 2)
            output.seek(max(0, output.tell() - 16000))
            error = output.read().decode("utf-8", errors="replace")
            raise PrerequisiteError("本机Daytona未通过：" + settings.redact(error)[-3000:])
    path = Path(product).parent / "daytona-verification.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("passed") is not True or receipt.get("cleanup") != "deleted":
        raise PrerequisiteError("本机Daytona缺少已通过且已清理的验收回执")
    return receipt


def main():
    data = sys.stdin.buffer.read(65537)
    if len(data) > 65536:
        raise ValueError("Daytona控制参数过大")
    payload = json.loads(data)
    install_loopback_guard()
    from workbench.sandbox import (
        _verify_in_daytona,
        client_for,
        close_client,
        validate_configuration,
    )
    from workbench.settings import Settings

    settings = Settings(_env_file=None, **payload["settings"])
    from workbench.daytona_profiles import selection_for

    validate_configuration(
        settings, payload["template"], selection_for(payload["product"], payload["template"])
    )
    client = client_for(settings)
    try:
        _verify_in_daytona(payload["product"], payload["template"], settings, client=client)
    except Exception as exc:
        print(settings.redact(str(exc)), file=sys.stderr)
        raise SystemExit(1) from None
    finally:
        close_client(client)


if __name__ == "__main__":
    main()
````
