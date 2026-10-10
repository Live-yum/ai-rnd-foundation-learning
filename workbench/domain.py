"""Compatibility import; implementation lives in workbench.core.contracts."""

import sys

from workbench.core import contracts as _implementation

sys.modules[__name__] = _implementation
