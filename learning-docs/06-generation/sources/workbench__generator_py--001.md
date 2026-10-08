# workbench/generator.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：确定性生成基础FastAPI产品。** generate_basic复制本项目编写的模板，再把Plan写入产品规格、路由信息和迁移文件。相同Plan使用同一套生成规则；模型不负责重写登录、数据库与整套骨架。代码字符串中的upgrade/downgrade是写入成品迁移的内容。

**对应关系：** flow生成节点 → generator → templates/product + product_sql → verification。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.settings`、`workbench.template_standards`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** generate_basic把批准Plan和已校验选择写成不可含糊的产物身份，再复制模板、生成迁移并登记每个文件SHA。第一次创建目标目录应得到完整产品；同一路径已经有文件却无相符回执时应停止并保留现场。这里不能用删除重建来伪装幂等，因为目录可能已包含用户修改或数据。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `PrerequisiteError`（L15–L16）：继承`RuntimeError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `generate_basic`（L19–L91）：接收`plan`、`destination`、`selection`。 控制顺序：L23按`(plan.business is None and plan.data_scope != "per_user") or plan.unsupported`分支；L24抛异常，停止当前正常路径；L28按`destination.is_symlink() or ( hasattr(destination, "is_junction") and destination.is_…`分支；L31抛异常，停止当前正常路径；L32按`destination.exists()`分支；L34按`destination.is_dir() and pending.is_file() and not pending.is_symlink() and not recei…`分支；L51抛异常，停止当前正常路径；L54按`recoverable`分支。后续分支沿下方源码相同行号继续阅读。 调用`Selection.model_validate(selection or {"template": "python-basic"…`、`Selection.model_validate`、`PrerequisiteError`、`Path`、`destination.is_symlink`、`hasattr`、`destination.is_junction`、`destination.exists`、`destination.is_dir`等。 返回路径：L57的`recovered`；L80的`previous`；L91的`receipt`。
- `_generate_product`（L94–L171）：接收`plan`、`destination`、`selection`。 控制顺序：L95遍历`files(ROOT / "templates" / "product")`；L102按`selection["frontend"] == "simple-admin"`分支；L103遍历`files(ROOT / "templates/frontends/simple-admin")`；L156按`plan.business is not None`分支。 调用`files`、`target.parent.mkdir`、`shutil.copyfile`、`write_json`、`plan.model_dump`、`atomic_text`、`'''"""Initial, frozen business schema.""" import json from alembi…`、`repr`、`json.dumps`等。 返回路径：L171的`receipt`。

</details>

**创建路径：** `workbench/generator.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L171。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7900`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/generator.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "05734c11d8c220ea88acc45b4aea0a55876def67c0fe0d199f393ab36f647cde"} -->
````python
# workbench/generator.py
"""Deterministic generation: approved metadata -> reviewed golden files, never LLM boilerplate."""

import ast
import json
import shutil
import tempfile
from pathlib import Path

from workbench.domain import Plan, digest
from workbench.filesystem import atomic_text, files, manifest, write_json
from workbench.settings import ROOT
from workbench.template_standards import write_coding_standard


class PrerequisiteError(RuntimeError):
    pass


def generate_basic(plan: Plan, destination: Path, selection=None):
    from workbench.catalog import Selection

    selection = Selection.model_validate(selection or {"template": "python-basic"}).model_dump()
    if (plan.business is None and plan.data_scope != "per_user") or plan.unsupported:
        raise PrerequisiteError("免服务模板仅支持逐用户 CRUD；不允许静默替换共享数据或未支持项")
    destination = Path(destination)
    receipt_path = destination.parent / "generation.json"
    pending = destination.parent / f".generation-{destination.name}.pending.json"
    if destination.is_symlink() or (
        hasattr(destination, "is_junction") and destination.is_junction()
    ):
        raise PrerequisiteError("生成目录不能是符号链接或 junction；原路径未修改")
    if destination.exists():
        # The directory rename succeeded but the final receipt write may not have.
        if (
            destination.is_dir()
            and pending.is_file()
            and not pending.is_symlink()
            and not receipt_path.is_symlink()
            and not receipt_path.is_dir()
        ):
            try:
                journal = json.loads(pending.read_text(encoding="utf-8"))
                recovered = journal["receipt"]
                recoverable = (
                    journal["destination"] == str(destination.resolve())
                    and recovered["spec_digest"] == digest(plan.model_dump())
                    and recovered["selection"] == selection
                    and recovered["files"] == manifest(destination)
                )
            except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
                raise PrerequisiteError(
                    "待恢复生成回执无效；已保留现有产品，请恢复回执或使用新目录"
                ) from exc
            if recoverable:
                write_json(receipt_path, recovered)
                pending.unlink()
                return recovered
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
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".generating-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "product"
        staging.mkdir()
        receipt = _generate_product(plan, staging, selection)
        write_json(pending, {"destination": str(destination.resolve()), "receipt": receipt})
        # rename, never copy, so a published product is always complete.
        staging.rename(destination)
        write_json(receipt_path, receipt)
        pending.unlink()
        return receipt


def _generate_product(plan, destination, selection):
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
from fields import integer_bounds
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
            kind = {"text": sa.String(f["max_length"]), "integer": sa.Integer(), "boolean": sa.Boolean(), "date": sa.String(10), "datetime": sa.String(40), "enum": sa.String(f["max_length"])}[f["kind"]]
            columns.append(sa.Column(f["name"], kind, nullable=not f["required"]))
            if f["kind"] == "integer":
                low, high = integer_bounds(f)
                columns.append(sa.CheckConstraint(f'"{f["name"]}" BETWEEN {low} AND {high}'))
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
    if plan.business is not None:
        from workbench.business_python import prepare_product

        prepare_product(plan, destination)
    else:
        from workbench.product_sql import render

        render(plan, destination)
    write_coding_standard(destination, selection["template"])
    receipt = {
        "generator": "reviewed-python-basic-v2",
        "spec_digest": digest(plan.model_dump()),
        "selection": selection,
        "files": manifest(destination),
    }
    return receipt
````
