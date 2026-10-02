# migrations/versions/0002_run_selection_and_delegation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台数据库迁移。** Alembic按revision/down_revision的依赖顺序执行；upgrade创建当前结构，downgrade描述逆操作。迁移表达结构，不是删除用户数据的排错手段；数据库模型、迁移和Store查询应保持一致。

**对应关系：** alembic.ini → migrations/env.py → versions → Store使用这些表。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `upgrade`（L12–L19）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`op.add_column`、`sa.Column`、`sa.JSON`、`sa.text`、`sa.Boolean`、`sa.false`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `downgrade`（L22–L25）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`op.batch_alter_table`、`batch.drop_column`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `migrations/versions/0002_run_selection_and_delegation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L25。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`718`。本段原文以LF换行结束。

<!-- learning-source: {"path": "migrations/versions/0002_run_selection_and_delegation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3a20b7b52079b016505fa761f4493bf856e8423a96c2e9ff7151246b8007020b"} -->
````python
# migrations/versions/0002_run_selection_and_delegation.py
"""Persist selected backend/frontend/database and explicit automated-decision consent."""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # ADD COLUMN is supported by both SQLite and PostgreSQL; keep existing run rows/checkpoints.
    op.add_column(
        "runs", sa.Column("options", sa.JSON(), nullable=False, server_default=sa.text("'{}'"))
    )
    op.add_column(
        "runs", sa.Column("auto_mode", sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade():
    with op.batch_alter_table("runs") as batch:
        batch.drop_column("auto_mode")
        batch.drop_column("options")
````
