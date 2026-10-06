"""One local command after unzip. Creates only its own database volume; never resets data.

python start.py                  # install locked dependencies, init/migrate and serve
python start.py --init-only      # install and apply migrations, do not serve
python start.py --no-install     # use current Python (CI / preinstalled environment)
"""

import argparse
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
CONSUMER_FILE = "RND-CONSUMER.json"


def consumer_contract(selection):
    """Read controller-authored data, never a product-supplied executable command."""
    path = ROOT / CONSUMER_FILE
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 4096:
        raise SystemExit("Invalid consumer runtime contract")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        raise SystemExit("Invalid consumer runtime contract") from None
    fields = {
        "schema",
        "profile",
        "entrypoint",
        "port",
        "database_path",
        "runtime_sha256",
        "database_environment",
        "initialization",
        "existing_schema_migration",
    }
    if (
        type(value) is not dict
        or set(value) != fields
        or type(value.get("schema")) is not int
        or value["schema"] != 1
        or value.get("profile") != "python-basic-sqlite-asgi-v1"
        or selection.get("template") != "python-basic"
        or selection.get("database") != "sqlite"
        or selection.get("backend") != "fastapi"
        or type(value.get("entrypoint")) is not str
        or re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*",
            value["entrypoint"],
        )
        is None
        or type(value.get("port")) is not int
        or not 1024 <= value["port"] <= 65535
        or value["port"] in {2280, 55432, 55433}
        or type(value.get("runtime_sha256")) is not str
        or re.fullmatch(r"[a-f0-9]{64}", value["runtime_sha256"]) is None
        or value.get("database_environment") != ["PRODUCT_DATABASE_URL", "DATABASE_URL"]
        or value.get("initialization") != "application-startup"
        or value.get("existing_schema_migration") != "unverified"
        or type(value.get("database_path")) is not str
    ):
        raise SystemExit("Invalid consumer runtime contract")
    name = value["database_path"]
    database = PurePosixPath(name)
    if (
        not name
        or str(database) != name
        or database.is_absolute()
        or database.parent.as_posix() == "."
        or any(part.startswith(".") or part in {"node_modules"} for part in database.parts)
        or "\\" in name
        or ":" in name
        or "?" in name
        or "#" in name
        or any(ord(char) < 32 for char in name)
        or database.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}
    ):
        raise SystemExit("Invalid consumer database path")
    return value


def consumer_environment(contract, env):
    """The canonical product URL and legacy alias always identify the same DB."""
    from urllib.parse import urlsplit

    default = ROOT.joinpath(*PurePosixPath(contract["database_path"]).parts)
    url = env.get("PRODUCT_DATABASE_URL") or "sqlite:///" + default.as_posix()
    # The current certified custom profile is a local persistent SQLite file.
    # Do not accidentally open an ambient platform DATABASE_URL or URI driver.
    parsed = urlsplit(url)
    database = url.removeprefix("sqlite:///")
    if (
        not url.startswith("sqlite:///")
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or not database
        or database == ":memory:"
        or database.startswith(("//", "\\\\", "file:"))
        or any(ord(char) < 32 for char in database)
    ):
        raise SystemExit("PRODUCT_DATABASE_URL must identify a local persistent SQLite file")
    # Resolve relative input against the ZIP root, regardless of caller cwd.
    path = Path(database)
    path = path if path.is_absolute() else ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    url = "sqlite:///" + path.resolve().as_posix()
    return {**env, "PRODUCT_DATABASE_URL": url, "DATABASE_URL": url}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int)
    parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"], default="127.0.0.1")
    parser.add_argument("--init-only", action="store_true")
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()
    selection = json.loads((ROOT / "selection.json").read_text(encoding="utf-8"))
    contract = consumer_contract(selection)
    port = args.port if args.port is not None else contract["port"] if contract else 8001
    if not 1024 <= port <= 65535 or port in {2280, 55432, 55433}:
        parser.error("port must be an unreserved value between 1024 and 65535")
    if contract and args.init_only:
        raise SystemExit(
            "This custom product initializes during application startup; --init-only is not "
            "supported. Existing-schema upgrades require a separately verified migration."
        )
    if not contract and args.host != "127.0.0.1":
        parser.error("the standard product listens only on 127.0.0.1")
    env = os.environ.copy()
    if contract:
        env = consumer_environment(contract, env)
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
                database_port = sock.getsockname()[1]
            value = {
                "password": secrets.token_urlsafe(32),
                "port": database_port,
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
            [
                docker,
                "--host",
                "npipe:////./pipe/docker_engine"
                if os.name == "nt"
                else "unix:///var/run/docker.sock",
                "compose",
                "--env-file",
                str(deployment),
                "up",
                "-d",
                "--wait",
                "database",
            ],
            cwd=ROOT,
            check=True,
        )
        env["PRODUCT_DATABASE_URL"] = (
            f"postgresql+psycopg://product:{value['password']}@127.0.0.1:{value['port']}/product"
        )
    if contract:
        print(
            "Starting the approved custom application; initialization is application-owned. "
            "Existing-schema migrations are not verified.",
            flush=True,
        )
        # This executes in the consumer's process (or guarded application UID
        # during verification), never in the platform controller process.
        command = [
            python,
            "-m",
            "uvicorn",
            contract["entrypoint"],
            "--host",
            args.host,
            "--port",
            str(port),
        ]
        if os.name == "nt":
            # Windows has no same-PID exec. Retain the parent so supervision
            # and taskkill /T can still own the application's process tree.
            subprocess.run(command, cwd=ROOT, env=env, check=True)
            return
        os.chdir(ROOT)
        os.execve(python, command, env)
    action = "init" if args.init_only else "start"
    print("Applying versioned migrations; existing data is preserved.", flush=True)
    subprocess.run(
        [python, "manage.py", action, "--port", str(port)], cwd=ROOT, env=env, check=True
    )


if __name__ == "__main__":
    main()
