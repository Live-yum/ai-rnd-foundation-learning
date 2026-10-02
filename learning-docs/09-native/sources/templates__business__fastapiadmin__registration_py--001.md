# templates/business/fastapiadmin/registration.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生注册与默认业务角色的事务连接。** 在已有账号校验和密码哈希之后添加合同默认非管理员角色；初始化权限和普通注册分离，不允许用户选择管理员角色。

**对应关系：** 原生注册接口 → 同事务注册钩子 → 产品专属角色。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `before_registration`（L9–L16）：接收`db`。 控制顺序：L10按`not rt.SPEC["registration"]["enabled"]`分支；L15按`marker is None`分支。 调用`rt.fail`、`db.scalar`、`select(BusinessEvent).where(BusinessEvent.source_key == "bootstra…`、`select(BusinessEvent).where`、`select`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `registration_completed`（L19–L32）：接收`db`、`user_id`。 调用`rt.set_role`、`db.add`、`BusinessEvent`、`db.commit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/business/fastapiadmin/registration.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L32。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1013`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/fastapiadmin/registration.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2e0379172005988b3dbc8cfe908490f95373e174913298aefb77d6884a934c34"} -->
````python
# templates/business/fastapiadmin/registration.py
"""Native registration extension: same session, native password/account validation."""

from sqlalchemy import select

from . import runtime as rt
from .model import BusinessEvent


async def before_registration(db):
    if not rt.SPEC["registration"]["enabled"]:
        rt.fail(403, "Business self-registration is disabled")
    marker = await db.scalar(
        select(BusinessEvent).where(BusinessEvent.source_key == "bootstrap").with_for_update()
    )
    if marker is None:
        rt.fail(409, "A native administrator must initialize this project first")


async def registration_completed(db, user_id):
    role = rt.SPEC["registration"]["default_role"]
    await rt.set_role(db, user_id, role)
    db.add(
        BusinessEvent(
            entity="roles",
            record_id=user_id,
            actor=user_id,
            event="joined",
            payload={"role": role},
        )
    )
    # Native user creation and restricted role membership are one atomic transaction.
    await db.commit()
````
