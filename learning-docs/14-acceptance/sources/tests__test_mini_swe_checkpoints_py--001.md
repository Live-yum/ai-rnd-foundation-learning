# tests/test_mini_swe_checkpoints.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.sla_fixture`、`workbench.coding`、`workbench.coding.ports`、`workbench.core.contracts`、`workbench.errors`、`workbench.filesystem`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `exercise`（L21–L112）：接收`settings`、`tmp_path`、`monkeypatch`、`outcomes`、`bad_edit`、`repeat`、`changed_snapshot`、`cleanup_effect`。 控制顺序：L32按`not agent.worker_python().is_file()`分支；L33断言`not os.environ.get("RND_REQUIRE_V2_TOOLS")`。 调用`agent.worker_python().is_file`、`agent.worker_python`、`os.environ.get`、`pytest.skip`、`design`、`product.mkdir`、`(product / "app.py").write_text`、`settings.model_copy`、`monkeypatch.setattr`。 返回路径：L112的`run, requests, checkpoints, cleaned, product`。
- `exercise.Gateway`（L44–L66）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `exercise.Gateway.complete`（L45–L66）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L47断言`"新库初始化" in instruction`；L49按`number % 2 == 0 or (repeat and number > 2)`分支；L60按`bad_edit == "path"`分支；L62按`bad_edit == "before"`分支。 调用`requests.append`、`deepcopy`、`len`、`AgentTurn`、`AgentTurn.model_validate`。 返回路径：L50的`AgentTurn(operation="submit")`；L64的`AgentTurn.model_validate( {"operation": "edit", "edits": {"explanation": "fixture", "files…`。
- `exercise.Environment`（L68–L76）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `exercise.Environment.write`（L69–L70）：接收`edits`。 调用`snapshot.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `exercise.Environment.snapshot`（L72–L76）：接收`paths`。 控制顺序：L74按`changed_snapshot`分支。 调用`dict`。 返回路径：L76的`result`。
- `exercise.environment`（L79–L84）：接收`*args`。 调用`Environment`、`cleaned.append`、`cleanup_effect`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `exercise.checkpoint`（L86–L95）：接收`s`、`t`、`p`、`candidate`、`deadline`。 控制顺序：L89按`isinstance(result, Exception)`分支；L90抛异常，停止当前正常路径。 调用`checkpoints.append`、`manifest`、`min`、`len`、`isinstance`、`digest`。 返回路径：L91的`{ "passed": result, "source_digest": digest(manifest(candidate)), **({} if result else {"c…`。
- `exercise.run`（L99–L110）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`agent.run_agent`、`Gateway`。 返回路径：L100的`agent.run_agent( settings, Gateway(), "fixture", task, plan, product, tmp_path / "worker",…`。
- `test_failed_submit_repairs_current_candidate_in_same_worker`（L115–L138）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L120断言`len(requests) == 4 and len(checks) == 2 and cleaned == [True]`；L121断言`requests[0]["verification_feedback"] is None`；L122断言`requests[2]["verification_feedback"] == { "passed": False, "source_digest": digest(ch…`；L127断言`requests[2]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]`；L128断言`checks[0][1] == checks[1][1]`；L129断言`checks[0][0] != checks[1][0]`；L130断言`(product / "app.py").read_text() == "# baseline\n"`；L131断言`next(e for e in edits.files if e.path == "app.py").before_sha256 == manifest(product)…`。后续分支沿下方源码相同行号继续阅读。 调用`exercise`、`run`、`len`、`digest`、`(product / "app.py").read_text`、`next`、`manifest`、`json.loads`、`(tmp_path / "worker/agent-budget.json").read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_persistent_failure_exhausts_existing_eight_steps`（L141–L147）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L145断言`len(requests) == 8 and len(checks) == 4 and cleaned == [True]`；L146断言`json.loads((tmp_path / "worker/agent-budget.json").read_text())["requests"] == 16`；L147断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`exercise`、`pytest.raises`、`run`、`len`、`json.loads`、`(tmp_path / "worker/agent-budget.json").read_text`、`(tmp_path / "worker/agent-result.json").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_failures_stop_without_model_repair`（L153–L157）：接收`settings`、`tmp_path`、`monkeypatch`、`failure`。 控制顺序：L157断言`len(requests) == 2 and len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`pytest.raises`、`type`、`run`、`len`、`pytest.mark.parametrize`、`TimeoutError`、`UnsupportedScope`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_never_grants_edit_authority`（L161–L168）：接收`settings`、`tmp_path`、`monkeypatch`、`bad_edit`。 控制顺序：L167断言`not checks and cleaned == [True]`；L168断言`(product / "app.py").read_text() == "# baseline\n"`。 调用`exercise`、`pytest.raises`、`run`、`(product / "app.py").read_text`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_repeated_or_changed_submissions_fail_closed`（L172–L183）：接收`settings`、`tmp_path`、`monkeypatch`、`case`。 控制顺序：L183断言`len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`pytest.raises`、`run`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `bound_check_fixture`（L186–L227）：接收`tmp_path`、`monkeypatch`、`mutate`。 调用`design`、`candidate.mkdir`、`(candidate / "app.py").write_text`、`monkeypatch.setattr`。 返回路径：L227的`plan, task, candidate`。
- `bound_check_fixture.verifier`（L200–L224）：接收`product`、`p`、`scenarios`、`settings`、`**kwargs`。 调用`digest`、`manifest`、`p.model_dump`、`mutate`。 返回路径：L224的`proof`。
- `test_feedback_strips_instructions_unknown_fields_and_paths`（L230–L235）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L233断言`feedback["category"] == "application_startup"`；L234断言`feedback["startup"]["command_exit_code"] == 3`；L235断言`not any(x in json.dumps(feedback) for x in ("secret", "private", "execute"))`。 调用`bound_check_fixture`、`agent.check_candidate`、`time.monotonic`、`any`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_untrusted_or_stale_checkpoint_cannot_finish`（L251–L254）：接收`settings`、`tmp_path`、`monkeypatch`、`mutation`。 调用`bound_check_fixture`、`pytest.raises`、`agent.check_candidate`、`time.monotonic`、`pytest.mark.parametrize`、`p.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_check_deadline_interrupts_exception_handlers_and_runs_cleanup`（L260–L278）：接收`monkeypatch`。 控制顺序：L278断言`events == ["cleanup"] and time.monotonic() - start < 1`。 调用`monkeypatch.setattr`、`time.monotonic`、`pytest.raises`、`sandbox._execute_payload`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_check_deadline_interrupts_exception_handlers_and_runs_cleanup.work`（L265–L272）：接收`payload`、`**kwargs`。 调用`time.sleep`、`events.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_final_oracle_rejection_does_not_reopen_agent_budget`（L281–L293）：接收`settings`、`store`、`monkeypatch`。 调用`Workflow`、`design`、`monkeypatch.setattr`、`pytest.raises`、`workflow.extension_after_verify`、`workflow.extension_after_aggregate`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline`（L297–L323）：接收`settings`、`tmp_path`、`monkeypatch`、`phase`。 控制顺序：L311按`phase == "check"`分支；L322断言`len(requests) == 2 and cleaned == [True]`；L323断言`not (tmp_path / "worker/agent-result.json").exists()`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`exercise`、`pytest.raises`、`run`、`len`、`(tmp_path / "worker/agent-result.json").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline.expire`（L301–L302）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checks_and_cleanup_share_module_deadline.delayed`（L314–L317）：接收`*args`。 调用`original`、`expire`。 返回路径：L317的`value`。
- `test_internal_success_is_not_ledger_acceptance`（L326–L342）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L341断言`ledger._load()["version"] == 0`；L342断言`len(checks) == 1 and cleaned == [True]`。 调用`exercise`、`run`、`design`、`ProductLedger`、`ledger.baseline`、`apply_candidate`、`plan.selection.model_dump`、`pytest.raises`、`ledger.promote`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_completed_business_assertions_are_repairable`（L346–L359）：接收`status`、`body`、`error`。 调用`httpx.Client`、`httpx.MockTransport`、`httpx.Response`、`httpx.ByteStream`、`pytest.raises`、`run_steps`、`HttpStep`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_failure_is_not_business_repair`（L362–L376）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L376断言`not isinstance(error.value, BusinessCheckFailure)`。 调用`httpx.Client`、`httpx.MockTransport`、`pytest.raises`、`run_steps`、`HttpStep`、`isinstance`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_transport_failure_is_not_business_repair.timeout`（L368–L369）：接收`request`。 控制顺序：L369抛异常，停止当前正常路径。 调用`httpx.ReadTimeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_startup_classification_never_turns_infrastructure_into_repair`（L396–L437）：接收`mutation`、`repairable`。 控制顺序：L437断言`("repairable_failure" in scope["receipt"]) is repairable`。 调用`ast.parse`、`inspect.getsource`、`next`、`ast.walk`、`isinstance`、`any`、`exec`、`compile`、`ast.Module`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sdk_download_retains_integer_overload_with_remaining_deadline`（L440–L462）：接收`monkeypatch`。 控制顺序：L458断言`set(env.snapshot(task.allowed_paths)) == set(task.allowed_paths)`；L459断言`len(calls) == len(task.allowed_paths)`。 调用`design`、`coding.DaytonaFiles`、`SimpleNamespace`、`time.monotonic`、`set`、`env.snapshot`、`len`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sdk_download_retains_integer_overload_with_remaining_deadline.download`（L447–L450）：接收`path`、`timeout`。 控制顺序：L448断言`type(timeout) is int and 0 < timeout <= 12`。 调用`type`、`calls.append`。 返回路径：L450的`b"# fixture\n"`。
- `test_actual_verifier_timeout_handler_preserves_owned_cleanup`（L467–L530）：接收`tmp_path`、`delete_fails`、`monkeypatch`。 控制顺序：L525断言`deleted == ["owned"]`；L526断言`timers == [True]`；L527断言`receipt["kind"] == "checkpoint_timeout" and receipt["passed"] is False`；L528断言`receipt["cleanup"] == ("delete-failed" if delete_fails else "deleted")`；L529断言`"repairable_failure" not in receipt`；L530断言`"private" not in json.dumps(receipt)`。 调用`ast.parse`、`inspect.getsource`、`next`、`isinstance`、`ast.Try`、`ast.Raise`、`ast.Name`、`ast.Load`、`vars`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_verifier_timeout_handler_preserves_owned_cleanup.delete`（L487–L490）：接收`value`、`**kwargs`。 控制顺序：L489按`delete_fails`分支；L490抛异常，停止当前正常路径。 调用`deleted.append`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_verifier_timeout_handler_preserves_owned_cleanup.absent`（L492–L495）：接收`identifier`。 控制顺序：L495抛异常，停止当前正常路径。 调用`DaytonaNotFoundError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_locked_sdk_cannot_erase_checkpoint_deadline`（L535–L572）：接收`blocking`。 源码说明：Exercise the real SDK decorator, including the old failing timer setup.。 控制顺序：L544断言`version("daytona") == DAYTONA_VERSION`；L554断言`signal.getitimer(signal.ITIMER_REAL)[0] == 0`；L571断言`events == ["cleaned"] and time.monotonic() - start < 1`；L572断言`signal.getsignal(signal.SIGALRM) == previous`。 调用`version`、`signal.signal`、`signal.setitimer`、`sdk_call`、`signal.getitimer`、`time.monotonic`、`CheckpointDeadline`、`pytest.raises`、`time.sleep`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_locked_sdk_cannot_erase_checkpoint_deadline.sdk_call`（L547–L548）：接收`timeout`、`delay`。 调用`time.sleep`、`with_timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `cleanup_binding`（L575–L587）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`design`、`digest`、`task.model_dump`、`plan.model_dump`。 返回路径：L578的`( task, plan, { "task": digest(task.model_dump()), "plan": digest(plan.model_dump()), "sou…`。
- `test_deletion_requires_typed_absence_after_delete`（L591–L612）：接收`observation`。 控制顺序：L607按`observation == "absent"`分支；L612断言`seen[:2] == ["delete", "owned"]`。 调用`SimpleNamespace`、`seen.append`、`confirm_deleted`、`time.monotonic`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deletion_requires_typed_absence_after_delete.get`（L598–L604）：接收`identifier`。 控制顺序：L600按`observation == "absent"`分支；L601抛异常，停止当前正常路径；L602按`observation == "error"`分支；L603抛异常，停止当前正常路径。 调用`seen.append`、`DaytonaNotFoundError`、`RuntimeError`、`object`。 返回路径：L604的`object()`。
- `test_cleanup_cannot_delete_another_task_sandbox`（L616–L640）：接收`settings`、`monkeypatch`、`mismatch`。 控制顺序：L640断言`not calls`。 调用`cleanup_binding`、`SimpleNamespace`、`calls.append`、`monkeypatch.setattr`、`pytest.raises`、`cleanup.perform`、`time.monotonic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_parent_is_only_terminal_receipt_writer`（L644–L685）：接收`settings`、`tmp_path`、`monkeypatch`、`case`。 控制顺序：L674按`case == "success"`分支；L680断言`value["binding"] == binding`；L681断言`value["status"] == ("deleted" if case == "success" else "unconfirmed")`；L682断言`settings.daytona_api_key.get_secret_value() not in path.read_text() or not settings.d…`。 调用`cleanup_binding`、`monkeypatch.setattr`、`Process`、`time.monotonic`、`cleanup.delete_owned`、`pytest.raises`、`json.loads`、`path.read_text`、`settings.daytona_api_key.get_secret_value`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cleanup_parent_is_only_terminal_receipt_writer.Process`（L651–L663）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_cleanup_parent_is_only_terminal_receipt_writer.Process.communicate`（L654–L660）：接收`body`、`timeout`。 控制顺序：L656断言`request["name"] == name and request["binding"] == binding`；L658按`case == "wrong-binding"`分支。 调用`json.loads`、`dict`、`json.dumps({"binding": value, "deleted": True}).encode`、`json.dumps`。 返回路径：L660的`json.dumps({"binding": value, "deleted": True}).encode(), b""`。
- `test_cleanup_parent_is_only_terminal_receipt_writer.Process.poll`（L662–L663）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L663的`0`。
- `test_real_sdk_thread_timeout_is_cut_off_by_cleanup_supervisor`（L690–L739）：接收`settings`、`tmp_path`、`monkeypatch`、`expired`。 源码说明：A real child and real SDK timeout around blocking C sleep; no SDK mocking.。 控制顺序：L735断言`marker.read_text() == "entered"`；L736断言`time.monotonic() - start < 4`；L737断言`children[0].poll() is not None`；L739断言`value["status"] == "unconfirmed" and value["binding"] == binding`。 调用`cleanup_binding`、`monkeypatch.setattr`、`time.monotonic`、`pytest.raises`、`cleanup.delete_owned`、`marker.read_text`、`children[0].poll`、`json.loads`、`path.read_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_thread_timeout_is_cut_off_by_cleanup_supervisor.launch`（L718–L721）：接收`command`、`**kwargs`。 调用`original`、`str`、`children.append`。 返回路径：L721的`process`。
- `test_public_cleanup_rejects_stale_or_poisoned_receipts`（L752–L764）：接收`tmp_path`、`mutate`。 控制顺序：L761断言`cleanup.public_receipt(path, task, plan) == { "status": "unconfirmed", "reason": "inv…`。 调用`cleanup_binding`、`cleanup.receipt`、`mutate`、`write_json`、`cleanup.public_receipt`、`pytest.mark.parametrize`、`value["binding"].update`、`value.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_cleanup_survives_workspace_deletion_without_raw_sdk_data`（L767–L785）：接收`tmp_path`。 控制顺序：L783断言`not path.exists()`；L784断言`exported["status"] == "unconfirmed" and exported["binding"] == binding`；L785断言`"private" not in json.dumps(exported)`。 调用`cleanup_binding`、`tempfile.TemporaryDirectory`、`Path`、`cleanup.receipt`、`write_json`、`cleanup.public_receipt`、`path.exists`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_checkpoint_cannot_retain_late_pass_or_repair`（L788–L800）：接收`tmp_path`。 控制顺序：L799断言`value["passed"] is False and value["cleanup"] == "unconfirmed"`；L800断言`value["checkpoint"] == checkpoint and "repairable_failure" not in value`。 调用`write_json`、`time.monotonic`、`terminate_checkpoint`、`json.loads`、`path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_thread_timer_alone_cannot_bound_blocking_c_call`（L803–L825）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L825断言`not thread.is_alive() and len(observed) == 1 and observed[0] >= 1.2`。 调用`threading.Thread`、`thread.start`、`thread.join`、`thread.is_alive`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_thread_timer_alone_cannot_bound_blocking_c_call.sdk_call`（L812–L813）：接收`timeout`。 调用`time.sleep`、`with_timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_thread_timer_alone_cannot_bound_blocking_c_call.work`（L815–L820）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`time.monotonic`、`sdk_call`、`observed.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_cleanup_summary_binds_task_and_current_candidate`（L829–L856）：接收`tmp_path`、`wrong_source`。 控制顺序：L852断言`len(result) == 1 and result[0]["cleanup"] == "unconfirmed"`；L853断言`result[0]["binding_valid"] is not wrong_source`；L854断言`"private" not in json.dumps(result)`；L855按`not wrong_source`分支；L856断言`result[0]["binding"]["source"] == source`。 调用`cleanup_binding`、`candidate.mkdir`、`(candidate / "app.py").write_text`、`digest`、`manifest`、`write_json`、`checkpoint_receipts`、`len`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_file_cleanup_tracks_expected_candidate_even_after_partial_upload`（L860–L915）：接收`settings`、`tmp_path`、`monkeypatch`、`fail_write`。 控制顺序：L910按`fail_write`分支；L915断言`operations == ["delete", "closed"]`。 调用`cleanup_binding`、`SimpleNamespace`、`monkeypatch.setattr`、`operations.append`、`pytest.raises`、`run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_file_cleanup_tracks_expected_candidate_even_after_partial_upload.create`（L872–L874）：接收`parameters`、`timeout`。 返回路径：L874的`target`。
- `test_file_cleanup_tracks_expected_candidate_even_after_partial_upload.delete`（L887–L891）：接收`settings`、`name`、`identifier`、`bound`、`path`、`deadline`。 控制顺序：L888断言`name == target.name and identifier == target.id`；L889断言`bound == {**binding, "source": "c" * 64}`；L891断言`json.loads(path.read_text())["binding"] == bound`。 调用`operations.append`、`json.loads`、`path.read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_file_cleanup_tracks_expected_candidate_even_after_partial_upload.run`（L896–L908）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L907按`fail_write`分支；L908抛异常，停止当前正常路径。 调用`coding.coding_environment`、`plan.selection.model_dump`、`time.monotonic`、`environment.bind_candidate`、`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_parent_kills_child_and_freezes_early_success`（L918–L968）：接收`settings`、`tmp_path`、`monkeypatch`。 控制顺序：L965断言`children[0].poll() is not None`；L967断言`value["passed"] is False and value["cleanup"] == "unconfirmed"`；L968断言`value["checkpoint"] == checkpoint and "repairable_failure" not in value`。 调用`fixed_application`、`monkeypatch.setattr`、`digest`、`plan.tasks[0].model_dump`、`time.monotonic`、`pytest.raises`、`verifier.verify_capabilities`、`plan.selection.model_dump`、`children[0].poll`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_checkpoint_parent_kills_child_and_freezes_early_success.launch`（L944–L947）：接收`command`、`**kwargs`。 调用`original`、`children.append`。 返回路径：L947的`process`。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline`（L972–L987）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L987断言`10 <= elapsed < 11.5`。 调用`time.monotonic`、`CheckpointDeadline`、`controller.enter_cleanup`、`pytest.raises`、`cleanup_call`、`pytest.mark.skipif`、`hasattr`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline.cleanup_call`（L978–L979）：接收`timeout`。 调用`time.sleep`、`with_timeout`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_mini_swe_checkpoints.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L987。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`35776`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_mini_swe_checkpoints.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6f93fb85a3d7c1ffb486373bd707bdc03e17708b3b49023d6175bd73fece916f"} -->
````python
# tests/test_mini_swe_checkpoints.py
"""Offline checkpoint control flow; fake proofs are never live acceptance evidence."""

import json
import os
import signal
import time
from contextlib import contextmanager
from copy import deepcopy
from types import SimpleNamespace

import pytest

from scripts.sla_fixture import design
from workbench.coding import mini_swe as agent
from workbench.coding.ports import AgentTurn
from workbench.core.contracts import digest
from workbench.errors import UnsupportedScope
from workbench.filesystem import manifest


def exercise(
    settings,
    tmp_path,
    monkeypatch,
    outcomes,
    *,
    bad_edit=None,
    repeat=False,
    changed_snapshot=False,
    cleanup_effect=lambda: None,
):
    if not agent.worker_python().is_file():
        assert not os.environ.get("RND_REQUIRE_V2_TOOLS"), "mandatory locked Worker missing"
        pytest.skip("optional locked Worker not installed")
    plan = design().implementation
    task = plan.tasks[0]
    product = tmp_path / "product"
    product.mkdir()
    (product / "app.py").write_text("# baseline\n")
    settings = settings.model_copy(update={"mini_swe_enabled": True, "max_context_chars": 20000})
    requests, checkpoints, cleaned = [], [], []
    snapshot = {}

    class Gateway:
        def complete(self, run_id, key, instruction, payload, schema):
            requests.append(deepcopy(payload))
            assert "新库初始化" in instruction
            number = len(requests)
            if number % 2 == 0 or (repeat and number > 2):
                return AgentTurn(operation="submit")
            context = payload["context"]
            files = [
                {
                    "path": name,
                    "before_sha256": context[name]["sha256"],
                    "content": f"# revision {number}\n",
                }
                for name in task.allowed_paths
            ]
            if bad_edit == "path":
                files[0]["path"] = "start.py"
            if bad_edit == "before":
                files[0]["before_sha256"] = "f" * 64
            return AgentTurn.model_validate(
                {"operation": "edit", "edits": {"explanation": "fixture", "files": files}}
            )

    class Environment:
        def write(self, edits):
            snapshot.update({e.path: e.content for e in edits.files})

        def snapshot(self, paths):
            result = dict(snapshot)
            if changed_snapshot:
                result["app.py"] += "# tampered\n"
            return result

    @contextmanager
    def environment(*args):
        try:
            yield Environment()
        finally:
            cleaned.append(True)
            cleanup_effect()

    def checkpoint(s, t, p, candidate, deadline):
        checkpoints.append((manifest(candidate), deadline))
        result = outcomes[min(len(checkpoints) - 1, len(outcomes) - 1)]
        if isinstance(result, Exception):
            raise result
        return {
            "passed": result,
            "source_digest": digest(manifest(candidate)),
            **({} if result else {"category": "application_startup"}),
        }

    monkeypatch.setattr(agent, "check_candidate", checkpoint)

    def run():
        return agent.run_agent(
            settings,
            Gateway(),
            "fixture",
            task,
            plan,
            product,
            tmp_path / "worker",
            {},
            environment_factory=environment,
        )

    return run, requests, checkpoints, cleaned, product


def test_failed_submit_repairs_current_candidate_in_same_worker(settings, tmp_path, monkeypatch):
    run, requests, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [False, True]
    )
    edits = run()
    assert len(requests) == 4 and len(checks) == 2 and cleaned == [True]
    assert requests[0]["verification_feedback"] is None
    assert requests[2]["verification_feedback"] == {
        "passed": False,
        "source_digest": digest(checks[0][0]),
        "category": "application_startup",
    }
    assert requests[2]["context"]["app.py"]["sha256"] == checks[0][0]["app.py"]
    assert checks[0][1] == checks[1][1]  # no fresh verification time window
    assert checks[0][0] != checks[1][0]
    assert (product / "app.py").read_text() == "# baseline\n"
    assert (
        next(e for e in edits.files if e.path == "app.py").before_sha256
        == manifest(product)["app.py"]
    )
    budget = json.loads((tmp_path / "worker/agent-budget.json").read_text())
    assert budget["requests"] == 8
    with pytest.raises(UnsupportedScope, match="重置"):
        run()


def test_persistent_failure_exhausts_existing_eight_steps(settings, tmp_path, monkeypatch):
    run, requests, checks, cleaned, _ = exercise(settings, tmp_path, monkeypatch, [False])
    with pytest.raises((UnsupportedScope, ValueError)):
        run()
    assert len(requests) == 8 and len(checks) == 4 and cleaned == [True]
    assert json.loads((tmp_path / "worker/agent-budget.json").read_text())["requests"] == 16
    assert not (tmp_path / "worker/agent-result.json").exists()


@pytest.mark.parametrize(
    "failure", [TimeoutError("fixed timeout"), UnsupportedScope("cleanup unconfirmed")]
)
def test_checkpoint_failures_stop_without_model_repair(settings, tmp_path, monkeypatch, failure):
    run, requests, checks, cleaned, _ = exercise(settings, tmp_path, monkeypatch, [failure])
    with pytest.raises(type(failure)):
        run()
    assert len(requests) == 2 and len(checks) == 1 and cleaned == [True]


@pytest.mark.parametrize("bad_edit", ["path", "before"])
def test_checkpoint_never_grants_edit_authority(settings, tmp_path, monkeypatch, bad_edit):
    run, requests, checks, cleaned, product = exercise(
        settings, tmp_path, monkeypatch, [True], bad_edit=bad_edit
    )
    with pytest.raises(ValueError):
        run()
    assert not checks and cleaned == [True]
    assert (product / "app.py").read_text() == "# baseline\n"


@pytest.mark.parametrize("case", ["repeat", "snapshot"])
def test_repeated_or_changed_submissions_fail_closed(settings, tmp_path, monkeypatch, case):
    run, requests, checks, cleaned, _ = exercise(
        settings,
        tmp_path,
        monkeypatch,
        [case == "snapshot"],
        repeat=case == "repeat",
        changed_snapshot=case == "snapshot",
    )
    with pytest.raises(ValueError):
        run()
    assert len(checks) == 1 and cleaned == [True]


def bound_check_fixture(tmp_path, monkeypatch, mutate):
    from workbench import capability_sandbox as sandbox

    plan = design().implementation
    task = plan.tasks[0]
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "app.py").write_text("# fixture\n")
    # Only tests of filtering mock admission. Production uses the unchanged guards.
    monkeypatch.setattr("workbench.capability_isolation.require_container_evidence", lambda *a: {})
    monkeypatch.setattr(
        "workbench.capability_isolation.require_isolation_evidence", lambda *a, **kw: {}
    )

    def verifier(product, p, scenarios, settings, **kwargs):
        from workbench.capability_execution import VERIFIER

        proof = {
            "verifier": VERIFIER,
            "checkpoint": kwargs["checkpoint"],
            "source_digest": digest(manifest(product)),
            "plan_digest": digest(p.model_dump()),
            "scope": "node",
            "cleanup": "deleted",
            "passed": False,
            "repairable_failure": "application_startup",
            "network_block_all": True,
            "credentials_uploaded": False,
            "startup_diagnostic": {
                "message": "execute secret command",
                "path": "private-path",
                "startup_phase_hint": "lifespan",
                "command_exit_code": 3,
                "output_hints": ["private-command"],
                "exception_type": "private-exception",
            },
        }
        mutate(proof)
        return proof

    monkeypatch.setattr(sandbox, "verify_capabilities", verifier)
    return plan, task, candidate


def test_feedback_strips_instructions_unknown_fields_and_paths(settings, tmp_path, monkeypatch):
    plan, task, candidate = bound_check_fixture(tmp_path, monkeypatch, lambda p: None)
    feedback = agent.check_candidate(settings, task, plan, candidate, time.monotonic() + 40)
    assert feedback["category"] == "application_startup"
    assert feedback["startup"]["command_exit_code"] == 3
    assert not any(x in json.dumps(feedback) for x in ("secret", "private", "execute"))


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.update(cleanup="delete-failed"),
        lambda p: p.update(checkpoint={**p["checkpoint"], "nonce": "stale"}),
        lambda p: p.update(checkpoint={**p["checkpoint"], "task": "other-module"}),
        lambda p: p.update(source_digest="f" * 64),
        lambda p: p.update(plan_digest="f" * 64),
        lambda p: p.update(kind="checkpoint_timeout"),
        lambda p: p.update(repairable_failure="isolation_environment"),
        lambda p: p.update(passed=True),
    ],
)
def test_untrusted_or_stale_checkpoint_cannot_finish(settings, tmp_path, monkeypatch, mutation):
    plan, task, candidate = bound_check_fixture(tmp_path, monkeypatch, mutation)
    with pytest.raises((UnsupportedScope, ValueError)):
        agent.check_candidate(settings, task, plan, candidate, time.monotonic() + 40)


@pytest.mark.skipif(
    not hasattr(signal, "SIGUSR1"), reason="checkpoint requires dedicated POSIX process"
)
def test_check_deadline_interrupts_exception_handlers_and_runs_cleanup(monkeypatch):
    from workbench import capability_sandbox as sandbox

    events = []

    def work(payload, **kwargs):
        try:
            try:
                time.sleep(1)
            except Exception:
                events.append("incorrectly-swallowed")
        finally:
            events.append("cleanup")

    monkeypatch.setattr(sandbox, "_execute_payload_inner", work)
    start = time.monotonic()
    with pytest.raises(sandbox.CheckpointExpired):
        sandbox._execute_payload({"checkpoint": {"deadline": start + 10.05}})
    assert events == ["cleanup"] and time.monotonic() - start < 1


def test_final_oracle_rejection_does_not_reopen_agent_budget(settings, store, monkeypatch):
    from workbench.flow import Workflow

    workflow = Workflow(settings, store, None)
    selected = design()
    monkeypatch.setattr(workflow, "checked_extension", lambda state: selected)
    monkeypatch.setattr(
        workflow, "extension_task", lambda state, d: selected.implementation.tasks[0]
    )
    with pytest.raises(UnsupportedScope, match="不重启"):
        workflow.extension_after_verify({"extension_candidate_passed": False})
    with pytest.raises(UnsupportedScope, match="不重启"):
        workflow.extension_after_aggregate({"extension_aggregate_passed": False})


@pytest.mark.parametrize("phase", ["check", "cleanup"])
def test_checks_and_cleanup_share_module_deadline(settings, tmp_path, monkeypatch, phase):
    clock = [1000.0]
    monkeypatch.setattr(agent, "time", SimpleNamespace(monotonic=lambda: clock[0], time=time.time))

    def expire():
        clock[0] += 181

    run, requests, checks, cleaned, _ = exercise(
        settings,
        tmp_path,
        monkeypatch,
        [True],
        cleanup_effect=expire if phase == "cleanup" else lambda: None,
    )
    if phase == "check":
        original = agent.check_candidate

        def delayed(*args):
            value = original(*args)
            expire()
            return value

        monkeypatch.setattr(agent, "check_candidate", delayed)
    with pytest.raises(UnsupportedScope):
        run()
    assert len(requests) == 2 and cleaned == [True]
    assert not (tmp_path / "worker/agent-result.json").exists()


def test_internal_success_is_not_ledger_acceptance(settings, tmp_path, monkeypatch):
    from workbench.coding.candidates import apply_candidate
    from workbench.production.candidates import ProductLedger

    run, requests, checks, cleaned, product = exercise(settings, tmp_path, monkeypatch, [True])
    edits = run()
    plan = design().implementation
    ledger = ProductLedger(tmp_path / "ledger", plan)
    ledger.baseline(product)
    candidate = tmp_path / "final"
    apply_candidate(product, edits, plan.tasks[0], plan.selection.model_dump(), candidate)
    with pytest.raises(ValueError):
        ledger.promote(
            candidate, plan.tasks[0], {"passed": False, "cleanup": "deleted"}, manifest(product)
        )
    assert ledger._load()["version"] == 0
    assert len(checks) == 1 and cleaned == [True]


@pytest.mark.parametrize("status,body,error", [(500, b"{}", True), (200, b'{"ok":false}', True)])
def test_only_completed_business_assertions_are_repairable(status, body, error):
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, run_steps

    with httpx.Client(
        base_url="http://fixture.invalid",
        transport=httpx.MockTransport(
            lambda r: httpx.Response(status, stream=httpx.ByteStream(body))
        ),
    ) as client:
        with pytest.raises(BusinessCheckFailure):
            run_steps(client, [HttpStep(path="/check", status=200, equals={"$.ok": True})], {})


def test_transport_failure_is_not_business_repair():
    import httpx

    from workbench.capability_contracts import HttpStep
    from workbench.capability_verification import BusinessCheckFailure, CheckFailure, run_steps

    def timeout(request):
        raise httpx.ReadTimeout("private-transport")

    with httpx.Client(
        base_url="http://fixture.invalid", transport=httpx.MockTransport(timeout)
    ) as client:
        with pytest.raises(CheckFailure) as error:
            run_steps(client, [HttpStep(path="/check", status=200)], {})
    assert not isinstance(error.value, BusinessCheckFailure)


@pytest.mark.parametrize(
    "mutation,repairable",
    [
        ({}, True),
        ({"exception_type": "PermissionError"}, False),
        ({"exception_type": "MemoryError"}, False),
        ({"output_hints": ["storage-full"]}, False),
        ({"output_hints": ["process-terminated"]}, False),
        ({"output_hints": ["memory-error"]}, False),
        ({"output_hints": ["missing-module"]}, False),
        ({"command_exit_status": "unknown"}, False),
        ({"command_exit_code": 137}, False),
        ({"command_exit_code": 143}, False),
        ({"startup_phase_hint": "unknown"}, False),
        ({"application_startup_reported": True}, False),
    ],
)
def test_real_startup_classification_never_turns_infrastructure_into_repair(mutation, repairable):
    import ast
    import inspect

    from workbench import capability_sandbox as sandbox

    tree = ast.parse(inspect.getsource(sandbox._verify))
    block = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and any(
            isinstance(child, ast.Assign)
            and any(
                isinstance(target, ast.Subscript)
                and isinstance(target.slice, ast.Constant)
                and target.slice.value == "repairable_failure"
                for target in child.targets
            )
            and isinstance(child.value, ast.Constant)
            and child.value.value == "application_startup"
            for child in node.body
        )
    )
    scope = {
        "checkpoint": {"nonce": "fixture"},
        "receipt": {},
        "startup": {
            "command_exit_status": "nonzero",
            "command_exit_code": 3,
            "startup_phase_hint": "lifespan",
            "application_startup_reported": False,
            "output_hints": [],
            "exception_type": "other",
            **mutation,
        },
    }
    exec(
        compile(ast.Module(body=[block], type_ignores=[]), "<actual-startup-classifier>", "exec"),
        scope,
    )
    assert ("repairable_failure" in scope["receipt"]) is repairable


def test_sdk_download_retains_integer_overload_with_remaining_deadline(monkeypatch):
    from scripts.sla_fixture import design
    from workbench.infrastructure.sandbox import coding

    task = design().implementation.tasks[0]
    calls = []

    def download(path, timeout):
        assert type(timeout) is int and 0 < timeout <= 12
        calls.append(timeout)
        return b"# fixture\n"

    env = coding.DaytonaFiles(
        SimpleNamespace(fs=SimpleNamespace(download_file=download)),
        task,
        120,
        time.monotonic() + 12.9,
    )
    assert set(env.snapshot(task.allowed_paths)) == set(task.allowed_paths)
    assert len(calls) == len(task.allowed_paths)
    env.deadline = time.monotonic() + 0.1
    with pytest.raises(UnsupportedScope):
        env.snapshot(task.allowed_paths)


@pytest.mark.parametrize("delete_fails", [False, True])
@pytest.mark.skipif(not hasattr(signal, "setitimer"), reason="checkpoint requires POSIX timer")
def test_actual_verifier_timeout_handler_preserves_owned_cleanup(
    tmp_path, delete_fails, monkeypatch
):
    import ast
    import inspect

    from workbench import capability_sandbox as sandbox

    timers = []

    tree = ast.parse(inspect.getsource(sandbox._verify))
    original = next(n for n in tree.body[0].body if isinstance(n, ast.Try))
    tested = ast.Try(
        body=[ast.Raise(exc=ast.Name(id="injected", ctx=ast.Load()), cause=None)],
        handlers=original.handlers,
        orelse=[],
        finalbody=original.finalbody,
    )
    deleted = []

    def delete(value, **kwargs):
        deleted.append(value.id)
        if delete_fails:
            raise RuntimeError("private cleanup text")

    def absent(identifier):
        from daytona.common.errors import DaytonaNotFoundError

        raise DaytonaNotFoundError("owned fixture absent")

    scope = {
        **vars(sandbox),
        "injected": sandbox.CheckpointExpired("fixed timeout"),
        "diagnostic_error": None,
        "oracle_adapter": None,
        "native": False,
        "checkpoint": {"nonce": "fixture", "deadline": time.monotonic() + 10},
        "checkpoint_deadline": SimpleNamespace(enter_cleanup=lambda: timers.append(True)),
        "name": "owned",
        "receipt": {
            "passed": False,
            "cleanup": "pending",
            "repairable_failure": "application_startup",
        },
        "sandbox": SimpleNamespace(id="owned"),
        "client": SimpleNamespace(delete=delete, get=absent),
        "settings": SimpleNamespace(tool_timeout=10),
        "receipt_path": tmp_path / "receipt.json",
    }
    exec(
        compile(
            ast.fix_missing_locations(ast.Module(body=[tested], type_ignores=[])),
            "<actual-timeout-handler>",
            "exec",
        ),
        scope,
    )
    receipt = json.loads((tmp_path / "receipt.json").read_text())
    assert deleted == ["owned"]
    assert timers == [True]
    assert receipt["kind"] == "checkpoint_timeout" and receipt["passed"] is False
    assert receipt["cleanup"] == ("delete-failed" if delete_fails else "deleted")
    assert "repairable_failure" not in receipt
    assert "private" not in json.dumps(receipt)


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="dedicated POSIX verifier")
@pytest.mark.parametrize("blocking", [False, True])
def test_real_locked_sdk_cannot_erase_checkpoint_deadline(blocking):
    """Exercise the real SDK decorator, including the old failing timer setup."""
    from importlib.metadata import version

    from daytona._utils.timeout import with_timeout

    from workbench.infrastructure.sandbox.deadline import CheckpointDeadline, CheckpointExpired
    from workbench.local_only import DAYTONA_VERSION

    assert version("daytona") == DAYTONA_VERSION

    @with_timeout()
    def sdk_call(timeout, delay=0):
        time.sleep(delay)

    previous = signal.signal(signal.SIGALRM, lambda *args: None)
    try:
        signal.setitimer(signal.ITIMER_REAL, 1)
        sdk_call(timeout=2)
        assert signal.getitimer(signal.ITIMER_REAL)[0] == 0  # real pre-fix conflict
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    events = []
    start = time.monotonic()
    with CheckpointDeadline(start + 10.15) as controller:
        with pytest.raises(CheckpointExpired):
            try:
                sdk_call(timeout=2, delay=1 if blocking else 0)
                time.sleep(1)
            except Exception:
                events.append("incorrectly-swallowed")
            finally:
                controller.enter_cleanup()
                sdk_call(timeout=1, delay=0.03)
                events.append("cleaned")
    assert events == ["cleaned"] and time.monotonic() - start < 1
    assert signal.getsignal(signal.SIGALRM) == previous


def cleanup_binding():
    plan = design().implementation
    task = plan.tasks[0]
    return (
        task,
        plan,
        {
            "task": digest(task.model_dump()),
            "plan": digest(plan.model_dump()),
            "source": "a" * 64,
            "nonce": "b" * 32,
        },
    )


@pytest.mark.parametrize("observation", ["absent", "present", "error"])
def test_deletion_requires_typed_absence_after_delete(observation):
    from daytona.common.errors import DaytonaNotFoundError

    from workbench.infrastructure.sandbox.cleanup import confirm_deleted

    seen = []

    def get(identifier):
        seen.append(identifier)
        if observation == "absent":
            raise DaytonaNotFoundError("owned fixture")
        if observation == "error":
            raise RuntimeError("private SDK details")
        return object()

    client = SimpleNamespace(delete=lambda target, timeout: seen.append("delete"), get=get)
    if observation == "absent":
        confirm_deleted(client, SimpleNamespace(id="owned"), time.monotonic() + 0.03, 1)
    else:
        with pytest.raises((RuntimeError, TimeoutError)):
            confirm_deleted(client, SimpleNamespace(id="owned"), time.monotonic() + 0.03, 1)
    assert seen[:2] == ["delete", "owned"]


@pytest.mark.parametrize("mismatch", ["name", "id"])
def test_cleanup_cannot_delete_another_task_sandbox(settings, monkeypatch, mismatch):
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    name = "rnd-source-agent-" + "b" * 32
    target = SimpleNamespace(
        name=name if mismatch == "id" else "another-task",
        id="another-id" if mismatch == "id" else "owned",
    )
    calls = []
    client = SimpleNamespace(get=lambda key: target, delete=lambda *a, **k: calls.append(True))
    monkeypatch.setattr("workbench.sandbox.client_for", lambda settings: client)
    monkeypatch.setattr("workbench.sandbox.close_client", lambda client: None)
    monkeypatch.setattr("workbench.local_only.install_loopback_guard", lambda: None)
    with pytest.raises(ValueError, match="identity"):
        cleanup.perform(
            {
                "name": name,
                "identifier": "owned",
                "binding": binding,
                "settings": {},
                "deadline": time.monotonic() + 2,
            }
        )
    assert not calls


@pytest.mark.parametrize("case", ["success", "wrong-binding", "late", "unknown-create"])
def test_cleanup_parent_is_only_terminal_receipt_writer(settings, tmp_path, monkeypatch, case):
    from workbench.infrastructure.sandbox import cleanup

    _, _, binding = cleanup_binding()
    name = "rnd-source-agent-" + "b" * 32
    path = tmp_path / "cleanup.json"

    class Process:
        returncode = 0

        def communicate(self, body, timeout):
            request = json.loads(body)
            assert request["name"] == name and request["binding"] == binding
            value = dict(binding)
            if case == "wrong-binding":
                value["source"] = "c" * 64
            return json.dumps({"binding": value, "deleted": True}).encode(), b""

        def poll(self):
            return 0

    monkeypatch.setattr(cleanup.subprocess, "Popen", lambda *a, **k: Process())
    args = (
        settings,
        name,
        None if case == "unknown-create" else "owned",
        binding,
        path,
        time.monotonic() + (-1 if case == "late" else 1),
    )
    if case == "success":
        cleanup.delete_owned(*args)
    else:
        with pytest.raises(UnsupportedScope):
            cleanup.delete_owned(*args)
    value = json.loads(path.read_text())
    assert value["binding"] == binding
    assert value["status"] == ("deleted" if case == "success" else "unconfirmed")
    assert (
        settings.daytona_api_key.get_secret_value() not in path.read_text()
        or not settings.daytona_api_key.get_secret_value()
    )


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="POSIX child deadline")
@pytest.mark.parametrize("expired", [False, True])
def test_real_sdk_thread_timeout_is_cut_off_by_cleanup_supervisor(
    settings, tmp_path, monkeypatch, expired
):
    """A real child and real SDK timeout around blocking C sleep; no SDK mocking."""
    import subprocess
    import sys

    from workbench.infrastructure.sandbox import cleanup

    _, _, binding = cleanup_binding()
    marker = tmp_path / "entered-sdk"
    child = """import json,sys,time,threading
from pathlib import Path
from daytona._utils.timeout import with_timeout
p=json.loads(sys.stdin.buffer.read())
@with_timeout()
def sdk_call(timeout):
    Path(sys.argv[1]).write_text("entered")
    time.sleep(6)
def worker():
    try: sdk_call(timeout=1)
    except Exception: pass
t=threading.Thread(target=worker);t.start();t.join()
print(json.dumps({"binding":p["binding"],"deleted":True}))
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        process = original([sys.executable, "-c", child, str(marker)], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(cleanup.subprocess, "Popen", launch)
    path = tmp_path / "cleanup.json"
    start = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        cleanup.delete_owned(
            settings,
            "rnd-source-agent-" + "b" * 32,
            "owned",
            binding,
            path,
            start + (-1 if expired else 2),
        )
    assert marker.read_text() == "entered"
    assert time.monotonic() - start < 4
    assert children[0].poll() is not None
    value = json.loads(path.read_text())
    assert value["status"] == "unconfirmed" and value["binding"] == binding


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["binding"].update(task="c" * 64),
        lambda value: value["binding"].update(source="private"),
        lambda value: value.update(status="private"),
        lambda value: value.update(reason="private"),
        lambda value: value.update(sandbox_name="another-unowned-sandbox"),
    ],
)
def test_public_cleanup_rejects_stale_or_poisoned_receipts(tmp_path, mutate):
    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    path = tmp_path / "cleanup.json"
    value = cleanup.receipt(binding, "rnd-source-agent-" + "b" * 32, "private-sdk-id")
    mutate(value)
    write_json(path, value)
    assert cleanup.public_receipt(path, task, plan) == {
        "status": "unconfirmed",
        "reason": "invalid_or_missing",
    }


def test_public_cleanup_survives_workspace_deletion_without_raw_sdk_data(tmp_path):
    import tempfile
    from pathlib import Path

    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox import cleanup

    task, plan, binding = cleanup_binding()
    with tempfile.TemporaryDirectory(dir=tmp_path) as directory:
        path = Path(directory) / "cleanup.json"
        value = cleanup.receipt(
            binding, "rnd-source-agent-" + "b" * 32, "private-sdk-id", "deletion_unconfirmed"
        )
        value["exception"] = "private secret"
        write_json(path, value)
        exported = cleanup.public_receipt(path, task, plan)
    assert not path.exists()
    assert exported["status"] == "unconfirmed" and exported["binding"] == binding
    assert "private" not in json.dumps(exported)


def test_terminal_checkpoint_cannot_retain_late_pass_or_repair(tmp_path):
    from workbench.capability_sandbox import terminate_checkpoint
    from workbench.filesystem import write_json

    path = tmp_path / "receipt.json"
    write_json(
        path, {"passed": True, "cleanup": "deleted", "repairable_failure": "application_startup"}
    )
    checkpoint = {"nonce": "b" * 32, "task": "approved", "deadline": time.monotonic()}
    terminate_checkpoint(path, checkpoint)
    value = json.loads(path.read_text())
    assert value["passed"] is False and value["cleanup"] == "unconfirmed"
    assert value["checkpoint"] == checkpoint and "repairable_failure" not in value


def test_real_sdk_thread_timer_alone_cannot_bound_blocking_c_call():
    import threading

    from daytona._utils.timeout import with_timeout
    from daytona.common.errors import DaytonaTimeoutError

    observed = []

    @with_timeout()
    def sdk_call(timeout):
        time.sleep(1.25)

    def work():
        start = time.monotonic()
        try:
            sdk_call(timeout=1)
        except DaytonaTimeoutError:
            observed.append(time.monotonic() - start)

    thread = threading.Thread(target=work)
    thread.start()
    thread.join(timeout=3)
    assert not thread.is_alive() and len(observed) == 1 and observed[0] >= 1.2


@pytest.mark.parametrize("wrong_source", [False, True])
def test_checkpoint_cleanup_summary_binds_task_and_current_candidate(tmp_path, wrong_source):
    from workbench.filesystem import write_json
    from workbench.infrastructure.sandbox.cleanup import checkpoint_receipts

    task, plan, binding = cleanup_binding()
    candidate = tmp_path / "step-1"
    candidate.mkdir()
    (candidate / "app.py").write_text("# fixture")
    source = digest(manifest(candidate))
    write_json(
        tmp_path / "step-1-node-verification.json",
        {
            "checkpoint": {"nonce": binding["nonce"], "task": binding["task"]},
            "plan_digest": binding["plan"],
            "source_digest": "c" * 64 if wrong_source else source,
            "sandbox_name": "rnd-source-" + "d" * 32,
            "passed": False,
            "cleanup": "unconfirmed",
            "error": "private-sdk-body",
            "repairable_failure": "private",
        },
    )
    result = checkpoint_receipts(tmp_path, task, plan)
    assert len(result) == 1 and result[0]["cleanup"] == "unconfirmed"
    assert result[0]["binding_valid"] is not wrong_source
    assert "private" not in json.dumps(result)
    if not wrong_source:
        assert result[0]["binding"]["source"] == source


@pytest.mark.parametrize("fail_write", [False, True])
def test_file_cleanup_tracks_expected_candidate_even_after_partial_upload(
    settings, tmp_path, monkeypatch, fail_write
):
    from workbench.infrastructure.sandbox import cleanup, coding

    task, plan, binding = cleanup_binding()
    operations = []
    client = SimpleNamespace()
    target = SimpleNamespace(
        id="owned", name=None, network_block_all=True, public=False, refresh_data=lambda: None
    )

    def create(parameters, timeout):
        target.name = parameters.name
        return target

    client.create = create
    monkeypatch.setattr(coding, "capability_execution_prerequisites", lambda *a: (tmp_path, {}))
    monkeypatch.setattr(coding, "client_for", lambda *a: client)
    monkeypatch.setattr(coding, "close_client", lambda *a: operations.append("closed"))
    monkeypatch.setattr(coding, "require_container_evidence", lambda *a: {})
    monkeypatch.setattr(coding, "require_profile_container_binding", lambda *a: None)
    monkeypatch.setattr(
        "scripts.daytona_capability_profile.inspect_created_sandbox", lambda *a, **k: {}
    )
    monkeypatch.setattr(coding.DaytonaFiles, "write", lambda *a: None)

    def delete(settings, name, identifier, bound, path, deadline):
        assert name == target.name and identifier == target.id
        assert bound == {**binding, "source": "c" * 64}
        operations.append("delete")
        assert json.loads(path.read_text())["binding"] == bound

    monkeypatch.setattr(cleanup, "delete_owned", delete)
    path = tmp_path / "agent-cleanup.json"

    def run():
        with coding.coding_environment(
            settings,
            task,
            plan.selection.model_dump(),
            tmp_path,
            deadline=time.monotonic() + 30,
            cleanup_record=path,
            cleanup_binding=binding,
        ) as environment:
            environment.bind_candidate("c" * 64)
            if fail_write:
                raise RuntimeError("partial upload failed")

    if fail_write:
        with pytest.raises(RuntimeError):
            run()
    else:
        run()
    assert operations == ["delete", "closed"]


def test_checkpoint_parent_kills_child_and_freezes_early_success(settings, tmp_path, monkeypatch):
    import subprocess
    import sys

    from scripts.ci_capability_profile import fixed_application
    from workbench import capability_sandbox as verifier
    from workbench.generator import PrerequisiteError

    product = tmp_path / "product"
    plan = fixed_application(product)
    monkeypatch.setattr(
        "workbench.capability_execution.capability_execution_prerequisites",
        lambda *a: (tmp_path, {}),
    )
    monkeypatch.setattr(
        "workbench.capability_dependencies.require_dependency_descriptors", lambda *a: None
    )
    child = """import json,sys,time
from pathlib import Path
p=json.loads(sys.stdin.buffer.read())
Path(p['receipt']).write_text(json.dumps({'passed':True,'cleanup':'deleted','checkpoint':p['checkpoint'],'repairable_failure':'application_startup'}))
time.sleep(30)
"""
    original = subprocess.Popen
    children = []

    def launch(command, **kwargs):
        process = original([sys.executable, "-c", child], **kwargs)
        children.append(process)
        return process

    monkeypatch.setattr(verifier.subprocess, "Popen", launch)
    checkpoint = {
        "task": digest(plan.tasks[0].model_dump()),
        "nonce": "a" * 32,
        "deadline": time.monotonic() + 0.5,
    }
    with pytest.raises(PrerequisiteError, match="超时"):
        verifier.verify_capabilities(
            product,
            plan,
            plan.scenarios,
            settings,
            aggregate=False,
            checkpoint=checkpoint,
            selection=plan.selection.model_dump(),
        )
    assert children[0].poll() is not None
    value = json.loads((tmp_path / "product-node-verification.json").read_text())
    assert value["passed"] is False and value["cleanup"] == "unconfirmed"
    assert value["checkpoint"] == checkpoint and "repairable_failure" not in value


@pytest.mark.skipif(not hasattr(signal, "SIGUSR1"), reason="dedicated POSIX deadline")
def test_real_sdk_cleanup_cannot_extend_original_checkpoint_deadline():
    from daytona._utils.timeout import with_timeout

    from workbench.infrastructure.sandbox.deadline import CheckpointDeadline, CheckpointExpired

    @with_timeout()
    def cleanup_call(timeout):
        time.sleep(12)

    start = time.monotonic()
    with CheckpointDeadline(start + 10.1) as controller:
        controller.enter_cleanup()
        with pytest.raises(CheckpointExpired):
            cleanup_call(timeout=20)
    elapsed = time.monotonic() - start
    assert 10 <= elapsed < 11.5
````
