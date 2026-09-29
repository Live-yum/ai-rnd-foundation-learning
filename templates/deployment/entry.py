"""Standalone native delivery entrypoint. Requires uv and the original language tools."""

import os
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    args = [
        "uv",
        "run",
        "--locked",
        "--project",
        str(root / "deployment"),
        "python",
        str(root / "deployment/run.py"),
        *sys.argv[1:],
    ]
    result = subprocess.run(args, cwd=root, env=os.environ.copy(), check=False)
    raise SystemExit(result.returncode)
