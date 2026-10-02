# scripts/daytona_diagnostics.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：保留有界且脱敏的失败诊断。** 仅读取本次本机安装的状态和尾部日志，先收集本机秘密用于替换，再写报告；不打包credentials或env。诊断脚本不宣告业务通过。

**对应关系：** 工作流always失败/成功收尾 → reports/daytona诊断 → 人工定位。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_local`、`workbench.filesystem`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L10–L43）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L12遍历`["credentials.json", "api-key.json"]`；L14按`path.is_file()`分支；L21遍历`[["ps", "--all"], ["logs", "--no-color", "--tail", "80"]]`；L22按`(HOME / "compose.lock.yaml").is_file()`分支；L38遍历`sorted(secrets, key=len, reverse=True)`；L42按`image.is_file()`分支。 调用`path.is_file`、`secrets.extend`、`json.loads(path.read_text()).values`、`json.loads`、`path.read_text`、`isinstance`、`len`、`(HOME / "compose.lock.yaml").is_file`、`logs.append`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/daytona_diagnostics.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L47。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1541`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/daytona_diagnostics.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a86b9018b870bdd43a8c1dbb170ef7379d97910ae863a5d068bf0a048096796e"} -->
````python
# scripts/daytona_diagnostics.py
"""Bounded, secret-redacted diagnostics from this local test deployment only."""

import json

from scripts.daytona_local import HOME, PROJECT, docker
from workbench.filesystem import atomic_text
from workbench.settings import ROOT


def main():
    secrets = []
    for name in ["credentials.json", "api-key.json"]:
        path = HOME / name
        if path.is_file():
            secrets.extend(
                v
                for v in json.loads(path.read_text()).values()
                if isinstance(v, str) and len(v) > 5
            )
    logs = []
    for args in [["ps", "--all"], ["logs", "--no-color", "--tail", "80"]]:
        if (HOME / "compose.lock.yaml").is_file():
            try:
                logs.append(
                    docker(
                        "compose",
                        "-p",
                        PROJECT,
                        "-f",
                        str(HOME / "compose.lock.yaml"),
                        *args,
                        timeout=60,
                    )[-80000:]
                )
            except Exception as exc:
                logs.append(type(exc).__name__)
    body = "\n".join(logs)
    for secret in sorted(secrets, key=len, reverse=True):
        body = body.replace(secret, "[REDACTED]")
    atomic_text(ROOT / "reports/daytona-matrix-diagnostics.log", body)
    image = HOME / "snapshot-image.json"
    if image.is_file():
        atomic_text(ROOT / "reports/daytona-matrix-image.json", image.read_text())


if __name__ == "__main__":
    main()
````
