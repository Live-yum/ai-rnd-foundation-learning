"""Independent runtime checks, reproducible packaging, and clean-room verification."""

import ast
import json
import os
import shutil
import sys
import tempfile
import zipfile
from contextlib import nullcontext
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import files, manifest, sha, unpack, write_json
from workbench.generator import PrerequisiteError
from workbench.rules import Rules, UnsafeRule
from workbench.settings import ROOT
from workbench.tools import ToolFailure, run_command


def product_interpreter(product, settings):
    if not settings.install_products:
        return sys.executable
    uv = shutil.which("uv")
    if not uv:
        raise PrerequisiteError("独立产品验收需要 uv，当前 PATH 中未找到")
    selected = json.loads((Path(product) / "selection.json").read_text())["database"]
    extras = ["--extra", "postgres"] if selected == "postgresql" else []
    try:
        run_command(
            [uv, "sync", "--locked", "--no-dev", *extras, "--project", str(product)],
            product,
            timeout=settings.tool_timeout,
            extra_env={"UV_PYTHON": sys.executable},
        )
    except ToolFailure as exc:
        raise PrerequisiteError("产品依赖安装失败；这是环境故障，不自动修改业务代码") from exc
    return str(product / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))


def run_probe(product, python, report_path, settings):
    from workbench.postgres_lab import database

    selection = json.loads((Path(product) / "selection.json").read_text(encoding="utf-8"))
    scope = database(settings) if selection["database"] == "postgresql" else nullcontext(None)
    with scope as url:
        return run_command(
            [
                sys.executable,
                str(ROOT / "templates/product/verify.py"),
                "--product",
                str(product),
                "--python",
                python,
                "--report",
                str(report_path),
            ],
            ROOT,
            timeout=settings.tool_timeout,
            extra_env={
                **({"VERIFY_DATABASE_URL": url} if url else {}),
                "PRODUCT_VERIFY_PLAYWRIGHT": os.environ.get(
                    "PRODUCT_VERIFY_PLAYWRIGHT",
                    str(ROOT / ".native/browser/node_modules/playwright"),
                ),
                "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
            },
        )


def require_browser_evidence(product, report):
    selection = json.loads((Path(product) / "selection.json").read_text(encoding="utf-8"))
    spec = json.loads((Path(product) / "approved-spec.json").read_text(encoding="utf-8"))
    if spec.get("business"):
        require_business_evidence(spec, report, selection["frontend"] == "simple-admin")
        return
    if selection["frontend"] != "simple-admin":
        return
    browser = report.get("browser")
    if (
        not isinstance(browser, dict)
        or any(browser.get(key) is not True for key in ("passed", "real_browser", "applicable"))
        or browser.get("entities") != [entity["name"] for entity in spec["entities"]]
    ):
        raise PrerequisiteError("simple-admin 缺少逐产品真实浏览器验收，不能交付")
    required = {"browser-registration", "browser-login-invalid-password-logout-reload"}
    for entity in spec["entities"]:
        name = entity["name"]
        required.update(
            f"{check}:{name}"
            for check in (
                "browser-create",
                "browser-field-lengths",
                "browser-combined-filter",
                "browser-user-isolation",
                "browser-update-delete",
            )
        )
        for field in entity["fields"]:
            for flag, check in (
                ("searchable", "browser-search"),
                ("filterable", "browser-filter"),
                ("date_range", "browser-inclusive-date"),
            ):
                if field.get(flag):
                    required.add(f"{check}:{name}.{field['name']}")
            if field["kind"] == "text":
                required.add(f"browser-overlength-rejected:{name}.{field['name']}")
    if not required.issubset(set(browser.get("checks", []))) or browser.get("errors") != []:
        raise PrerequisiteError("真实浏览器验收覆盖不完整或存在页面错误")


def require_business_evidence(spec, report, with_browser):
    business = report.get("business")
    required = {
        "business-bootstrap",
        "business-role-default",
        "business-row-permissions",
        "business-protected-fields",
        "business-relations",
        "business-transitions",
        "business-notes-history",
        "business-notifications",
        "business-scoped-metrics",
        "business-archive",
    }
    if (
        not isinstance(business, dict)
        or business.get("passed") is not True
        or business.get("spec_digest") != digest(spec)
        or business.get("resources_checked") != [e["name"] for e in spec["entities"]]
        or business.get("roles_checked") != [r["name"] for r in spec["business"]["roles"]]
        or not required.issubset(set(business.get("checks", [])))
    ):
        raise PrerequisiteError("业务关系、流程、角色权限与统计验收证据缺失，不能交付")
    if not with_browser:
        return
    browser = report.get("browser")
    checks = {
        "business-browser-auth",
        "business-browser-role-navigation",
        "business-browser-assignment",
        "business-browser-transitions",
        "business-browser-notes-history",
        "business-browser-reminders",
        "business-browser-metrics",
        "business-browser-role-restrictions",
        *["business-browser-records:" + e["name"] for e in spec["entities"]],
    }
    if (
        not isinstance(browser, dict)
        or any(browser.get(key) is not True for key in ("passed", "real_browser", "applicable"))
        or browser.get("spec_digest") != digest(spec)
        or browser.get("entities") != [e["name"] for e in spec["entities"]]
        or browser.get("errors") != []
        or not checks.issubset(set(browser.get("checks", [])))
    ):
        raise PrerequisiteError("业务页面的逐角色真实浏览器验收不完整")


def validate_rule_examples(plan, product):
    rules = Rules((product / "custom_rules.py").read_text(encoding="utf-8"))
    for rule in plan.custom_rules:
        for sample in rule.accept_examples:
            rules.validate(rule.entity, sample)
        for sample in rule.reject_examples:
            try:
                rules.validate(rule.entity, sample)
            except ValueError:
                continue
            raise ValueError("业务规则没有拒绝已经批准的反例")


def verify_basic(plan, product, settings, attempt=0):
    product = Path(product)
    receipt = json.loads((product.parent / "generation.json").read_text(encoding="utf-8"))
    current = manifest(product)
    original = receipt["files"]
    if set(current) != set(original) or any(
        current[k] != v for k, v in original.items() if k != "custom_rules.py"
    ):
        raise PrerequisiteError("可信模板文件被修改；禁止通过修改测试或启动器绕过验收")
    if receipt["spec_digest"] != digest(plan.model_dump()):
        raise PrerequisiteError("生成依据与已批准设计不一致")
    try:
        for name, path in files(product):
            if name.endswith(".py"):
                ast.parse(path.read_text(encoding="utf-8"), filename=name)
        validate_rule_examples(plan, product)
    except (SyntaxError, ValueError, UnsafeRule) as exc:
        return {
            "passed": False,
            "kind": "code",
            "error": str(exc)[:500],
            "attempt": attempt,
        }
    python = product_interpreter(product, settings)
    report_path = product.parent / f"runtime-{attempt}.json"
    try:
        execution = run_probe(product, python, report_path, settings)
    except ToolFailure as exc:
        if not report_path.exists():
            raise PrerequisiteError("运行验收未产生报告；检查本机工具环境与超时配置") from exc
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("kind") == "environment":
            raise PrerequisiteError(report.get("message", "浏览器验收环境不可用")) from exc
        if report.get("passed") is True:
            raise PrerequisiteError("验证进程失败但报告声称成功；拒绝使用该报告") from exc
        return {
            "passed": False,
            "kind": "code",
            "error": report.get("message", "运行验收失败"),
            "attempt": attempt,
            "source_digest": digest(current),
        }
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if manifest(product) != current:
        raise PrerequisiteError("验收期间源码发生变化")
    if report.get("passed") is not True or not report.get("restart") or not report.get("http"):
        raise PrerequisiteError("运行验收证据不完整")
    require_browser_evidence(product, report)
    report.update(
        source_digest=digest(current),
        spec_digest=digest(plan.model_dump()),
        isolated_dependencies=settings.install_products,
        attempt=attempt,
        exit_code=execution["returncode"],
    )
    write_json(product.parent / "verification.json", report)
    return report


def package_basic(plan, product, settings, report):
    product = Path(product)
    listing = manifest(product)
    if report.get("passed") is not True or report.get("source_digest") != digest(listing):
        raise PrerequisiteError("源码在测试后发生变化，必须重新验证")
    require_browser_evidence(product, report)
    archive = product.parent / "delivery.zip"
    temporary = archive.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, path in files(product):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, path.read_bytes())
        with tempfile.TemporaryDirectory(prefix="rnd-cleanroom-") as directory:
            clean = Path(directory) / "product"
            unpack(temporary, clean)
            if manifest(clean) != listing:
                raise PrerequisiteError("ZIP 内文件与通过验收的源码不一致")
            python = product_interpreter(clean, settings)
            clean_report = Path(directory) / "cleanroom.json"
            run_probe(clean, python, clean_report, settings)
            evidence = json.loads(clean_report.read_text(encoding="utf-8"))
            if manifest(clean) != listing:
                raise PrerequisiteError("干净验收期间源码发生变化")
            require_browser_evidence(clean, evidence)
            if evidence.get("passed") is not True:
                raise PrerequisiteError("干净解压验收失败")
        os.replace(temporary, archive)
    finally:
        temporary.unlink(missing_ok=True)
    result = {
        "package": "delivery.zip",
        "sha256": sha(archive),
        "files": listing,
        "spec_digest": digest(plan.model_dump()),
        "cleanroom": evidence,
        "isolated_dependencies": settings.install_products,
        "validation_level": "runtime",
        "production_ready": False,
    }
    write_json(product.parent / "delivery.json", result)
    return result
