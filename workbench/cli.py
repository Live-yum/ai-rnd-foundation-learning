"""Compatible import and executable entry for workbench.interfaces.cli."""

import sys

from workbench.interfaces import cli as _implementation

if __name__ == "__main__":
    _implementation.app()
else:
    sys.modules[__name__] = _implementation
