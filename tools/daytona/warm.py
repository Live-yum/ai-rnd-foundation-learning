"""Prewarm only locked build dependencies; this is not runtime acceptance evidence."""

import json
import subprocess
from pathlib import Path

ROOT = Path("/opt/rnd")
profile = json.loads((ROOT / "profile.json").read_text())
product = ROOT / "prewarm/product"


def run(argv, cwd):
    subprocess.run(argv, cwd=cwd, check=True, timeout=1800)


if profile["template"] == "python-basic":
    run(["uv", "sync", "--locked", "--no-dev", "--extra", "postgres", "--python", "3.14.7"], product)
else:
    import sys
    sys.path.insert(0, str(product / "deployment"))
    from workbench.native_environment import install_backend, native_environment
    from workbench.native_frontend import build_frontend, frontend_environment
    template = profile["template"]
    backend = product / "backend"
    frontend = product / ("frontend/web" if template == "fastapiadmin" else "frontend-product")
    native_environment(template, backend, "postgresql+psycopg://warm:unused@127.0.0.1:5432/warm_codegen", 8001 if template == "fastapiadmin" else 48080)
    run(["uv", "sync", "--locked", "--python", "3.14.7"], product / "deployment")
    install_backend(template, backend, ROOT / "warm-reports")
    build_frontend(template, frontend, frontend_environment(template, "http://127.0.0.1:48080" if template == "yudao-vben" else "http://127.0.0.1:8001"), ROOT / "warm-reports", prepared=True)
print("Locked native dependencies prepared; no runtime result asserted.")
