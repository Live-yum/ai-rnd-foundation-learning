# workbench/business_native.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：事务安装明确的原生业务扩展。** 根据模板选适配器，再向已验证的专用本机库按顺序执行受信任扩展SQL；同一事务失败全部回滚，证据记录实际SQL哈希而非直接宣告运行成功。

**对应关系：** 生成器及菜单完成 → 本文件 → 后端重新构建/启动 → HTTP与浏览器验收。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_environment`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 业务扩展SQL属于已验证适配器的输出，安装前先验证专用本机库与模板身份。按既定顺序在事务中执行；中途失败整体回滚，记录的是实际执行SQL的哈希。不能接收模型随口生成的任意SQL，也不能为修复冲突自动清空既有业务库。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `install_native_business`（L12–L50）：接收`template`、`plan`、`backend`、`frontend`、`targets`、`reports`、`url`。 控制顺序：L14按`plan.business is None`分支；L17按`template == "fastapiadmin"`分支；L21按`template == "yudao-vben"`分支；L26抛异常，停止当前正常路径；L32按`roles.is_file()`分支；L34按`not scripts[0].is_file()`分支；L35抛异常，停止当前正常路径；L40遍历`scripts`。 调用`Plan.model_validate`、`Path`、`extend_business`、`install_yudao_business`、`ValueError`、`checked_database(url).set(drivername="postgresql").render_as_stri…`、`checked_database(url).set`、`checked_database`、`roles.is_file`等。 返回路径：L15的`None`；L50的`evidence`。

</details>

**创建路径：** `workbench/business_native.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L50。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2036`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_native.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "da56f59c8af6891b08113124d37d7b1fa346f9419997c544db3aeaf2d45d835e"} -->
````python
# workbench/business_native.py
"""Install reviewed native business adapters and explicit transaction-scoped schema."""

from pathlib import Path

import psycopg

from workbench.domain import Plan
from workbench.filesystem import sha, write_json
from workbench.native_environment import checked_database


def install_native_business(template, plan, backend, frontend, targets, reports, url):
    plan = Plan.model_validate(plan)
    if plan.business is None:
        return None
    reports = Path(reports)
    if template == "fastapiadmin":
        from workbench.business_fastapi import extend_business

        receipt = extend_business(plan, backend, frontend, targets, reports, database_url=url)
    elif template == "yudao-vben":
        from workbench.business_yudao import install_yudao_business

        receipt = install_yudao_business(plan, backend, frontend, targets, reports)
    else:
        raise ValueError("Unknown native business adapter")
    database = (
        checked_database(url).set(drivername="postgresql").render_as_string(hide_password=False)
    )
    scripts = [reports / "business-extension-schema.sql"]
    roles = reports / "business-role-seed.sql"
    if roles.is_file():
        scripts.append(roles)
    if not scripts[0].is_file():
        raise ValueError("Business adapter must emit explicit schema before runtime acceptance")
    # These files are deterministic adapter output, never model-supplied SQL. Any
    # failure rolls back the entire extension; the outer recovery guard preserves
    # source/data and does not claim an incomplete bootstrap can safely resume.
    with psycopg.connect(database) as connection:
        for script in scripts:
            connection.execute(script.read_text(encoding="utf-8"))
    evidence = {
        "template": template,
        "adapter": receipt,
        "schema_applied": True,
        "schema_files": {script.name: sha(script) for script in scripts},
        "runtime_verified": False,
    }
    write_json(reports / "business-installation.json", evidence)
    return evidence
````
