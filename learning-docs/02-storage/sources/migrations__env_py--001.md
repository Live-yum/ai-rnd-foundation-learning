# migrations/env.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台数据库迁移。** Alembic按revision/down_revision的依赖顺序执行；upgrade创建当前结构，downgrade描述逆操作。迁移表达结构，不是删除用户数据的排错手段；数据库模型、迁移和Store查询应保持一致。

**对应关系：** alembic.ini → migrations/env.py → versions → Store使用这些表。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`、`workbench.store`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `migrate`（L7–L18）：接收`connection`。 调用`context.configure`、`context.begin_transaction`、`context.run_migrations`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `migrations/env.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L34。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1013`。本段原文以LF换行结束。

<!-- learning-source: {"path": "migrations/env.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1654fd7ac585cffbb0d88d19007515eaf6caa54cd7edecdd0ce3ea5f095cbae4"} -->
````python
# migrations/env.py
from alembic import context

from workbench.settings import Settings
from workbench.store import Base, Store


def migrate(connection):
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        include_object=lambda obj, name, kind, reflected, compare: (
            kind != "table" or name in Base.metadata.tables
        ),
        compare_type=True,
        render_as_batch=connection.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


connection = context.config.attributes.get("connection")
if connection is not None:
    migrate(connection)
elif context.is_offline_mode():
    context.configure(url=Settings().db_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    store = Store(Settings())
    try:
        with store.engine.begin() as connection:
            migrate(connection)
    finally:
        store.engine.dispose()
````
