# tests/test_capability_startup_paths.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `helpers`（L19–L29）：接收`loader`。 调用`ast.parse`、`ast.Module`、`isinstance`、`SimpleNamespace`、`vars`、`getattr`、`str`、`exec`、`compile`。 返回路径：L29的`scope`。
- `elf`（L32–L41）：接收`loader`。 调用`bytearray`、`struct.pack_into`、`len`。 返回路径：L41的`data`。
- `test_missing_regular_directory_and_dangling_link`（L44–L62）：接收`tmp_path`。 控制顺序：L48断言`inspect(str(path))["entry"] == "missing"`；L50断言`inspect(str(path))["target"] == "regular"`；L51断言`inspect(str(tmp_path))["target"] == "directory"`；L57断言`inspect(str(link))["entry"] == "symlink"`；L58断言`inspect(str(link))["target"] == "regular"`；L61断言`value["entry"] == "symlink" and value["target"] == "missing"`；L62断言`"private-sentinel" not in json.dumps(value)`。 调用`helpers`、`inspect`、`str`、`path.write_bytes`、`link.symlink_to`、`pytest.skip`、`path.unlink`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_app_dac_does_not_use_root_access`（L66–L75）：接收`tmp_path`。 控制顺序：L74断言`result["dac_read"] is False and result["dac_exec"] is False`；L75断言`file.read_bytes() == b"inert" if os.geteuid() == 0 else True`。 调用`base.mkdir`、`file.write_bytes`、`file.chmod`、`helpers(base / "loader")["inspect"]`、`helpers`、`str`、`os.geteuid`、`file.read_bytes`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_elf_header_reports_only_fixed_loader_state`（L79–L86）：接收`tmp_path`、`present`。 控制顺序：L81按`present`分支；L86断言`result == {"format": "elf", "loader": "present" if present else "missing"}`。 调用`loader.write_bytes`、`program.write_bytes`、`elf`、`helpers(loader)["executable_format"]`、`helpers`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_binary_and_shebang_never_expose_content`（L98–L103）：接收`tmp_path`、`data`、`kind`、`loader`。 控制顺序：L102断言`result == {"format": kind, "loader": loader}`；L103断言`"private" not in json.dumps(result)`。 调用`program.write_bytes`、`helpers(tmp_path / "loader")["executable_format"]`、`helpers`、`str`、`json.dumps`、`pytest.mark.parametrize`、`elf`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_elf_program_header_outside_read_budget_is_unknown`（L106–L114）：接收`tmp_path`。 控制顺序：L111断言`helpers(tmp_path / "loader")["executable_format"](str(program)) == { "format": "elf",…`。 调用`elf`、`bytearray`、`struct.pack_into`、`program.write_bytes`、`helpers(tmp_path / "loader")["executable_format"]`、`helpers`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fifo_is_never_read_and_descriptor_is_closed`（L118–L135）：接收`tmp_path`。 控制顺序：L132断言`scope["executable_format"](str(fifo)) == {"format": "unknown", "loader": "unknown"}`；L133断言`len(descriptors) == 1`。 调用`os.mkfifo`、`helpers`、`pytest.fail`、`scope["executable_format"]`、`str`、`len`、`pytest.raises`、`os.fstat`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fifo_is_never_read_and_descriptor_is_closed.open_fd`（L125–L128）：接收`*args`。 调用`opened`、`descriptors.append`。 返回路径：L128的`fd`。
- `receipt`（L138–L145）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L139的`{ "paths": { name: {"entry": "regular", "target": "regular", "dac_read": True, "dac_exec":…`。
- `test_controller_requests_only_fixed_program_and_bounds_output`（L148–L157）：接收`monkeypatch`。 控制顺序：L156断言`diagnostic.native_startup_paths(object(), 5) == {"status": "observed", **receipt()}`；L157断言`calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.PROBE], 5)]`。 调用`monkeypatch.setattr`、`diagnostic.native_startup_paths`、`object`、`receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_controller_requests_only_fixed_program_and_bounds_output.execute`（L151–L153）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`、`receipt`。 返回路径：L153的`SimpleNamespace(exit_code=0, result=json.dumps(receipt()))`。
- `test_malformed_receipt_is_unknown`（L173–L181）：接收`monkeypatch`、`mutate`。 控制顺序：L181断言`diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}`。 调用`copy.deepcopy`、`receipt`、`mutate`、`monkeypatch.setattr`、`SimpleNamespace`、`json.dumps`、`diagnostic.native_startup_paths`、`object`、`pytest.mark.parametrize`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_or_oversize_probe_never_serializes_output`（L187–L191）：接收`monkeypatch`、`code`、`output`。 控制顺序：L191断言`diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`diagnostic.native_startup_paths`、`object`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_output_format_classification_never_copies_content`（L215–L217）：接收`text`、`expected`。 控制顺序：L216断言`diagnostic.output_shapes(text) == expected`；L217断言`diagnostic.output_shapes("x" * 8000 + (text or "")) == []`。 调用`diagnostic.output_shapes`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `native_plan`（L220–L224）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`。 返回路径：L221的`SimpleNamespace( selection=SimpleNamespace(template="fastapiadmin", database="postgresql")…`。
- `smoke_checks`（L227–L228）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`dict.fromkeys`。 返回路径：L228的`dict.fromkeys(("version_matches", "executable_matches", "cwd_matches", "isolated"), True)`。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget`（L231–L271）：接收`monkeypatch`。 控制顺序：L270断言`result == {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}`；L271断言`"private-sentinel" not in json.dumps(result)`。 调用`monkeypatch.setattr`、`native_plan`、`diagnostic.product_argv`、`diagnostic.native_startup_smoke`、`object`、`smoke_checks`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget.execute`（L250–L260）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L251断言`timeout == 5`；L252断言`argv[:2] == ["/bin/sh", "-c"]`；L253断言`argv[2].startswith("cd /tmp/rnd-capability/product/backend && ")`；L255断言`inner[:2] == ["/bin/sh", "-c"]`；L257断言`launcher == ["exec", *expected]`；L258断言`"--native-shm" in launcher and "--reuid=rnd-module" in launcher`。 调用`argv[2].startswith`、`shlex.split`、`argv[2].split`、`inner[2].split`、`SimpleNamespace`。 返回路径：L260的`SimpleNamespace(exit_code=0)`。
- `test_smoke_uses_original_guard_and_env_with_shared_five_second_budget.read`（L262–L265）：接收`sandbox`、`path`、`timeout`、`limit`、`tail`。 控制顺序：L263断言`timeout == 1 and limit == 512 and tail is True`；L264断言`path.startswith("/tmp/rnd-module-control/private/")`。 调用`path.startswith`、`json.dumps`、`smoke_checks`。 返回路径：L265的`json.dumps(smoke_checks())`。
- `test_smoke_failure_and_corrupt_output_are_finite`（L286–L293）：接收`monkeypatch`、`code`、`output`、`expected`。 控制顺序：L292断言`result["exit_status"] == expected and result["checks"] is None`；L293断言`"private-sentinel" not in json.dumps(result)`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`diagnostic.native_startup_smoke`、`object`、`native_plan`、`json.dumps`、`pytest.mark.parametrize`、`smoke_checks`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_timeout_keeps_unknown_and_does_not_start_another_read`（L296–L310）：接收`monkeypatch`。 控制顺序：L308断言`diagnostic.native_startup_smoke( object(), native_plan(), {}, {"native_semaphore_stor…`。 调用`monkeypatch.setattr`、`pytest.fail`、`diagnostic.native_startup_smoke`、`object`、`native_plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_smoke_timeout_keeps_unknown_and_does_not_start_another_read.execute`（L300–L302）：接收`*args`。 调用`SimpleNamespace`。 返回路径：L302的`SimpleNamespace(exit_code=0)`。
- `test_all_native_diagnostic_reads_fit_existing_byte_budget`（L313–L318）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L314断言`diagnostic.NATIVE_TAIL_LIMIT + diagnostic.PATH_OUTPUT_LIMIT + diagnostic.SMOKE_OUTPUT…`；L318断言`len(json.dumps(receipt()).encode()) < diagnostic.PATH_OUTPUT_LIMIT`。 调用`len`、`json.dumps(receipt()).encode`、`json.dumps`、`receipt`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline`（L324–L384）：接收`monkeypatch`、`probe`、`fail`、`role`。 控制顺序：L335按`role == "frontend"`分支；L375断言`len(requests) == (1 if probe == "metadata" or fail else 2)`；L376断言`len(transports) == len(requests)`；L377断言`_DEADLINE.get() == 999.0`；L378按`probe == "metadata"`分支；L379断言`result["status"] == ("unknown" if fail else "observed")`；L381断言`result["checks"] == (None if fail else expected_checks)`；L382断言`"private-sentinel" not in json.dumps(result)`。 调用`smoke_checks`、`receipt`、`expected_checks.pop`、`next`、`iter`、`expected_paths["paths"].values`、`monkeypatch.setattr`、`SimpleNamespace`、`transports.append`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline.execute_command`（L348–L360）：接收`request`、`**kwargs`。 控制顺序：L350断言`type(request.timeout) is int and 1 <= request.timeout <= 5`；L351断言`_DEADLINE.get() == 15`；L356断言`0 < transports[-1] <= 15 - clock[0]`；L357按`fail`分支；L358抛异常，停止当前正常路径。 调用`requests.append`、`type`、`_DEADLINE.get`、`rest.request`、`RuntimeError`、`SimpleNamespace`、`json.dumps`。 返回路径：L360的`SimpleNamespace(result=json.dumps(value), exit_code=0, additional_properties={})`。
- `test_actual_start_keeps_health_failure_and_closes_http`（L389–L492）：接收`monkeypatch`、`failure`、`native`。 控制顺序：L480断言`events == (["tail", "paths", "smoke", "closed"] if native else ["tail", "closed"])`；L481断言`state["command_exit_status"] == "nonzero"`；L482断言`state["command_exit_code"] == 2`；L483断言`state["output_raw_bytes"] == output_limit`；L484断言`state["output_read_limit_reached"] is True`；L485按`native`分支；L486断言`state["launch_paths"]["status"] == ("unknown" if failure == "paths" else "observed")`；L487断言`state["interpreter_probe"]["exit_status"] == ( "unknown" if failure == "smoke" else "…`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`next`、`ast.walk`、`ast.parse`、`source.read_text`、`isinstance`、`complete_native_plan`、`iter`、`SimpleNamespace`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_start_keeps_health_failure_and_closes_http.paths`（L411–L416）：接收`role`、`*args`。 控制顺序：L412断言`role == "backend"`；L414按`failure == "paths"`分支；L415抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`、`receipt`。 返回路径：L416的`{"status": "observed", **receipt()}`。
- `test_actual_start_keeps_health_failure_and_closes_http.smoke`（L418–L423）：接收`role`、`*args`。 控制顺序：L419断言`role == "backend"`；L421按`failure == "smoke"`分支；L422抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`、`smoke_checks`。 返回路径：L423的`{"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}`。
- `test_actual_start_keeps_health_failure_and_closes_http.read`（L431–L434）：接收`limit`、`tail`、`*args`。 控制顺序：L432断言`limit == output_limit and tail is True`。 调用`events.append`。 返回路径：L434的`output`。
- `test_startup_target_binds_registered_original_command`（L496–L516）：接收`role`。 控制顺序：L504断言`target == { "role": role, "interpreter": "node" if role == "frontend" else "python", …`；L511断言`command.argv[0] == ( "/usr/local/bin/node" if role == "frontend" else "/opt/rnd/runti…`；L516断言`plan.runtime.health_path not in json.dumps(target)`。 调用`complete_native_plan`、`frontend_start_command`、`diagnostic.startup_target`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_target_rejects_role_port_or_endpoint_mismatch`（L531–L540）：接收`frontend`、`port`、`health`。 调用`pytest.raises`、`diagnostic.startup_target`、`complete_native_plan`、`frontend_start_command`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_target_rejects_unregistered_command`（L543–L552）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`diagnostic.startup_target`、`complete_native_plan`、`TaskCommand`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_paths_read_only_fixed_node_and_vite_metadata`（L555–L583）：接收`monkeypatch`。 控制顺序：L567断言`diagnostic.native_startup_paths(object(), 5, role="frontend") == { "status": "observe…`；L571断言`calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.NODE_PROBE], 5)]`；L572断言`{"native_node", "vite_entry", "frontend", "dist_index", "preview_launcher"} <= set( v…`；L575断言`{"native_python", "backend", "app"}.isdisjoint(value["paths"])`；L576断言`len(json.dumps(value).encode()) < diagnostic.PATH_OUTPUT_LIMIT`；L583断言`diagnostic.native_startup_paths(object(), 5, role="frontend") == {"status": "unknown"…`。 调用`receipt`、`next`、`iter`、`value["paths"].values`、`monkeypatch.setattr`、`diagnostic.native_startup_paths`、`object`、`set`、`{"native_python", "backend", "app"}.isdisjoint`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_paths_read_only_fixed_node_and_vite_metadata.execute`（L562–L564）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`SimpleNamespace`、`json.dumps`。 返回路径：L564的`SimpleNamespace(exit_code=0, result=json.dumps(value))`。
- `test_frontend_smoke_uses_same_guard_identity_environment_and_frontend_cwd`（L586–L628）：接收`monkeypatch`。 控制顺序：L627断言`result == {"exit_status": "zero", "output_shapes": [], "checks": checks}`；L628断言`"private-sentinel" not in json.dumps(result)`。 调用`native_plan`、`monkeypatch.setattr`、`diagnostic.product_argv`、`diagnostic.native_startup_smoke`、`object`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_frontend_smoke_uses_same_guard_identity_environment_and_frontend_cwd.execute`（L608–L616）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L609断言`timeout == 5`；L610断言`argv[:2] == ["/bin/sh", "-c"]`；L611断言`argv[2].startswith("cd /tmp/rnd-capability/product/frontend/web && ")`；L614断言`launcher == ["exec", *expected]`。 调用`argv[2].startswith`、`shlex.split`、`argv[2].split`、`inner[2].split`、`SimpleNamespace`。 返回路径：L616的`SimpleNamespace(exit_code=0)`。
- `test_frontend_smoke_uses_same_guard_identity_environment_and_frontend_cwd.read`（L618–L620）：接收`sandbox`、`path`、`timeout`、`limit`、`tail`。 控制顺序：L619断言`timeout == 1 and limit == 512 and tail is True`。 调用`json.dumps`。 返回路径：L620的`json.dumps(checks)`。
- `test_source_free_node_smoke_runs_as_owned_fixture`（L638–L658）：接收`tmp_path`、`node_options`、`expected`。 控制顺序：L642按`node_options is not None`分支；L653断言`result.returncode == 0 and result.stderr == ""`；L655断言`set(value) == {"version_matches", "executable_matches", "cwd_matches", "no_preload"}`；L656断言`all(type(item) is bool for item in value.values())`；L657断言`value["no_preload"] is expected and value["cwd_matches"] is False`；L658断言`len(result.stdout.encode()) < diagnostic.SMOKE_OUTPUT_LIMIT`。 调用`os.environ.items`、`subprocess.run`、`shutil.which`、`json.loads`、`set`、`all`、`type`、`value.values`、`len`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_probe_roles_do_not_execute`（L662–L670）：接收`monkeypatch`、`role`。 控制顺序：L666断言`diagnostic.native_startup_paths(object(), 5, role=role) == {"status": "unknown"}`；L667断言`diagnostic.native_startup_smoke(object(), native_plan(), {}, {}, 5, role=role)["check…`。 调用`monkeypatch.setattr`、`pytest.fail`、`diagnostic.native_startup_paths`、`object`、`diagnostic.native_startup_smoke`、`native_plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients`（L676–L869）：接收`monkeypatch`、`failed_role`、`status`、`phase`。 控制顺序：L702按`phase == "restart"`分支；L854断言`state["target"] == { "role": failed_role, "interpreter": "node" if failed_role == "fr…`；L862断言`state["command_exit_code"] == (1 if type(status) is int and status == 1 else None)`；L863断言`events.count(("status", failed_role)) == 1`；L864断言`("node_error" in state) is (failed_role == "frontend")`；L865断言`("closed", failed_role) in events and ("closed", "backend") in events`；L866断言`events[-1] == ("deleted", True) and scope["receipt"]["cleanup"] == "deleted"`；L867断言`scope["receipt"]["passed"] is False`。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`ast.parse`、`source.read_text`、`next`、`ast.walk`、`isinstance`、`any`、`enumerate`、`range`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.Client`（L738–L752）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.Client.__init__`（L739–L740）：接收`base_url`、`**kwargs`。 调用`base_url.endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.Client.stream`（L743–L749）：接收`method`、`endpoint`。 控制顺序：L744断言`method == "GET"`；L745断言`endpoint == ("/" if self.role == "frontend" else plan.runtime.health_path)`。 调用`events.append`、`SimpleNamespace`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.Client.close`（L751–L752）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.redirect`（L754–L758）：接收`argv`。 调用`diagnostic.redirected_command`。 返回路径：L758的`command, path`。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.submit`（L760–L763）：接收`session`、`request`、`**kwargs`。 调用`SimpleNamespace`。 返回路径：L763的`SimpleNamespace(cmd_id=role + "-owned-id")`。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.command_status`（L765–L773）：接收`session`、`command`。 控制顺序：L766断言`session == sessions[failed_role]`；L767断言`command == failed_role + "-owned-id"`；L769按`status == "missing"`分支。 调用`events.append`、`SimpleNamespace`。 返回路径：L770的`None`；L771的`SimpleNamespace( id="another-owned-id" if status == "wrong-command" else command, exit_cod…`。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.read`（L775–L779）：接收`sandbox`、`path`、`timeout`、`limit`、`tail`。 控制顺序：L776断言`path == outputs[failed_role] and limit == diagnostic.NATIVE_TAIL_LIMIT and tail is Tr…`。 返回路径：L779的`"private-sentinel"`。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.paths`（L781–L784）：接收`sandbox`、`timeout`、`role`。 控制顺序：L782断言`role == failed_role and timeout == 5`。 调用`events.append`。 返回路径：L784的`{"status": "unknown"}`。
- `test_actual_sequential_start_binds_failed_target_and_closes_both_clients.smoke`（L786–L789）：接收`sandbox`、`passed_plan`、`database`、`identity`、`timeout`、`role`。 控制顺序：L787断言`role == failed_role and passed_plan is plan and timeout == 5`。 调用`events.append`。 返回路径：L789的`{"exit_status": "unknown", "output_shapes": [], "checks": None}`。

</details>

**创建路径：** `tests/test_capability_startup_paths.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L869。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`34667`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_paths.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "15e24ac3586d2ec88cf122f4e10b88df0f2ac9b65391273e2a381fed4e5212c4"} -->
````python
# tests/test_capability_startup_paths.py
"""Finite metadata from real owned launch fixtures, without candidate execution."""

import ast
import copy
import json
import os
import shlex
import shutil
import stat
import struct
import subprocess
from types import SimpleNamespace

import pytest

from workbench import capability_startup_paths as diagnostic


def helpers(loader):
    tree = ast.parse(diagnostic.PROBE)
    functions = ast.Module([node for node in tree.body if isinstance(node, ast.FunctionDef)], [])
    # Pure regular-file ELF parsing remains covered on Windows. Only this test
    # adapter supplies zero for an absent nonblocking flag; real FIFO handling
    # is separately POSIX-only and the production Linux probe is unchanged.
    probe_os = SimpleNamespace(**vars(os))
    probe_os.O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
    scope = {"os": probe_os, "stat": stat, "struct": struct, "paths": {"elf_loader": str(loader)}}
    exec(compile(functions, "trusted-probe-functions", "exec"), scope)
    return scope


def elf(loader=b"/lib64/ld-linux-x86-64.so.2\0"):
    data = bytearray(256)
    data[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", data, 32, 64)
    struct.pack_into("<HH", data, 54, 56, 1)
    struct.pack_into("<I", data, 64, 3)
    struct.pack_into("<Q", data, 72, 128)
    struct.pack_into("<Q", data, 96, len(loader))
    data[128 : 128 + len(loader)] = loader
    return data


def test_missing_regular_directory_and_dangling_link(tmp_path):
    scope = helpers(tmp_path / "loader")
    inspect = scope["inspect"]
    path = tmp_path / "private-sentinel"
    assert inspect(str(path))["entry"] == "missing"
    path.write_bytes(b"inert")
    assert inspect(str(path))["target"] == "regular"
    assert inspect(str(tmp_path))["target"] == "directory"
    link = tmp_path / "link"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("Creating symlinks requires platform support")
    assert inspect(str(link))["entry"] == "symlink"
    assert inspect(str(link))["target"] == "regular"
    path.unlink()
    value = inspect(str(link))
    assert value["entry"] == "symlink" and value["target"] == "missing"
    assert "private-sentinel" not in json.dumps(value)


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits and directory traversal")
def test_app_dac_does_not_use_root_access(tmp_path):
    # All existing ancestors have to permit UID 20000 traversal too.
    base = tmp_path / "directory"
    base.mkdir(mode=0o755)
    file = base / "program"
    file.write_bytes(b"inert")
    file.chmod(0o000)
    result = helpers(base / "loader")["inspect"](str(file))
    assert result["dac_read"] is False and result["dac_exec"] is False
    assert file.read_bytes() == b"inert" if os.geteuid() == 0 else True


@pytest.mark.parametrize("present", [True, False])
def test_real_elf_header_reports_only_fixed_loader_state(tmp_path, present):
    loader = tmp_path / "loader"
    if present:
        loader.write_bytes(b"inert")
    program = tmp_path / "program"
    program.write_bytes(elf())
    result = helpers(loader)["executable_format"](str(program))
    assert result == {"format": "elf", "loader": "present" if present else "missing"}


@pytest.mark.parametrize(
    "data,kind,loader",
    [
        (b"#!/private/secret\n", "script", "unknown"),
        (b"private-sentinel", "other", "unknown"),
        (elf(b"/private/secret\0"), "elf", "unexpected"),
        (b"\x7fELF", "elf", "unknown"),
    ],
)
def test_unknown_binary_and_shebang_never_expose_content(tmp_path, data, kind, loader):
    program = tmp_path / "program"
    program.write_bytes(data)
    result = helpers(tmp_path / "loader")["executable_format"](str(program))
    assert result == {"format": kind, "loader": loader}
    assert "private" not in json.dumps(result)


def test_elf_program_header_outside_read_budget_is_unknown(tmp_path):
    program = tmp_path / "program"
    data = elf() + bytearray(70000)
    struct.pack_into("<Q", data, 72, 66000)
    program.write_bytes(data)
    assert helpers(tmp_path / "loader")["executable_format"](str(program)) == {
        "format": "elf",
        "loader": "unknown",
    }


@pytest.mark.skipif(os.name != "posix", reason="Actual FIFO requires POSIX nonblocking open")
def test_fifo_is_never_read_and_descriptor_is_closed(tmp_path):
    fifo = tmp_path / "owned-fifo"
    os.mkfifo(fifo)
    scope = helpers(tmp_path / "loader")
    descriptors = []
    opened = scope["os"].open

    def open_fd(*args):
        fd = opened(*args)
        descriptors.append(fd)
        return fd

    scope["os"].open = open_fd
    scope["os"].read = lambda *a: pytest.fail("Non-regular contents must not be read")
    assert scope["executable_format"](str(fifo)) == {"format": "unknown", "loader": "unknown"}
    assert len(descriptors) == 1
    with pytest.raises(OSError):
        os.fstat(descriptors[0])


def receipt():
    return {
        "paths": {
            name: {"entry": "regular", "target": "regular", "dac_read": True, "dac_exec": False}
            for name in diagnostic.PATH_ROLES
        },
        "native_binary": {"format": "elf", "loader": "present"},
    }


def test_controller_requests_only_fixed_program_and_bounds_output(monkeypatch):
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append((argv, timeout))
        return SimpleNamespace(exit_code=0, result=json.dumps(receipt()))

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "observed", **receipt()}
    assert calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.PROBE], 5)]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(secret="private-sentinel"),
        lambda d: d["paths"].pop("native_python"),
        lambda d: d["paths"].update(secret=d["paths"]["env"]),
        lambda d: d["paths"]["env"].update(entry="private-sentinel"),
        lambda d: d["paths"]["env"].update(dac_read=1),
        lambda d: d["paths"]["env"].update(dac_exec="true"),
        lambda d: d["native_binary"].update(loader="private-sentinel"),
        lambda d: d.update(native_binary=[]),
    ],
)
def test_malformed_receipt_is_unknown(monkeypatch, mutate):
    value = copy.deepcopy(receipt())
    mutate(value)
    monkeypatch.setattr(
        diagnostic,
        "control_exec",
        lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(value)),
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "code,output", [(False, "{}"), (1, "private-sentinel"), (0, "x" * 2049), (0, "{"), (0, None)]
)
def test_failed_or_oversize_probe_never_serializes_output(monkeypatch, code, output):
    monkeypatch.setattr(
        diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code, result=output)
    )
    assert diagnostic.native_startup_paths(object(), 5) == {"status": "unknown"}


@pytest.mark.parametrize(
    "text,expected",
    [
        ("/usr/bin/env: '/private/secret': No such file or directory", ["env-launcher"]),
        ("/bin/sh: 1: cd: can't cd to /private/secret", ["shell-launcher"]),
        (
            "/private/secret: error while loading shared libraries: private.so: cannot open shared object file: No such file or directory",
            ["elf-loader", "shared-library-open"],
        ),
        (
            "2026-10-05 08:00:00.001 | ERROR    | app.core.discover:_build:44 - private-sentinel",
            ["vendor-loguru"],
        ),
        (
            "\x1b[31mFileNotFoundError: private-sentinel\x1b[0m",
            ["file-not-found-type", "ansi-control"],
        ),
        ("private-sentinel", []),
        (None, []),
    ],
)
def test_output_format_classification_never_copies_content(text, expected):
    assert diagnostic.output_shapes(text) == expected
    assert diagnostic.output_shapes("x" * 8000 + (text or "")) == []


def native_plan():
    return SimpleNamespace(
        selection=SimpleNamespace(template="fastapiadmin", database="postgresql"),
        runtime=SimpleNamespace(port=8123),
    )


def smoke_checks():
    return dict.fromkeys(("version_matches", "executable_matches", "cwd_matches", "isolated"), True)


def test_smoke_uses_original_guard_and_env_with_shared_five_second_budget(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    plan = native_plan()
    database = {"DATABASE_PASSWORD": "private-sentinel"}
    identity = {"native_semaphore_storage": True}
    expected = diagnostic.product_argv(
        plan,
        [
            "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python",
            "-I",
            "-S",
            "-c",
            diagnostic.SMOKE,
        ],
        database,
        **identity,
    )

    def execute(sandbox, argv, timeout):
        assert timeout == 5
        assert argv[:2] == ["/bin/sh", "-c"]
        assert argv[2].startswith("cd /tmp/rnd-capability/product/backend && ")
        inner = shlex.split(argv[2].split(" && ", 1)[1])
        assert inner[:2] == ["/bin/sh", "-c"]
        launcher = shlex.split(inner[2].split(" </dev/null ", 1)[0])
        assert launcher == ["exec", *expected]
        assert "--native-shm" in launcher and "--reuid=rnd-module" in launcher
        clock[0] = 4
        return SimpleNamespace(exit_code=0)

    def read(sandbox, path, timeout, limit, tail):
        assert timeout == 1 and limit == 512 and tail is True
        assert path.startswith("/tmp/rnd-module-control/private/")
        return json.dumps(smoke_checks())

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(diagnostic, "read_command_output", read)
    result = diagnostic.native_startup_smoke(object(), plan, database, identity, 99)
    assert result == {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "code,output,expected",
    [
        (127, "/usr/bin/env: private-sentinel: No such file or directory", "nonzero"),
        (0, '{"version_matches":true,"version_matches":false}', "zero"),
        (False, "private-sentinel", "unknown"),
        (0, "private-sentinel", "zero"),
        (0, "x" * 513, "zero"),
        (0, json.dumps({**smoke_checks(), "isolated": 1}), "zero"),
        (0, json.dumps({**smoke_checks(), "secret": "private-sentinel"}), "zero"),
    ],
)
def test_smoke_failure_and_corrupt_output_are_finite(monkeypatch, code, output, expected):
    monkeypatch.setattr(diagnostic, "control_exec", lambda *a: SimpleNamespace(exit_code=code))
    monkeypatch.setattr(diagnostic, "read_command_output", lambda *a, **k: output)
    result = diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    )
    assert result["exit_status"] == expected and result["checks"] is None
    assert "private-sentinel" not in json.dumps(result)


def test_smoke_timeout_keeps_unknown_and_does_not_start_another_read(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])

    def execute(*args):
        clock[0] = 5.1
        return SimpleNamespace(exit_code=0)

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(
        diagnostic, "read_command_output", lambda *a, **k: pytest.fail("Deadline exceeded")
    )
    assert diagnostic.native_startup_smoke(
        object(), native_plan(), {}, {"native_semaphore_storage": True}, 5
    ) == {"exit_status": "zero", "output_shapes": [], "checks": None}


def test_all_native_diagnostic_reads_fit_existing_byte_budget():
    assert (
        diagnostic.NATIVE_TAIL_LIMIT + diagnostic.PATH_OUTPUT_LIMIT + diagnostic.SMOKE_OUTPUT_LIMIT
        == 8000
    )
    assert len(json.dumps(receipt()).encode()) < diagnostic.PATH_OUTPUT_LIMIT


@pytest.mark.parametrize("probe", ["metadata", "smoke"])
@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("role", ["backend", "frontend"])
def test_real_sdk_integer_model_reaches_api_with_shared_transport_deadline(
    monkeypatch, probe, fail, role
):
    import httpx
    from daytona._sync.process import Process

    from workbench.daytona_sessions import _DEADLINE, harden_toolbox_transport

    clock = [10.0]
    expected_checks = smoke_checks()
    expected_paths = receipt()
    if role == "frontend":
        expected_checks["no_preload"] = expected_checks.pop("isolated")
        expected_paths["paths"] = {
            key: next(iter(expected_paths["paths"].values())) for key in diagnostic.NODE_PATH_ROLES
        }
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    requests, transports = [], []
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda method, url, **kwargs: transports.append(kwargs["_request_timeout"]),
    )
    harden_toolbox_transport(SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest)))

    def execute_command(*, request, **kwargs):
        requests.append(request)
        assert type(request.timeout) is int and 1 <= request.timeout <= 5
        assert _DEADLINE.get() == 15
        clock[0] += 1.25
        # Exercise the actual SDK-selected larger HTTP budget through the real
        # hardened transport. The absolute deadline must win over that budget.
        rest.request("POST", "https://owned.invalid", **kwargs)
        assert 0 < transports[-1] <= 15 - clock[0]
        if fail:
            raise RuntimeError("private-sentinel")
        value = expected_paths if probe == "metadata" else expected_checks
        return SimpleNamespace(result=json.dumps(value), exit_code=0, additional_properties={})

    outer = _DEADLINE.set(999.0)
    try:
        with httpx.Client(trust_env=False) as client:
            sandbox = SimpleNamespace(
                process=Process("python", SimpleNamespace(execute_command=execute_command), client)
            )
            result = (
                diagnostic.native_startup_paths(sandbox, 5, role=role)
                if probe == "metadata"
                else diagnostic.native_startup_smoke(
                    sandbox, native_plan(), {}, {"native_semaphore_storage": True}, 5, role=role
                )
            )
        assert len(requests) == (1 if probe == "metadata" or fail else 2)
        assert len(transports) == len(requests)
        assert _DEADLINE.get() == 999.0
        if probe == "metadata":
            assert result["status"] == ("unknown" if fail else "observed")
        else:
            assert result["checks"] == (None if fail else expected_checks)
        assert "private-sentinel" not in json.dumps(result)
    finally:
        _DEADLINE.reset(outer)


@pytest.mark.parametrize("failure", [None, "paths", "smoke"])
@pytest.mark.parametrize("native", [False, True])
def test_actual_start_keeps_health_failure_and_closes_http(monkeypatch, failure, native):
    import uuid
    from pathlib import Path

    from daytona import SessionExecuteRequest
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_dependencies import readonly_start_command
    from workbench.capability_sandbox import startup_failure_diagnostic
    from workbench.capability_verification import CheckFailure

    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    start = next(
        n
        for n in ast.walk(ast.parse(source.read_text(encoding="utf-8")))
        if isinstance(n, ast.FunctionDef) and n.name == "start"
    )
    events = []
    plan = complete_native_plan()
    clock = iter((0, plan.runtime.startup_seconds + 1))
    client = SimpleNamespace(close=lambda: events.append("closed"))

    def paths(*args, role):
        assert role == "backend"
        events.append("paths")
        if failure == "paths":
            raise RuntimeError("private-sentinel")
        return {"status": "observed", **receipt()}

    def smoke(*args, role):
        assert role == "backend"
        events.append("smoke")
        if failure == "smoke":
            raise RuntimeError("private-sentinel")
        return {"exit_status": "zero", "output_shapes": [], "checks": smoke_checks()}

    monkeypatch.setattr(diagnostic, "native_startup_paths", paths)
    monkeypatch.setattr(diagnostic, "native_startup_smoke", smoke)

    output_limit = diagnostic.NATIVE_TAIL_LIMIT if native else 8000
    output = "/usr/bin/env: private-sentinel: No such file or directory".ljust(output_limit)

    def read(*args, limit, tail):
        assert limit == output_limit and tail is True
        events.append("tail")
        return output

    state = {}
    process = SimpleNamespace(
        create_session=lambda *a: None,
        execute_session_command=lambda *a, **k: SimpleNamespace(cmd_id="owned"),
    )
    scope = {
        "readonly_start_command": readonly_start_command,
        "require_preinstalled_evidence": lambda *a, **k: None,
        "verify_readonly_dependencies": lambda *a, **k: {},
        "dependency_profile": {},
        "before": {},
        "receipt": {"source_digest": "bound"},
        "plan": plan,
        "settings": SimpleNamespace(tool_timeout=20),
        "sandbox": SimpleNamespace(
            id="owned",
            process=process,
            get_preview_link=lambda *a: SimpleNamespace(url="owned", token="private-sentinel"),
        ),
        "uuid": uuid,
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "product_argv": diagnostic.product_argv,
        "redirected_command": diagnostic.redirected_command,
        "SessionExecuteRequest": SessionExecuteRequest,
        "REMOTE": "/tmp/rnd-capability",
        "shlex": shlex,
        "preview_url": lambda *a: "http://owned.invalid",
        "httpx": SimpleNamespace(Client=lambda **k: client),
        "time": SimpleNamespace(monotonic=lambda: next(clock)),
        "read_command_output": read,
        "control_exec": lambda *a: SimpleNamespace(exit_code=0, result="1"),
        "startup_failure_diagnostic": startup_failure_diagnostic,
        "startup_command_exit_facts": lambda *a: {
            "command_exit_status": "nonzero",
            "command_exit_code": 2,
        },
        "native": native,
        "CheckFailure": CheckFailure,
    }
    exec(compile(ast.Module([start], []), "actual-start-function", "exec"), scope)
    with pytest.raises(CheckFailure, match="健康检查"):
        scope["start"]()
    state = scope["receipt"]["startup_diagnostic"]
    assert events == (["tail", "paths", "smoke", "closed"] if native else ["tail", "closed"])
    assert state["command_exit_status"] == "nonzero"
    assert state["command_exit_code"] == 2
    assert state["output_raw_bytes"] == output_limit
    assert state["output_read_limit_reached"] is True
    if native:
        assert state["launch_paths"]["status"] == ("unknown" if failure == "paths" else "observed")
        assert state["interpreter_probe"]["exit_status"] == (
            "unknown" if failure == "smoke" else "zero"
        )
    else:
        assert "launch_paths" not in state and "interpreter_probe" not in state
    assert "private-sentinel" not in json.dumps(state)


@pytest.mark.parametrize("role", ["backend", "frontend"])
def test_startup_target_binds_registered_original_command(role):
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import frontend_start_command

    plan = complete_native_plan()
    original = frontend_start_command() if role == "frontend" else plan.runtime.start
    command, target = diagnostic.startup_target(plan, original)
    assert target == {
        "role": role,
        "interpreter": "node" if role == "frontend" else "python",
        "port": 5173 if role == "frontend" else plan.runtime.port,
        "health_endpoint": "frontend-root" if role == "frontend" else "plan-health",
        "registered_command_bound": True,
    }
    assert command.argv[0] == (
        "/usr/local/bin/node"
        if role == "frontend"
        else "/opt/rnd/runtime/fastapiadmin/backend/.venv/bin/python"
    )
    assert plan.runtime.health_path not in json.dumps(target)


@pytest.mark.parametrize(
    "frontend,port,health",
    [
        (False, 5173, None),
        (False, True, None),
        (False, 0, None),
        (False, None, "/"),
        (True, 8001, None),
        (True, None, "/openapi.json"),
        (True, "5173", "/"),
    ],
)
def test_startup_target_rejects_role_port_or_endpoint_mismatch(frontend, port, health):
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import frontend_start_command
    from workbench.capability_verification import CheckFailure

    with pytest.raises(CheckFailure):
        diagnostic.startup_target(
            complete_native_plan(), frontend_start_command() if frontend else None, port, health
        )


def test_startup_target_rejects_unregistered_command():
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_contracts import TaskCommand
    from workbench.capability_verification import CheckFailure

    with pytest.raises(CheckFailure):
        diagnostic.startup_target(
            complete_native_plan(), TaskCommand(cwd="frontend/web", argv=["node", "private.js"])
        )


def test_frontend_paths_read_only_fixed_node_and_vite_metadata(monkeypatch):
    value = receipt()
    value["paths"] = {
        key: next(iter(value["paths"].values())) for key in diagnostic.NODE_PATH_ROLES
    }
    calls = []

    def execute(sandbox, argv, timeout):
        calls.append((argv, timeout))
        return SimpleNamespace(exit_code=0, result=json.dumps(value))

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    assert diagnostic.native_startup_paths(object(), 5, role="frontend") == {
        "status": "observed",
        **value,
    }
    assert calls == [(["/usr/bin/python3", "-I", "-S", "-c", diagnostic.NODE_PROBE], 5)]
    assert {"native_node", "vite_entry", "frontend", "dist_index", "preview_launcher"} <= set(
        value["paths"]
    )
    assert {"native_python", "backend", "app"}.isdisjoint(value["paths"])
    assert len(json.dumps(value).encode()) < diagnostic.PATH_OUTPUT_LIMIT
    # A Python receipt cannot be presented as frontend metadata.
    monkeypatch.setattr(
        diagnostic,
        "control_exec",
        lambda *a: SimpleNamespace(exit_code=0, result=json.dumps(receipt())),
    )
    assert diagnostic.native_startup_paths(object(), 5, role="frontend") == {"status": "unknown"}


def test_frontend_smoke_uses_same_guard_identity_environment_and_frontend_cwd(monkeypatch):
    plan = native_plan()
    database = {
        "DATABASE_PASSWORD": "private-sentinel",
        "NODE_OPTIONS": "--max-old-space-size=3072",
    }
    identity = {"native_semaphore_storage": True}
    clock = [0.0]
    monkeypatch.setattr(diagnostic.time, "monotonic", lambda: clock[0])
    expected = diagnostic.product_argv(
        plan,
        ["/usr/local/bin/node", "--input-type=module", "--eval", diagnostic.NODE_SMOKE],
        database,
        **identity,
    )
    checks = {
        "version_matches": True,
        "executable_matches": True,
        "cwd_matches": True,
        "no_preload": True,
    }

    def execute(sandbox, argv, timeout):
        assert timeout == 5
        assert argv[:2] == ["/bin/sh", "-c"]
        assert argv[2].startswith("cd /tmp/rnd-capability/product/frontend/web && ")
        inner = shlex.split(argv[2].split(" && ", 1)[1])
        launcher = shlex.split(inner[2].split(" </dev/null ", 1)[0])
        assert launcher == ["exec", *expected]
        clock[0] = 4
        return SimpleNamespace(exit_code=0)

    def read(sandbox, path, timeout, limit, tail):
        assert timeout == 1 and limit == 512 and tail is True
        return json.dumps(checks)

    monkeypatch.setattr(diagnostic, "control_exec", execute)
    monkeypatch.setattr(diagnostic, "read_command_output", read)
    result = diagnostic.native_startup_smoke(
        object(), plan, database, identity, 99, role="frontend"
    )
    assert result == {"exit_status": "zero", "output_shapes": [], "checks": checks}
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.skipif(
    shutil.which("node") is None, reason="Trusted Node unavailable for owned smoke fixture"
)
@pytest.mark.parametrize(
    "node_options,expected",
    [(None, True), ("--max-old-space-size=3072", True), ("--stack-trace-limit=2", False)],
)
def test_source_free_node_smoke_runs_as_owned_fixture(tmp_path, node_options, expected):
    environment = {
        key: value for key, value in os.environ.items() if key not in {"NODE_OPTIONS", "NODE_PATH"}
    }
    if node_options is not None:
        environment["NODE_OPTIONS"] = node_options
    result = subprocess.run(
        [shutil.which("node"), "--input-type=module", "--eval", diagnostic.NODE_SMOKE],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
        env=environment,
    )
    assert result.returncode == 0 and result.stderr == ""
    value = json.loads(result.stdout)
    assert set(value) == {"version_matches", "executable_matches", "cwd_matches", "no_preload"}
    assert all(type(item) is bool for item in value.values())
    assert value["no_preload"] is expected and value["cwd_matches"] is False
    assert len(result.stdout.encode()) < diagnostic.SMOKE_OUTPUT_LIMIT


@pytest.mark.parametrize("role", [None, [], {}, True, "private-sentinel"])
def test_invalid_probe_roles_do_not_execute(monkeypatch, role):
    monkeypatch.setattr(
        diagnostic, "control_exec", lambda *a: pytest.fail("Unknown target executed")
    )
    assert diagnostic.native_startup_paths(object(), 5, role=role) == {"status": "unknown"}
    assert (
        diagnostic.native_startup_smoke(object(), native_plan(), {}, {}, 5, role=role)["checks"]
        is None
    )


@pytest.mark.parametrize("failed_role", ["backend", "frontend"])
@pytest.mark.parametrize("status", [1, None, True, "1", -1, 256, "wrong-command", "missing"])
@pytest.mark.parametrize("phase", ["initial", "restart"])
def test_actual_sequential_start_binds_failed_target_and_closes_both_clients(
    monkeypatch, failed_role, status, phase
):
    from contextlib import closing, contextmanager
    from pathlib import Path

    from daytona import SessionExecuteRequest
    from test_capability_startup_session import native_plan as complete_native_plan

    from workbench.capability_native_runtime import FRONTEND_PORT, frontend_start_command
    from workbench.capability_sandbox import startup_command_exit_facts, startup_failure_diagnostic
    from workbench.capability_verification import CheckFailure

    source = Path(__file__).parents[1] / "workbench/capability_sandbox.py"
    tree = ast.parse(source.read_text())
    outer = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Try)
        and any(isinstance(child, ast.FunctionDef) and child.name == "start" for child in n.body)
    )
    first = next(
        i for i, n in enumerate(outer.body) if isinstance(n, ast.FunctionDef) and n.name == "start"
    )
    last = next(i for i in range(first, len(outer.body)) if isinstance(outer.body[i], ast.With))
    body = outer.body[first : last + 1]
    if phase == "restart":
        parent = next(
            n
            for n in ast.walk(outer)
            if isinstance(n, ast.If)
            and any(
                isinstance(child, ast.Assign)
                and isinstance(child.targets[0], ast.Tuple)
                and [item.id for item in child.targets[0].elts if isinstance(item, ast.Name)]
                == ["http", "_", "_"]
                for child in n.body
            )
        )
        begin = next(
            i
            for i, child in enumerate(parent.body)
            if isinstance(child, ast.Assign)
            and isinstance(child.targets[0], ast.Tuple)
            and [item.id for item in child.targets[0].elts if isinstance(item, ast.Name)]
            == ["http", "_", "_"]
        )
        finish = next(
            i for i in range(begin, len(parent.body)) if isinstance(parent.body[i], ast.With)
        )
        body = [outer.body[first], *parent.body[begin : finish + 1]]
    tested = ast.Try(body=body, handlers=[], orelse=[], finalbody=outer.finalbody)
    plan = complete_native_plan()
    plan.runtime.health_path = "/private-health-sentinel"
    events, sessions, outputs = [], {}, {}
    moments = iter(
        [0, 0, plan.runtime.startup_seconds + 1]
        if failed_role == "backend"
        else [0, 0, 0, 0, plan.runtime.startup_seconds + 1]
    )
    ids = iter(["b" * 32, "f" * 32])

    class Client:
        def __init__(self, base_url, **kwargs):
            self.role = "frontend" if base_url.endswith("5173") else "backend"

        @contextmanager
        def stream(self, method, endpoint):
            assert method == "GET"
            assert endpoint == ("/" if self.role == "frontend" else plan.runtime.health_path)
            events.append(("health", self.role, endpoint))
            yield SimpleNamespace(
                status_code=200 if self.role == "backend" and failed_role == "frontend" else 503
            )

        def close(self):
            events.append(("closed", self.role))

    def redirect(argv):
        role = "frontend" if "/usr/local/bin/node" in argv else "backend"
        command, path = diagnostic.redirected_command(argv)
        outputs[role] = path
        return command, path

    def submit(session, request, **kwargs):
        role = "frontend" if "native-preview.mjs" in request.command else "backend"
        sessions[role] = session
        return SimpleNamespace(cmd_id=role + "-owned-id")

    def command_status(session, command):
        assert session == sessions[failed_role]
        assert command == failed_role + "-owned-id"
        events.append(("status", failed_role))
        if status == "missing":
            return None
        return SimpleNamespace(
            id="another-owned-id" if status == "wrong-command" else command, exit_code=status
        )

    def read(sandbox, path, timeout, *, limit, tail):
        assert (
            path == outputs[failed_role] and limit == diagnostic.NATIVE_TAIL_LIMIT and tail is True
        )
        return "private-sentinel"

    def paths(sandbox, timeout, *, role):
        assert role == failed_role and timeout == 5
        events.append(("paths", role))
        return {"status": "unknown"}

    def smoke(sandbox, passed_plan, database, identity, timeout, *, role):
        assert role == failed_role and passed_plan is plan and timeout == 5
        events.append(("smoke", role))
        return {"exit_status": "unknown", "output_shapes": [], "checks": None}

    monkeypatch.setattr(diagnostic, "native_startup_paths", paths)
    monkeypatch.setattr(diagnostic, "native_startup_smoke", smoke)
    sandbox = SimpleNamespace(
        id="owned",
        process=SimpleNamespace(
            create_session=lambda *a: None,
            execute_session_command=submit,
            get_session_command=command_status,
        ),
        get_preview_link=lambda port: SimpleNamespace(url="private-preview", token="private-token"),
    )
    scope = {
        "require_preinstalled_evidence": lambda *a, **k: None,
        "verify_readonly_dependencies": lambda *a, **k: {},
        "dependency_profile": {},
        "before": {},
        # A previous backend observation must not survive a failed new attempt.
        "receipt": {
            "source_digest": "bound",
            "passed": False,
            "cleanup": "pending",
            "backend_health_observed": True,
        },
        "plan": plan,
        "settings": SimpleNamespace(tool_timeout=20),
        "sandbox": sandbox,
        "uuid": SimpleNamespace(uuid4=lambda: SimpleNamespace(hex=next(ids))),
        "database": {},
        "identity_options": {"native_semaphore_storage": True},
        "product_argv": diagnostic.product_argv,
        "redirected_command": redirect,
        "SessionExecuteRequest": SessionExecuteRequest,
        "REMOTE": "/tmp/rnd-capability",
        "shlex": shlex,
        "preview_url": lambda url, sid, port: "https://owned.invalid/" + str(port),
        "httpx": SimpleNamespace(Client=Client),
        "time": SimpleNamespace(monotonic=lambda: next(moments), sleep=lambda *a: None),
        "read_command_output": read,
        "control_exec": lambda *a: SimpleNamespace(exit_code=0, result="1"),
        "startup_failure_diagnostic": startup_failure_diagnostic,
        "startup_command_exit_facts": startup_command_exit_facts,
        "native": True,
        "FRONTEND_PORT": FRONTEND_PORT,
        "frontend_start_command": frontend_start_command,
        "CheckFailure": CheckFailure,
        "closing": closing,
        "oracle_adapter": None,
        "client": SimpleNamespace(
            delete=lambda actual, **k: events.append(("deleted", actual is sandbox))
        ),
        "write_json": lambda *a: None,
        "receipt_path": "unused",
    }
    with pytest.raises(CheckFailure, match="健康检查"):
        exec(
            compile(
                ast.fix_missing_locations(ast.Module([tested], [])),
                "actual-sequential-start-and-cleanup",
                "exec",
            ),
            scope,
        )
    state = scope["receipt"]["startup_diagnostic"]
    assert state["target"] == {
        "role": failed_role,
        "interpreter": "node" if failed_role == "frontend" else "python",
        "port": 5173 if failed_role == "frontend" else plan.runtime.port,
        "health_endpoint": "frontend-root" if failed_role == "frontend" else "plan-health",
        "registered_command_bound": True,
        "backend_health_observed": failed_role == "frontend",
    }
    assert state["command_exit_code"] == (1 if type(status) is int and status == 1 else None)
    assert events.count(("status", failed_role)) == 1
    assert ("node_error" in state) is (failed_role == "frontend")
    assert ("closed", failed_role) in events and ("closed", "backend") in events
    assert events[-1] == ("deleted", True) and scope["receipt"]["cleanup"] == "deleted"
    assert scope["receipt"]["passed"] is False
    assert "private" not in json.dumps(scope["receipt"])
    assert "owned-id" not in json.dumps(scope["receipt"])
````
