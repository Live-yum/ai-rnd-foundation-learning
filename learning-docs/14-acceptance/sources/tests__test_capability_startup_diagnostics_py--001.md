# tests/test_capability_startup_diagnostics.py · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](tests__test_capability_startup_diagnostics_py--002.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.capability_sandbox`、`workbench.capability_startup_paths`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_startup_hints_are_finite_even_for_secret_bearing_tracebacks`（L25–L57）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L32断言`result == { "phase": "health_deadline", "http_status": 503, "http_error": "other", "o…`；L55断言`"secret" not in json.dumps(result)`；L56断言`len(json.dumps(result)) < 1024`；L57断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`len`、`output.encode`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nontext_startup_output_never_stringifies_candidate_data`（L61–L79）：接收`output`。 控制顺序：L63断言`result["output_readable"] is False`；L64断言`result["http_status"] is None`；L65断言`result["http_error"] == "other"`；L66断言`result["output_hints"] == []`；L67断言`result["startup_phase_hint"] == "unknown"`；L68断言`result["failure_component"] == "unknown"`；L69断言`result["exception_type"] == "unknown"`；L70断言`result["exception_errno"] is None`。后续分支沿下方源码相同行号继续阅读。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_exact_public_module_names_can_be_reported`（L85–L92）：接收`module`。 控制顺序：L89断言`result["known_missing_modules"] == [module]`；L90断言`startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"]…`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_loader_failure_is_not_mislabeled_as_missing_module`（L95–L105）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102断言`result["output_hints"] == ["import-error", "native-library-mapping"]`；L103断言`result["tmpfs_noexec"] is True`；L104断言`"secret" not in json.dumps(result)`；L105断言`startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `colored`（L119–L120）：接收`text`。 调用`"\x1b[0m\x1b[38;2;1;2;3m".join`。 返回路径：L120的`"\x1b[31m" + "\x1b[0m\x1b[38;2;1;2;3m".join(text) + "\x1b[0m"`。
- `test_observed_sgr_can_split_exception_words_and_errno`（L123–L129）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L126断言`result["exception_type"] == "FileNotFoundError"`；L127断言`result["exception_errno"] == 2`；L128断言`result["output_hints"] == ["missing-file"]`；L129断言`result["output_shapes"] == ["file-not-found-type", "ansi-control"]`。 调用`colored`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sgr_trace_retains_same_trace_association_with_later_cleanup`（L132–L141）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L139断言`result["failure_component"] == "multiprocessing-semaphore"`；L140断言`result["exception_type"] == "FileNotFoundError" and result["exception_errno"] == 2`；L141断言`"secret" not in json.dumps(result)`。 调用`"\n".join`、`SEMAPHORE_TRACE.splitlines`、`colored`、`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_oversize_and_non_sgr_sequences_are_not_interpreted`（L147–L151）：接收`prefix`。 控制顺序：L149断言`result["exception_type"] == "unknown"`；L150断言`result["failure_component"] == "unknown"`；L151断言`"private" not in json.dumps(result) and "secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_stripped_control_bytes_do_not_create_a_larger_scan_window`（L154–L160）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L158断言`result["output_nonempty"] is True`；L159断言`result["exception_type"] == "unknown" and result["output_hints"] == []`；L160断言`result["output_shapes"] == ["ansi-control"]`。 调用`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sgr_from_another_trace_cannot_supply_a_semaphore_denial`（L163–L167）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L167断言`startup_failure_diagnostic(trace, 502, "none")["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace`、`"\n".join`、`(first + second).splitlines`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_semaphore_failure_requires_known_constructor_frames_and_denial`（L170–L178）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L172断言`result["failure_component"] == "multiprocessing-semaphore"`；L173断言`result["exception_type"] == "PermissionError"`；L174断言`result["exception_errno"] == 13`；L175断言`result["startup_phase_hint"] == "factory"`；L176断言`result["application_startup_reported"] is False`；L177断言`"secret" not in json.dumps(result)`；L178断言`"passed" not in result`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_partial_or_unrelated_trace_does_not_claim_semaphore`（L193–L196）：接收`old`、`new`。 控制顺序：L195断言`result["failure_component"] == "unknown"`；L196断言`"private_constructor" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`SEMAPHORE_TRACE.replace`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_only_fixed_errno_values_are_emitted`（L200–L202）：接收`number`。 控制顺序：L202断言`result["exception_errno"] == number`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_errno_is_not_copied`（L206–L209）：接收`number`。 控制顺序：L208断言`result["exception_errno"] is None`；L209断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_terminal_unknown_error_does_not_hide_complete_earlier_trace`（L212–L219）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L216断言`result["exception_type"] == "unknown"`；L217断言`result["exception_errno"] is None`；L218断言`result["failure_component"] == "multiprocessing-semaphore"`；L219断言`"SecretError" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno`（L230–L243）：接收`separator`。 控制顺序：L239断言`result["failure_component"] == "multiprocessing-semaphore"`；L240断言`result["exception_type"] == "FileNotFoundError"`；L241断言`result["exception_errno"] == 2`；L242断言`result["output_hints"] == ["permission-denied", "missing-file"]`；L243断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrelated_permission_error_cannot_complete_a_constructor_trace`（L247–L256）：接收`header`。 控制顺序：L254断言`result["exception_type"] == "PermissionError"`；L255断言`result["exception_errno"] == 13`；L256断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_incomplete_traceback_cannot_supply_a_semaphore_hint`（L259–L264）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L262遍历`(no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] p…`；L264断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.split`、`no_error.ljust`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_startup_phase_is_only_a_fixed_hint`（L277–L280）：接收`output`、`phase`。 控制顺序：L279断言`result["startup_phase_hint"] == phase`；L280断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_context_outside_the_existing_output_bound_cannot_supply_a_hint`（L283–L288）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L285断言`result["failure_component"] == "unknown"`；L286断言`result["startup_phase_hint"] == "unknown"`；L287断言`result["exception_type"] == "unknown"`；L288断言`result["exception_errno"] is None`。 调用`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_tail_traceback_preserves_final_error_without_joining_truncated_primary_trace`（L291–L306）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L303断言`result["failure_component"] == "unknown"`；L304断言`result["exception_type"] == "PermissionError"`；L305断言`result["exception_errno"] == 13`；L306断言`"secret" not in json.dumps(result)`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`primary.split`、`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_ascii_output_has_same_byte_budget_before_any_parsing`（L309–L315）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L311断言`result["failure_component"] == "unknown"`；L312断言`result["startup_phase_hint"] == "unknown"`；L313断言`result["exception_type"] == "unknown"`；L314断言`result["exception_errno"] is None`；L315断言`"汉" not in json.dumps(result, ensure_ascii=False)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_split_utf8_and_surrogate_data_never_escape_diagnostic`（L318–L324）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L322断言`result["exception_type"] == "PermissionError"`；L323断言`result["exception_errno"] == 13`；L324断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_command_exit_facts_use_status_only`（L331–L362）：接收`value`、`expected`、`monkeypatch`。 控制顺序：L357断言`startup_command_exit_facts(process, "private-session", "private-command", 5) == { "co…`；L361断言`seen == [5]`；L362断言`daytona_sessions._DEADLINE.get() is None`。 调用`monkeypatch.setattr`、`SimpleNamespace`、`seen.append`、`daytona_sessions.harden_toolbox_transport`、`httpx.Client`、`Process`、`startup_command_exit_facts`、`daytona_sessions._DEADLINE.get`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_command_exit_facts_use_status_only.get_command`（L348–L353）：接收`session_id`、`command_id`。 控制顺序：L349断言`session_id == "private-session" and command_id == "private-command"`。 调用`rest.request`、`Command.from_dict`。 返回路径：L351的`Command.from_dict( {"id": command_id, "command": "secret TOKEN=secret", "exitCode": value}…`。
- `test_pinned_sdk_null_or_omitted_exit_never_proves_running`（L366–L374）：接收`exit_present`。 控制顺序：L370按`exit_present`分支；L374断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`Command.from_dict`、`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_strict_exit_model_rejection_is_safe`（L378–L388）：接收`value`。 控制顺序：L388断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`pytest.raises`、`get_command`、`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_pinned_sdk_strict_exit_model_rejection_is_safe.get_command`（L382–L383）：接收`*args`。 调用`Command.from_dict`。 返回路径：L383的`Command.from_dict({"id": "fixture-command", "command": "secret", "exitCode": value})`。
- `test_malformed_exit_values_remain_unknown`（L392–L396）：接收`value`。 控制顺序：L396断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_different_command_remains_unknown`（L403–L405）：接收`command`。 控制顺序：L405断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`。 调用`SimpleNamespace`、`startup_command_exit_status`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline`（L408–L422）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L416遍历`(SimpleNamespace(), SimpleNamespace(get_session_command=unavailab…`；L417断言`startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"`；L420断言`daytona_sessions._DEADLINE.get() == 123`。 调用`daytona_sessions._DEADLINE.set`、`SimpleNamespace`、`startup_command_exit_status`、`daytona_sessions._DEADLINE.get`、`daytona_sessions._DEADLINE.reset`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline.unavailable`（L411–L412）：接收`*args`。 控制顺序：L412抛异常，停止当前正常路径。 调用`RuntimeError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_command_status_classifier_cannot_disclose_arbitrary_values`（L426–L429）：接收`value`。 控制顺序：L428断言`result["command_exit_status"] == "unknown"`；L429断言`"secret" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `rich_trace`（L432–L456）：接收`exc`、`panel`、`width`、`legacy_windows`。 源码说明：Render real Rich 15 tracebacks, including its actual SGR and borders.。 控制顺序：L448抛异常，停止当前正常路径；L455断言`"\x1b[" in value`。 调用`StringIO`、`Console`、`Traceback.from_exception`、`type`、`console.print`、`Panel`、`output.getvalue`。 返回路径：L456的`value`。
- `test_real_rich_builtin_exception_matrix`（L495–L506）：接收`name`、`panel`。 控制顺序：L497断言`len(output.encode()) < NATIVE_TAIL_LIMIT`；L499断言`result["exception_type"] == name`；L500断言`result["output_raw_bytes"] == len(output.encode())`；L501断言`result["output_normalized_bytes"] < result["output_raw_bytes"]`；L502断言`result["output_normalized_nonspace"] is True`；L503断言`result["output_has_non_sgr_control"] is False`；L504断言`"ansi-control" in result["output_shapes"]`；L505断言`result["failure_component"] == "unknown"`。后续分支沿下方源码相同行号继续阅读。 调用`rich_trace`、`getattr(builtins, name)`、`getattr`、`len`、`output.encode`、`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_empty_message_exception_headers`（L513–L515）：接收`renderer`、`exc`。 控制顺序：L515断言`result["exception_type"] == type(exc).__name__`。 调用`startup_failure_diagnostic`、`renderer`、`type`、`pytest.mark.parametrize`、`"".join`、`traceback.format_exception`、`AssertionError`、`KeyboardInterrupt`、`SystemExit`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_panel_padding_preserves_empty_exception_headers`（L520–L525）：接收`width`、`exception`。 控制顺序：L522断言`len(output.encode()) < NATIVE_TAIL_LIMIT`；L524断言`result["exception_type"] == exception.__name__`；L525断言`result["failure_component"] == "unknown"`。 调用`rich_trace`、`exception`、`len`、`output.encode`、`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_panel_padding_does_not_publish_unknown_empty_exception`（L529–L538）：接收`width`。 控制顺序：L536断言`result["exception_type"] == "unknown"`；L537断言`result["failure_component"] == "unknown"`；L538断言`"PrivateSentinel" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`rich_trace`、`PrivateSentinelError`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_panel_padding_does_not_publish_unknown_empty_exception.PrivateSentinelError`（L530–L531）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_padding_normalization_requires_complete_bounded_known_panel`（L550–L552）：接收`output`。 控制顺序：L552断言`result["exception_type"] == "unknown"`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_chained_trace_preserves_terminal_exception`（L556–L562）：接收`panel`。 控制顺序：L560断言`result["exception_type"] == "KeyError"`；L561断言`result["failure_component"] == "unknown"`；L562断言`"private" not in json.dumps(result)`。 调用`KeyError`、`TypeError`、`startup_failure_diagnostic`、`rich_trace`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_unknown_exception_remains_unknown`（L566–L575）：接收`panel`。 控制顺序：L573断言`result["exception_type"] == "unknown"`；L574断言`"PrivateSentinel" not in json.dumps(result)`；L575断言`"private-sentinel" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`rich_trace`、`PrivateSentinelError`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_rich_unknown_exception_remains_unknown.PrivateSentinelError`（L567–L568）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_unrecognized_prefix_is_not_normalized_into_a_builtin`（L581–L584）：接收`prefix`。 控制顺序：L583断言`result["exception_type"] == "unknown"`；L584断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_bounded_standard_exception_indentation`（L588–L590）：接收`prefix`。 控制顺序：L590断言`result["exception_type"] == "TypeError"`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_rich_wrappers_cannot_complete_a_semaphore_trace`（L593–L601）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L599断言`result["exception_type"] == "PermissionError"`；L600断言`result["exception_errno"] == 13`；L601断言`result["failure_component"] == "unknown"`。 调用`SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").r…`、`SEMAPHORE_TRACE.replace`、`rich_trace`、`PermissionError`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_raw_budget_precedes_sgr_rich_wrappers_and_exception_search`（L606–L614）：接收`limit`、`prefix`。 控制顺序：L609断言`result["output_raw_bytes"] == limit`；L610断言`0 <= result["output_normalized_bytes"] <= limit`；L611断言`result["output_read_limit_reached"] is True`；L612断言`result["exception_type"] == "unknown"`；L613断言`result["failure_component"] == "unknown"`；L614断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_measured_output_facts_do_not_serialize_text`（L630–L637）：接收`output`、`normalized`、`nonspace`、`control`。 控制顺序：L632断言`result["output_raw_bytes"] == len(output.encode())`；L633断言`result["output_normalized_bytes"] == len(normalized.encode())`；L634断言`result["output_normalized_nonspace"] is nonspace`；L635断言`result["output_has_non_sgr_control"] is control`；L636断言`result["output_read_limit_reached"] is False`；L637断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`len`、`output.encode`、`normalized.encode`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_read_limit_fact_measures_observed_cap_without_claiming_truncation`（L642–L646）：接收`limit`、`length`。 控制顺序：L644断言`result["output_read_limit_reached"] is (length >= 0)`；L645断言`result["output_raw_bytes"] == min(limit + length, limit)`；L646断言`"truncated" not in result`。 调用`startup_failure_diagnostic`、`min`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_read_limit_cannot_expand_existing_budget`（L650–L655）：接收`limit`。 控制顺序：L654断言`result["output_raw_bytes"] == 8000`；L655断言`result["exception_type"] == "unknown"`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_exit_code_is_authoritative_and_finite`（L659–L664）：接收`code`。 控制顺序：L663断言`result["command_exit_code"] == code`；L664断言`result["command_exit_status"] == ("zero" if code == 0 else "nonzero")`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_exit_code_is_never_serialized`（L668–L671）：接收`code`。 控制顺序：L670断言`result["command_exit_code"] is None`；L671断言`result["command_exit_status"] == "unknown"`。 调用`startup_failure_diagnostic`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_argparse_fixture_reports_real_exit_two_without_exception`（L674–L698）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L690断言`result.returncode == 2 and result.stdout == ""`；L694断言`diagnostic["command_exit_status"] == "nonzero"`；L695断言`diagnostic["command_exit_code"] == 2`；L696断言`diagnostic["exception_type"] == "unknown"`；L697断言`diagnostic["output_shapes"] == ["cli-usage", "cli-error"]`；L698断言`"private" not in json.dumps(diagnostic)`。 调用`subprocess.run`、`startup_failure_diagnostic`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_owned_argparse_success_does_not_claim_failure_or_usage`（L701–L721）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L715断言`result.returncode == 0`；L719断言`diagnostic["command_exit_code"] == 0`；L720断言`diagnostic["output_shapes"] == []`；L721断言`diagnostic["output_nonempty"] is False`。 调用`subprocess.run`、`startup_failure_diagnostic`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_pydantic_validation_error_has_only_fixed_public_facts`（L727–L741）：接收`renderer`。 控制顺序：L738断言`result["exception_type"] == "ValidationError"`；L739断言`"pydantic-validation" in result["output_shapes"]`；L740断言`"private" not in json.dumps(result)`；L741断言`"OwnedModel" not in json.dumps(result)`。 调用`OwnedModel`、`renderer`、`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`、`"".join`、`traceback.format_exception`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_pydantic_validation_error_has_only_fixed_public_facts.OwnedModel`（L730–L731）：继承`BaseModel`。声明的数据项为`value`；类型约束/数据库列参数以完整定义为准。
- `test_real_sqlalchemy_dbapi_error_uses_exact_public_alias`（L750–L760）：接收`renderer`、`name`。 控制顺序：L758断言`result["exception_type"] == name`；L759断言`"sqlalchemy-error" in result["output_shapes"]`；L760断言`"private" not in json.dumps(result)`。 调用`getattr(exc, name)`、`getattr`、`RuntimeError`、`renderer`、`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`、`"".join`、`traceback.format_exception`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_framework_message_tails_supply_only_finite_format_hints`（L763–L783）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L775遍历`( (pydantic_output, "pydantic-validation"), (sql_output, "sqlalch…`；L781断言`result["exception_type"] == "unknown"`；L782断言`shape in result["output_shapes"]`；L783断言`"private" not in json.dumps(result)`。 调用`create_model`、`range`、`model`、`rich_trace`、`OperationalError`、`RuntimeError`、`output.encode()[-NATIVE_TAIL_LIMIT:].decode`、`output.encode`、`startup_failure_diagnostic`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_qualified_unknown_classes_do_not_inherit_public_suffixes`（L789–L792）：接收`name`。 控制顺序：L791断言`result["exception_type"] == "unknown"`；L792断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `public_framework_classes`（L795–L823）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：Check the installed packages independently of production's frozen list. Their 66 non-warning defining classes also match the native tagged sources: SQLAlchemy 2.0.51, Pydantic 2.12.5, pydantic-core 2.。 控制顺序：L803遍历`( "pydantic", "pydantic.errors", "pydantic_core", "sqlalchemy.exc…`；L811遍历`getattr(module, "__all__", vars(module))`；L812按`name.startswith("_")`分支；L815按`inspect.isclass(value) and issubclass(value, Exception) and not issubclass(value, War…`分支。 调用`importlib.import_module`、`getattr`、`vars`、`name.startswith`、`inspect.isclass`、`issubclass`、`sorted`、`classes.items`。 返回路径：L823的`sorted(classes.items())`。
- `test_verified_public_framework_inventory_has_no_missing_alias`（L827–L831）：接收`alias`、`canonical`。 控制顺序：L829断言`result["exception_type"] == canonical`；L830断言`result["failure_component"] == "unknown"`；L831断言`"private" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`json.dumps`、`pytest.mark.parametrize`、`public_framework_classes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `framework_exception_examples`（L834–L879）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`errors.PydanticUserError`、`errors.PydanticUndefinedAnnotation`、`errors.PydanticImportError`、`errors.PydanticSchemaGenerationError`、`errors.PydanticInvalidForJsonSchema`、`errors.PydanticForbiddenQualifier`、`PydanticCustomError`、`PydanticKnownError`、`PydanticOmit`等。 返回路径：L853的`[ errors.PydanticUserError("private-sentinel", code=None), errors.PydanticUndefinedAnnotat…`。
- `test_real_extended_framework_exception_renderers`（L892–L897）：接收`renderer`、`exc`。 控制顺序：L894断言`result["exception_type"] == type(exc).__name__`；L895断言`result["failure_component"] == "unknown"`；L896断言`"private" not in json.dumps(result)`；L897断言`"PrivateSentinel" not in json.dumps(result)`。 调用`startup_failure_diagnostic`、`renderer`、`type`、`json.dumps`、`pytest.mark.parametrize`、`rich_trace`、`"".join`、`traceback.format_exception`、`framework_exception_examples`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_startup_diagnostics.py`；**本文件共有 2 段**。本段覆盖源文件 L1–L899。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`35629`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_startup_diagnostics.py", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "df648bc3201c0092e2ccc87b79cc1b79759b08cf463395057e49bfb5d5483bf1"} -->
````python
# tests/test_capability_startup_diagnostics.py
"""Startup hints cannot become product acceptance or disclose candidate output."""

import builtins
import importlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import traceback
from io import StringIO
from types import SimpleNamespace

import pytest

from workbench.capability_sandbox import (
    startup_command_exit_facts,
    startup_command_exit_status,
    startup_failure_diagnostic,
)
from workbench.capability_startup_paths import NATIVE_TAIL_LIMIT, node_failure_facts


def test_startup_hints_are_finite_even_for_secret_bearing_tracebacks():
    output = (
        "secret content /private/secret token=secret\n"
        "ModuleNotFoundError: No module named 'secret.module'\n"
        "PermissionError: secret path\nApplication startup complete"
    )
    result = startup_failure_diagnostic(output, 503, "secret transport error")
    assert result == {
        "phase": "health_deadline",
        "http_status": 503,
        "http_error": "other",
        "output_readable": True,
        "output_nonempty": True,
        "output_raw_bytes": len(output.encode()),
        "output_normalized_bytes": len(output.encode()),
        "output_normalized_nonspace": True,
        "output_read_limit_reached": False,
        "output_has_non_sgr_control": False,
        "output_hints": ["permission-denied", "missing-module"],
        "output_shapes": [],
        "known_missing_modules": [],
        "startup_phase_hint": "unknown",
        "failure_component": "unknown",
        "exception_type": "PermissionError",
        "exception_errno": None,
        "application_startup_reported": True,
        "tmpfs_noexec": None,
        "command_exit_status": "unknown",
        "command_exit_code": None,
    }
    assert "secret" not in json.dumps(result)
    assert len(json.dumps(result)) < 1024
    assert "passed" not in result


@pytest.mark.parametrize("output", [None, [], {"secret": "private"}, True])
def test_nontext_startup_output_never_stringifies_candidate_data(output):
    result = startup_failure_diagnostic(output, True, [])
    assert result["output_readable"] is False
    assert result["http_status"] is None
    assert result["http_error"] == "other"
    assert result["output_hints"] == []
    assert result["startup_phase_hint"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    for name in (
        "output_raw_bytes",
        "output_normalized_bytes",
        "output_normalized_nonspace",
        "output_read_limit_reached",
        "output_has_non_sgr_control",
    ):
        assert result[name] is None
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "module", ["uvicorn", "fastapi", "sqlalchemy", "pydantic", "app", "access"]
)
def test_only_exact_public_module_names_can_be_reported(module):
    result = startup_failure_diagnostic(
        "ModuleNotFoundError: No module named '" + module + "'", 502, "none"
    )
    assert result["known_missing_modules"] == [module]
    assert (
        startup_failure_diagnostic("x" * 8000 + "PermissionError", 0, "none")["output_hints"] == []
    )


def test_native_loader_failure_is_not_mislabeled_as_missing_module():
    result = startup_failure_diagnostic(
        "ImportError: /private/secret: failed to map segment from shared object",
        502,
        "none",
        True,
    )
    assert result["output_hints"] == ["import-error", "native-library-mapping"]
    assert result["tmpfs_noexec"] is True
    assert "secret" not in json.dumps(result)
    assert startup_failure_diagnostic("", None, "none", "secret")["tmpfs_noexec"] is None


SEMAPHORE_TRACE = """Traceback (most recent call last):
  File "/private/secret/backend/app/__init__.py", line 146, in create_app
    register_routers(app)
  File "/private/secret/python/concurrent/futures/process.py", line 731, in __init__
    self._call_queue = _SafeQueue(
  File "/private/secret/python/multiprocessing/synchronize.py", line 57, in __init__
    sl = self._semlock = _multiprocessing.SemLock(
PermissionError: [Errno 13] Permission denied: '/private/secret'
"""


def colored(text):
    return "\x1b[31m" + "\x1b[0m\x1b[38;2;1;2;3m".join(text) + "\x1b[0m"


def test_observed_sgr_can_split_exception_words_and_errno():
    output = colored("FileNotFoundError: [Errno 2] No such file or directory")
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["missing-file"]
    assert result["output_shapes"] == ["file-not-found-type", "ansi-control"]


def test_sgr_trace_retains_same_trace_association_with_later_cleanup():
    # Ordinary per-line coloring stays comfortably within the original budget.
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in SEMAPHORE_TRACE.splitlines())
    trace += "\nTraceback (most recent call last):\n" + colored(
        "FileNotFoundError: [Errno 2] secret"
    )
    result = startup_failure_diagnostic(trace, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError" and result["exception_errno"] == 2
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "prefix", ["\x1b[", "\x1b[123", "\x1b[" + "1;" * 10000 + "m", "\x1b]0;private\x07"]
)
def test_incomplete_oversize_and_non_sgr_sequences_are_not_interpreted(prefix):
    result = startup_failure_diagnostic(prefix + "PermissionError: [Errno 13] secret", 502, "none")
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result) and "secret" not in json.dumps(result)


def test_stripped_control_bytes_do_not_create_a_larger_scan_window():
    result = startup_failure_diagnostic(
        "\x1b[0m" * 2000 + "PermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["output_nonempty"] is True
    assert result["exception_type"] == "unknown" and result["output_hints"] == []
    assert result["output_shapes"] == ["ansi-control"]


def test_sgr_from_another_trace_cannot_supply_a_semaphore_denial():
    first = SEMAPHORE_TRACE.replace("PermissionError: [Errno 13]", "FileNotFoundError: [Errno 2]")
    second = "Traceback (most recent call last):\nPermissionError: [Errno 13] secret"
    trace = "\n".join("\x1b[31m" + line + "\x1b[0m" for line in (first + second).splitlines())
    assert startup_failure_diagnostic(trace, 502, "none")["failure_component"] == "unknown"


def test_semaphore_failure_requires_known_constructor_frames_and_denial():
    result = startup_failure_diagnostic(SEMAPHORE_TRACE, 502, "none", True)
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["startup_phase_hint"] == "factory"
    assert result["application_startup_reported"] is False
    assert "secret" not in json.dumps(result)
    assert "passed" not in result


@pytest.mark.parametrize(
    "old,new",
    [
        ("concurrent/futures/process.py", "private/secret.py"),
        ("multiprocessing/synchronize.py", "private/secret.py"),
        ("_multiprocessing.SemLock(", "private_constructor("),
        ("in __init__", "in private_constructor"),
        ("PermissionError", "FileNotFoundError"),
        ("[Errno 13]", "[Errno 2]"),
        ("[Errno 13]", "[Errno 9999999999]"),
    ],
)
def test_partial_or_unrelated_trace_does_not_claim_semaphore(old, new):
    result = startup_failure_diagnostic(SEMAPHORE_TRACE.replace(old, new), 502, "none")
    assert result["failure_component"] == "unknown"
    assert "private_constructor" not in json.dumps(result)


@pytest.mark.parametrize("number", [1, 2, 13, 28, 30])
def test_only_fixed_errno_values_are_emitted(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] == number


@pytest.mark.parametrize("number", [0, -1, 5, 42, 9999999999999999999999999999])
def test_unknown_errno_is_not_copied(number):
    result = startup_failure_diagnostic(f"OSError: [Errno {number}] secret", 502, "none")
    assert result["exception_errno"] is None
    assert "secret" not in json.dumps(result)


def test_terminal_unknown_error_does_not_hide_complete_earlier_trace():
    result = startup_failure_diagnostic(
        SEMAPHORE_TRACE + "\nprivate.SecretError: [Errno 13] secret\n", 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert "SecretError" not in json.dumps(result)


@pytest.mark.parametrize(
    "separator",
    [
        "\n",
        "\nDuring handling of the above exception, another exception occurred:\n\n",
        "\nThe above exception was the direct cause of the following exception:\n\n",
    ],
)
def test_secondary_traceback_keeps_primary_semaphore_hint_and_terminal_errno(separator):
    output = (
        SEMAPHORE_TRACE
        + separator
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "FileNotFoundError: [Errno 2] No such file or directory: '/private/secret'\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "multiprocessing-semaphore"
    assert result["exception_type"] == "FileNotFoundError"
    assert result["exception_errno"] == 2
    assert result["output_hints"] == ["permission-denied", "missing-file"]
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize("header", ["", "Traceback (most recent call last):\n"])
def test_unrelated_permission_error_cannot_complete_a_constructor_trace(header):
    unrelated = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    result = startup_failure_diagnostic(
        unrelated + "\n" + header + "PermissionError: [Errno 13] private\n", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["failure_component"] == "unknown"


def test_incomplete_traceback_cannot_supply_a_semaphore_hint():
    no_header = SEMAPHORE_TRACE.split("\n", 1)[1]
    no_error = SEMAPHORE_TRACE.split("PermissionError:", 1)[0]
    for output in (no_header, no_error.ljust(8000) + "PermissionError: [Errno 13] private"):
        result = startup_failure_diagnostic(output, 502, "none")
        assert result["failure_component"] == "unknown"


@pytest.mark.parametrize(
    "output,phase",
    [
        ('  File "/secret/uvicorn/importer.py", line 10, in import_from_string\n', "import"),
        (SEMAPHORE_TRACE, "factory"),
        ("INFO:     Waiting for application startup.\n" + SEMAPHORE_TRACE, "lifespan"),
        ("ERROR:    Application startup failed. Exiting.", "lifespan"),
        ("private-phase secret", "unknown"),
    ],
)
def test_startup_phase_is_only_a_fixed_hint(output, phase):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["startup_phase_hint"] == phase
    assert "secret" not in json.dumps(result)


def test_context_outside_the_existing_output_bound_cannot_supply_a_hint():
    result = startup_failure_diagnostic("x" * 8000 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None


def test_tail_traceback_preserves_final_error_without_joining_truncated_primary_trace():
    primary = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    output = (
        primary.split("\n", 1)[1]
        + "\nDuring handling of the above exception, another exception occurred:\n\n"
        + "Traceback (most recent call last):\n"
        + '  File "/private/secret/cleanup.py", line 1, in cleanup\n'
        + "PermissionError: [Errno 13] secret\n"
    )
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


def test_non_ascii_output_has_same_byte_budget_before_any_parsing():
    result = startup_failure_diagnostic("汉" * 2667 + SEMAPHORE_TRACE, 502, "none")
    assert result["failure_component"] == "unknown"
    assert result["startup_phase_hint"] == "unknown"
    assert result["exception_type"] == "unknown"
    assert result["exception_errno"] is None
    assert "汉" not in json.dumps(result, ensure_ascii=False)


def test_split_utf8_and_surrogate_data_never_escape_diagnostic():
    result = startup_failure_diagnostic(
        "\ufffd\udc80secret\nPermissionError: [Errno 13] secret", 502, "none"
    )
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert "secret" not in json.dumps(result)


@pytest.mark.parametrize(
    "value,expected",
    [(0, "zero"), (1, "nonzero"), (137, "nonzero"), (255, "nonzero")],
)
def test_pinned_sdk_command_exit_facts_use_status_only(value, expected, monkeypatch):
    import httpx
    from daytona._sync.process import Process
    from daytona_toolbox_api_client.models.command import Command

    from workbench import daytona_sessions

    seen = []
    monkeypatch.setattr(daytona_sessions.time, "monotonic", lambda: 100)
    rest = SimpleNamespace(
        pool_manager=SimpleNamespace(connection_pool_kw={}),
        request=lambda *a, **k: seen.append(k["_request_timeout"]),
    )
    daytona_sessions.harden_toolbox_transport(
        SimpleNamespace(_toolbox_api_client=SimpleNamespace(rest_client=rest))
    )

    def get_command(*, session_id, command_id):
        assert session_id == "private-session" and command_id == "private-command"
        rest.request("GET", "local")
        return Command.from_dict(
            {"id": command_id, "command": "secret TOKEN=secret", "exitCode": value}
        )

    with httpx.Client(trust_env=False) as client:
        process = Process("python", SimpleNamespace(get_session_command=get_command), client)
        assert startup_command_exit_facts(process, "private-session", "private-command", 5) == {
            "command_exit_status": expected,
            "command_exit_code": value,
        }
    assert seen == [5]
    assert daytona_sessions._DEADLINE.get() is None


@pytest.mark.parametrize("exit_present", [False, True])
def test_pinned_sdk_null_or_omitted_exit_never_proves_running(exit_present):
    from daytona_toolbox_api_client.models.command import Command

    payload = {"id": "fixture-command", "command": "secret"}
    if exit_present:
        payload["exitCode"] = None
    command = Command.from_dict(payload)
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [True, False, "1", 1.0])
def test_pinned_sdk_strict_exit_model_rejection_is_safe(value):
    from daytona_toolbox_api_client.models.command import Command
    from pydantic import ValidationError

    def get_command(*args):
        return Command.from_dict({"id": "fixture-command", "command": "secret", "exitCode": value})

    with pytest.raises(ValidationError):
        get_command()
    process = SimpleNamespace(get_session_command=get_command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize("value", [None, True, False, "1", 1.0, [], {}, -1, 256, 10**100])
def test_malformed_exit_values_remain_unknown(value):
    process = SimpleNamespace(
        get_session_command=lambda *a: SimpleNamespace(id="fixture-command", exit_code=value)
    )
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


@pytest.mark.parametrize(
    "command",
    [None, SimpleNamespace(), SimpleNamespace(id="other-command", exit_code=1)],
)
def test_missing_or_different_command_remains_unknown(command):
    process = SimpleNamespace(get_session_command=lambda *a: command)
    assert startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"


def test_missing_sdk_method_and_status_error_remain_unknown_and_restore_deadline():
    from workbench import daytona_sessions

    def unavailable(*args):
        raise RuntimeError("secret session, command and SDK body")

    token = daytona_sessions._DEADLINE.set(123)
    try:
        for process in (SimpleNamespace(), SimpleNamespace(get_session_command=unavailable)):
            assert (
                startup_command_exit_status(process, "session", "fixture-command", 5) == "unknown"
            )
            assert daytona_sessions._DEADLINE.get() == 123
    finally:
        daytona_sessions._DEADLINE.reset(token)


@pytest.mark.parametrize("value", [True, 1, [], {"secret": "secret"}, "running", "secret"])
def test_command_status_classifier_cannot_disclose_arbitrary_values(value):
    result = startup_failure_diagnostic("", 502, "none", command_exit_status=value)
    assert result["command_exit_status"] == "unknown"
    assert "secret" not in json.dumps(result)


def rich_trace(exc, *, panel=False, width=100, legacy_windows=None):
    """Render real Rich 15 tracebacks, including its actual SGR and borders."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.traceback import Traceback

    output = StringIO()
    console = Console(
        file=output,
        width=width,
        force_terminal=True,
        color_system="truecolor",
        no_color=False,
        legacy_windows=legacy_windows,
    )
    try:
        raise exc
    except BaseException as caught:
        rendered = Traceback.from_exception(
            type(caught), caught, caught.__traceback__, show_locals=False, extra_lines=0
        )
        console.print(Panel(rendered) if panel else rendered)
    value = output.getvalue()
    assert "\x1b[" in value
    return value


@pytest.mark.parametrize("panel", [False, True])
@pytest.mark.parametrize(
    "name",
    [
        "TypeError",
        "AttributeError",
        "KeyError",
        "IndexError",
        "NameError",
        "UnboundLocalError",
        "AssertionError",
        "ValueError",
        "RuntimeError",
        "RecursionError",
        "NotImplementedError",
        "ImportError",
        "ModuleNotFoundError",
        "MemoryError",
        "SyntaxError",
        "IndentationError",
        "OSError",
        "FileNotFoundError",
        "PermissionError",
        "TimeoutError",
        "ConnectionRefusedError",
        "ZeroDivisionError",
        "OverflowError",
        "EOFError",
        "StopIteration",
        "SystemExit",
        "KeyboardInterrupt",
        "GeneratorExit",
        "Exception",
        "BaseException",
    ],
)
def test_real_rich_builtin_exception_matrix(name, panel):
    output = rich_trace(getattr(builtins, name)("private-sentinel /private/token"), panel=panel)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == name
    assert result["output_raw_bytes"] == len(output.encode())
    assert result["output_normalized_bytes"] < result["output_raw_bytes"]
    assert result["output_normalized_nonspace"] is True
    assert result["output_has_non_sgr_control"] is False
    assert "ansi-control" in result["output_shapes"]
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
@pytest.mark.parametrize("exc", [AssertionError(), KeyboardInterrupt(), SystemExit()])
def test_real_empty_message_exception_headers(renderer, exc):
    result = startup_failure_diagnostic(renderer(exc), 502, "none")
    assert result["exception_type"] == type(exc).__name__


@pytest.mark.parametrize("width", [80, 100, 120])
@pytest.mark.parametrize("exception", [TypeError, KeyError, SystemExit])
def test_real_rich_panel_padding_preserves_empty_exception_headers(width, exception):
    output = rich_trace(exception(), panel=True, width=width)
    assert len(output.encode()) < NATIVE_TAIL_LIMIT
    result = startup_failure_diagnostic(output, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
    assert result["exception_type"] == exception.__name__
    assert result["failure_component"] == "unknown"


@pytest.mark.parametrize("width", [80, 100, 120])
def test_real_rich_panel_padding_does_not_publish_unknown_empty_exception(width):
    class PrivateSentinelError(Exception):
        pass

    result = startup_failure_diagnostic(
        rich_trace(PrivateSentinelError(), panel=True, width=width), 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "PrivateSentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "output",
    [
        "TypeError" + " " * 80,
        "│ TypeError" + " " * 80,
        "| TypeError" + " " * 80 + " |",
        "│ TypeError" + " " * 600 + " │",
    ],
)
def test_padding_normalization_requires_complete_bounded_known_panel(output):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "unknown"


@pytest.mark.parametrize("panel", [False, True])
def test_real_rich_chained_trace_preserves_terminal_exception(panel):
    terminal = KeyError("private-terminal")
    terminal.__cause__ = TypeError("private-primary")
    result = startup_failure_diagnostic(rich_trace(terminal, panel=panel), 502, "none")
    assert result["exception_type"] == "KeyError"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("panel", [False, True])
def test_real_rich_unknown_exception_remains_unknown(panel):
    class PrivateSentinelError(Exception):
        pass

    result = startup_failure_diagnostic(
        rich_trace(PrivateSentinelError("private-sentinel"), panel=panel), 502, "none"
    )
    assert result["exception_type"] == "unknown"
    assert "PrivateSentinel" not in json.dumps(result)
    assert "private-sentinel" not in json.dumps(result)


@pytest.mark.parametrize(
    "prefix", ["secret.", "prefix ", "│ ", "\x1b]0;private\x07", "\x1b[2J", "\x1b[", " " * 33]
)
def test_unrecognized_prefix_is_not_normalized_into_a_builtin(prefix):
    result = startup_failure_diagnostic(prefix + "TypeError: private", 502, "none")
    assert result["exception_type"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("prefix", ["", "  ", "\t", " " * 32])
def test_bounded_standard_exception_indentation(prefix):
    result = startup_failure_diagnostic(prefix + "TypeError: private", 502, "none")
    assert result["exception_type"] == "TypeError"


def test_rich_wrappers_cannot_complete_a_semaphore_trace():
    first = SEMAPHORE_TRACE.replace("PermissionError", "FileNotFoundError").replace(
        "[Errno 13]", "[Errno 2]"
    )
    output = first + rich_trace(PermissionError(13, "private-sentinel"), panel=True)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "PermissionError"
    assert result["exception_errno"] == 13
    assert result["failure_component"] == "unknown"


@pytest.mark.parametrize("limit", [NATIVE_TAIL_LIMIT, 8000])
@pytest.mark.parametrize("prefix", ["x", "\x1b[0m", "汉", "\x1b]0;secret\x07"])
def test_raw_budget_precedes_sgr_rich_wrappers_and_exception_search(limit, prefix):
    output = prefix * limit + "\n│ TypeError: private │\n"
    result = startup_failure_diagnostic(output, 502, "none", output_limit=limit)
    assert result["output_raw_bytes"] == limit
    assert 0 <= result["output_normalized_bytes"] <= limit
    assert result["output_read_limit_reached"] is True
    assert result["exception_type"] == "unknown"
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "output,normalized,nonspace,control",
    [
        ("", "", False, False),
        ("\x1b[0m\x1b[31m", "", False, False),
        ("\x1b[0m \n\t\r", " \n\t\r", False, False),
        ("\x1b[31munmatched私\x1b[0m", "unmatched私", True, False),
        ("\x1b]0;private\x07", "\x1b]0;private\x07", True, True),
        ("\x1b[2J", "\x1b[2J", True, True),
        ("\x1b[", "\x1b[", True, True),
        ("\x00\x08\x7f\x9b", "\x00\x08\x7f\x9b", True, True),
    ],
)
def test_measured_output_facts_do_not_serialize_text(output, normalized, nonspace, control):
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["output_raw_bytes"] == len(output.encode())
    assert result["output_normalized_bytes"] == len(normalized.encode())
    assert result["output_normalized_nonspace"] is nonspace
    assert result["output_has_non_sgr_control"] is control
    assert result["output_read_limit_reached"] is False
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize("limit", [NATIVE_TAIL_LIMIT, 8000])
@pytest.mark.parametrize("length", [-1, 0, 1])
def test_read_limit_fact_measures_observed_cap_without_claiming_truncation(limit, length):
    result = startup_failure_diagnostic("x" * (limit + length), 502, "none", output_limit=limit)
    assert result["output_read_limit_reached"] is (length >= 0)
    assert result["output_raw_bytes"] == min(limit + length, limit)
    assert "truncated" not in result


@pytest.mark.parametrize("limit", [None, True, "5440", 0, -1, 8001, 10**100])
def test_invalid_read_limit_cannot_expand_existing_budget(limit):
    result = startup_failure_diagnostic(
        "x" * 8000 + "\nTypeError: private", 502, "none", output_limit=limit
    )
    assert result["output_raw_bytes"] == 8000
    assert result["exception_type"] == "unknown"


@pytest.mark.parametrize("code", [0, 1, 2, 127, 137, 255])
def test_exact_exit_code_is_authoritative_and_finite(code):
    result = startup_failure_diagnostic(
        "", 502, "none", command_exit_status="unknown", command_exit_code=code
    )
    assert result["command_exit_code"] == code
    assert result["command_exit_status"] == ("zero" if code == 0 else "nonzero")


@pytest.mark.parametrize("code", [None, True, False, "1", 1.0, [], {}, -1, 256, 10**100])
def test_invalid_exit_code_is_never_serialized(code):
    result = startup_failure_diagnostic("", 502, "none", command_exit_code=code)
    assert result["command_exit_code"] is None
    assert result["command_exit_status"] == "unknown"


def test_owned_argparse_fixture_reports_real_exit_two_without_exception():
    # This owned stdlib fixture executes no candidate code or application imports.
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import argparse; argparse.ArgumentParser(prog='private-sentinel').parse_args()",
            "--unknown-private",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 2 and result.stdout == ""
    diagnostic = startup_failure_diagnostic(
        result.stderr, 502, "none", command_exit_code=result.returncode
    )
    assert diagnostic["command_exit_status"] == "nonzero"
    assert diagnostic["command_exit_code"] == 2
    assert diagnostic["exception_type"] == "unknown"
    assert diagnostic["output_shapes"] == ["cli-usage", "cli-error"]
    assert "private" not in json.dumps(diagnostic)


def test_owned_argparse_success_does_not_claim_failure_or_usage():
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import argparse; argparse.ArgumentParser().parse_args()",
        ],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode == 0
    diagnostic = startup_failure_diagnostic(
        result.stderr, 502, "none", command_exit_code=result.returncode
    )
    assert diagnostic["command_exit_code"] == 0
    assert diagnostic["output_shapes"] == []
    assert diagnostic["output_nonempty"] is False


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
def test_real_pydantic_validation_error_has_only_fixed_public_facts(renderer):
    from pydantic import BaseModel, ValidationError

    class OwnedModel(BaseModel):
        value: int

    try:
        OwnedModel(value="private-sentinel")
    except ValidationError as exc:
        output = renderer(exc)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == "ValidationError"
    assert "pydantic-validation" in result["output_shapes"]
    assert "private" not in json.dumps(result)
    assert "OwnedModel" not in json.dumps(result)


@pytest.mark.parametrize(
    "renderer", [rich_trace, lambda exc: "".join(traceback.format_exception(exc))]
)
@pytest.mark.parametrize(
    "name", ["InterfaceError", "OperationalError", "ProgrammingError", "IntegrityError"]
)
def test_real_sqlalchemy_dbapi_error_uses_exact_public_alias(renderer, name):
    from sqlalchemy import exc

    error = getattr(exc, name)(
        "private-sql", {"private-key": "private-value"}, RuntimeError("private-error")
    )
    output = renderer(error)
    result = startup_failure_diagnostic(output, 502, "none")
    assert result["exception_type"] == name
    assert "sqlalchemy-error" in result["output_shapes"]
    assert "private" not in json.dumps(result)


def test_real_framework_message_tails_supply_only_finite_format_hints():
    from pydantic import ValidationError, create_model
    from sqlalchemy.exc import OperationalError

    model = create_model("PrivateSentinel", **{f"field{n}": (int, ...) for n in range(100)})
    try:
        model(**{f"field{n}": "private-sentinel" for n in range(100)})
    except ValidationError as exc:
        pydantic_output = rich_trace(exc)
    sql_output = rich_trace(
        OperationalError("private-sentinel" * 1000, {}, RuntimeError("private-error"))
    )
    for output, shape in (
        (pydantic_output, "pydantic-validation"),
        (sql_output, "sqlalchemy-error"),
    ):
        tail = output.encode()[-NATIVE_TAIL_LIMIT:].decode("utf-8", errors="ignore")
        result = startup_failure_diagnostic(tail, 502, "none", output_limit=NATIVE_TAIL_LIMIT)
        assert result["exception_type"] == "unknown"
        assert shape in result["output_shapes"]
        assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "name", ["private.ValidationError", "private.OperationalError", "custom.TypeError"]
)
def test_qualified_unknown_classes_do_not_inherit_public_suffixes(name):
    result = startup_failure_diagnostic(name + ": private-sentinel", 502, "none")
    assert result["exception_type"] == "unknown"
    assert "private" not in json.dumps(result)


def public_framework_classes():
    """Check the installed packages independently of production's frozen list.

    Their 66 non-warning defining classes also match the native tagged sources:
    SQLAlchemy 2.0.51, Pydantic 2.12.5, pydantic-core 2.41.5. Tests inspect only
    controller dependencies; no candidate module or downloaded source executes.
    """
    classes = {}
    for module_name in (
        "pydantic",
        "pydantic.errors",
        "pydantic_core",
        "sqlalchemy.exc",
        "sqlalchemy.orm.exc",
    ):
        module = importlib.import_module(module_name)
        for name in getattr(module, "__all__", vars(module)):
            if name.startswith("_"):
                continue
            value = getattr(module, name, None)
            if (
                inspect.isclass(value)
                and issubclass(value, Exception)
                and not issubclass(value, Warning)
            ):
                classes[module_name + "." + name] = value.__name__
                classes[value.__module__ + "." + value.__name__] = value.__name__
                classes[name] = value.__name__
    return sorted(classes.items())


@pytest.mark.parametrize("alias,canonical", public_framework_classes())
def test_verified_public_framework_inventory_has_no_missing_alias(alias, canonical):
    result = startup_failure_diagnostic(alias + ": private-sentinel", 502, "none")
    assert result["exception_type"] == canonical
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)


def framework_exception_examples():
    from pydantic import errors
    from pydantic_core import (
        PydanticCustomError,
        PydanticKnownError,
        PydanticOmit,
        PydanticSerializationError,
        PydanticSerializationUnexpectedValue,
        PydanticUseDefault,
        SchemaError,
    )
    from sqlalchemy import exc
    from sqlalchemy.orm.exc import (
        DetachedInstanceError,
        FlushError,
        MappedAnnotationError,
        StaleDataError,
    )

    return [
        errors.PydanticUserError("private-sentinel", code=None),
        errors.PydanticUndefinedAnnotation("PrivateSentinel", "private-sentinel"),
        errors.PydanticImportError("private-sentinel"),
        errors.PydanticSchemaGenerationError("private-sentinel"),
        errors.PydanticInvalidForJsonSchema("private-sentinel"),
        errors.PydanticForbiddenQualifier("final", "private-sentinel"),
        PydanticCustomError("private-kind", "private-sentinel"),
        PydanticKnownError("int_parsing"),
        PydanticOmit(),
        PydanticUseDefault(),
        PydanticSerializationError("private-sentinel"),
        PydanticSerializationUnexpectedValue("private-sentinel"),
        SchemaError("private-sentinel"),
        exc.InvalidRequestError("private-sentinel"),
        exc.MissingGreenlet("private-sentinel"),
        exc.AwaitRequired("private-sentinel"),
        exc.NoResultFound(),
        exc.MultipleResultsFound(),
        exc.DataError("private-sql", {}, RuntimeError("private-sentinel")),
        exc.InternalError("private-sql", {}, RuntimeError("private-sentinel")),
        exc.NotSupportedError("private-sql", {}, RuntimeError("private-sentinel")),
        DetachedInstanceError("private-sentinel"),
        FlushError("private-sentinel"),
        MappedAnnotationError("private-sentinel"),
        StaleDataError("private-sentinel"),
    ]


@pytest.mark.parametrize(
    "renderer",
    [
        rich_trace,
        lambda exc: rich_trace(exc, panel=True),
        lambda exc: "".join(traceback.format_exception(exc)),
    ],
    ids=["rich", "rich-panel", "plain"],
)
@pytest.mark.parametrize("exc", framework_exception_examples(), ids=lambda exc: type(exc).__name__)
def test_real_extended_framework_exception_renderers(renderer, exc):
    result = startup_failure_diagnostic(renderer(exc), 502, "none")
    assert result["exception_type"] == type(exc).__name__
    assert result["failure_component"] == "unknown"
    assert "private" not in json.dumps(result)
    assert "PrivateSentinel" not in json.dumps(result)


````
