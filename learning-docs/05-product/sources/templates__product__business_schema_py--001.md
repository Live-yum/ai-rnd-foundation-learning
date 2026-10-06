# templates/product/business_schema.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 纯元数据构造器：按批准合同创建实体真实外键、角色、初始化标记、不可改审计、处理记录与收件人通知表；不在导入时连接数据库，可供生成器编译审查SQL。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `build_metadata`（L15–L81）：接收`spec`。 控制顺序：L39遍历`spec["entities"]`；L48遍历`entity["fields"]`；L58按`target`分支；L77按`field["kind"] == "integer" and not target`分支。 调用`MetaData`、`Table`、`Column`、`String`、`ForeignKey`、`Integer`、`Boolean`、`relations.get`、`columns.append`等。 返回路径：L81的`metadata`。
- `integer_check`（L84–L95）：接收`field`。 调用`max`、`field.get`、`min`、`CheckConstraint`。 返回路径：L95的`CheckConstraint(f'"{field["name"]}" BETWEEN {low} AND {high}')`。
- `business_tables`（L98–L133）：接收`metadata`。 调用`Table`、`Column`、`String`、`ForeignKey`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/product/business_schema.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L133。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4970`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/business_schema.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "2e56ce0d08e611b644659b8bc2518aec40d2e312de83468fd239dbc291ecba5c"} -->
````python
# templates/product/business_schema.py
"""Pure SQL metadata for approved business specs; no connections or environment reads."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)


def build_metadata(spec):
    business = spec["business"]
    metadata = MetaData()
    Table(
        "users",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("username", String(100), nullable=False, unique=True),
        Column("password", String(400), nullable=False),
        Column(
            "role",
            String(40),
            nullable=False,
            server_default=business["registration"]["default_role"],
        ),
    )
    Table(
        "tokens",
        metadata,
        Column("token", String(64), primary_key=True),
        Column("user_id", String(36), ForeignKey("users.id"), nullable=False),
        Column("expires_at", Integer, nullable=False),
    )
    relations = {(r["entity"], r["field"]): r["target_entity"] for r in business["relations"]}
    for entity in spec["entities"]:
        columns = [
            Column("id", String(36), primary_key=True),
            Column("owner_id", String(36), ForeignKey("users.id"), nullable=False),
            Column("created_by", String(36), ForeignKey("users.id"), nullable=False),
            Column("created_at", String(40), nullable=False),
            Column("updated_at", String(40), nullable=False),
            Column("archived_at", String(40), nullable=True),
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
            target = relations.get((entity["name"], field["name"]))
            if target:
                kind = String(36)
            columns.append(
                Column(
                    field["name"],
                    kind,
                    *(
                        [
                            ForeignKey(
                                ("users" if target == "$users" else target) + ".id",
                                ondelete="RESTRICT",
                            )
                        ]
                        if target
                        else []
                    ),
                    nullable=not field["required"],
                )
            )
            if field["kind"] == "integer" and not target:
                columns.append(integer_check(field))
        Table(entity["name"], metadata, *columns)
    business_tables(metadata)
    return metadata


def integer_check(field):
    low = max(
        -(2**31),
        field.get("minimum") if field.get("minimum") is not None else -(2**31),
        field["exclusive_minimum"] + 1 if field.get("exclusive_minimum") is not None else -(2**31),
    )
    high = min(
        2**31 - 1,
        field.get("maximum") if field.get("maximum") is not None else 2**31 - 1,
        field["exclusive_maximum"] - 1 if field.get("exclusive_maximum") is not None else 2**31 - 1,
    )
    return CheckConstraint(f'"{field["name"]}" BETWEEN {low} AND {high}')


def business_tables(metadata):
    Table("business_setup", metadata, Column("key", String(80), primary_key=True))
    Table(
        "business_audit",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("entity", String(40), nullable=False),
        Column("record_id", String(36), nullable=False, index=True),
        Column("actor_id", String(36), ForeignKey("users.id"), nullable=False),
        Column("action", String(80), nullable=False),
        Column("created_at", String(40), nullable=False),
        Column("before_json", String, nullable=True),
        Column("after_json", String, nullable=True),
    )
    Table(
        "business_notes",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("entity", String(40), nullable=False),
        Column("record_id", String(36), nullable=False, index=True),
        Column("actor_id", String(36), ForeignKey("users.id"), nullable=False),
        Column("created_at", String(40), nullable=False),
        Column("body", String(10000), nullable=False),
    )
    Table(
        "business_notifications",
        metadata,
        Column("id", String(36), primary_key=True),
        Column("recipient_id", String(36), ForeignKey("users.id"), nullable=False, index=True),
        Column("entity", String(40), nullable=False),
        Column("record_id", String(36), nullable=False),
        Column("event", String(40), nullable=False),
        Column("created_at", String(40), nullable=False),
        Column("read_at", String(40), nullable=True),
        Column("dedupe_key", String(64), nullable=False, unique=True),
    )
````
