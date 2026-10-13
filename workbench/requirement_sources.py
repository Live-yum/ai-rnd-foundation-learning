"""Compatibility import; implementation lives in workbench.requirements.source_ledger."""

import sys

from workbench.requirements import source_ledger as _implementation

sys.modules[__name__] = _implementation
