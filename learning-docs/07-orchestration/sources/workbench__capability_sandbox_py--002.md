# workbench/capability_sandbox.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__capability_sandbox_py--001.md)

**作用：项目根配置或说明。** 按文件名原样保存到项目根目录；点号开头的文件也是实际文件。Python代码读取.env，uv读取pyproject及锁，Git读取忽略/换行规则，Alembic读取迁移配置；各文件不是任意替换关系。

**对应关系：** 先按正文准备基础文件，再安装依赖；README是演示入口，完整实现路径在本教材。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_contracts`、`workbench.capability_isolation`、`workbench.capability_stack`、`workbench.capability_verification`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.local_only`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_verify`（L397–L973）：接收`product`、`plan`、`scenarios`、`settings`、`selection`、`receipt_path`、`client`、`aggregate`、`control_observer`、`security_probe`、`trusted_oracle`、`profile_record`。 控制顺序：L433按`trusted_oracle not in (None, "contest-business-v2")`分支；L434抛异常，停止当前正常路径；L435按`trusted_oracle and ( not aggregate or selection["template"] != "fastapiadmin" or secu…`分支；L438抛异常，停止当前正常路径；L441按`selection != plan.selection.model_dump() or selection not in ( Selection(template="py…`分支；L445抛异常，停止当前正常路径；L446按`not isinstance(profile_record, dict) or profile_record.get("selection", Selection(tem…`分支；L451抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`write_json`、`CheckFailure`、`plan.selection.model_dump`、`Selection(template="python-basic").model_dump`、`Selection`、`Selection(template="fastapiadmin").model_dump`、`isinstance`、`profile_record.get`、`require_dependency_descriptors`等。 返回路径：L973的`receipt`。
- `_verify.start`（L591–L742）：接收`command`、`port`、`health_path`。 控制顺序：L595按`target["role"] == "backend"`分支；L626按`not response.cmd_id`分支；L627抛异常，停止当前正常路径；L630按`not isinstance(preview.token, str) or not preview.token`分支；L631抛异常，停止当前正常路径；L643在`time.monotonic() < deadline`成立时循环；L647按`200 <= check.status_code < 300`分支；L648按`target["role"] == "backend"`分支。后续分支沿下方源码相同行号继续阅读。 调用`startup_target`、`require_preinstalled_evidence`、`verify_readonly_dependencies`、`uuid.uuid4`、`sandbox.process.create_session`、`redirected_command`、`product_argv`、`sandbox.process.execute_session_command`、`SessionExecuteRequest`等。 返回路径：L650的`http, url, preview.token`。
- `main`（L976–L1021）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L978按`len(body) > 1_000_000`分支；L979抛异常，停止当前正常路径；L988按`len(scenarios) != len(payload["scenario_ids"]) or not scenarios or type(payload["aggr…`分支；L994抛异常，停止当前正常路径。 调用`sys.stdin.buffer.read`、`len`、`ValueError`、`json.loads`、`install_loopback_guard`、`Settings`、`CapabilityPlan.model_validate`、`type`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/capability_sandbox.py`；**本文件共有 2 段**。本段覆盖源文件 L397–L1025。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28913`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/capability_sandbox.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "aa123a2e3967006ef2ce8a079a5bf4dc3b054f66f9f4c2b970a698dd47920b97"} -->
````python
# workbench/capability_sandbox.py
def _verify(
    product,
    plan,
    scenarios,
    settings,
    selection,
    receipt_path,
    *,
    client,
    aggregate,
    control_observer=None,
    security_probe=None,
    trusted_oracle=None,
    profile_record=None,
):
    from daytona import SessionExecuteRequest

    from workbench.capability_dependencies import (
        prepare_readonly_dependencies,
        readonly_prepare_commands,
        readonly_start_command,
        require_dependency_descriptors,
        verify_readonly_dependencies,
    )
    from workbench.capability_execution import (
        VERIFIER,
        require_preinstalled_evidence,
        require_profile_container_binding,
    )
    from workbench.catalog import Selection
    from workbench.daytona_sessions import run_session_command
    from workbench.sandbox import params_for, source_archive

    # Even a direct caller rejected during admission must not leave a prior
    # successful receipt available at the requested output path.
    write_json(receipt_path, {"passed": False, "cleanup": "not-created", "verifier": VERIFIER})
    if trusted_oracle not in (None, "contest-business-v2"):
        raise CheckFailure("未知控制端业务oracle，拒绝候选自定义验证器")
    if trusted_oracle and (
        not aggregate or selection["template"] != "fastapiadmin" or security_probe is None
    ):
        raise CheckFailure("独立竞赛oracle必须使用原生完整隔离验收")
    # This boundary is shared by production and certification callers. Neither
    # direct calls nor a missing outer CLI preflight can waive exact provenance.
    if selection != plan.selection.model_dump() or selection not in (
        Selection(template="python-basic").model_dump(),
        Selection(template="fastapiadmin").model_dump(),
    ):
        raise CheckFailure("隔离验证的技术栈与已批准计划或登记的只读依赖profile不一致")
    if (
        not isinstance(profile_record, dict)
        or profile_record.get("selection", Selection(template="python-basic").model_dump())
        != selection
    ):
        raise CheckFailure("只读依赖镜像profile没有绑定当前技术栈")
    require_dependency_descriptors(product, plan, profile_record)
    commands = readonly_prepare_commands(plan)
    readonly_start_command(plan)
    dependency_profile = profile_record["snapshot"]["dependency_manifest"]
    before = manifest(product)
    native = selection["template"] == "fastapiadmin"
    prefix = "rnd-source-native-" if native else "rnd-source-"
    name = (prefix if security_probe is not None else "rnd-capability-") + uuid.uuid4().hex
    receipt = {
        "verifier": VERIFIER,
        "dependency_profile": dependency_profile,
        "passed": False,
        "source_digest": digest(before),
        "plan_digest": digest(plan.model_dump()),
        "network_block_all": True,
        "credentials_uploaded": False,
        "scope": "aggregate" if aggregate else "node",
        "checks": [],
        "sandbox_name": name,
        "cleanup": "not-created",
        "restarted": False,
        "stack": inspect_stack(product, plan),
    }
    write_json(receipt_path, receipt)
    sandbox = None
    oracle_adapter = None
    try:
        parameters = params_for(settings, name, selection["template"], selection)
        parameters.os_user = "root"
        if aggregate:
            # SDK 0.190.0 uses 0 for delete-on-stop, so the ordinary disposable
            # policy destroys the database before aggregate restart acceptance.
            # Keep only this owned sandbox for a finite stop/start window; the
            # mandatory finally deletion and all isolation gates still apply.
            parameters.auto_delete_interval = (2 * settings.tool_timeout + 59) // 60 + 1
        sandbox = client.create(parameters, timeout=settings.tool_timeout)
        receipt.update(sandbox_id=sandbox.id, cleanup="pending")
        write_json(receipt_path, receipt)
        if security_probe is not None:
            sandbox.refresh_data()
            if sandbox.network_block_all is not True or sandbox.public is not False:
                raise IsolationUnavailable("实际沙箱未确认私有且禁止网络出口，未上传或执行源码")
        if control_observer is None:
            raise IsolationUnavailable("缺少可信控制面的实际容器检查，未上传或执行源码")
        try:
            receipt["container_isolation"] = require_container_evidence(
                control_observer(sandbox.id), sandbox.id
            )
            require_profile_container_binding(profile_record, receipt["container_isolation"])
            if native and receipt["container_isolation"].get("profile") != (
                "native-fastapiadmin-postgresql-v1"
            ):
                raise ValueError("Native execution requires its exact container profile")
        except ContainerInspectionRejected as exc:
            raise IsolationUnavailable(
                "实际容器不符合已批准的非特权策略，未上传或执行源码",
                evidence=ContainerInspectionRejected.diagnostic(exc),
            ) from None
        except ValueError:
            raise IsolationUnavailable(
                "实际容器不符合已批准的非特权策略，未上传或执行源码"
            ) from None
        write_json(receipt_path, receipt)
        sandbox.fs.create_folder(REMOTE, "700")
        sandbox.fs.upload_file(
            source_archive(product), REMOTE + "/source.zip", timeout=settings.tool_timeout
        )
        result = control_exec(
            sandbox,
            ["/usr/bin/python3", "-I", "-S", "-m", "zipfile", "-e", REMOTE + "/source.zip", REMOTE],
            settings.tool_timeout,
        )
        if result.exit_code != 0:
            raise CheckFailure("自定义产品源码解压失败")
        identity_options = {"native_semaphore_storage": True} if native else {}
        receipt["execution_isolation"] = prepare_identity(
            sandbox, plan, settings.tool_timeout, **identity_options
        )
        receipt["preinstalled_dependencies"] = require_preinstalled_evidence(
            prepare_readonly_dependencies(
                sandbox,
                plan,
                settings.tool_timeout,
                expected=dependency_profile,
                source_inventory=before,
            ),
            dependency_profile,
            source_digest=receipt["source_digest"],
        )
        database_password = prepare_database(sandbox, plan, settings.tool_timeout)
        if database_password:
            with settings._model_keys_lock:
                settings._model_keys.add(database_password)
        from workbench.capability_services import prepare_native_services

        services = prepare_native_services(sandbox, plan, settings.tool_timeout)
        if services:
            with settings._model_keys_lock:
                settings._model_keys.update(services.values())
        database = database_environment(plan, database_password, services)
        if trusted_oracle:
            from workbench.capability_stack import owned_database_identity

            oracle_database_ownership = owned_database_identity(sandbox, settings.tool_timeout)
        if security_probe is not None:
            receipt["security_checks"] = security_probe(
                sandbox, plan, settings.tool_timeout, receipt["container_isolation"], database
            )
        for index, command in enumerate(commands):
            evidence = {}
            guarded_command, command_output = redirected_command(
                product_argv(plan, command.argv, database, **identity_options)
            )
            result = run_session_command(
                sandbox.process,
                guarded_command,
                REMOTE + "/product/" + command.cwd,
                settings.tool_timeout,
                evidence,
            )
            if result.exit_code != 0:
                receipt["build_diagnostic"] = settings.redact(
                    read_command_output(sandbox, command_output, settings.tool_timeout)
                )[-4000:]
                raise CheckFailure(f"第 {index + 1} 个隔离准备/构建命令失败；检查节点构建诊断")
        if native:
            from workbench.capability_native_runtime import verify_and_freeze_native_sources

            restart_application_identity(
                sandbox, plan.runtime.port, settings.tool_timeout, extra_ports=(5173,)
            )
            verify_and_freeze_native_sources(sandbox, before, settings.tool_timeout)
            receipt["native_build"] = {
                "preinstalled_dependencies_verified": True,
                "frontend_build": True,
                "frontend_typecheck": True,
                "source_frozen": True,
            }

        def start(command=None, port=None, health_path=None):
            from workbench.capability_startup_paths import startup_target

            command, target = startup_target(plan, command, port, health_path)
            if target["role"] == "backend":
                receipt["backend_health_observed"] = False
            require_preinstalled_evidence(
                verify_readonly_dependencies(
                    sandbox,
                    plan,
                    settings.tool_timeout,
                    expected=dependency_profile,
                    source_inventory=before,
                ),
                dependency_profile,
                source_digest=receipt["source_digest"],
            )
            port = target["port"]
            health_path = "/" if target["role"] == "frontend" else plan.runtime.health_path
            session = "rnd-app-" + uuid.uuid4().hex
            sandbox.process.create_session(session)
            guarded_command, command_output = redirected_command(
                product_argv(plan, command.argv, database, **identity_options)
            )
            response = sandbox.process.execute_session_command(
                session,
                SessionExecuteRequest(
                    command="cd "
                    + shlex.quote(REMOTE + "/product/" + command.cwd)
                    + " && "
                    + shlex.join(guarded_command),
                    run_async=True,
                ),
                timeout=settings.tool_timeout,
            )
            if not response.cmd_id:
                raise CheckFailure("隔离应用启动未返回命令标识")
            preview = sandbox.get_preview_link(port)
            url = preview_url(preview.url, sandbox.id, port)
            if not isinstance(preview.token, str) or not preview.token:
                raise CheckFailure("私有隔离预览缺少授权标识")
            # The pinned local proxy consumes/strips this token before forwarding.
            http = httpx.Client(
                base_url=url,
                headers={"x-daytona-preview-token": preview.token},
                timeout=15,
                follow_redirects=False,
                trust_env=False,
            )
            try:
                deadline = time.monotonic() + plan.runtime.startup_seconds
                last_http_status, last_http_error = None, "none"
                while time.monotonic() < deadline:
                    try:
                        with http.stream("GET", health_path) as check:
                            last_http_status, last_http_error = check.status_code, "none"
                            if 200 <= check.status_code < 300:
                                if target["role"] == "backend":
                                    receipt["backend_health_observed"] = True
                                return http, url, preview.token
                    except httpx.HTTPError as exc:
                        last_http_error = (
                            "timeout"
                            if isinstance(exc, httpx.TimeoutException)
                            else "connect"
                            if isinstance(exc, httpx.ConnectError)
                            else "protocol"
                            if isinstance(exc, httpx.ProtocolError)
                            else "other"
                        )
                    time.sleep(0.2)
                try:
                    from workbench.capability_startup_paths import NATIVE_TAIL_LIMIT

                    startup_output = read_command_output(
                        sandbox,
                        command_output,
                        min(settings.tool_timeout, 5),
                        limit=NATIVE_TAIL_LIMIT if native else 8000,
                        tail=True,
                    )
                except Exception:
                    startup_output = None
                tmpfs_noexec = None
                try:
                    mode = control_exec(
                        sandbox,
                        [
                            "/usr/bin/python3",
                            "-I",
                            "-S",
                            "-c",
                            "import os; print(int(bool(os.statvfs('/tmp').f_flag & os.ST_NOEXEC)))",
                        ],
                        min(settings.tool_timeout, 5),
                    )
                    value = mode.result.strip() if type(mode.result) is str else ""
                    if type(mode.exit_code) is int and mode.exit_code == 0 and value in {"0", "1"}:
                        tmpfs_noexec = value == "1"
                except Exception:
                    pass
                receipt["startup_diagnostic"] = startup_failure_diagnostic(
                    startup_output,
                    last_http_status,
                    last_http_error,
                    tmpfs_noexec,
                    **startup_command_exit_facts(
                        sandbox.process, session, response.cmd_id, min(settings.tool_timeout, 5)
                    ),
                    output_limit=NATIVE_TAIL_LIMIT if native else 8000,
                )
                receipt["startup_diagnostic"]["target"] = {
                    **target,
                    "backend_health_observed": receipt.get("backend_health_observed") is True,
                }
                if target["role"] == "frontend":
                    from workbench.capability_startup_paths import node_failure_facts

                    receipt["startup_diagnostic"]["node_error"] = node_failure_facts(startup_output)
                if native:
                    from workbench.capability_startup_paths import (
                        native_startup_paths,
                        native_startup_smoke,
                    )

                    receipt["startup_diagnostic"]["launch_paths"] = {"status": "unknown"}
                    receipt["startup_diagnostic"]["interpreter_probe"] = {
                        "exit_status": "unknown",
                        "output_shapes": [],
                        "checks": None,
                    }
                    try:
                        receipt["startup_diagnostic"]["launch_paths"] = native_startup_paths(
                            sandbox, min(settings.tool_timeout, 5), role=target["role"]
                        )
                    except Exception:
                        pass
                    try:
                        receipt["startup_diagnostic"]["interpreter_probe"] = native_startup_smoke(
                            sandbox,
                            plan,
                            database,
                            identity_options,
                            min(settings.tool_timeout, 5),
                            role=target["role"],
                        )
                    except Exception:
                        pass
                raise CheckFailure("隔离应用未在约定时间内通过健康检查")
            except BaseException:
                http.close()
                raise

        http, url, token = start()
        browser_url, browser_token = url, token
        # The health request already opened this client; entering it again is
        # invalid. Own its close even when the independent baseline probe fails.
        with closing(http):
            if native:
                from workbench.capability_native_runtime import (
                    FRONTEND_PORT,
                    frontend_start_command,
                )

                frontend_http, browser_url, browser_token = start(
                    frontend_start_command(), FRONTEND_PORT, "/"
                )
                frontend_http.close()
                receipt["native_frontend_started"] = True
            baseline_counts = database_counts(sandbox, plan, settings.tool_timeout)
            if plan.selection.backend in {"fastapi", "fastapiadmin"}:
                with http.stream("GET", "/openapi.json") as response:
                    if response.status_code != 200:
                        raise CheckFailure("实际运行服务没有FastAPI OpenAPI契约，拒绝技术栈替换")
            if trusted_oracle:
                from scripts.extension_oracles import contest
                from workbench.capability_contest_oracle import ContestOracleAdapter

                oracle_adapter = ContestOracleAdapter(url, token, sandbox, settings.tool_timeout)
                oracle_state, oracle_witnesses = contest.initial(
                    oracle_adapter.http,
                    oracle_adapter.probe,
                    oracle_adapter.actor_ids,
                    uuid.uuid4().hex,
                )
                receipt["business_oracle"] = {
                    "protocol": trusted_oracle,
                    "witnesses": oracle_witnesses,
                    "full_request_complete": False,
                    "remaining_obligations": list(contest.REMAINING),
                }
            checks, saved = run_scenarios(http, scenarios)
            receipt["checks"].extend(checks)
        if security_probe is not None:
            from workbench.capability_browser_isolation import run_isolated_browser

            receipt["browser"] = run_isolated_browser(
                browser_url,
                browser_token,
                scenarios,
                saved,
                settings.tool_timeout,
                image=settings.capability_browser_image,
            )
            receipt["browser_image"] = settings.capability_browser_image
        else:
            receipt["browser"] = run_browser(url, token, scenarios, saved, settings.tool_timeout)
        counts = database_counts(sandbox, plan, settings.tool_timeout)
        if not any(counts[name] > baseline_counts[name] for name in counts):
            raise CheckFailure(
                "独立物理数据库探针未观察到验收请求写入的数据；静态响应不能替代持久化"
            )
        receipt["database"] = {
            "engine": plan.selection.database,
            "baseline": baseline_counts,
            "after": counts,
            "observed_writes": True,
        }
        if aggregate:
            if security_probe is not None:
                restart_application_identity(
                    sandbox,
                    plan.runtime.port,
                    settings.tool_timeout,
                    extra_ports=(5173,) if native else (),
                )
                receipt["restart_kind"] = "application_process"
            else:
                client.stop(sandbox, timeout=settings.tool_timeout)
                client.start(sandbox, timeout=settings.tool_timeout)
                receipt["restart_kind"] = "container"
            if security_probe is not None:
                restarted_container = require_container_evidence(
                    control_observer(sandbox.id), sandbox.id
                )
                require_profile_container_binding(profile_record, restarted_container)
                receipt["restart_preinstalled_dependencies"] = require_preinstalled_evidence(
                    verify_readonly_dependencies(
                        sandbox,
                        plan,
                        settings.tool_timeout,
                        expected=dependency_profile,
                        source_inventory=before,
                    ),
                    dependency_profile,
                    source_digest=receipt["source_digest"],
                )
                receipt["restart_security_checks"] = security_probe(
                    sandbox, plan, settings.tool_timeout, restarted_container, database
                )
            if security_probe is None:
                receipt["restart_preinstalled_dependencies"] = require_preinstalled_evidence(
                    verify_readonly_dependencies(
                        sandbox,
                        plan,
                        settings.tool_timeout,
                        expected=dependency_profile,
                        source_inventory=before,
                    ),
                    dependency_profile,
                    source_digest=receipt["source_digest"],
                )
                prepare_database(
                    sandbox, plan, settings.tool_timeout, restart=True, password=database_password
                )
            http, _, _ = start()
            with closing(http):
                if native:
                    frontend_http, _, _ = start(frontend_start_command(), FRONTEND_PORT, "/")
                    frontend_http.close()
                    receipt["native_frontend_restart"] = True
                if trusted_oracle:
                    oracle_witnesses.update(
                        contest.after_restart(
                            oracle_adapter.http,
                            oracle_adapter.probe,
                            oracle_state,
                            uuid.uuid4().hex,
                        )
                    )
                checks, _ = run_scenarios(http, scenarios, saved=saved, after_restart=True)
                receipt["checks"].extend(checks)
            receipt["restarted"] = True
            restarted = database_counts(sandbox, plan, settings.tool_timeout)
            if any(restarted[name] < counts[name] for name in counts):
                raise CheckFailure("独立数据库重启后丢失已写入的记录")
            receipt["database"]["after_restart"] = restarted
            if trusted_oracle:
                from workbench.capability_stack import recreate_owned_native_database

                oracle_adapter.close()
                fresh_identity = recreate_owned_native_database(
                    sandbox, plan, settings.tool_timeout, oracle_database_ownership
                )
                from workbench.capability_services import reset_owned_native_cache

                reset_owned_native_cache(sandbox, settings.tool_timeout)
                http, url, token = start()
                http.close()
                frontend_http, _, _ = start(frontend_start_command(), FRONTEND_PORT, "/")
                frontend_http.close()
                oracle_adapter = ContestOracleAdapter(url, token, sandbox, settings.tool_timeout)
                oracle_witnesses.update(contest.fresh_database(oracle_adapter.probe, oracle_state))
                _, replay = contest.initial(
                    oracle_adapter.http,
                    oracle_adapter.probe,
                    oracle_adapter.actor_ids,
                    uuid.uuid4().hex,
                )
                if not all(replay.get(name) is True for name in contest.SEMANTICS[:5]):
                    raise CheckFailure("新库业务请求重放未通过")
                oracle_adapter.close()
                receipt["business_oracle"].update(
                    witnesses=oracle_witnesses,
                    fresh_replay=True,
                    same_cluster=oracle_database_ownership["cluster"] == fresh_identity["cluster"],
                    distinct_database_oid=oracle_database_ownership["database_oid"]
                    != fresh_identity["database_oid"],
                )
        # Drain candidate processes before the final exact tree/link inventory;
        # a successful live response cannot hide additional executable modules.
        restart_application_identity(
            sandbox,
            plan.runtime.port,
            settings.tool_timeout,
            extra_ports=(5173,) if native else (),
        )
        receipt["final_preinstalled_dependencies"] = require_preinstalled_evidence(
            verify_readonly_dependencies(
                sandbox,
                plan,
                settings.tool_timeout,
                expected=dependency_profile,
                source_inventory=before,
            ),
            dependency_profile,
            source_digest=receipt["source_digest"],
        )
        if manifest(product) != before:
            raise CheckFailure("隔离验收期间宿主源码发生变化")
        receipt["passed"] = True
    except IsolationUnavailable as exc:
        receipt.update(kind="isolation_environment", error=str(exc))
        receipt["isolation_diagnostic"] = exc.evidence
    except CheckFailure as exc:
        receipt["error"] = str(exc)
        receipt["failed_scenario"] = getattr(exc, "scenario_id", None)
        if native:
            from scripts.capability_native_shm_probe import native_shm_cleanup_diagnostic

            cleanup_diagnostic = native_shm_cleanup_diagnostic(exc)
            if cleanup_diagnostic:
                receipt["native_shm_cleanup_diagnostic"] = cleanup_diagnostic
        if isinstance(exc, BrowserFailure):
            receipt["browser_diagnostic"] = exc.diagnostic
    except Exception as exc:
        receipt["error"] = (
            "本机隔离服务未完成验收（" + type(exc).__name__ + "），未使用本机执行回退"
        )
    finally:
        if oracle_adapter is not None:
            try:
                oracle_adapter.close()
            except Exception:
                receipt.update(passed=False, error="可信业务验证器连接清理失败")
        if sandbox is None:
            receipt["cleanup"] = "create-failed-unknown"
            try:
                sandbox = client.get(name)
            except Exception:
                pass
        if sandbox is not None:
            try:
                client.delete(sandbox, timeout=settings.tool_timeout)
                receipt["cleanup"] = "deleted"
            except Exception:
                receipt.update(cleanup="delete-failed", passed=False)
                receipt["cleanup_error"] = "本机隔离沙箱删除未确认；请按回执名称检查，交付已停止"
                receipt.setdefault("error", receipt["cleanup_error"])
        if receipt["cleanup"] != "deleted":
            receipt["passed"] = False
        write_json(receipt_path, receipt)
    return receipt


def main():
    body = sys.stdin.buffer.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError("自定义验收控制契约过大")
    payload = json.loads(body)
    install_loopback_guard()
    from workbench.sandbox import client_for, close_client
    from workbench.settings import Settings

    settings = Settings(_env_file=None, **payload["settings"])
    plan = CapabilityPlan.model_validate(payload["plan"])
    scenarios = [s for s in plan.scenarios if s.id in payload["scenario_ids"]]
    if (
        len(scenarios) != len(payload["scenario_ids"])
        or not scenarios
        or type(payload["aggregate"]) is not bool
        or payload["selection"] != plan.selection.model_dump()
    ):
        raise ValueError("自定义验证输入未绑定准确场景、技术栈或验收模式")
    from scripts.capability_security_probe import security_probe_for_profile
    from scripts.daytona_capability_profile import inspect_created_sandbox
    from workbench.capability_execution import capability_execution_prerequisites

    directory, record = capability_execution_prerequisites(settings, payload["selection"])
    client = client_for(settings)
    try:
        _verify(
            Path(payload["product"]),
            plan,
            scenarios,
            settings,
            payload["selection"],
            Path(payload["receipt"]),
            client=client,
            aggregate=payload["aggregate"],
            control_observer=lambda sandbox_id: inspect_created_sandbox(
                directory, sandbox_id, require_resources=True, selection=payload["selection"]
            ),
            security_probe=security_probe_for_profile(
                directory, record, client=client, settings=settings
            ),
            trusted_oracle=payload.get("trusted_oracle"),
            profile_record=record,
        )
    finally:
        close_client(client)


if __name__ == "__main__":
    main()
````
