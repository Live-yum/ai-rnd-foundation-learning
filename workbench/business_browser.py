"""Run native three-role UI acceptance with temporary synthetic credentials only."""

import json
import os
import tempfile
from pathlib import Path

from workbench.filesystem import atomic_text, write_json
from workbench.tools import run_command


def run_business_browser(template, script, front_url, reports, scenario, plan, playwright):
    reports = Path(reports)
    actors = {
        name: {**actor, "password": "BusinessTest123!"}
        for name, actor in scenario["browser_actors"].items()
    }
    actors["manager"] = {
        "username": "super" if template == "fastapiadmin" else "admin",
        "password": "123456" if template == "fastapiadmin" else "admin123",
    }
    with tempfile.TemporaryDirectory(prefix="rnd-owned-business-browser-") as tmp:
        fixture = Path(tmp) / "scenario.json"
        write_json(
            fixture,
            {
                "actors": actors,
                "records": scenario["records"],
                "attempt": scenario["attempt"],
                "targets": scenario["targets"],
                "route": scenario["targets"][0]["route"],
                "plan": plan.model_dump(),
            },
        )
        try:
            result = run_command(
                [
                    "node",
                    str(script),
                    front_url,
                    str(reports.resolve()),
                    str(playwright),
                    str(fixture),
                ],
                Path(script).parent,
                480,
                {
                    "PLAYWRIGHT_BROWSERS_PATH": os.getenv("PLAYWRIGHT_BROWSERS_PATH", "0"),
                    "NODE_OPTIONS": "--dns-result-order=ipv4first",
                },
            )
        except Exception as exc:
            atomic_text(reports / "business-browser.log", getattr(exc, "log", type(exc).__name__))
            raise
    atomic_text(reports / "business-browser.log", result["log"])
    report_path = reports / "business-browser.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("passed") is not True or report.get("errors") != []:
        raise ValueError("Native business browser did not pass all three-role UI checks")
    return report
