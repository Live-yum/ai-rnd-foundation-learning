"""Every complete teaching experiment must run as written, without network/model keys."""

import os
import re
import subprocess
import sys

import pytest

from scripts.build_handbook import ROOT

LESSON = ROOT / "docs/implementation-labs.md"
BLOCKS = re.findall(
    r"```python\n(# lesson: (\d+)\n.*?)\n```", LESSON.read_text(encoding="utf-8"), re.S
)


def test_all_expected_lessons_are_present():
    assert [number for _, number in BLOCKS] == [f"{number:02d}" for number in range(7)]


@pytest.mark.parametrize("source,number", BLOCKS, ids=[number for _, number in BLOCKS])
def test_complete_lesson_runs_from_the_printed_code(source, number, tmp_path):
    path = tmp_path / f"lesson_{number}.py"
    path.write_text(source + "\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONIOENCODING": "utf-8"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_teaching_notes_do_not_confuse_same_named_functions():
    from scripts.handbook_notes import notes

    auth = notes("workbench/api.py", "def auth():\n    return None\n")
    sql = notes("workbench/product_sql.py", "def render():\n    return None\n")
    assert "不联系Dex" in auth
    assert "真实签发" not in auth
    assert "可读DDL" in sql
    assert "生成物完全由正文" not in sql
