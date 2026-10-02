# scripts/ci_native_generated.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：定义并运行原生模块集成样例。** acceptance_spec给出多实体、文本/整数/布尔的确定性Plan；入口把模板、数据库和源码参数交给同一个native_lab，避免CI另写一套伪生成器。

**对应关系：** 原生CI入口 → acceptance_spec → native_lab.run_acceptance。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.native_lab`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `acceptance_spec`（L11–L40）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan`。 返回路径：L12的`Plan( title="Native generated management", data_scope="shared", entities=[ { "name": "devi…`。
- `main`（L43–L65）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`argparse.ArgumentParser`、`parser.add_argument`、`Path`、`parser.parse_args`、`Plan.model_validate_json`、`args.spec.read_text`、`acceptance_spec`、`run_acceptance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_native_generated.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L69。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2157`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_native_generated.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e666947db9e7edb5c85621d877f5643b05f001ee77ba3cc75dda5a86348d898e"} -->
````python
# scripts/ci_native_generated.py
"""CI fixtures exercise the same native lab implementation used by the platform."""

import argparse
import os
from pathlib import Path

from workbench.domain import Plan
from workbench.native_lab import run_acceptance


def acceptance_spec():
    return Plan(
        title="Native generated management",
        data_scope="shared",
        entities=[
            {
                "name": "device",
                "description": "设备台账",
                "fields": [
                    {"name": "name", "kind": "text"},
                    {"name": "quantity", "kind": "integer"},
                    {"name": "active", "kind": "boolean"},
                ],
            },
            {
                "name": "category",
                "description": "分类台账",
                "fields": [
                    {"name": "name", "kind": "text"},
                    {"name": "position", "kind": "integer"},
                ],
            },
        ],
        acceptance=[
            "Two separate native modules support CRUD",
            "Role grants and revocation are enforced",
            "Native frontend renders both generated modules",
            "Records persist across process restart",
        ],
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--source", type=Path, default=Path(".native/source"))
    parser.add_argument("--output", type=Path, default=Path(".native/product"))
    parser.add_argument("--frontend-source", type=Path, default=Path(".native/frontend"))
    parser.add_argument("--reports", type=Path, default=Path("reports/native"))
    parser.add_argument("--spec", type=Path)
    args = parser.parse_args()
    plan = (
        Plan.model_validate_json(args.spec.read_text(encoding="utf-8"))
        if args.spec
        else acceptance_spec()
    )
    run_acceptance(
        args.template,
        args.source,
        args.output,
        args.frontend_source,
        os.environ["NATIVE_TEST_DATABASE_URL"],
        args.reports,
        plan,
    )


if __name__ == "__main__":
    main()
````
