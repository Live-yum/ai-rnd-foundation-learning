# templates/product/schema.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 产品数据库及字段合同：按spec.json创建运行表模型与校验规则；独立产品也拒绝远程数据库。字段类型同时决定请求校验、SQL列类型、序列化和查询筛选行为。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `configure`（L46–L55）：接收`connection`、`_`。 调用`connection.cursor`、`cursor.execute`、`cursor.close`、`event.listens_for`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/product/schema.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L96。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3488`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/schema.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "50e3ddbf376feeef25ba0e4b25debd0bf2db0dedb2153ceda28a59b49efd6fb8"} -->
````python
# templates/product/schema.py
"""Product database is independent of the platform; no credentials are inherited."""

import json
import os
from pathlib import Path

from fields import integer_bounds
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    event,
)
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent
SPEC = json.loads((ROOT / "approved-spec.json").read_text(encoding="utf-8"))
BUSINESS = SPEC.get("business")
DATA = Path(os.environ.get("PRODUCT_DATA_DIR", ROOT / ".data")).resolve()
DATA.mkdir(parents=True, exist_ok=True)
url = os.environ.get("PRODUCT_DATABASE_URL") or f"sqlite:///{(DATA / 'product.db').as_posix()}"
parsed = make_url(url)
if parsed.get_backend_name() == "postgresql":
    if parsed.host not in {"127.0.0.1", "localhost", "::1"} or parsed.query:
        raise ValueError(
            "PRODUCT_DATABASE_URL must use local PostgreSQL without driver query overrides"
        )
    parsed = parsed.set(host="127.0.0.1" if parsed.host == "localhost" else parsed.host)
elif parsed.get_backend_name() == "sqlite":
    if parsed.host or parsed.query or (parsed.database or "").startswith(("//", "\\\\")):
        raise ValueError("SQLite must use a local file")
else:
    raise ValueError("Only local SQLite/PostgreSQL is supported")
url = parsed.render_as_string(hide_password=False)
args = {"check_same_thread": False, "autocommit": False} if url.startswith("sqlite:") else {}
engine = create_engine(url, connect_args=args, pool_pre_ping=True)
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def configure(connection, _):
        old = connection.autocommit
        connection.autocommit = True
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
        finally:
            connection.autocommit = old


if BUSINESS:
    from business_schema import build_metadata

    metadata = build_metadata(SPEC)
else:
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
    for entity in SPEC["entities"]:
        columns = [
            Column("id", String(36), primary_key=True),
            Column("owner_id", String(36), ForeignKey("users.id"), nullable=False),
        ]
        for field in entity["fields"]:
            kind = {
                "text": String(field["max_length"]),
                "integer": Integer(),
                "boolean": Boolean(),
                "date": String(10),
                "datetime": String(40),
                "enum": String(field["max_length"]),
            }[field["kind"]]
            columns.append(Column(field["name"], kind, nullable=not field["required"]))
            if field["kind"] == "integer":
                low, high = integer_bounds(field)
                columns.append(CheckConstraint(f'"{field["name"]}" BETWEEN {low} AND {high}'))
        Table(entity["name"], metadata, *columns)
````
