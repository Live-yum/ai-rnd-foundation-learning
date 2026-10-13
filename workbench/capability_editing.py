"""Compatibility import; implementation lives in workbench.coding.candidates."""

import sys

from workbench.coding import candidates as _implementation

sys.modules[__name__] = _implementation
