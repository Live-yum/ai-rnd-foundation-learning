"""Reproducible native integration entry point; consumes only dedicated empty test databases."""

import argparse
import os
from pathlib import Path

from workbench.filesystem import atomic_text, write_json
from workbench.native_environment import (
    bootstrap_database,
    copy_source,
    install_backend,
    login,
    native_environment,
    running_backend,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--source", type=Path, default=Path(".native/source"))
    parser.add_argument("--output", type=Path, default=Path(".native/product"))
    args = parser.parse_args()
    reports = Path("reports/native").resolve()
    reports.mkdir(parents=True, exist_ok=True)
    url = os.environ["NATIVE_TEST_DATABASE_URL"]
    copy_source(args.source, args.output)
    backend = args.output / "backend" if args.template == "fastapiadmin" else args.output
    env = native_environment(args.template, backend, url, 8001 if args.template == "fastapiadmin" else 48080)
    # The pinned upstream supports dev/prod only. Use prod so startup cannot autogenerate/drop tables.
    if args.template == "fastapiadmin":
        env["ENVIRONMENT"] = "prod"
    try:
        bootstrap_database(args.template, backend, url)
        install_backend(args.template, backend, reports)
        with running_backend(args.template, backend, env, reports) as (base_url, openapi):
            token = login(args.template, base_url)
            assert isinstance(token, str) and len(token) > 10
            write_json(reports / "baseline.json", {
                "template": args.template, "database": "postgresql", "native_login": True,
                "server_started": True, "generated_runtime_verified": False,
            })
            print("Native baseline login PASS; generated runtime is not yet claimed")
    except Exception as exc:
        atomic_text(reports / "failure.log", type(exc).__name__ + ": " + str(exc) + "\n" + getattr(exc, "log", ""))
        raise


if __name__ == "__main__":
    main()
