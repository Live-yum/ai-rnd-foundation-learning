"""The first database lesson must not depend on a future API or agent module."""

import os
import shutil
import subprocess
import sys

from workbench.settings import ROOT


def test_database_lesson_runs_from_only_its_documented_files(tmp_path):
    destination = tmp_path / "lesson"
    names = [
        "pyproject.toml",
        "alembic.ini",
        "README.md",
        "workbench/__init__.py",
        "workbench/local_only.py",
        "workbench/settings.py",
        "workbench/domain.py",
        "workbench/errors.py",
        "workbench/catalog.py",
        "workbench/store.py",
        "tests/conftest.py",
        "tests/test_contracts.py",
        "tests/test_store.py",
    ]
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "migrations").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for name in names:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    env = dict(os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; import workbench.store; assert Path(workbench.store.__file__).resolve().is_relative_to(Path.cwd())",
        ],
        cwd=destination,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    assert probe.returncode == 0, probe.stderr
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_contracts.py", "tests/test_store.py", "-q"],
        cwd=destination,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (destination / "workbench/api.py").exists()
    assert not (destination / "workbench/runtime.py").exists()
