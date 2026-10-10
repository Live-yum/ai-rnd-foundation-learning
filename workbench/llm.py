"""Compatibility import for workbench.infrastructure.llm.gateway."""

import sys

from workbench.infrastructure.llm import gateway as _implementation

sys.modules[__name__] = _implementation
