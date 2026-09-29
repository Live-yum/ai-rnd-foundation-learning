"""Per-run Docker services, created only after an operator chooses/approves a native stack."""

import json
import secrets
import socket

from workbench.filesystem import write_json
from workbench.settings import ROOT
from workbench.tools import run_command


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def for_run(settings, run_id):
    folder = settings.data_dir / "native-services" / run_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "services.json"
    if not path.exists():
        write_json(
            path,
            {
                "password": secrets.token_urlsafe(32),
                "project": "rnd" + secrets.token_hex(8),
                "pg_port": free_port(),
                "redis_port": free_port(),
            },
        )
        path.chmod(0o600)
    data = json.loads(path.read_text(encoding="utf-8"))
    env = folder / "services.env"
    env.write_text(
        f"POSTGRES_PASSWORD={data['password']}\nPG_PORT={data['pg_port']}\nREDIS_PORT={data['redis_port']}\nCOMPOSE_PROJECT_NAME={data['project']}\n",
        encoding="utf-8",
    )
    env.chmod(0o600)
    run_command(
        [
            "docker",
            "compose",
            "--env-file",
            str(env),
            "-f",
            str(ROOT / "templates/deployment/services.yaml"),
            "up",
            "-d",
            "--wait",
        ],
        folder,
        300,
    )
    return (
        f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_codegen",
        data["redis_port"],
    )
