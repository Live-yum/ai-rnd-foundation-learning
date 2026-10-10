"""Compatibility import; implementation lives in workbench.planning.contracts."""

import sys

from workbench.planning import contracts as _implementation

sys.modules[__name__] = _implementation
