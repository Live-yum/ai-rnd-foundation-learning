"""Lazy, exact legacy module aliases with the canonical module's identity.

This is import compatibility only. Executable legacy names keep physical entry
points. No target is imported during installation, including optional runtimes.
"""

import importlib
import importlib.abc
import importlib.util
import sys

from .aliases import ALIASES


class _AliasLoader(importlib.abc.Loader):
    def __init__(self, target):
        self.target = target

    def create_module(self, spec):
        # Returning the target here would let importlib replace its canonical spec.
        return None

    def exec_module(self, module):
        implementation = importlib.import_module(self.target)
        sys.modules[module.__name__] = implementation


class _AliasFinder(importlib.abc.MetaPathFinder):
    _workbench_legacy_aliases = True

    def find_spec(self, fullname, path=None, target=None):
        implementation = ALIASES.get(fullname)
        if implementation is None:
            return None
        return importlib.util.spec_from_loader(fullname, _AliasLoader(implementation))


def install():
    """Install once, after normal finders; real modules always take precedence."""
    if not any(getattr(finder, "_workbench_legacy_aliases", False) for finder in sys.meta_path):
        sys.meta_path.append(_AliasFinder())
