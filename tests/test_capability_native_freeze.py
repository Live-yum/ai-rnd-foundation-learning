"""Exercise trusted freeze script against owned hostile symlink fixtures only."""

import json
from types import SimpleNamespace

import pytest

from workbench import capability_native_runtime as runtime


def captured_script(monkeypatch):
    scripts = []
    sandbox = SimpleNamespace(fs=SimpleNamespace(upload_file=lambda *a, **kw: None))

    def capture(sandbox, argv, timeout):
        scripts.append(argv[-1])
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(runtime, "control_exec", capture)
    runtime.verify_and_freeze_native_sources(sandbox, {}, 10)
    return scripts[0]


@pytest.mark.parametrize("relative", ["backend/static", "backend", "frontend/web/node_modules"])
def test_ancestor_symlink_rejected_before_privileged_mkdir_or_chown(
    tmp_path, monkeypatch, relative
):
    script = captured_script(monkeypatch)
    root = tmp_path / "product"
    root.mkdir()
    (root / "frontend/web/dist").mkdir(parents=True)
    (root / "frontend/web/dist/index.html").write_text("owned test")
    outside = tmp_path / "outside"
    outside.mkdir()
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(outside, target_is_directory=True)
    control = tmp_path / "manifest.json"
    control.write_text(json.dumps({}))
    script = script.replace("/tmp/rnd-capability/product", str(root)).replace(
        "/tmp/rnd-module-control/private/source-manifest.json", str(control)
    )
    mutations = []
    monkeypatch.setattr("os.chown", lambda *a: mutations.append(a))
    with pytest.raises(AssertionError):
        exec(compile(script, "<owned-freeze-test>", "exec"), {})
    assert mutations == []
    assert list(outside.iterdir()) == []


def test_writable_hardlink_cannot_restore_protected_source_write_access(tmp_path, monkeypatch):
    import os

    script = captured_script(monkeypatch)
    root = tmp_path / "product"
    (root / "frontend/web/dist").mkdir(parents=True)
    (root / "frontend/web/dist/index.html").write_text("owned test")
    (root / "backend/app").mkdir(parents=True)
    source = root / "backend/app/protected.py"
    source.write_text("protected = True")
    (root / "backend/logs").mkdir()
    os.link(source, root / "backend/logs/source-link")
    control = tmp_path / "manifest.json"
    control.write_text("{}")
    script = script.replace("/tmp/rnd-capability/product", str(root)).replace(
        "/tmp/rnd-module-control/private/source-manifest.json", str(control)
    )
    mutations = []
    monkeypatch.setattr("os.chown", lambda *a: mutations.append(a))
    with pytest.raises(AssertionError):
        exec(compile(script, "<owned-hardlink-test>", "exec"), {})
    assert mutations == []
    assert source.read_text() == "protected = True"
