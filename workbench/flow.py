"""Compatibility import for workbench.production.graph."""

import sys

from workbench.production import graph as _implementation

sys.modules[__name__] = _implementation
