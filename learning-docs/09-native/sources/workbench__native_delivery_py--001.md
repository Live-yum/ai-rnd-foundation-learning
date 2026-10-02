# workbench/native_delivery.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生生成、完整验收和打包的流程接口。** managed_generate协调本机源码、专用数据库和生成器；managed_verify核对数据库身份及完整回执，managed_package只有在验收成功时打包。serve_managed用于本机查看生成结果，不是公网部署。

**对应关系：** flow → managed_generate/verify/package → native_lab/portable；test_native_managed。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.native_environment`、`workbench.native_evidence`、`workbench.native_frontend`、`workbench.native_lab`、`workbench.native_modules`、`workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `RuntimeConfig`（L26–L29）：继承`BaseModel`。声明的数据项为`database_url_env`、`initialize_empty_database`；类型约束/数据库列参数以完整定义为准。
- `runtime_path`（L32–L35）：接收`settings`、`template`。 控制顺序：L33按`template not in {"fastapiadmin", "yudao-vben"}`分支；L34抛异常，停止当前正常路径。 调用`ValueError`。 返回路径：L35的`settings.data_dir / "native" / f"{template}.runtime.json"`。
- `runtime_enabled`（L38–L39）：接收`settings`、`template`。 调用`runtime_path(settings, template).is_file`、`runtime_path`。 返回路径：L39的`runtime_path(settings, template).is_file()`。
- `write_runtime_example`（L42–L49）：接收`settings`、`template`。 控制顺序：L44按`path.exists()`分支；L45抛异常，停止当前正常路径。 调用`runtime_path`、`path.exists`、`FileExistsError`、`settings.prepare`、`write_json`、`RuntimeConfig(database_url_env=prefix + "_DATABASE_URL").model_du…`、`RuntimeConfig`。 返回路径：L49的`path`。
- `runtime_config`（L52–L66）：接收`settings`、`template`、`initialize`。 控制顺序：L54按`not path.is_file()`分支；L55抛异常，停止当前正常路径；L57按`not re.fullmatch(r"NATIVE_[A-Z0-9_]+", config.database_url_env)`分支；L58抛异常，停止当前正常路径；L59按`initialize and config.initialize_empty_database is not True`分支；L60抛异常，停止当前正常路径；L63按`not url`分支；L64抛异常，停止当前正常路径。 调用`runtime_path`、`path.is_file`、`PrerequisiteError`、`RuntimeConfig.model_validate_json`、`path.read_text`、`re.fullmatch`、`dotenv_values`、`env.get`、`checked_database`。 返回路径：L66的`config, url`。
- `database_identity`（L69–L72）：接收`url`。 源码说明：Bind a retained product to its database without storing credentials.。 调用`checked_database`、`digest`。 返回路径：L72的`digest({"host": parsed.host, "port": parsed.port or 5432, "database": parsed.database})`。
- `check_database_identity`（L75–L79）：接收`receipt`、`url`。 控制顺序：L76按`receipt.get("database_identity") != database_identity(url)`分支；L77抛异常，停止当前正常路径。 调用`receipt.get`、`database_identity`、`PrerequisiteError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prerequisites`（L82–L92）：接收`template`。 控制顺序：L83按`os.name == "nt"`分支；L84抛异常，停止当前正常路径；L88遍历`commands`；L89按`not shutil.which(name)`分支；L90抛异常，停止当前正常路径；L91按`not (ROOT / ".native/browser/node_modules/playwright").is_dir()`分支；L92抛异常，停止当前正常路径。 调用`PrerequisiteError`、`shutil.which`、`(ROOT / ".native/browser/node_modules/playwright").is_dir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `managed_generate`（L95–L149）：接收`settings`、`template`、`plan`、`destination`、`customization`。 控制顺序：L101按`runtime_enabled(settings, template)`分支；L109按`receipt_path.is_file()`分支；L111按`receipt.get("execution") == "managed-runtime" and receipt.get("spec_digest") == diges…`分支；L117抛异常，停止当前正常路径；L134按`report.get("generated_runtime_verified") is not True`分支；L135抛异常，停止当前正常路径。 调用`validate_plan`、`Path(destination).resolve`、`Path`、`prerequisites`、`runtime_enabled`、`runtime_config`、`for_run`、`receipt_path.is_file`、`json.loads`等。 返回路径：L116的`receipt`；L149的`receipt`。
- `require_native_style`（L152–L223）：接收`report`、`receipt`、`current`。 源码说明：A legacy runtime receipt is not evidence of native UI inheritance.。 控制顺序：L162按`template not in PROFILES or report.get("template") != template or not isinstance(styl…`分支；L172抛异常，停止当前正常路径；L178遍历`PROFILES[template]["protected"]`；L184按`not group`分支；L185抛异常，停止当前正常路径；L187按`style.get("protected_files") != protected or style.get("protected_source_digest") != …`分支；L190抛异常，停止当前正常路径；L192按`not isinstance(entities, list) or not entities or any( not isinstance(name, str) or n…`分支。后续分支沿下方源码相同行号继续阅读。 调用`receipt.get`、`report.get`、`isinstance`、`style.get`、`PrerequisiteError`、`len`、`current.items`、`name.startswith`、`frontend.items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `require_native_business`（L226–L313）：接收`report`、`receipt`、`spec_path`。 源码说明：Classic CRUD receipts cannot stand in for either business installation.。 控制顺序：L234抛异常，停止当前正常路径；L236按`identity != receipt.get("spec_digest") or identity != report.get("spec_digest")`分支；L237抛异常，停止当前正常路径；L238按`not plan.business`分支；L239按`report.get("business_contract") is not None`分支；L240抛异常，停止当前正常路径；L243按`restored.get("restart") is not True or restored.get("restart_preserved_records") is n…`分支；L244抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Plan.model_validate_json`、`Path(spec_path).read_text`、`Path`、`PrerequisiteError`、`digest`、`plan.model_dump`、`receipt.get`、`report.get`、`restored.get`等。 返回路径：L241的`False`；L313的`True`。
- `require_native_runtime`（L316–L350）：接收`report`。 源码说明：Shared fail-closed runtime/deployment gates for production and zero-model CI.。 控制顺序：L330按`any(report.get(name) is not True for name in gates)`分支；L331抛异常，停止当前正常路径；L342按`not isinstance(restored, dict) or any(restored.get(key) is not True for key in requir…`分支；L347抛异常，停止当前正常路径。 调用`any`、`report.get`、`PrerequisiteError`、`isinstance`、`restored.get`。 返回路径：L350的`gates`。
- `managed_verify`（L353–L391）：接收`destination`、`receipt`。 控制顺序：L356按`not report_path.is_file()`分支；L357抛异常，停止当前正常路径；L358按`report_path.stat().st_size > MAX_ACCEPTANCE_BYTES`分支；L359抛异常，停止当前正常路径；L362按`len(raw) > MAX_ACCEPTANCE_BYTES`分支；L363抛异常，停止当前正常路径；L364按`hashlib.sha256(raw).hexdigest() != receipt.get("evidence_sha256")`分支；L365抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`report_path.is_file`、`PrerequisiteError`、`report_path.stat`、`report_path.open`、`handle.read`、`len`、`hashlib.sha256(raw).hexdigest`、`hashlib.sha256`等。 返回路径：L391的`result`。
- `managed_package`（L394–L416）：接收`destination`、`report`。 控制顺序：L400按`report != verified`分支；L401抛异常，停止当前正常路径。 调用`Path`、`json.loads`、`(destination.parent / "native-generation.json").read_text`、`managed_verify`、`PrerequisiteError`、`manifest`、`pack_source`、`sha`、`write_json`。 返回路径：L416的`result`。
- `serve_managed`（L419–L445）：接收`settings`、`run_id`。 控制顺序：L423按`not receipt_path.is_file()`分支；L424抛异常，停止当前正常路径；L426按`receipt.get("execution") != "managed-runtime"`分支；L427抛异常，停止当前正常路径；L444在`True`成立时循环。 调用`str`、`uuid.UUID`、`receipt_path.is_file`、`PrerequisiteError`、`json.loads`、`receipt_path.read_text`、`receipt.get`、`managed_verify`、`runtime_config`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/native_delivery.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L445。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18574`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_delivery.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "248ec20a2b3fbd6f01883e08e52d1bf9bc1c55818c4ebbe4bf472e86c7b8ffe8"} -->
````python
# workbench/native_delivery.py
"""Explicitly authorized local native runtime delivery; source export is a separate mode."""

import hashlib
import json
import os
import re
import shutil
import uuid
from contextlib import ExitStack
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, StrictBool

from workbench.domain import Plan, digest
from workbench.filesystem import manifest, pack_source, sha, write_json
from workbench.generator import PrerequisiteError
from workbench.native_environment import checked_database, native_environment, running_backend
from workbench.native_evidence import MAX_ACCEPTANCE_BYTES, native_review_evidence
from workbench.native_frontend import frontend_environment, frontend_preview
from workbench.native_lab import run_acceptance
from workbench.native_modules import validate_plan
from workbench.settings import ROOT


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    database_url_env: str
    initialize_empty_database: StrictBool = False


def runtime_path(settings, template):
    if template not in {"fastapiadmin", "yudao-vben"}:
        raise ValueError("未知原生模板")
    return settings.data_dir / "native" / f"{template}.runtime.json"


def runtime_enabled(settings, template):
    return runtime_path(settings, template).is_file()


def write_runtime_example(settings, template):
    path = runtime_path(settings, template)
    if path.exists():
        raise FileExistsError("原生运行配置已存在，拒绝覆盖")
    settings.prepare()
    prefix = "NATIVE_FASTAPIADMIN" if template == "fastapiadmin" else "NATIVE_YUDAO"
    write_json(path, RuntimeConfig(database_url_env=prefix + "_DATABASE_URL").model_dump())
    return path


def runtime_config(settings, template, *, initialize=True):
    path = runtime_path(settings, template)
    if not path.is_file():
        raise PrerequisiteError("先执行 rnd native runtime-config TEMPLATE 并授权专用空开发库")
    config = RuntimeConfig.model_validate_json(path.read_text(encoding="utf-8"))
    if not re.fullmatch(r"NATIVE_[A-Z0-9_]+", config.database_url_env):
        raise PrerequisiteError("原生数据库只能读取明确的 NATIVE_* 环境变量")
    if initialize and config.initialize_empty_database is not True:
        raise PrerequisiteError("请明确批准仅在自己创建的专用空数据库初始化原生框架")
    env = {**dotenv_values(ROOT / ".env"), **os.environ}
    url = env.get(config.database_url_env)
    if not url:
        raise PrerequisiteError("原生数据库环境变量未设置")
    checked_database(url)
    return config, url


def database_identity(url):
    """Bind a retained product to its database without storing credentials."""
    parsed = checked_database(url)
    return digest({"host": parsed.host, "port": parsed.port or 5432, "database": parsed.database})


def check_database_identity(receipt, url):
    if receipt.get("database_identity") != database_identity(url):
        raise PrerequisiteError(
            "当前原生数据库不是该产品已验证的数据库；恢复原数据库配置，不自动迁移"
        )


def prerequisites(template):
    if os.name == "nt":
        raise PrerequisiteError(
            "原生全栈运行通道请在 WSL 2/Linux 使用；默认 Python 通道支持 Windows"
        )
    commands = ["git", "uv", "node", "pnpm"] + (["java", "mvn"] if template == "yudao-vben" else [])
    for name in commands:
        if not shutil.which(name):
            raise PrerequisiteError(f"缺少原生运行工具：{name}，请按手册原生运行章节安装")
    if not (ROOT / ".native/browser/node_modules/playwright").is_dir():
        raise PrerequisiteError("尚未安装独立 Playwright/Chromium 验证工具，请按手册安装")


def managed_generate(settings, template, plan, destination, *, customization=None):
    from workbench.native import prepare_sources

    plan = validate_plan(plan)
    destination = Path(destination).resolve()
    prerequisites(template)
    if runtime_enabled(settings, template):
        _, url = runtime_config(settings, template)
        redis_port = 6379
    else:
        from workbench.native_resources import for_run

        url, redis_port = for_run(settings, destination.parent.name)
    receipt_path = destination.parent / "native-generation.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt.get("execution") == "managed-runtime" and receipt.get("spec_digest") == digest(
            plan.model_dump()
        ):
            check_database_identity(receipt, url)
            managed_verify(destination, receipt)
            return receipt
        raise PrerequisiteError("已有产物不能被另一份设计或执行模式覆盖")
    sources = prepare_sources(settings, template)
    slots = {item["slot"]: Path(item["path"]) for item in sources}
    reports = destination.parent / "native-evidence"
    source = slots["fastapiadmin"] if template == "fastapiadmin" else slots["backend"]
    output = destination if template == "fastapiadmin" else destination / "backend"
    report = run_acceptance(
        template,
        source,
        output,
        slots.get("frontend"),
        url,
        reports,
        plan,
        redis_port=redis_port,
        customization=customization,
    )
    if report.get("generated_runtime_verified") is not True:
        raise PrerequisiteError("原生运行验收尚未完成")
    receipt = {
        "template": template,
        "execution": "managed-runtime",
        "database_identity": database_identity(url),
        "sources": [{k: v for k, v in item.items() if k != "path"} for item in sources],
        "spec_digest": digest(plan.model_dump()),
        "files": manifest(destination),
        "validation_level": "runtime",
        "runtime_verified": True,
        "evidence_sha256": sha(reports / "acceptance.json"),
        "report": report,
    }
    write_json(receipt_path, receipt)
    return receipt


def require_native_style(report, receipt, current):
    """A legacy runtime receipt is not evidence of native UI inheritance."""
    from workbench.native_style import PROFILES, native_page_contracts

    template = receipt.get("template")
    style = report.get("native_style")
    error = (
        "原生UI风格验收证据缺失、过期或不匹配；保留运行目录与数据库，"
        "需要重新执行原生UI、浏览器及独立新库验收，不能沿用旧回执或删除数据绕过"
    )
    if (
        template not in PROFILES
        or report.get("template") != template
        or not isinstance(style, dict)
        or style.get("template") != template
        or style.get("ui_family") != PROFILES[template]["family"]
        or style.get("passed") is not True
        or style.get("shell_and_theme_unchanged") is not True
        or style.get("generic_frontend_substitution") is not False
    ):
        raise PrerequisiteError(error)
    root = "frontend/web/" if template == "fastapiadmin" else "frontend-product/"
    frontend = {
        name[len(root) :]: value for name, value in current.items() if name.startswith(root)
    }
    protected = {}
    for prefix in PROFILES[template]["protected"]:
        group = {
            name: value
            for name, value in frontend.items()
            if name == prefix or (prefix.endswith("/") and name.startswith(prefix))
        }
        if not group:
            raise PrerequisiteError(error)
        protected.update(group)
    if style.get("protected_files") != protected or style.get("protected_source_digest") != digest(
        protected
    ):
        raise PrerequisiteError(error)
    entities, pages = report.get("entities"), style.get("generated_pages")
    if (
        not isinstance(entities, list)
        or not entities
        or any(
            not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name)
            for name in entities
        )
        or len(set(entities)) != len(entities)
        or not isinstance(pages, list)
    ):
        raise PrerequisiteError(error)
    expected = {
        path: values[0]
        for path, values in native_page_contracts(
            template, entities, report.get("business_contract") is not None
        ).items()
    }
    if (
        len(pages) != len(expected)
        or any(
            not isinstance(page, dict)
            or not isinstance(page.get("path"), str)
            or page["path"] not in expected
            or not frontend.get(page["path"])
            or page.get("sha256") != frontend.get(page["path"])
            or not isinstance(page.get("native_components"), list)
            or any(name not in page["native_components"] for name in expected[page["path"]])
            for page in pages
        )
        or {page["path"] for page in pages} != set(expected)
    ):
        raise PrerequisiteError(error)


def require_native_business(report, receipt, spec_path):
    """Classic CRUD receipts cannot stand in for either business installation."""
    from workbench.business_browser import require_business_browser

    error = "原生业务验收缺失或与批准设计不匹配；需要真实角色、业务浏览器和独立新库证据"
    try:
        plan = Plan.model_validate_json(Path(spec_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PrerequisiteError(error) from exc
    identity = digest(plan.model_dump())
    if identity != receipt.get("spec_digest") or identity != report.get("spec_digest"):
        raise PrerequisiteError(error)
    if not plan.business:
        if report.get("business_contract") is not None:
            raise PrerequisiteError(error)
        return False
    restored = report.get("portable_restored", {})
    if restored.get("restart") is not True or restored.get("restart_preserved_records") is not True:
        raise PrerequisiteError(error)
    if not isinstance(restored.get("restart_records"), dict) or set(
        restored["restart_records"]
    ) != {entity.name for entity in plan.entities}:
        raise PrerequisiteError(error)
    for entity, record in restored["restart_records"].items():
        if (
            not isinstance(record, dict)
            or record.get("id") != restored.get("business", {}).get("records", {}).get(entity)
            or not isinstance(record.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"])
        ):
            raise PrerequisiteError(error)
    required = (
        "passed",
        "real_native_auth",
        "public_native_registration",
        "three_roles",
        "relations",
        "related_history",
        "assignment",
        "transitions",
        "handling_history",
        "audit",
        "in_app_reminders",
        "due_reminders",
        "note_reminders",
        "status_change_reminders",
        "reminder_read_isolation",
        "metrics",
        "row_isolation",
    )
    for evidence in (
        report.get("business_contract"),
        report.get("portable_restored", {}).get("business"),
    ):
        if (
            not isinstance(evidence, dict)
            or evidence.get("spec_digest") != identity
            or any(evidence.get(key) is not True for key in required)
            or not isinstance(evidence.get("records"), dict)
            or set(evidence["records"]) != {entity.name for entity in plan.entities}
            or any(
                not isinstance(value, str) or not re.fullmatch(r"[1-9][0-9]*", value)
                for value in evidence["records"].values()
            )
        ):
            raise PrerequisiteError(error)
    for browser in (
        report.get("business_browser"),
        report.get("portable_restored", {}).get("browser"),
    ):
        try:
            if not isinstance(browser, dict) or browser.get("spec_digest") != identity:
                raise ValueError("Unbound browser evidence")
            require_business_browser(browser, plan, receipt["template"])
        except (KeyError, ValueError, TypeError) as exc:
            raise PrerequisiteError(error) from exc
    if receipt["template"] == "yudao-vben":
        from workbench.yudao_navigation_checks import validate_navigation

        try:
            for business in (report["business_contract"], restored["business"]):
                first = validate_navigation(business.get("installed_navigation"), plan)
                restarted = validate_navigation(business.get("installed_navigation_restart"), plan)
                if first != restarted:
                    raise ValueError("Installed navigation changed across restart")
        except (KeyError, ValueError, TypeError) as exc:
            raise PrerequisiteError(error) from exc
    return True


def require_native_runtime(report):
    """Shared fail-closed runtime/deployment gates for production and zero-model CI."""
    gates = (
        "generated_runtime_verified",
        "native_codegen",
        "automatic_mount",
        "menu_and_permissions",
        "real_crud",
        "restart_persistence",
        "frontend_build",
        "frontend_typecheck",
        "real_browser",
        "source_unmodified",
    )
    if any(report.get(name) is not True for name in gates):
        raise PrerequisiteError("原生运行未满足所有独立验收门槛")
    restored = report.get("portable_restored")
    required_true = (
        "passed",
        "fresh_database",
        "frontend_started",
        "installed_from_lock",
        "standalone_launcher",
        "restart",
    )
    required_false = ("source_database_reused", "original_platform_imported", "model_required")
    if (
        not isinstance(restored, dict)
        or any(restored.get(key) is not True for key in required_true)
        or any(restored.get(key) is not False for key in required_false)
    ):
        raise PrerequisiteError(
            "原生独立交付缺少通过的新数据库恢复证据；不得以原生成数据库可启动代替独立交付"
        )
    return gates


def managed_verify(destination, receipt):
    destination = Path(destination)
    report_path = destination.parent / "native-evidence/acceptance.json"
    if not report_path.is_file():
        raise PrerequisiteError("原生运行证据丢失或已改变")
    if report_path.stat().st_size > MAX_ACCEPTANCE_BYTES:
        raise PrerequisiteError("原生运行证据超出安全大小限制")
    with report_path.open("rb") as handle:
        raw = handle.read(MAX_ACCEPTANCE_BYTES + 1)
    if len(raw) > MAX_ACCEPTANCE_BYTES:
        raise PrerequisiteError("原生运行证据超出安全大小限制")
    if hashlib.sha256(raw).hexdigest() != receipt.get("evidence_sha256"):
        raise PrerequisiteError("原生运行证据丢失或已改变")
    report = json.loads(raw)
    gates = require_native_runtime(report)
    current = manifest(destination)
    if current != receipt["files"] or report.get("spec_digest") != receipt.get("spec_digest"):
        raise PrerequisiteError("原生源码或设计在验收后发生变化，需要重新验证")
    require_native_style(report, receipt, current)
    business = require_native_business(report, receipt, report_path.with_name("approved-spec.json"))
    plan = Plan.model_validate_json(
        report_path.with_name("approved-spec.json").read_text(encoding="utf-8")
    )
    review_evidence = native_review_evidence(report, plan, current, receipt["evidence_sha256"])
    result = {
        "passed": True,
        "validation_level": "runtime",
        "runtime_verified": True,
        "production_ready": False,
        "source_digest": digest(current),
        "evidence_sha256": receipt["evidence_sha256"],
        "checks": [*gates, "native_template_ui_style"]
        + (["native_business_contract"] if business else []),
        "database_delivery": "standalone-fresh-database-bootstrap",
        "startup": "uv run --no-project --python 3.14 python start.py",
        "native_acceptance": review_evidence,
    }
    write_json(destination.parent / "verification.json", result)
    return result


def managed_package(destination, report):
    destination = Path(destination)
    receipt = json.loads(
        (destination.parent / "native-generation.json").read_text(encoding="utf-8")
    )
    verified = managed_verify(destination, receipt)
    if report != verified:
        raise PrerequisiteError("交付的原生运行验证报告不匹配")
    listing = manifest(destination)
    package = destination.parent / "native-runtime.zip"
    archive_report = pack_source(destination, package, template=receipt["template"])
    result = {
        "package": package.name,
        "sha256": sha(package),
        "files": listing,
        "archive": archive_report,
        "validation_level": "runtime",
        "runtime_verified": True,
        "production_ready": False,
        "database_delivery": verified["database_delivery"],
    }
    write_json(destination.parent / "delivery.json", result)
    return result


def serve_managed(settings, run_id):
    run_id = str(uuid.UUID(run_id))
    destination = settings.data_dir / "runs" / run_id / "product"
    receipt_path = destination.parent / "native-generation.json"
    if not receipt_path.is_file():
        raise PrerequisiteError("未找到此运行的原生全栈产品")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("execution") != "managed-runtime":
        raise PrerequisiteError("SOURCE_READY 源码导出不能直接作为已挂载产品启动")
    managed_verify(destination, receipt)
    template = receipt["template"]
    _, url = runtime_config(settings, template, initialize=False)
    check_database_identity(receipt, url)
    backend = destination / "backend"
    frontend = destination / ("frontend/web" if template == "fastapiadmin" else "frontend-product")
    env = native_environment(template, backend, url, 8001 if template == "fastapiadmin" else 48080)
    reports = destination.parent / "native-live"
    with ExitStack() as stack:
        base, _ = stack.enter_context(running_backend(template, backend, env, reports))
        front = stack.enter_context(
            frontend_preview(template, frontend, frontend_environment(template, base), reports)
        )
        print(f"Native backend: {base}; native frontend: {front}; Ctrl+C to stop", flush=True)
        import time

        while True:
            time.sleep(1)
````
