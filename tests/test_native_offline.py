"""Source-only native generation must be useful without executing upstream code."""

import ast
import json
import socket
import subprocess
from pathlib import Path

import pytest

from workbench.generation.native.offline import _write_new, generate_offline
from workbench.templates import vendor


def plan():
    return {
        "title": "Offline tickets",
        "data_scope": "per_user",
        "acceptance": ["Create tickets"],
        "entities": [
            {
                "name": "tickets",
                "description": "Ticket ' \" {danger()} </script>",
                "fields": [
                    {
                        "name": "title",
                        "kind": "text",
                        "label": "Title ' \" {danger()} </script>",
                        "min_length": 2,
                        "max_length": 80,
                        "searchable": True,
                    },
                    {"name": "priority", "kind": "integer", "minimum": 1, "maximum": 10},
                    {"name": "done", "kind": "boolean"},
                    {"name": "due", "kind": "date", "date_range": True},
                    {"name": "updated", "kind": "datetime", "required": False},
                    {"name": "stage", "kind": "enum", "choices": ["open", "closed"]},
                ],
            }
        ],
    }


def sources(template):
    # Exact immutable metadata supplied by prepare_sources, no mutable templates.
    return [
        {k: row[k] for k in ("slot", "sha", "source_digest")}
        for row in vendor.inventory()
        if row["template"] == template
    ]


def forbidden(*args, **kwargs):
    raise AssertionError("Offline generation attempted a process/network operation")


def test_fastapi_real_business_sources_without_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    baseline = tmp_path / "backend" / "main.py"
    baseline.parent.mkdir()
    baseline.write_text("raise RuntimeError('upstream must not execute')\n")
    receipt = generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert receipt["generation_status"] == "partial"
    assert receipt["pending_steps"]
    assert "backend/main.py" not in receipt["generated_files"]
    assert len(receipt["generated_files"]) == 12
    for name in receipt["generated_files"]:
        path = tmp_path / name
        assert path.is_file()
        if path.suffix == ".py":
            ast.parse(path.read_text())
    root = tmp_path / "backend/app/plugin/module_rnd/tickets"
    assert "class TicketsModel" in (root / "model.py").read_text()
    assert "String(80)" in (root / "model.py").read_text()
    assert "TicketsRouter" in (root / "controller.py").read_text()
    schema = ast.parse((root / "schema.py").read_text())
    create = next(
        node
        for node in schema.body
        if isinstance(node, ast.ClassDef) and node.name == "TicketsCreateSchema"
    )
    fields = {node.target.id: node for node in create.body if isinstance(node, ast.AnnAssign)}
    for name in ("title", "priority", "done", "due", "stage"):
        default = next(k.value for k in fields[name].value.keywords if k.arg == "default")
        assert isinstance(default, ast.Constant) and default.value is Ellipsis
    assert ast.unparse(fields["stage"].annotation) == "Literal['open', 'closed']"
    title_args = {k.arg: ast.literal_eval(k.value) for k in fields["title"].value.keywords}
    assert title_args["max_length"] == 80
    assert title_args["description"] == plan()["entities"][0]["fields"][0]["label"]
    api_source = (tmp_path / "frontend/web/src/api/module_rnd/tickets.ts").read_text()
    assert "/rnd/tickets" in api_source
    assert "//rnd" not in api_source
    assert (tmp_path / "frontend/web/src/views/module_rnd/tickets/index.vue").is_file()
    stored = json.loads((tmp_path / "generated/business-schema.json").read_text())
    assert stored["entities"][0]["description"] == plan()["entities"][0]["description"]


@pytest.mark.parametrize("template", ["fastapiadmin", "yudao-vben"])
def test_output_is_deterministic_and_never_clobbers(tmp_path, template):
    first, second = tmp_path / "first", tmp_path / "second"
    receipt = generate_offline(template, plan(), first, sources(template))
    assert generate_offline(template, plan(), second, sources(template)) == receipt
    for name in receipt["generated_files"]:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    marker = first / receipt["generated_files"][0]
    marker.write_text("USER EDIT")
    with pytest.raises(FileExistsError):
        generate_offline(template, plan(), first, sources(template))
    assert marker.read_text() == "USER EDIT"


def test_yudao_is_honest_sql_only_partial(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    receipt = generate_offline("yudao-vben", plan(), tmp_path, sources("yudao-vben"))
    assert receipt["generation_status"] == "partial"
    assert any("not Java/Vue" in s for s in receipt["pending_steps"])
    sql = (tmp_path / "backend/sql/workbench-business.sql").read_text()
    assert 'CREATE TABLE "wb_tickets"' in sql
    assert '"title" VARCHAR(80) NOT NULL' in sql
    assert '"due" DATE NOT NULL' in sql
    assert not any(p.endswith((".java", ".vue")) for p in receipt["generated_files"])
    template_inputs = json.loads((tmp_path / "generated/offline-template-inputs.json").read_text())
    assert "java/dal/do.vm" in template_inputs


def test_rejects_unpinned_source_and_tampered_archive(tmp_path, monkeypatch):
    bad = sources("fastapiadmin")
    bad[0]["sha"] = "bad"
    with pytest.raises(ValueError, match="pinned"):
        generate_offline("fastapiadmin", plan(), tmp_path / "out", bad)
    rows = vendor.inventory()
    fake = tmp_path / "vendor"
    fake.mkdir()
    (fake / "fastapiadmin.zip").write_bytes(b"not the pinned archive")
    monkeypatch.setattr(vendor, "inventory", lambda: rows)
    monkeypatch.setattr(vendor, "VENDOR", fake)
    with pytest.raises(ValueError, match="checksum"):
        generate_offline("fastapiadmin", plan(), tmp_path / "out", sources("fastapiadmin"))
    assert not (tmp_path / "out").exists()


def test_symlink_and_colliding_paths_leave_no_outputs(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    out = tmp_path / "out"
    out.mkdir()
    (out / "backend").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="符号链接|Symlink"):
        generate_offline("fastapiadmin", plan(), out, sources("fastapiadmin"))
    assert not list(outside.iterdir())
    assert not (out / "generated").exists()


def test_reserved_native_fields_are_not_silently_discarded(tmp_path):
    value = plan()
    value["entities"][0]["fields"][0]["name"] = "created_id"
    with pytest.raises(ValueError, match="collision"):
        generate_offline("fastapiadmin", value, tmp_path, sources("fastapiadmin"))
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "name", ["C:/escape.py", "../escape.py", "folder:stream/file.py", "a/../../escape.py"]
)
def test_windows_and_traversal_targets_rejected(tmp_path, name):
    with pytest.raises(ValueError):
        _write_new(tmp_path, {name: "unsafe"})
    assert not list(tmp_path.iterdir())


def test_casefold_existing_path_conflict_is_preflighted(tmp_path):
    (tmp_path / "BACKEND").mkdir()
    with pytest.raises(FileExistsError, match="Case-insensitive"):
        generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert not (tmp_path / "generated").exists()
    assert not list((tmp_path / "BACKEND").iterdir())


def test_windows_junction_is_rejected(tmp_path, monkeypatch):
    (tmp_path / "backend").mkdir()
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda self: self.name == "backend" or original(self))
    with pytest.raises(ValueError, match="junction"):
        generate_offline("fastapiadmin", plan(), tmp_path, sources("fastapiadmin"))
    assert not (tmp_path / "generated").exists()
