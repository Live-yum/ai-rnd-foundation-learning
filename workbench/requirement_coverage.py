"""Compatibility import; implementation lives in workbench.requirements.coverage."""

import sys

from workbench.requirements import coverage as _implementation

sys.modules[__name__] = _implementation
