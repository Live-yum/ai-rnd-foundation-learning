"""Pure SQL metadata for approved business specs; no connections or environment reads."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table


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
        Table(entity["name"], metadata, *columns)
    business_tables(metadata)
    return metadata


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
