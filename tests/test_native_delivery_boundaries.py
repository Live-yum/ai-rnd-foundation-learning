"""Native product source must not export server logs or include secret credentials."""

from workbench.filesystem import files, manifest
from workbench.native_environment import copy_source


def test_native_runtime_logs_never_enter_source_manifest(tmp_path):
    (tmp_path / "app.py").write_text("print('native')\n", encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs/server.log").write_text("password=local-example\n", encoding="utf-8")
    (tmp_path / ".env.native").write_text("NATIVE_DB_PASSWORD=private\n", encoding="utf-8")
    assert set(dict(files(tmp_path))) == {"app.py"}
    assert set(manifest(tmp_path)) == {"app.py"}


def test_source_copy_is_independent_of_generated_edits(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "module.py").write_text("original\n", encoding="utf-8")
    before = manifest(source)
    copied = tmp_path / "product"
    copy_source(source, copied)
    (copied / "module.py").write_text("generated\n", encoding="utf-8")
    assert manifest(source) == before
    assert manifest(copied) != before
