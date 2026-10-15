"""Compatible import and executable entry for workbench.infrastructure.sandbox.daytona.worker."""

import sys

from workbench.infrastructure.sandbox.daytona import worker as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
