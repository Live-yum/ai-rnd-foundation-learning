# templates/business/fastapiadmin/model.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：FastapiAdmin业务事件与通知模型。** 用原生ORM事件表承载操作、处理记录和收件人通知，字段来自受审查适配器；与生成实体使用同一专用数据库，不建立旁路内存数据库。

**对应关系：** 扩展DDL → 原生模型发现 → runtime事务读写。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `BusinessEvent`（L12–L27）：继承`MappedBase`。声明的数据项为`id`、`entity`、`record_id`、`actor`、`recipient`、`event`、`payload`、`source_key`、`created_at`、`read_at`；类型约束/数据库列参数以完整定义为准。

</details>

**创建路径：** `templates/business/fastapiadmin/model.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L27。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1208`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/fastapiadmin/model.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "3f9558076fc3b2d65536eed5423e5651ec3daab1649022811d574fc4fe3f11ac"} -->
````python
# templates/business/fastapiadmin/model.py
import json
from datetime import UTC, datetime
from pathlib import Path

from app.core.base_model import MappedBase
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

CONFIG = json.loads(Path(__file__).with_name("business.json").read_text(encoding="utf-8"))


class BusinessEvent(MappedBase):
    __tablename__ = CONFIG["namespace"] + "_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    entity: Mapped[str] = mapped_column(String(40), index=True)
    record_id: Mapped[int] = mapped_column(Integer, index=True)
    actor: Mapped[int] = mapped_column(Integer, ForeignKey("sys_user.id", ondelete="RESTRICT"))
    recipient: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("sys_user.id", ondelete="RESTRICT"), index=True
    )
    event: Mapped[str] = mapped_column(String(40))
    payload: Mapped[dict] = mapped_column(JSON)
    source_key: Mapped[str | None] = mapped_column(String(200), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
````
