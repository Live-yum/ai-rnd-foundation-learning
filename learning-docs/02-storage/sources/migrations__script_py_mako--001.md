# migrations/script.py.mako · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：工作台数据库迁移。** Alembic按revision/down_revision的依赖顺序执行；upgrade创建当前结构，downgrade描述逆操作。迁移表达结构，不是删除用户数据的排错手段；数据库模型、迁移和Store查询应保持一致。

**对应关系：** alembic.ini → migrations/env.py → versions → Store使用这些表。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `migrations/script.py.mako`；**本文件共有 1 段**。本段覆盖源文件 L1–L21。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`424`。本段原文以LF换行结束。

<!-- learning-source: {"path": "migrations/script.py.mako", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "116d035db5d6b4abe2f7e00e60d547bf8396983c741d09af902b184ccc6e0a35"} -->
````text
# migrations/script.py.mako
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
````
