# tests/test_customer_coverage.py · 1/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](tests__test_customer_coverage_py--002.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `customer_case`（L9–L68）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan`、`Requirement`。 返回路径：L68的`requirement, plan`。
- `test_nested_entity_facts_do_not_cross_apply_duplicate_field_names`（L71–L84）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L82断言`coverage_gaps(requirement, plan) == []`；L84断言`any("max_length" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fact_metadata_identifiers_are_not_field_name_fragments`（L87–L94）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L94断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_compact_model_field_summaries_preserve_each_subject`（L107–L143）：接收`typed`。 控制顺序：L110按`typed`分支；L122断言`coverage_gaps(requirement, plan) == []`；L123遍历`[ ("customers", "name", "max_length", 160), ("customers", "organi…`；L143断言`coverage_gaps(requirement, changed)`。 调用`customer_case`、`FieldRequirement`、`field.model_dump`、`set`、`coverage_gaps`、`plan.model_copy`、`next`、`setattr`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_legacy_descriptions_preserve_entity_scope_and_extra_obligations`（L146–L157）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L155断言`coverage_gaps(requirement, plan) == []`；L157断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`FieldRequirement`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_typed_contract_does_not_override_explicit_legacy_conflict`（L160–L168）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L166断言`coverage_gaps(requirement, plan)`；L168断言`coverage_gaps(requirement, plan)`。 调用`customer_case`、`FieldRequirement`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_model_validation_summary_does_not_make_optional_fields_required`（L171–L174）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L174断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_both_length_bounds_use_their_own_number`（L177–L182）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L180断言`coverage_gaps(requirement, plan) == []`；L182断言`coverage_gaps(requirement, plan)`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_qualified_prose_scopes_each_duplicate_field_independently`（L185–L190）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L188断言`coverage_gaps(requirement, plan) == []`；L190断言`coverage_gaps(requirement, plan)`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shared_legacy_subject_cannot_lose_one_field`（L193–L196）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L196断言`any("body" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_known_identifier_description_does_not_invent_alias_field`（L199–L202）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L202断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_presentation_labels_do_not_become_executable_field_obligations`（L205–L219）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L217断言`coverage_gaps(requirement, plan) == []`；L219断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_literally_named_name_is_not_descriptor_metadata`（L223–L231）：接收`fact`。 控制顺序：L226断言`coverage_gaps(requirement, plan) == []`；L228断言`coverage_gaps(requirement, plan)`；L231断言`coverage_gaps(requirement, plan)`。 调用`customer_case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_summary_does_not_invent_category_search`（L244–L250）：接收`text`。 控制顺序：L247断言`coverage_gaps(requirement, plan) == []`；L250断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`requirement.features.append`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_negative_date_capability_cannot_invent_a_date_field`（L263–L268）：接收`text`。 控制顺序：L266断言`coverage_gaps(requirement, plan) == []`；L268断言`any("date_range" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`requirement.features.append`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_negative_clause_cannot_erase_positive_search_requirement`（L271–L276）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L274断言`coverage_gaps(requirement, plan) == []`；L276断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_generic_query_clause_stays_in_its_entity_scope`（L279–L287）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L282断言`coverage_gaps(requirement, plan) == []`；L283遍历`plan.entities[0].fields`；L286断言`plan.entities[1].fields[0].searchable`；L287断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_parenthesized_operation_targets_all_remain_required`（L290–L297）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L293断言`coverage_gaps(requirement, plan) == []`；L294遍历`("name", "organization", "contact")`；L297断言`any("searchable" in gap for gap in coverage_gaps(requirement, changed))`。 调用`customer_case`、`coverage_gaps`、`plan.model_copy`、`next`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_gap_diagnostics_trace_typed_and_legacy_conflict_without_overriding_either`（L300–L316）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L307断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L308断言`diagnostics[0]["source"] == {"section": "features", "index": 0, "clause": 0}`；L309断言`diagnostics[0]["targets"] == [{"entity": "customers", "field": "category"}]`；L310断言`diagnostics[0]["attribute"] == "searchable"`；L313断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L314断言`diagnostics[0]["source"] == {"section": "field_requirements", "index": 0}`；L315断言`diagnostics[0]["expected"] is False`；L316断言`diagnostics[0]["actual"] is True`。 调用`customer_case`、`FieldRequirement`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_customer_field_contract_text_does_not_invent_query_flags`（L319–L343）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L341断言`coverage_gaps(requirement, plan) == []`；L343断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`(ROOT / "examples/requirements/customer-service-contract.md").rea…`、`Requirement`、`line.removeprefix`、`text.splitlines`、`line.startswith`、`coverage_gaps`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_field_prohibition_is_enforced_without_typed_ledger`（L355–L362）：接收`text`、`attribute`。 控制顺序：L360断言`coverage_gaps(requirement, plan) == []`；L362断言`any(attribute in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_textual_false_and_true_conflict_is_never_silently_overridden`（L365–L373）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L371断言`coverage_gaps(requirement, plan)`；L373断言`coverage_gaps(requirement, plan)`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrequested_capability_does_not_disable_other_requested_search`（L376–L380）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L379断言`plan.entities[0].fields[0].searchable is True`；L380断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_textual_false_date_range_is_enforced_for_named_date_field`（L383–L391）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L389断言`coverage_gaps(requirement, plan) == []`；L391断言`any("date_range" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`plan.entities[0].fields.append`、`FieldSpec`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `customer_metric_case`（L394–L437）：接收`kind`。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`next`、`MetricSpec`、`Requirement`、`FieldRequirement`。 返回路径：L437的`requirement, plan`。
- `test_metric_predicates_are_not_list_filter_flags`（L442–L454）：接收`kind`、`section`。 控制顺序：L445按`section == "facts"`分支；L450断言`coverage_gaps(requirement, plan) == []`；L451断言`plan.model_dump() == before`；L454断言`gaps and all("业务指标" in gap for gap in gaps)`。 调用`customer_metric_case`、`setattr`、`plan.model_dump`、`coverage_gaps`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_predicate_still_requires_the_correct_executable_metric`（L458–L472）：接收`mutation`。 控制顺序：L461断言`coverage_gaps(requirement, plan) == []`；L462按`mutation == "missing_business"`分支；L464按`mutation in {"entity", "kind"}`分支；L472断言`any("业务指标" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_metric_case`、`coverage_gaps`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_context_does_not_override_explicit_list_filtering`（L476–L479）：接收`surface`。 控制顺序：L479断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_metric_case`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_predicate_and_unrelated_ui_filter_remain_separate`（L482–L491）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L487断言`coverage_gaps(requirement, plan) == []`；L489断言`any( "filterable" in gap and "category" in gap for gap in coverage_gaps(requirement, …`。 调用`customer_metric_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_predicate_does_not_override_explicit_typed_legacy_conflict`（L494–L508）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L500断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`；L508断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_metric_case`、`any`、`coverage_gaps`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metric_row_scope_does_not_require_global_ui_filter`（L519–L524）：接收`text`。 控制顺序：L523断言`coverage_gaps(requirement, plan) == []`；L524断言`plan.business.model_dump() == before`。 调用`customer_metric_case`、`plan.business.model_dump`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_entity_capability_heading_does_not_make_first_search_field_filterable`（L529–L540）：接收`first`、`heading`。 控制顺序：L538断言`coverage_gaps(requirement, plan) == []`；L540断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`"、".join`、`coverage_gaps`、`requirement.features.append`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unrequested_metric_filter_does_not_become_a_positive_metric_predicate`（L543–L547）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L547断言`coverage_gaps(requirement, plan) == []`。 调用`customer_metric_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `actual_customer_field_case`（L562–L578）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`Plan.model_validate`、`json.loads`、`(ROOT / "examples/plans/customer-service.json").read_text`、`Plan`、`Requirement`。 返回路径：L578的`requirement, plan`。
- `test_exact_real_model_timestamp_exclusions_do_not_invent_query_obligations`（L583–L589）：接收`text`、`section`。 控制顺序：L585按`section == "facts"`分支；L589断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`setattr`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_nonparticipating_timestamp_operations_remain_false_constraints`（L595–L611）：接收`text`、`attribute`、`entity`。 控制顺序：L611断言`any(attribute in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`typed_field_ledger`、`next`、`setattr`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_descriptor_list_keeps_bare_datetime_fields_separate_and_scoped`（L614–L635）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L621断言`coverage_gaps(requirement, plan) == []`；L631断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L632断言`diagnostics[0]["targets"] == [{"entity": "requests", "field": "priority"}]`；L635断言`any("priority" in gap and "必填" in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`next`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_completed_type_only_descriptor_cannot_inherit_next_fields_predicates`（L639–L647）：接收`kind`。 控制顺序：L645断言`coverage_gaps(requirement, plan) == []`；L647断言`any("filterable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`plan.entities[0].fields.insert`、`FieldSpec`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_negative_operation_coordination_stops_at_later_positive_field_clause`（L652–L659）：接收`negative`、`separator`。 控制顺序：L657断言`coverage_gaps(requirement, plan) == []`；L659断言`any("searchable" in gap and "title" in gap for gap in coverage_gaps(requirement, plan…`。 调用`customer_case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_optional_negative_wording_does_not_disable_an_existing_search_capability`（L662–L666）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L665断言`plan.entities[0].fields[0].searchable`；L666断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prohibition_before_field_name_retains_its_false_constraint`（L669–L674）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L672断言`coverage_gaps(requirement, plan) == []`；L674断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_positive_operation_after_negative_contrast_keeps_its_field_subject`（L677–L684）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L681断言`plan.entities[0].fields[-1].filterable`；L682断言`any("filterable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan)…`；L684断言`coverage_gaps(requirement, plan) == []`。 调用`customer_case`、`any`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_shared_predicate_survives_completed_descriptor_boundaries`（L687–L692）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L690断言`coverage_gaps(requirement, plan) == []`；L692断言`any("searchable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan)…`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ambiguous_localized_heading_does_not_inherit_the_previous_entity`（L695–L700）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L698断言`coverage_gaps(requirement, plan) == []`；L700断言`any("title" in gap and "可选" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_unsupported_search_is_false_constraint`（L706–L724）：接收`negative`、`section`、`descriptor`。 控制顺序：L709按`section == "facts"`分支；L715断言`coverage_gaps(requirement, plan) == []`；L718断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L719断言`any( item["attribute"] == "searchable" and item["expected"] is False and item["target…`。 调用`customer_case`、`descriptor.format`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsupported_search_does_not_negate_adjacent_positive_field`（L729–L742）：接收`negative`、`separator`。 控制顺序：L734断言`contact.searchable`；L735断言`coverage_gaps(requirement, plan) == []`；L737断言`any("searchable" in gap and "contact" in gap for gap in coverage_gaps(requirement, pl…`；L740断言`any( "searchable=False" in gap and "name" in gap for gap in coverage_gaps(requirement…`。 调用`customer_case`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsupported_operations_remain_field_scoped`（L754–L763）：接收`negative`、`kind`、`attribute`、`operation`。 控制顺序：L761断言`coverage_gaps(requirement, plan) == []`；L763断言`any(attribute in gap and "extra" in gap for gap in coverage_gaps(requirement, plan))`。 调用`customer_case`、`FieldSpec`、`plan.entities[0].fields.append`、`coverage_gaps`、`setattr`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `typed_field_ledger`（L781–L790）：接收`plan`。 调用`FieldRequirement`、`field.model_dump`、`set`。 返回路径：L782的`[ FieldRequirement( entity=entity.name, field=field.name, **field.model_dump(include=set(F…`。
- `test_exact_final_model_clauses_respect_inventory_heading_and_typed_ledger`（L796–L804）：接收`text`、`section`、`typed`。 控制顺序：L798按`section == "facts"`分支；L802按`typed`分支；L804断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`setattr`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_direct_query_binds_its_own_list_and_unambiguous_section`（L826–L850）：接收`query`、`inventory`、`heading`。 控制顺序：L829遍历`tasks.fields`；L833断言`coverage_gaps(requirement, plan) == []`；L839断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L841断言`query_gaps`；L842断言`all( target["entity"] == "requests" and target["field"] in {"title", "detail"} for it…`；L847断言`all( item["source"]["section"] == "features" and item["source"]["index"] == 0 for ite…`。 调用`actual_customer_field_case`、`next`、`typed_field_ledger`、`coverage_gaps`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_query_headings_and_operation_order_do_not_cross_assign_flags`（L862–L877）：接收`text`。 控制顺序：L865断言`coverage_gaps(requirement, plan) == []`；L867遍历`( ("name", "searchable"), ("organization", "searchable"), ("conta…`；L876断言`any(attribute in gap for gap in coverage_gaps(requirement, changed))`；L877断言`all(not field.filterable for field in customers.fields if field.name != "category")`。 调用`actual_customer_field_case`、`coverage_gaps`、`plan.model_copy`、`next`、`setattr`、`any`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_coverage.py`；**本文件共有 3 段**。本段覆盖源文件 L1–L879。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`36827`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_coverage.py", "part": 1, "parts": 3, "encoding": "utf-8", "sha256": "5fd2b0712b5be0631f9c5c586a01a9cc782f0a68dd09d1941dd4e84c80a2d3b6"} -->
````python
# tests/test_customer_coverage.py
"""Model-style summaries must preserve entity/field subjects without fixture substitution."""

import pytest

from workbench.domain import FieldRequirement, Plan, Requirement
from workbench.requirement_coverage import coverage_gaps


def customer_case():
    plan = Plan(
        title="客服",
        data_scope="shared",
        entities=[
            {
                "name": "customers",
                "description": "客户",
                "fields": [
                    {"name": "name", "kind": "text", "max_length": 120, "searchable": True},
                    {
                        "name": "organization",
                        "kind": "text",
                        "required": False,
                        "max_length": 160,
                        "searchable": True,
                    },
                    {
                        "name": "contact",
                        "kind": "text",
                        "required": False,
                        "max_length": 200,
                        "searchable": True,
                    },
                    {
                        "name": "category",
                        "kind": "enum",
                        "choices": ["企业", "个人"],
                        "filterable": True,
                    },
                ],
            },
            {
                "name": "requests",
                "description": "请求",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 200, "searchable": True},
                    {"name": "detail", "kind": "text", "max_length": 3000, "searchable": True},
                    {"name": "resolved_at", "kind": "datetime", "required": False},
                ],
            },
            {
                "name": "tasks",
                "description": "任务",
                "fields": [
                    {"name": "title", "kind": "text", "max_length": 80, "required": False},
                    {"name": "resolved_at", "kind": "datetime", "required": True},
                ],
            },
        ],
        acceptance=["客服字段合同"],
    )
    requirement = Requirement(
        summary="客服字段合同",
        users=["管理人员"],
        data_scope="shared",
        features=[],
        acceptance=[],
    )
    return requirement, plan


def test_nested_entity_facts_do_not_cross_apply_duplicate_field_names():
    requirement, plan = customer_case()
    requirement.facts = {
        "entities": [
            {
                "name": "requests",
                "fields": [{"name": "title", "required": True, "max_length": 200}],
            },
            {"name": "tasks", "fields": [{"name": "title", "required": False, "max_length": 80}]},
        ]
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[2].fields[0].max_length = 200
    assert any("max_length" in gap for gap in coverage_gaps(requirement, plan))


def test_fact_metadata_identifiers_are_not_field_name_fragments():
    requirement, plan = customer_case()
    requirement.facts = {
        "entity_names": ["customers", "requests", "tasks"],
        "display_name": "客服必填字段验证",
        "request_title": "页面标题",
    }
    assert coverage_gaps(requirement, plan) == []


CUSTOMER_FEATURES = [
    "customers：name（必填文本，最长120，可搜索）、organization（可选文本，最长160，可搜索）、"
    "contact（可选文本，最长200，可搜索）、category（必填枚举，可精确筛选）",
    "requests：title（必填文本，最长200，可搜索）、detail（必填文本，最长3000，可搜索）、"
    "resolved_at（可选 datetime）",
    "tasks：title（可选文本，最长80）、resolved_at（必填 datetime）",
]


@pytest.mark.parametrize("typed", [False, True])
def test_compact_model_field_summaries_preserve_each_subject(typed):
    requirement, plan = customer_case()
    requirement.features = CUSTOMER_FEATURES
    if typed:
        requirement.field_requirements = [
            FieldRequirement(
                entity=entity.name,
                field=field.name,
                **field.model_dump(
                    include=set(FieldRequirement.model_fields) - {"entity", "field"}
                ),
            )
            for entity in plan.entities
            for field in entity.fields
        ]
    assert coverage_gaps(requirement, plan) == []
    for entity_name, field_name, attribute, value in [
        ("customers", "name", "max_length", 160),
        ("customers", "organization", "required", True),
        ("customers", "contact", "searchable", False),
        ("customers", "category", "filterable", False),
        ("requests", "title", "searchable", False),
        ("requests", "detail", "max_length", 200),
        ("requests", "resolved_at", "required", True),
        ("tasks", "title", "max_length", 200),
        ("tasks", "resolved_at", "required", False),
    ]:
        changed = plan.model_copy(deep=True)
        target = next(
            field
            for entity in changed.entities
            if entity.name == entity_name
            for field in entity.fields
            if field.name == field_name
        )
        setattr(target, attribute, value)
        assert coverage_gaps(requirement, changed), (entity_name, field_name, attribute)


def test_nested_legacy_descriptions_preserve_entity_scope_and_extra_obligations():
    requirement, plan = customer_case()
    requirement.facts = {
        "requests": {"title": {"required": True, "说明": "必填文本，最长200，可搜索"}},
        "tasks": {"title": {"required": False, "说明": "可选文本，最长80"}},
    }
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="title", required=True)
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_typed_contract_does_not_override_explicit_legacy_conflict():
    requirement, plan = customer_case()
    requirement.field_requirements = [
        FieldRequirement(entity="tasks", field="title", required=False)
    ]
    requirement.features = ["tasks：title 必填"]
    assert coverage_gaps(requirement, plan)
    plan.entities[2].fields[0].required = True
    assert coverage_gaps(requirement, plan)


def test_model_validation_summary_does_not_make_optional_fields_required():
    requirement, plan = customer_case()
    requirement.features = ["客户信息包含 name、organization、contact，必填字段缺失时拒绝保存"]
    assert coverage_gaps(requirement, plan) == []


def test_both_length_bounds_use_their_own_number():
    requirement, plan = customer_case()
    requirement.features = ["requests：title 最小长度0，最大长度200"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].max_length = 201
    assert coverage_gaps(requirement, plan)


def test_qualified_prose_scopes_each_duplicate_field_independently():
    requirement, plan = customer_case()
    requirement.features = ["requests.title 必填且最长200、tasks.title 可选且最长80"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[2].fields[0].required = True
    assert coverage_gaps(requirement, plan)


def test_shared_legacy_subject_cannot_lose_one_field():
    requirement, plan = customer_case()
    requirement.features = ["标题和正文都必填并且可搜索"]
    assert any("body" in gap for gap in coverage_gaps(requirement, plan))


def test_known_identifier_description_does_not_invent_alias_field():
    requirement, plan = customer_case()
    requirement.features = ["requests：detail（正文）必填且可搜索"]
    assert coverage_gaps(requirement, plan) == []


def test_presentation_labels_do_not_become_executable_field_obligations():
    requirement, plan = customer_case()
    requirement.facts = {
        "customers": {
            "category": {
                "required": True,
                "choices": ["企业", "个人"],
                "label": "可选分类",
                "choice_labels": {"企业": "必填企业"},
            }
        }
    }
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].choices = ["个人"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("fact", [{"required": True, "max_length": 120}, "必填文本，最长120"])
def test_field_literally_named_name_is_not_descriptor_metadata(fact):
    requirement, plan = customer_case()
    requirement.facts = {"customers": {"name": fact, "organization": {"required": False}}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = False
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[0].required = True
    plan.entities[0].fields[0].max_length = 200
    assert coverage_gaps(requirement, plan)


@pytest.mark.parametrize(
    "text",
    [
        "customers：支持分类筛选和关键词搜索",
        "customers：支持关键词搜索和category分类筛选",
        "category用于客户分类，name、organization、contact可搜索",
        "客户支持关键词搜索（name、organization、contact）和按category精确筛选",
        "客户支持关键词搜索(name、organization、contact)和按category精确筛选",
    ],
)
def test_query_summary_does_not_invent_category_search(text):
    requirement, plan = customer_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    # A genuine category-search requirement must still conflict with this plan.
    requirement.features.append("customers：category必须可搜索")
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text",
    [
        "datetime字段searchable=false、filterable=false、date_range=false",
        "时间字段不搜索、不筛选、无日期范围",
        "datetime仅存储时间戳，不添加搜索或日期范围",
        "datetime 字段不支持 date_range",
        "datetime仅存储，不要求日期范围筛选",
    ],
)
def test_negative_date_capability_cannot_invent_a_date_field(text):
    requirement, plan = customer_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    requirement.features.append("必须支持日期范围筛选")
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))


def test_negative_clause_cannot_erase_positive_search_requirement():
    requirement, plan = customer_case()
    requirement.features = ["customers：name可搜索，category不支持搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_generic_query_clause_stays_in_its_entity_scope():
    requirement, plan = customer_case()
    requirement.features = ["customers：支持分类筛选和关键词搜索"]
    assert coverage_gaps(requirement, plan) == []
    for field in plan.entities[0].fields:
        field.searchable = False
    # requests.title still searches, but cannot satisfy customers' obligation.
    assert plan.entities[1].fields[0].searchable
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_parenthesized_operation_targets_all_remain_required():
    requirement, plan = customer_case()
    requirement.features = ["customers：关键词搜索（name、organization、contact）和category筛选"]
    assert coverage_gaps(requirement, plan) == []
    for name in ("name", "organization", "contact"):
        changed = plan.model_copy(deep=True)
        next(field for field in changed.entities[0].fields if field.name == name).searchable = False
        assert any("searchable" in gap for gap in coverage_gaps(requirement, changed)), name


def test_gap_diagnostics_trace_typed_and_legacy_conflict_without_overriding_either():
    requirement, plan = customer_case()
    requirement.field_requirements = [
        FieldRequirement(entity="customers", field="category", searchable=False)
    ]
    requirement.features = ["customers：category必须可搜索"]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["source"] == {"section": "features", "index": 0, "clause": 0}
    assert diagnostics[0]["targets"] == [{"entity": "customers", "field": "category"}]
    assert diagnostics[0]["attribute"] == "searchable"
    plan.entities[0].fields[-1].searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["source"] == {"section": "field_requirements", "index": 0}
    assert diagnostics[0]["expected"] is False
    assert diagnostics[0]["actual"] is True


def test_exact_customer_field_contract_text_does_not_invent_query_flags():
    import json

    from workbench.settings import ROOT

    # This fixture is a comparison target only; the real-provider harness still
    # obtains every Requirement and Plan from the authorized provider.
    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    text = (ROOT / "examples/requirements/customer-service-contract.md").read_text(encoding="utf-8")
    requirement = Requirement(
        summary="客服字段合同",
        users=["客服"],
        acceptance=[],
        data_scope="shared",
        features=[
            line.removeprefix("- ")
            for line in text.splitlines()
            if line.startswith(("- customers：", "- requests：", "- tasks：", "字段的补充精确定义"))
        ],
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text,attribute",
    [
        ("customers.category searchable=false", "searchable"),
        ("customers：category filterable=false", "filterable"),
        ("customers：category 禁用搜索", "searchable"),
        ("customers：category 禁止筛选", "filterable"),
    ],
)
def test_explicit_field_prohibition_is_enforced_without_typed_ledger(text, attribute):
    requirement, plan = customer_case()
    requirement.features = [text]
    target = plan.entities[0].fields[-1]
    setattr(target, attribute, False)
    assert coverage_gaps(requirement, plan) == []
    setattr(target, attribute, True)
    assert any(attribute in gap for gap in coverage_gaps(requirement, plan))


def test_textual_false_and_true_conflict_is_never_silently_overridden():
    requirement, plan = customer_case()
    requirement.features = [
        "customers.category searchable=false",
        "customers.category searchable=true",
    ]
    assert coverage_gaps(requirement, plan)
    plan.entities[0].fields[-1].searchable = True
    assert coverage_gaps(requirement, plan)


def test_unrequested_capability_does_not_disable_other_requested_search():
    requirement, plan = customer_case()
    requirement.features = ["customers：name 不要求搜索"]
    assert plan.entities[0].fields[0].searchable is True
    assert coverage_gaps(requirement, plan) == []


def test_textual_false_date_range_is_enforced_for_named_date_field():
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    plan.entities[0].fields.append(FieldSpec(name="meeting_date", kind="date"))
    requirement.features = ["customers.meeting_date date_range=false"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].date_range = True
    assert any("date_range" in gap for gap in coverage_gaps(requirement, plan))


def customer_metric_case(kind="count"):
    import json

    from workbench.business_contracts import MetricSpec
    from workbench.settings import ROOT

    plan = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    field = next(
        f
        for e in plan.entities
        if e.name == "requests"
        for f in e.fields
        if f.name == "request_state"
    )
    field.filterable = False
    options = {
        "count": {},
        "group_count": {"group_by": "priority"},
        "time_count": {"time_field": "created_at"},
        "average_duration": {"start_field": "created_at", "end_field": "resolved_at"},
    }[kind]
    plan.business.metrics = [
        MetricSpec(
            name="matching",
            label="条件指标",
            entity="requests",
            kind=kind,
            filters=[{"field": "request_state", "op": "eq", "value": "resolved"}],
            **options,
        )
    ]
    requirement = Requirement(
        summary="指标合同",
        users=["管理人员", "服务人员"],
        features=[],
        acceptance=[],
        data_scope="shared",
        field_requirements=[
            FieldRequirement(entity="requests", field="request_state", filterable=False)
        ],
    )
    return requirement, plan


@pytest.mark.parametrize("kind", ["count", "group_count", "time_count", "average_duration"])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_metric_predicates_are_not_list_filter_flags(kind, section):
    requirement, plan = customer_metric_case(kind)
    text = f"requests：业务指标（{kind}，按 request_state=resolved 筛选）"
    if section == "facts":
        requirement.facts = {"统计条件": text}
    else:
        setattr(requirement, section, [text])
    before = plan.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert plan.model_dump() == before
    plan.business.metrics[0].filters = []
    gaps = coverage_gaps(requirement, plan)
    assert gaps and all("业务指标" in gap for gap in gaps)


@pytest.mark.parametrize("mutation", ["entity", "kind", "value", "op", "missing_business"])
def test_metric_predicate_still_requires_the_correct_executable_metric(mutation):
    requirement, plan = customer_metric_case()
    requirement.features = ["已解决数（count，按 requests.request_state=resolved 筛选）"]
    assert coverage_gaps(requirement, plan) == []
    if mutation == "missing_business":
        plan.business = None
    elif mutation in {"entity", "kind"}:
        setattr(
            plan.business.metrics[0], mutation, "tasks" if mutation == "entity" else "time_count"
        )
    else:
        setattr(
            plan.business.metrics[0].filters[0], mutation, "active" if mutation == "value" else "ne"
        )
    assert any("业务指标" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("surface", ["列表", "表格", "页面", "查询参数", "list", "table", "UI"])
def test_metric_context_does_not_override_explicit_list_filtering(surface):
    requirement, plan = customer_metric_case()
    requirement.features = [f"统计{surface}必须支持 request_state 筛选"]
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


def test_metric_predicate_and_unrelated_ui_filter_remain_separate():
    requirement, plan = customer_metric_case()
    requirement.features = [
        "已解决数（count，按 request_state=resolved 筛选），客户列表支持 category 筛选"
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any(
        "filterable" in gap and "category" in gap for gap in coverage_gaps(requirement, plan)
    )


def test_metric_predicate_does_not_override_explicit_typed_legacy_conflict():
    requirement, plan = customer_metric_case()
    requirement.features = [
        "已解决数（count，按 request_state=resolved 筛选）",
        "requests.request_state filterable=true",
    ]
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))
    next(
        f
        for e in plan.entities
        if e.name == "requests"
        for f in e.fields
        if f.name == "request_state"
    ).filterable = True
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "text",
    [
        "所有统计指标按本人可见权限范围过滤",
        "服务人员的count指标按assigned负责范围筛选",
        "manager/service的统计按角色权限筛选，只计算可见行",
    ],
)
def test_metric_row_scope_does_not_require_global_ui_filter(text):
    requirement, plan = customer_metric_case()
    requirement.features = [text]
    before = plan.business.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert plan.business.model_dump() == before


@pytest.mark.parametrize("first", ["name", "organization", "contact"])
@pytest.mark.parametrize("heading", ["客户管理", "customers：", "客户档案（customers）"])
def test_entity_capability_heading_does_not_make_first_search_field_filterable(first, heading):
    requirement, plan = customer_case()
    names = [first, *[name for name in ("name", "organization", "contact") if name != first]]
    requirement.features = [
        heading
        + "支持关键词搜索和精确筛选，字段包括"
        + "、".join(name + "（可搜索）" for name in names)
        + "、category（可精确筛选）"
    ]
    assert coverage_gaps(requirement, plan) == []
    requirement.features.append(f"customers：{first}搜索和精确筛选")
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


def test_unrequested_metric_filter_does_not_become_a_positive_metric_predicate():
    requirement, plan = customer_metric_case()
    requirement.features = ["count统计无需request_state筛选"]
    plan.business.metrics[0].filters = []
    assert coverage_gaps(requirement, plan) == []


ACTUAL_TIMESTAMP_EXCLUSIONS = [
    "resolved_at 与 due_at 仅作为时间戳存储，不提供关键词搜索、精确筛选或日期范围筛选。",
    "datetime 字段（resolved_at、due_at）仅存储时间戳，不参与搜索、筛选或日期范围查询；关系键字段不参与关键词搜索与日期范围。",
]
ACTUAL_REQUEST_DESCRIPTORS = (
    "请求字段：title（必填，≤200，可搜索）、detail（必填，≤3000，可搜索）、"
    "customer_id（必填关系键→customers）、assignee_id（可选关系键→$users）、"
    "request_state（必填枚举 new/active/resolved）、resolved_at（datetime）、due_at（datetime）、"
    "priority（必填枚举 普通/紧急，可精确筛选）"
)


def actual_customer_field_case():
    import json

    from workbench.settings import ROOT

    # Public deterministic contract is only the unit-test comparison target.
    # These exact Requirement excerpts came from the sanitized real-run report.
    source = Plan.model_validate(
        json.loads((ROOT / "examples/plans/customer-service.json").read_text(encoding="utf-8"))
    )
    plan = Plan(
        title="字段合同", data_scope="shared", entities=source.entities, acceptance=["字段合同验证"]
    )
    requirement = Requirement(
        summary="客服字段", users=["客服"], data_scope="shared", features=[], acceptance=[]
    )
    return requirement, plan


@pytest.mark.parametrize("text", ACTUAL_TIMESTAMP_EXCLUSIONS)
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
def test_exact_real_model_timestamp_exclusions_do_not_invent_query_obligations(text, section):
    requirement, plan = actual_customer_field_case()
    if section == "facts":
        requirement.facts = {"字段查询约束": text}
    else:
        setattr(requirement, section, [text])
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("text", ACTUAL_TIMESTAMP_EXCLUSIONS)
@pytest.mark.parametrize("attribute", ["searchable", "filterable", "date_range"])
@pytest.mark.parametrize("entity", ["requests", "tasks"])
def test_explicit_nonparticipating_timestamp_operations_remain_false_constraints(
    text, attribute, entity
):
    requirement, plan = actual_customer_field_case()
    requirement.acceptance = [text]
    # The actual run also supplied per-entity false flags. An unscoped repeated
    # name cannot independently establish that every entity shares one policy.
    requirement.field_requirements = typed_field_ledger(plan)
    field = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "due_at"
    )
    setattr(field, attribute, True)
    assert any(attribute in gap for gap in coverage_gaps(requirement, plan))


def test_exact_descriptor_list_keeps_bare_datetime_fields_separate_and_scoped():
    requirement, plan = actual_customer_field_case()
    requirement.features = [ACTUAL_REQUEST_DESCRIPTORS]
    tasks = next(entity for entity in plan.entities if entity.name == "tasks")
    next(field for field in tasks.fields if field.name == "title").required = False
    next(field for field in tasks.fields if field.name == "detail").required = False
    next(field for field in tasks.fields if field.name == "assignee_id").required = True
    assert coverage_gaps(requirement, plan) == []
    priority = next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "priority"
    )
    priority.filterable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "requests", "field": "priority"}]
    priority.filterable = True
    priority.required = False
    assert any("priority" in gap and "必填" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("kind", ["datetime", "text", "integer", "boolean"])
def test_completed_type_only_descriptor_cannot_inherit_next_fields_predicates(kind):
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    plan.entities[0].fields.insert(0, FieldSpec(name="extra", kind=kind, required=False))
    requirement.features = [f"customers：extra（{kind}）、category（必填枚举，可精确筛选）"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].filterable = False
    assert any("filterable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("negative", ["不参与", "不提供"])
@pytest.mark.parametrize("separator", ["、", "与", "和", "或", "以及"])
def test_negative_operation_coordination_stops_at_later_positive_field_clause(negative, separator):
    requirement, plan = customer_case()
    requirement.features = [
        f"requests：resolved_at{negative}搜索{separator}日期范围查询，但title必须可搜索"
    ]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[1].fields[0].searchable = False
    assert any("searchable" in gap and "title" in gap for gap in coverage_gaps(requirement, plan))


def test_optional_negative_wording_does_not_disable_an_existing_search_capability():
    requirement, plan = customer_case()
    requirement.features = ["customers：name不要求搜索与日期范围查询"]
    assert plan.entities[0].fields[0].searchable
    assert coverage_gaps(requirement, plan) == []


def test_prohibition_before_field_name_retains_its_false_constraint():
    requirement, plan = customer_case()
    requirement.features = ["customers：禁止category搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].searchable = True
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


def test_positive_operation_after_negative_contrast_keeps_its_field_subject():
    requirement, plan = customer_case()
    requirement.features = ["customers：name不提供搜索，但必须支持精确筛选"]
    plan.entities[0].fields[0].searchable = False
    assert plan.entities[0].fields[-1].filterable  # Another field cannot satisfy name's filter.
    assert any("filterable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[0].filterable = True
    assert coverage_gaps(requirement, plan) == []


def test_explicit_shared_predicate_survives_completed_descriptor_boundaries():
    requirement, plan = customer_case()
    requirement.features = ["customers：name（必填文本）、contact（可选文本）均可搜索"]
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].searchable = False
    assert any("searchable" in gap and "name" in gap for gap in coverage_gaps(requirement, plan))


def test_ambiguous_localized_heading_does_not_inherit_the_previous_entity():
    requirement, plan = customer_case()
    requirement.features = ["tasks：title（可选）；另一组字段：title（可选）"]
    assert coverage_gaps(requirement, plan) == []
    requirement.features = ["tasks：title（可选）；所有实体：title（可选）"]
    assert any("title" in gap and "可选" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("descriptor", ["name（{negative}搜索）", "name{negative}搜索"])
def test_explicit_unsupported_search_is_false_constraint(negative, section, descriptor):
    requirement, plan = customer_case()
    text = "customers：" + descriptor.format(negative=negative)
    if section == "facts":
        requirement.facts = {"查询限制": text}
    else:
        setattr(requirement, section, [text])
    field = plan.entities[0].fields[0]
    field.searchable = False
    assert coverage_gaps(requirement, plan) == []
    field.searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "searchable"
        and item["expected"] is False
        and item["targets"] == [{"entity": "customers", "field": "name"}]
        for item in diagnostics
    )


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize("separator", ["，", "；", "，但", "。"])
def test_unsupported_search_does_not_negate_adjacent_positive_field(negative, separator):
    requirement, plan = customer_case()
    requirement.features = [f"customers：name{negative}搜索{separator}contact必须可搜索"]
    name, contact = plan.entities[0].fields[0], plan.entities[0].fields[2]
    name.searchable = False
    assert contact.searchable
    assert coverage_gaps(requirement, plan) == []
    contact.searchable = False
    assert any("searchable" in gap and "contact" in gap for gap in coverage_gaps(requirement, plan))
    contact.searchable = True
    name.searchable = True
    assert any(
        "searchable=False" in gap and "name" in gap for gap in coverage_gaps(requirement, plan)
    )


@pytest.mark.parametrize("negative", ["不可", "不可以", "不支持"])
@pytest.mark.parametrize(
    "kind,attribute,operation",
    [
        ("text", "searchable", "关键词搜索"),
        ("text", "filterable", "精确筛选"),
        ("date", "date_range", "日期范围查询"),
    ],
)
def test_unsupported_operations_remain_field_scoped(negative, kind, attribute, operation):
    from workbench.domain import FieldSpec

    requirement, plan = customer_case()
    field = FieldSpec(name="extra", kind=kind)
    plan.entities[0].fields.append(field)
    requirement.features = [f"customers：extra{negative}{operation}，name必须可搜索"]
    assert coverage_gaps(requirement, plan) == []
    setattr(field, attribute, True)
    assert any(attribute in gap and "extra" in gap for gap in coverage_gaps(requirement, plan))


FINAL_CUSTOMER_QUERY = (
    "客户搜索与筛选：按 name、organization、contact 关键词搜索，"
    "按 category（企业/个人/合作伙伴）精确筛选。"
)
FINAL_REQUEST_QUERY = (
    "服务请求管理：创建服务请求，记录 title、detail、customer_id、priority、due_at，"
    "并按 title、detail 关键词搜索。"
)
FINAL_REQUEST_FIELDS = (
    "requests 服务请求：创建请求需填写 title（必填，≤200）、detail（必填，≤3000）、"
    "customer_id（必填关联 customers）、priority（必填枚举：普通/紧急），"
    "可选填 assignee_id（关联 $users）、due_at。"
)


def typed_field_ledger(plan):
    return [
        FieldRequirement(
            entity=entity.name,
            field=field.name,
            **field.model_dump(include=set(FieldRequirement.model_fields) - {"entity", "field"}),
        )
        for entity in plan.entities
        for field in entity.fields
    ]


@pytest.mark.parametrize("text", [FINAL_CUSTOMER_QUERY, FINAL_REQUEST_QUERY, FINAL_REQUEST_FIELDS])
@pytest.mark.parametrize("section", ["features", "acceptance", "facts"])
@pytest.mark.parametrize("typed", [False, True])
def test_exact_final_model_clauses_respect_inventory_heading_and_typed_ledger(text, section, typed):
    requirement, plan = actual_customer_field_case()
    if section == "facts":
        requirement.facts = {"功能说明": text}
    else:
        setattr(requirement, section, [text])
    if typed:
        requirement.field_requirements = typed_field_ledger(plan)
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "query",
    [
        "按 title、detail 关键词搜索",
        "对 title、detail 进行关键词搜索",
        "search using title, detail",
        "search by detail and title",
        "using title and detail for keyword search",
    ],
)
@pytest.mark.parametrize(
    "inventory",
    [
        "title、detail、customer_id、priority、due_at",
        "due_at、priority、customer_id、detail、title",
        "priority, title, due_at, customer_id, detail",
    ],
)
@pytest.mark.parametrize("heading", ["服务请求管理", "Request management", "requests"])
def test_direct_query_binds_its_own_list_and_unambiguous_section(query, inventory, heading):
    requirement, plan = actual_customer_field_case()
    tasks = next(entity for entity in plan.entities if entity.name == "tasks")
    for field in tasks.fields:
        field.searchable = False
    requirement.features = [f"{heading}：记录 {inventory}，{query}。"]
    requirement.field_requirements = typed_field_ledger(plan)
    assert coverage_gaps(requirement, plan) == []
    # Prove the explicit prose still carries an independent obligation.
    requirement.field_requirements = []
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    next(field for field in requests.fields if field.name == "title").searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    query_gaps = [item for item in diagnostics if item["attribute"] == "searchable"]
    assert query_gaps
    assert all(
        target["entity"] == "requests" and target["field"] in {"title", "detail"}
        for item in query_gaps
        for target in item["targets"]
    )
    assert all(
        item["source"]["section"] == "features" and item["source"]["index"] == 0
        for item in query_gaps
    )


@pytest.mark.parametrize(
    "text",
    [
        FINAL_CUSTOMER_QUERY,
        "Customer search and filtering: search using contact, name, organization, filter by category.",
        "客户查询：按 category 精确筛选，并对 organization、contact、name 关键词搜索。",
        "customers: filter by category and search using organization, name, contact",
    ],
)
def test_query_headings_and_operation_order_do_not_cross_assign_flags(text):
    requirement, plan = actual_customer_field_case()
    requirement.features = [text]
    assert coverage_gaps(requirement, plan) == []
    customers = plan.entities[0]
    for field_name, attribute in (
        ("name", "searchable"),
        ("organization", "searchable"),
        ("contact", "searchable"),
        ("category", "filterable"),
    ):
        changed = plan.model_copy(deep=True)
        target = next(field for field in changed.entities[0].fields if field.name == field_name)
        setattr(target, attribute, False)
        assert any(attribute in gap for gap in coverage_gaps(requirement, changed)), field_name
    assert all(not field.filterable for field in customers.fields if field.name != "category")


````
