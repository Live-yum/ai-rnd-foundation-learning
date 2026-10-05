# tests/fixtures/contest_native/module_contest/model.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `ContestTeam`（L10–L18）：继承`MappedBase`。声明的数据项为`id`、`captain_id`、`capacity`、`name`、`submission_title`；类型约束/数据库列参数以完整定义为准。
- `ContestMembership`（L21–L30）：继承`MappedBase`。声明的数据项为`team_id`、`user_id`；类型约束/数据库列参数以完整定义为准。
- `ContestInvitation`（L33–L45）：继承`MappedBase`。声明的数据项为`id`、`team_id`、`code_hash`、`expires_at`、`status`；类型约束/数据库列参数以完整定义为准。

</details>

**创建路径：** `tests/fixtures/contest_native/module_contest/model.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L45。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1971`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/fixtures/contest_native/module_contest/model.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "beeaea7f88fa939ff1cce811d6029339240d90f3d1ed26d196d0dc3dd2660701"} -->
````python
# tests/fixtures/contest_native/module_contest/model.py
"""Authored reference fixture ORM, registered by the real native model loader."""

from datetime import datetime

from app.core.base_model import MappedBase
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class ContestTeam(MappedBase):
    __tablename__ = "rnd_contest_team"
    __table_args__ = (CheckConstraint("capacity >= 2 AND capacity <= 10", name="capacity"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    captain_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id", ondelete="RESTRICT"))
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    submission_title: Mapped[str] = mapped_column(String(200), nullable=False)


class ContestMembership(MappedBase):
    __tablename__ = "rnd_contest_membership"
    __table_args__ = (UniqueConstraint("user_id", name="uq_contest_one_team_per_user"),)

    team_id: Mapped[int] = mapped_column(
        ForeignKey("rnd_contest_team.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("sys_user.id", ondelete="RESTRICT"), primary_key=True
    )


class ContestInvitation(MappedBase):
    __tablename__ = "rnd_contest_invitation"
    __table_args__ = (
        CheckConstraint("status IN ('active', 'revoked', 'expired')", name="invitation_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("rnd_contest_team.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
````
