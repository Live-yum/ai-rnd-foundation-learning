"""Run native three-role UI acceptance with temporary synthetic credentials only."""

import json
import os
import tempfile
from pathlib import Path

from workbench.domain import digest
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
                "route": next(
                    target["route"]
                    for target in scenario["targets"]
                    if target["entity"] == "customers"
                ),
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
    require_business_browser(report, plan, template)
    report["spec_digest"] = digest(plan.model_dump())
    write_json(report_path, report)
    return report


def require_business_browser(report, plan, template):
    if (
        report.get("passed") is not True
        or report.get("errors") != []
        or report.get("template") != template
    ):
        raise ValueError("Native business browser did not pass all three-role UI checks")
    fastapi = template == "fastapiadmin"
    family = "Fa/Element Plus" if fastapi else "Vben/Ant Design/VXE"
    tokens = (
        {"--el-color-primary", "--el-font-size-base"}
        if fastapi
        else {"--primary", "--background", "--font-family"}
    )
    login = "real_native_login_menu_shell" if fastapi else "native-login-and-tenant"
    if not {role + ":" + login for role in ("manager", "service", "employee")} <= set(
        report.get("checks", [])
    ):
        raise ValueError("Native business browser omitted a real role login")
    if fastapi:
        journeys = {
            "manager:customer_native_form_create",
            "manager:changed_value_edit",
            "employee:related_request_native_form_create",
            "manager:linked_task_and_native_assignment",
            "service:assigned_workflows_notes_timestamps",
            "employee:own_timeline_and_read_reminder",
            "other_employee:row_isolation",
            "other_service:row_isolation",
            "manager:five_native_metric_cards",
        }
    else:
        journeys = {
            "manager:customers:native-form-create",
            "manager:requests:native-form-create",
            "manager:tasks:native-form-create",
            "native-business-action:assign:",
            "native-business-action:transition:start",
            "native-business-action:transition:resolve",
            "native-business-action:add_note:",
            "manager:customers:requests:related-record-and-history",
            "manager:requests:tasks:related-record-and-history",
            "manager:real-native-echarts-metrics",
            "employee:own_timeline_and_read_reminder",
            "other_employee:row_isolation",
            "other_service:row_isolation",
        }
    if not journeys <= set(report.get("checks", [])):
        raise ValueError("Native business browser omitted required workflow or isolation checks")
    for entity in plan.entities:
        proofs = [page for page in report.get("pages", []) if page.get("entity") == entity.name]
        if not any(
            page.get("native_shell_visible") is True
            and page.get("native_form_components_visible") is True
            and page.get("real_list_request") is True
            and page.get("native_component_family") == family
            and all(
                isinstance(page.get("native_theme_tokens", {}).get(token), str)
                and page["native_theme_tokens"][token].strip()
                for token in tokens
            )
            for page in proofs
        ):
            raise ValueError(
                "Native business page lacks original shell, form and real list proof: "
                + entity.name
            )
