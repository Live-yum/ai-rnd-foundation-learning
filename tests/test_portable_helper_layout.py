"""Standalone native delivery must resolve its own deliberately bounded helpers."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from workbench.delivery.portable import HELPER_RESOURCES, HELPERS
from workbench.settings import ROOT


def test_portable_helpers_include_package_parents():
    assert len(HELPERS) == len(set(HELPERS))
    assert "_compat/__init__.py" in HELPERS
    assert "_compat/aliases.py" in HELPERS
    for name in HELPERS:
        assert (ROOT / "workbench" / name).is_file(), name
        for parent in Path(name).parents:
            if str(parent) != ".":
                assert (parent / "__init__.py").as_posix() in HELPERS
    assert "production/worker.py" not in HELPERS
    assert "interfaces/http.py" not in HELPERS


def test_portable_helpers_import_without_checkout(tmp_path):
    deployment = tmp_path / "deployment"
    for name in HELPERS:
        target = deployment / "workbench" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "workbench" / name, target)
    for name in HELPER_RESOURCES:
        target = deployment / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    shutil.copyfile(ROOT / "templates/deployment/run.py", deployment / "run.py")
    modules = [
        "workbench." + name[:-3].replace("/", ".")
        for name in HELPERS
        if not name.endswith("__init__.py")
    ]
    code = """
import importlib, importlib.abc, pathlib, runpy, sys
class NoPlatformServices(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.', 1)[0] in {'fastapi', 'langgraph', 'daytona'}:
            raise ModuleNotFoundError('Platform-only dependency in delivery: ' + fullname)
sys.meta_path.insert(0, NoPlatformServices())
root = pathlib.Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root))
for name in __import__('json').loads(sys.argv[2]):
    module = importlib.import_module(name)
    assert pathlib.Path(module.__file__).resolve().is_relative_to(root), name
from workbench.settings import ROOT
assert ROOT == root
from workbench.catalog import Selection
assert Selection(template='fastapiadmin').template == 'fastapiadmin'
from workbench.native_environment import checked_database
assert checked_database is importlib.import_module(
    'workbench.infrastructure.native.environment').checked_database
assert 'workbench.production.worker' not in sys.modules
assert 'workbench.interfaces.http' not in sys.modules
sys.argv = ['run.py', '--help']
runpy.run_path(str(root / 'run.py'), run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-I", "-B", "-c", code, str(deployment), json.dumps(modules)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "--check" in result.stdout
