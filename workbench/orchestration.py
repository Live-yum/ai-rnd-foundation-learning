"""Compatibility import for workbench.production.dispatcher."""

import sys

from workbench.production import dispatcher as _implementation

sys.modules[__name__] = _implementation
