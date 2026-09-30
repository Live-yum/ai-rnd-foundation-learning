"""Install reviewed native business adapters and explicit transaction-scoped schema."""

from pathlib import Path

import psycopg

from workbench.domain import Plan
from workbench.filesystem import sha, write_json
from workbench.native_environment import checked_database


def install_native_business(template, plan, backend, frontend, targets, reports, url):
    plan = Plan.model_validate(plan)
    if plan.business is None:
        return None
    reports = Path(reports)
    if template == "fastapiadmin":
        from workbench.business_fastapi import extend_business

        receipt = extend_business(plan, backend, frontend, targets, reports, database_url=url)
    elif template == "yudao-vben":
        from workbench.business_yudao import install_yudao_business

        receipt = install_yudao_business(plan, backend, frontend, targets, reports)
    else:
        raise ValueError("Unknown native business adapter")
    database = (
        checked_database(url).set(drivername="postgresql").render_as_string(hide_password=False)
    )
    scripts = [reports / "business-extension-schema.sql"]
    roles = reports / "business-role-seed.sql"
    if roles.is_file():
        scripts.append(roles)
    if not scripts[0].is_file():
        raise ValueError("Business adapter must emit explicit schema before runtime acceptance")
    # These files are deterministic adapter output, never model-supplied SQL. Any
    # failure rolls back the entire extension; the outer recovery guard preserves
    # source/data and does not claim an incomplete bootstrap can safely resume.
    with psycopg.connect(database) as connection:
        for script in scripts:
            connection.execute(script.read_text(encoding="utf-8"))
    evidence = {
        "template": template,
        "adapter": receipt,
        "schema_applied": True,
        "schema_files": {script.name: sha(script) for script in scripts},
        "runtime_verified": False,
    }
    write_json(reports / "business-installation.json", evidence)
    return evidence
