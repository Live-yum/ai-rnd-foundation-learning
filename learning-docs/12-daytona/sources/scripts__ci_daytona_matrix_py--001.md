# scripts/ci_daytona_matrix.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：数据库与模板矩阵的沙箱验收入口。** prepare-basic创建用于矩阵的基础PG产品；verify读取已登记同profile快照并运行真实沙箱，核对运行和清理证据。它不能用一种镜像冒充所有技术栈。

**对应关系：** native-toolchain-daytona三行矩阵 → profile快照 → daytona-matrix.json。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.daytona_local`、`scripts.news_fixture`、`workbench.catalog`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.sandbox`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `main`（L17–L51）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L23按`args.action == "prepare-basic"`分支；L24按`args.template != "python-basic"`分支；L25抛异常，停止当前正常路径；L37断言`result["passed"] is True and result["cleanup"] == "deleted"`；L38断言`result["runtime"]["host_credentials_used"] is False`；L39断言`result["runtime"]["host_database_used"] is False`。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`ValueError`、`Plan.model_validate`、`news_spec`、`Selection`、`generate_basic`、`Settings`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_daytona_matrix.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L55。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2057`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_daytona_matrix.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f77a60e12943948a59a4b1af18e28e6ce0564c13512892736e50cc62c0dfaf0c"} -->
````python
# scripts/ci_daytona_matrix.py
"""Actual self-hosted sandbox profiles; failures never become local-success fallbacks."""

import argparse
import json
from pathlib import Path

from scripts.daytona_local import HOME
from scripts.news_fixture import news_spec
from workbench.catalog import Selection
from workbench.domain import Plan
from workbench.filesystem import write_json
from workbench.generator import generate_basic
from workbench.sandbox import verify_in_daytona
from workbench.settings import ROOT, Settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare-basic", "verify"])
    parser.add_argument("template", choices=["python-basic", "fastapiadmin", "yudao-vben"])
    parser.add_argument("--product", type=Path, default=ROOT / ".native/tool-product")
    args = parser.parse_args()
    if args.action == "prepare-basic":
        if args.template != "python-basic":
            raise ValueError("Only the native generator may prepare a native product")
        plan = Plan.model_validate(news_spec())
        selection = Selection(
            template="python-basic",
            backend="fastapi",
            frontend="simple-admin",
            database="postgresql",
        )
        generate_basic(plan, args.product, selection=selection)
        return
    settings = Settings(_env_file=HOME / "workbench.env", daytona_runtime_timeout=3600)
    result = verify_in_daytona(args.product, args.template, settings)
    assert result["passed"] is True and result["cleanup"] == "deleted"
    assert result["runtime"]["host_credentials_used"] is False
    assert result["runtime"]["host_database_used"] is False
    write_json(ROOT / "reports/daytona-matrix.json", result)
    print(
        json.dumps(
            {
                "passed": True,
                "template": args.template,
                "database": result["database"],
                "cleanup": result["cleanup"],
                "network_block_all": True,
            }
        )
    )


if __name__ == "__main__":
    main()
````
