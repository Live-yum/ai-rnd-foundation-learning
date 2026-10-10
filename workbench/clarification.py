"""Compatibility import; implementation lives in workbench.requirements.clarification."""

import sys

from workbench.requirements import clarification as _implementation

sys.modules[__name__] = _implementation
