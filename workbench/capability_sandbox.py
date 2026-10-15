"""Compatible import and executable entry for workbench.acceptance.capability_sandbox."""

import sys

from workbench.acceptance import capability_sandbox as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation
