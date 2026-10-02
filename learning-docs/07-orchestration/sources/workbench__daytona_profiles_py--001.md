# workbench/daytona_profiles.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：按技术栈登记离线快照和验收合同。** 模板与数据库组成profile，依赖锁的内容摘要绑定预热镜像；报告必须属于当前源码及选择，并使用严格布尔值证明对应关卡和清理，不能复用主机数据库。

**对应关系：** daytona_matrix_image准备 → snapshot_for选择 → sandbox运行 → require_runtime_report核验；test_daytona_matrix。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `selection_for`（L16–L20）：接收`product`、`template`。 控制顺序：L18按`template == "python-basic"`分支。 调用`Path`、`json.loads`、`(root / "selection.json").read_text`。 返回路径：L19的`json.loads((root / "selection.json").read_text(encoding="utf-8"))`；L20的`{"template": template, "database": "postgresql"}`。
- `profile_key`（L23–L29）：接收`template`、`selection`。 控制顺序：L27按`database not in MATRIX.get(template, set())`分支；L28抛异常，停止当前正常路径。 调用`(selection or {}).get`、`MATRIX.get`、`set`、`ValueError`。 返回路径：L29的`template + "/" + database`。
- `snapshot_for`（L32–L35）：接收`settings`、`template`、`selection`。 调用`settings.daytona_snapshots.get`、`profile_key`。 返回路径：L33的`settings.daytona_snapshots.get( profile_key(template, selection), settings.daytona_snapsho…`。
- `dependency_identity`（L38–L46）：接收`product`。 控制顺序：L44按`not locks`分支；L45抛异常，停止当前正常路径。 调用`sha`、`files`、`ValueError`、`digest`。 返回路径：L46的`digest(locks)`。
- `require_runtime_report`（L49–L81）：接收`report`、`template`、`selection`、`source_digest`。 控制顺序：L60按`template != "python-basic"`分支；L69按`not isinstance(report, dict) or any(report.get(key) is not True for key in required)`分支；L70抛异常，停止当前正常路径；L71按`report.get("template") != template or report.get("database") != database or report.ge…`分支；L76抛异常，停止当前正常路径；L77按`report.get("host_credentials_used") is not False or report.get("host_database_used") …`分支；L81抛异常，停止当前正常路径。 调用`isinstance`、`any`、`report.get`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/daytona_profiles.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L81。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2590`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/daytona_profiles.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "fc695b9f9576ee7631ac17900d948793d5bf1a2031f316598f47243106d5418b"} -->
````python
# workbench/daytona_profiles.py
"""Exact supported sandbox matrix and dependency identity; no cloud fallback."""

import json
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, sha

MATRIX = {
    "python-basic": {"sqlite", "postgresql"},
    "fastapiadmin": {"postgresql"},
    "yudao-vben": {"postgresql"},
}


def selection_for(product, template):
    root = Path(product)
    if template == "python-basic":
        return json.loads((root / "selection.json").read_text(encoding="utf-8"))
    return {"template": template, "database": "postgresql"}


def profile_key(template, selection=None):
    database = (selection or {}).get(
        "database", "sqlite" if template == "python-basic" else "postgresql"
    )
    if database not in MATRIX.get(template, set()):
        raise ValueError("No registered Daytona template/database acceptance profile")
    return template + "/" + database


def snapshot_for(settings, template, selection=None):
    return settings.daytona_snapshots.get(
        profile_key(template, selection), settings.daytona_snapshot
    )


def dependency_identity(product):
    locks = {
        name: sha(path)
        for name, path in files(product)
        if path.name in {"pyproject.toml", "uv.lock", "pnpm-lock.yaml", "package.json", "pom.xml"}
    }
    if not locks:
        raise ValueError("Sandbox input has no dependency lock identity")
    return digest(locks)


def require_runtime_report(report, template, selection, source_digest):
    database = selection["database"]
    required = [
        "passed",
        "http",
        "restart",
        "fresh_database",
        "locked_install",
        "offline",
        "services_stopped",
    ]
    if template != "python-basic":
        required += [
            "frontend_build",
            "frontend_typecheck",
            "browser",
            "permissions",
            "standalone_launcher",
            "business_rules",
        ]
    if not isinstance(report, dict) or any(report.get(key) is not True for key in required):
        raise ValueError("Daytona缺少完整的独立数据库/运行/浏览器验收证据")
    if (
        report.get("template") != template
        or report.get("database") != database
        or report.get("source_digest") != source_digest
    ):
        raise ValueError("Daytona运行报告与当前源码或技术栈不匹配")
    if (
        report.get("host_credentials_used") is not False
        or report.get("host_database_used") is not False
    ):
        raise ValueError("Daytona不能复用主机数据库或凭据")
````
