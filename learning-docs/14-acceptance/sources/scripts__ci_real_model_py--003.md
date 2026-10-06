# scripts/ci_real_model.py · 3/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](scripts__ci_real_model_py--002.md)

**作用：显式授权的真实模型完整验收。** 可信客服分支的手动任务在rnd中将APK_KEY映射为API_KEY，三个模板各自先Hello再校验同提交同attempt回执。完整需求由原文、默认决策和命名约定构成；真实网页只一次初始智能推荐，随后必须READY、实际下载、新库HTTP/浏览器/重启；公开白名单状态及经过校验的合成页面截图，不输出密钥或模型原文。

**对应关系：** native-probe手动real_model=true+expected_sha，或real-model手动矩阵 → rnd job → ModelGateway真实请求 → 当前模板独立产品 → summary.json与合成PNG；工具矩阵和BLOCKED恢复另验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run_acceptance.failure_context`（L1560–L1607）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1562按`run_id is None`分支；L1564按`not result_path.is_symlink() and result_path.stat().st_size <= 4096`分支；L1580遍历`( ( "approved_plan_replay", lambda: preserve_approved_customer_pl…`。 调用`result_path.is_symlink`、`result_path.stat`、`json.loads(result_path.read_text(encoding="utf-8")).get`、`json.loads`、`result_path.read_text`、`approved_plan_artifact_directory`、`safe_workflow_details`、`type`、`preserve_approved_customer_plan`等。 返回路径：L1607的`details`。
- `verified_smoke_receipt`（L1760–L1776）：接收`path`、`config`、`env`。 控制顺序：L1763断言`saved["passed"] is True and saved["acceptance_scope"] == "smoke_only"`；L1764断言`saved["smoke"] == { "passed": True, "http_status": 200, "actual_provider_request": Tr…`；L1769断言`saved["actual_http_calls"] == 1 and saved["provider_statuses"] == [200]`；L1770断言`saved["model"] == config.model and saved["endpoint"] == config.base_url`；L1771断言`saved["run_identity"] == [ env.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTE…`；L1776抛异常，停止当前正常路径。 调用`json.loads`、`path.read_text`、`env.get`、`SafeFailure`。 返回路径：L1774的`saved["smoke"]`。
- `main`（L1779–L1869）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1814按`mode == "full"`分支；L1815遍历`("approved-plan-replay.json", "unapproved-design-contract.json")`；L1826按`mode == "smoke"`分支；L1837按`exc.status is not None`分支；L1839按`exc.details is not None`分支；L1856按`transport`分支；L1864按`config is not None`分支；L1868按`not result["passed"]`分支。后续分支沿下方源码相同行号继续阅读。 调用`argparse.ArgumentParser`、`parser.add_argument`、`parser.parse_args`、`trusted_dispatch`、`configuration`、`os.environ.pop`、`result.update`、`os.environ.get`、`(destination / filename).unlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `scripts/ci_real_model.py`；**本文件共有 3 段**。本段覆盖源文件 L1560–L1873。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13993`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/ci_real_model.py", "part": 3, "parts": 3, "encoding": "utf-8", "sha256": "2e06606292c1367f1eb2733e34f1f9f99c7d811ef469530baf8c34b479a5200a"} -->
````python
# scripts/ci_real_model.py
    def failure_context():
        nonlocal run_id
        if run_id is None:
            try:
                if not result_path.is_symlink() and result_path.stat().st_size <= 4096:
                    run_id = json.loads(result_path.read_text(encoding="utf-8")).get("run_id")
            except OSError, ValueError, TypeError, AttributeError:
                pass
        artifact_directory = approved_plan_artifact_directory(settings.data_dir, run_id, template)
        native_reports = artifact_directory if template != "python-basic" else None
        try:
            details = safe_workflow_details(
                application.state.store,
                run_id,
                traces,
                text_budget=diagnostic_text,
                native_reports=native_reports,
            )
        except Exception as diagnostic_error:
            details = {"diagnostic_error_type": type(diagnostic_error).__name__[:80]}
        for key, operation in (
            (
                "approved_plan_replay",
                lambda: preserve_approved_customer_plan(
                    artifact_directory,
                    ROOT / "reports/real-model/approved-plan-replay.json",
                    diagnostic_text,
                ),
            ),
            (
                "unapproved_design_replay",
                lambda: preserve_unapproved_design_contract(
                    application.state.store,
                    run_id,
                    ROOT / "reports/real-model/unapproved-design-contract.json",
                    diagnostic_text,
                    acceptance_failed=True,
                ),
            ),
        ):
            try:
                details[key] = operation()
            except Exception as diagnostic_error:
                details[key] = {
                    "status": "diagnostic_failed",
                    "error_type": type(diagnostic_error).__name__[:80],
                }
        return details

    try:
        for _ in range(150):
            if server.started:
                break
            time.sleep(0.1)
        else:
            raise SafeFailure("platform_start_failed")
        driver = directory / "browser.cjs"
        driver.write_text(BROWSER_DRIVER, encoding="utf-8")
        result_path, archive = directory / "browser-result.json", directory / "download.zip"
        cfg = directory / "browser-private.json"
        write_json(
            cfg,
            {
                "platform": f"http://127.0.0.1:{port}",
                "token": application.state.token,
                "requirement": customer_request(),
                "template": template,
                "frontend": selection.frontend,
                "database": selection.database,
                "download": str(archive),
                "result": str(result_path),
            },
        )
        module = os.environ.get(
            "PRODUCT_VERIFY_PLAYWRIGHT", str(ROOT / ".native/browser/node_modules/playwright")
        )
        acceptance_stage = "smart_delivery_browser"
        process = subprocess.run(
            ["node", str(driver), str(cfg), module],
            cwd=ROOT,
            env=clean_env({"PLAYWRIGHT_BROWSERS_PATH": "0"}),
            capture_output=True,
            timeout=6960,
            check=False,
        )
        if process.returncode or not result_path.is_file():
            last = next((s for s in reversed(transport.statuses) if s >= 400), None)
            run_id = None
            if result_path.is_file():
                run_id = json.loads(result_path.read_text(encoding="utf-8")).get("run_id")
            details = failure_context()
            raise SafeFailure("workflow_not_ready", last, details)
        acceptance_stage = "delivery_receipt"
        browser = json.loads(result_path.read_text(encoding="utf-8"))
        run_id = browser["run_id"]
        run = application.state.store.get_run(run_id)
        if run["status"] != "READY" or not run["auto_mode"] or not archive.is_file():
            raise SafeFailure("delivery_not_ready")
        if hashlib.sha256(archive.read_bytes()).hexdigest() != run["result"]["sha256"]:
            raise SafeFailure("download_integrity_failed")
        product = directory / "downloaded-product"
        acceptance_stage = "download_unpack"
        unpack(archive, product, template=template)
        acceptance_stage = "approved_contract"
        screenshot_dir = ROOT / "reports/real-model/screenshots"
        approved_requirement = application.state.store.latest_revision(
            browser["run_id"], "requirements"
        )["requirement"]
        if template == "python-basic":
            spec = json.loads((product / "approved-spec.json").read_text(encoding="utf-8"))
            require_customer_spec(spec, approved_requirement=approved_requirement)
            if not run["result"]["cleanroom"].get("passed"):
                raise SafeFailure("pipeline_cleanroom_failed")
            require_browser_evidence(product, run["result"]["cleanroom"])
            python = product_interpreter(product, settings)
            probe = directory / "downloaded-product-verification.json"
            acceptance_stage = "downloaded_python_runtime"
            run_probe(product, python, probe, settings, business_screenshots=screenshot_dir)
            evidence = json.loads(probe.read_text(encoding="utf-8"))
            require_browser_evidence(product, evidence)
            if evidence.get("passed") is not True or evidence.get("restart") is not True:
                raise SafeFailure("downloaded_cleanroom_failed")
        else:
            from workbench.portable import verify_native_delivery

            manifest = json.loads(
                (product / "deployment/manifest.json").read_text(encoding="utf-8")
            )
            require_customer_spec(manifest["plan"], approved_requirement=approved_requirement)
            acceptance_stage = "downloaded_native_runtime"
            evidence = verify_native_delivery(
                product,
                os.environ["NATIVE_TEST_DATABASE_URL"],
                directory / "downloaded-evidence",
                template=template,
            )
            if (
                evidence.get("passed") is not True
                or evidence.get("fresh_database") is not True
                or evidence.get("restart") is not True
                or evidence.get("restart_preserved_records") is not True
            ):
                raise SafeFailure("downloaded_cleanroom_failed")
            acceptance_stage = "screenshot_export"
            # Only allowlisted synthetic UI PNGs, never full logs, credentials or product archives.
            import shutil

            native_reports = settings.data_dir / "runs" / browser["run_id"] / "native-evidence"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            for screenshot in native_reports.rglob("*.png"):
                if screenshot.is_symlink() or screenshot.stat().st_size > 12_000_000:
                    raise SafeFailure("invalid_screenshot_artifact")
                if not re.fullmatch(r"[a-zA-Z0-9_-]+\.png", screenshot.name):
                    raise SafeFailure("invalid_screenshot_name")
                if not screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                    raise SafeFailure("invalid_screenshot_png")
                shutil.copyfile(screenshot, screenshot_dir / screenshot.name)
            if not list(screenshot_dir.glob("*.png")):
                raise SafeFailure("missing_native_screenshots")
        return {
            "passed": True,
            "real_model": True,
            "single_initial_smart_consent": True,
            "explicit_customer_obligations_preserved": True,
            "template": template,
            "ready": True,
            "ui_download": True,
            "download_hash_matches": True,
            "independent_database": True,
            "real_browser": True,
            "restart": True,
            "model_calls": run["model_calls"],
            "page_errors": browser["page_errors"],
            "aider_edit": "not_exercised",
            "continue_native_index": "not_exercised",
            "daytona": "not_exercised",
            "old_blocked_recovery": "not_exercised_in_real_run",
        }
    except Exception as error:
        # Collect while the private product and approval artifacts still exist.
        # Expected gates with existing detail retain their original explanation.
        if isinstance(error, SafeFailure) and error.details is not None:
            raise
        details = failure_context()
        details["execution"] = safe_execution_failure(
            error,
            acceptance_stage,
            DiagnosticTextBudget(secrets=(config.key.get_secret_value(),), limit=1000),
        )
        if isinstance(error, SafeFailure) and hasattr(error, "guard_code"):
            details["customer_guard"] = {"code": error.guard_code}
        if isinstance(error, SafeFailure):
            error.details = details
            raise
        raise SafeFailure("acceptance_execution_failed", details=details) from None
    finally:
        server.should_exit = True
        thread.join(timeout=120)


def verified_smoke_receipt(path, config, env):
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        assert saved["passed"] is True and saved["acceptance_scope"] == "smoke_only"
        assert saved["smoke"] == {
            "passed": True,
            "http_status": 200,
            "actual_provider_request": True,
        }
        assert saved["actual_http_calls"] == 1 and saved["provider_statuses"] == [200]
        assert saved["model"] == config.model and saved["endpoint"] == config.base_url
        assert saved["run_identity"] == [
            env.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
        ]
        return saved["smoke"]
    except OSError, ValueError, KeyError, AssertionError, TypeError:
        raise SafeFailure("missing_matching_successful_smoke") from None


def main():
    import argparse

    from workbench.settings import ROOT

    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "full"], required=True)
    parser.add_argument(
        "--template", choices=["python-basic", "fastapiadmin", "yudao-vben"], default="python-basic"
    )
    args = parser.parse_args()
    mode = args.phase
    destination = ROOT / "reports/real-model"
    summary = destination / "summary.json"
    result = {
        "passed": False,
        "real_provider_attempted": False,
        "acceptance_scope": "smoke_only" if mode == "smoke" else "full_workflow",
    }
    transport = None
    config = None
    phase = "configuration"
    prior_calls = 0
    try:
        trusted_dispatch(os.environ)
        config = configuration(os.environ)
        # Never inherit the provider credential into browser/uv/product child processes.
        os.environ.pop("API_KEY", None)
        result.update(
            model=config.model,
            endpoint=config.base_url,
            run_identity=[
                os.environ.get(k, "") for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_SHA")
            ],
        )
        if mode == "full":
            for filename in ("approved-plan-replay.json", "unapproved-design-contract.json"):
                (destination / filename).unlink(missing_ok=True)
            result["smoke"] = verified_smoke_receipt(summary, config, os.environ)
            prior_calls = 1
        transport = BoundedRealTransport(config)
        with tempfile.TemporaryDirectory(prefix="rnd-real-model-") as private:
            # Suppress raw application/provider tracebacks and model-generated text.
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as quiet:
                logging.disable(logging.CRITICAL)
                with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
                    result["real_provider_attempted"] = True
                    if mode == "smoke":
                        phase = "smoke"
                        result["smoke"] = smoke(config, transport)
                    else:
                        phase = "workflow"
                        result["workflow"] = run_acceptance(
                            config, transport, Path(private), args.template
                        )
        result["passed"] = True
    except SafeFailure as exc:
        result.update(failure_phase=phase, failure_code=exc.code)
        if exc.status is not None:
            result["provider_status"] = exc.status
        if exc.details is not None:
            result["configuration_checks" if "configuration" in exc.code else "failure_details"] = (
                exc.details
            )
    except Exception as error:
        budget = DiagnosticTextBudget(
            secrets=(config.key.get_secret_value(),)
            if config
            else (os.environ.get("API_KEY", ""),),
            limit=1000,
        )
        result.update(
            failure_phase=phase,
            failure_code="acceptance_execution_failed",
            failure_details={"execution": safe_execution_failure(error, phase, budget)},
        )
    finally:
        if transport:
            result["actual_http_calls"] = prior_calls + transport.calls
            result["provider_statuses"] = ([200] if prior_calls else []) + transport.statuses
            result["provider_receipts"] = transport.receipts
            with contextlib.suppress(Exception):
                transport.shutdown()
        destination.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(result, indent=2)
        if config is not None:
            rendered = rendered.replace(config.key.get_secret_value(), "[REDACTED]")
        summary.write_text(rendered, encoding="utf-8")
    print(rendered)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
````
