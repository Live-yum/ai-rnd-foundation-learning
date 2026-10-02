# workbench/business_browser.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：用临时场景连接真实原生浏览器验收。** 只把本次合成账号交给临时场景文件，启动对应浏览器脚本并要求passed及零错误；临时凭据不进入上传报告。

**对应关系：** native_lab/portable → 模板专用CJS脚本 → business-browser.json与截图。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run_business_browser`（L13–L66）：接收`template`、`script`、`front_url`、`reports`、`scenario`、`plan`、`playwright`。 控制顺序：L59抛异常，停止当前正常路径。 调用`Path`、`scenario["browser_actors"].items`、`tempfile.TemporaryDirectory`、`write_json`、`next`、`plan.model_dump`、`run_command`、`str`、`reports.resolve`等。 返回路径：L66的`report`。
- `query_journey_evidence`（L69–L94）：接收`report`。 源码说明：A marker alone cannot prove native widgets serialized a discriminating query.。 控制顺序：L85按`not isinstance(value, dict) or set(value) != set(expected) or any( type(value[key]) i…`分支；L93抛异常，停止当前正常路径。 调用`report.get`、`isinstance`、`set`、`any`、`type`、`expected.items`、`ValueError`、`dict`。 返回路径：L94的`dict(expected)`。
- `require_business_browser`（L97–L170）：接收`report`、`plan`、`template`。 控制顺序：L98按`report.get("passed") is not True or report.get("errors") != [] or report.get("templat…`分支；L103抛异常，停止当前正常路径；L112按`not {role + ":" + login for role in ("manager", "service", "employee")} <= set( repor…`分支；L115抛异常，停止当前正常路径；L116按`fastapi`分支；L146按`not journeys <= set(report.get("checks", []))`分支；L147抛异常，停止当前正常路径；L149按`template == "yudao-vben"`分支。后续分支沿下方源码相同行号继续阅读。 调用`report.get`、`ValueError`、`set`、`journeys.add`、`query_journey_evidence`、`validate_sidebar`、`page.get`、`any`、`all`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/business_browser.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L170。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6673`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/business_browser.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "68a3181d1d4da771b1653bfd9962bb9136b533e7248df63dba0a47b04e968f18"} -->
````python
# workbench/business_browser.py
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


def query_journey_evidence(report):
    """A marker alone cannot prove native widgets serialized a discriminating query."""
    expected = {
        "entity": "customers",
        "keyword_field": "name",
        "filter_field": "category",
        "cases": 3,
        "keyword": True,
        "combined_positive": True,
        "combined_mismatch": True,
        "request_values_verified": True,
        "response_ids_exact": True,
        "rendered_ids_exact": True,
        "controls_reset": True,
    }
    value = report.get("query_journey")
    if (
        not isinstance(value, dict)
        or set(value) != set(expected)
        or any(
            type(value[key]) is not type(item) or value[key] != item
            for key, item in expected.items()
        )
    ):
        raise ValueError("Native browser query journey is missing or incomplete")
    return dict(expected)


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
            "employee:own_record_history_acl_and_read_reminder",
            "other_employee:row_isolation",
            "other_service:row_isolation",
            "manager:all_declared_native_metric_cards",
        }
    else:
        journeys = {
            "manager:customers:native-form-create",
            "manager:requests:native-form-create",
            "employee:requests:native-form-create",
            "manager:tasks:native-form-create",
            "native-business-action:assign:",
            "native-business-action:transition:start",
            "native-business-action:transition:resolve",
            "native-business-action:add_note:",
            "manager:customers:requests:related-record-and-history",
            "manager:requests:tasks:related-record-and-history",
            "manager:real-native-echarts-metrics",
            "employee:own_record_history_acl_and_read_reminder",
            "other_employee:row_isolation",
            "other_service:row_isolation",
        }
    journeys.add("manager:customers:native-query-and-exact-filter")
    if not journeys <= set(report.get("checks", [])):
        raise ValueError("Native business browser omitted required workflow or isolation checks")
    query_journey_evidence(report)
    if template == "yudao-vben":
        from workbench.yudao_navigation_checks import validate_sidebar

        validate_sidebar(report.get("installed_navigation"), plan)
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
````
