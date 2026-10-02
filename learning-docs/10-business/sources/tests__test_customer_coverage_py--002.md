# tests/test_customer_coverage.py · 2/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_customer_coverage_py--001.md) · [下一段](tests__test_customer_coverage_py--003.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_final_python_required_priority_is_not_changed_by_next_optional_subject`（L880–L904）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L884断言`coverage_gaps(requirement, plan) == []`；L885遍历`(("priority", False), ("assignee_id", True), ("due_at", True))`；L896断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L897断言`any( item["targets"] == [{"entity": "requests", "field": name}] and item["attribute"]…`；L904断言`coverage_gaps(requirement, plan)`。 调用`actual_customer_field_case`、`next`、`coverage_gaps`、`plan.model_copy`、`any`、`typed_field_ledger`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_query_conflict_with_typed_prohibition_keeps_both_provenances`（L907–L929）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L914断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L915断言`any( item["source"]["section"] == "features" and item["targets"] == [{"entity": "requ…`；L928断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L929断言`any(item["source"]["section"] == "field_requirements" for item in diagnostics)`。 调用`actual_customer_field_case`、`FieldRequirement`、`coverage_gaps`、`any`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_ambiguous_duplicate_prose_does_not_override_typed_entity_policies`（L935–L949）：接收`heading`。 控制顺序：L937遍历`plan.entities`；L938按`entity.name == "tasks"`分支；L939遍历`entity.fields`；L940按`field.name in {"title", "detail"}`分支；L944断言`coverage_gaps(requirement, plan) == []`；L948断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L949断言`all(item["source"]["section"] == "field_requirements" for item in diagnostics)`。 调用`actual_customer_field_case`、`typed_field_ledger`、`coverage_gaps`、`next`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_entity_or_universal_subject_preserves_positive_and_false_obligations`（L954–L977）：接收`scope`、`negative`。 控制顺序：L960遍历`plan.entities`；L961遍历`entity.fields`；L962按`field.name == "title"`分支；L964断言`coverage_gaps(requirement, plan) == []`；L974断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L975断言`any( target["entity"] == target_entity for item in diagnostics for target in item["ta…`。 调用`actual_customer_field_case`、`coverage_gaps`、`next`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_combined_capability_heading_cannot_donate_operations_to_a_bare_list`（L983–L987）：接收`heading`。 控制顺序：L987断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_single_operation_heading_is_an_explicit_field_list_predicate`（L991–L998）：接收`heading`。 控制顺序：L994断言`coverage_gaps(requirement, plan) == []`；L998断言`any("searchable" in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`coverage_gaps`、`next`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_false_operation_heading_is_not_discarded_as_context`（L1002–L1008）：接收`heading`。 控制顺序：L1006断言`coverage_gaps(requirement, plan)`；L1008断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`next`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_property_headings_retain_values_and_entity_scope`（L1033–L1055）：接收`entity`、`heading`、`attribute`、`expected`、`invalid`。 控制顺序：L1046断言`coverage_gaps(requirement, plan) == []`；L1049断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1050断言`any( item["attribute"] == attribute and item["expected"] == expected and item["target…`。 调用`actual_customer_field_case`、`next`、`setattr`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unique_field_property_heading_is_not_discarded`（L1062–L1069）：接收`heading`、`attribute`、`expected`、`invalid`。 控制顺序：L1067断言`coverage_gaps(requirement, plan) == []`；L1069断言`coverage_gaps(requirement, plan)`。 调用`actual_customer_field_case`、`next`、`setattr`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `encode_fact_shapes`（L1170–L1182）：接收`facts`、`encoding`。 控制顺序：L1175按`encoding == "json"`分支；L1177按`encoding == "items"`分支。 调用`deepcopy`、`json.dumps`、`facts.items`。 返回路径：L1176的`{key: json.dumps(value, ensure_ascii=False) for key, value in facts.items()}`；L1178的`{ key: [json.dumps(item, ensure_ascii=False) for item in value] for key, value in facts.it…`；L1182的`facts`。
- `test_business_structures_are_not_field_names_kinds_or_enum_lists`（L1187–L1192）：接收`facts`、`encoding`。 控制顺序：L1191断言`coverage_gaps(requirement, plan) == []`；L1192断言`requirement.model_dump() == before`。 调用`actual_customer_field_case`、`encode_fact_shapes`、`requirement.model_dump`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_field_constraints_nested_in_metadata_cannot_disappear`（L1200–L1228）：接收`namespace`、`encoding`。 控制顺序：L1214断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1215断言`any( item["attribute"] == "required" and item["targets"] == [{"entity": "requests", "…`；L1228断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`encode_fact_shapes`、`coverage_gaps`、`any`、`next`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_relation_field_attributes_are_preserved_without_treating_roles_as_choices`（L1232–L1256）：接收`encoding`。 控制顺序：L1248断言`coverage_gaps(requirement, plan) == []`；L1256断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`encode_fact_shapes`、`coverage_gaps`、`next`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_enum_descriptor_preserves_membership_inside_json`（L1260–L1272）：接收`encoding`。 控制顺序：L1270断言`coverage_gaps(requirement, plan) == []`；L1272断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`encode_fact_shapes`、`coverage_gaps`、`any`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_genuine_missing_field_declaration_is_not_satisfied_by_metadata_or_ancestor`（L1285–L1297）：接收`facts`。 控制顺序：L1289断言`any( "missing" in gap for gap in coverage_gaps(requirement, plan, diagnostics=diagnos…`；L1292断言`any( item["code"] == "structured_missing_field" and item["source"]["path"] and not it…`。 调用`actual_customer_field_case`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_field_identifier_can_equal_a_metadata_namespace`（L1301–L1309）：接收`name`。 控制顺序：L1307断言`any("required" in gap for gap in coverage_gaps(requirement, plan))`；L1309断言`coverage_gaps(requirement, plan) == []`。 调用`actual_customer_field_case`、`plan.entities[0].fields.append`、`FieldSpec`、`any`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structured_subject_identity_does_not_match_wrapper_field_names`（L1312–L1326）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1315断言`coverage_gaps(requirement, plan) == []`；L1324断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1325断言`diagnostics[0]["targets"] == [{"entity": "tasks", "field": "resolved_at"}]`；L1326断言`diagnostics[0]["source"]["path"] == "title"`。 调用`actual_customer_field_case`、`coverage_gaps`、`next`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_structured_field_fact_and_typed_opposite_constraint_both_remain_blocking`（L1329–L1349）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1335遍历`[(True, "facts"), (False, "field_requirements")]`；L1344断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1345断言`any( item["source"]["section"] == source and item["targets"] == [{"entity": "requests…`。 调用`actual_customer_field_case`、`FieldRequirement`、`next`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_explicit_field_kind_blocks_without_parser_crash`（L1353–L1357）：接收`kind`。 控制顺序：L1357断言`bool(gaps) is (kind is not None)`。 调用`actual_customer_field_case`、`coverage_gaps`、`bool`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_explicit_field_entity_cannot_fall_back_to_another_target`（L1361–L1364）：接收`entity`。 控制顺序：L1364断言`coverage_gaps(requirement, plan)`。 调用`actual_customer_field_case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_keyed_field_constraints_honor_their_explicit_entity_identity`（L1367–L1387）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1377断言`coverage_gaps(requirement, plan) == []`；L1386断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1387断言`diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]`。 调用`actual_customer_field_case`、`next`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_json_encoded_enum_attribute_keeps_membership_and_raw_source`（L1390–L1407）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1404断言`coverage_gaps(requirement, plan) == []`；L1405断言`requirement.model_dump() == before`；L1407断言`any("choices" in gap for gap in coverage_gaps(requirement, plan))`。 调用`actual_customer_field_case`、`json.dumps`、`requirement.model_dump`、`coverage_gaps`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `scoped_resource_field_case`（L1410–L1433）：接收`attribute`、`expected`、`other`、`kind`。 源码说明：Repeated identifiers with deliberately different per-entity properties.。 调用`customer_case`、`Plan`。 返回路径：L1433的`requirement, plan`。
- `encode_resource_collection`（L1436–L1448）：接收`collection`、`encoding`。 控制顺序：L1439按`encoding == "json"`分支；L1441按`encoding == "items"`分支；L1442按`isinstance(collection, list)`分支。 调用`json.dumps`、`isinstance`、`collection.items`。 返回路径：L1440的`json.dumps(collection)`；L1443的`[json.dumps(item) for item in collection]`；L1444的`{ key: json.dumps(value) if isinstance(value, (dict, list)) else value for key, value in c…`。
- `test_resource_namespace_scopes_every_field_property_without_cross_binding`（L1466–L1503）：接收`attribute`、`expected`、`other`、`kind`、`shape`、`encoding`。 控制顺序：L1476按`shape == "entity_list"`分支；L1479按`shape == "name_list"`分支；L1482按`shape == "keyed"`分支；L1485按`shape == "aliased_key"`分支；L1495断言`coverage_gaps(requirement, plan) == []`；L1496断言`requirement.model_dump() == before`；L1499断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1500断言`len(diagnostics) == 1`。后续分支沿下方源码相同行号继续阅读。 调用`scoped_resource_field_case`、`encode_resource_collection`、`requirement.model_dump`、`coverage_gaps`、`setattr`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_relation_namespace_uses_source_scope_and_never_target_or_wrapper_scope`（L1508–L1536）：接收`shape`、`encoding`。 控制顺序：L1511按`shape == "list"`分支；L1514按`shape == "keyed"`分支；L1517按`shape == "source_group"`分支；L1520按`shape == "single"`分支；L1527按`shape == "resource_nested"`分支；L1530断言`coverage_gaps(requirement, plan) == []`；L1533断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1534断言`len(diagnostics) == 1`。后续分支沿下方源码相同行号继续阅读。 调用`scoped_resource_field_case`、`encode_resource_collection`、`coverage_gaps`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_leaf_explicit_entity_overrides_resource_context_and_keeps_typed_conflict`（L1540–L1552）：接收`namespace`。 控制顺序：L1546遍历`[(True, "facts"), (False, "field_requirements")]`；L1549断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1550断言`len(diagnostics) == 1`；L1551断言`diagnostics[0]["source"]["section"] == section`；L1552断言`diagnostics[0]["targets"] == [{"entity": "beta", "field": "value"}]`。 调用`scoped_resource_field_case`、`FieldRequirement`、`coverage_gaps`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_resource_or_relation_scope_cannot_fall_back_to_matching_field`（L1557–L1568）：接收`scope`、`namespace`。 控制顺序：L1566断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1567断言`diagnostics[0]["code"] == "structured_missing_field"`；L1568断言`diagnostics[0]["source"]["path"].startswith(namespace)`。 调用`scoped_resource_field_case`、`coverage_gaps`、`diagnostics[0]["source"]["path"].startswith`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_conflicting_relation_source_identifiers_block_instead_of_picking_one`（L1571–L1578）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1577断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1578断言`diagnostics[0]["code"] == "structured_missing_field"`。 调用`scoped_resource_field_case`、`coverage_gaps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_business_names_and_prose_do_not_supply_implicit_field_scope`（L1582–L1600）：接收`name`。 控制顺序：L1600断言`coverage_gaps(requirement, plan) == []`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_resource_and_field_identifiers_can_collide_with_namespace_names`（L1605–L1616）：接收`entity`、`field`。 控制顺序：L1608遍历`plan.entities`；L1611断言`coverage_gaps(requirement, plan) == []`；L1614断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1615断言`diagnostics[0]["targets"] == [{"entity": entity, "field": field}]`；L1616断言`diagnostics[0]["source"]["path"] == f"resources.{entity}.fields.{field}"`。 调用`scoped_resource_field_case`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chinese_query_result_nouns_never_declare_field_operations`（L1634–L1642）：接收`enabled`、`attribute`、`kind`、`operation`、`noun`。 控制顺序：L1642断言`coverage_gaps(requirement, plan) == []`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_english_query_result_nouns_never_declare_field_operations`（L1655–L1663）：接收`enabled`、`attribute`、`kind`、`operation`、`noun`。 控制顺序：L1663断言`coverage_gaps(requirement, plan) == []`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_operation_predicates_with_result_nouns_preserve_typed_contradictions`（L1683–L1700）：接收`attribute`、`kind`、`text`。 控制顺序：L1690断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1691断言`any( item["source"]["section"] == "acceptance" and item["attribute"] == attribute and…`；L1699断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1700断言`all(item["source"]["section"] == "field_requirements" for item in diagnostics)`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`any`、`setattr`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inflected_operation_result_nouns_do_not_create_query_flags`（L1704–L1708）：接收`operation`。 控制顺序：L1708断言`coverage_gaps(requirement, plan) == []`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_explicit_negated_condition_bindings_are_still_false_obligations`（L1721–L1736）：接收`attribute`、`kind`、`text`。 控制顺序：L1726断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1727断言`any( item["source"]["section"] == "features" and item["attribute"] == attribute and i…`；L1735断言`coverage_gaps(requirement, plan, diagnostics=diagnostics)`；L1736断言`all(item["source"]["section"] == "field_requirements" for item in diagnostics)`。 调用`scoped_resource_field_case`、`typed_field_ledger`、`coverage_gaps`、`any`、`setattr`、`all`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_2a4_fastapi_search_result_acceptance_preserves_independent_query_flags`（L1739–L1758）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L1745断言`coverage_gaps(requirement, plan) == []`；L1746遍历`[("name", "searchable"), ("category", "filterable")]`；L1754断言`coverage_gaps(requirement, changed, diagnostics=diagnostics)`；L1755断言`any( item["source"]["section"] == "acceptance" and item["attribute"] == flag for item…`。 调用`actual_customer_field_case`、`typed_field_ledger`、`coverage_gaps`、`plan.model_copy`、`setattr`、`next`、`any`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_customer_coverage.py`；**本文件共有 3 段**。本段覆盖源文件 L880–L1760。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`35048`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_customer_coverage.py", "part": 2, "parts": 3, "encoding": "utf-8", "sha256": "e92c82ad943e38bd011ecf623466a3a6043e7197030ddcd5d4dbc867031403a4"} -->
````python
# tests/test_customer_coverage.py
def test_final_python_required_priority_is_not_changed_by_next_optional_subject():
    requirement, plan = actual_customer_field_case()
    requirement.features = [FINAL_REQUEST_FIELDS]
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    assert coverage_gaps(requirement, plan) == []
    for name, invalid in (("priority", False), ("assignee_id", True), ("due_at", True)):
        changed = plan.model_copy(deep=True)
        field = next(
            field
            for entity in changed.entities
            if entity.name == "requests"
            for field in entity.fields
            if field.name == name
        )
        field.required = invalid
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["targets"] == [{"entity": "requests", "field": name}]
            and item["attribute"] == "required"
            for item in diagnostics
        )
    requirement.field_requirements = typed_field_ledger(plan)
    next(field for field in requests.fields if field.name == "priority").required = False
    assert coverage_gaps(requirement, plan)


def test_explicit_query_conflict_with_typed_prohibition_keeps_both_provenances():
    requirement, plan = actual_customer_field_case()
    requirement.features = ["服务请求管理：记录 title、detail、customer_id，按 customer_id 搜索"]
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="customer_id", searchable=False)
    ]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features"
        and item["targets"] == [{"entity": "requests", "field": "customer_id"}]
        for item in diagnostics
    )
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "customer_id"
    ).searchable = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize(
    "heading", ["请求搜索与筛选", "Service request queries", "功能说明：请求查询"]
)
def test_ambiguous_duplicate_prose_does_not_override_typed_entity_policies(heading):
    requirement, plan = actual_customer_field_case()
    for entity in plan.entities:
        if entity.name == "tasks":
            for field in entity.fields:
                if field.name in {"title", "detail"}:
                    field.searchable = False
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"{heading}：按 title、detail 搜索"]
    assert coverage_gaps(requirement, plan) == []
    requests = next(entity for entity in plan.entities if entity.name == "requests")
    next(field for field in requests.fields if field.name == "title").searchable = False
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize("scope", ["requests", "所有实体", "all entities", "both entities"])
@pytest.mark.parametrize("negative", [False, True])
def test_explicit_entity_or_universal_subject_preserves_positive_and_false_obligations(
    scope, negative
):
    requirement, plan = actual_customer_field_case()
    operation = "不提供搜索" if negative else "必须可搜索"
    requirement.features = [f"{scope}：title{operation}"]
    for entity in plan.entities:
        for field in entity.fields:
            if field.name == "title":
                field.searchable = not negative
    assert coverage_gaps(requirement, plan) == []
    target_entity = "requests" if scope == "requests" else "tasks"
    next(
        field
        for entity in plan.entities
        if entity.name == target_entity
        for field in entity.fields
        if field.name == "title"
    ).searchable = negative
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        target["entity"] == target_entity for item in diagnostics for target in item["targets"]
    )


@pytest.mark.parametrize(
    "heading", ["客户搜索与筛选", "Customer search and filtering", "搜索和筛选"]
)
def test_combined_capability_heading_cannot_donate_operations_to_a_bare_list(heading):
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"{heading}：name、organization、contact"]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("heading", ["search", "搜索", "search fields", "关键词搜索"])
def test_single_operation_heading_is_an_explicit_field_list_predicate(heading):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers：{heading}: name, organization, contact"]
    assert coverage_gaps(requirement, plan) == []
    next(
        field for field in plan.entities[0].fields if field.name == "organization"
    ).searchable = False
    assert any("searchable" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("heading", ["searchable=false", "禁止搜索", "不提供搜索"])
def test_explicit_false_operation_heading_is_not_discarded_as_context(heading):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers：{heading}: name"]
    name = next(field for field in plan.entities[0].fields if field.name == "name")
    assert coverage_gaps(requirement, plan)
    name.searchable = False
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("entity", ["requests", "tasks"])
@pytest.mark.parametrize(
    "heading,attribute,expected,invalid",
    [
        ("required", "required", True, False),
        ("required=true", "required", True, False),
        ("required=false", "required", False, True),
        ("required: false", "required", False, True),
        ("optional", "required", False, True),
        ("required fields", "required", True, False),
        ("必填", "required", True, False),
        ("必填字段", "required", True, False),
        ("可选", "required", False, True),
        ("非必填", "required", False, True),
        ("max_length=120", "max_length", 120, 200),
        ("max_length: 120", "max_length", 120, 200),
        ("min_length=1", "min_length", 1, 0),
        ("min_length=0", "min_length", 0, 1),
        ("长度上限120", "max_length", 120, 200),
        ("最小长度0", "min_length", 0, 1),
    ],
)
def test_explicit_property_headings_retain_values_and_entity_scope(
    entity, heading, attribute, expected, invalid
):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"{entity}: {heading}: title"]
    target = next(
        field
        for item in plan.entities
        if item.name == entity
        for field in item.fields
        if field.name == "title"
    )
    setattr(target, attribute, expected)
    assert coverage_gaps(requirement, plan) == []
    setattr(target, attribute, invalid)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == attribute
        and item["expected"] == expected
        and item["targets"] == [{"entity": entity, "field": "title"}]
        for item in diagnostics
    )


@pytest.mark.parametrize(
    "heading,attribute,expected,invalid",
    [("max_length=120", "max_length", 120, 200), ("min_length=1", "min_length", 1, 0)],
)
def test_unique_field_property_heading_is_not_discarded(heading, attribute, expected, invalid):
    requirement, plan = actual_customer_field_case()
    requirement.features = [f"customers: {heading}: name"]
    name = next(field for field in plan.entities[0].fields if field.name == "name")
    setattr(name, attribute, expected)
    assert coverage_gaps(requirement, plan) == []
    setattr(name, attribute, invalid)
    assert coverage_gaps(requirement, plan)


STRUCTURED_BUSINESS_METADATA = [
    {
        "metrics": [
            {
                "name": "requests_total",
                "entity": "requests",
                "kind": "count",
                "role_scope": ["manager", "service"],
            }
        ]
    },
    {
        "metrics": [
            {
                "name": "title",
                "entity": "requests",
                "kind": "average_duration",
                "start_field": "created_at",
                "end_field": "resolved_at",
                "role_scope": ["manager"],
                "filters": [{"field": "request_state", "op": "in", "value": ["resolved"]}],
            }
        ]
    },
    {
        "relations": [
            {
                "entity": "requests",
                "field": "customer_id",
                "target_entity": "customers",
                "roles": ["manager", "service"],
            }
        ]
    },
    {
        "permissions": [
            {
                "entity": "requests",
                "role": "service",
                "scope": "assigned",
                "actions": ["read", "update", "add_note"],
            }
        ]
    },
    {
        "notifications": [
            {
                "entity": "requests",
                "event": "transitioned",
                "transition": "resolve",
                "recipient": "creator",
                "role_scope": ["employee"],
            }
        ]
    },
    {
        "roles": [
            {
                "name": "category",
                "label": "可选分类",
                "actions": ["read"],
                "role_scope": ["manager"],
            }
        ]
    },
    {
        "resources": [
            {"entity": "requests", "assignee_field": "assignee_id", "notes": True, "required": True}
        ]
    },
    {
        "workflows": [
            {
                "entity": "requests",
                "status_field": "request_state",
                "transitions": [
                    {
                        "name": "title",
                        "from_states": ["new"],
                        "to_state": "active",
                        "roles": ["manager", "service"],
                    }
                ],
            }
        ]
    },
    {
        "entities": [
            {
                "name": "requests",
                "fields": ["title", "detail"],
                "role_scope": ["manager", "service"],
            }
        ]
    },
]


def encode_fact_shapes(facts, encoding):
    import json
    from copy import deepcopy

    facts = deepcopy(facts)
    if encoding == "json":
        return {key: json.dumps(value, ensure_ascii=False) for key, value in facts.items()}
    if encoding == "items":
        return {
            key: [json.dumps(item, ensure_ascii=False) for item in value]
            for key, value in facts.items()
        }
    return facts


@pytest.mark.parametrize("facts", STRUCTURED_BUSINESS_METADATA)
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_business_structures_are_not_field_names_kinds_or_enum_lists(facts, encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(facts, encoding)
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before


@pytest.mark.parametrize(
    "namespace",
    ["metrics", "relations", "permissions", "notifications", "roles", "resources", "workflows"],
)
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_explicit_field_constraints_nested_in_metadata_cannot_disappear(namespace, encoding):
    requirement, plan = actual_customer_field_case()
    facts = {
        namespace: [
            {
                "name": "business_definition",
                "entity": "requests",
                "role_scope": ["manager"],
                "field_constraints": [{"entity": "requests", "field": "title", "required": False}],
            }
        ]
    }
    requirement.facts = encode_fact_shapes(facts, encoding)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["attribute"] == "required"
        and item["targets"] == [{"entity": "requests", "field": "title"}]
        and item["source"]["path"] == f"{namespace}.0.field_constraints.0"
        for item in diagnostics
    )
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "title"
    ).required = False
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_relation_field_attributes_are_preserved_without_treating_roles_as_choices(encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(
        {
            "relations": [
                {
                    "entity": "requests",
                    "field": "customer_id",
                    "target_entity": "customers",
                    "required": True,
                    "roles": ["manager", "employee"],
                }
            ]
        },
        encoding,
    )
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "requests"
        for field in entity.fields
        if field.name == "customer_id"
    ).required = False
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_explicit_enum_descriptor_preserves_membership_inside_json(encoding):
    requirement, plan = actual_customer_field_case()
    requirement.facts = encode_fact_shapes(
        {
            "fields": [
                {"entity": "customers", "name": "category", "choices": ["个人", "企业", "合作伙伴"]}
            ]
        },
        encoding,
    )
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[-1].choices = ["个人", "企业"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


@pytest.mark.parametrize(
    "facts",
    [
        {"fields": [{"field": "missing", "required": True}]},
        {"fields": [{"entity": "requests", "field": "missing"}]},
        {"requests": {"missing": {"required": True}}},
        {"fields": {"missing": {"choices": ["a", "b"]}}},
        {"title": {"entity": "requests", "field": "missing", "required": True}},
    ],
)
def test_genuine_missing_field_declaration_is_not_satisfied_by_metadata_or_ancestor(facts):
    requirement, plan = actual_customer_field_case()
    requirement.facts = facts
    diagnostics = []
    assert any(
        "missing" in gap for gap in coverage_gaps(requirement, plan, diagnostics=diagnostics)
    )
    assert any(
        item["code"] == "structured_missing_field"
        and item["source"]["path"]
        and not item["targets"]
        for item in diagnostics
    )


@pytest.mark.parametrize("name", ["metrics", "permissions", "fields", "entities", "role_scope"])
def test_field_identifier_can_equal_a_metadata_namespace(name):
    from workbench.domain import FieldSpec

    requirement, plan = actual_customer_field_case()
    plan.entities[0].fields.append(FieldSpec(name=name, kind="text", required=True))
    requirement.facts = {"fields": {name: {"entity": "customers", "required": False}}}
    assert any("required" in gap for gap in coverage_gaps(requirement, plan))
    plan.entities[0].fields[-1].required = False
    assert coverage_gaps(requirement, plan) == []


def test_structured_subject_identity_does_not_match_wrapper_field_names():
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"title": {"entity": "tasks", "field": "resolved_at", "required": False}}
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "resolved_at"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "resolved_at"}]
    assert diagnostics[0]["source"]["path"] == "title"


def test_structured_field_fact_and_typed_opposite_constraint_both_remain_blocking():
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = [
        FieldRequirement(entity="requests", field="title", required=True)
    ]
    requirement.facts = {"fields": [{"entity": "requests", "name": "title", "required": False}]}
    for value, source in [(True, "facts"), (False, "field_requirements")]:
        next(
            field
            for entity in plan.entities
            if entity.name == "requests"
            for field in entity.fields
            if field.name == "title"
        ).required = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == source
            and item["targets"] == [{"entity": "requests", "field": "title"}]
            for item in diagnostics
        )


@pytest.mark.parametrize("kind", [{"type": "text"}, ["text"], True, None])
def test_malformed_explicit_field_kind_blocks_without_parser_crash(kind):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"fields": [{"entity": "requests", "field": "title", "kind": kind}]}
    gaps = coverage_gaps(requirement, plan)
    assert bool(gaps) is (kind is not None)


@pytest.mark.parametrize("entity", [17, {}, "not an identifier"])
def test_invalid_explicit_field_entity_cannot_fall_back_to_another_target(entity):
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"fields": [{"entity": entity, "field": "title", "required": True}]}
    assert coverage_gaps(requirement, plan)


def test_keyed_field_constraints_honor_their_explicit_entity_identity():
    requirement, plan = actual_customer_field_case()
    requirement.facts = {"title": {"entity": "tasks", "required": False}}
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "title"
    ).required = False
    assert coverage_gaps(requirement, plan) == []
    next(
        field
        for entity in plan.entities
        if entity.name == "tasks"
        for field in entity.fields
        if field.name == "title"
    ).required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": "tasks", "field": "title"}]


def test_json_encoded_enum_attribute_keeps_membership_and_raw_source():
    import json

    requirement, plan = actual_customer_field_case()
    requirement.facts = {
        "fields": [
            {
                "entity": "customers",
                "field": "category",
                "choices": json.dumps(["个人", "企业", "合作伙伴"]),
            }
        ]
    }
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    plan.entities[0].fields[-1].choices = ["企业"]
    assert any("choices" in gap for gap in coverage_gaps(requirement, plan))


def scoped_resource_field_case(attribute, expected, other, kind):
    """Repeated identifiers with deliberately different per-entity properties."""
    requirement, _ = customer_case()
    plan = Plan(
        title="Scoped fields",
        data_scope="shared",
        entities=[
            {
                "name": entity,
                "description": entity,
                "fields": [
                    {
                        "name": "value",
                        "kind": kind,
                        **({"choices": ["a", "b"]} if kind == "enum" else {}),
                        attribute: value,
                    }
                ],
            }
            for entity, value in [("alpha", expected), ("beta", other)]
        ],
        acceptance=["Scoped field constraints"],
    )
    return requirement, plan


def encode_resource_collection(collection, encoding):
    import json

    if encoding == "json":
        return json.dumps(collection)
    if encoding == "items":
        if isinstance(collection, list):
            return [json.dumps(item) for item in collection]
        return {
            key: json.dumps(value) if isinstance(value, (dict, list)) else value
            for key, value in collection.items()
        }
    return collection


@pytest.mark.parametrize(
    "attribute,expected,other,kind",
    [
        ("required", False, True, "text"),
        ("min_length", 0, 1, "text"),
        ("max_length", 120, 160, "text"),
        ("searchable", True, False, "text"),
        ("filterable", False, True, "text"),
        ("date_range", False, True, "date"),
        ("choices", ["a", "b"], ["a", "c"], "enum"),
        ("kind", "text", "integer", "text"),
    ],
)
@pytest.mark.parametrize("shape", ["entity_list", "name_list", "keyed", "aliased_key", "single"])
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_resource_namespace_scopes_every_field_property_without_cross_binding(
    attribute, expected, other, kind, shape, encoding
):
    requirement, plan = scoped_resource_field_case(attribute, expected, other, kind)
    record = {
        "fields": [{"name": "value", attribute: expected}],
        "label": "A resource whose field name also exists elsewhere",
        "capabilities": ["search", "filter", "value"],
        "role_scope": ["manager"],
    }
    if shape == "entity_list":
        collection = [{"entity": "alpha", **record}]
        path = "business.resources.0.fields.0"
    elif shape == "name_list":
        collection = [{"name": "alpha", **record}]
        path = "business.resources.0.fields.0"
    elif shape == "keyed":
        collection = {"alpha": {**record, "fields": {"value": {attribute: expected}}}}
        path = "business.resources.alpha.fields.value"
    elif shape == "aliased_key":
        collection = {"value": {"entity": "alpha", **record}}
        path = "business.resources.value.fields.0"
    else:
        collection = {"entity": "alpha", **record}
        path = "business.resources.fields.0"
    requirement.facts = {
        "business": {"resources": encode_resource_collection(collection, encoding)}
    }
    before = requirement.model_dump()
    assert coverage_gaps(requirement, plan) == []
    assert requirement.model_dump() == before
    setattr(plan.entities[0].fields[0], attribute, other)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "value"}]
    assert diagnostics[0]["attribute"] == attribute
    assert diagnostics[0]["source"]["path"] == path


@pytest.mark.parametrize("shape", ["list", "keyed", "source_group", "resource_nested", "single"])
@pytest.mark.parametrize("encoding", ["native", "json", "items"])
def test_relation_namespace_uses_source_scope_and_never_target_or_wrapper_scope(shape, encoding):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    record = {"field": "value", "to": "beta", "required": False, "kind": "foreign_key"}
    if shape == "list":
        collection = [{"from": "alpha", **record}]
        path = "business.relations.0"
    elif shape == "keyed":
        collection = {"value": {"from": "alpha", **record}}
        path = "business.relations.value"
    elif shape == "source_group":
        collection = {"alpha": [record]}
        path = "business.relations.alpha.0"
    elif shape == "single":
        collection = {"from": "alpha", **record}
        path = "business.relations"
    else:
        collection = [record]
        path = "business.resources.0.relations.0"
    facts = {"relations": encode_resource_collection(collection, encoding)}
    if shape == "resource_nested":
        facts = {"resources": [{"entity": "alpha", **facts}]}
    requirement.facts = {"business": facts}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert len(diagnostics) == 1
    assert diagnostics[0]["targets"] == [{"entity": "alpha", "field": "value"}]
    assert diagnostics[0]["source"]["path"] == path


@pytest.mark.parametrize("namespace", ["resources", "entities", "资源", "实体"])
def test_leaf_explicit_entity_overrides_resource_context_and_keeps_typed_conflict(namespace):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.field_requirements = [FieldRequirement(entity="beta", field="value", required=True)]
    requirement.facts = {
        namespace: {"alpha": {"fields": [{"entity": "beta", "name": "value", "required": False}]}}
    }
    for value, section in [(True, "facts"), (False, "field_requirements")]:
        plan.entities[1].fields[0].required = value
        diagnostics = []
        assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
        assert len(diagnostics) == 1
        assert diagnostics[0]["source"]["section"] == section
        assert diagnostics[0]["targets"] == [{"entity": "beta", "field": "value"}]


@pytest.mark.parametrize("scope", ["missing", 12, {}, "not an identifier"])
@pytest.mark.parametrize("namespace", ["resources", "relations"])
def test_invalid_resource_or_relation_scope_cannot_fall_back_to_matching_field(scope, namespace):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    record = (
        {"entity": scope, "fields": [{"name": "value", "required": False}]}
        if namespace == "resources"
        else {"from": scope, "field": "value", "to": "beta", "required": False}
    )
    requirement.facts = {namespace: [record]}
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "structured_missing_field"
    assert diagnostics[0]["source"]["path"].startswith(namespace)


def test_conflicting_relation_source_identifiers_block_instead_of_picking_one():
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.facts = {
        "relations": [{"from": "alpha", "entity": "beta", "field": "value", "required": True}]
    }
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["code"] == "structured_missing_field"


@pytest.mark.parametrize("name", ["value", "alpha", "resources", "relations"])
def test_business_names_and_prose_do_not_supply_implicit_field_scope(name):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.facts = {
        "business": {
            "resources": [{"name": name, "required": True, "capabilities": ["value", "filter"]}],
            "metrics": [
                {
                    "name": name,
                    "kind": "count",
                    "from": "beta",
                    "to": "alpha",
                    "role_scope": ["manager"],
                }
            ],
            "metadata": {"name": name, "label": "value", "from": "beta"},
        }
    }
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("entity", ["resources", "entities", "relations", "fields"])
@pytest.mark.parametrize("field", ["resources", "relations", "fields", "name"])
def test_resource_and_field_identifiers_can_collide_with_namespace_names(entity, field):
    requirement, plan = scoped_resource_field_case("required", False, True, "text")
    plan.entities[0].name = entity
    for item in plan.entities:
        item.fields[0].name = field
    requirement.facts = {"resources": {entity: {"fields": {field: {"required": False}}}}}
    assert coverage_gaps(requirement, plan) == []
    plan.entities[0].fields[0].required = True
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert diagnostics[0]["targets"] == [{"entity": entity, "field": field}]
    assert diagnostics[0]["source"]["path"] == f"resources.{entity}.fields.{field}"


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize(
    "attribute,kind,operation",
    [
        ("searchable", "text", "搜索"),
        ("searchable", "text", "检索"),
        ("filterable", "text", "精确筛选"),
        ("filterable", "text", "过滤"),
        ("date_range", "date", "日期范围查询"),
        ("date_range", "date", "日期区间筛选"),
    ],
)
@pytest.mark.parametrize(
    "noun", ["结果", "结果集", "的效果", "后的结果", "返回的结果", "输出", "条件"]
)
def test_chinese_query_result_nouns_never_declare_field_operations(
    enabled, attribute, kind, operation, noun
):
    requirement, plan = scoped_resource_field_case(attribute, enabled, not enabled, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        f"alpha: value 的{operation}{noun}由系统展示，没有{operation}{noun}时显示空列表"
    ]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize(
    "attribute,kind,operation",
    [
        ("searchable", "text", "search"),
        ("filterable", "text", "filter"),
        ("date_range", "date", "date range"),
    ],
)
@pytest.mark.parametrize("noun", ["results", "outcomes", "outputs", "conditions", "criteria"])
def test_english_query_result_nouns_never_declare_field_operations(
    enabled, attribute, kind, operation, noun
):
    requirement, plan = scoped_resource_field_case(attribute, enabled, not enabled, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        f"alpha: value appears in the {operation} {noun}; no {operation} {noun} are available"
    ]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "attribute,kind,text",
    [
        ("searchable", "text", "搜索结果中 value 必须支持搜索"),
        ("searchable", "text", "value 的搜索结果应正确；value 必须支持搜索"),
        ("filterable", "text", "按 value 筛选搜索结果"),
        ("filterable", "text", "filter results by value"),
        ("searchable", "text", "search results using value"),
        ("searchable", "text", "value 作为搜索条件"),
        ("filterable", "text", "value 用作精确筛选条件"),
        ("searchable", "text", "搜索条件包括 value"),
        ("filterable", "text", "value is a filter condition"),
        ("searchable", "text", "search criteria: value"),
        ("date_range", "date", "value 作为日期范围查询条件"),
        ("date_range", "date", "date range conditions include value"),
    ],
)
def test_explicit_operation_predicates_with_result_nouns_preserve_typed_contradictions(
    attribute, kind, text
):
    requirement, plan = scoped_resource_field_case(attribute, False, False, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = ["alpha: " + text]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "acceptance"
        and item["attribute"] == attribute
        and item["targets"] == [{"entity": "alpha", "field": "value"}]
        for item in diagnostics
    )
    setattr(plan.entities[0].fields[0], attribute, True)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


@pytest.mark.parametrize("operation", ["searched", "filtered", "searching", "filtering"])
def test_inflected_operation_result_nouns_do_not_create_query_flags(operation):
    requirement, plan = scoped_resource_field_case("filterable", False, False, "text")
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = [f"alpha: value is displayed in the {operation} results"]
    assert coverage_gaps(requirement, plan) == []


@pytest.mark.parametrize(
    "attribute,kind,text",
    [
        ("searchable", "text", "value 不可作为搜索条件"),
        ("filterable", "text", "value is not a filter condition"),
        ("date_range", "date", "value 不得用作日期范围查询条件"),
        ("searchable", "text", "搜索条件不包括 value"),
        ("searchable", "text", "search criteria do not include value"),
    ],
)
def test_explicit_negated_condition_bindings_are_still_false_obligations(attribute, kind, text):
    requirement, plan = scoped_resource_field_case(attribute, True, False, kind)
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.features = ["alpha: " + text]
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert any(
        item["source"]["section"] == "features"
        and item["attribute"] == attribute
        and item["expected"] is False
        for item in diagnostics
    )
    setattr(plan.entities[0].fields[0], attribute, False)
    diagnostics = []
    assert coverage_gaps(requirement, plan, diagnostics=diagnostics)
    assert all(item["source"]["section"] == "field_requirements" for item in diagnostics)


def test_exact_2a4_fastapi_search_result_acceptance_preserves_independent_query_flags():
    requirement, plan = actual_customer_field_case()
    requirement.field_requirements = typed_field_ledger(plan)
    requirement.acceptance = [
        "客户列表支持按 name、organization、contact 关键词搜索，并可按 category（企业/个人/合作伙伴）精确筛选，搜索结果符合筛选条件。"
    ]
    assert coverage_gaps(requirement, plan) == []
    for field_name, flag in [("name", "searchable"), ("category", "filterable")]:
        changed = plan.model_copy(deep=True)
        setattr(
            next(field for field in changed.entities[0].fields if field.name == field_name),
            flag,
            False,
        )
        diagnostics = []
        assert coverage_gaps(requirement, changed, diagnostics=diagnostics)
        assert any(
            item["source"]["section"] == "acceptance" and item["attribute"] == flag
            for item in diagnostics
        )


````
