import io
import zipfile

import pytest

from workbench.coding import apply_patch
from workbench.domain import Patch
from workbench.filesystem import inside, manifest, unpack
from workbench.generator import PrerequisiteError, generate_basic
from workbench.knowledge import build_index, context_for
from workbench.rules import Rules, UnsafeRule
from workbench.verification import verify_basic


@pytest.mark.parametrize(
    "source",
    [
        "import os",
        "def validate(entity, data):\n    import os",
        'def validate(entity, data):\n    open("x")',
        "def validate(entity, data):\n    while True: pass",
        "def validate(entity, data):\n    return data.__class__",
        "def validate(entity, data):\n    x = 1",
        'def validate(entity, data):\n    return eval("1")',
    ],
)
def test_rule_sandbox_rejects(source):
    with pytest.raises((UnsafeRule, SyntaxError)):
        Rules(source)


def test_rule_validation():
    rule = Rules(
        "def validate(entity, data):\n    if data.get('age', 0) < 18:\n        raise ValueError('adult only')\n"
    )
    rule.validate("user", {"age": 20})
    with pytest.raises(ValueError):
        rule.validate("user", {"age": 12})


@pytest.mark.parametrize("path", ["../x", "/etc/passwd", "C:/x", "..\\x", "file:stream"])
def test_path_boundary(tmp_path, path):
    with pytest.raises(ValueError):
        inside(tmp_path, path)


@pytest.mark.parametrize("path", ["../evil", ".env", "secret.key"])
def test_zip_rejects(tmp_path, path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(path, "x")
    archive.seek(0)
    with pytest.raises(ValueError):
        unpack(archive, tmp_path / "out")


def test_duplicate_case_zip_rejected(tmp_path):
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("a.txt", "one")
        z.writestr("A.txt", "two")
    archive.seek(0)
    with pytest.raises(ValueError):
        unpack(archive, tmp_path)


def test_secret_not_indexed_cache_staleness(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.py").write_text("def hello():\n    return 1\n", encoding="utf-8")
    (source / ".env").write_text("API_KEY=secret")
    index = tmp_path / "index"
    assert build_index(source, index)["parsed_python"] == 1
    assert build_index(source, index)["reused"] == 1
    assert ".env" not in manifest(source)
    assert "a.py" in context_for(source, index, ["a.py"])["files"]
    (source / "a.py").write_text("x = 2")
    with pytest.raises(ValueError):
        context_for(source, index, ["a.py"])


def test_stale_patch_and_template_tamper(settings, plan):
    product = settings.data_dir / "runs" / "test" / "product"
    generate_basic(plan, product)
    with pytest.raises(ValueError):
        apply_patch(
            product,
            Patch(
                path="custom_rules.py",
                before_sha256="0" * 64,
                content="def validate(entity, data):\n    pass\n",
            ),
        )
    (product / "app.py").write_text('print("fake success")')
    with pytest.raises(PrerequisiteError):
        verify_basic(plan, product, settings)
