"""Compatibility import for workbench.interfaces.http."""

import sys

from workbench.interfaces import http as _implementation

sys.modules[__name__] = _implementation
