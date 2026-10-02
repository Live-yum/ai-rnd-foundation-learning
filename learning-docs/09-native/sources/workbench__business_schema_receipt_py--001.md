# workbench/business_schema_receipt.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立交付的真实数据库结构签名。** 从当前数据库读取列、外键与关键约束，形成可比较结构；恢复不能仅以表存在代替结构一致，也不能删除不匹配的数据。

**对应关系：** portable创建清单 → 独立启动器校验新库/已有同产品库 → 结构一致性证据。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `table_signature`（L8–L46）：接收`connection`、`name`。 控制顺序：L10按`not inspector.has_table(name)`分支。 调用`inspect`、`inspector.has_table`、`sorted`、`str`、`inspector.get_columns`、`inspector.get_pk_constraint`、`ordered`、`inspector.get_foreign_keys`、`inspector.get_unique_constraints`等。 返回路径：L11的`None`；L16的`{ "columns": sorted( [ {"name": c["name"], "type": str(c["type"]), "nullable": c["nullable…`。
- `table_signature.ordered`（L13–L14）：接收`values`。 调用`sorted`、`json.dumps`。 返回路径：L14的`sorted(values, key=lambda item: json.dumps(item, sort_keys=True))`。
- `verify_tables`（L49–L52）：接收`connection`、`expected`。 控制顺序：L50遍历`expected.items()`；L51按`table_signature(connection, name) != signature`分支；L52抛异常，停止当前正常路径。 调用`expected.items`、`table_signature`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/business_schema_receipt.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L52。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1712`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_schema_receipt.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7b8da7085f5a8477d84dff208ec8e63a552885a880698ec93e2feb80467679d7"} -->
````python
# workbench/business_schema_receipt.py
"""Stable introspected PostgreSQL schema evidence for owned portable business tables."""

import json

from sqlalchemy import inspect


def table_signature(connection, name):
    inspector = inspect(connection)
    if not inspector.has_table(name):
        return None

    def ordered(values):
        return sorted(values, key=lambda item: json.dumps(item, sort_keys=True))

    return {
        "columns": sorted(
            [
                {"name": c["name"], "type": str(c["type"]), "nullable": c["nullable"]}
                for c in inspector.get_columns(name)
            ],
            key=lambda c: c["name"],
        ),
        "primary_key": inspector.get_pk_constraint(name)["constrained_columns"],
        "foreign_keys": ordered(
            [
                {
                    "columns": f["constrained_columns"],
                    "table": f["referred_table"],
                    "targets": f["referred_columns"],
                    "options": f["options"],
                }
                for f in inspector.get_foreign_keys(name)
            ]
        ),
        "unique": ordered(
            [{"columns": u["column_names"]} for u in inspector.get_unique_constraints(name)]
        ),
        "indexes": ordered(
            [
                {"columns": i["column_names"], "unique": bool(i["unique"])}
                for i in inspector.get_indexes(name)
                if not i.get("duplicates_constraint")
            ]
        ),
    }


def verify_tables(connection, expected):
    for name, signature in expected.items():
        if table_signature(connection, name) != signature:
            raise ValueError("Owned business schema mismatch; preserve database: " + name)
````
