# workbench/projects/models.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `now`（L10–L11）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`datetime.now(timezone.utc).isoformat`、`datetime.now`。 返回路径：L11的`datetime.now(timezone.utc).isoformat(timespec="microseconds")`。
- `uid`（L14–L15）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`str`、`uuid.uuid4`。 返回路径：L15的`str(uuid.uuid4())`。
- `Base`（L18–L19）：继承`DeclarativeBase`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Project`（L22–L26）：继承`Base`。声明的数据项为`id`、`title`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Run`（L29–L42）：继承`Base`。声明的数据项为`id`、`project_id`、`template`、`status`、`pending`、`result`、`error`、`model_calls`、`options`、`auto_mode`、`created_at`、`updated_at`；类型约束/数据库列参数以完整定义为准。
- `Message`（L45–L51）：继承`Base`。声明的数据项为`id`、`run_id`、`role`、`content`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Job`（L54–L60）：继承`Base`。声明的数据项为`id`、`run_id`、`payload`、`status`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Request`（L63–L67）：继承`Base`。声明的数据项为`key`、`fingerprint`、`response`；类型约束/数据库列参数以完整定义为准。
- `Revision`（L70–L77）：继承`Base`。声明的数据项为`gate_id`、`run_id`、`stage`、`digest`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Approval`（L80–L85）：继承`Base`。声明的数据项为`gate_id`、`decision`、`actor`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Step`（L88–L95）：继承`Base`。声明的数据项为`id`、`run_id`、`name`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。
- `Event`（L98–L104）：继承`Base`。声明的数据项为`id`、`run_id`、`kind`、`data`、`created_at`；类型约束/数据库列参数以完整定义为准。

</details>

**创建路径：** `workbench/projects/models.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L104。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4108`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/projects/models.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "244e26df47a9ac67981bcffcaab74569e168576da6a68860d8dba2b8782dfa6b"} -->
````python
# workbench/projects/models.py
"""Existing persistent project schemas; no table or column changes."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def uid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True)
    template: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(50), default="QUEUED")
    pending: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_calls: Mapped[int] = mapped_column(default=0)
    options: Mapped[dict] = mapped_column(JSON, default=dict)
    auto_mode: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    updated_at: Mapped[str] = mapped_column(String(40), default=now, onupdate=now)


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="QUEUED", index=True)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Request(Base):
    __tablename__ = "requests"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSON)


class Revision(Base):
    __tablename__ = "revisions"
    gate_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    stage: Mapped[str] = mapped_column(String(40))
    digest: Mapped[str] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Approval(Base):
    __tablename__ = "approvals"
    gate_id: Mapped[str] = mapped_column(ForeignKey("revisions.gate_id"), primary_key=True)
    decision: Mapped[bool] = mapped_column()
    actor: Mapped[str] = mapped_column(String(40), default="local-operator")
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Step(Base):
    __tablename__ = "steps"
    __table_args__ = (UniqueConstraint("run_id", "name", name="uq_steps_run_name"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"), index=True)
    kind: Mapped[str] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40), default=now)
````
