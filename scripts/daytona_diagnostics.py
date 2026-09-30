"""Bounded, secret-redacted diagnostics from this local test deployment only."""

import json

from scripts.daytona_local import HOME, PROJECT, docker
from workbench.filesystem import atomic_text
from workbench.settings import ROOT


def main():
    secrets = []
    for name in ["credentials.json", "api-key.json"]:
        path = HOME / name
        if path.is_file():
            secrets.extend(v for v in json.loads(path.read_text()).values() if isinstance(v, str) and len(v) > 5)
    logs = []
    for args in [["ps", "--all"], ["logs", "--no-color", "--tail", "80"]]:
        if (HOME / "compose.lock.yaml").is_file():
            try:
                logs.append(docker("compose", "-p", PROJECT, "-f", str(HOME / "compose.lock.yaml"), *args, timeout=60)[-80000:])
            except Exception as exc:
                logs.append(type(exc).__name__)
    body = "\n".join(logs)
    for secret in sorted(secrets, key=len, reverse=True):
        body = body.replace(secret, "[REDACTED]")
    atomic_text(ROOT / "reports/daytona-matrix-diagnostics.log", body)
    image = HOME / "snapshot-image.json"
    if image.is_file():
        atomic_text(ROOT / "reports/daytona-matrix-image.json", image.read_text())


if __name__ == "__main__":
    main()
