"""The first database lesson must not depend on a future API or agent module."""

import os
import shutil
import subprocess
import sys

from scripts.build_learning_docs import MODULE_STAGE, stage_for
from scripts.handbook_notes import RELOCATED_MODULES
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
        "workbench/models/settings.py",
        "workbench/business/contracts.py",
        "workbench/core/contracts.py",
        "workbench/core/__init__.py",
        "workbench/errors.py",
        "workbench/templates/catalog.py",
        "workbench/templates/adapters.py",
        "workbench/templates/standards.py",
        "templates/standards/common.md",
        "templates/standards/python-basic.md",
        "templates/standards/fastapiadmin.md",
        "templates/standards/yudao-vben.md",
        "workbench/infrastructure/persistence/store.py",
        "workbench/projects/__init__.py",
        "workbench/projects/models.py",
        "workbench/infrastructure/__init__.py",
        "workbench/infrastructure/persistence/__init__.py",
        "workbench/requirements/clarification.py",
        "workbench/requirements/__init__.py",
        "tests/conftest.py",
        "tests/test_contracts.py",
        "tests/test_store.py",
    ]
    # Include only inert package scaffolding, never future implementation code.
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "workbench").rglob("__init__.py")
        if path.relative_to(ROOT).as_posix() not in names
        and stage_for(path.relative_to(ROOT).as_posix()) == 0
    )
    names.append("workbench/_compat/aliases.py")
    names.extend(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "migrations").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    for name in names:
        if name.startswith("workbench/"):
            assert stage_for(name) <= 2, name
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    env = dict(os.environ, PYTHONPATH=str(destination), PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; import sys; "
            "import workbench; import importlib; "
            '[importlib.import_module(".".join(path.parent.parts)) '
            'for path in Path("workbench").rglob("__init__.py")]; '
            "assert not any(name in sys.modules for name in "
            '("workbench.interfaces.http", "workbench.production.worker", '
            '"workbench.infrastructure.llm.gateway")); '
            "from workbench import store, model_settings, clarification; "
            "assert all(Path(module.__file__).resolve().is_relative_to(Path.cwd()) "
            "for module in (store, model_settings, clarification))",
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
    assert not (destination / "workbench/interfaces/http.py").exists()
    assert not (destination / "workbench/production/worker.py").exists()


def test_relocated_implementations_keep_their_original_learning_stage():
    for relative, original in RELOCATED_MODULES.items():
        assert stage_for(f"workbench/{relative}.py") == MODULE_STAGE[original], relative
    for path in (ROOT / "workbench").rglob("__init__.py"):
        name = path.relative_to(ROOT).as_posix()
        assert stage_for(name) == (7 if name == "workbench/coding/__init__.py" else 0)
    assert stage_for("workbench/_compat/aliases.py") == 0
    assert stage_for("workbench/cli.py") == 8
    assert stage_for("workbench/capability_sandbox.py") == 7
    assert stage_for("workbench/daytona_worker.py") == 12
