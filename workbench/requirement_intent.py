"""Compatibility import for workbench.requirements.intent."""

import sys

from workbench.requirements import intent as _implementation

sys.modules[__name__] = _implementation
