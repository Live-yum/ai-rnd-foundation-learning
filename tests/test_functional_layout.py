"""Legacy imports are the same lazy modules, not copies or eager proxies."""

import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from workbench._compat import _AliasFinder, install
from workbench._compat.aliases import ALIASES

ROOT = Path(__file__).resolve().parents[1]


def isolated(source, *arguments):
    result = subprocess.run(
        [sys.executable, "-c", source, *arguments],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("legacy,canonical", sorted(ALIASES.items()))
@pytest.mark.parametrize("canonical_first", [False, True])
def test_alias_identity_in_fresh_interpreter(legacy, canonical, canonical_first):
    isolated(
        """
import importlib, sys, workbench
old_name, new_name, first = sys.argv[1:]
first = first == 'True'
a = importlib.import_module(new_name if first else old_name)
b = importlib.import_module(old_name if first else new_name)
assert a is b
assert getattr(workbench, old_name.rsplit('.', 1)[1]) is a
assert sys.modules[old_name] is sys.modules[new_name]
assert a.__spec__.name == new_name
assert a.__name__ == new_name
marker = object()
a._compatibility_probe = marker
assert b._compatibility_probe is marker
b._compatibility_probe = None
assert a._compatibility_probe is None
assert importlib.reload(b) is a
""",
        legacy,
        canonical,
        str(canonical_first),
    )


def test_package_startup_is_lazy_and_disables_telemetry():
    isolated("""
import os, sys
os.environ['LANGSMITH_TRACING'] = 'true'
import workbench
assert os.environ['LANGSMITH_TRACING'] == 'false'
for module in ('fastapi', 'sqlalchemy', 'langgraph', 'daytona', 'psycopg',
               'workbench.coding.aider', 'workbench.production.worker'):
    assert module not in sys.modules, module
""")


def test_finder_is_exact_and_installation_is_idempotent():
    install()
    install()
    assert sum(isinstance(finder, _AliasFinder) for finder in sys.meta_path) == 1
    finder = _AliasFinder()
    for unknown in ("json", "workbench.nonexistent", "workbench.aider_tool.extra"):
        assert finder.find_spec(unknown) is None
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("workbench.nonexistent")


def test_failed_target_import_cleans_alias_and_can_retry(tmp_path):
    isolated("""
import importlib, sys, types
from workbench._compat.aliases import ALIASES
name = 'workbench._missing_compatibility_fixture'
target = 'workbench._missing_target_fixture'
ALIASES[name] = target
try:
    importlib.import_module(name)
except ModuleNotFoundError as exc:
    assert exc.name == target
else:
    raise AssertionError('Failure was swallowed')
assert name not in sys.modules
implementation = types.ModuleType(target)
sys.modules[target] = implementation
assert importlib.import_module(name) is implementation
""")


def test_concurrent_alias_and_canonical_imports():
    isolated("""
import concurrent.futures, importlib, threading
barrier = threading.Barrier(8)
def load(index):
    barrier.wait(timeout=10)
    return importlib.import_module(
        'workbench.aider_tool' if index % 2 else 'workbench.coding.aider')
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    modules = list(pool.map(load, range(8)))
assert all(module is modules[0] for module in modules)
""")


def test_root_inventory_is_small_and_aliases_do_not_shadow_packages():
    assert {path.name for path in (ROOT / "workbench").glob("*.py")} == {
        "__init__.py",
        "settings.py",
        "local_only.py",
        "filesystem.py",
        "errors.py",
        "cli.py",
        "daytona_worker.py",
        "capability_sandbox.py",
    }
    assert len(ALIASES) == 97
    for legacy, canonical in ALIASES.items():
        assert legacy != canonical and canonical not in ALIASES
        assert not (ROOT / legacy.replace(".", "/")).exists()
        assert not (ROOT / (legacy.replace(".", "/") + ".py")).exists()
        assert (ROOT / (canonical.replace(".", "/") + ".py")).is_file()


@pytest.mark.parametrize(
    "legacy,canonical",
    [
        ("workbench.cli", "workbench.interfaces.cli"),
        ("workbench.daytona_worker", "workbench.infrastructure.sandbox.daytona.worker"),
        ("workbench.capability_sandbox", "workbench.acceptance.capability_sandbox"),
    ],
)
def test_physical_command_wrappers_preserve_module_identity(legacy, canonical):
    assert importlib.import_module(legacy) is importlib.import_module(canonical)


def test_old_cli_module_entry_still_executes():
    result = subprocess.run(
        [sys.executable, "-m", "workbench.cli", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "NO_COLOR": "1", "TERM": "dumb"},
    )
    assert result.returncode == 0, result.stderr
    assert all(command in result.stdout for command in ("start", "chat", "tools"))


def test_legacy_checkpoint_class_path_restores_canonical_type():
    # Match JsonPlus's historical Pydantic msgpack representation. Do not enable
    # pickle or expand the production serializer's allowed module policy.
    import ormsgpack
    from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

    from workbench.business.contracts import BusinessRole

    fields = {"name": "manager", "label": "Manager"}
    role = BusinessRole.model_validate(fields)
    payload = ormsgpack.packb(
        ormsgpack.Ext(
            5,
            ormsgpack.packb(
                [
                    "workbench.business_contracts",
                    "BusinessRole",
                    role.model_dump(),
                    "model_validate",
                ]
            ),
        )
    )
    serializer = JsonPlusSerializer(pickle_fallback=False, allowed_msgpack_modules=None)
    restored = serializer.loads_typed(("msgpack", payload))
    # Production deliberately blocks arbitrary class reconstruction and restores
    # its data; migration must preserve this fail-closed behavior.
    assert restored == role.model_dump()
    assert BusinessRole.model_validate(restored) == role
    # A consumer explicitly allowing the historical type still resolves it to
    # the same canonical class. This does not change the production policy.
    permitted = JsonPlusSerializer(
        pickle_fallback=False,
        allowed_msgpack_modules=[("workbench.business_contracts", "BusinessRole")],
    )
    decoded = permitted.loads_typed(("msgpack", payload))
    assert type(decoded) is BusinessRole
    assert decoded == role


def test_security_source_identities_cover_alias_routing_and_real_implementations():
    from workbench.capability_browser_isolation import BROWSER_SOURCES
    from workbench.capability_execution import SOURCE_FILES

    import_sources = {
        "workbench/__init__.py",
        "workbench/_compat/__init__.py",
        "workbench/_compat/aliases.py",
        "workbench/capability_sandbox.py",
    }
    assert import_sources <= set(SOURCE_FILES) & set(BROWSER_SOURCES)
    assert "workbench/acceptance/capability_sandbox.py" in SOURCE_FILES
    assert "workbench/infrastructure/sandbox/browser/isolation.py" in BROWSER_SOURCES
    for name in set(SOURCE_FILES) | set(BROWSER_SOURCES):
        assert (ROOT / name).is_file(), name
