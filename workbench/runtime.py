"""Compatibility import for workbench.production.worker."""

import sys

from workbench.production import worker as _implementation

sys.modules[__name__] = _implementation
