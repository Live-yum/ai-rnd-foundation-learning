"""Compatibility import for workbench.generation.python_basic."""

import sys

from workbench.generation import python_basic as _implementation

sys.modules[__name__] = _implementation
