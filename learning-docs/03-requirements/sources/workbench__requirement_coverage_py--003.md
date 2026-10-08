# workbench/requirement_coverage.py · 3/4

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__requirement_coverage_py--002.md) · [下一段](workbench__requirement_coverage_py--004.md)

**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`、`workbench.requirement_canonical`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_metric_clauses`（L1796–L1912）：接收`text`、`fields`。 源码说明：Separate aggregate predicates from field-query declarations. Only a recognized metric clause with named filter operands or permission scope is consumed. Explicit UI/query flags always remain field obl。 控制顺序：L1901遍历`_top_level_parts(text, r"[、，,；;。\n]\|并且\|并\|且\|和\|与\|\band\b")`；L1902按`_METRIC_CONTEXT.search(part)`分支；L1909按`_QUERY_SURFACE.search(part) or re.fullmatch(r"[；;。\n]", separator)`分支。 调用`re.sub`、`_top_level_parts`、`_METRIC_CONTEXT.search`、`result.append`、`consume`、`_QUERY_SURFACE.search`、`re.fullmatch`、`"".join`。 返回路径：L1912的`"".join(result), obligations`。
- `_metric_clauses.consume`（L1806–L1885）：接收`fragment`、`context`、`inherited`。 控制顺序：L1809按`not _METRIC_CONTEXT.search(combined) or _QUERY_SURFACE.search(fragment)`分支；L1814遍历`matches`；L1816按`name in {"group_by", "start_field", "end_field", "time_field", "kind", "scope"}`分支；L1829按`not quoted and ( value.lower() == "null" or (target is not None and target.kind in {"…`分支；L1847按`not _METRIC_FILTER.search(_legacy_operation_text(fragment, fields)) and not ( inherit…`分支；L1854按`inherited and not predicates and not scope_only`分支；L1861按`not targets and not predicates and not scope_only`分支；L1863按`not scope_only`分支。后续分支沿下方源码相同行号继续阅读。 调用`_METRIC_CONTEXT.search`、`_QUERY_SURFACE.search`、`list`、`_METRIC_PREDICATE.finditer`、`_metric_entity`、`match.group`、`literal.startswith`、`literal.strip`、`next`等。 返回路径：L1810的`fragment`；L1850的`fragment`；L1855的`fragment`。
- `_metric_clauses.parenthesis`（L1889–L1896）：接收`match`。 调用`match.start`、`re.split`、`match.group`、`consume`。 返回路径：L1896的`match.group() if filtered == body else ""`。
- `_negative_operation_pattern`（L1915–L1940）：接收`fields`。 调用`names.update`、`ALIASES.values`、`"\|".join`、`re.escape`、`sorted`、`re.compile`。 返回路径：L1932的`re.compile( negative + r"\s*(?:任何\|额外的?\|新的?)?\s*" + targets + r"(?:" + operation + r")" r…`。
- `_legacy_boolean_text`（L1943–L1971）：接收`text`、`fields`。 源码说明：Lower explicit negative capability lists before field-clause splitting. 不可/不支持/不提供/不参与 describe disabled behavior; 无需/不要求 merely decline a requirement. Coordination ends before a new field or a positi。 调用`_negative_operation_pattern(fields).sub`、`_negative_operation_pattern`。 返回路径：L1971的`_negative_operation_pattern(fields).sub(replace, text)`。
- `_legacy_boolean_text.replace`（L1950–L1969）：接收`match`。 控制顺序：L1952按`not re.match( r"禁止\|禁用\|关闭\|不得\|不允许\|不可(?:以)?\|不支持\|不提供\|不参与\|" r"\b(?:never\|cannot\…`分支；L1961按`re.search(r"搜索\|检索\|search", phrase, re.I)`分支；L1965按`re.search(r"筛选\|过滤\|filter", exact, re.I)`分支；L1967按`re.search(r"日期区间\|日期范围\|date.?range", phrase, re.I)`分支。 调用`match.group`、`re.match`、`re.search`、`attributes.append`、`_DATE_RANGE_QUERY.sub`、`" ".join`。 返回路径：L1959的`""`；L1969的`" " + (match.group("targets") or "") + " " + " ".join(attributes) + " "`。
- `_legacy_operation_text`（L1974–L1986）：接收`text`、`fields`。 源码说明：Remove checked negatives without merging their subjects into the next clause. An empty descriptor preserves the field boundary, while keeping coordinated negated date-range terms out of the positive f。 调用`re.sub`、`_negative_operation_pattern(fields).sub`、`_negative_operation_pattern`。 返回路径：L1986的`_negative_operation_pattern(fields).sub("（）", text)`。
- `_legacy_field_exclusions`（L1989–L2075）：接收`text`、`fields`。 源码说明：Separate absence of fields from nullable fields or disabled operations. Only explicit absence/removal predicates bind exclusions. In particular, 'not required', 'not null' and 'do not filter' are not 。 控制顺序：L2036遍历`sentences`；L2038按`heading`分支。 调用`names.update`、`ALIASES.values`、`"\|".join`、`re.escape`、`sorted`、`name.isascii`、`re.compile`、`_fact_entity`、`_top_level_parts`等。 返回路径：L2075的`"".join(output), obligations`。
- `_legacy_field_exclusions.replace`（L2041–L2070）：接收`match`。 控制顺序：L2050按`query_location or re.search( r"搜索\|检索\|筛选\|过滤\|显示\|展示\|界面\|列表\|\b(?:search\|filter\|d…`分支；L2058遍历`re.split(separator_pattern, identities, flags=re.I)`。 调用`re.split`、`match.start`、`re.match`、`match.end`、`re.search`、`match.group`、`identity.strip`、`re.fullmatch`、`qualified.group`等。 返回路径：L2055的`match.group()`；L2070的`match.group()[:start] + " " * (end - start) + match.group()[end:]`。
- `_legacy_date_obligations`（L2110–L2191）：接收`text`、`fields`。 源码说明：Interpret field types, not every mention of a date-shaped string. Read original source clauses before query lowering discards negations or headings. A format alone is presentation metadata; it becomes。 控制顺序：L2120遍历`re.split(r"[；;。\n]\|但是\|但\|不过\|\bbut\b", text, flags=re.I)`；L2121按`not sentence.strip()`分支；L2129遍历`_legacy_clauses(sentence, fields)`；L2132按`not markers and not formats`分支；L2149遍历`[*markers, *formats]`；L2153按`_DATE_NEGATIVE.search(local_prefix) or re.match( r"\s*(?:字段\|类型\|校验\|验证)?\s*(?:无需\|不需…`分支；L2159按`context or _DATE_CONTEXT.search(local_prefix)`分支；L2161按`marker in formats and ( not concrete or not _DATE_INPUT.search(clause) or _DATE_PRESE…`分支。后续分支沿下方源码相同行号继续阅读。 调用`_fact_entity`、`re.split`、`sentence.strip`、`re.match`、`bool`、`_DATE_CONTEXT.search`、`headings.group`、`re.search`、`_legacy_clauses`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_normalized_constraint_value`（L2194–L2214）：接收`attribute`、`expected`。 控制顺序：L2195按`attribute in {"required", "searchable", "filterable", "date_range"}`分支；L2196按`isinstance(expected, str)`分支；L2198按`word in {"true", "是", "必填"}`分支；L2200按`word in {"false", "否", "可选", "非必填"}`分支；L2202按`attribute in { "min_length", "max_length", "minimum", "maximum", "exclusive_minimum",…`分支；L2210按`isinstance(expected, str)`分支；L2212按`legacy`分支。 调用`isinstance`、`expected.strip().lower`、`expected.strip`、`re.fullmatch`、`int`、`legacy.group`。 返回路径：L2214的`expected`。
- `_matches_constraint`（L2217–L2236）：接收`attribute`、`expected`、`actual`。 控制顺序：L2219按`attribute in {"required", "searchable", "filterable", "date_range"}`分支；L2221按`attribute in { "min_length", "max_length", "minimum", "maximum", "exclusive_minimum",…`分支；L2230按`attribute == "choices"`分支。 调用`_normalized_constraint_value`、`type`、`isinstance`、`all`、`set`。 返回路径：L2220的`type(expected) is bool and actual is expected`；L2229的`type(expected) is int and actual == expected`；L2231的`isinstance(expected, list) and all(isinstance(item, str) for item in expected) and set(act…`。
- `_field_constraint_matches`（L2239–L2252）：接收`field`、`attribute`、`expected`。 控制顺序：L2240按`attribute in {"minimum", "maximum", "exclusive_minimum", "exclusive_maximum"}`分支；L2243按`field.kind != "integer" or type(expected) is not int`分支。 调用`type`、`integer_bounds`、`field.model_dump`、`_matches_constraint`、`getattr`。 返回路径：L2244的`False`；L2246的`{ "minimum": low == expected, "maximum": high == expected, "exclusive_minimum": low == exp…`；L2252的`_matches_constraint(attribute, expected, getattr(field, attribute))`。
- `_legacy_scalar_constraints`（L2255–L2278）：接收`text`。 源码说明：Shared scalar predicate extraction after entity/field subject binding.。 控制顺序：L2266按`not validation`分支；L2267按`re.search(r"必填\|required", text, re.I) and not optional`分支；L2269按`optional or re.search(r"可选", text)`分支；L2271遍历`( ("max_length", r"上限\|最大\|max_length\|最多\|最长"), ("min_length", r…`；L2276按`number`分支。 调用`bool`、`re.search`、`int`、`number.group`、`_legacy_integer_constraints`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_legacy_integer_constraints`（L2281–L2298）：接收`text`。 控制顺序：L2282按`not re.search( r"minimum\s*[:=]\|maximum\s*[:=]\|必须\|保存\|校验\|拒绝\|不得\|应当\|应满足", text, …`分支；L2288按`not re.search(r"筛选\|过滤\|统计\|查询\|filter\|query\|metric", text, re.I) or re.search( r"保…`分支；L2291遍历`( ("minimum", r"(?<!exclusive_)minimum\s*[:=]\|>=\|≥\|大于等于\|不小于\|…`；L2297遍历`re.finditer(rf"(?:{pattern})\s*(-?\d+)(?![\d.])", text, re.I)`。 调用`re.search`、`re.finditer`、`int`、`match.group`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `explicit_legacy_field_constraints`（L2301–L2379）：接收`requirement`。 源码说明：Reliably bound scalar constraints using Requirement vocabulary only. This is a read-only projection for source-conflict detection, not a new requirements ledger or an excuse to discard unsupported tex。 控制顺序：L2315按`not fields`分支；L2327遍历`texts`；L2331遍历`enumerate( _legacy_clauses(_legacy_operation_text(text, fields), …`；L2334遍历`_legacy_targets(clause, fields)`；L2336遍历`_legacy_scalar_constraints(clause)`；L2347遍历`enumerate( _fact_constraints(requirement.facts, fields) )`；L2350按`subject not in vocabulary`分支；L2352遍历`( "required", "min_length", "max_length", "minimum", "maximum", "…`。后续分支沿下方源码相同行号继续阅读。 调用`SimpleNamespace`、`vocabulary.items`、`enumerate`、`getattr`、`texts.extend`、`_fact_texts`、`_legacy_field_exclusions`、`_metric_clauses`、`_query_predicate_text`等。 返回路径：L2316的`[]`；L2379的`result`。
- `_legacy_declared_fields`（L2382–L2452）：接收`text`、`fields`。 源码说明：Recognize explicit field declarations, never infer fields from bare prose. This is a compatibility guard, not a general-language parser. Typed ledgers remain independent. Only a schema heading/imperat。 控制顺序：L2392按`heading`分支；L2394按`owner`分支；L2397按`match`分支；L2416按`declaration`分支；L2418按`body[:1] in "（([【"`分支；L2427按`not descriptor`分支；L2431遍历`_top_level_parts(body, separators)`；L2433按`not subject`分支。后续分支沿下方源码相同行号继续阅读。 调用`_fact_entity`、`_entity_subject_heading`、`re.search`、`re.escape`、`match.end`、`ALIASES.values`、`name.isascii`、`"\|".join`、`re.match`等。 返回路径：L2428的`[]`；L2452的`result`。
- `coverage_gaps`（L2455–L2915）：接收`requirement`、`plan`、`diagnostics`、`native_normalization`。 源码说明：Return blocking messages; optionally record the exact deterministic provenance. Diagnostic source indices refer to the retained Requirement, never a model verdict. Consumers exporting diagnostics must。 控制顺序：L2463按`native_normalization`分支；L2511按`plan.data_scope != requirement.data_scope`分支；L2518遍历`enumerate(requirement.field_requirements)`；L2526按`len(matches) != 1`分支；L2530遍历`obligation.model_dump().items()`；L2531按`key in {"field", "entity"} or value is None`分支；L2535按`key in {"searchable", "filterable", "date_range"} and type(value) is bool`分支；L2537按`not matches_constraint`分支。后续分支沿下方源码相同行号继续阅读。 调用`source_plan`、`entity_gaps`、`gap`、`enumerate`、`len`、`obligation.model_dump().items`、`obligation.model_dump`、`getattr`、`_field_constraint_matches`等。 返回路径：L2915的`list(dict.fromkeys(gaps))`。
- `coverage_gaps.query_matches`（L2473–L2479）：接收`field`、`attribute`、`expected`。 控制顺序：L2475按`key in typed_queries`分支。 调用`id`、`getattr`。 返回路径：L2476的`typed_queries[key]`；L2479的`getattr(field, attribute) is expected`。

</details>

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 4 段**。本段覆盖源文件 L1796–L2480。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`30046`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 3, "parts": 4, "encoding": "utf-8", "sha256": "e8f763da98b56b141795e675c32163f3d7a38083122d6cab677fadc4695c3f43"} -->
````python
# workbench/requirement_coverage.py
def _metric_clauses(text, fields):
    """Separate aggregate predicates from field-query declarations.

    Only a recognized metric clause with named filter operands or permission
    scope is consumed. Explicit UI/query flags always remain field obligations.
    The caller checks consumed predicates against executable MetricSpec.filters.
    """
    obligations = []
    active = None

    def consume(fragment, context="", inherited=False):
        nonlocal active
        combined = context + fragment
        if not _METRIC_CONTEXT.search(combined) or _QUERY_SURFACE.search(fragment):
            return fragment
        matches = list(_METRIC_PREDICATE.finditer(fragment))
        entity = _metric_entity(fragment, fields) or _metric_entity(context, fields)
        predicates = []
        for match in matches:
            name = match.group("field")
            if name in {"group_by", "start_field", "end_field", "time_field", "kind", "scope"}:
                continue
            literal = match.group("value")
            quoted = literal.startswith(('"', "'"))
            value = literal.strip("\"'")
            target = next(
                (
                    field
                    for owner, field in fields
                    if field.name == name and (entity is None or owner == entity)
                ),
                None,
            )
            if not quoted and (
                value.lower() == "null"
                or (target is not None and target.kind in {"integer", "boolean"})
            ):
                try:
                    value = json.loads(value.lower())
                except ValueError:
                    pass
            predicates.append(
                {
                    "entity": match.group("entity"),
                    "field": name,
                    "op": {"=": "eq", "==": "eq", "!=": "ne", ">=": "gte", "<=": "lte"}[
                        match.group("op")
                    ],
                    "value": value,
                }
            )
        if not _METRIC_FILTER.search(_legacy_operation_text(fragment, fields)) and not (
            inherited and active is not None and predicates
        ):
            return fragment
        scope_only = not predicates and bool(_METRIC_SCOPE.search(fragment))
        # A metric heading may scope a following predicate, never an unrelated
        # bare field-filter declaration after a comma or conjunction.
        if inherited and not predicates and not scope_only:
            return fragment
        targets = (
            [field for _, field in fields if any(p["field"] == field.name for p in predicates)]
            if predicates
            else _fact_candidates(fragment, fields)
        )
        if not targets and not predicates and not scope_only:
            return fragment
        if not scope_only:
            kinds = list(_METRIC_KIND.finditer(combined))
            kind = kinds[-1].group().lower() if kinds else None
            kind = {
                "已解决数": "count",
                "总数": "count",
                "趋势": "time_count",
                "分组": "group_count",
            }.get(kind, "average_duration" if kind and "时长" in kind else kind)
            if inherited and active is not None and entity == active["entity"]:
                active["predicates"].extend(predicates)
                active["targets"].extend(
                    target for target in targets if all(target is not t for t in active["targets"])
                )
            else:
                active = {
                    "kind": kind,
                    "entity": entity,
                    "predicates": predicates,
                    "targets": targets,
                }
                obligations.append(active)
        return ""

    # Parenthesized metric definitions have their own scope, even alongside a
    # list-filter requirement in the same sentence.
    def parenthesis(match):
        nonlocal active
        active = None
        prefix = text[: match.start()]
        label = re.split(r"[，,、；;。\n]", prefix)[-1]
        body = match.group(1)
        filtered = consume(body, label)
        return match.group() if filtered == body else ""

    text = re.sub(r"[（(]([^（）()]*)[）)]", parenthesis, text)
    result, context = [], ""
    active = None
    for part, separator in _top_level_parts(text, r"[、，,；;。\n]|并且|并|且|和|与|\band\b"):
        if _METRIC_CONTEXT.search(part):
            context = part
            active = None
            result.append(consume(part))
        else:
            result.append(consume(part, context, inherited=True))
        result.append(separator)
        if _QUERY_SURFACE.search(part) or re.fullmatch(r"[；;。\n]", separator):
            context = ""
            active = None
    return "".join(result), obligations


def _negative_operation_pattern(fields):
    negative = (
        r"(?:无需|不需要|不要求|取消|禁止|禁用|关闭|不得|不允许|不可(?:以)?|不支持|不添加|不提供|不参与|不要|没有|无|不|"
        r"\b(?:no|without|never|cannot|disable|forbid|(?:(?:do|does|must|should)\s+)?not"
        r"(?:\s+(?:require|need|allow|support|provide|enable|use))?)\b)"
    )
    operation = (
        r"(?:(?:关键词|关键字|精确)\s*)?(?:搜索|检索|筛选|过滤)"
        r"|(?:日期区间|日期范围)(?:筛选|过滤|查询)?"
        r"|(?:keyword\s+)?search(?:ing|able|es)?|(?:exact\s+)?filter(?:ing|s|able)?|date.?range"
    )
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    name = (
        "(?:" + "|".join(re.escape(value) for value in sorted(names, key=len, reverse=True)) + ")"
    )
    targets = "(?P<targets>" + name + r"(?:\s*[、和与]\s*" + name + r")*(?:的)?\s*)?"
    return re.compile(
        negative + r"\s*(?:任何|额外的?|新的?)?\s*" + targets + r"(?:" + operation + r")"
        r"(?:\s*(?:以及|[、或和及与]|\band\b|\bor\b)\s*(?:"
        + negative
        + r")?\s*(?:"
        + operation
        + r"))*",
        re.I,
    )


def _legacy_boolean_text(text, fields):
    """Lower explicit negative capability lists before field-clause splitting.

    不可/不支持/不提供/不参与 describe disabled behavior; 无需/不要求 merely
    decline a requirement. Coordination ends before a new field or a positive predicate.
    """

    def replace(match):
        phrase = match.group()
        if not re.match(
            r"禁止|禁用|关闭|不得|不允许|不可(?:以)?|不支持|不提供|不参与|"
            r"\b(?:never|cannot|disable|forbid|(?:(?:do|does|must|should)\s+)?not"
            r"(?!\s+(?:require|need)\b))\b",
            phrase,
            re.I,
        ):
            return ""
        attributes = []
        if re.search(r"搜索|检索|search", phrase, re.I):
            attributes.append("searchable=false")
        # A date-range operation is not a separate exact-filter toggle.
        exact = _DATE_RANGE_QUERY.sub("", phrase)
        if re.search(r"筛选|过滤|filter", exact, re.I):
            attributes.append("filterable=false")
        if re.search(r"日期区间|日期范围|date.?range", phrase, re.I):
            attributes.append("date_range=false")
        return " " + (match.group("targets") or "") + " " + " ".join(attributes) + " "

    return _negative_operation_pattern(fields).sub(replace, text)


def _legacy_operation_text(text, fields):
    """Remove checked negatives without merging their subjects into the next clause.

    An empty descriptor preserves the field boundary, while keeping coordinated
    negated date-range terms out of the positive field-alias parser.
    """
    text = re.sub(
        r"(?:searchable|filterable|date_range)\s*[:=]\s*(?:false|否)(?![a-z])",
        "（）",
        text,
        flags=re.I,
    )
    return _negative_operation_pattern(fields).sub("（）", text)


def _legacy_field_exclusions(text, fields):
    """Separate absence of fields from nullable fields or disabled operations.

    Only explicit absence/removal predicates bind exclusions. In particular,
    'not required', 'not null' and 'do not filter' are not absence predicates.
    Mask just the excluded subjects so adjacent positive clauses survive. Keep
    the absence predicate for any trailing type description, e.g. 'date field'.
    """
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    name = (
        r"(?:[a-z][a-z0-9_]*|"
        + "|".join(
            re.escape(name) for name in sorted(names, key=len, reverse=True) if not name.isascii()
        )
        + ")"
    )
    subject = rf"(?<![a-z0-9_])(?:[a-z][a-z0-9_]*(?:::|\.))?{name}(?![a-z0-9_])"
    separator_pattern = r"[、/]|或|和|与|以及|\band\b|\bor\b"
    bare_subject = rf"{subject}(?!\s*(?:{LEGACY_PROPERTY}|\b(?:is|are|must|should|not)\b))"
    targets = rf"{bare_subject}(?:\s*(?:{separator_pattern})\s*{bare_subject})*"
    suffix_targets = rf"{subject}(?:\s*(?:{separator_pattern})\s*{subject})*"
    absence = (
        r"不出现|(?:不应|不得|不允许|不能)\s*(?:出现|存在|包含|含有|添加|引入|保留)|"
        r"禁止\s*(?:出现|存在|添加|引入|保留)|不包含|不含有|"
        r"\b(?:must|should)\s+not\s+(?:include|contain|have|add|retain)|"
        r"\b(?:do|does)\s+not\s+(?:include|contain|add|retain)|\bexclude|"
        rf"禁止(?=\s*{subject}\s*字段(?!\s*(?:{LEGACY_PROPERTY})))"
    )
    prefix = re.compile(
        rf"(?:{absence})\s*(?:(?:字段|fields?)\s*[：:]?\s*)?(?P<targets>{targets})", re.I
    )
    suffix = re.compile(
        rf"(?P<targets>{suffix_targets})\s*(?:字段|fields?)?\s*"
        r"(?:不得|不应|不能|不允许)\s*(?:出现|存在|被添加|被引入)|"
        rf"(?P<english>{suffix_targets})\s+(?:fields?\s+)?"
        r"(?:must|should)\s+not\s+(?:exist|appear|be\s+(?:included|added|present))\b",
        re.I,
    )
    initial_scope = _fact_entity(text, fields)
    obligations, output = [], []
    scopes = (initial_scope,) if initial_scope else ()
    sentences = (
        (part, inner_separator or separator)
        for sentence, separator in _top_level_parts(text, r"[；;。\n]|但是|但|不过|\bbut\b")
        for part, inner_separator in _explicit_entity_sections(sentence, fields)
    )
    for sentence, separator in sentences:
        heading = _entity_subject_heading(sentence, fields)
        if heading:
            scopes, _ = heading

        def replace(match):
            local_prefix = re.split(r"[，,]|并且|并|且|\band\b", sentence[: match.start()])[-1]
            query_location = re.match(
                r"\s*(?:在|于|\b(?:in|on|from|within|as)\s+(?:the\s+)?)\s*"
                r"(?:搜索|检索|筛选|过滤|显示|展示|界面|列表|表格|页面|"
                r"\b(?:search|filters?|filtering|display(?:ed)?|ui|lists?|tables?|forms?|views?)\b)",
                sentence[match.end() :],
                re.I,
            )
            if query_location or re.search(
                r"搜索|检索|筛选|过滤|显示|展示|界面|列表|\b(?:search|filter|display|ui|list)\b",
                local_prefix,
                re.I,
            ):
                return match.group()
            group = "targets" if match.group("targets") else "english"
            identities = match.group(group)
            for identity in re.split(separator_pattern, identities, flags=re.I):
                identity = identity.strip()
                qualified = re.fullmatch(r"([a-z][a-z0-9_]*)(?:::|\.)(.+)", identity, re.I)
                owners = (qualified.group(1),) if qualified else scopes or (None,)
                field_name = qualified.group(2) if qualified else identity
                aliases = next(
                    (aliases for aliases in ALIASES.values() if field_name in aliases),
                    (field_name,),
                )
                obligations.extend((owner, aliases, field_name) for owner in owners)
            start, end = match.span(group)
            start, end = start - match.start(), end - match.start()
            return match.group()[:start] + " " * (end - start) + match.group()[end:]

        sentence = prefix.sub(replace, sentence)
        sentence = suffix.sub(replace, sentence)
        output.append(sentence + separator)
    return "".join(output), obligations


_DATE_TYPE = re.compile(
    r"真实日期|\breal\s+date\b|(?:日期|\bdate\b)\s*(?:类型|字段|\b(?:type|field)\b)|"
    r"(?:类型|kind)\s*[:=为是]?\s*(?:日期|date\b)|"
    r"(?:必填|可选|为|使用|采用)\s*(?:日期|date\b)(?!格式|范围|区间|显示|展示)",
    re.I,
)
_DATE_FORMAT = re.compile(r"YYYY-MM-DD|日期格式|\bdate[_ ]format\b", re.I)
_DATE_RANGE_OPERATOR = re.compile(r"日期区间|日期范围|date.?range", re.I)
_DATE_RANGE_QUERY = re.compile(
    r"(?:\b(?:filter(?:ing)?|search(?:ing)?)\s+(?:by|using|on)\s+)?"
    rf"(?:{_DATE_RANGE_OPERATOR.pattern})"
    r"(?:\s*(?:筛选|过滤|查询)|\s+(?:filters?|filtering|search(?:ing)?|quer(?:y|ies))\b)?",
    re.I,
)
_DATE_INPUT = re.compile(r"输入|录入|校验|验证|拒绝保存|\b(?:input|validate|validation)\b", re.I)
_DATE_NEGATIVE = re.compile(
    r"无需|不需要|不要求|不使用|不采用|不添加|不提供|不要|没有|无|不是|并非|取消|禁止|"
    r"不出现|不应|不得|不允许|不能|不包含|不含有|"
    r"\b(?:no|not|never|without|do\s+not|does\s+not)\b",
    re.I,
)
_DATE_CONTEXT = re.compile(
    r"模板|可用能力|能力(?:清单|目录|示例)|示例|例如|举例|假设|如果|若|"
    r"\b(?:template(?:_capabilities)?|capabilities|catalog|example|e\.g\.|if)\b",
    re.I,
)
_DATE_PRESENTATION = re.compile(
    r"显示|展示|呈现|界面|默认|时间戳|datetime|timestamp|\b(?:display|render|default)\b",
    re.I,
)


def _legacy_date_obligations(text, fields):
    """Interpret field types, not every mention of a date-shaped string.

    Read original source clauses before query lowering discards negations or
    headings. A format alone is presentation metadata; it becomes a type
    obligation only when bound to a concrete field and used as its input
    contract. Explicit real-date declarations can still introduce a field.
    Typed field constraints are checked separately and never filtered here.
    """
    scope = _fact_entity(text, fields)
    for sentence in re.split(r"[；;。\n]|但是|但|不过|\bbut\b", text, flags=re.I):
        if not sentence.strip():
            continue
        # Keep catalog/example provenance that _legacy_clauses may otherwise
        # remove while normalizing section headings.
        headings = re.match(r"\s*(?:[^，,：:；;（）()]+[：:]\s*)+", sentence)
        context = bool(headings and _DATE_CONTEXT.search(headings.group())) or bool(
            re.search(r"假设|如果|若|\bif\b", sentence, re.I)
        )
        for clause in _legacy_clauses(sentence, fields):
            markers = list(_DATE_TYPE.finditer(clause))
            formats = list(_DATE_FORMAT.finditer(clause))
            if not markers and not formats:
                continue
            candidates = _legacy_targets(clause, fields)
            concrete = [
                field
                for field in candidates
                if _field_mentions(clause, [field.name])
                or any(
                    field.name in aliases and _field_mentions(clause, [alias])
                    for aliases in ALIASES.values()
                    for alias in aliases
                    if alias not in {"日期", "date"}
                )
            ]
            # Generic 日期 must not donate another entity's published_on to a
            # declaration naming a different field.
            targets = concrete or candidates
            for marker in [*markers, *formats]:
                prefix = clause[: marker.start()]
                local_prefix = re.split(r"[，,、]", prefix)[-1]
                suffix = clause[marker.end() :]
                if _DATE_NEGATIVE.search(local_prefix) or re.match(
                    r"\s*(?:字段|类型|校验|验证)?\s*(?:无需|不需要|不要求|取消)", suffix
                ):
                    continue
                # A later example/display instruction cannot erase an earlier
                # affirmative field-type declaration in this same clause.
                if context or _DATE_CONTEXT.search(local_prefix):
                    continue
                if marker in formats and (
                    not concrete
                    or not _DATE_INPUT.search(clause)
                    or _DATE_PRESENTATION.search(clause)
                ):
                    continue
                if marker in markers and _DATE_PRESENTATION.search(local_prefix):
                    # "默认真实日期格式" is a formatting default, while a
                    # field explicitly declared 真实日期 before display prose
                    # remains executable intent.
                    continue
                entity = _fact_entity(clause, fields) or scope
                qualified = bool(
                    re.search(r"(?<![a-z0-9_])[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*", clause)
                )
                if not targets and (_fact_candidates(clause, fields) or qualified):
                    # An ambiguous repeated subject cannot be satisfied by an
                    # unrelated date field in another entity.
                    yield clause, [], True
                elif not targets and not _field_mentions(
                    clause,
                    [alias for aliases in ALIASES.values() for alias in aliases if alias.isascii()],
                ):
                    yield (
                        clause,
                        [field for owner, field in fields if entity is None or owner == entity],
                        False,
                    )
                else:
                    yield clause, targets, True
                break


def _normalized_constraint_value(attribute, expected):
    if attribute in {"required", "searchable", "filterable", "date_range"}:
        if isinstance(expected, str):
            word = expected.strip().lower()
            if word in {"true", "是", "必填"}:
                expected = True
            elif word in {"false", "否", "可选", "非必填"}:
                expected = False
    if attribute in {
        "min_length",
        "max_length",
        "minimum",
        "maximum",
        "exclusive_minimum",
        "exclusive_maximum",
    }:
        if isinstance(expected, str):
            legacy = re.fullmatch(r"\s*(\d+)\s*(?:字符|字|characters?)?\s*", expected, re.I)
            if legacy:
                expected = int(legacy.group(1))
    return expected


def _matches_constraint(attribute, expected, actual):
    expected = _normalized_constraint_value(attribute, expected)
    if attribute in {"required", "searchable", "filterable", "date_range"}:
        return type(expected) is bool and actual is expected
    if attribute in {
        "min_length",
        "max_length",
        "minimum",
        "maximum",
        "exclusive_minimum",
        "exclusive_maximum",
    }:
        return type(expected) is int and actual == expected
    if attribute == "choices":
        return (
            isinstance(expected, list)
            and all(isinstance(item, str) for item in expected)
            and set(actual) == set(expected)
        )
    return type(expected) is str and actual == expected


def _field_constraint_matches(field, attribute, expected):
    if attribute in {"minimum", "maximum", "exclusive_minimum", "exclusive_maximum"}:
        from templates.product.fields import integer_bounds

        if field.kind != "integer" or type(expected) is not int:
            return False
        low, high = integer_bounds(field.model_dump())
        return {
            "minimum": low == expected,
            "maximum": high == expected,
            "exclusive_minimum": low == expected + 1,
            "exclusive_maximum": high == expected - 1,
        }[attribute]
    return _matches_constraint(attribute, expected, getattr(field, attribute))


def _legacy_scalar_constraints(text):
    """Shared scalar predicate extraction after entity/field subject binding."""
    validation = bool(
        re.search(r"必填(?:字段|项).*(?:缺失|为空)|(?:缺少|缺失)必填|必填.*可选.*校验", text)
    )
    optional = re.search(
        r"非必填|不必填|是否必填.*否|optional|\bnot\s+required\b|"
        r"required\s*[:=]\s*(?:false|否)",
        text,
        re.I,
    )
    if not validation:
        if re.search(r"必填|required", text, re.I) and not optional:
            yield "required", True
        if optional or re.search(r"可选", text):
            yield "required", False
    for attribute, pattern in (
        ("max_length", r"上限|最大|max_length|最多|最长"),
        ("min_length", r"最小|min_length|至少|最短"),
    ):
        number = re.search(rf"(?:{pattern})[^\d]*?(\d+)", text, re.I)
        if number:
            yield attribute, int(number.group(1))
    yield from _legacy_integer_constraints(text)


def _legacy_integer_constraints(text):
    if not re.search(
        r"minimum\s*[:=]|maximum\s*[:=]|必须|保存|校验|拒绝|不得|应当|应满足", text, re.I
    ):
        return
    # Numeric query thresholds select records; only save-time requirements
    # and explicit scalar declarations constrain the input domain.
    if not re.search(r"筛选|过滤|统计|查询|filter|query|metric", text, re.I) or re.search(
        r"保存|校验|拒绝|必须", text
    ):
        for attribute, pattern in (
            ("minimum", r"(?<!exclusive_)minimum\s*[:=]|>=|≥|大于等于|不小于|至少为"),
            ("maximum", r"(?<!exclusive_)maximum\s*[:=]|<=|≤|小于等于|不大于|至多为"),
            ("exclusive_minimum", r"exclusive_minimum\s*[:=]|>(?!=)|大于(?!等于)"),
            ("exclusive_maximum", r"exclusive_maximum\s*[:=]|<(?!=)|小于(?!等于)"),
        ):
            for match in re.finditer(rf"(?:{pattern})\s*(-?\d+)(?![\d.])", text, re.I):
                yield attribute, int(match.group(1))


def explicit_legacy_field_constraints(requirement: Requirement):
    """Reliably bound scalar constraints using Requirement vocabulary only.

    This is a read-only projection for source-conflict detection, not a new
    requirements ledger or an excuse to discard unsupported text. It never
    reads a candidate Plan. Unknown/ambiguous subjects remain ordinary coverage
    inputs. Typed obligations are independent and must not be overridden here.
    """
    vocabulary = {
        (item.entity, item.field): SimpleNamespace(name=item.field, kind=item.kind)
        for item in requirement.field_requirements
        if item.entity is not None
    }
    fields = [(entity, subject) for (entity, _), subject in vocabulary.items()]
    if not fields:
        return []
    result = []
    texts = [
        ({"section": section, "index": index}, text)
        for section in ("features", "acceptance")
        for index, text in enumerate(getattr(requirement, section))
    ]
    texts.extend(
        ({"section": "facts", "index": index, "encoding": "legacy", "path": path}, text)
        for index, (path, text) in enumerate(_fact_texts(requirement.facts, fields))
    )
    for origin, original in texts:
        text, _ = _legacy_field_exclusions(original, fields)
        text, _ = _metric_clauses(text, fields)
        text = _query_predicate_text(text, fields)
        for index, clause in enumerate(
            _legacy_clauses(_legacy_operation_text(text, fields), fields)
        ):
            for target in _legacy_targets(clause, fields):
                entity = next(owner for owner, field in fields if field is target)
                for attribute, expected in _legacy_scalar_constraints(clause):
                    result.append(
                        {
                            "source": {**origin, "clause": index},
                            "entity": entity,
                            "field": target.name,
                            "attribute": attribute,
                            "expected": expected,
                            "text": original,
                        }
                    )
    for index, (path, attributes, subject) in enumerate(
        _fact_constraints(requirement.facts, fields)
    ):
        if subject not in vocabulary:
            continue
        for attribute in (
            "required",
            "min_length",
            "max_length",
            "minimum",
            "maximum",
            "exclusive_minimum",
            "exclusive_maximum",
        ):
            value = _normalized_constraint_value(attribute, attributes.get(attribute))
            if type(value) is not (bool if attribute == "required" else int):
                continue
            result.append(
                {
                    "source": {
                        "section": "facts",
                        "index": index,
                        "encoding": "structured",
                        "path": path,
                    },
                    "entity": subject[0],
                    "field": subject[1],
                    "attribute": attribute,
                    "expected": value,
                    "text": json.dumps(attributes, ensure_ascii=False),
                }
            )
    return result


def _legacy_declared_fields(text, fields):
    """Recognize explicit field declarations, never infer fields from bare prose.

    This is a compatibility guard, not a general-language parser. Typed ledgers
    remain independent. Only a schema heading/imperative or a direct scalar
    descriptor can introduce an arbitrary identifier absent from the candidate.
    """
    owner = _fact_entity(text, fields)
    heading = _entity_subject_heading(text, fields)
    owners = (owner,) if owner else (None,)
    if heading:
        owners, text = heading
    elif owner:
        # Legacy facts retain a namespaced path before their description.
        match = re.search(rf"(?:^|[:：])\s*{re.escape(owner)}(?:::|[:：])", text)
        if match:
            text = text[match.end() :]
    aliases = [name for names in ALIASES.values() for name in names if not name.isascii()]
    name = (
        r"(?<![a-z0-9_])(?:[a-z][a-z0-9_]*(?:::|\.))?(?:[a-z][a-z0-9_]*|"
        + "|".join(aliases)
        + r")(?![a-z0-9_])"
    )
    separators = r"[、/,，]|和|与|及|\band\b"
    scalar = r"非必填|不必填|可选|必填|\bnot\s+required\b|\brequired\b|\boptional\b|max_length|min_length|(?:长度)?(?:上限|下限|最大|最小|最多|至少|最长|最短)"
    presence = r"(?:必须|需要)?存在|\bmust\s+exist\b"
    declaration = re.match(
        r"\s*(?:(?:字段(?:清单|列表)?|fields?)\s*[:：]?|"
        r"(?:必须|需要|要求)\s*(?:包含|添加|保留|存在|有)|"
        r"(?:must|should)\s+(?:include|add|retain|have)\b|"
        r"(?:不得|不要|不能)\s*(?:遗漏|缺少))\s*",
        text,
        re.I,
    )
    if declaration:
        body = text[declaration.end() :].strip()
        if body[:1] in "（([【":
            body = body[1:]
    else:
        descriptor = re.match(
            rf"\s*(?P<subjects>{name}(?:\s*(?:{separators})\s*{name})*)"
            rf"\s*(?:字段|fields?)?\s*[（(\[【]?\s*(?={scalar}|{presence})",
            text,
            re.I,
        )
        if not descriptor:
            return []
        body = descriptor["subjects"]
    result = []
    for part, _ in _top_level_parts(body, separators):
        subject = re.match(rf"\s*(?P<name>{name})", part, re.I)
        if not subject:
            break
        tail = part[subject.end() :].strip().rstrip("）)]】")
        # A new explanatory/waived clause is not another catalog member.
        if tail and tail[:1] not in "（([【" and not re.match(scalar, tail, re.I):
            break
        identity = subject["name"]
        qualified = re.fullmatch(r"([a-z][a-z0-9_]*)(?:::|\.)(.+)", identity, re.I)
        if qualified and qualified[1] in {field.name for _, field in fields} - {
            entity for entity, _ in fields
        }:
            # _fact_texts prefixes localized attributes with their field name;
            # title.标题长度上限 is a descriptor path, not entity title.
            continue
        result.extend(
            [(qualified[1], qualified[2])]
            if qualified
            else [(entity, identity) for entity in owners]
        )
    return result


def coverage_gaps(
    requirement: Requirement, plan: Plan, *, diagnostics=None, native_normalization=None
) -> list[str]:
    """Return blocking messages; optionally record the exact deterministic provenance.

    Diagnostic source indices refer to the retained Requirement, never a model
    verdict. Consumers exporting diagnostics must allowlist values separately.
    """
    if native_normalization:
        from workbench.native_plan_normalization import source_plan

        plan = source_plan(plan, native_normalization)
    gaps = entity_gaps(requirement, plan, diagnostics=diagnostics)
    fields = [(entity.name, field) for entity in plan.entities for field in entity.fields]
    typed_queries = {}
    source = {"section": "data_scope"}
    source_text = ""

    def query_matches(field, attribute, expected):
        key = (id(field), attribute, expected)
        if key in typed_queries:
            return typed_queries[key]
        # None/missing typed values and a genuinely different source value are
        # still checked. Reusing a typed result keeps every failure's provenance.
        return getattr(field, attribute) is expected

````
