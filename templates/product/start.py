"""One local command after unzip. Creates only its own database volume; never resets data.

python start.py                  # install locked dependencies, init/migrate and serve
python start.py --init-only      # install and apply migrations, do not serve
python start.py --no-install     # use current Python (CI / preinstalled environment)
"""

import argparse
import json
import os
import secrets
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--init-only", action="store_true")
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()
    selection = json.loads((ROOT / "selection.json").read_text(encoding="utf-8"))
    env = os.environ.copy()
    python = sys.executable
    if not args.no_install:
        uv = shutil.which("uv")
        if not uv:
            raise SystemExit("Install uv first; see README.md")
        cmd = [uv, "sync", "--locked", "--no-dev"]
        if selection["database"] == "postgresql":
            cmd += ["--extra", "postgres"]
        subprocess.run(cmd, cwd=ROOT, check=True)
        python = str(ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
    if selection["database"] == "postgresql" and not env.get("PRODUCT_DATABASE_URL"):
        docker = shutil.which("docker")
        if not docker:
            raise SystemExit(
                "Selected PostgreSQL: start Docker Desktop, or supply PRODUCT_DATABASE_URL for your local database"
            )
        data = ROOT / ".data"
        data.mkdir(exist_ok=True)
        config = data / "deployment.json"
        if not config.exists():
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            value = {
                "password": secrets.token_urlsafe(32),
                "port": port,
                "project": "rnd" + secrets.token_hex(6),
            }
            with config.open("x", encoding="utf-8") as file:
                json.dump(value, file)
            config.chmod(0o600)
        value = json.loads(config.read_text(encoding="utf-8"))
        deployment = data / "deployment.env"
        deployment.write_text(
            f"POSTGRES_PASSWORD={value['password']}\nPG_PORT={value['port']}\nCOMPOSE_PROJECT_NAME={value['project']}\n",
            encoding="utf-8",
        )
        deployment.chmod(0o600)
        subprocess.run(
            [docker, "compose", "--env-file", str(deployment), "up", "-d", "--wait", "database"],
            cwd=ROOT,
            check=True,
        )
        env["PRODUCT_DATABASE_URL"] = (
            f"postgresql+psycopg://product:{value['password']}@127.0.0.1:{value['port']}/product"
        )
    action = "init" if args.init_only else "start"
    print("Applying versioned migrations; existing data is preserved.", flush=True)
    subprocess.run(
        [python, "manage.py", action, "--port", str(args.port)], cwd=ROOT, env=env, check=True
    )


if __name__ == "__main__":
    main()
