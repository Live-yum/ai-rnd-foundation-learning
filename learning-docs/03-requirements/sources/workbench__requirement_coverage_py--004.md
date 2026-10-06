# workbench/requirement_coverage.py · 4/4

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__requirement_coverage_py--003.md)

**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`、`workbench.requirement_canonical`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `coverage_gaps.gap`（L2373–L2401）：接收`message`、`code`、`targets`、`attribute`、`expected`、`actual`。 控制顺序：L2375按`diagnostics is not None`分支。 调用`gaps.append`、`diagnostics.append`、`dict`、`any`、`re.search`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 4 段**。本段覆盖源文件 L2373–L2804。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`20544`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 4, "parts": 4, "encoding": "utf-8", "sha256": "b23845f2d0421e9b078546869bedf2a843df8876bcb938bbe04254263fd95057"} -->
````python
# workbench/requirement_coverage.py
    def gap(message, code, *, targets=(), attribute=None, expected=None, actual=None):
        gaps.append(message)
        if diagnostics is not None:
            diagnostics.append(
                {
                    "code": code,
                    "source": dict(source),
                    "targets": [
                        {"entity": entity, "field": field.name}
                        for entity, field in fields
                        if any(field is target for target in targets)
                    ],
                    "attribute": attribute,
                    "expected": expected,
                    "actual": actual,
                    "source_markers": [
                        code
                        for code, pattern in (
                            ("search", r"搜索|检索|search"),
                            ("filter", r"筛选|过滤|filter"),
                            ("metric", _METRIC_CONTEXT.pattern),
                            ("date_range", r"日期区间|日期范围|date.?range"),
                            ("capability_catalog", r"可用能力|模板能力|template_capabilities"),
                            ("negation", r"无需|不需要|不要求|取消|禁用|不支持|false"),
                        )
                        if re.search(pattern, source_text, re.I)
                    ],
                }
            )

    if plan.data_scope != requirement.data_scope:
        gap(
            "设计改变了已批准的数据归属，必须修改后重新批准",
            "data_scope",
            expected=requirement.data_scope,
            actual=plan.data_scope,
        )
    for index, obligation in enumerate(requirement.field_requirements):
        source = {"section": "field_requirements", "index": index}
        matches = [
            f
            for e, f in fields
            if f.name == obligation.field and (obligation.entity is None or e == obligation.entity)
        ]
        label = f"{obligation.entity + '.' if obligation.entity else ''}{obligation.field}"
        if len(matches) != 1:
            gap(f"已确认字段 {label} 缺失或映射不唯一", "missing_or_ambiguous", targets=matches)
            continue
        field = matches[0]
        for key, value in obligation.model_dump().items():
            if key in {"field", "entity"} or value is None:
                continue
            actual = getattr(field, key)
            matches_constraint = _field_constraint_matches(field, key, value)
            if key in {"searchable", "filterable", "date_range"} and type(value) is bool:
                typed_queries[(id(field), key, value)] = matches_constraint
            if not matches_constraint:
                gap(
                    f"已确认字段 {label}.{key}={value!r}，设计为 {actual!r}",
                    "constraint_mismatch",
                    targets=[field],
                    attribute=key,
                    expected=value,
                    actual=actual,
                )

    # Recognize legacy constraints even when a model has omitted the new typed
    # ledger. Do not inspect assumptions/limitations as if they were requirements.
    texts = [
        ({"section": section, "index": index}, text)
        for section in ("features", "acceptance")
        for index, text in enumerate(getattr(requirement, section))
    ]
    structured = list(_fact_constraints(requirement.facts, fields))
    for index, (key, attributes, subject) in enumerate(structured):
        source = {"section": "facts", "index": index, "encoding": "structured", "path": key}
        source_text = key
        entity_name, field_name = subject
        identity = f"{entity_name + '.' if entity_name else ''}{field_name}"
        candidates = [
            field
            for entity, field in fields
            if field.name == field_name and (entity_name is None or entity == entity_name)
        ]
        if not candidates:
            gap(f"已确认条件缺少对应字段 {identity}（来源 {key}）", "structured_missing_field")
        elif len(candidates) > 1:
            gap(
                f"已确认字段 {identity} 映射不唯一（来源 {key}）",
                "missing_or_ambiguous",
                targets=candidates,
            )
            continue
        for field in candidates:
            for attribute, expected in attributes.items():
                if expected is None:
                    continue
                if (
                    attribute == "choices" and field.kind != "enum"
                ) or not _field_constraint_matches(field, attribute, expected):
                    gap(
                        f"已确认字段 {field.name}.{attribute}={expected!r}，设计不一致",
                        "constraint_mismatch",
                        targets=[field],
                        attribute=attribute,
                        expected=expected,
                        actual=getattr(field, attribute),
                    )
    texts.extend(
        ({"section": "facts", "index": index, "encoding": "legacy", "path": path}, text)
        for index, (path, text) in enumerate(_fact_texts(requirement.facts, fields))
    )
    affirmative_texts = []
    for origin, text in texts:
        affirmative, exclusions = _legacy_field_exclusions(text, fields)
        affirmative_texts.append((origin, affirmative))
        for index, (owner, name) in enumerate(_legacy_declared_fields(affirmative, fields)):
            source = {**origin, "declaration": index}
            source_text = text
            aliases = next((values for values in ALIASES.values() if name in values), (name,))
            if not any(
                (owner is None or entity == owner) and field.name in aliases
                for entity, field in fields
            ):
                label = f"{owner + '.' if owner else ''}{name}"
                gap(f"已确认条件缺少对应字段 {label}: {text}", "legacy_missing_field")
        for index, (owner, aliases, field_name) in enumerate(exclusions):
            source = {**origin, "exclusion_clause": index}
            source_text = text
            forbidden = [
                field
                for entity, field in fields
                if (owner is None or owner == entity) and field.name in aliases
            ]
            if forbidden:
                gap(
                    f"设计包含已禁止的字段 {owner + '.' if owner else ''}{field_name}: {text}",
                    "forbidden_field",
                    targets=forbidden,
                    attribute="present",
                    expected=False,
                    actual=True,
                )
    texts = affirmative_texts
    for origin, text in texts:
        for index, (clause, targets, field_bound) in enumerate(
            _legacy_date_obligations(text, fields)
        ):
            source = {**origin, "date_clause": index}
            source_text = clause
            missing = [field for field in targets if field.kind != "date"]
            if (
                (not targets or missing)
                if field_bound
                else not any(field.kind == "date" for field in targets)
            ):
                gap(
                    f"设计未覆盖真实日期类型: {clause}",
                    "date_kind",
                    targets=missing if field_bound else targets,
                    attribute="kind",
                    expected="date",
                )
    operations = {
        "searchable": r"搜索|检索|search",
        "filterable": r"筛选|过滤|filter",
        "date_range": r"日期区间|日期范围|含边界.*(?:日期|范围)|date.?range",
    }
    query_texts = []
    for origin, text in texts:
        query_text, metric_obligations = _metric_clauses(text, fields)
        query_texts.append((origin, _query_predicate_text(query_text, fields)))
        for index, obligation in enumerate(metric_obligations):
            source = {**origin, "metric_clause": index}
            source_text = text
            targets = obligation["targets"]
            predicates = obligation["predicates"]
            entities = {
                entity for entity, field in fields if any(field is target for target in targets)
            }
            explicit = {item["entity"] for item in predicates if item["entity"]}
            if obligation["entity"]:
                explicit.add(obligation["entity"])
            candidates = plan.business.metrics if plan.business else []
            candidates = [
                metric
                for metric in candidates
                if (not explicit or explicit == {metric.entity})
                and (not entities or metric.entity in entities)
                and (obligation["kind"] is None or metric.kind == obligation["kind"])
            ]
            if not any(
                all(
                    any(
                        predicate.field == requested["field"]
                        and predicate.op == requested["op"]
                        and type(predicate.value) is type(requested["value"])
                        and predicate.value == requested["value"]
                        for predicate in metric.filters
                    )
                    for requested in predicates
                )
                and (
                    bool(predicates)
                    or all(
                        any(predicate.field == target.name for predicate in metric.filters)
                        for target in targets
                    )
                )
                for metric in candidates
            ):
                gap(
                    "业务指标缺少已确认的筛选条件: " + text,
                    "missing_metric_predicate",
                    targets=targets,
                    attribute="metric_filter",
                    expected=True,
                    actual=False,
                )
    texts = query_texts
    # A field-bound false assignment or prohibition is a real constraint.
    # Extract it before discarding merely unrequested operation phrases; a
    # typed ledger is helpful but is not required to preserve explicit intent.
    for origin, text in texts:
        for index, clause in enumerate(_legacy_clauses(_legacy_boolean_text(text, fields), fields)):
            source = {**origin, "clause": index}
            source_text = clause
            targets = _legacy_targets(clause, fields)
            constraints = [
                (match.group(1).lower(), match.group(2).lower() in {"true", "是"})
                for match in re.finditer(
                    r"(?<![a-z_])(searchable|filterable|date_range)\s*[:=]\s*(true|false|是|否)(?![a-z])",
                    clause,
                    re.I,
                )
            ]
            constraints.extend(
                (flag, False)
                for flag, pattern in operations.items()
                if re.search(
                    r"(?:禁止|禁用|关闭|不得|不允许)\s*(?:关键词|关键字|精确)?\s*(?:"
                    + pattern
                    + ")",
                    clause,
                    re.I,
                )
            )
            for attribute, expected in constraints:
                for field in targets:
                    actual = getattr(field, attribute)
                    if not query_matches(field, attribute, expected):
                        gap(
                            f"已确认字段 {field.name}.{attribute}={expected!r}，设计不一致: {clause}",
                            "constraint_mismatch",
                            targets=[field],
                            attribute=attribute,
                            expected=expected,
                            actual=actual,
                        )
    texts = [
        ({**origin, "clause": index}, clause)
        for origin, text in texts
        for index, clause in enumerate(
            _legacy_clauses(_legacy_operation_text(text, fields), fields)
        )
    ]
    for source, text in texts:
        source_text = text
        known_subjects = _fact_candidates(text, fields)
        mentioned = _legacy_targets(text, fields)
        entity_scope = _fact_entity(text, fields)
        declarations = _legacy_declared_fields(text, fields)
        for owner, name in declarations:
            if not any(name in aliases for aliases in ALIASES.values()) and not any(
                (owner is None or entity == owner) and field.name == name
                for entity, field in fields
            ):
                label = f"{owner + '.' if owner else ''}{name}"
                gap(f"已确认条件缺少对应字段 {label}: {text}", "legacy_missing_field")
        if entity_scope and list(_legacy_scalar_constraints(text)):
            # A known field on another entity cannot satisfy this subject.
            # Vocabulary comes from declared fields, never grammatical words
            # such as 'not required' or descriptor attribute names.
            names = {field.name for _, field in fields}
            names.update(item.field for item in requirement.field_requirements)
            names.update(
                name for entity in requirement.entity_requirements for name in entity.fields
            )
            for name in sorted(name for name in names if _field_mentions(text, [name])):
                if not any(name in aliases for aliases in ALIASES.values()) and not any(
                    owner == entity_scope and field.name == name for owner, field in fields
                ):
                    gap(
                        f"已确认条件缺少对应字段 {entity_scope}.{name}: {text}",
                        "legacy_missing_field",
                    )
        for canonical, aliases in ALIASES.items():
            # Date type/format predicates are not identifiers named "date".
            # Their independently scoped obligations were checked above.
            if canonical == "published_on" and (
                _DATE_TYPE.search(text) or _DATE_FORMAT.search(text)
            ):
                continue
            if canonical == "published_on":
                spans = [match.span() for match in _DATE_RANGE_OPERATOR.finditer(text)]
                subjects = [
                    match
                    for alias in aliases
                    for match in re.finditer(
                        rf"(?<![a-z0-9_]){re.escape(alias)}(?![a-z0-9_])"
                        if alias.isascii()
                        else re.escape(alias),
                        text,
                        re.I,
                    )
                    if not any(
                        start <= match.start() and match.end() <= end for start, end in spans
                    )
                ]
                if spans and not subjects:
                    continue  # A query operator's name is not an extra field declaration.
            if _field_mentions(text, aliases):
                matches = [f for f in known_subjects if f.name in aliases]
                # Generic words such as 内容/分类 in a business summary are
                # not declarations of a missing field. An explicit identifier
                # with its description (detail/内容) binds the real field.
                explicit = any(_field_mentions(text, [name]) for name in aliases if name.isascii())
                description = any(
                    re.search(rf"{re.escape(field.name)}\s*[(（/]\s*{re.escape(alias)}", text, re.I)
                    for field in mentioned
                    for alias in aliases
                )
                if (
                    not matches
                    and not description
                    # An identifier mention is not an existence predicate.
                    # Keep direct scalar/query declarations and explicit schema
                    # declarations; descriptive/negative bare prose adds none.
                    and (
                        bool(declarations)
                        or bool(list(_legacy_scalar_constraints(text)))
                        or any(re.search(pattern, text, re.I) for pattern in operations.values())
                    )
                    and (explicit or re.search(LEGACY_PROPERTY, text, re.I))
                ):
                    gap(f"已确认条件缺少对应字段 {canonical}: {text}", "legacy_missing_field")
        operation_parts = [text]
        if re.search(operations["searchable"], text, re.I) and re.search(
            operations["filterable"], text, re.I
        ):
            operation_parts = list(_query_operation_groups(text, fields, operations))
        previous_targets = []
        for part in operation_parts:
            entity_scope = _fact_entity(part, fields) or _fact_entity(text, fields)
            bound = part
            if part != text and _fact_entity(part, fields) is None:
                if entity_scope:
                    bound = f"{entity_scope}::{part}"
                elif _ALL_ENTITIES.search(text):
                    bound = f"所有实体 {part}"
            targets = _legacy_targets(bound, fields) if part != text else mentioned
            ambiguous_subject = not targets and bool(_fact_candidates(bound, fields))
            # An operation-only continuation (标题搜索和精确筛选) inherits
            # the previous named subject; another field cannot satisfy it.
            if (
                not targets
                and not ambiguous_subject
                and previous_targets
                # A named generic keyword search is its own capability, not
                # a search obligation on the preceding exact-filter field.
                and not re.search(r"关键词|关键字|keyword", part, re.I)
            ):
                targets = previous_targets
            if targets:
                previous_targets = targets
            available = [
                f for entity, f in fields if entity_scope is None or entity == entity_scope
            ]
            for flag, pattern in operations.items():
                if not re.search(pattern, part, re.I):
                    continue
                if ambiguous_subject:
                    continue
                candidates = targets
                if flag == "date_range":
                    candidates = [f for f in targets if f.kind == "date"] or [
                        f for f in available if f.kind == "date"
                    ]
                if not targets:
                    candidates = available
                    if not any(query_matches(f, flag, True) for f in candidates):
                        gap(
                            f"设计未覆盖已确认的 {flag}: {part}",
                            "uncovered_operation",
                            targets=candidates,
                            attribute=flag,
                            expected=True,
                            actual=False,
                        )
                elif not candidates or any(not query_matches(f, flag, True) for f in candidates):
                    gap(
                        f"设计未覆盖已确认的 {flag}: {part}",
                        "uncovered_operation",
                        targets=candidates,
                        attribute=flag,
                        expected=True,
                        actual=False,
                    )
        for field in mentioned:
            for attribute, expected in _legacy_scalar_constraints(text):
                if (
                    attribute in {"minimum", "maximum", "exclusive_minimum", "exclusive_maximum"}
                    and field.kind != "integer"
                ):
                    continue
                actual = getattr(field, attribute)
                if _field_constraint_matches(field, attribute, expected):
                    continue
                description = (
                    ("必填" if expected else "可选")
                    if attribute == "required"
                    else attribute + "=" + str(expected)
                )
                gap(
                    f"已确认字段 {field.name} {description}: {text}",
                    "constraint_mismatch",
                    targets=[field],
                    attribute=attribute,
                    expected=expected,
                    actual=actual,
                )
    return list(dict.fromkeys(gaps))
````
