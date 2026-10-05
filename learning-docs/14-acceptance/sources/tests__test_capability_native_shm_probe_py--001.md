# tests/test_capability_native_shm_probe.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`workbench.capability_isolation`、`workbench.capability_verification`、`workbench.catalog`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `outside_fragment`（L32–L80）：接收`inside`、`outside`、`legacy_exclusive`。 源码说明：Execute the actual authored outside-write block, changing only owned paths.。 调用`ast.parse`、`next`、`isinstance`、`enumerate`、`ast.Module`、`ast.unparse`、`ast.fix_missing_locations`、`OwnedPaths().visit`、`OwnedPaths`。 返回路径：L80的`ast.unparse(ast.fix_missing_locations(OwnedPaths().visit(module)))`。
- `outside_fragment.OwnedPaths`（L55–L77）：继承`ast.NodeTransformer`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `outside_fragment.OwnedPaths.visit_Constant`（L56–L64）：接收`node`。 控制顺序：L57按`isinstance(node.value, str)`分支；L58遍历`( ("/home/rnd-module", str(outside)), ("/tmp/rnd-capability", str…`；L62按`node.value.startswith(old)`分支。 调用`isinstance`、`str`、`node.value.startswith`、`ast.copy_location`、`ast.Constant`、`len`。 返回路径：L63的`ast.copy_location(ast.Constant(new + node.value[len(old) :]), node)`；L64的`node`。
- `outside_fragment.OwnedPaths.visit_Call`（L66–L77）：接收`node`。 控制顺序：L68按`legacy_exclusive and isinstance(node.func, ast.Name) and node.func.id == "open" and l…`分支。 调用`self.generic_visit`、`isinstance`、`len`、`ast.Constant`。 返回路径：L77的`node`。
- `test_outside_probe_follows_owned_symlink_instead_of_testing_eexist`（L85–L123）：接收`tmp_path`、`legacy`。 控制顺序：L111按`legacy`分支；L116断言`namespace["checks"] == {"native_shm_outside_writes_denied": True}`；L117断言`len(attempted) == 3`；L118断言`attempted[-1][1] == ("xb" if legacy else "ab")`；L119断言`not list(outside.iterdir())`；L121遍历`namespace["paths"]`；L123断言`not list((inside / "tmp").iterdir())`。 调用`(inside / "tmp").mkdir`、`outside.mkdir`、`pytest.raises`、`exec`、`outside_fragment`、`len`、`list`、`outside.iterdir`、`Path(path).unlink`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_outside_probe_follows_owned_symlink_instead_of_testing_eexist.confined_open`（L91–L100）：接收`path`、`mode`。 控制顺序：L95按`mode == "xb" and os.path.lexists(path)`分支；L98按`Path(resolved).resolve().is_relative_to(outside)`分支；L99抛异常，停止当前正常路径。 调用`attempted.append`、`str`、`os.path.lexists`、`builtins.open`、`str(path).removeprefix`、`Path(resolved).resolve().is_relative_to`、`Path(resolved).resolve`、`Path`、`PermissionError`。 返回路径：L96的`builtins.open(path, mode)`；L100的`builtins.open(path, mode)`。
- `test_outside_probe_never_overwrites_an_existing_target`（L127–L136）：接收`tmp_path`。 控制顺序：L136断言`target.read_bytes() == b"keep-owned-fixture" and namespace["paths"] == []`。 调用`(inside / "tmp").mkdir`、`outside.mkdir`、`target.write_bytes`、`pytest.raises`、`exec`、`outside_fragment`、`target.read_bytes`、`pytest.mark.skipif`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_outside_probe_block_remains_denied_by_real_guard`（L140–L171）：接收`tmp_path`。 控制顺序：L166按`result.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1"`分支；L168断言`result.returncode == 0`；L169断言`result.stdout == "outside-write-denied\n" and result.stderr == ""`；L170断言`[path.name for path in outside.iterdir()] == ["writable-before-confinement"]`；L171断言`not list((inside / "tmp").iterdir())`。 调用`(inside / "tmp").mkdir`、`outside.mkdir`、`(outside / "writable-before-confinement").write_bytes`、`outside_fragment`、`Path(__file__).resolve`、`Path`、`str`、`subprocess.run`、`os.environ.get`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `plan`（L174–L175）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`SimpleNamespace`、`Selection`。 返回路径：L175的`SimpleNamespace(selection=Selection(template="fastapiadmin"))`。
- `argv_passthrough`（L178–L182）：接收`plan`、`argv`、`environment`、`native_semaphore_storage`。 控制顺序：L179断言`plan.selection.template == "fastapiadmin"`；L180断言`environment == {} and native_semaphore_storage is True`；L181断言`argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]`。 返回路径：L182的`argv`。
- `test_runtime_requires_exact_true_checkset_and_explicit_guard`（L185–L199）：接收`monkeypatch`。 控制顺序：L194断言`probe.verify_native_shm("owned", plan(), 900) == dict.fromkeys( probe.RUNTIME_CHECKS,…`；L197断言`len(calls) == 1 and calls[0][0] == "owned" and calls[0][2] == 45`；L198断言`calls[0][1][4] == probe.PROBE`；L199断言`len(calls[0][1][5]) == 32`。 调用`monkeypatch.setattr`、`probe.verify_native_shm`、`plan`、`dict.fromkeys`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_requires_exact_true_checkset_and_explicit_guard.guarded`（L189–L191）：接收`sandbox`、`argv`、`timeout`。 调用`calls.append`、`json.dumps`、`dict.fromkeys`。 返回路径：L191的`0, json.dumps(dict.fromkeys(probe.RUNTIME_CHECKS, True))`。
- `test_runtime_rejects_incomplete_or_untrusted_receipts_without_echo`（L214–L221）：接收`monkeypatch`、`status`、`receipt`。 控制顺序：L221断言`"private" not in str(error.value)`。 调用`monkeypatch.setattr`、`json.dumps`、`pytest.raises`、`probe.verify_native_shm`、`plan`、`str`、`pytest.mark.parametrize`、`dict.fromkeys`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_failure_diagnostics_are_finite`（L225–L233）：接收`monkeypatch`、`stage`。 调用`monkeypatch.setattr`、`json.dumps`、`pytest.raises`、`probe.verify_native_shm`、`plan`、`pytest.mark.parametrize`、`sorted`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runtime_parse_errors_are_suppressed`（L237–L243）：接收`monkeypatch`、`output`。 控制顺序：L242断言`error.value.__suppress_context__`；L243断言`"synthetic" not in str(error.value)`。 调用`monkeypatch.setattr`、`pytest.raises`、`probe.verify_native_shm`、`plan`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `marker_runner`（L246–L282）：接收`monkeypatch`、`tmp_path`、`shared`、`corrupt`、`fail_cleanup`。 控制顺序：L247按`not all(hasattr(os, name) for name in ("O_NOFOLLOW", "getuid"))`分支；L253遍历`((FIRST, "first"), (SECOND, "second"))`。 调用`all`、`hasattr`、`pytest.skip`、`root.mkdir`、`monkeypatch.setattr`、`SimpleNamespace`。 返回路径：L282的`roots, calls`。
- `marker_runner.guarded`（L260–L279）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L261断言`argv[4] == probe.MARKER`；L263断言`nonce == NONCE and timeout <= 15`；L265按`fail_cleanup and operation == "cleanup" and sandbox.id == FIRST`分支；L266抛异常，停止当前正常路径；L268按`corrupt and operation == "verify" and sandbox.id == FIRST`分支；L278断言`result.stderr == ""`。 调用`calls.append`、`RuntimeError`、`(root / f"rnd-shm-pair-{NONCE}-shared").write_text`、`probe.MARKER.replace`、`str`、`subprocess.run`。 返回路径：L279的`result.returncode, result.stdout`。
- `execute_pair`（L285–L288）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`probe.verify_native_shm_isolation`、`SimpleNamespace`、`plan`。 返回路径：L286的`probe.verify_native_shm_isolation( SimpleNamespace(id=FIRST), SimpleNamespace(id=SECOND), …`。
- `test_pair_controller_protocol_and_cleanup_remain_cross_platform`（L303–L349）：接收`monkeypatch`、`case`。 源码说明：Data-only channel fixture, separate from real POSIX marker-file tests.。 控制顺序：L340按`case == "isolated"`分支；L341断言`execute_pair() == dict.fromkeys(probe.PAIR_CHECKS, True)`；L342断言`(FIRST, "verify") in calls and (SECOND, "verify") in calls`；L346断言`"untrusted-result" not in str(caught.value)`；L347断言`calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]`；L348按`case != "cleanup"`分支；L349断言`not first and not second`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`execute_pair`、`dict.fromkeys`、`pytest.raises`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pair_controller_protocol_and_cleanup_remain_cross_platform.guarded`（L311–L337）：接收`sandbox`、`argv`、`timeout`。 控制顺序：L312断言`argv[4] == probe.MARKER`；L314断言`nonce == NONCE and timeout <= 15`；L319按`operation == "empty"`分支；L321按`operation == "create"`分支；L322按`case == side + "-create"`分支；L325按`valid`分支；L327按`operation == "verify"`分支；L329按`case == "wrong-token" or case == "second-verify" and side == "second"`分支。后续分支沿下方源码相同行号继续阅读。 调用`calls.append`、`files.update`、`files.get`、`files.clear`、`pytest.fail`。 返回路径：L323的`1, ""`；L330的`0, "untrusted-result"`；L333的`1, ""`。
- `test_real_marker_protocol_checks_both_directions_and_cleans_all_owned_files`（L352–L368）：接收`monkeypatch`、`tmp_path`。 控制顺序：L356断言`execute_pair() == dict.fromkeys(probe.PAIR_CHECKS, True)`；L357断言`calls == [ (FIRST, "empty"), (SECOND, "empty"), (FIRST, "create"), (SECOND, "empty"),…`；L368断言`all(list(root.iterdir()) == [] for root in roots.values())`。 调用`marker_runner`、`execute_pair`、`dict.fromkeys`、`all`、`list`、`root.iterdir`、`roots.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shared_namespace_or_marker_tampering_fails_and_still_cleans`（L372–L379）：接收`monkeypatch`、`tmp_path`、`changes`。 控制顺序：L378断言`calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]`；L379断言`all(list(root.iterdir()) == [] for root in roots.values())`。 调用`marker_runner`、`pytest.raises`、`execute_pair`、`all`、`list`、`root.iterdir`、`roots.values`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_marker_cleanup_failure_still_attempts_second_cleanup`（L382–L389）：接收`monkeypatch`、`tmp_path`。 控制顺序：L386断言`"primary=none; cleanup=failed" in str(error.value)`；L387断言`"synthetic" not in str(error.value)`；L388断言`calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]`；L389断言`list(roots[SECOND].iterdir()) == []`。 调用`marker_runner`、`pytest.raises`、`execute_pair`、`str`、`list`、`roots[SECOND].iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_existing_marker_is_not_deleted_as_probe_property`（L392–L399）：接收`monkeypatch`、`tmp_path`。 控制顺序：L398断言`original.read_text() == "preexisting"`；L399断言`(SECOND, "cleanup") not in calls`。 调用`marker_runner`、`original.write_text`、`pytest.raises`、`execute_pair`、`original.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pair_requires_distinct_known_sandboxes_before_any_command`（L403–L408）：接收`monkeypatch`、`identifier`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`probe.verify_native_shm_isolation`、`SimpleNamespace`、`plan`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `container_evidence`（L411–L432）：接收`identifier`。 返回路径：L412的`{ "profile": "native-fastapiadmin-postgresql-v1", "sandbox_id": identifier, "control_user"…`。
- `lifecycle`（L435–L536）：接收`monkeypatch`、`create_error`、`delete_error`、`foreign`、`unknown`。 调用`plan().selection.model_dump`、`plan`、`SimpleNamespace`、`events.append`、`container_evidence`、`monkeypatch.setattr`。 返回路径：L534的`SimpleNamespace( execute=execute, events=events, record=record, evidence=evidence, first=f…`。
- `lifecycle.params`（L448–L456）：接收`settings`、`name`、`template`、`selection`。 调用`events.append`、`SimpleNamespace`。 返回路径：L450的`SimpleNamespace( name=name, snapshot="owned-native", network_block_all=True, public=False,…`。
- `lifecycle.create`（L458–L466）：接收`parameters`、`timeout`。 控制顺序：L462按`foreign`分支；L464按`create_error`分支；L465抛异常，停止当前正常路径。 调用`events.append`、`dict`、`RuntimeError`。 返回路径：L466的`peer`。
- `lifecycle.get`（L468–L472）：接收`name`。 控制顺序：L470按`unknown`分支；L471抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。 返回路径：L472的`peer`。
- `lifecycle.delete`（L474–L478）：接收`sandbox`、`timeout`。 控制顺序：L475断言`sandbox is peer`；L477按`delete_error`分支；L478抛异常，停止当前正常路径。 调用`events.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `lifecycle.inspect`（L480–L484）：接收`directory`、`identifier`、`require_resources`、`selection`。 控制顺序：L481断言`directory == "owned-directory" and require_resources is True`；L482断言`selection == record["selection"]`。 调用`events.append`。 返回路径：L484的`evidence[identifier]`。
- `lifecycle.binding`（L486–L489）：接收`current_record`、`container`。 控制顺序：L487断言`current_record is record`；L488按`container.get("snapshot_image_id") != SNAPSHOT`分支；L489抛异常，停止当前正常路径。 调用`container.get`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `lifecycle.prepare`（L491–L494）：接收`sandbox`、`selected_plan`、`timeout`、`native_semaphore_storage`。 控制顺序：L492断言`sandbox is peer and native_semaphore_storage is True`。 调用`events.append`、`dict`。 返回路径：L494的`{"native_shared_memory": dict(NATIVE_SHARED_MEMORY_EVIDENCE)}`。
- `lifecycle.pair`（L496–L499）：接收`one`、`two`、`selected_plan`、`timeout`。 控制顺序：L497断言`one is first and two is peer`。 调用`events.append`、`dict.fromkeys`。 返回路径：L499的`dict.fromkeys(probe.PAIR_CHECKS, True)`。
- `lifecycle.docker`（L501–L518）：接收`*args`、`**kwargs`。 控制顺序：L503断言`args == ( "exec", RUNNER, "docker", "--host", "unix:///var/run/docker.sock", "contain…`；L517断言`set(kwargs) == {"timeout"} and 0 < kwargs["timeout"] <= 15`。 调用`events.append`、`set`。 返回路径：L518的`""`。
- `lifecycle.execute`（L529–L532）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`probe.verify_native_shm_peer`、`plan`。 返回路径：L530的`probe.verify_native_shm_peer( client, settings, "owned-directory", record, first, plan(), …`。
- `test_peer_lifecycle_uses_same_sdk_profile_and_proves_physical_cleanup`（L539–L564）：接收`monkeypatch`。 控制顺序：L541断言`fixture.execute() == {"cross_container_shm_private": True, "peer_cleanup": True}`；L544断言`creation.os_user == "root"`；L545断言`creation.name == "rnd-source-native-shm-peer-" + NONCE`；L546断言`creation.labels["rnd-shm-probe"] == NONCE`；L547断言`[event[0] for event in events] == [ "refresh", "inspect", "params", "create", "refres…`；L561断言`[event[1:] for event in events if event[0] == "folder"] == [ ("/tmp/rnd-capability", …`。 调用`lifecycle`、`fixture.execute`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_incoming_native_binding_creates_no_peer`（L579–L584）：接收`monkeypatch`、`change`。 控制顺序：L584断言`not any(event[0] in {"create", "get", "delete", "docker"} for event in fixture.events…`。 调用`lifecycle`、`change`、`pytest.raises`、`fixture.execute`、`any`、`pytest.mark.parametrize`、`f.evidence[FIRST].update`、`f.record["snapshot"].update`、`setattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_peer_wrong_image_is_deleted_without_identity_preparation`（L587–L593）：接收`monkeypatch`。 控制顺序：L592断言`not any(event[0] == "prepare" for event in fixture.events)`；L593断言`[event[0] for event in fixture.events][-2:] == ["delete", "docker"]`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_create_recovers_exact_owned_name_without_recreating`（L596–L603）：接收`monkeypatch`。 控制顺序：L600断言`"synthetic" not in str(error.value)`；L601断言`[event[0] for event in fixture.events].count("create") == 1`；L602断言`("get", "rnd-source-native-shm-peer-" + NONCE) in fixture.events`；L603断言`[event[0] for event in fixture.events][-2:] == ["delete", "docker"]`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`str`、`[event[0] for event in fixture.events].count`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_uncertain_or_foreign_ownership_never_deletes_another_container`（L607–L611）：接收`monkeypatch`、`changes`。 控制顺序：L611断言`not any(event[0] in {"delete", "docker"} for event in fixture.events)`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sdk_delete_failure_prevents_any_success`（L614–L620）：接收`monkeypatch`。 控制顺序：L618断言`"synthetic" not in str(error.value)`；L619断言`error.value.__suppress_context__`；L620断言`fixture.events[-1][0] == "delete"`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_dangling_physical_container_cannot_certify_cleanup`（L623–L629）：接收`monkeypatch`。 调用`lifecycle`、`monkeypatch.setattr`、`iter`、`next`、`pytest.raises`、`fixture.execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_empty_stdout_from_failed_docker_command_is_not_cleanup`（L632–L640）：接收`monkeypatch`。 调用`lifecycle`、`monkeypatch.setattr`、`pytest.raises`、`fixture.execute`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_empty_stdout_from_failed_docker_command_is_not_cleanup.failed`（L635–L636）：接收`*args`、`**kwargs`。 控制顺序：L636抛异常，停止当前正常路径。 调用`subprocess.CalledProcessError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_native_profiles_never_execute_or_create`（L643–L651）：接收`monkeypatch`。 调用`monkeypatch.setattr`、`pytest.fail`、`SimpleNamespace`、`Selection`、`pytest.raises`、`probe.verify_native_shm`、`probe.verify_native_shm_isolation`、`probe.verify_native_shm_peer`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_peer_environment_cannot_silently_skip_live_evidence`（L654–L656）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`pytest.raises`、`probe.verify_native_shm_peer`、`plan`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_diagnostic_keeps_only_own_validated_recovery_identifiers`（L667–L680）：接收`monkeypatch`、`changes`、`identifier`、`stage`。 控制顺序：L674断言`diagnostic == { "peer_name": "rnd-source-native-shm-peer-" + NONCE, "peer_id": identi…`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`probe.native_shm_cleanup_diagnostic`、`changes.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsafe_cleanup_diagnostics_never_serialize`（L695–L700）：接收`field`、`value`。 控制顺序：L700断言`probe.native_shm_cleanup_diagnostic(error) == {}`。 调用`probe.NativeShmCleanupFailure`、`probe.native_shm_cleanup_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ordinary_exception_attributes_cannot_impersonate_cleanup_diagnostic`（L703–L706）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L706断言`probe.native_shm_cleanup_diagnostic(error) == {}`。 调用`CheckFailure`、`probe.native_shm_cleanup_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_peer_cannot_expand_existing_native_resource_gates`（L721–L726）：接收`monkeypatch`、`key`、`value`。 控制顺序：L726断言`not any(event[0] == "create" for event in fixture.events)`。 调用`lifecycle`、`pytest.raises`、`fixture.execute`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_physical_cleanup_lookup_rejects_noncanonical_identifiers`（L730–L733）：接收`monkeypatch`、`identifier`。 调用`monkeypatch.setattr`、`pytest.fail`、`pytest.raises`、`probe._require_peer_absent`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_native_shm_probe.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L733。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`28949`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_native_shm_probe.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "24f2ab9bbbe2b9a500c9c32eb6ca4f738bf638a2715bad3247db5ad351473f76"} -->
````python
# tests/test_capability_native_shm_probe.py
"""Probe protocol and owned peer lifecycle tests, not a live shm certificate.

The marker programs use only test-owned ordinary directories here. Actual
64MiB /dev/shm allocation and spawn workers run exclusively in native CI's
approved disposable containers, never against a developer machine's shm root.
"""

import ast
import builtins
import errno
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import capability_native_shm_probe as probe
from workbench.capability_isolation import NATIVE_SHARED_MEMORY_EVIDENCE
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection

FIRST = "11111111-1111-1111-1111-111111111111"
SECOND = "22222222-2222-2222-2222-222222222222"
NONCE = "a" * 32
RUNNER = "b" * 64
SNAPSHOT = "sha256:" + "c" * 64


def outside_fragment(inside, outside, *, legacy_exclusive=False):
    """Execute the actual authored outside-write block, changing only owned paths."""
    tree = ast.parse(probe.PROBE)
    denied = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "denied"
    )
    body = next(node.body for node in tree.body if isinstance(node, ast.Try))
    start = next(
        index
        for index, node in enumerate(body)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and node.value.value == "outside"
    )
    end = next(
        index
        for index, node in enumerate(body[start:], start)
        if isinstance(node, ast.Assign)
        and isinstance(node.targets[0], ast.Subscript)
        and isinstance(node.targets[0].slice, ast.Constant)
        and node.targets[0].slice.value == "native_shm_outside_writes_denied"
    )

    class OwnedPaths(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str):
                for old, new in (
                    ("/home/rnd-module", str(outside)),
                    ("/tmp/rnd-capability", str(inside)),
                ):
                    if node.value.startswith(old):
                        return ast.copy_location(ast.Constant(new + node.value[len(old) :]), node)
            return node

        def visit_Call(self, node):
            self.generic_visit(node)
            if (
                legacy_exclusive
                and isinstance(node.func, ast.Name)
                and node.func.id == "open"
                and len(node.args) == 2
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "escape"
            ):
                node.args[1] = ast.Constant("xb")
            return node

    module = ast.Module(body=[denied, *body[start : end + 1]], type_ignores=[])
    return ast.unparse(ast.fix_missing_locations(OwnedPaths().visit(module)))


@pytest.mark.skipif(os.name != "posix", reason="Actual POSIX symlink/O_EXCL fixture")
@pytest.mark.parametrize("legacy", [False, True])
def test_outside_probe_follows_owned_symlink_instead_of_testing_eexist(tmp_path, legacy):
    inside, outside = tmp_path / "inside", tmp_path / "outside"
    (inside / "tmp").mkdir(parents=True)
    outside.mkdir()
    attempted = []

    def confined_open(path, mode):
        attempted.append((str(path), mode))
        # Real O_EXCL refuses a symlink before resolving its target, independent
        # of filesystem confinement. The remaining permission check is modeled.
        if mode == "xb" and os.path.lexists(path):
            return builtins.open(path, mode)
        resolved = str(path).removeprefix("/proc/self/root")
        if Path(resolved).resolve().is_relative_to(outside):
            raise PermissionError(errno.EACCES, "owned fixture permission denial")
        return builtins.open(path, mode)

    namespace = {
        "os": os,
        "errno": errno,
        "nonce": NONCE,
        "paths": [],
        "checks": {},
        "open": confined_open,
    }
    try:
        if legacy:
            with pytest.raises(AssertionError):
                exec(outside_fragment(inside, outside, legacy_exclusive=True), namespace)
        else:
            exec(outside_fragment(inside, outside), namespace)
            assert namespace["checks"] == {"native_shm_outside_writes_denied": True}
        assert len(attempted) == 3
        assert attempted[-1][1] == ("xb" if legacy else "ab")
        assert not list(outside.iterdir())
    finally:
        for path in namespace["paths"]:
            Path(path).unlink(missing_ok=True)
    assert not list((inside / "tmp").iterdir())


@pytest.mark.skipif(os.name != "posix", reason="Actual POSIX symlink target fixture")
def test_outside_probe_never_overwrites_an_existing_target(tmp_path):
    inside, outside = tmp_path / "inside", tmp_path / "outside"
    (inside / "tmp").mkdir(parents=True)
    outside.mkdir()
    target = outside / ("rnd-shm-" + NONCE + "-outside")
    target.write_bytes(b"keep-owned-fixture")
    namespace = {"os": os, "errno": errno, "nonce": NONCE, "paths": [], "checks": {}}
    with pytest.raises(AssertionError):
        exec(outside_fragment(inside, outside), namespace)
    assert target.read_bytes() == b"keep-owned-fixture" and namespace["paths"] == []


@pytest.mark.skipif(sys.platform != "linux", reason="Real Linux Landlock outside-write check")
def test_actual_outside_probe_block_remains_denied_by_real_guard(tmp_path):
    inside, outside = tmp_path / "inside", tmp_path / "outside"
    (inside / "tmp").mkdir(parents=True)
    outside.mkdir()
    (outside / "writable-before-confinement").write_bytes(b"owned")
    command = (
        "import os,errno\n"
        + f"nonce={NONCE!r};paths=[];checks={{}}\n"
        + outside_fragment(inside, outside)
    )
    command += (
        "\nassert checks=={'native_shm_outside_writes_denied':True}\nprint('outside-write-denied')"
    )
    guard = Path(__file__).resolve().parents[1] / "scripts/capability_guard.py"
    source = f"""
import ctypes,runpy,sys
libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
if libc.syscall(444,0,0,1)<6:sys.exit(78)
module=runpy.run_path({str(guard)!r})
module['main'].__globals__['WRITABLE_ROOT']={str(inside)!r}
sys.argv=['guard','8123','','--',sys.executable,'-I','-S','-c',{command!r}]
module['main']()
"""
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", source], capture_output=True, text=True, timeout=15
    )
    if result.returncode == 78 and os.environ.get("RND_REQUIRE_LANDLOCK") != "1":
        pytest.skip("Host kernel/security profile cannot run mandatory live Landlock checks")
    assert result.returncode == 0, result.stderr
    assert result.stdout == "outside-write-denied\n" and result.stderr == ""
    assert [path.name for path in outside.iterdir()] == ["writable-before-confinement"]
    assert not list((inside / "tmp").iterdir())


def plan():
    return SimpleNamespace(selection=Selection(template="fastapiadmin"))


def argv_passthrough(plan, argv, environment, *, native_semaphore_storage=False):
    assert plan.selection.template == "fastapiadmin"
    assert environment == {} and native_semaphore_storage is True
    assert argv[:4] == ["/usr/bin/python3", "-I", "-S", "-c"]
    return argv


def test_runtime_requires_exact_true_checkset_and_explicit_guard(monkeypatch):
    calls = []
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)

    def guarded(sandbox, argv, timeout):
        calls.append((sandbox, argv, timeout))
        return 0, json.dumps(dict.fromkeys(probe.RUNTIME_CHECKS, True))

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    assert probe.verify_native_shm("owned", plan(), 900) == dict.fromkeys(
        probe.RUNTIME_CHECKS, True
    )
    assert len(calls) == 1 and calls[0][0] == "owned" and calls[0][2] == 45
    assert calls[0][1][4] == probe.PROBE
    assert len(calls[0][1][5]) == 32


@pytest.mark.parametrize(
    "status,receipt",
    [
        (1, dict.fromkeys(probe.RUNTIME_CHECKS, True)),
        (0, dict.fromkeys(probe.RUNTIME_CHECKS, 1)),
        (0, dict.fromkeys(probe.RUNTIME_CHECKS[:-1], True)),
        (0, {**dict.fromkeys(probe.RUNTIME_CHECKS, True), "private-path": "/private"}),
        (0, []),
        (1, {"passed": False, "stage": "synthetic-private-log"}),
        (1, {"passed": False, "stage": []}),
    ],
)
def test_runtime_rejects_incomplete_or_untrusted_receipts_without_echo(
    monkeypatch, status, receipt
):
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)
    monkeypatch.setattr(probe, "run_guarded_control", lambda *args: (status, json.dumps(receipt)))
    with pytest.raises(CheckFailure, match="stage=unknown") as error:
        probe.verify_native_shm(None, plan(), 30)
    assert "private" not in str(error.value)


@pytest.mark.parametrize("stage", sorted(probe.FAILURE_STAGES))
def test_runtime_failure_diagnostics_are_finite(monkeypatch, stage):
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)
    monkeypatch.setattr(
        probe,
        "run_guarded_control",
        lambda *args: (1, json.dumps({"passed": False, "stage": stage})),
    )
    with pytest.raises(CheckFailure, match=f"stage={stage}"):
        probe.verify_native_shm(None, plan(), 30)


@pytest.mark.parametrize("output", ["synthetic-private-log", "", '{"stage":'])
def test_runtime_parse_errors_are_suppressed(monkeypatch, output):
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)
    monkeypatch.setattr(probe, "run_guarded_control", lambda *args: (1, output))
    with pytest.raises(CheckFailure) as error:
        probe.verify_native_shm(None, plan(), 30)
    assert error.value.__suppress_context__
    assert "synthetic" not in str(error.value)


def marker_runner(monkeypatch, tmp_path, *, shared=False, corrupt=False, fail_cleanup=False):
    if not all(hasattr(os, name) for name in ("O_NOFOLLOW", "getuid")):
        pytest.skip(
            "Actual POSIX no-follow/ownership marker program; protocol tests remain enabled"
        )
    roots = {}
    calls = []
    for identifier, name in ((FIRST, "first"), (SECOND, "second")):
        root = tmp_path / ("shared" if shared else name)
        root.mkdir(exist_ok=True)
        roots[identifier] = root
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex=NONCE))

    def guarded(sandbox, argv, timeout):
        assert argv[4] == probe.MARKER
        operation, nonce, side = argv[5:]
        assert nonce == NONCE and timeout <= 15
        calls.append((sandbox.id, operation))
        if fail_cleanup and operation == "cleanup" and sandbox.id == FIRST:
            raise RuntimeError("synthetic-private-error")
        root = roots[sandbox.id]
        if corrupt and operation == "verify" and sandbox.id == FIRST:
            (root / f"rnd-shm-pair-{NONCE}-shared").write_text("wrong")
        source = probe.MARKER.replace("SHM='/dev/shm'", f"SHM={str(root)!r}")
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", source, operation, nonce, side],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # The helper never emits raw failure diagnostics, even on bad contents.
        assert result.stderr == ""
        return result.returncode, result.stdout

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    return roots, calls


def execute_pair():
    return probe.verify_native_shm_isolation(
        SimpleNamespace(id=FIRST), SimpleNamespace(id=SECOND), plan(), 30
    )


@pytest.mark.parametrize(
    "case",
    [
        "isolated",
        "shared",
        "first-create",
        "second-create",
        "wrong-token",
        "second-verify",
        "cleanup",
    ],
)
def test_pair_controller_protocol_and_cleanup_remain_cross_platform(monkeypatch, case):
    """Data-only channel fixture, separate from real POSIX marker-file tests."""
    first, second = {}, {}
    stores = {FIRST: first, SECOND: first if case == "shared" else second}
    calls = []
    monkeypatch.setattr(probe, "product_argv", argv_passthrough)
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex=NONCE))

    def guarded(sandbox, argv, timeout):
        assert argv[4] == probe.MARKER
        operation, nonce, side = argv[5:]
        assert nonce == NONCE and timeout <= 15
        calls.append((sandbox.id, operation))
        files = stores[sandbox.id]
        other = "second" if side == "first" else "first"
        valid = True
        if operation == "empty":
            valid = not files
        elif operation == "create":
            if case == side + "-create":
                return 1, ""
            valid = not files
            if valid:
                files.update({side: side, "shared": side})
        elif operation == "verify":
            valid = other not in files and files.get(side) == files.get("shared") == side
            if case == "wrong-token" or case == "second-verify" and side == "second":
                return 0, "untrusted-result"
        elif operation == "cleanup":
            if case == "cleanup" and sandbox.id == FIRST:
                return 1, ""
            files.clear()
        else:
            pytest.fail("Unexpected marker protocol operation")
        return (0, probe.COMPLETE) if valid else (1, "")

    monkeypatch.setattr(probe, "run_guarded_control", guarded)
    if case == "isolated":
        assert execute_pair() == dict.fromkeys(probe.PAIR_CHECKS, True)
        assert (FIRST, "verify") in calls and (SECOND, "verify") in calls
    else:
        with pytest.raises(CheckFailure) as caught:
            execute_pair()
        assert "untrusted-result" not in str(caught.value)
    assert calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]
    if case != "cleanup":
        assert not first and not second


def test_real_marker_protocol_checks_both_directions_and_cleans_all_owned_files(
    monkeypatch, tmp_path
):
    roots, calls = marker_runner(monkeypatch, tmp_path)
    assert execute_pair() == dict.fromkeys(probe.PAIR_CHECKS, True)
    assert calls == [
        (FIRST, "empty"),
        (SECOND, "empty"),
        (FIRST, "create"),
        (SECOND, "empty"),
        (SECOND, "create"),
        (FIRST, "verify"),
        (SECOND, "verify"),
        (FIRST, "cleanup"),
        (SECOND, "cleanup"),
    ]
    assert all(list(root.iterdir()) == [] for root in roots.values())


@pytest.mark.parametrize("changes", [{"shared": True}, {"corrupt": True}])
def test_shared_namespace_or_marker_tampering_fails_and_still_cleans(
    monkeypatch, tmp_path, changes
):
    roots, calls = marker_runner(monkeypatch, tmp_path, **changes)
    with pytest.raises(CheckFailure, match="隔离未确认"):
        execute_pair()
    assert calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]
    assert all(list(root.iterdir()) == [] for root in roots.values())


def test_marker_cleanup_failure_still_attempts_second_cleanup(monkeypatch, tmp_path):
    roots, calls = marker_runner(monkeypatch, tmp_path, fail_cleanup=True)
    with pytest.raises(CheckFailure) as error:
        execute_pair()
    assert "primary=none; cleanup=failed" in str(error.value)
    assert "synthetic" not in str(error.value)
    assert calls[-2:] == [(FIRST, "cleanup"), (SECOND, "cleanup")]
    assert list(roots[SECOND].iterdir()) == []


def test_existing_marker_is_not_deleted_as_probe_property(monkeypatch, tmp_path):
    roots, calls = marker_runner(monkeypatch, tmp_path)
    original = roots[SECOND] / f"rnd-shm-pair-{NONCE}-first"
    original.write_text("preexisting")
    with pytest.raises(CheckFailure, match="second-empty"):
        execute_pair()
    assert original.read_text() == "preexisting"
    assert (SECOND, "cleanup") not in calls


@pytest.mark.parametrize("identifier", [FIRST, "", None])
def test_pair_requires_distinct_known_sandboxes_before_any_command(monkeypatch, identifier):
    monkeypatch.setattr(probe, "run_guarded_control", lambda *a: pytest.fail("command ran"))
    with pytest.raises(CheckFailure):
        probe.verify_native_shm_isolation(
            SimpleNamespace(id=FIRST), SimpleNamespace(id=identifier), plan(), 30
        )


def container_evidence(identifier):
    return {
        "profile": "native-fastapiadmin-postgresql-v1",
        "sandbox_id": identifier,
        "control_user": "0:0",
        "privileged": False,
        "seccomp": "docker-default",
        "seccomp_engine": "builtin",
        "trusted_readonly_binary_mounts": True,
        "runner_image_id": "sha256:" + RUNNER,
        "snapshot_image_id": SNAPSHOT,
        "snapshot_digest": "registry:6000/rnd-native-fastapiadmin@" + SNAPSHOT,
        "shared_memory": {"ipc_mode": "private", "size_bytes": 64 * 1024 * 1024},
        "resource_limits": {
            "cpu_period": 100000,
            "cpu_quota": 200000,
            "memory": 6 * 1024**3,
            "memory_swap": 6 * 1024**3,
            "tmpfs_bytes": 4294967296,
            "pids": 384,
        },
    }


def lifecycle(monkeypatch, *, create_error=False, delete_error=False, foreign=False, unknown=False):
    events = []
    record = {"selection": plan().selection.model_dump(), "snapshot": {"snapshot": "owned-native"}}
    settings = SimpleNamespace(sandbox_provider="daytona")
    first = SimpleNamespace(id=FIRST, network_block_all=True, public=False)
    first.refresh_data = lambda: events.append(("refresh", FIRST))
    peer = SimpleNamespace(id=SECOND, network_block_all=True, public=False)
    peer.refresh_data = lambda: events.append(("refresh", SECOND))
    peer.fs = SimpleNamespace(create_folder=lambda *args: events.append(("folder", *args)))
    evidence = {FIRST: container_evidence(FIRST), SECOND: container_evidence(SECOND)}
    monkeypatch.setattr(probe.uuid, "uuid4", lambda: SimpleNamespace(hex=NONCE))
    monkeypatch.setattr(probe, "snapshot_for", lambda *args: "owned-native")

    def params(settings, name, template, selection):
        events.append(("params", name, template, selection))
        return SimpleNamespace(
            name=name,
            snapshot="owned-native",
            network_block_all=True,
            public=False,
            labels={"managed-by": "rnd-toolchain", "purpose": "disposable-verification"},
        )

    def create(parameters, *, timeout):
        events.append(("create", parameters, timeout))
        peer.name = parameters.name
        peer.labels = dict(parameters.labels)
        if foreign:
            peer.labels["rnd-shm-probe"] = "foreign"
        if create_error:
            raise RuntimeError("synthetic-private-create-error")
        return peer

    def get(name):
        events.append(("get", name))
        if unknown:
            raise RuntimeError("synthetic-private-lookup-error")
        return peer

    def delete(sandbox, *, timeout):
        assert sandbox is peer
        events.append(("delete", sandbox.id, timeout))
        if delete_error:
            raise RuntimeError("synthetic-private-delete-error")

    def inspect(directory, identifier, *, require_resources, selection):
        assert directory == "owned-directory" and require_resources is True
        assert selection == record["selection"]
        events.append(("inspect", identifier))
        return evidence[identifier]

    def binding(current_record, container):
        assert current_record is record
        if container.get("snapshot_image_id") != SNAPSHOT:
            raise ValueError("synthetic-image-mismatch")

    def prepare(sandbox, selected_plan, timeout, *, native_semaphore_storage):
        assert sandbox is peer and native_semaphore_storage is True
        events.append(("prepare", sandbox.id))
        return {"native_shared_memory": dict(NATIVE_SHARED_MEMORY_EVIDENCE)}

    def pair(one, two, selected_plan, timeout):
        assert one is first and two is peer
        events.append(("pair", one.id, two.id))
        return dict.fromkeys(probe.PAIR_CHECKS, True)

    def docker(*args, **kwargs):
        events.append(("docker", args, kwargs))
        assert args == (
            "exec",
            RUNNER,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "ls",
            "--all",
            "--quiet",
            "--no-trunc",
            "--filter",
            "name=^/" + SECOND + "$",
        )
        assert set(kwargs) == {"timeout"} and 0 < kwargs["timeout"] <= 15
        return ""

    monkeypatch.setattr(probe, "params_for", params)
    monkeypatch.setattr(probe, "inspect_created_sandbox", inspect)
    monkeypatch.setattr(probe, "require_profile_container_binding", binding)
    monkeypatch.setattr(probe, "prepare_identity", prepare)
    monkeypatch.setattr(probe, "verify_native_shm_isolation", pair)
    monkeypatch.setattr(probe, "compose", lambda *args, **kwargs: RUNNER)
    monkeypatch.setattr(probe.local, "docker", docker)
    client = SimpleNamespace(create=create, get=get, delete=delete)

    def execute():
        return probe.verify_native_shm_peer(
            client, settings, "owned-directory", record, first, plan(), 30
        )

    return SimpleNamespace(
        execute=execute, events=events, record=record, evidence=evidence, first=first, peer=peer
    )


def test_peer_lifecycle_uses_same_sdk_profile_and_proves_physical_cleanup(monkeypatch):
    fixture = lifecycle(monkeypatch)
    assert fixture.execute() == {"cross_container_shm_private": True, "peer_cleanup": True}
    events = fixture.events
    creation = next(event[1] for event in events if event[0] == "create")
    assert creation.os_user == "root"
    assert creation.name == "rnd-source-native-shm-peer-" + NONCE
    assert creation.labels["rnd-shm-probe"] == NONCE
    assert [event[0] for event in events] == [
        "refresh",
        "inspect",
        "params",
        "create",
        "refresh",
        "inspect",
        "folder",
        "folder",
        "prepare",
        "pair",
        "delete",
        "docker",
    ]
    assert [event[1:] for event in events if event[0] == "folder"] == [
        ("/tmp/rnd-capability", "711"),
        ("/tmp/rnd-capability/product", "700"),
    ]


@pytest.mark.parametrize(
    "change",
    [
        lambda f: f.evidence[FIRST].update(
            shared_memory={"ipc_mode": "host", "size_bytes": 67108864}
        ),
        lambda f: f.evidence[FIRST].update(resource_limits=False),
        lambda f: f.evidence[FIRST].update(snapshot_image_id="sha256:" + "d" * 64),
        lambda f: f.record["snapshot"].update(snapshot="other-native"),
        lambda f: setattr(f.first, "network_block_all", False),
    ],
)
def test_invalid_incoming_native_binding_creates_no_peer(monkeypatch, change):
    fixture = lifecycle(monkeypatch)
    change(fixture)
    with pytest.raises(CheckFailure, match="stage=admission"):
        fixture.execute()
    assert not any(event[0] in {"create", "get", "delete", "docker"} for event in fixture.events)


def test_peer_wrong_image_is_deleted_without_identity_preparation(monkeypatch):
    fixture = lifecycle(monkeypatch)
    fixture.evidence[SECOND]["snapshot_image_id"] = "sha256:" + "d" * 64
    with pytest.raises(CheckFailure, match="stage=inspect"):
        fixture.execute()
    assert not any(event[0] == "prepare" for event in fixture.events)
    assert [event[0] for event in fixture.events][-2:] == ["delete", "docker"]


def test_partial_create_recovers_exact_owned_name_without_recreating(monkeypatch):
    fixture = lifecycle(monkeypatch, create_error=True)
    with pytest.raises(CheckFailure, match="stage=create") as error:
        fixture.execute()
    assert "synthetic" not in str(error.value)
    assert [event[0] for event in fixture.events].count("create") == 1
    assert ("get", "rnd-source-native-shm-peer-" + NONCE) in fixture.events
    assert [event[0] for event in fixture.events][-2:] == ["delete", "docker"]


@pytest.mark.parametrize("changes", [{"foreign": True}, {"create_error": True, "unknown": True}])
def test_uncertain_or_foreign_ownership_never_deletes_another_container(monkeypatch, changes):
    fixture = lifecycle(monkeypatch, **changes)
    with pytest.raises(CheckFailure, match="cleanup=failed"):
        fixture.execute()
    assert not any(event[0] in {"delete", "docker"} for event in fixture.events)


def test_sdk_delete_failure_prevents_any_success(monkeypatch):
    fixture = lifecycle(monkeypatch, delete_error=True)
    with pytest.raises(CheckFailure, match="primary=none; cleanup=failed") as error:
        fixture.execute()
    assert "synthetic" not in str(error.value)
    assert error.value.__suppress_context__
    assert fixture.events[-1][0] == "delete"


def test_dangling_physical_container_cannot_certify_cleanup(monkeypatch):
    fixture = lifecycle(monkeypatch)
    monkeypatch.setattr(probe.local, "docker", lambda *args, **kwargs: "d" * 64)
    clock = iter((0, 0, 31))
    monkeypatch.setattr(probe.time, "monotonic", lambda: next(clock))
    with pytest.raises(CheckFailure, match="cleanup=failed"):
        fixture.execute()


def test_empty_stdout_from_failed_docker_command_is_not_cleanup(monkeypatch):
    fixture = lifecycle(monkeypatch)

    def failed(*args, **kwargs):
        raise subprocess.CalledProcessError(1, "synthetic", output="")

    monkeypatch.setattr(probe.local, "docker", failed)
    with pytest.raises(CheckFailure, match="cleanup=failed"):
        fixture.execute()


def test_non_native_profiles_never_execute_or_create(monkeypatch):
    monkeypatch.setattr(probe, "run_guarded_control", lambda *args: pytest.fail("command ran"))
    ordinary = SimpleNamespace(selection=Selection())
    with pytest.raises(CheckFailure):
        probe.verify_native_shm(None, ordinary, 30)
    with pytest.raises(CheckFailure):
        probe.verify_native_shm_isolation(None, None, ordinary, 30)
    with pytest.raises(CheckFailure):
        probe.verify_native_shm_peer(None, None, None, None, None, ordinary, 30)


def test_missing_peer_environment_cannot_silently_skip_live_evidence():
    with pytest.raises(CheckFailure, match="SDK"):
        probe.verify_native_shm_peer(None, None, None, None, None, plan(), 30)


@pytest.mark.parametrize(
    "changes,identifier,stage",
    [
        ({"delete_error": True}, SECOND, "delete"),
        ({"foreign": True}, None, "identity"),
        ({"create_error": True, "unknown": True}, None, "recover"),
    ],
)
def test_cleanup_diagnostic_keeps_only_own_validated_recovery_identifiers(
    monkeypatch, changes, identifier, stage
):
    fixture = lifecycle(monkeypatch, **changes)
    with pytest.raises(CheckFailure) as error:
        fixture.execute()
    diagnostic = probe.native_shm_cleanup_diagnostic(error.value)
    assert diagnostic == {
        "peer_name": "rnd-source-native-shm-peer-" + NONCE,
        "peer_id": identifier,
        "primary_stage": "none" if changes.get("delete_error") else "create",
        "cleanup_stage": stage,
        "cleanup": "unconfirmed",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("peer_name", "someone-else"),
        ("peer_id", "unsafe\nprivate-path"),
        ("primary_stage", "private-error"),
        ("primary_stage", []),
        ("cleanup_stage", "private-error"),
        ("cleanup", True),
        ("private-extra", "secret"),
    ],
)
def test_unsafe_cleanup_diagnostics_never_serialize(field, value):
    error = probe.NativeShmCleanupFailure(
        "rnd-source-native-shm-peer-" + NONCE, SECOND, "none", "delete"
    )
    error.diagnostic[field] = value
    assert probe.native_shm_cleanup_diagnostic(error) == {}


def test_ordinary_exception_attributes_cannot_impersonate_cleanup_diagnostic():
    error = CheckFailure("private-error")
    error.diagnostic = {"peer_name": "private", "peer_id": "foreign"}
    assert probe.native_shm_cleanup_diagnostic(error) == {}


@pytest.mark.parametrize(
    "key,value",
    [
        ("cpu_period", True),
        ("cpu_quota", 200001),
        ("memory", 7 * 1024**3),
        ("memory_swap", -1),
        ("pids", 385),
        ("tmpfs_bytes", 4294967297),
        ("new_limit", 1),
    ],
)
def test_peer_cannot_expand_existing_native_resource_gates(monkeypatch, key, value):
    fixture = lifecycle(monkeypatch)
    fixture.evidence[FIRST]["resource_limits"][key] = value
    with pytest.raises(CheckFailure, match="stage=admission"):
        fixture.execute()
    assert not any(event[0] == "create" for event in fixture.events)


@pytest.mark.parametrize("identifier", ["foreign", "../../outside", FIRST + "\n", None])
def test_physical_cleanup_lookup_rejects_noncanonical_identifiers(monkeypatch, identifier):
    monkeypatch.setattr(probe, "compose", lambda *a, **kw: pytest.fail("Docker queried"))
    with pytest.raises(ValueError):
        probe._require_peer_absent(None, identifier, 30)
````
