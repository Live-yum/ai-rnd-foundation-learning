"""Compatibility import; implementation lives in workbench.coding.aider."""

import sys

from workbench.coding import aider as _implementation

sys.modules[__name__] = _implementation
