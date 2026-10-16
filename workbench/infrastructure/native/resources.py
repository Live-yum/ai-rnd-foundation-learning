"""Per-run Docker services, created only after an operator chooses/approves a native stack."""

import json
import secrets
import shutil
import socket

from workbench.filesystem import write_json
from workbench.infrastructure.processes.tools import ToolFailure, run_command
from workbench.settings import ROOT


class NativeServiceUnavailable(ToolFailure):
    """A known local service availability failure, never an authorization failure."""


def start_services(command, folder):
    try:
        return run_command(command, folder, 300)
    except ToolFailure as exc:
        # Docker often reports socket authorization errors after a successful spawn.
        # Its CLI has no structured error protocol: classify only known availability
        # diagnostics and fail closed for unknown/localized failures.
        diagnostic = getattr(exc, "log", "").casefold()
        if any(
            marker in diagnostic
            for marker in (
                "permission denied",
                "access is denied",
                "access denied",
                "operation not permitted",
                "unauthorized",
                "forbidden",
                "authentication required",
            )
        ):
            raise PermissionError(
                "Docker service access denied; source fallback is prohibited"
            ) from exc
        # Missing Compose is an executable-capability failure, not a daemon or
        # authorization failure. Match only the Docker CLI's explicit missing
        # subcommand diagnostics; unrelated unknown flags/commands fail closed.
        missing_compose = {
            "'compose' is not a docker command.",
            '"compose" is not a docker command.',
            'unknown command "compose" for "docker"',
        }
        if (
            len(command) >= 2
            and command[0] == "docker"
            and command[1] == "compose"
            and any(
                line.strip().removeprefix("docker: ") in missing_compose
                for line in diagnostic.splitlines()
            )
        ):
            raise NativeServiceUnavailable("Local Docker Compose plugin is unavailable") from exc
        if (
            "cannot connect to the docker daemon" in diagnostic
            or "is the docker daemon running?" in diagnostic
        ):
            raise NativeServiceUnavailable("Local Docker daemon is unavailable") from exc
        raise


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def for_run(settings, run_id):
    if not shutil.which("docker"):
        raise NativeServiceUnavailable("Local Docker executable is unavailable")
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
    start_services(
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
    )
    return (
        f"postgresql+psycopg://native:{data['password']}@127.0.0.1:{data['pg_port']}/product_codegen",
        data["redis_port"],
    )
