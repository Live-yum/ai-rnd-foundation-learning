"""Native baseline acceptance against empty test databases, not generated-module acceptance."""

import argparse
import os
from pathlib import Path

from workbench.filesystem import atomic_text, write_json
from workbench.native_checks import check_native_permissions
from workbench.native_environment import (
    bootstrap_database,
    copy_source,
    install_backend,
    login,
    native_environment,
    running_backend,
)
from workbench.native_frontend import (
    browser_check,
    build_frontend,
    frontend_environment,
    frontend_preview,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("template", choices=["fastapiadmin", "yudao-vben"])
    parser.add_argument("--source", type=Path, default=Path(".native/source"))
    parser.add_argument("--output", type=Path, default=Path(".native/product"))
    parser.add_argument("--frontend-source", type=Path, default=Path(".native/frontend"))
    parser.add_argument("--frontend", action="store_true")
    args = parser.parse_args()
    reports = Path("reports/native").resolve()
    reports.mkdir(parents=True, exist_ok=True)
    url = os.environ["NATIVE_TEST_DATABASE_URL"]
    copy_source(args.source, args.output)
    backend = args.output / "backend" if args.template == "fastapiadmin" else args.output
    env = native_environment(
        args.template, backend, url, 8001 if args.template == "fastapiadmin" else 48080
    )
    try:
        bootstrap_database(args.template, backend, url)
        install_backend(args.template, backend, reports)
        with running_backend(args.template, backend, env, reports) as (base_url, _):
            token = login(args.template, base_url)
            if not isinstance(token, str) or len(token) < 10:
                raise AssertionError("Native login did not return an access token")
            write_json(
                reports / "baseline.json",
                {
                    "template": args.template,
                    "database": "postgresql",
                    "native_login": True,
                    "server_started": True,
                    "generated_runtime_verified": False,
                },
            )
            permissions = check_native_permissions(args.template, base_url, token)
            write_json(reports / "permissions.json", permissions)
            print("Original native backend: login and role permissions PASS")
            if args.frontend:
                if args.template == "fastapiadmin":
                    frontend = args.output / "frontend/web"
                else:
                    frontend = args.output.parent / "frontend-product"
                    copy_source(args.frontend_source, frontend)
                front_env = frontend_environment(args.template, base_url)
                build_frontend(args.template, frontend, front_env, reports)
                with frontend_preview(args.template, frontend, front_env, reports) as front_url:
                    browser_check(args.template, front_url, reports)
            write_json(
                reports / "acceptance.json",
                {
                    "template": args.template,
                    "scope": "original-native-baseline",
                    "backend_login": True,
                    "native_permissions": True,
                    "frontend_browser": args.frontend,
                    "generated_runtime_verified": False,
                },
            )
    except Exception as exc:
        atomic_text(
            reports / "failure.log",
            type(exc).__name__ + ": " + str(exc) + "\n" + getattr(exc, "log", ""),
        )
        raise


if __name__ == "__main__":
    main()
