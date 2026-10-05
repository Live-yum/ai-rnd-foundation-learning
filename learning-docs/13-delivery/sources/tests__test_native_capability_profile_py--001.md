# tests/test_native_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `product`（L24–L53）：接收`tmp_path`。 控制顺序：L27遍历`("backend", "deployment")`；L41遍历`native.dependencies.native_descriptor_roles()["auxiliary_source"]`。 调用`atomic_text`、`json.dumps`、`native.dependencies.native_descriptor_roles`、`name.endswith`。 返回路径：L53的`root`。
- `foundation`（L57–L77）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L58的`{ "profile": native.base.PROFILE, "recipe_identity": "e" * 64, "runner": { "image_id": RUN…`。
- `image_for`（L80–L102）：接收`record`。 返回路径：L81的`{ "Id": IMAGE, "Os": "linux", "Architecture": "amd64", "RepoDigests": ["127.0.0.1:6000/" +…`。
- `prepared`（L106–L154）：接收`tmp_path`、`product`、`foundation`、`monkeypatch`。 调用`directory.mkdir`、`native.product_inputs`、`native.recipe_identity`、`native.base_identity`、`native.native_stamp`、`native.selection`、`copy.deepcopy`、`dict`、`monkeypatch.setattr`等。 返回路径：L154的`directory, record, image`。
- `test_filtered_dependency_context_never_copies_product_code_secrets_or_hooks`（L157–L177）：接收`product`、`tmp_path`。 控制顺序：L163断言`paths == {"product/" + name for name in native.DESCRIPTORS} \| { "Dockerfile", "harne…`；L172断言`"https://pypi.org/simple" in (context / "product/backend/uv.lock").read_text()`；L173断言`"tuna.tsinghua" in (product / "backend/uv.lock").read_text()`；L174断言`native.product_inputs(product) == expected`；L175断言`not any( "must-not-be-copied" in path.read_text() for path in context.rglob("*") if p…`。 调用`native.product_inputs`、`context.mkdir`、`native.prepare_context`、`path.relative_to(context).as_posix`、`path.relative_to`、`context.rglob`、`path.is_file`、`(context / "product/backend/uv.lock").read_text`、`(product / "backend/uv.lock").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registry_credentials_are_rejected_before_build`（L188–L191）：接收`product`、`value`。 调用`atomic_text`、`pytest.raises`、`native.product_inputs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secret_files_are_filtered_but_dependency_and_source_drift_are_distinct`（L194–L205）：接收`product`。 控制顺序：L199断言`native.product_inputs(product) == original`；L202断言`changed["dependency_identity"] == original["dependency_identity"]`；L203断言`changed["source_identity"] != original["source_identity"]`；L205断言`native.product_inputs(product)["dependency_identity"] != original["dependency_identit…`。 调用`native.product_inputs`、`atomic_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_native_manifest_selection_is_supported`（L216–L219）：接收`product`、`metadata`。 调用`atomic_text`、`json.dumps`、`pytest.raises`、`native.product_inputs`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_locks_and_symlinks_are_rejected`（L222–L228）：接收`product`、`tmp_path`。 调用`(product / "backend/uv.lock").unlink`、`pytest.raises`、`native.product_inputs`、`(product / "backend/uv.lock").symlink_to`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_rejects_source_drift`（L231–L235）：接收`product`、`tmp_path`。 调用`native.product_inputs`、`atomic_text`、`pytest.raises`、`native.prepare_context`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_readonly_check_revalidates_base_snapshot_and_normalizes_native_record`（L238–L252）：接收`prepared`、`monkeypatch`、`foundation`。 控制顺序：L246断言`native.require_native_profile(directory, record["snapshot"]["snapshot"]) == record`；L247断言`checked == [directory]`；L248断言`record["runner"] == foundation["runner"]`；L249断言`record["selection"]["database"] == "postgresql"`；L250断言`record["resources"] == {"cpu": 2, "memory": 6, "disk": 30}`。 调用`monkeypatch.setattr`、`checked.append`、`native.require_native_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_record_tampering_fails_closed`（L272–L277）：接收`prepared`、`mutation`。 调用`mutation`、`atomic_text`、`json.dumps`、`pytest.raises`、`native.require_native_profile`、`pytest.mark.parametrize`、`record.update`、`record["runner"].update`、`record["base"].update`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_image_drift_is_rejected`（L293–L297）：接收`prepared`、`mutation`。 调用`mutation`、`pytest.raises`、`native.require_native_profile`、`pytest.mark.parametrize`、`image.update`、`image["Config"].update`、`image["Config"]["Labels"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_product_lock_drift_prevents_reusing_native_profile`（L300–L304）：接收`prepared`、`product`。 调用`atomic_text`、`pytest.raises`、`native.require_native_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_uses_only_owned_base_and_separate_ready_record`（L309–L375）：接收`prepared`、`product`、`monkeypatch`、`failure`、`diagnostics`。 控制顺序：L321遍历`protected`；L349按`failure`分支；L352断言`not (directory / native.LOCK).exists()`；L353按`diagnostics`分支；L355断言`value["stage"] == { "push": "prepare-image-push", "image": "prepare-published-image-v…`；L363断言`value["passed"] is False and value["affects_acceptance"] is False`；L366断言`result == expected`；L367断言`native.require_native_profile(directory) == result`。后续分支沿下方源码相同行号继续阅读。 调用`(directory / native.LOCK).unlink`、`atomic_text`、`monkeypatch.setattr`、`calls.append`、`pytest.raises`、`native.prepare`、`(directory / native.LOCK).exists`、`json.loads`、`report.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_uses_only_owned_base_and_separate_ready_record.docker`（L325–L340）：接收`*args`、`**kwargs`。 控制顺序：L327按`args[0] == "build"`分支；L329断言`not (context / "product/.env").exists()`；L330断言`not (context / "product/backend/main.py").exists()`；L331断言`"BASE_IMAGE=127.0.0.1:6000/rnd-python@" + DIGEST in args`；L332断言`"--pull=false" in args`；L333按`failure == "input"`分支；L335按`args[0] == "push"`分支；L336按`failure == "push"`分支。后续分支沿下方源码相同行号继续阅读。 调用`calls.append`、`Path`、`(context / "product/.env").exists`、`(context / "product/backend/main.py").exists`、`atomic_text`、`RuntimeError`。 返回路径：L340的`""`。
- `test_prepare_refuses_overwrite_before_docker`（L378–L386）：接收`prepared`、`product`、`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base`（L391–L473）：接收`prepared`、`monkeypatch`、`failure`、`diagnostics`。 控制顺序：L408按`failure == "source"`分支；L410按`failure == "state"`分支；L412按`failure == "resources"`分支；L445按`failure`分支；L448断言`not (directory / native.ENVIRONMENT).exists()`；L449按`diagnostics`分支；L451断言`value["stage"] == ( "register-worker-client-close" if failure == "close" else "regist…`；L456断言`KEY not in report.read_text()`。后续分支沿下方源码相同行号继续阅读。 调用`atomic_text`、`json.dumps`、`SimpleNamespace`、`Snapshots`、`monkeypatch.setattr`、`calls.append`、`pytest.raises`、`native.register_worker`、`(directory / native.ENVIRONMENT).exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.Snapshots`（L415–L423）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.Snapshots.create`（L416–L423）：接收`params`、`**kwargs`。 控制顺序：L418断言`params.image == snapshot["digest"]`；L419断言`{ name: getattr(params.resources, name) for name in native.RESOURCES } == native.RESO…`；L422断言`params.region_id == "local" and kwargs["timeout"] == 600`。 调用`calls.append`、`getattr`。 返回路径：L423的`existing`。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.factory`（L427–L431）：接收`settings`。 控制顺序：L428断言`settings.daytona_api_key.get_secret_value() == KEY`；L429断言`settings.daytona_api_url == "http://127.0.0.1:3000/api"`；L430断言`settings.daytona_target == "local"`。 调用`settings.daytona_api_key.get_secret_value`。 返回路径：L431的`client`。
- `test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base.close`（L433–L437）：接收`value`。 控制顺序：L434断言`value is client`；L436按`failure == "close"`分支；L437抛异常，停止当前正常路径。 调用`calls.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_has_bounded_subprocess_and_no_key_in_argv`（L476–L488）：接收`prepared`、`monkeypatch`。 控制顺序：L482断言`args[0][1:4] == [ "-m", "scripts.daytona_native_capability_profile", "register-worker…`；L487断言`kwargs["timeout"] == 720`；L488断言`KEY not in repr(calls)`。 调用`monkeypatch.setattr`、`calls.append`、`native.register`、`repr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_real_sdk_serializes_digest_without_tag_substitution`（L491–L561）：接收`prepared`、`monkeypatch`。 源码说明：Run register_worker through the actual SDK and JSON transport; only HTTP is fake.。 控制顺序：L502遍历`tuple(os.environ)`；L503按`name.lower().endswith("_proxy")`分支；L559断言`[method for method, _ in calls] == ["GET", "POST", "GET"]`；L560断言`created["imageName"] == snapshot["digest"]`；L561断言`snapshot["snapshot"] in (directory / native.ENVIRONMENT).read_text()`。 调用`atomic_text`、`json.dumps`、`tuple`、`name.lower().endswith`、`name.lower`、`monkeypatch.delenv`、`monkeypatch.setattr`、`native.register_worker`、`(directory / native.ENVIRONMENT).read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registration_real_sdk_serializes_digest_without_tag_substitution.request`（L506–L552）：接收`_pool`、`method`、`url`、`**kwargs`。 控制顺序：L507断言`url.startswith("http://127.0.0.1:3000/api/snapshots")`；L509按`method == "GET"`分支；L510按`len(calls) == 1`分支；L513断言`len(calls) == 3`；L514断言`url == "http://127.0.0.1:3000/api/snapshots/" + created["id"]`；L517断言`method == "POST" and url == "http://127.0.0.1:3000/api/snapshots"`；L519断言`isinstance(kwargs["body"], str)`；L521断言`data["imageName"] == snapshot["digest"]`。后续分支沿下方源码相同行号继续阅读。 调用`url.startswith`、`calls.append`、`len`、`isinstance`、`json.loads`、`created.update`、`urllib3.HTTPResponse`、`json.dumps(data).encode`、`json.dumps`。 返回路径：L548的`urllib3.HTTPResponse( body=json.dumps(data).encode(), status=200, headers={"Content-Type":…`。
- `test_registration_does_not_overwrite_other_native_credentials`（L564–L572）：接收`prepared`、`monkeypatch`。 调用`atomic_text`、`json.dumps`、`native.write_private_new`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.register_worker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_recipe_keeps_control_identity_pinned_tools_and_no_product_execution`（L575–L600）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L577遍历`( "ARG BASE_IMAGE", "FROM ${BASE_IMAGE}", "libseccomp2 procps", "…`；L597断言`text in recipe`；L598断言`recipe.rstrip().endswith("USER 0:0")`；L599断言`"warm.py" not in recipe and "vite build" not in recipe`；L600断言`"CAPABILITY_EXECUTION_ENABLED" not in recipe`。 调用`(native.ROOT / native.DOCKERFILE).read_text`、`recipe.rstrip().endswith`、`recipe.rstrip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_key_cannot_inject_environment_or_shell_syntax`（L607–L609）：接收`key`。 调用`pytest.raises`、`native.environment_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_native_environment_must_remain_private`（L612–L621）：接收`prepared`。 控制顺序：L613按`os.name == "nt"`分支。 调用`pytest.skip`、`atomic_text`、`json.dumps`、`native.environment_text`、`path.chmod`、`pytest.raises`、`native.register_worker`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_metadata_cannot_be_adopted_through_a_symlink`（L624–L631）：接收`prepared`、`tmp_path`。 调用`atomic_text`、`json.dumps`、`(directory / native.LOCK).unlink`、`(directory / native.LOCK).symlink_to`、`pytest.raises`、`native.require_native_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_build_diagnostics_match_only_complete_reviewed_run_commands`（L636–L654）：接收`form`、`run`。 控制顺序：L640按`form == "header"`分支；L642按`form == "footer"`分支；L645按`form == "continued-process"`分支；L652断言`(facts["stage"], facts["run"]) == (stage, run)`；L653断言`"private" not in json.dumps(facts)`；L654断言`command not in json.dumps(facts)`。 调用`next`、`native.reviewed_run_commands().items`、`native.reviewed_run_commands`、`command.replace`、`json.dumps`、`native.build_failure_facts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_build_diagnostics_emit_only_fixed_known_error_categories`（L673–L683）：接收`signature`、`category`。 控制顺序：L681断言`category in value["categories"]`；L682断言`signature not in json.dumps(value)`；L683断言`"private" not in json.dumps(value)`。 调用`next`、`native.reviewed_run_commands().items`、`native.reviewed_run_commands`、`native.build_failure_facts`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_build_diagnostics_do_not_adopt_unreviewed_commands_or_ambient_text`（L686–L697）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L688遍历`( f"#12 [native-system 1/2] RUN {command}\n#12 ERROR: private-sec…`；L693断言`native.build_failure_facts(log) == { "stage": "unknown", "run": "unknown", "categorie…`。 调用`next`、`iter`、`native.reviewed_run_commands`、`json.dumps`、`native.build_failure_facts`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_diagnostic_run_mapping_requires_exact_reviewed_recipe`（L701–L720）：接收`tmp_path`、`monkeypatch`、`mutation`。 控制顺序：L704按`mutation == "same-count-edit"`分支；L706按`mutation == "reordered"`分支；L711按`mutation == "oversized"`分支；L713按`mutation != "missing"`分支；L717断言`native.reviewed_run_commands() == {}`；L720断言`result == {"stage": "unknown", "run": "unknown", "categories": ["unknown"]}`。 调用`(native.ROOT / native.DOCKERFILE).read_text`、`list`、`native.reviewed_run_commands`、`recipe.replace`、`recipe.index`、`(tmp_path / "Dockerfile").write_text`、`monkeypatch.setattr`、`native.build_failure_facts`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failure_diagnostics_are_bounded_and_never_serialize_hostile_payloads`（L724–L747）：接收`code`。 控制顺序：L733断言`len(encoded) <= native.DIAGNOSTIC_REPORT_BYTES`；L734断言`report["build"]["scanned_bytes"] <= native.DIAGNOSTIC_SCAN_BYTES`；L735断言`report["build"]["truncated"] is True`；L736断言`report["error"]["returncode"] == ( code if type(code) is int and abs(code) < 2**31 el…`；L739断言`report["error"]["timed_out"] is False`；L740遍历`("private-secret", "password", "private.invalid", "token", "界")`；L741断言`fragment.encode() not in encoded`；L742断言`native.failure_diagnostic({"action": secret, "stage": secret}, RuntimeError(secret))[…`。 调用`subprocess.CalledProcessError`、`native.failure_diagnostic`、`json.dumps(report).encode`、`json.dumps`、`len`、`type`、`abs`、`fragment.encode`、`RuntimeError`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_build_failure_preserves_failure_and_never_writes_readiness`（L750–L773）：接收`prepared`、`product`、`monkeypatch`。 控制顺序：L765断言`caught.value is error`；L767断言`value["stage"] == "prepare-docker-build"`；L768断言`value["error"]["returncode"] == 23`；L769断言`not (directory / native.LOCK).exists()`；L770断言`not (directory / native.ENVIRONMENT).exists()`；L771断言`not list(directory.glob("native-capability-build-*"))`；L772按`os.name != "nt"`分支；L773断言`report.stat().st_mode & 0o777 == 0o600`。 调用`(directory / native.LOCK).unlink`、`subprocess.CalledProcessError`、`monkeypatch.setattr`、`pytest.raises`、`native.prepare`、`json.loads`、`report.read_text`、`(directory / native.LOCK).exists`、`(directory / native.ENVIRONMENT).exists`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_build_failure_preserves_failure_and_never_writes_readiness.fail`（L758–L760）：接收`*args`、`**kwargs`。 控制顺序：L759断言`args[0] == "build" and kwargs == {"timeout": 3600}`；L760抛异常，停止当前正常路径。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stale_ready_profile_and_existing_report_cannot_be_overwritten`（L776–L784）：接收`prepared`、`product`、`monkeypatch`。 控制顺序：L784断言`(directory / native.LOCK).read_bytes() == before`。 调用`(directory / native.LOCK).read_bytes`、`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`native.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_register_parent_preserves_exact_worker_report_and_failure`（L787–L815）：接收`prepared`、`monkeypatch`。 控制顺序：L810断言`caught.value is error`；L811断言`json.loads(report.read_text()) == expected`；L812断言`expected["stage"] == "register-worker-snapshot-create"`；L813断言`expected["error"]["timed_out"] is True`；L814断言`"private" not in report.read_text()`；L815断言`not (directory / native.ENVIRONMENT).exists()`。 调用`native.ToolFailure`、`monkeypatch.setattr`、`pytest.raises`、`native.register`、`json.loads`、`report.read_text`、`(directory / native.ENVIRONMENT).exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_register_parent_preserves_exact_worker_report_and_failure.worker`（L795–L805）：接收`command`、`cwd`、`**kwargs`。 控制顺序：L796断言`command[-2:] == ["--diagnostics", str(report.absolute())]`；L797断言`kwargs["timeout"] == 720`；L801抛异常，停止当前正常路径；L805抛异常，停止当前正常路径。 调用`str`、`report.absolute`、`pytest.raises`、`native.diagnostic_scope`、`subprocess.TimeoutExpired`、`expected.update`、`json.loads`、`report.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_cli_remains_compatible_and_success_does_not_emit_diagnostics`（L820–L837）：接收`tmp_path`、`monkeypatch`、`capsys`、`action`、`diagnostics`。 控制顺序：L826按`action == "prepare"`分支；L828按`diagnostics`分支；L833断言`calls[0][1] == ({"diagnostics": report} if diagnostics else {})`；L834断言`not report.exists()`；L835断言`capsys.readouterr().out == ( "Native snapshot identity step completed; runtime/isolat…`。 调用`str`、`monkeypatch.setattr`、`action.replace`、`calls.append`、`native.main`、`report.exists`、`capsys.readouterr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_workflow_collects_separate_bounded_prepare_and_register_diagnostics`（L840–L858）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L855断言`"--diagnostics reports/native-profile-prepare-diagnostic.json" in build["run"]`；L856断言`"--diagnostics reports/native-profile-register-diagnostic.json" in build["run"]`；L857断言`upload["if"] == "always()"`；L858断言`"reports/native-profile-*-diagnostic.json" in upload["with"]["path"]`。 调用`yaml.safe_load`、`(native.ROOT / ".github/workflows/native-capability-profile.yml")…`、`next`、`step.get`、`step.get("uses", "").startswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_native_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L858。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`35304`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_native_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "52144dd79f0d7a9b2a36d1dab09efa1784317339db8b1bb00cee94f57fc57928"} -->
````python
# tests/test_native_capability_profile.py
"""Native preparation contracts use explicit fakes, never live Docker/runtime proof."""

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import daytona_native_capability_profile as native
from workbench.filesystem import atomic_text

RUNNER = "sha256:" + "a" * 64
BASE_IMAGE = "sha256:" + "b" * 64
IMAGE = "sha256:" + "c" * 64
DIGEST = "sha256:" + "d" * 64
KEY = "existing-local-account-fixture"


@pytest.fixture
def product(tmp_path):
    root = tmp_path / "product"
    atomic_text(root / "deployment/manifest.json", json.dumps({"template": "fastapiadmin"}))
    for folder in ("backend", "deployment"):
        atomic_text(
            root / folder / "pyproject.toml",
            '[project]\nname = "fixture"\nversion = "1"\n',
        )
        atomic_text(
            root / folder / "uv.lock",
            'version = 1\nregistry = "https://pypi.tuna.tsinghua.edu.cn/simple"\n',
        )
    atomic_text(
        root / "frontend/web/package.json",
        '{"name":"fixture","scripts":{"prepare":"DO_NOT_RUN"}}',
    )
    atomic_text(root / "frontend/web/pnpm-lock.yaml", "lockfileVersion: '9.0'\n")
    for name in native.dependencies.native_descriptor_roles()["auxiliary_source"]:
        atomic_text(root / name, "{}" if name.endswith(".json") else "lockfileVersion: '9.0'\n")
    atomic_text(
        root / "backend/main.py",
        "raise RuntimeError('never execute candidate source')\n",
    )
    atomic_text(
        root / "deployment/workbench/native_environment.py",
        "raise RuntimeError('untrusted control')\n",
    )
    atomic_text(root / "frontend/web/.pnpmfile.cjs", "throw Error('untrusted package hook')")
    atomic_text(root / ".env", "API_KEY=must-not-be-copied\n")
    return root


@pytest.fixture
def foundation():
    return {
        "profile": native.base.PROFILE,
        "recipe_identity": "e" * 64,
        "runner": {
            "image_id": RUNNER,
            "tag": "fixed-base-runner",
            "recipe_sha256": "f" * 64,
        },
        "snapshot": {
            "image_id": BASE_IMAGE,
            "digest": "registry:6000/rnd-python@" + DIGEST,
        },
        "bases": {
            "RUST_IMAGE": {
                "tag": "rust:1.85.1-bookworm",
                "digest": "rust@" + DIGEST,
                "image_id": BASE_IMAGE,
            }
        },
    }


def image_for(record):
    return {
        "Id": IMAGE,
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["127.0.0.1:6000/" + native.FAMILY + "@" + DIGEST],
        "Config": {
            "User": "0:0",
            "WorkingDir": native.base.CONTROL_WORKDIR,
            "Entrypoint": [],
            "Cmd": [],
            "Labels": {
                "org.opencontainers.image.revision": native.base.DAYTONA_SOURCE,
                "rnd.capability.profile": native.PROFILE,
                "rnd.capability.recipe": record["recipe_identity"],
                "rnd.capability.base-recipe": record["base"]["recipe_identity"],
                "rnd.capability.base-image": record["base"]["snapshot_image_id"],
                "rnd.capability.base-digest": record["base"]["snapshot_digest"],
                "rnd.capability.dependencies": record["dependency_identity"],
                "rnd.capability.input": record["inputs"]["source_identity"],
            },
        },
    }


@pytest.fixture
def prepared(tmp_path, product, foundation, monkeypatch):
    directory = tmp_path / "profile"
    directory.mkdir()
    inputs = native.product_inputs(product)
    identity, recipes = native.recipe_identity()
    base = native.base_identity(foundation)
    stamp = native.native_stamp(identity, base, inputs)
    record = {
        "profile": native.PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "selection": native.selection(),
        "base": base,
        "runner": copy.deepcopy(foundation["runner"]),
        "inputs": inputs,
        "dependency_identity": inputs["dependency_identity"],
        "resources": dict(native.RESOURCES),
        "snapshot": {
            "image": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "digest": "registry:6000/" + native.FAMILY + "@" + DIGEST,
            "image_id": IMAGE,
            "local_tag": "127.0.0.1:6000/" + native.FAMILY + ":" + stamp,
            "source_hash": stamp,
            "snapshot": native.FAMILY + "-" + stamp,
            "user": "0:0",
            "working_dir": native.base.CONTROL_WORKDIR,
            "recipe_sha256": recipes[native.DOCKERFILE],
        },
    }
    dependency_record = {
        "schema": 1,
        "profile": "fastapiadmin",
        "image_id": IMAGE,
        "manifest_sha256": "1" * 64,
        "installed_tree_sha256": "2" * 64,
        "original_descriptors": inputs["descriptors"],
        "descriptor_roles": inputs["descriptor_roles"],
    }
    record["snapshot"]["dependency_manifest"] = dependency_record
    monkeypatch.setattr(
        native.base,
        "inspect_dependency_manifest",
        lambda *args: copy.deepcopy(dependency_record),
    )
    image = image_for(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    monkeypatch.setattr(native.base, "require_profile", lambda path: copy.deepcopy(foundation))
    monkeypatch.setattr(native.base, "inspect_image", lambda reference: copy.deepcopy(image))
    return directory, record, image


def test_filtered_dependency_context_never_copies_product_code_secrets_or_hooks(product, tmp_path):
    expected = native.product_inputs(product)
    context = tmp_path / "context"
    context.mkdir()
    native.prepare_context(product, context, expected)
    paths = {path.relative_to(context).as_posix() for path in context.rglob("*") if path.is_file()}
    assert paths == {"product/" + name for name in native.DESCRIPTORS} | {
        "Dockerfile",
        "harness/pyproject.toml",
        "harness/uv.lock",
        "dependency-image.py",
        "dependency-build.py",
        "dependency-build.lock.json",
        "dependency-inputs.json",
    }
    assert "https://pypi.org/simple" in (context / "product/backend/uv.lock").read_text()
    assert "tuna.tsinghua" in (product / "backend/uv.lock").read_text()
    assert native.product_inputs(product) == expected
    assert not any(
        "must-not-be-copied" in path.read_text() for path in context.rglob("*") if path.is_file()
    )


@pytest.mark.parametrize(
    "value",
    [
        "_authToken=secret",
        "registry=https://person:secret@registry.npmjs.org/",
        "password=${TOKEN}",
    ],
)
def test_registry_credentials_are_rejected_before_build(product, value):
    atomic_text(product / "frontend/web/.npmrc", value)
    with pytest.raises(ValueError, match="configuration|URLs"):
        native.product_inputs(product)


def test_secret_files_are_filtered_but_dependency_and_source_drift_are_distinct(
    product,
):
    original = native.product_inputs(product)
    atomic_text(product / ".env", "CHANGED_PRIVATE_SECRET=ignored\n")
    assert native.product_inputs(product) == original
    atomic_text(product / "backend/main.py", "changed source\n")
    changed = native.product_inputs(product)
    assert changed["dependency_identity"] == original["dependency_identity"]
    assert changed["source_identity"] != original["source_identity"]
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    assert native.product_inputs(product)["dependency_identity"] != original["dependency_identity"]


@pytest.mark.parametrize(
    "metadata",
    [
        {"template": "python-basic"},
        {"template": "fastapiadmin", "database": "sqlite"},
        {"template": "fastapiadmin", "selection": {"template": "python-basic"}},
    ],
)
def test_only_exact_native_manifest_selection_is_supported(product, metadata):
    atomic_text(product / "deployment/manifest.json", json.dumps(metadata))
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_missing_locks_and_symlinks_are_rejected(product, tmp_path):
    (product / "backend/uv.lock").unlink()
    with pytest.raises(ValueError, match="missing a dependency descriptor"):
        native.product_inputs(product)
    (product / "backend/uv.lock").symlink_to(tmp_path / "not-a-lock")
    with pytest.raises(ValueError):
        native.product_inputs(product)


def test_context_rejects_source_drift(product, tmp_path):
    expected = native.product_inputs(product)
    atomic_text(product / "backend/main.py", "changed")
    with pytest.raises(ValueError, match="input changed"):
        native.prepare_context(product, tmp_path / "context", expected)


def test_readonly_check_revalidates_base_snapshot_and_normalizes_native_record(
    prepared, monkeypatch, foundation
):
    directory, record, _ = prepared
    checked = []
    monkeypatch.setattr(
        native.base, "require_profile", lambda path: checked.append(path) or foundation
    )
    assert native.require_native_profile(directory, record["snapshot"]["snapshot"]) == record
    assert checked == [directory]
    assert record["runner"] == foundation["runner"]
    assert record["selection"]["database"] == "postgresql"
    assert record["resources"] == {"cpu": 2, "memory": 6, "disk": 30}
    with pytest.raises(ValueError, match="derived identity"):
        native.require_native_profile(directory, "wrong-snapshot")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(profile="arbitrary-profile"),
        lambda record: record.update(recipe_identity="0" * 64),
        lambda record: record.update(resources={"cpu": 99, "memory": 6, "disk": 30}),
        lambda record: record["runner"].update(image_id="sha256:" + "0" * 64),
        lambda record: record["base"].update(recipe_identity="0" * 64),
        lambda record: record.update(dependency_identity="0" * 64),
        lambda record: record["snapshot"].update(user="daytona"),
        lambda record: record["snapshot"].update(working_dir="/tmp"),
        lambda record: record["snapshot"].update(local_tag="remote:latest"),
        lambda record: record["snapshot"].update(image_id="mutable"),
        lambda record: record["snapshot"].update(image="remote:latest"),
        lambda record: record["snapshot"].update(source_hash="0" * 16),
    ],
)
def test_native_record_tampering_fails_closed(prepared, mutation):
    directory, record, _ = prepared
    mutation(record)
    atomic_text(directory / native.LOCK, json.dumps(record))
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda image: image.update(Id="sha256:" + "0" * 64),
        lambda image: image.update(RepoDigests=[]),
        lambda image: image.update(Architecture="arm64"),
        lambda image: image["Config"].update(User="daytona"),
        lambda image: image["Config"].update(WorkingDir="/tmp"),
        lambda image: image["Config"].update(Entrypoint=["untrusted"]),
        lambda image: image["Config"].update(Cmd=["untrusted"]),
        lambda image: image["Config"]["Labels"].update({"rnd.capability.input": "0" * 64}),
    ],
)
def test_live_image_drift_is_rejected(prepared, mutation):
    directory, _, image = prepared
    mutation(image)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


def test_product_lock_drift_prevents_reusing_native_profile(prepared, product):
    directory, _, _ = prepared
    atomic_text(product / "backend/uv.lock", "version = 2\n")
    with pytest.raises(ValueError, match="input or base identity changed"):
        native.require_native_profile(directory)


@pytest.mark.parametrize("diagnostics", [False, True])
@pytest.mark.parametrize("failure", [None, "push", "image", "input"])
def test_prepare_uses_only_owned_base_and_separate_ready_record(
    prepared, product, monkeypatch, failure, diagnostics
):
    directory, expected, image = prepared
    (directory / native.LOCK).unlink()
    protected = (
        "snapshot-image.json",
        "workbench.env",
        "api-key.json",
        native.base.LOCK,
        native.base.COMPOSE,
    )
    for name in protected:
        atomic_text(directory / name, "base-must-stay-unchanged")
    calls = []

    def docker(*args, **kwargs):
        calls.append((args, kwargs))
        if args[0] == "build":
            context = Path(args[-1])
            assert not (context / "product/.env").exists()
            assert not (context / "product/backend/main.py").exists()
            assert "BASE_IMAGE=127.0.0.1:6000/rnd-python@" + DIGEST in args
            assert "--pull=false" in args
            if failure == "input":
                atomic_text(product / "backend/main.py", "changed during build")
        if args[0] == "push":
            if failure == "push":
                raise RuntimeError("explicit publication failure")
            if failure == "image":
                image["Id"] = "sha256:" + "0" * 64
        return ""

    monkeypatch.setattr(native.local, "docker", docker)
    monkeypatch.setattr(
        native.base, "compose", lambda *args, **kwargs: calls.append((args, kwargs))
    )
    monkeypatch.setattr(native.local, "wait_for_registry", lambda: None)
    report = directory / "diagnostic.json"
    options = {"diagnostics": report} if diagnostics else {}
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.prepare(product, directory, **options)
        assert not (directory / native.LOCK).exists()
        if diagnostics:
            value = json.loads(report.read_text())
            assert (
                value["stage"]
                == {
                    "push": "prepare-image-push",
                    "image": "prepare-published-image-validation",
                    "input": "prepare-final-identity-validation",
                }[failure]
            )
            assert value["passed"] is False and value["affects_acceptance"] is False
    else:
        result = native.prepare(product, directory, **options)
        assert result == expected
        assert native.require_native_profile(directory) == result
        assert not (directory / native.ENVIRONMENT).exists()
        if os.name != "nt":
            assert (directory / native.LOCK).stat().st_mode & 0o777 == 0o600
        assert not report.exists()
    if not diagnostics:
        assert not report.exists()
    assert all((directory / name).read_text() == "base-must-stay-unchanged" for name in protected)
    assert any(args[0] == "build" for args, _ in calls)


def test_prepare_refuses_overwrite_before_docker(prepared, product, monkeypatch):
    directory, _, _ = prepared
    monkeypatch.setattr(
        native.local,
        "docker",
        lambda *args, **kwargs: pytest.fail("Docker must not run"),
    )
    with pytest.raises(ValueError, match="refuses to overwrite"):
        native.prepare(product, directory)


@pytest.mark.parametrize("diagnostics", [False, True])
@pytest.mark.parametrize("failure", [None, "source", "state", "resources", "close"])
def test_registration_reuses_existing_key_in_local_sdk_without_rewriting_base(
    prepared, monkeypatch, failure, diagnostics
):
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    atomic_text(directory / "workbench.env", "base-environment-unchanged")
    calls = []
    snapshot = record["snapshot"]
    existing = SimpleNamespace(
        name=snapshot["snapshot"],
        image_name=snapshot["digest"],
        state="active",
        cpu=2,
        mem=6,
        disk=30,
        entrypoint=[],
    )
    if failure == "source":
        existing.image_name = "mutable:tag"
    if failure == "state":
        existing.state = "failed"
    if failure == "resources":
        existing.mem = 12

    class Snapshots:
        def create(self, params, **kwargs):
            calls.append("create")
            assert params.image == snapshot["digest"]
            assert {
                name: getattr(params.resources, name) for name in native.RESOURCES
            } == native.RESOURCES
            assert params.region_id == "local" and kwargs["timeout"] == 600
            return existing

    client = SimpleNamespace(snapshot=Snapshots())

    def factory(settings):
        assert settings.daytona_api_key.get_secret_value() == KEY
        assert settings.daytona_api_url == "http://127.0.0.1:3000/api"
        assert settings.daytona_target == "local"
        return client

    def close(value):
        assert value is client
        calls.append("close")
        if failure == "close":
            raise RuntimeError("explicit close failure")

    monkeypatch.setattr(native, "install_loopback_guard", lambda: calls.append("guard"))
    monkeypatch.setattr(native, "client_for", factory)
    monkeypatch.setattr(native, "close_client", close)
    monkeypatch.setattr(native, "snapshot_named", lambda service, name: None)
    report = directory / "diagnostic.json"
    options = {"diagnostics": report} if diagnostics else {}
    if failure:
        with pytest.raises((ValueError, RuntimeError)):
            native.register_worker(directory, **options)
        assert not (directory / native.ENVIRONMENT).exists()
        if diagnostics:
            value = json.loads(report.read_text())
            assert value["stage"] == (
                "register-worker-client-close"
                if failure == "close"
                else "register-worker-snapshot-validation"
            )
            assert KEY not in report.read_text()
    else:
        native.register_worker(directory, **options)
        content = (directory / native.ENVIRONMENT).read_text()
        assert KEY in content and "fastapiadmin/postgresql" in content
        assert "CAPABILITY_EXECUTION_ENABLED" not in content
        assert "local" in content
        monkeypatch.setattr(native, "snapshot_named", lambda service, name: existing)
        native.register_worker(directory, **options)
        assert calls.count("create") == 1
        if os.name != "nt":
            assert (directory / native.ENVIRONMENT).stat().st_mode & 0o777 == 0o600
        assert not report.exists()
    if not diagnostics:
        assert not report.exists()
    assert calls[-1] == "close"
    assert (directory / "workbench.env").read_text() == "base-environment-unchanged"
    assert json.loads((directory / "api-key.json").read_text()) == {"value": KEY}


def test_registration_has_bounded_subprocess_and_no_key_in_argv(prepared, monkeypatch):
    directory, _, _ = prepared
    calls = []
    monkeypatch.setattr(native, "run_command", lambda *args, **kwargs: calls.append((args, kwargs)))
    native.register(directory)
    args, kwargs = calls[0]
    assert args[0][1:4] == [
        "-m",
        "scripts.daytona_native_capability_profile",
        "register-worker",
    ]
    assert kwargs["timeout"] == 720
    assert KEY not in repr(calls)


def test_registration_real_sdk_serializes_digest_without_tag_substitution(prepared, monkeypatch):
    """Run register_worker through the actual SDK and JSON transport; only HTTP is fake."""
    import urllib3

    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    snapshot = record["snapshot"]
    calls = []
    created = {}

    # The production registration subprocess uses clean_env; match that boundary.
    for name in tuple(os.environ):
        if name.lower().endswith("_proxy"):
            monkeypatch.delenv(name)

    def request(_pool, method, url, **kwargs):
        assert url.startswith("http://127.0.0.1:3000/api/snapshots")
        calls.append((method, url))
        if method == "GET":
            if len(calls) == 1:
                data = {"items": [], "total": 0, "page": 1, "totalPages": 0}
            else:
                assert len(calls) == 3
                assert url == "http://127.0.0.1:3000/api/snapshots/" + created["id"]
                data = created | {"state": "active"}
        else:
            assert method == "POST" and url == "http://127.0.0.1:3000/api/snapshots"
            # This is the JSON string after SDK model and REST serialization.
            assert isinstance(kwargs["body"], str)
            data = json.loads(kwargs["body"])
            assert data["imageName"] == snapshot["digest"]
            assert "@sha256:" in data["imageName"]
            assert ":sha256:" not in data["imageName"]
            assert data["name"] == snapshot["snapshot"]
            assert data["regionId"] == "local"
            assert {name: data[name] for name in native.RESOURCES} == native.RESOURCES
            assert "buildInfo" not in data
            data = {
                "id": "00000000-0000-4000-8000-000000000001",
                "general": False,
                "name": data["name"],
                "imageName": data["imageName"],
                "state": "pending",
                # Upstream's internal propagation ref is separate from imageName.
                "ref": "registry:6000/daytona/daytona-" + "d" * 64 + ":daytona",
                "size": 1,
                "entrypoint": [],
                "cpu": data["cpu"],
                "mem": data["memory"],
                "disk": data["disk"],
                "gpu": 0,
                "errorReason": None,
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
                "lastUsedAt": None,
            }
            created.update(data)
        return urllib3.HTTPResponse(
            body=json.dumps(data).encode(),
            status=200,
            headers={"Content-Type": "application/json"},
        )

    monkeypatch.setattr(urllib3.PoolManager, "request", request)
    # Installing a process-wide socket guard here would affect unrelated tests.
    # The production path keeps it; only this in-process transport fixture omits it.
    monkeypatch.setattr(native, "install_loopback_guard", lambda: None)
    native.register_worker(directory)
    assert [method for method, _ in calls] == ["GET", "POST", "GET"]
    assert created["imageName"] == snapshot["digest"]
    assert snapshot["snapshot"] in (directory / native.ENVIRONMENT).read_text()


def test_registration_does_not_overwrite_other_native_credentials(prepared, monkeypatch):
    directory, _, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    native.write_private_new(directory / native.ENVIRONMENT, "different credentials")
    monkeypatch.setattr(
        native, "client_for", lambda settings: pytest.fail("No SDK request allowed")
    )
    with pytest.raises(ValueError, match="refusing overwrite"):
        native.register_worker(directory)


def test_native_recipe_keeps_control_identity_pinned_tools_and_no_product_execution():
    recipe = (native.ROOT / native.DOCKERFILE).read_text()
    for text in (
        "ARG BASE_IMAGE",
        "FROM ${BASE_IMAGE}",
        "libseccomp2 procps",
        "postgresql-17",
        "redis-server",
        "pnpm@9.15.3",
        "dependency-build.py install",
        "RUN --network=none",
        "USER daytona",
        "--package-import-method=copy",
        "--ignore-scripts",
        "--frozen-lockfile",
        "--store-dir /opt/rnd/pnpm-store",
        "node_modules/vue/package.json",
        "UV_OFFLINE=1",
        "WORKDIR /opt/rnd/control",
        "ENTRYPOINT []",
        "CMD []",
    ):
        assert text in recipe
    assert recipe.rstrip().endswith("USER 0:0")
    assert "warm.py" not in recipe and "vite build" not in recipe
    assert "CAPABILITY_EXECUTION_ENABLED" not in recipe


@pytest.mark.parametrize(
    "key",
    ["key\nREMOTE=x", "key;touch-payload", "key$(payload)", "key'quoted", "", None],
)
def test_existing_key_cannot_inject_environment_or_shell_syntax(key):
    with pytest.raises(ValueError, match="safely written"):
        native.environment_text(key, "rnd-native-fastapiadmin-" + "a" * 16)


def test_existing_native_environment_must_remain_private(prepared):
    if os.name == "nt":
        pytest.skip("POSIX file-mode contract")
    directory, record, _ = prepared
    atomic_text(directory / "api-key.json", json.dumps({"value": KEY}))
    path = directory / native.ENVIRONMENT
    atomic_text(path, native.environment_text(KEY, record["snapshot"]["snapshot"]))
    path.chmod(0o644)
    with pytest.raises(ValueError, match="private permissions"):
        native.register_worker(directory)


def test_native_metadata_cannot_be_adopted_through_a_symlink(prepared, tmp_path):
    directory, record, _ = prepared
    outside = tmp_path / "other-record.json"
    atomic_text(outside, json.dumps(record))
    (directory / native.LOCK).unlink()
    (directory / native.LOCK).symlink_to(outside)
    with pytest.raises(ValueError):
        native.require_native_profile(directory)


@pytest.mark.parametrize("form", ["header", "footer", "process", "continued-process"])
@pytest.mark.parametrize("run", [row[1] for row in native.REVIEWED_RUNS])
def test_build_diagnostics_match_only_complete_reviewed_run_commands(form, run):
    (stage, command), _ = next(
        (key, value) for key, value in native.reviewed_run_commands().items() if value == run
    )
    if form == "header":
        log = f"#19 [{stage} 7/16] RUN {command}\n#19 ERROR: private failure"
    elif form == "footer":
        log = f" > [{stage} 7/16] RUN {command}:\nprivate failure"
    else:
        if form == "continued-process":
            command = command.replace(" && ", " \\\n    && ")
        process = json.dumps("/bin/sh -c " + command)
        log = (
            f"ERROR: failed to solve: process {process} did not complete successfully: exit code: 1"
        )
    facts = native.build_failure_facts(log)
    assert (facts["stage"], facts["run"]) == (stage, run)
    assert "private" not in json.dumps(facts)
    assert command not in json.dumps(facts)


@pytest.mark.parametrize(
    "signature,category",
    [
        ("Permission denied (os error 13) at cache", "cache-permission-denied"),
        ("error: unexpected argument\nUsage: uv pip sync", "uv-cli-rejected"),
        ("Failed to build a private source", "source-build-failed"),
        ("error: could not compile a private crate", "compiler-failed"),
        ("failed to get private as a dependency of package private", "rust-dependency-failed"),
        ("configured Python interpreter version is newer than PyO3", "python-version-unsupported"),
        ("no matching package named private found in offline mode", "offline-dependency-missing"),
        ("private wheel hash mismatch", "dependency-hash-mismatch"),
        ("failed to download https://private.invalid", "registry-fetch-failed"),
        ("ERR_PNPM_OUTDATED_LOCKFILE private contents", "node-install-failed"),
        ("Dependency symlink escapes the complete image graph", "image-seal-rejected"),
    ],
)
def test_build_diagnostics_emit_only_fixed_known_error_categories(signature, category):
    (stage, command), _ = next(
        (key, value)
        for key, value in native.reviewed_run_commands().items()
        if value == "build-native-sources"
    )
    log = f"#12 [{stage} 6/16] RUN {command}\n#12 ERROR: {signature}"
    value = native.build_failure_facts(log)
    assert category in value["categories"]
    assert signature not in json.dumps(value)
    assert "private" not in json.dumps(value)


def test_build_diagnostics_do_not_adopt_unreviewed_commands_or_ambient_text():
    command = next(iter(native.reviewed_run_commands()))[1] + " && echo private-secret"
    for log in (
        f"#12 [native-system 1/2] RUN {command}\n#12 ERROR: private-secret",
        f"ERROR: process {json.dumps('/bin/sh -c ' + command)} did not complete successfully: exit code: 1",
        "private-package private-path https://private.invalid API_KEY=private-secret\n",
    ):
        assert native.build_failure_facts(log) == {
            "stage": "unknown",
            "run": "unknown",
            "categories": ["unknown"],
        }


@pytest.mark.parametrize("mutation", ["same-count-edit", "reordered", "missing", "oversized"])
def test_diagnostic_run_mapping_requires_exact_reviewed_recipe(tmp_path, monkeypatch, mutation):
    recipe = (native.ROOT / native.DOCKERFILE).read_text()
    commands = list(native.reviewed_run_commands())
    if mutation == "same-count-edit":
        recipe = recipe.replace("libseccomp2 procps", "libseccomp2 unreviewed", 1)
    elif mutation == "reordered":
        first = recipe.index("RUN ")
        second = recipe.index("\nRUN ", first) + 1
        end = recipe.index("\nENV ", second)
        recipe = recipe[:first] + recipe[second:end] + "\n" + recipe[first:second] + recipe[end:]
    elif mutation == "oversized":
        recipe += "#" * (native.DIAGNOSTIC_SCAN_BYTES + 1)
    if mutation != "missing":
        (tmp_path / "Dockerfile").write_text(recipe)
    monkeypatch.setattr(native, "ROOT", tmp_path)
    monkeypatch.setattr(native, "DOCKERFILE", "Dockerfile")
    assert native.reviewed_run_commands() == {}
    stage, command = commands[0]
    result = native.build_failure_facts(f"#1 [{stage} 1/2] RUN {command}\n#1 ERROR: failure")
    assert result == {"stage": "unknown", "run": "unknown", "categories": ["unknown"]}


@pytest.mark.parametrize("code", [-9, 1, True, 1.5, 2**40, "private-secret"])
def test_failure_diagnostics_are_bounded_and_never_serialize_hostile_payloads(code):
    secret = 'private-secret\n"token":"value"\r\x00https://person:password@private.invalid?key=x'
    error = subprocess.CalledProcessError(
        code, [secret], output=(secret + "界") * 20000, stderr=(secret + "\ud800") * 20000
    )
    report = native.failure_diagnostic(
        {"action": "prepare", "stage": "prepare-docker-build"}, error
    )
    encoded = json.dumps(report).encode()
    assert len(encoded) <= native.DIAGNOSTIC_REPORT_BYTES
    assert report["build"]["scanned_bytes"] <= native.DIAGNOSTIC_SCAN_BYTES
    assert report["build"]["truncated"] is True
    assert report["error"]["returncode"] == (
        code if type(code) is int and abs(code) < 2**31 else None
    )
    assert report["error"]["timed_out"] is False
    for fragment in ("private-secret", "password", "private.invalid", "token", "界"):
        assert fragment.encode() not in encoded
    assert (
        native.failure_diagnostic({"action": secret, "stage": secret}, RuntimeError(secret))[
            "stage"
        ]
        == "unknown"
    )


def test_prepare_build_failure_preserves_failure_and_never_writes_readiness(
    prepared, product, monkeypatch
):
    directory, _, _ = prepared
    (directory / native.LOCK).unlink()
    report = directory / "diagnostic.json"
    error = subprocess.CalledProcessError(23, ["private command"], stderr=b"Permission denied")

    def fail(*args, **kwargs):
        assert args[0] == "build" and kwargs == {"timeout": 3600}
        raise error

    monkeypatch.setattr(native.local, "docker", fail)
    with pytest.raises(subprocess.CalledProcessError) as caught:
        native.prepare(product, directory, diagnostics=report)
    assert caught.value is error
    value = json.loads(report.read_text())
    assert value["stage"] == "prepare-docker-build"
    assert value["error"]["returncode"] == 23
    assert not (directory / native.LOCK).exists()
    assert not (directory / native.ENVIRONMENT).exists()
    assert not list(directory.glob("native-capability-build-*"))
    if os.name != "nt":
        assert report.stat().st_mode & 0o777 == 0o600


def test_stale_ready_profile_and_existing_report_cannot_be_overwritten(
    prepared, product, monkeypatch
):
    directory, _, _ = prepared
    before = (directory / native.LOCK).read_bytes()
    monkeypatch.setattr(native.local, "docker", lambda *a, **k: pytest.fail("No build permitted"))
    with pytest.raises(ValueError, match="refuses to overwrite"):
        native.prepare(product, directory, diagnostics=directory / native.LOCK)
    assert (directory / native.LOCK).read_bytes() == before


def test_register_parent_preserves_exact_worker_report_and_failure(prepared, monkeypatch):
    directory, _, _ = prepared
    report = directory / "diagnostic.json"
    error = native.ToolFailure("private parent log")
    error.log = "token=private-child-secret"
    error.returncode = 1
    expected = {}

    def worker(command, cwd, **kwargs):
        assert command[-2:] == ["--diagnostics", str(report.absolute())]
        assert kwargs["timeout"] == 720
        with pytest.raises(subprocess.TimeoutExpired):
            with native.diagnostic_scope(report, "register-worker") as progress:
                progress["stage"] = "register-worker-snapshot-create"
                raise subprocess.TimeoutExpired(
                    "private SDK request", 600, output=b"private-secret"
                )
        expected.update(json.loads(report.read_text()))
        raise error

    monkeypatch.setattr(native, "run_command", worker)
    with pytest.raises(native.ToolFailure) as caught:
        native.register(directory, diagnostics=report)
    assert caught.value is error
    assert json.loads(report.read_text()) == expected
    assert expected["stage"] == "register-worker-snapshot-create"
    assert expected["error"]["timed_out"] is True
    assert "private" not in report.read_text()
    assert not (directory / native.ENVIRONMENT).exists()


@pytest.mark.parametrize("action", ["prepare", "register", "register-worker"])
@pytest.mark.parametrize("diagnostics", [False, True])
def test_native_cli_remains_compatible_and_success_does_not_emit_diagnostics(
    tmp_path, monkeypatch, capsys, action, diagnostics
):
    calls = []
    report = tmp_path / "diagnostic.json"
    command = ["native-profile", action, "--directory", str(tmp_path)]
    if action == "prepare":
        command += ["--product", str(tmp_path / "product")]
    if diagnostics:
        command += ["--diagnostics", str(report)]
    monkeypatch.setattr(sys, "argv", command)
    monkeypatch.setattr(native, action.replace("-", "_"), lambda *a, **k: calls.append((a, k)))
    native.main()
    assert calls[0][1] == ({"diagnostics": report} if diagnostics else {})
    assert not report.exists()
    assert capsys.readouterr().out == (
        "Native snapshot identity step completed; runtime/isolation acceptance is still required.\n"
    )


def test_native_workflow_collects_separate_bounded_prepare_and_register_diagnostics():
    import yaml

    workflow = yaml.safe_load(
        (native.ROOT / ".github/workflows/native-capability-profile.yml").read_text()
    )
    steps = workflow["jobs"]["local-service"]["steps"]
    build = next(
        step
        for step in steps
        if step.get("name") == "Build and register exact native offline dependency profile"
    )
    upload = next(
        step for step in steps if step.get("uses", "").startswith("actions/upload-artifact@")
    )
    assert "--diagnostics reports/native-profile-prepare-diagnostic.json" in build["run"]
    assert "--diagnostics reports/native-profile-register-diagnostic.json" in build["run"]
    assert upload["if"] == "always()"
    assert "reports/native-profile-*-diagnostic.json" in upload["with"]["path"]
````
