"""Stable introspected PostgreSQL schema evidence for owned portable business tables."""

import json

from sqlalchemy import inspect


def table_signature(connection, name):
    inspector = inspect(connection)
    if not inspector.has_table(name):
        return None

    def ordered(values):
        return sorted(values, key=lambda item: json.dumps(item, sort_keys=True))

    return {
        "columns": sorted(
            [
                {"name": c["name"], "type": str(c["type"]), "nullable": c["nullable"]}
                for c in inspector.get_columns(name)
            ],
            key=lambda c: c["name"],
        ),
        "primary_key": inspector.get_pk_constraint(name)["constrained_columns"],
        "foreign_keys": ordered(
            [
                {
                    "columns": f["constrained_columns"],
                    "table": f["referred_table"],
                    "targets": f["referred_columns"],
                    "options": f["options"],
                }
                for f in inspector.get_foreign_keys(name)
            ]
        ),
        "unique": ordered(
            [{"columns": u["column_names"]} for u in inspector.get_unique_constraints(name)]
        ),
        "indexes": ordered(
            [
                {"columns": i["column_names"], "unique": bool(i["unique"])}
                for i in inspector.get_indexes(name)
                if not i.get("duplicates_constraint")
            ]
        ),
    }


def verify_tables(connection, expected):
    for name, signature in expected.items():
        if table_signature(connection, name) != signature:
            raise ValueError("Owned business schema mismatch; preserve database: " + name)
