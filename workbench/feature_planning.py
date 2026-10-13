"""Compatibility import; implementation lives in workbench.planning.feature_planner."""

import sys

from workbench.planning import feature_planner as _implementation

sys.modules[__name__] = _implementation
