"""Deterministic generation: approved metadata -> reviewed golden files, never LLM boilerplate."""

import ast
import json
import shutil
from pathlib import Path

from workbench.domain import Plan, digest
from workbench.filesystem import atomic_text, files, manifest, write_json
from workbench.settings import ROOT


class PrerequisiteError(RuntimeError):
    pass


def generate_basic(plan: Plan, destination: Path, selection=None):
    from workbench.catalog import Selection

    selection = Selection.model_validate(selection or {"template": "python-basic"}).model_dump()
    if plan.data_scope != "per_user" or plan.unsupported:
        raise PrerequisiteError("免服务模板仅支持逐用户 CRUD；不允许静默替换共享数据或未支持项")
    destination = Path(destination)
    if destination.is_symlink() or (
        hasattr(destination, "is_junction") and destination.is_junction()
    ):
        raise PrerequisiteError("生成目录不能是符号链接或 junction；原路径未修改")
    if destination.exists():
        error = (
            "现有产品目录缺少有效且匹配的生成回执；已保留源码、用户文件和.data数据库。"
            "请恢复此运行原有的generation.json及批准设计，或使用新的空目录生成；"
            "不自动删除、覆盖或迁移现有产品数据"
        )
        receipt = destination.parent / "generation.json"
        if not destination.is_dir() or receipt.is_symlink() or not receipt.is_file():
            raise PrerequisiteError(error)
        try:
            previous = json.loads(receipt.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise PrerequisiteError(error) from exc
        if (
            not isinstance(previous, dict)
            or previous.get("spec_digest") != digest(plan.model_dump())
            or previous.get("selection") != selection
            or not isinstance(previous.get("files"), dict)
            or not previous["files"]
        ):
            raise PrerequisiteError(error)
        # Idempotence never authorizes resetting an existing product. Runtime
        # verification separately binds its source hashes before any delivery.
        return previous
    destination.mkdir(parents=True)
    for name, source in files(ROOT / "templates" / "product"):
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    shutil.copyfile(ROOT / "workbench/rules.py", destination / "rule_engine.py")
    write_json(destination / "approved-spec.json", plan.model_dump())
    write_json(destination / "selection.json", selection)
    if selection["frontend"] == "simple-admin":
        for name, source in files(ROOT / "templates/frontends/simple-admin"):
            target = destination / "web" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    atomic_text(destination / ".python-version", "3.14\n")
    atomic_text(
        destination / "alembic.ini",
        "[alembic]\nscript_location = %(here)s/migrations\nprepend_sys_path = %(here)s\npath_separator = os\n",
    )
    atomic_text(
        destination / "migrations/env.py",
        """from alembic import context
from schema import engine
with engine.begin() as connection:
    context.configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()
""",
    )
    text = '''"""Initial, frozen business schema."""
import json
from alembic import op
import sqlalchemy as sa
revision = "0001"
down_revision = None
SPEC = json.loads(SPEC_LITERAL)
def upgrade():
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("password", sa.String(400), nullable=False))
    op.create_table("tokens", sa.Column("token", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expires_at", sa.Integer, nullable=False))
    for entity in SPEC["entities"]:
        columns = [sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False)]
        for f in entity["fields"]:
            kind = {"text": sa.String(f["max_length"]), "integer": sa.Integer(), "boolean": sa.Boolean(), "date": sa.String(10), "enum": sa.String(f["max_length"])}[f["kind"]]
            columns.append(sa.Column(f["name"], kind, nullable=not f["required"]))
        op.create_table(entity["name"], *columns)
        op.create_index("ix_" + entity["name"] + "_owner_id", entity["name"], ["owner_id"])
def downgrade():
    for entity in reversed(SPEC["entities"]):
        op.drop_table(entity["name"])
    op.drop_table("tokens")
    op.drop_table("users")
'''.replace("SPEC_LITERAL", repr(json.dumps(plan.model_dump(), ensure_ascii=False)))
    ast.parse(text)
    atomic_text(destination / "migrations/versions/0001_initial.py", text)
    from workbench.product_sql import render

    render(plan, destination)
    receipt = {
        "generator": "reviewed-python-basic-v2",
        "spec_digest": digest(plan.model_dump()),
        "selection": selection,
        "files": manifest(destination),
    }
    write_json(destination.parent / "generation.json", receipt)
    return receipt
