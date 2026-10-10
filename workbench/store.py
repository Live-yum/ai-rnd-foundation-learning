"""Compatibility import for workbench.infrastructure.persistence.store."""

import sys

from workbench.infrastructure.persistence import store as _implementation

sys.modules[__name__] = _implementation
