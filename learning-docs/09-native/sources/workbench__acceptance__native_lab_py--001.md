# workbench/acceptance/native_lab.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：两套原生全链路验收的总协调。** run_acceptance依次准备本机数据库、启动后端、生成挂载模块、检查CRUD/RBAC、重启验证持久化、构建前端和打开真实浏览器。任何一步失败都保留报告并退出，不能仅看后端健康接口。

**对应关系：** ci_native_generated/native_delivery → native_lab → native_environment/modules/acceptance/frontend。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.acceptance.native_acceptance`、`workbench.business.browser`、`workbench.core.contracts`、`workbench.delivery`、`workbench.delivery.portable`、`workbench.filesystem`、`workbench.generation.native.compatibility`、`workbench.generation.native.frontend`、`workbench.generation.native.modules`、`workbench.generation.native.style`、`workbench.infrastructure.native.environment`、`workbench.infrastructure.native.ports`、`workbench.infrastructure.processes.tools`、`workbench.settings`、`workbench.templates.standards`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 把原生流程看成一串证据：固定来源→专用库→真实生成→SQL/菜单→编译/类型检查→HTTP→原生页面。run_acceptance只能在每一步实际完成后汇总报告。某个模板跑通不能替另一个模板写passed，恢复也必须先核对原始Plan、源码与数据库身份。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_runtime_check`（L48–L84）：接收`check`、`check_id`、`*args`、`**kwargs`。 源码说明：Only explicitly selected executable acceptance checks use this boundary.。 控制顺序：L50按`check_id not in { "customer-service-http", "generated-crud", "generated-permissions",…`分支；L57抛异常，停止当前正常路径；L61按`isinstance(exc, BusinessBrowserValidationFailure) and check_id != "customer-service-b…`分支；L65抛异常，停止当前正常路径；L72遍历`reversed(traceback.extract_tb(exc.__traceback__))`；L77按`frame.name.isidentifier() and relative.suffix == ".py"`分支；L82抛异常，停止当前正常路径。 调用`ValueError`、`check`、`isinstance`、`reversed`、`traceback.extract_tb`、`Path(frame.filename).resolve().relative_to`、`Path(frame.filename).resolve`、`Path`、`frame.name.isidentifier`等。 返回路径：L59的`check(*args, **kwargs)`。
- `generated_browser`（L87–L110）：接收`template`、`front_url`、`reports`。 控制顺序：L109抛异常，停止当前正常路径。 调用`str`、`reports.resolve`、`(reports / "browser-targets.json").resolve`、`run_command`、`os.environ.get`、`atomic_text`、`getattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `run_acceptance`（L113–L143）：接收`template`、`source`、`output`、`frontend_source`、`url`、`reports`、`plan`、`redis_port`、`customization`、`source_handoff`。 源码说明：Hold one non-ephemeral backend lease across all build/restart phases.。 控制顺序：L128按`plan.custom_rules and customization is None`分支；L129抛异常，停止当前正常路径。 调用`validate_plan`、`ValueError`、`backend_port_lease`、`Path`、`_run_acceptance`。 返回路径：L131的`_run_acceptance( template, source, output, frontend_source, url, reports, plan, redis_port…`。
- `_run_acceptance`（L146–L472）：接收`template`、`source`、`output`、`frontend_source`、`url`、`reports`、`plan`、`redis_port`、`customization`、`source_handoff`、`backend_port`。 源码说明：Shared by CLI and CI; never reset an existing database or workspace.。 控制顺序：L173按`not resumed`分支；L176按`template == "fastapiadmin"`分支；L180按`not resumed`分支；L182按`not resumed`分支；L197按`not resumed`分支；L201按`template == "fastapiadmin"`分支；L224按`plan.business`分支；L243按`plan.custom_rules`分支。后续分支沿下方源码相同行号继续阅读。 调用`Path(source).resolve`、`Path`、`Path(output).resolve`、`Path(reports).resolve`、`reports.mkdir`、`manifest`、`native_recovery.identity`、`output.exists`、`native_recovery.load`等。 返回路径：L443的`report`。
- `_run_acceptance.stage`（L190–L192）：接收`name`。 调用`write_json`、`print`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/acceptance/native_lab.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L472。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18966`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/acceptance/native_lab.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "11a6bfcfea954aff021e170030df5b0295d03ba9448576534b40e71e3201d904"} -->
````python
# workbench/acceptance/native_lab.py
"""Actual native generation, mounting, permissions, CRUD, restart and browser acceptance."""

import os
import traceback
from pathlib import Path

from workbench.acceptance.native_acceptance import (
    check_generated_persistence,
    generated_crud,
    generated_permissions,
)
from workbench.business.browser import BusinessBrowserValidationFailure
from workbench.core.contracts import digest
from workbench.delivery import recovery as native_recovery
from workbench.delivery.portable import (
    build_native_delivery,
    export_menu_sql,
    menu_snapshot,
    verify_native_delivery,
)
from workbench.filesystem import atomic_text, manifest, write_json
from workbench.generation.native.compatibility import prepare_fastapi_transactions
from workbench.generation.native.frontend import (
    build_frontend,
    frontend_environment,
    frontend_preview,
)
from workbench.generation.native.modules import (
    create_native_tables,
    generate_modules,
    validate_plan,
)
from workbench.generation.native.style import verify_native_style
from workbench.infrastructure.native.environment import (
    bootstrap_database,
    copy_source,
    install_backend,
    login,
    native_environment,
    running_backend,
)
from workbench.infrastructure.native.ports import backend_port_lease
from workbench.infrastructure.processes.tools import run_command
from workbench.settings import ROOT
from workbench.templates.standards import write_coding_standard


def _runtime_check(check, *args, check_id, **kwargs):
    """Only explicitly selected executable acceptance checks use this boundary."""
    if check_id not in {
        "customer-service-http",
        "generated-crud",
        "generated-permissions",
        "restart-persistence",
        "customer-service-browser",
    }:
        raise ValueError("Unknown native acceptance check identifier")
    try:
        return check(*args, **kwargs)
    except (AssertionError, BusinessBrowserValidationFailure) as exc:
        if (
            isinstance(exc, BusinessBrowserValidationFailure)
            and check_id != "customer-service-browser"
        ):
            raise
        reason = (
            "browser_evidence_failed"
            if isinstance(exc, BusinessBrowserValidationFailure)
            else "assertion_failed"
        )
        location = ""
        for frame in reversed(traceback.extract_tb(exc.__traceback__)):
            try:
                relative = Path(frame.filename).resolve().relative_to(ROOT / "workbench")
            except ValueError:
                continue
            if frame.name.isidentifier() and relative.suffix == ".py":
                location = f"; source=workbench/{relative.as_posix()}:{frame.lineno}:{frame.name}"
                break
        # Only a controller-owned identifier is serialized. Assertion text can
        # contain credentials or entire HTTP responses and is deliberately omitted.
        raise native_recovery.NativeValidationFailure(
            f"原生可执行验收未通过 [check_id={check_id}; reason={reason}{location}]"
        ) from exc


def generated_browser(template, front_url, reports):
    command = [
        "node",
        str(ROOT / "scripts/native_browser.cjs"),
        template,
        front_url,
        str(reports.resolve()),
        str(ROOT / ".native/browser/node_modules/playwright"),
        str((reports / "browser-targets.json").resolve()),
    ]
    try:
        result = run_command(
            command,
            ROOT,
            240,
            {
                "NODE_OPTIONS": "--dns-result-order=ipv4first",
                "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "0"),
            },
        )
    except Exception as exc:
        atomic_text(reports / "browser.log", getattr(exc, "log", str(exc)))
        raise
    atomic_text(reports / "browser.log", result["log"])


def run_acceptance(
    template,
    source,
    output,
    frontend_source,
    url,
    reports,
    plan,
    redis_port=6379,
    *,
    customization=None,
    source_handoff=None,
):
    """Hold one non-ephemeral backend lease across all build/restart phases."""
    plan = validate_plan(plan)
    if plan.custom_rules and customization is None:
        raise ValueError("原生业务规则未接入Aider执行器；不允许忽略规则生成CRUD")
    with backend_port_lease(Path(reports) / "backend-port.json") as backend_port:
        return _run_acceptance(
            template,
            source,
            output,
            frontend_source,
            url,
            reports,
            plan,
            redis_port,
            customization=customization,
            **({"source_handoff": source_handoff} if source_handoff is not None else {}),
            backend_port=backend_port,
        )


def _run_acceptance(
    template,
    source,
    output,
    frontend_source,
    url,
    reports,
    plan,
    redis_port=6379,
    *,
    customization=None,
    source_handoff=None,
    backend_port,
):
    """Shared by CLI and CI; never reset an existing database or workspace."""
    source, output, reports = (
        Path(source).resolve(),
        Path(output).resolve(),
        Path(reports).resolve(),
    )
    reports.mkdir(parents=True, exist_ok=True)
    before = manifest(source)
    frontend_before = manifest(frontend_source) if template == "yudao-vben" else None
    product_root = output if template == "fastapiadmin" else output.parent
    checkpoint = reports / "recovery.json"
    expected = native_recovery.identity(template, plan, url, source, frontend_source)
    resumed = native_recovery.load(checkpoint, expected, product_root) if output.exists() else None
    if not resumed:
        copy_source(source, output)
    backend = output / "backend" if template == "fastapiadmin" else output
    if template == "fastapiadmin":
        frontend = output / "frontend/web"
    else:
        frontend = output.parent / "frontend-product"
        if not resumed:
            copy_source(frontend_source, frontend)
    if not resumed:
        write_coding_standard(product_root, template)
    env = native_environment(template, backend, url, backend_port, redis_port=redis_port)
    write_json(reports / "approved-spec.json", plan.model_dump())
    write_json(
        reports / "acceptance.json", {"template": template, "generated_runtime_verified": False}
    )

    def stage(name):
        write_json(reports / "progress.json", {"template": template, "stage": name})
        print(f"Native {template}: {name}", flush=True)

    generation_ready = bool(resumed)
    try:
        targets = resumed["targets"] if resumed else None
        if not resumed:
            native_recovery.save(
                checkpoint, expected, product_root, [], resumable=False, stage="initial-generation"
            )
            if template == "fastapiadmin":
                write_json(
                    reports / "native-compatibility.json", prepare_fastapi_transactions(backend)
                )
            stage("bootstrap-empty-database")
            bootstrap_database(template, backend, url)
            stage("baseline-install")
            install_backend(template, backend, reports / "baseline")
            with running_backend(template, backend, env, reports / "baseline") as (
                base_url,
                openapi,
            ):
                stage("native-generation")
                token = login(template, base_url)
                write_json(reports / "baseline/login.json", {"native_login": True})
                baseline_menus = menu_snapshot(template, url)
                mapping = create_native_tables(
                    template, plan, url, digest(plan.model_dump()), reports
                )
                targets = generate_modules(
                    template, backend, frontend, base_url, openapi, token, mapping, plan, reports
                )
                export_menu_sql(template, url, baseline_menus, reports / "menu-seed.sql")
                if plan.business:
                    from workbench.business.native import install_native_business

                    stage("native-business-contract")
                    install_native_business(
                        template, plan, backend, frontend, targets, reports, url
                    )
            native_recovery.save(
                checkpoint,
                expected,
                product_root,
                targets,
                resumable=True,
                stage="native-generated",
            )
            generation_ready = True
        else:
            stage("resume-native-validation")
        product_root = output if template == "fastapiadmin" else output.parent
        if plan.custom_rules:
            from workbench.generation.native.coding import verified_native_customization

            stage("plop-aider-native-business-rules")
            if not (resumed and verified_native_customization(plan, product_root, reports)):
                customization(
                    template, plan, product_root, backend, frontend, env, targets, reports
                )
        if template == "yudao-vben":
            stage("generated-build")
            install_backend(template, backend, reports / "generated-build")
        with running_backend(template, backend, env, reports / "generated") as (base_url, _):
            token = login(template, base_url)
            if plan.business:
                from workbench.business.probe import customer_service_acceptance

                stage("customer-service-http")
                records = _runtime_check(
                    customer_service_acceptance,
                    template,
                    base_url,
                    token,
                    targets,
                    plan,
                    check_id="customer-service-http",
                )
                write_json(reports / "generated/business.json", records)
            else:
                stage("generated-crud")
                records = _runtime_check(
                    generated_crud,
                    template,
                    base_url,
                    token,
                    targets,
                    plan,
                    check_id="generated-crud",
                )
                write_json(reports / "generated/crud.json", records)
                stage("generated-permissions")
                write_json(
                    reports / "generated/permissions.json",
                    _runtime_check(
                        generated_permissions,
                        template,
                        base_url,
                        token,
                        targets,
                        plan,
                        check_id="generated-permissions",
                    ),
                )
        # Compile the large Vben application while the Java process is stopped.
        # Running both heaps concurrently needlessly exhausts smaller CI/WSL hosts.
        front_env = frontend_environment(template, base_url, plan.title)
        stage("native-frontend-build")
        build_frontend(
            template,
            frontend,
            front_env,
            reports,
            prepared=(reports / "native-front-prepared.json").is_file(),
        )
        write_json(reports / "native-front-prepared.json", {"prepared": True})
        style = verify_native_style(
            template,
            source / "frontend/web" if template == "fastapiadmin" else frontend_source,
            frontend,
            plan,
            reports,
        )
        stage("restart-persistence")
        with running_backend(template, backend, env, reports / "restart") as (base_url, _):
            token = login(template, base_url)
            if plan.business:
                from workbench.business.probe import BusinessClient

                client = BusinessClient(template, base_url, token, targets)
                try:
                    for name, identifier in records["records"].items():
                        if not any(str(row["id"]) == identifier for row in client.rows(name)):
                            raise native_recovery.NativeValidationFailure(
                                "Business record missing after restart"
                            )
                finally:
                    client.close()
                if template == "yudao-vben":
                    from workbench.acceptance.yudao_navigation import check_navigation_restart

                    records["installed_navigation_restart"] = check_navigation_restart(
                        template, base_url, token, targets, records, plan
                    )
                write_json(
                    reports / "restart/persistence.json",
                    {"process_restart_preserves_records": True, "business": True},
                )
            else:
                write_json(
                    reports / "restart/persistence.json",
                    _runtime_check(
                        check_generated_persistence,
                        template,
                        base_url,
                        token,
                        targets,
                        records,
                        check_id="restart-persistence",
                    ),
                )
            for target, entity in zip(targets, plan.entities, strict=True):
                target["fields"] = [field.model_dump() for field in entity.fields]
                from workbench.acceptance.native_business_checks import wire

                rule = next(
                    (rule for rule in plan.custom_rules if rule.entity == entity.name), None
                )
                if rule:
                    target["business_rule"] = {
                        "accept": wire(template, rule.accept_examples[0]),
                        "reject": wire(template, rule.reject_examples[0]),
                    }
            write_json(reports / "browser-targets.json", targets)
            with frontend_preview(template, frontend, front_env, reports) as front_url:
                stage("native-browser")
                if plan.business:
                    from workbench.business.browser import run_business_browser

                    script = (
                        ROOT
                        / "scripts"
                        / (
                            "business_fastapi_browser.cjs"
                            if template == "fastapiadmin"
                            else "business_yudao_browser.cjs"
                        )
                    )
                    browser_report = _runtime_check(
                        run_business_browser,
                        template,
                        script,
                        front_url,
                        reports,
                        records,
                        plan,
                        ROOT / ".native/browser/node_modules/playwright",
                        check_id="customer-service-browser",
                    )
                    write_json(reports / "browser.json", browser_report)
                else:
                    generated_browser(template, front_url, reports)
        if before != manifest(source):
            raise native_recovery.NativeIntegrityError("Original native source was modified")
        if frontend_before is not None and frontend_before != manifest(frontend_source):
            raise native_recovery.NativeIntegrityError("Original Vben source was modified")
        write_json(
            reports / "generated-manifest.json",
            {"backend": manifest(backend), "frontend": manifest(frontend)},
        )
        report = {
            "template": template,
            "scope": "generated-native-modules",
            "backend_port": backend_port,
            "backend_url": base_url,
            "generated_runtime_verified": True,
            "native_codegen": True,
            "automatic_mount": True,
            "menu_and_permissions": True,
            "real_crud": True,
            "restart_persistence": True,
            "frontend_build": True,
            "frontend_typecheck": True,
            "real_browser": True,
            "entities": [e.name for e in plan.entities],
            "spec_digest": digest(plan.model_dump()),
            "source_unmodified": True,
            "native_business_rules": bool(plan.custom_rules),
            "native_style": style,
            "business_contract": records if plan.business else None,
            "business_browser": browser_report if plan.business else None,
            "data_scope": "shared-with-native-role-permissions",
        }
        stage("portable-startup-assets")
        product_root = output if template == "fastapiadmin" else output.parent
        report["portable_delivery"] = build_native_delivery(
            template, product_root, reports, plan, targets, url
        )
        stage("independent-native-delivery")
        report["portable_restored"] = verify_native_delivery(
            product_root,
            url,
            reports,
            redis_port,
            template=template,
            **({"source_handoff": source_handoff} if source_handoff is not None else {}),
        )
        stage("accepted")
        write_json(reports / "acceptance.json", report)
        print(
            "Generated native modules, menus, permissions, CRUD, restart, frontend build and browser PASS"
        )
        return report
    except Exception as exc:
        # Integrity failures never become downloadable failed-runtime candidates,
        # even if the tool that noticed the corruption raised a generic error.
        if digest(plan.model_dump()) != expected["spec_digest"]:
            raise native_recovery.NativeIntegrityError("Approved native Plan was modified") from exc
        if before != manifest(source) or (
            frontend_before is not None and frontend_before != manifest(frontend_source)
        ):
            raise native_recovery.NativeIntegrityError(
                "Original native source was modified"
            ) from exc
        # Only generation-complete checkpoints can replay validation. Never re-run
        # upstream DROP/seed or codegen import against an existing database.
        if generation_ready and targets:
            native_recovery.save(
                checkpoint,
                expected,
                product_root,
                targets,
                resumable=not isinstance(exc, native_recovery.NativeIntegrityError),
                stage="validation-interrupted",
            )
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        atomic_text(
            reports / "failure.log",
            f"{type(exc).__name__} at {Path(frame.filename).name}:{frame.lineno} ({frame.name}): {exc}\n"
            + getattr(exc, "log", ""),
        )
        raise
````
