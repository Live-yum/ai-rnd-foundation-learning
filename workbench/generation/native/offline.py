"""Portable source-only native generation from checksum-pinned templates.

Never imports upstream Python, starts services, executes SQL, or contacts a model.
A generated file receipt excludes the baseline copied by the caller. Partial means
that these sources still need integration, not that they have passed runtime QA.
"""

import ast
import hashlib
import json
import keyword
import re
import zipfile
from pathlib import Path

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

from workbench.core.contracts import Plan
from workbench.filesystem import inside
from workbench.templates import vendor

_RESERVED = {
    "id",
    "uuid",
    "tenant_id",
    "created_time",
    "updated_time",
    "created_id",
    "updated_id",
    "is_deleted",
    "deleted_time",
    "deleted_id",
}
_TYPES = {
    "text": ("str", "String"),
    "enum": ("str", "String"),
    "integer": ("int", "Integer"),
    "boolean": ("bool", "Boolean"),
    "date": ("date", "Date"),
    "datetime": ("datetime", "DateTime"),
}


def _identifier(value):
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value) or keyword.iskeyword(value):
        raise ValueError("Unsafe native identifier: " + value)
    return value


def _templates(template, sources):
    """Read trusted archive bytes, never templates from a mutable runtime tree."""
    slot = "fastapiadmin" if template == "fastapiadmin" else "backend"
    row = next(r for r in vendor.inventory() if r["template"] == template and r["slot"] == slot)
    source = next((s for s in sources if s.get("slot") == slot), None)
    if not source or any(source.get(k) != row[k] for k in ("sha", "source_digest")):
        raise ValueError("Offline generation requires the prepared, pinned source receipt")
    archive = vendor.VENDOR / row["archive"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != row["archive_sha256"]:
        raise ValueError("Bundled template archive checksum mismatch")
    prefix = (
        "backend/templates/"
        if template == "fastapiadmin"
        else ("yudao-module-infra/yudao-module-infra-server/src/main/resources/codegen/")
    )
    suffix = ".jinja2" if template == "fastapiadmin" else ".vm"
    with zipfile.ZipFile(archive) as bundle:
        return {
            n[len(prefix) :]: bundle.read(n).decode("utf-8")
            for n in sorted(bundle.namelist())
            if n.startswith(prefix) and n.endswith(suffix)
        }


def _context(entity):
    columns = [
        {
            "column_name": "id",
            "column_comment": "id",
            "python_type": "int",
            "sqlalchemy_type": "Integer",
            "is_nullable": False,
            "is_pk": True,
            "is_increment": True,
            "is_unique": False,
            "is_insert": False,
            "is_edit": False,
            "is_list": True,
            "is_query": False,
            "html_type": "input",
            "dict_type": "",
            "query_type": "EQ",
        }
    ]
    for field in entity.fields:
        py_type, sa_type = _TYPES[field.kind]
        columns.append(
            {
                "column_name": field.name,
                "column_comment": field.name,
                "python_type": py_type,
                "sqlalchemy_type": f"String({field.max_length})"
                if sa_type == "String"
                else sa_type,
                "is_nullable": not field.required,
                "is_pk": False,
                "is_increment": False,
                "is_unique": False,
                "is_insert": True,
                "is_edit": True,
                "is_list": True,
                "is_query": field.searchable or field.filterable or field.date_range,
                "html_type": "datetime" if field.kind in {"date", "datetime"} else "input",
                "dict_type": "",
                "query_type": "LIKE" if field.searchable else "EQ",
            }
        )
    imports = [
        "from sqlalchemy import " + ", ".join(sorted({_TYPES[f.kind][1] for f in entity.fields}))
    ]
    dates = sorted({_TYPES[f.kind][0] for f in entity.fields if f.kind in {"date", "datetime"}})
    date_imports = ["from datetime import " + ", ".join(dates)] if dates else []
    return {
        "class_name": "".join(x.capitalize() for x in entity.name.split("_")),
        "module_name": entity.name,
        "table_name": "wb_" + entity.name,
        # Upstream templates interpolate labels into mixed Python/JS/HTML contexts.
        # Use safe identifiers there; preserve full human labels in approved schema.
        "function_name": entity.name,
        "package_name": "module_rnd",
        "plugin_name": "rnd",
        "permission_prefix": "module_rnd:" + entity.name,
        "api_route_prefix": "rnd",
        "pk_column": columns[0],
        "pk_column_name": "id",
        "columns": columns,
        "table": {"sub": False},
        "is_sub_entity": False,
        "model_import_list": date_imports + imports,
        "schema_import_list": date_imports,
        "has_dict_column": False,
        "has_image_column": False,
        "has_json_column": False,
    }


def _schema(rendered, entity, class_name):
    """Replace upstream's permissive create/update defaults with approved fields.

    AST editing does not execute either generated code or upstream code. In
    particular a required boolean/date is not silently made optional by Jinja.
    """
    tree = ast.parse(rendered)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name not in {
            class_name + "CreateSchema",
            class_name + "UpdateSchema",
        }:
            continue
        updating = node.name.endswith("UpdateSchema")
        declarations = []
        for field in entity.fields:
            annotation = _TYPES[field.kind][0]
            if field.kind == "enum":
                annotation = "Literal[" + ", ".join(repr(v) for v in field.choices) + "]"
            optional = not field.required or updating
            if optional:
                annotation += " | None"
            arguments = [
                "default=" + ("None" if optional else "..."),
                "description=" + repr(field.label or field.name),
            ]
            if field.kind in {"text", "enum"}:
                arguments += [f"min_length={field.min_length}", f"max_length={field.max_length}"]
                if field.pattern is not None:
                    arguments.append("pattern=" + repr(field.pattern))
            for attr, argument in (
                ("minimum", "ge"),
                ("maximum", "le"),
                ("exclusive_minimum", "gt"),
                ("exclusive_maximum", "lt"),
            ):
                value = getattr(field, attr)
                if value is not None:
                    arguments.append(f"{argument}={value!r}")
            declarations.extend(
                ast.parse(f"{field.name}: {annotation} = Field({', '.join(arguments)})").body
            )
        node.body = declarations
    tree.body.insert(0, ast.ImportFrom(module="typing", names=[ast.alias(name="Literal")], level=0))
    return ast.unparse(ast.fix_missing_locations(tree)) + "\n"


def _fastapi(plan, templates):
    env = SandboxedEnvironment(
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    env.filters["get_sqlalchemy_type"] = lambda column: column["sqlalchemy_type"]
    env.filters["python_to_ts_type"] = lambda value: {
        "str": "string",
        "int": "number",
        "bool": "boolean",
        "date": "string",
        "datetime": "string",
    }[value]
    result = {}
    base = "backend/app/plugin/module_rnd"
    for entity in plan.entities:
        context = _context(entity)
        for name in ("__init__", "model", "schema", "crud", "service", "controller"):
            rendered = env.from_string(templates[f"python/{name}.py.jinja2"]).render(context)
            if name == "schema":
                rendered = _schema(rendered, entity, context["class_name"])
            ast.parse(rendered)
            result[f"{base}/{entity.name}/{name}.py"] = rendered
        for kind, name, output in (
            ("ts", "api.ts", f"frontend/web/src/api/module_rnd/{entity.name}.ts"),
            ("vue", "index.vue", f"frontend/web/src/views/module_rnd/{entity.name}/index.vue"),
        ):
            result[output] = env.from_string(templates[f"{kind}/{name}.jinja2"]).render(context)
    result[f"{base}/__init__.py"] = templates["python/package_init.py.jinja2"]
    result[f"{base}/plugin.toml"] = env.from_string(templates["python/plugin.toml.jinja2"]).render(
        plugin_name="rnd", function_name="Approved workbench business sources", module_name="rnd"
    )
    return result


def _sql(plan):
    """PostgreSQL draft business tables, not a complete runtime migration.

    This intentionally has stable, un-hashed table names: the native runtime must
    select its run-specific mapping before applying a reviewed migration.
    """
    blocks = [
        "-- PostgreSQL business-table DRAFT ONLY; not a complete Yudao migration.\n"
        "-- Review audit columns, tenant isolation, constraints and run-specific names before use."
    ]
    for entity in plan.entities:
        columns = ['  "id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY']
        for field in entity.fields:
            sql_type = {
                "text": f"VARCHAR({field.max_length})",
                "enum": f"VARCHAR({field.max_length})",
                "integer": "INTEGER",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "TIMESTAMP WITHOUT TIME ZONE",
            }[field.kind]
            columns.append(
                f'  "{field.name}" {sql_type}' + (" NOT NULL" if field.required else " NULL")
            )
        blocks.append(f'CREATE TABLE "wb_{entity.name}" (\n' + ",\n".join(columns) + "\n);")
    return "\n\n".join(blocks) + "\n"


def _write_new(destination, contents):
    root = Path(destination).absolute()
    # Reject symlinks even if their current targets happen to be inside root.
    for parent in (root, *root.parents):
        if parent.is_symlink() or (hasattr(parent, "is_junction") and parent.is_junction()):
            raise ValueError("Symlink or junction destination is not allowed")
    targets = []
    seen = set()
    for name, content in sorted(contents.items()):
        path = inside(root, name)
        relative = path.relative_to(root)
        if relative.as_posix().casefold() in seen:
            raise ValueError("Case-insensitive generated path collision")
        seen.add(relative.as_posix().casefold())
        current = root
        for part in relative.parts:
            if current.is_dir() and any(
                child.name.casefold() == part.casefold() and child.name != part
                for child in current.iterdir()
            ):
                raise FileExistsError("Case-insensitive existing path collision: " + name)
            current = current / part
        if path.exists():
            raise FileExistsError("Refusing to overwrite generated target: " + name)
        targets.append((path, content))
    written = []
    try:
        for path, content in targets:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8", newline="\n") as output:
                written.append(path)
                output.write(content)
    except Exception:
        for path in written:
            path.unlink()
        raise


def generate_offline(template, plan, destination, sources):
    """Generate actual business files into the caller's copied runtime layout.

    ``sources`` is the list returned by prepare_sources. No baseline file is
    counted as generated. Existing files are never overwritten, even on retries.
    """
    if template not in {"fastapiadmin", "yudao-vben"}:
        raise ValueError("Unsupported offline native template")
    plan = Plan.model_validate(plan)
    for entity in plan.entities:
        _identifier(entity.name)
        for field in entity.fields:
            _identifier(field.name)
            if field.name in _RESERVED:
                raise ValueError("Native base-model field collision: " + field.name)
    templates = _templates(template, sources)
    if not templates:
        raise ValueError("Pinned source has no native templates")
    if template == "fastapiadmin":
        contents = _fastapi(plan, templates)
        pending = [
            "Register generated plugins, menus and role permissions in a development runtime.",
            "Implement and verify approved data isolation, business rules and acceptance criteria.",
            "Wire approved human labels and enum selectors into the generated frontend.",
        ]
    else:
        contents = {"backend/sql/workbench-business.sql": _sql(plan)}
        pending = [
            "Render Yudao Java and Vben sources using an approved native Velocity codegen runtime; "
            "the portable adapter generated SQL and schema only, not Java/Vue business code.",
            "Turn the PostgreSQL draft into a reviewed run-specific migration with Yudao audit "
            "columns, enum/bounds constraints, menus, permissions "
            "and approved business behavior before runtime acceptance.",
        ]
    contents["generated/business-schema.json"] = (
        json.dumps(plan.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, indent=2)
        + "\n"
    )
    contents["generated/offline-template-inputs.json"] = (
        json.dumps(
            {name: hashlib.sha256(text.encode()).hexdigest() for name, text in templates.items()},
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    _write_new(destination, contents)
    return {
        "generated_files": sorted(contents),
        "generation_status": "partial",
        "pending_steps": pending,
    }
