# workbench/product_sql.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：从同一Plan生成可读SQL交付资料。** render使用字段合同生成业务DDL和菜单等资料，标识符不是任意模型文本。SQL资料与真正的迁移/原生生成器用途不同，文档说明哪个脚本负责实际初始化，防止重复执行。

**对应关系：** knowledge/generator → product_sql → 设计包与产品。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `render`（L10–L51）：接收`plan`、`destination`。根据同一Plan建立SQLAlchemy元数据，再分别编译SQLite/PostgreSQL的可读DDL；写出SQL用于审查，不在此函数中连接或修改数据库。 控制顺序：L26遍历`plan.entities`；L31遍历`entity.fields`；L42遍历`[("sqlite", sqlite.dialect()), ("postgresql", postgresql.dialect(…`；L46遍历`metadata.sorted_tables`。 调用`MetaData`、`Table`、`Column`、`String`、`ForeignKey`、`Integer`、`Boolean`、`columns.append`、`Index`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/product_sql.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L51。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2175`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/product_sql.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0b7da6fa90f58ae24813b5125d7c5154ec85d6583cb5cfdb929605c75fb1c617"} -->
````python
# workbench/product_sql.py
"""Human-readable SQL generated from the same frozen product fields as the migration."""

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, MetaData, String, Table
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.schema import CreateIndex, CreateTable

from workbench.filesystem import atomic_text


def render(plan, destination):
    metadata = MetaData()
    Table(
        "users",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("username", String(100), nullable=False, unique=True),
        Column("password", String(400), nullable=False),
    )
    Table(
        "tokens",
        metadata,
        Column("token", String(64), primary_key=True),
        Column("user_id", String(36), ForeignKey("users.id"), nullable=False),
        Column("expires_at", Integer, nullable=False),
    )
    for entity in plan.entities:
        columns = [
            Column("id", String(36), primary_key=True),
            Column("owner_id", String(36), ForeignKey("users.id"), nullable=False),
        ]
        for field in entity.fields:
            kind = {
                "text": String(field.max_length),
                "enum": String(field.max_length),
                "date": String(10),
                "integer": Integer(),
                "boolean": Boolean(),
            }[field.kind]
            columns.append(Column(field.name, kind, nullable=not field.required))
        table = Table(entity.name, metadata, *columns)
        Index("ix_" + entity.name + "_owner_id", table.c.owner_id)
    for name, dialect in [("sqlite", sqlite.dialect()), ("postgresql", postgresql.dialect())]:
        statements = [
            "-- Reference DDL. Normal startup uses the versioned Alembic migration; do not apply both.\n"
        ]
        for table in metadata.sorted_tables:
            statements.append(str(CreateTable(table).compile(dialect=dialect)) + ";")
            statements.extend(
                str(CreateIndex(index).compile(dialect=dialect)) + ";" for index in table.indexes
            )
        atomic_text(destination / "database" / f"schema.{name}.sql", "\n".join(statements) + "\n")
````
