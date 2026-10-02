# tests/test_streaming_backend.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.api`、`workbench.domain`、`workbench.llm`、`workbench.store`、`workbench.streaming`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `frame`（L19–L35）：接收`text`、`finish`、`**delta`。 控制顺序：L20按`text is not None`分支。 调用`( "data: " + json.dumps( { "id": "fixture", "object": "chat.compl…`、`json.dumps`。 返回路径：L22的`( "data: " + json.dumps( { "id": "fixture", "object": "chat.completion.chunk", "created": …`。
- `stream_body`（L38–L49）：接收`text`、`finish`、`done`、`fragment_size`。 调用`frame`、`b"".join`、`range`、`len`。 返回路径：L39的`frame(role="assistant", reasoning_content="private-reasoning-canary") + b"".join(frame(tex…`。
- `Bytes`（L52–L61）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Bytes.__init__`（L53–L54）：接收`value`、`size`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Bytes.__iter__`（L56–L58）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L57遍历`range(0, len(self.value), self.size)`。 调用`range`、`len`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `Bytes.close`（L60–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `gateway`（L64–L68）：接收`store`、`handler`。 调用`SecretStr`、`ModelGateway`、`httpx.MockTransport`。 返回路径：L68的`ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True)`。
- `assistant_events`（L71–L72）：接收`store`、`run`。 调用`store.events`、`r["kind"].startswith`。 返回路径：L72的`[r for r in store.events(run) if r["kind"].startswith("assistant_")]`。
- `test_real_provider_stream_is_visible_before_response_finishes_and_replays_once`（L75–L115）：接收`store`。 控制顺序：L97断言`result.summary == "你好世界🌍"`；L98断言`seen[0]["stream"] is True`；L99断言`seen[0]["response_format"] == {"type": "json_object"}`；L100断言`model.complete(run, "review:1", "JSON", {}, ModelReview) == result`；L101断言`len(seen) == store.get_run(run)["model_calls"] == 1`；L103断言`len([e for e in events if e["kind"] == "assistant_completed"]) == 1`；L105断言`final["content"] == "你好世界🌍" and final["validation"] == "validated"`；L106断言`final["transport"] == "streaming"`。后续分支沿下方源码相同行号继续阅读。 调用`new_run`、`frame`、`stream_body`、`gateway`、`model.complete`、`len`、`store.get_run`、`assistant_events`、`store.transcript`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_provider_stream_is_visible_before_response_finishes_and_replays_once.Progressive`（L81–L87）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_real_provider_stream_is_visible_before_response_finishes_and_replays_once.Progressive.__iter__`（L82–L87）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85断言`"".join(e["data"]["text"] for e in drafts) == "你好"`；L86断言`not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))`。 调用`assistant_events`、`"".join`、`any`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_real_provider_stream_is_visible_before_response_finishes_and_replays_once.handler`（L89–L93）：接收`request`。 调用`seen.append`、`json.loads`、`httpx.Response`、`Progressive`。 返回路径：L91的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Progressive() )`。
- `test_unicode_provider_byte_boundaries_and_json_escape_boundaries`（L119–L131）：接收`store`、`ensure_ascii`。 控制顺序：L128断言`model.complete(run, "review:unicode", "JSON", {}, ModelReview).summary == expected`；L130断言`"".join(e["data"]["text"] for e in events if e["kind"] == "assistant_delta") == expec…`；L131断言`body.closed`。 调用`json.dumps`、`ModelReview(summary=expected).model_dump`、`ModelReview`、`Bytes`、`stream_body`、`gateway`、`httpx.Response`、`new_run`、`model.complete`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_allowlisted_root_field_is_projected_and_patch_source_is_never_streamed`（L134–L162）：接收`store`。 控制顺序：L156断言`store.transcript(run)["messages"][-1]["content"] == "已增加字段校验"`；L157断言`"source-code-private-canary" not in json.dumps(events)`；L158断言`"private-system-instruction" not in json.dumps(events)`；L159断言`root_string_prefix('{"facts":{"summary":"hidden"},"summary":"shown', "summary") == "s…`；L162断言`root_string_prefix('{"facts":{"summary":"hidden', "summary") == ""`。 调用`Patches`、`gateway`、`httpx.Response`、`Bytes`、`stream_body`、`value.model_dump_json`、`new_run`、`model.complete`、`assistant_events`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_credentials_are_redacted_across_every_chunk_and_hot_config_keys`（L165–L194）：接收`store`。 控制顺序：L185遍历`raw`；L192断言`text == result["content"] == "前缀 [redacted] [redacted] [redacted] [redacted] 后缀"`；L193断言`"offline-key-secret" not in json.dumps(assistant_events(store, run))`；L194断言`model.streaming`。 调用`gateway`、`new_run`、`store.settings._remember_model_keys`、`store.settings.model_configuration`、`store.settings._model_keys.add`、`AssistantStream`、`SecretStr`、`observer.mode`、`json.dumps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_stream_never_completes_and_safe_failure_clears_draft`（L207–L231）：接收`store`、`finish`、`extra`、`expected_calls`。 控制顺序：L223断言`len(calls) == expected_calls`；L224断言`not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))`；L225断言`all( m["validation"] == "failed" and m["content"] == "" for m in store.transcript(run…`；L230断言`"private-refusal" not in json.dumps(assistant_events(store, run))`；L231断言`"private-tool" not in json.dumps(assistant_events(store, run))`。 调用`gateway`、`new_run`、`pytest.raises`、`model.complete`、`len`、`any`、`assistant_events`、`all`、`store.transcript`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_failed_stream_never_completes_and_safe_failure_clears_draft.handler`（L212–L217）：接收`request`。 调用`calls.append`、`frame`、`httpx.Response`、`Bytes`。 返回路径：L215的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Bytes(body) )`。
- `test_strict_final_validation_and_missing_done_cannot_be_hidden_by_sdk`（L243–L256）：接收`store`、`raw`、`done`。 控制顺序：L255断言`store.get_run(run)["model_calls"] == 2`；L256断言`not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))`。 调用`gateway`、`httpx.Response`、`Bytes`、`stream_body`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_only_provider_is_honest_completed_response_without_fake_deltas`（L259–L285）：接收`store`。 控制顺序：L282断言`len(seen) == 1 and seen[0]["stream"] is True`；L283断言`not any(e["kind"] == "assistant_delta" for e in assistant_events(store, run))`；L284断言`store.transcript(run)["messages"][-1]["transport"] == "non_streaming"`；L285断言`store.transcript(run)["messages"][-1]["content"] == requirement().summary`。 调用`gateway`、`new_run`、`model.complete`、`len`、`any`、`assistant_events`、`store.transcript`、`requirement`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_only_provider_is_honest_completed_response_without_fake_deltas.handler`（L262–L277）：接收`request`。 调用`seen.append`、`json.loads`、`httpx.Response`、`requirement().model_dump_json`、`requirement`。 返回路径：L264的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": re…`。
- `test_explicit_unsupported_stream_falls_back_once_without_downgrading_contract`（L288–L318）：接收`store`。 控制顺序：L315断言`[v["stream"] for v in seen] == [True, False]`；L316断言`all(v["response_format"] == {"type": "json_object"} for v in seen)`；L317断言`store.transcript(run)["messages"][-1]["transport"] == "non_streaming"`；L318断言`"private-error" not in json.dumps(assistant_events(store, run))`。 调用`gateway`、`new_run`、`model.complete`、`all`、`store.transcript`、`json.dumps`、`assistant_events`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_unsupported_stream_falls_back_once_without_downgrading_contract.handler`（L291–L310）：接收`request`。 控制顺序：L293按`len(seen) == 1`分支。 调用`seen.append`、`json.loads`、`len`、`httpx.Response`、`ModelReview(summary="完成").model_dump_json`、`ModelReview`。 返回路径：L294的`httpx.Response( 400, json={"error": {"code": "unsupported_stream", "message": "private-err…`；L297的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": Mo…`。
- `test_sse_auth_cursor_replay_pagination_and_no_generation_on_subscribe`（L321–L357）：接收`settings`。 控制顺序：L326断言`client.get(f"/runs/{run}/stream").status_code == 401`；L327断言`client.get(f"/runs/{run}/transcript").status_code == 401`；L329遍历`range(231)`；L334断言`response.status_code == 200 and response.headers["content-type"].startswith( "text/ev…`；L338断言`len(ids) == 232 and ids == sorted(set(ids))`；L339断言`"event: idle" in response.text`；L344断言`[ int(line[4:]) for line in again.text.splitlines() if line.startswith("id: ") ] == i…`；L348断言`transcript["cursor"] == ids[-1]`。后续分支沿下方源码相同行号继续阅读。 调用`create_app`、`TestClient`、`new_run`、`client.get`、`range`、`store.record_event`、`store.claim`、`store.finish`、`response.headers["content-type"].startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_disconnect_only_closes_subscription_and_durable_work_can_continue`（L360–L392）：接收`store`。 控制顺序：L384断言`store.get_run(run)["status"] == "RUNNING"`；L392断言`store.transcript(run)["messages"][-1]["content"] == "first second"`。 调用`new_run`、`store.claim`、`AssistantStream`、`observer.mode`、`observer.content`、`Request`、`asyncio.run`、`subscribe`、`store.get_run`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_disconnect_only_closes_subscription_and_durable_work_can_continue.Request`（L367–L371）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_disconnect_only_closes_subscription_and_durable_work_can_continue.Request.is_disconnected`（L370–L371）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L371的`self.disconnected`。
- `test_disconnect_only_closes_subscription_and_durable_work_can_continue.subscribe`（L375–L381）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L378断言`"assistant_start" in first`。 调用`event_stream`、`anext`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_new_attempt_marks_interrupted_draft_and_terminal_event_is_idempotent`（L395–L407）：接收`store`。 控制顺序：L405断言`messages[-2]["code"] == "worker_interrupted" and messages[-2]["content"] == ""`；L406断言`messages[-1]["content"] == "完成"`；L407断言`sum(e["kind"] == "assistant_completed" for e in assistant_events(store, run)) == 1`。 调用`new_run`、`AssistantStream`、`old.content`、`new.completed_data`、`ModelReview`、`store.assistant_event`、`store.transcript`、`sum`、`assistant_events`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deepseek_real_sse_preserves_framework_strict_validation`（L410–L427）：接收`store`。 控制顺序：L425断言`model.complete(run, "review:deepseek", "JSON", {}, ModelReview).summary == "审阅完成"`；L426断言`calls[0]["stream"] is True and calls[0]["response_format"] == {"type": "json_object"}`；L427断言`store.model_records(run)[0]["provider"] == "deepseek"`。 调用`gateway`、`new_run`、`model.complete`、`store.model_records`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_deepseek_real_sse_preserves_framework_strict_validation.handler`（L413–L419）：接收`request`。 调用`calls.append`、`json.loads`、`httpx.Response`、`Bytes`、`stream_body`、`ModelReview(summary="审阅完成").model_dump_json`、`ModelReview`。 返回路径：L415的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Bytes(stream_bo…`。
- `test_schema_repair_keeps_failed_and_validated_attempts_separate`（L430–L453）：接收`store`。 控制顺序：L450断言`len(calls) == 2`；L451断言`messages[-2]["validation"] == "failed" and messages[-2]["content"] == ""`；L452断言`messages[-1]["validation"] == "validated" and messages[-1]["content"] == "corrected"`；L453断言`messages[-1]["message_id"] != messages[-2]["message_id"]`。 调用`gateway`、`new_run`、`model.complete`、`store.transcript`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_schema_repair_keeps_failed_and_validated_attempts_separate.handler`（L433–L444）：接收`request`。 调用`calls.append`、`json.loads`、`len`、`ModelReview(summary="corrected").model_dump_json`、`ModelReview`、`httpx.Response`、`Bytes`、`stream_body`。 返回路径：L440的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Bytes(stream_bo…`。
- `test_saved_ui_only_secret_never_leaks_across_provider_fragments`（L456–L489）：接收`store`。 控制顺序：L470断言`not store.settings.api_key.get_secret_value()`；L488断言`deltas == "Before [redacted] after"`；L489断言`"ui-configuration-only-secret" not in json.dumps(events)`。 调用`ModelSettingsRepository`、`repository.update`、`repository.snapshot`、`store.settings.api_key.get_secret_value`、`ModelReview(summary="Before ui-configuration-only-secret after").…`、`ModelReview`、`ModelGateway`、`httpx.MockTransport`、`httpx.Response`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cached_legacy_completion_backfills_transcript_without_another_model_call`（L492–L521）：接收`store`。 控制顺序：L519断言`len(calls) == 1`；L520断言`store.transcript(run)["messages"][-1]["content"] == "cached"`；L521断言`len(assistant_events(store, run)) == 1`。 调用`gateway`、`new_run`、`model.complete`、`len`、`store.transcript`、`assistant_events`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_cached_legacy_completion_backfills_transcript_without_another_model_call.handler`（L495–L510）：接收`request`。 调用`calls.append`、`httpx.Response`、`ModelReview(summary="cached").model_dump_json`、`ModelReview`。 返回路径：L497的`httpx.Response( 200, json={ "choices": [ { "message": { "role": "assistant", "content": Mo…`。
- `test_provider_stream_size_bound_is_enforced_before_line_buffering`（L524–L537）：接收`store`。 控制顺序：L536断言`store.get_run(run)["model_calls"] == 1`；L537断言`store.transcript(run)["messages"][-1]["code"] == "response_too_large"`。 调用`gateway`、`httpx.Response`、`Bytes`、`new_run`、`pytest.raises`、`model.complete`、`store.get_run`、`store.transcript`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_text_length_cap_cannot_cut_a_secret_before_redaction`（L540–L559）：接收`store`。 控制顺序：L558断言`len(final) == MAX_PUBLIC_TEXT`；L559断言`final.endswith("[red") and not final.endswith("offl")`。 调用`gateway`、`AssistantStream`、`new_run`、`Patches`、`observer.completed_data`、`len`、`final.endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_projection_never_reparses_or_retains_tail_after_boundary`（L563–L601）：接收`settings`、`monkeypatch`、`boundary`。 控制顺序：L585按`boundary == "closed"`分支；L588断言`not observer.projection_finished`；L594断言`observer.projection_finished and observer.raw == ""`；L597遍历`range(0, len(tail), 32)`；L599断言`len(calls) == boundary_calls`；L600断言`observer.raw == "" and observer.sent == expected`；L601断言`not any(kind == "assistant_completed" for kind, _ in fake.events)`。 调用`Store`、`AssistantStream`、`monkeypatch.setattr`、`observer.content`、`len`、`range`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_projection_never_reparses_or_retains_tail_after_boundary.Store`（L568–L573）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_public_projection_never_reparses_or_retains_tail_after_boundary.Store.__init__`（L569–L570）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_projection_never_reparses_or_retains_tail_after_boundary.Store.assistant_event`（L572–L573）：接收`run_id`、`kind`、`data`。 调用`self.events.append`、`dict`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_public_projection_never_reparses_or_retains_tail_after_boundary.tracked`（L580–L582）：接收`source`、`field`。 调用`calls.append`、`len`、`project`。 返回路径：L582的`project(source, field)`。
- `test_projection_cap_keeps_split_key_held_until_full_validated_redaction`（L604–L639）：接收`settings`、`monkeypatch`。 控制顺序：L619断言`observer.projection_finished and observer.sent == prefix`；L626断言`observer.sent == prefix and observer.raw == ""`；L638断言`completed["content"] == prefix + "[red"`；L639断言`"cap-" not in "".join(data.get("text", "") for _, data in fake.events)`。 调用`SecretStr`、`Store`、`AssistantStream`、`observer.content`、`monkeypatch.setattr`、`Patches`、`observer.completed_data`、`"".join`、`data.get`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_projection_cap_keeps_split_key_held_until_full_validated_redaction.Store`（L607–L612）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_projection_cap_keeps_split_key_held_until_full_validated_redaction.Store.__init__`（L608–L609）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_projection_cap_keeps_split_key_held_until_full_validated_redaction.Store.assistant_event`（L611–L612）：接收`run_id`、`kind`、`data`。 调用`self.events.append`、`dict`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_projection_cap_keeps_split_key_held_until_full_validated_redaction.forbidden_reparse`（L621–L622）：接收`*args`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_recovery_closes_abandoned_stream_after_model_profile_change`（L642–L688）：接收`store`。 控制顺序：L670断言`draft["validation"] == "pending" and draft["content"] == "old model draft"`；L674断言`interrupted["message_id"] == draft["message_id"]`；L675断言`interrupted["validation"] == "failed" and interrupted["content"] == ""`；L676断言`interrupted["code"] == "worker_interrupted"`；L678断言`resumed["id"] == job["id"]`；L679断言`model.complete(run, "review:recovery", "JSON", {}, ModelReview).summary == "new model…`；L685断言`messages[-1]["response_id"] != draft["response_id"]`；L686断言`messages[-1]["validation"] == "validated"`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`store.claim`、`pytest.raises`、`model.complete`、`store.transcript`、`store.recover`、`store.finish`、`any`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_recovery_closes_abandoned_stream_after_model_profile_change.WorkerCrash`（L643–L644）：继承`BaseException`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_worker_recovery_closes_abandoned_stream_after_model_profile_change.CrashStream`（L646–L649）：继承`httpx.SyncByteStream`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_worker_recovery_closes_abandoned_stream_after_model_profile_change.CrashStream.__iter__`（L647–L649）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L649抛异常，停止当前正常路径。 调用`frame`、`WorkerCrash`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `test_worker_recovery_closes_abandoned_stream_after_model_profile_change.handler`（L653–L662）：接收`request`。 调用`calls.append`、`json.loads`、`len`、`CrashStream`、`Bytes`、`stream_body`、`ModelReview(summary="new model result").model_dump_json`、`ModelReview`、`httpx.Response`。 返回路径：L662的`httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)`。
- `test_worker_recovery_repairs_committed_step_before_missing_completion_event`（L691–L741）：接收`store`、`monkeypatch`。 控制顺序：L724断言`draft["validation"] == "pending"`；L725断言`store.model_records(run)[0]["status"] == "validated"`；L730断言`completed["message_id"] == draft["message_id"]`；L731断言`completed["validation"] == "validated"`；L732断言`completed["content"] == "validated [redacted] result"`；L733断言`not any(event["kind"] == "assistant_failed" for event in assistant_events(store, run)…`；L735断言`resumed["id"] == job["id"]`；L737断言`len(calls) == 1`。后续分支沿下方源码相同行号继续阅读。 调用`gateway`、`new_run`、`store.claim`、`monkeypatch.setattr`、`pytest.raises`、`model.complete`、`store.transcript`、`store.model_records`、`store.recover`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_worker_recovery_repairs_committed_step_before_missing_completion_event.WorkerCrash`（L692–L693）：继承`BaseException`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_worker_recovery_repairs_committed_step_before_missing_completion_event.handler`（L697–L708）：接收`request`。 调用`calls.append`、`json.loads`、`httpx.Response`、`Bytes`、`stream_body`、`ModelReview(summary="validated offline-key-secret result").model_…`、`ModelReview`。 返回路径：L699的`httpx.Response( 200, headers={"content-type": "text/event-stream"}, stream=Bytes( stream_b…`。
- `test_worker_recovery_repairs_committed_step_before_missing_completion_event.crash_before_completion`（L715–L718）：接收`run_id`、`kind`、`data`。 控制顺序：L716按`kind == "assistant_completed"`分支；L717抛异常，停止当前正常路径。 调用`WorkerCrash`、`append`。 返回路径：L718的`append(run_id, kind, data)`。
- `test_recovery_does_not_fail_drafts_outside_recovered_running_jobs`（L744–L749）：接收`store`。 控制顺序：L749断言`store.transcript(run)["messages"][-1]["validation"] == "pending"`。 调用`new_run`、`AssistantStream`、`observer.content`、`store.recover`、`store.transcript`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix`（L762–L783）：接收`settings`、`keys`、`summary`。 控制顺序：L771按`len(keys) > 1`分支；L776遍历`json.dumps({"summary": summary})`；L778断言`final.startswith(observer.sent)`；L779按`keys == ("ababa",) and summary == "abababa"`分支；L780断言`final == "[redacted]ba"`；L781断言`observer.sent == ""`；L782遍历`keys`；L783断言`key not in "".join(data.get("text", "") for _, data in fake.events)`。 调用`SecretStr`、`len`、`Store`、`AssistantStream`、`observer.completed_data`、`ModelReview`、`json.dumps`、`observer.content`、`final.startswith`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix.Store`（L763–L768）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix.Store.__init__`（L764–L765）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix.Store.assistant_event`（L767–L768）：接收`run_id`、`kind`、`data`。 调用`self.events.append`、`dict`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_streaming_backend.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L783。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`29779`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_streaming_backend.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "deaec9b54018d2ecec70b9f8954b03ef5b47eff81f09cc1cd3b78e9514929c9d"} -->
````python
# tests/test_streaming_backend.py
"""Offline provider streams only. No saved credentials or paid model calls."""

import asyncio
import json

import httpx
import pytest
from conftest import new_run, requirement
from fastapi.testclient import TestClient
from pydantic import SecretStr

from workbench.api import create_app
from workbench.domain import ModelReview, Patches, Requirement
from workbench.llm import ModelFailure, ModelGateway
from workbench.store import Store
from workbench.streaming import AssistantStream, event_stream, root_string_prefix


def frame(text=None, *, finish=None, **delta):
    if text is not None:
        delta["content"] = text
    return (
        "data: "
        + json.dumps(
            {
                "id": "fixture",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": "offline",
                "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
            },
            ensure_ascii=False,
        )
        + "\n\n"
    ).encode()


def stream_body(text, *, finish="stop", done=True, fragment_size=12):
    return (
        frame(role="assistant", reasoning_content="private-reasoning-canary")
        + b"".join(frame(text[i : i + fragment_size]) for i in range(0, len(text), fragment_size))
        + frame(finish=finish)
        + (
            b'data: {"choices":[],"usage":{"total_tokens":12,"extra":"private-usage"}}\n\n'
            b"data: [DONE]\n\n"
            if done
            else b""
        )
    )


class Bytes(httpx.SyncByteStream):
    def __init__(self, value, *, size=1):
        self.value, self.size, self.closed = value, size, False

    def __iter__(self):
        for offset in range(0, len(self.value), self.size):
            yield self.value[offset : offset + self.size]

    def close(self):
        self.closed = True


def gateway(store, handler):
    store.settings.base_url = "https://api.openai.com/v1"
    store.settings.model = "offline-model"
    store.settings.api_key = SecretStr("offline-key-secret")
    return ModelGateway(store.settings, store, httpx.MockTransport(handler), streaming=True)


def assistant_events(store, run):
    return [r for r in store.events(run) if r["kind"].startswith("assistant_")]


def test_real_provider_stream_is_visible_before_response_finishes_and_replays_once(store):
    run = new_run(store)
    first = frame('{"summary":"你好')
    rest = stream_body('世界🌍","observations":[],"uncovered_requirements":[]}', fragment_size=7)
    seen = []

    class Progressive(httpx.SyncByteStream):
        def __iter__(self):
            yield first
            drafts = [e for e in assistant_events(store, run) if e["kind"] == "assistant_delta"]
            assert "".join(e["data"]["text"] for e in drafts) == "你好"
            assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))
            yield rest

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=Progressive()
        )

    model = gateway(store, handler)
    result = model.complete(run, "review:1", "JSON", {}, ModelReview)
    assert result.summary == "你好世界🌍"
    assert seen[0]["stream"] is True
    assert seen[0]["response_format"] == {"type": "json_object"}
    assert model.complete(run, "review:1", "JSON", {}, ModelReview) == result
    assert len(seen) == store.get_run(run)["model_calls"] == 1
    events = assistant_events(store, run)
    assert len([e for e in events if e["kind"] == "assistant_completed"]) == 1
    final = store.transcript(run)["messages"][-1]
    assert final["content"] == "你好世界🌍" and final["validation"] == "validated"
    assert final["transport"] == "streaming"
    assert "private-reasoning-canary" not in json.dumps(events)
    assert "private-usage" not in json.dumps(events)
    assert store.model_records(run)[0]["usage"] == {"total_tokens": 12}
    assert store.messages(run) == [{"role": "user", "content": "个人任务 CRUD"}]
    other = Store(store.settings)
    try:
        assert other.transcript(run) == store.transcript(run)
    finally:
        other.engine.dispose()


@pytest.mark.parametrize("ensure_ascii", [True, False])
def test_unicode_provider_byte_boundaries_and_json_escape_boundaries(store, ensure_ascii):
    expected = '中文🌍「引号"」\\路径\n第二行'
    raw = json.dumps(ModelReview(summary=expected).model_dump(), ensure_ascii=ensure_ascii)
    body = Bytes(stream_body(raw, fragment_size=1))
    model = gateway(
        store,
        lambda _: httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body),
    )
    run = new_run(store)
    assert model.complete(run, "review:unicode", "JSON", {}, ModelReview).summary == expected
    events = assistant_events(store, run)
    assert "".join(e["data"]["text"] for e in events if e["kind"] == "assistant_delta") == expected
    assert body.closed


def test_only_allowlisted_root_field_is_projected_and_patch_source_is_never_streamed(store):
    value = Patches(
        explanation="已增加字段校验",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "source-code-private-canary",
            }
        ],
    )
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(value.model_dump_json()), size=50),
        ),
    )
    run = new_run(store)
    model.complete(run, "coding:1", "private-system-instruction", {}, Patches)
    events = assistant_events(store, run)
    assert store.transcript(run)["messages"][-1]["content"] == "已增加字段校验"
    assert "source-code-private-canary" not in json.dumps(events)
    assert "private-system-instruction" not in json.dumps(events)
    assert (
        root_string_prefix('{"facts":{"summary":"hidden"},"summary":"shown', "summary") == "shown"
    )
    assert root_string_prefix('{"facts":{"summary":"hidden', "summary") == ""


def test_credentials_are_redacted_across_every_chunk_and_hot_config_keys(store):
    model = gateway(store, lambda _: None)
    run = new_run(store)
    store.settings._remember_model_keys(store.settings.model_configuration())
    with store.settings._model_keys_lock:
        store.settings._model_keys.add("ui-only-hot-key")
        store.settings._model_keys.add("abab")
    observer = AssistantStream(
        store,
        store.settings,
        run,
        "response",
        "review",
        ModelReview,
        True,
        api_key=SecretStr("frozen-profile-key"),
    )
    observer.mode("streaming")
    value = "前缀 offline-key-secret ui-only-hot-key frozen-profile-key abab 后缀"
    raw = json.dumps({"summary": value}, ensure_ascii=False)
    for char in raw:
        observer.content(char)
    result = observer.completed_data(ModelReview(summary=value), ModelReview)
    store.assistant_event(run, "assistant_completed", result)
    text = "".join(
        e["data"]["text"] for e in assistant_events(store, run) if e["kind"] == "assistant_delta"
    )
    assert text == result["content"] == "前缀 [redacted] [redacted] [redacted] [redacted] 后缀"
    assert "offline-key-secret" not in json.dumps(assistant_events(store, run))
    assert model.streaming


@pytest.mark.parametrize(
    "finish,extra,expected_calls",
    [
        ("length", {}, 1),
        ("content_filter", {}, 1),
        ("stop", {"refusal": "private-refusal"}, 1),
        ("stop", {"tool_calls": [{"name": "private-tool"}]}, 1),
        ("aborted", {}, 2),
    ],
)
def test_failed_stream_never_completes_and_safe_failure_clears_draft(
    store, finish, extra, expected_calls
):
    calls = []

    def handler(request):
        calls.append(request)
        body = frame('{"summary":"draft"') + frame(finish=finish, **extra) + b"data: [DONE]\n\n"
        return httpx.Response(
            200, headers={"content-type": "text/event-stream"}, stream=Bytes(body)
        )

    model = gateway(store, handler)
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "review:bad", "JSON", {}, ModelReview)
    assert len(calls) == expected_calls
    assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))
    assert all(
        m["validation"] == "failed" and m["content"] == ""
        for m in store.transcript(run)["messages"]
        if m["role"] == "assistant"
    )
    assert "private-refusal" not in json.dumps(assistant_events(store, run))
    assert "private-tool" not in json.dumps(assistant_events(store, run))


@pytest.mark.parametrize(
    "raw,done",
    [
        ('{"summary":"first","summary":"second"}', True),
        ('{"summary":"incomplete"', True),
        ('{"summary":"valid"}', False),
        ('{"summary":"valid","observations":"wrong-type"}', True),
    ],
)
def test_strict_final_validation_and_missing_done_cannot_be_hidden_by_sdk(store, raw, done):
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw, done=done), size=19),
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure):
        model.complete(run, "review:invalid", "JSON", {}, ModelReview)
    assert store.get_run(run)["model_calls"] == 2
    assert not any(e["kind"] == "assistant_completed" for e in assistant_events(store, run))


def test_json_only_provider_is_honest_completed_response_without_fake_deltas(store):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": requirement().model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "requirement:1", "JSON", {}, Requirement)
    assert len(seen) == 1 and seen[0]["stream"] is True
    assert not any(e["kind"] == "assistant_delta" for e in assistant_events(store, run))
    assert store.transcript(run)["messages"][-1]["transport"] == "non_streaming"
    assert store.transcript(run)["messages"][-1]["content"] == requirement().summary


def test_explicit_unsupported_stream_falls_back_once_without_downgrading_contract(store):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        if len(seen) == 1:
            return httpx.Response(
                400, json={"error": {"code": "unsupported_stream", "message": "private-error"}}
            )
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": ModelReview(summary="完成").model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "review:1", "JSON", {}, ModelReview)
    assert [v["stream"] for v in seen] == [True, False]
    assert all(v["response_format"] == {"type": "json_object"} for v in seen)
    assert store.transcript(run)["messages"][-1]["transport"] == "non_streaming"
    assert "private-error" not in json.dumps(assistant_events(store, run))


def test_sse_auth_cursor_replay_pagination_and_no_generation_on_subscribe(settings):
    app = create_app(settings, start_worker=False)
    with TestClient(app) as client:
        store = app.state.store
        run = new_run(store)
        assert client.get(f"/runs/{run}/stream").status_code == 401
        assert client.get(f"/runs/{run}/transcript").status_code == 401
        headers = {"Authorization": "Bearer " + app.state.token}
        for index in range(231):
            store.record_event(run, "fixture", {"number": index})
        job = store.claim()
        store.finish(job, "WAITING_REQUIREMENT")
        response = client.get(f"/runs/{run}/stream", headers=headers)
        assert response.status_code == 200 and response.headers["content-type"].startswith(
            "text/event-stream"
        )
        ids = [int(line[4:]) for line in response.text.splitlines() if line.startswith("id: ")]
        assert len(ids) == 232 and ids == sorted(set(ids))
        assert "event: idle" in response.text
        again = client.get(
            f"/runs/{run}/stream?after={ids[3]}",
            headers={**headers, "Last-Event-ID": str(ids[200])},
        )
        assert [
            int(line[4:]) for line in again.text.splitlines() if line.startswith("id: ")
        ] == ids[201:]
        transcript = client.get(f"/runs/{run}/transcript", headers=headers).json()
        assert transcript["cursor"] == ids[-1]
        assert store.get_run(run)["model_calls"] == 0
        assert (
            client.get(
                f"/runs/{run}/stream", headers={**headers, "Last-Event-ID": "oops"}
            ).status_code
            == 422
        )
        assert client.get(f"/runs/{run}/stream?after=-1", headers=headers).status_code == 422
        assert client.get("/runs/missing/stream", headers=headers).status_code == 404


def test_disconnect_only_closes_subscription_and_durable_work_can_continue(store):
    run = new_run(store)
    job = store.claim()
    observer = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    observer.mode("streaming")
    observer.content('{"summary":"first')

    class Request:
        disconnected = False

        async def is_disconnected(self):
            return self.disconnected

    request = Request()

    async def subscribe():
        events = event_stream(request, store, run, 0, interval=0)
        first = await anext(events)
        assert "assistant_start" in first
        request.disconnected = True
        with pytest.raises(StopAsyncIteration):
            await anext(events)

    asyncio.run(subscribe())
    assert store.get_run(run)["status"] == "RUNNING"
    observer.content(' second"}')
    store.assistant_event(
        run,
        "assistant_completed",
        observer.completed_data(ModelReview(summary="first second"), ModelReview),
    )
    store.finish(job, "WAITING_REQUIREMENT")
    assert store.transcript(run)["messages"][-1]["content"] == "first second"


def test_new_attempt_marks_interrupted_draft_and_terminal_event_is_idempotent(store):
    run = new_run(store)
    old = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    old.content('{"summary":"unfinished')
    new = AssistantStream(store, store.settings, run, "response", "review", ModelReview, True)
    complete = new.completed_data(ModelReview(summary="完成"), ModelReview)
    store.assistant_event(run, "assistant_completed", complete)
    store.assistant_event(run, "assistant_completed", complete)
    old.content("still should not append")
    messages = store.transcript(run)["messages"]
    assert messages[-2]["code"] == "worker_interrupted" and messages[-2]["content"] == ""
    assert messages[-1]["content"] == "完成"
    assert sum(e["kind"] == "assistant_completed" for e in assistant_events(store, run)) == 1


def test_deepseek_real_sse_preserves_framework_strict_validation(store):
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(ModelReview(summary="审阅完成").model_dump_json()), size=2),
        )

    model = gateway(store, handler)
    store.settings.base_url = "https://api.deepseek.com"
    store.settings.model = "offline-deepseek"
    run = new_run(store)
    assert model.complete(run, "review:deepseek", "JSON", {}, ModelReview).summary == "审阅完成"
    assert calls[0]["stream"] is True and calls[0]["response_format"] == {"type": "json_object"}
    assert store.model_records(run)[0]["provider"] == "deepseek"


def test_schema_repair_keeps_failed_and_validated_attempts_separate(store):
    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        raw = (
            '{"summary":"candidate","observations":false}'
            if len(calls) == 1
            else ModelReview(summary="corrected").model_dump_json()
        )
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(stream_body(raw), size=33),
        )

    model = gateway(store, handler)
    run = new_run(store)
    model.complete(run, "review:repair", "JSON", {}, ModelReview)
    messages = store.transcript(run)["messages"]
    assert len(calls) == 2
    assert messages[-2]["validation"] == "failed" and messages[-2]["content"] == ""
    assert messages[-1]["validation"] == "validated" and messages[-1]["content"] == "corrected"
    assert messages[-1]["message_id"] != messages[-2]["message_id"]


def test_saved_ui_only_secret_never_leaks_across_provider_fragments(store):
    from workbench.model_settings import ModelSettingsRepository

    repository = ModelSettingsRepository(store.settings)
    repository.update(
        {
            "expected_revision": repository.snapshot().revision,
            "default": {
                "base_url": "https://api.openai.com/v1",
                "model": "offline",
                "api_key": "ui-configuration-only-secret",
            },
        }
    )
    assert not store.settings.api_key.get_secret_value()
    raw = ModelReview(summary="Before ui-configuration-only-secret after").model_dump_json()
    model = ModelGateway(
        store.settings,
        store,
        httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                stream=Bytes(stream_body(raw, fragment_size=1), size=3),
            )
        ),
        streaming=True,
    )
    run = new_run(store)
    model.complete(run, "review:ui-key", "JSON", {}, ModelReview)
    events = assistant_events(store, run)
    deltas = "".join(e["data"]["text"] for e in events if e["kind"] == "assistant_delta")
    assert deltas == "Before [redacted] after"
    assert "ui-configuration-only-secret" not in json.dumps(events)


def test_cached_legacy_completion_backfills_transcript_without_another_model_call(store):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": ModelReview(summary="cached").model_dump_json(),
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

    model = gateway(store, handler)
    model.streaming = False
    run = new_run(store)
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    model.streaming = True
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    model.complete(run, "review:cached", "JSON", {}, ModelReview)
    assert len(calls) == 1
    assert store.transcript(run)["messages"][-1]["content"] == "cached"
    assert len(assistant_events(store, run)) == 1


def test_provider_stream_size_bound_is_enforced_before_line_buffering(store):
    model = gateway(
        store,
        lambda _: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(b"data: " + b"x" * 2_000_001, size=65536),
        ),
    )
    run = new_run(store)
    with pytest.raises(ModelFailure, match="响应过大"):
        model.complete(run, "review:oversize", "JSON", {}, ModelReview)
    assert store.get_run(run)["model_calls"] == 1
    assert store.transcript(run)["messages"][-1]["code"] == "response_too_large"


def test_public_text_length_cap_cannot_cut_a_secret_before_redaction(store):
    from workbench.streaming import MAX_PUBLIC_TEXT

    gateway(store, lambda _: None)
    observer = AssistantStream(
        store, store.settings, new_run(store), "limit", "coding", Patches, True
    )
    value = Patches(
        explanation="x" * (MAX_PUBLIC_TEXT - 4) + "offline-key-secret",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "pass",
            }
        ],
    )
    final = observer.completed_data(value, Patches)["content"]
    assert len(final) == MAX_PUBLIC_TEXT
    assert final.endswith("[red") and not final.endswith("offl")


@pytest.mark.parametrize("boundary", ["closed", "cap"])
def test_public_projection_never_reparses_or_retains_tail_after_boundary(
    settings, monkeypatch, boundary
):
    import workbench.streaming as streaming

    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "coding", Patches, True)
    calls = []
    project = streaming.root_string_projection

    def tracked(source, field):
        calls.append(len(source))
        return project(source, field)

    monkeypatch.setattr(streaming, "root_string_projection", tracked)
    if boundary == "closed":
        # An escaped quote must not end the projection; the genuine quote must.
        observer.content('{"explanation":"hello \\"')
        assert not observer.projection_finished
        observer.content(' world"')
        expected = 'hello " world'
    else:
        observer.content('{"explanation":"' + "x" * streaming.MAX_PUBLIC_TEXT)
        expected = "x" * streaming.MAX_PUBLIC_TEXT
    assert observer.projection_finished and observer.raw == ""
    boundary_calls = len(calls)
    tail = ',"patches":[{"content":"' + "private-body" * 20000 + '"}]}'
    for offset in range(0, len(tail), 32):
        observer.content(tail[offset : offset + 32])
    assert len(calls) == boundary_calls
    assert observer.raw == "" and observer.sent == expected
    assert not any(kind == "assistant_completed" for kind, _ in fake.events)


def test_projection_cap_keeps_split_key_held_until_full_validated_redaction(settings, monkeypatch):
    import workbench.streaming as streaming

    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    settings.api_key = SecretStr("cap-split-key-secret")
    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "coding", Patches, True)
    prefix = "x" * (streaming.MAX_PUBLIC_TEXT - 4)
    observer.content('{"explanation":"' + prefix + "cap-")
    assert observer.projection_finished and observer.sent == prefix

    def forbidden_reparse(*args):
        pytest.fail("Public projection must remain frozen after its display cap")

    monkeypatch.setattr(streaming, "root_string_projection", forbidden_reparse)
    observer.content('split-key-secret","patches":[] }')
    assert observer.sent == prefix and observer.raw == ""
    result = Patches(
        explanation=prefix + "cap-split-key-secret",
        patches=[
            {
                "path": "custom_rules.py",
                "before_sha256": "0" * 64,
                "content": "pass",
            }
        ],
    )
    completed = observer.completed_data(result, Patches)
    assert completed["content"] == prefix + "[red"
    assert "cap-" not in "".join(data.get("text", "") for _, data in fake.events)


def test_worker_recovery_closes_abandoned_stream_after_model_profile_change(store):
    class WorkerCrash(BaseException):
        pass

    class CrashStream(httpx.SyncByteStream):
        def __iter__(self):
            yield frame('{"summary":"old model draft')
            raise WorkerCrash()

    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        body = (
            CrashStream()
            if len(calls) == 1
            else Bytes(
                stream_body(ModelReview(summary="new model result").model_dump_json()), size=31
            )
        )
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)

    model = gateway(store, handler)
    run = new_run(store)
    job = store.claim()
    with pytest.raises(WorkerCrash):
        model.complete(run, "review:recovery", "JSON", {}, ModelReview)
    draft = store.transcript(run)["messages"][-1]
    assert draft["validation"] == "pending" and draft["content"] == "old model draft"
    store.settings.model = "different-model-after-restart"
    store.recover()
    interrupted = store.transcript(run)["messages"][-1]
    assert interrupted["message_id"] == draft["message_id"]
    assert interrupted["validation"] == "failed" and interrupted["content"] == ""
    assert interrupted["code"] == "worker_interrupted"
    resumed = store.claim()
    assert resumed["id"] == job["id"]
    assert (
        model.complete(run, "review:recovery", "JSON", {}, ModelReview).summary
        == "new model result"
    )
    store.finish(resumed, "WAITING_REQUIREMENTS")
    messages = store.transcript(run)["messages"]
    assert messages[-1]["response_id"] != draft["response_id"]
    assert messages[-1]["validation"] == "validated"
    assert not any(row["validation"] == "pending" for row in messages)
    assert len(calls) == 2


def test_worker_recovery_repairs_committed_step_before_missing_completion_event(store, monkeypatch):
    class WorkerCrash(BaseException):
        pass

    calls = []

    def handler(request):
        calls.append(json.loads(request.content))
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=Bytes(
                stream_body(
                    ModelReview(summary="validated offline-key-secret result").model_dump_json()
                ),
                size=32,
            ),
        )

    model = gateway(store, handler)
    run = new_run(store)
    job = store.claim()
    append = store.assistant_event

    def crash_before_completion(run_id, kind, data):
        if kind == "assistant_completed":
            raise WorkerCrash()
        return append(run_id, kind, data)

    monkeypatch.setattr(store, "assistant_event", crash_before_completion)
    with pytest.raises(WorkerCrash):
        model.complete(run, "review:committed", "JSON", {}, ModelReview)
    draft = store.transcript(run)["messages"][-1]
    assert draft["validation"] == "pending"
    assert store.model_records(run)[0]["status"] == "validated"
    monkeypatch.setattr(store, "assistant_event", append)
    store.recover()
    store.recover()  # Recovery itself must be idempotent.
    completed = store.transcript(run)["messages"][-1]
    assert completed["message_id"] == draft["message_id"]
    assert completed["validation"] == "validated"
    assert completed["content"] == "validated [redacted] result"
    assert not any(event["kind"] == "assistant_failed" for event in assistant_events(store, run))
    resumed = store.claim()
    assert resumed["id"] == job["id"]
    model.complete(run, "review:committed", "JSON", {}, ModelReview)
    assert len(calls) == 1
    assert (
        sum(event["kind"] == "assistant_completed" for event in assistant_events(store, run)) == 1
    )
    assert "offline-key-secret" not in json.dumps(assistant_events(store, run))


def test_recovery_does_not_fail_drafts_outside_recovered_running_jobs(store):
    run = new_run(store)
    observer = AssistantStream(store, store.settings, run, "unrelated", "review", ModelReview, True)
    observer.content('{"summary":"queued fixture')
    store.recover()
    assert store.transcript(run)["messages"][-1]["validation"] == "pending"


@pytest.mark.parametrize(
    "keys,summary",
    [
        (("ababa",), "abababa"),
        (("ababa",), "ababababababa"),
        (("aa",), "aaaaaa"),
        (("abcde", "cdefg"), "abcdefghi"),
        (("aaaa", "aabaa"), "aaaaaabaaaaa"),
    ],
)
def test_overlapping_keys_never_emit_inconsistent_or_unredacted_prefix(settings, keys, summary):
    class Store:
        def __init__(self):
            self.events = []

        def assistant_event(self, run_id, kind, data):
            self.events.append((kind, dict(data)))

    settings.api_key = SecretStr(keys[0])
    if len(keys) > 1:
        settings.planning_api_key = SecretStr(keys[1])
    fake = Store()
    observer = AssistantStream(fake, settings, "run", "response", "review", ModelReview, True)
    final = observer.completed_data(ModelReview(summary=summary), ModelReview)["content"]
    for char in json.dumps({"summary": summary}):
        observer.content(char)
        assert final.startswith(observer.sent)
    if keys == ("ababa",) and summary == "abababa":
        assert final == "[redacted]ba"
        assert observer.sent == ""
    for key in keys:
        assert key not in "".join(data.get("text", "") for _, data in fake.events)
````
