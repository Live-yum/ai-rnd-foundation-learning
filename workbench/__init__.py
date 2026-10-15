"""Approval-gated workbench; hosted telemetry is disabled before library imports."""

from workbench.local_only import disable_telemetry

disable_telemetry()

# Keep optional providers and workflow modules unloaded during package startup.
from workbench._compat import install as _install_legacy_imports  # noqa: E402

_install_legacy_imports()
del _install_legacy_imports
