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
    subprocess.run([sys.executable, str(script), str(OUTPUT), str(destination)], check=True)
    for _, files in sources():
        for name, content in files:
            assert (destination / name).read_text(encoding="utf-8") == content


def test_daytona_recipes_have_distinct_teaching_roles():
    from scripts.handbook_notes import purpose

    assert "Runner服务" in purpose("tools/daytona/runner.Dockerfile")[0]
    assert "对象存储" in purpose("tools/daytona/minio.Dockerfile")[0]
    assert "预热" in purpose("tools/daytona/Dockerfile")[0]
