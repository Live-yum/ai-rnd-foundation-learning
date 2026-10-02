import subprocess
import sys

from scripts.build_handbook import OUTPUT, render, sources
from scripts.rebuild_from_handbook import extract, restore


def test_document_matches_every_source():
    assert OUTPUT.read_text(encoding="utf-8") == render()
    rows = extract(OUTPUT.read_text(encoding="utf-8"))
    for _, files in sources():
        for name, content in files:
            assert rows[name] == content


def test_reconstruction_is_complete(tmp_path):
    destination = tmp_path / "restored"
    restore(OUTPUT, destination)
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(destination / "workbench")], check=True
    )
    result = subprocess.run(
        [sys.executable, "-m", "scripts.build_handbook"],
        cwd=destination,
        text=True,
        capture_output=True,
        check=True,
    )
    assert (destination / OUTPUT.name).read_bytes() == OUTPUT.read_bytes(), result.stdout


def block(name, content):
    import hashlib

    fingerprint = hashlib.sha256(content.encode()).hexdigest()
    return f"<!-- source-file: {name} sha256: {fingerprint} -->\n````python\n{content}````\n"


def test_inline_marker_example_is_not_a_source_record():
    example = 'pattern = r"<!-- source-file: (.+?) sha256: ([0-9a-f]{64}) -->"\n'
    assert extract(example + block("example.py", "answer = 42\n")) == {
        "example.py": "answer = 42\n"
    }


def test_reject_partial_duplicate_or_unsafe_source_before_writing(tmp_path):
    import pytest

    valid = block("example.py", "answer = 42\n")
    invalid = [
        valid + valid,
        valid + block("missing.py", "x = 1\n").removesuffix("````\n"),
        valid + block("corrupt.py", "x = 1\n").replace("x = 1", "x = 2"),
    ]
    invalid += [
        block(name, "x = 1\n")
        for name in (
            "../escape.py",
            "/absolute.py",
            "a//alias.py",
            "./alias.py",
            ".",
            ".git/config",
            "C:drive.py",
        )
    ]
    for number, text in enumerate(invalid):
        book = tmp_path / f"bad-{number}.md"
        book.write_text(text)
        destination = tmp_path / f"must-stay-absent-{number}"
        with pytest.raises(ValueError):
            restore(book, destination)
        assert not destination.exists()


def test_standalone_bootstrap_in_the_lesson_restores_all_files(tmp_path):
    import re

    from scripts.build_handbook import ROOT

    lesson = (ROOT / "docs/implementation.md").read_text(encoding="utf-8")
    candidates = re.findall(r"```python\n(.*?)\n```", lesson, re.S)
    bootstrap = next(code for code in candidates if "rebuild_book.py" in code)
    script = tmp_path / "rebuild_book.py"
    script.write_text(bootstrap, encoding="utf-8")
    destination = tmp_path / "student-project"
    subprocess.run(
        [sys.executable, str(script), str(OUTPUT), str(destination)],
        check=True,
        env={**__import__("os").environ, "PYTHONIOENCODING": "cp1252"},
        capture_output=True,
    )
    for _, files in sources():
        for name, content in files:
            expected = content if isinstance(content, bytes) else content.encode("utf-8")
            assert (destination / name).read_bytes() == expected


def test_daytona_recipes_have_distinct_teaching_roles():
    from scripts.handbook_notes import purpose

    assert "Runner服务" in purpose("tools/daytona/runner.Dockerfile")[0]
    assert "对象存储" in purpose("tools/daytona/minio.Dockerfile")[0]
    assert "预热" in purpose("tools/daytona/Dockerfile")[0]


def test_handbook_ignores_nested_installed_dependencies(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    source = tmp_path / "templates/product"
    source.mkdir(parents=True)
    (source / "app.py").write_text("# source", encoding="utf-8")
    for cache in (".venv", "node_modules", ".git", ".data"):
        (source / cache).mkdir()
        (source / cache / "native.so").write_bytes(b"\xff\x00")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GROUPS", [("source", ["templates"])])
    assert list(builder.sources()) == [("source", [("templates/product/app.py", "# source")])]


def test_roundtrip_preserves_empty_files_and_exact_trailing_newlines(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    original = {
        "empty.py": "",
        "one-newline.txt": "\n",
        "no-newline.py": "answer = 42",
        "regular.py": "answer = 42\n",
        "trailing.py": "answer = 42\n\n\n",
        "nested.md": "````\ninside a code fence\n````\n",
    }
    for name, content in original.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", [])
    monkeypatch.setattr(builder, "GROUPS", [("source", list(original))])
    assert extract(builder.render()) == original


def test_binary_asset_roundtrip_preserves_exact_bytes_and_wrapping(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    data = b"\x89PNG\r\n\x1a\n\x00\xff" + bytes(range(256))
    (tmp_path / "screenshot.png").write_bytes(data)
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", [])
    monkeypatch.setattr(builder, "GROUPS", [("assets", ["screenshot.png"])])
    text = builder.render()
    assert "encoding: base64" in text
    assert "data:image" not in text
    assert "<details>" in text
    assert extract(text) == {"screenshot.png": data}
    book = tmp_path / "book.md"
    book.write_text(text, encoding="utf-8")
    destination = tmp_path / "restored"
    assert restore(book, destination) == 1
    assert (destination / "screenshot.png").read_bytes() == data


def test_reject_invalid_binary_before_writing(tmp_path):
    import base64
    import hashlib

    import pytest

    data = b"\x89PNG\x00\xff"
    encoded = base64.b64encode(data).decode("ascii")
    fingerprint = hashlib.sha256(data).hexdigest()
    valid = (
        f"<!-- source-file: image.png sha256: {fingerprint} encoding: base64 -->\n"
        f"````base64\n{encoded}\n````\n"
    )
    invalid = [
        valid.replace(encoded, "!not-base64!"),
        valid.replace(encoded, base64.b64encode(b"changed").decode("ascii")),
        valid.replace("encoding: base64", "encoding: unknown"),
        valid.removesuffix("````\n"),
        valid + valid,
        valid + block("image.png", "duplicate path\n"),
        valid.replace("image.png", "../image.png"),
    ]
    for number, text in enumerate(invalid):
        book = tmp_path / f"binary-bad-{number}.md"
        book.write_text(block("safe.py", "answer = 42\n") + text, encoding="utf-8")
        destination = tmp_path / f"absent-{number}"
        with pytest.raises(ValueError):
            restore(book, destination)
        assert not destination.exists()


def test_chapter_images_are_rebased_only_in_readable_handbook(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    source = "![实际画面](images/example.png)\n"
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "lesson.md").write_text(source, encoding="utf-8")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", ["docs/lesson.md"])
    monkeypatch.setattr(builder, "GROUPS", [("docs", ["docs/lesson.md"])])
    text = builder.render()
    assert text.startswith("![实际画面](docs/images/example.png)")
    assert extract(text)["docs/lesson.md"] == source
