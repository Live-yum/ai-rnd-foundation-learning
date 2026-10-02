# workbench/requirement_coverage.py · 3/3

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__requirement_coverage_py--002.md)

**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_metric_clauses.parenthesis`（L1781–L1788）：接收`match`。 调用`match.start`、`re.split`、`match.group`、`consume`。 返回路径：L1788的`match.group() if filtered == body else ""`。
- `_negative_operation_pattern`（L1807–L1824）：接收`fields`。 调用`names.update`、`ALIASES.values`、`"\|".join`、`re.escape`、`sorted`、`re.compile`。 返回路径：L1820的`re.compile( negative + r"\s*(?:任何\|额外的?\|新的?)?\s*" + targets + r"(?:" + operation + r")" r…`。
- `_legacy_boolean_text`（L1827–L1851）：接收`text`、`fields`。 源码说明：Lower explicit negative capability lists before field-clause splitting. 不可/不支持/不提供/不参与 describe disabled behavior; 无需/不要求 merely decline a requirement. Coordination ends before a new field or a positi。 调用`_negative_operation_pattern(fields).sub`、`_negative_operation_pattern`。 返回路径：L1851的`_negative_operation_pattern(fields).sub(replace, text)`。
- `_legacy_boolean_text.replace`（L1834–L1849）：接收`match`。 控制顺序：L1836按`not re.match(r"禁止\|禁用\|关闭\|不得\|不允许\|不可(?:以)?\|不支持\|不提供\|不参与", phrase)`分支；L1839按`re.search(r"搜索\|检索\|search", phrase, re.I)`分支；L1845按`re.search(r"筛选\|过滤\|filter", exact, re.I)`分支；L1847按`re.search(r"日期区间\|日期范围\|date.?range", phrase, re.I)`分支。 调用`match.group`、`re.match`、`re.search`、`attributes.append`、`re.sub`、`" ".join`。 返回路径：L1837的`""`；L1849的`" " + (match.group("targets") or "") + " " + " ".join(attributes) + " "`。
- `_legacy_operation_text`（L1854–L1866）：接收`text`、`fields`。 源码说明：Remove checked negatives without merging their subjects into the next clause. An empty descriptor preserves the field boundary, while keeping coordinated negated date-range terms out of the positive f。 调用`re.sub`、`_negative_operation_pattern(fields).sub`、`_negative_operation_pattern`。 返回路径：L1866的`_negative_operation_pattern(fields).sub("（）", text)`。
- `_legacy_field_exclusions`（L1869–L1955）：接收`text`、`fields`。 源码说明：Separate absence of fields from nullable fields or disabled operations. Only explicit absence/removal predicates bind exclusions. In particular, 'not required', 'not null' and 'do not filter' are not 。 控制顺序：L1916遍历`sentences`；L1918按`heading`分支。 调用`names.update`、`ALIASES.values`、`"\|".join`、`re.escape`、`sorted`、`name.isascii`、`re.compile`、`_fact_entity`、`_top_level_parts`等。 返回路径：L1955的`"".join(output), obligations`。
- `_legacy_field_exclusions.replace`（L1921–L1950）：接收`match`。 控制顺序：L1930按`query_location or re.search( r"搜索\|检索\|筛选\|过滤\|显示\|展示\|界面\|列表\|\b(?:search\|filter\|d…`分支；L1938遍历`re.split(separator_pattern, identities, flags=re.I)`。 调用`re.split`、`match.start`、`re.match`、`match.end`、`re.search`、`match.group`、`identity.strip`、`re.fullmatch`、`qualified.group`等。 返回路径：L1935的`match.group()`；L1950的`match.group()[:start] + " " * (end - start) + match.group()[end:]`。
- `_legacy_date_obligations`（L1984–L2065）：接收`text`、`fields`。 源码说明：Interpret field types, not every mention of a date-shaped string. Read original source clauses before query lowering discards negations or headings. A format alone is presentation metadata; it becomes。 控制顺序：L1994遍历`re.split(r"[；;。\n]\|但是\|但\|不过\|\bbut\b", text, flags=re.I)`；L1995按`not sentence.strip()`分支；L2003遍历`_legacy_clauses(sentence, fields)`；L2006按`not markers and not formats`分支；L2023遍历`[*markers, *formats]`；L2027按`_DATE_NEGATIVE.search(local_prefix) or re.match( r"\s*(?:字段\|类型\|校验\|验证)?\s*(?:无需\|不需…`分支；L2033按`context or _DATE_CONTEXT.search(local_prefix)`分支；L2035按`marker in formats and ( not concrete or not _DATE_INPUT.search(clause) or _DATE_PRESE…`分支。后续分支沿下方源码相同行号继续阅读。 调用`_fact_entity`、`re.split`、`sentence.strip`、`re.match`、`bool`、`_DATE_CONTEXT.search`、`headings.group`、`re.search`、`_legacy_clauses`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_normalized_constraint_value`（L2068–L2081）：接收`attribute`、`expected`。 控制顺序：L2069按`attribute in {"required", "searchable", "filterable", "date_range"}`分支；L2070按`isinstance(expected, str)`分支；L2072按`word in {"true", "是", "必填"}`分支；L2074按`word in {"false", "否", "可选", "非必填"}`分支；L2076按`attribute in {"min_length", "max_length"}`分支；L2077按`isinstance(expected, str)`分支；L2079按`legacy`分支。 调用`isinstance`、`expected.strip().lower`、`expected.strip`、`re.fullmatch`、`int`、`legacy.group`。 返回路径：L2081的`expected`。
- `_matches_constraint`（L2084–L2096）：接收`attribute`、`expected`、`actual`。 控制顺序：L2086按`attribute in {"required", "searchable", "filterable", "date_range"}`分支；L2088按`attribute in {"min_length", "max_length"}`分支；L2090按`attribute == "choices"`分支。 调用`_normalized_constraint_value`、`type`、`isinstance`、`all`、`set`。 返回路径：L2087的`type(expected) is bool and actual is expected`；L2089的`type(expected) is int and actual == expected`；L2091的`isinstance(expected, list) and all(isinstance(item, str) for item in expected) and set(act…`。
- `_legacy_scalar_constraints`（L2099–L2121）：接收`text`。 源码说明：Shared scalar predicate extraction after entity/field subject binding.。 控制顺序：L2110按`not validation`分支；L2111按`re.search(r"必填\|required", text, re.I) and not optional`分支；L2113按`optional or re.search(r"可选", text)`分支；L2115遍历`( ("max_length", r"上限\|最大\|max_length\|最多\|最长"), ("min_length", r…`；L2120按`number`分支。 调用`bool`、`re.search`、`int`、`number.group`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `explicit_legacy_field_constraints`（L2124–L2194）：接收`requirement`。 源码说明：Reliably bound scalar constraints using Requirement vocabulary only. This is a read-only projection for source-conflict detection, not a new requirements ledger or an excuse to discard unsupported tex。 控制顺序：L2138按`not fields`分支；L2150遍历`texts`；L2154遍历`enumerate( _legacy_clauses(_legacy_operation_text(text, fields), …`；L2157遍历`_legacy_targets(clause, fields)`；L2159遍历`_legacy_scalar_constraints(clause)`；L2170遍历`enumerate( _fact_constraints(requirement.facts, fields) )`；L2173按`subject not in vocabulary`分支；L2175遍历`("required", "min_length", "max_length")`。后续分支沿下方源码相同行号继续阅读。 调用`SimpleNamespace`、`vocabulary.items`、`enumerate`、`getattr`、`texts.extend`、`_fact_texts`、`_legacy_field_exclusions`、`_metric_clauses`、`_query_predicate_text`等。 返回路径：L2139的`[]`；L2194的`result`。
- `_legacy_declared_fields`（L2197–L2267）：接收`text`、`fields`。 源码说明：Recognize explicit field declarations, never infer fields from bare prose. This is a compatibility guard, not a general-language parser. Typed ledgers remain independent. Only a schema heading/imperat。 控制顺序：L2207按`heading`分支；L2209按`owner`分支；L2212按`match`分支；L2231按`declaration`分支；L2233按`body[:1] in "（([【"`分支；L2242按`not descriptor`分支；L2246遍历`_top_level_parts(body, separators)`；L2248按`not subject`分支。后续分支沿下方源码相同行号继续阅读。 调用`_fact_entity`、`_entity_subject_heading`、`re.search`、`re.escape`、`match.end`、`ALIASES.values`、`name.isascii`、`"\|".join`、`re.match`等。 返回路径：L2243的`[]`；L2267的`result`。
- `coverage_gaps`（L2270–L2717）：接收`requirement`、`plan`、`diagnostics`。 源码说明：Return blocking messages; optionally record the exact deterministic provenance. Diagnostic source indices refer to the retained Requirement, never a model verdict. Consumers exporting diagnostics must。 控制顺序：L2320按`plan.data_scope != requirement.data_scope`分支；L2327遍历`enumerate(requirement.field_requirements)`；L2335按`len(matches) != 1`分支；L2339遍历`obligation.model_dump().items()`；L2340按`key in {"field", "entity"} or value is None`分支；L2344按`key in {"searchable", "filterable", "date_range"} and type(value) is bool`分支；L2346按`not matches_constraint`分支；L2364遍历`enumerate(structured)`。后续分支沿下方源码相同行号继续阅读。 调用`entity_gaps`、`gap`、`enumerate`、`len`、`obligation.model_dump().items`、`obligation.model_dump`、`getattr`、`_matches_constraint`、`type`等。 返回路径：L2717的`list(dict.fromkeys(gaps))`。
- `coverage_gaps.query_matches`（L2282–L2288）：接收`field`、`attribute`、`expected`。 控制顺序：L2284按`key in typed_queries`分支。 调用`id`、`getattr`。 返回路径：L2285的`typed_queries[key]`；L2288的`getattr(field, attribute) is expected`。
- `coverage_gaps.gap`（L2290–L2318）：接收`message`、`code`、`targets`、`attribute`、`expected`、`actual`。 控制顺序：L2292按`diagnostics is not None`分支。 调用`gaps.append`、`diagnostics.append`、`dict`、`any`、`re.search`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 3 段**。本段覆盖源文件 L1781–L2717。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`43528`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 3, "parts": 3, "encoding": "utf-8", "sha256": "e2d4321c3a2ea7087b4d5f68fdbfd233e288f912fc61968665bc568e5473f407"} -->
````python
# workbench/requirement_coverage.py
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
    negative = r"(?:无需|不需要|不要求|取消|禁止|禁用|关闭|不得|不允许|不可(?:以)?|不支持|不添加|不提供|不参与|不要|没有|无|不)"
    operation = (
        r"(?:(?:关键词|关键字|精确)\s*)?(?:搜索|检索|筛选|过滤)"
        r"|(?:日期区间|日期范围)(?:筛选|过滤|查询)?"
        r"|search(?:able)?|filter(?:able)?|date.?range"
    )
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    name = (
        "(?:" + "|".join(re.escape(value) for value in sorted(names, key=len, reverse=True)) + ")"
    )
    targets = "(?P<targets>" + name + r"(?:\s*[、和与]\s*" + name + r")*(?:的)?\s*)?"
    return re.compile(
        negative + r"\s*(?:任何|额外的?|新的?)?\s*" + targets + r"(?:" + operation + r")"
        r"(?:\s*(?:以及|[、或和及与])\s*(?:" + negative + r")?\s*(?:" + operation + r"))*",
        re.I,
    )


def _legacy_boolean_text(text, fields):
    """Lower explicit negative capability lists before field-clause splitting.

    不可/不支持/不提供/不参与 describe disabled behavior; 无需/不要求 merely
    decline a requirement. Coordination ends before a new field or a positive predicate.
    """

    def replace(match):
        phrase = match.group()
        if not re.match(r"禁止|禁用|关闭|不得|不允许|不可(?:以)?|不支持|不提供|不参与", phrase):
            return ""
        attributes = []
        if re.search(r"搜索|检索|search", phrase, re.I):
            attributes.append("searchable=false")
        # A date-range operation is not a separate exact-filter toggle.
        exact = re.sub(
            r"(?:日期区间|日期范围)(?:筛选|过滤|查询)?|date.?range", "", phrase, flags=re.I
        )
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
    if attribute in {"min_length", "max_length"}:
        if isinstance(expected, str):
            legacy = re.fullmatch(r"\s*(\d+)\s*(?:字符|字|characters?)?\s*", expected, re.I)
            if legacy:
                expected = int(legacy.group(1))
    return expected


def _matches_constraint(attribute, expected, actual):
    expected = _normalized_constraint_value(attribute, expected)
    if attribute in {"required", "searchable", "filterable", "date_range"}:
        return type(expected) is bool and actual is expected
    if attribute in {"min_length", "max_length"}:
        return type(expected) is int and actual == expected
    if attribute == "choices":
        return (
            isinstance(expected, list)
            and all(isinstance(item, str) for item in expected)
            and set(actual) == set(expected)
        )
    return type(expected) is str and actual == expected


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
        for attribute in ("required", "min_length", "max_length"):
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


def coverage_gaps(requirement: Requirement, plan: Plan, *, diagnostics=None) -> list[str]:
    """Return blocking messages; optionally record the exact deterministic provenance.

    Diagnostic source indices refer to the retained Requirement, never a model
    verdict. Consumers exporting diagnostics must allowlist values separately.
    """
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
            matches_constraint = _matches_constraint(key, value, actual)
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
                if (attribute == "choices" and field.kind != "enum") or not _matches_constraint(
                    attribute, expected, getattr(field, attribute)
                ):
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
                actual = getattr(field, attribute)
                if actual == expected:
                    continue
                description = (
                    ("必填" if expected else "可选")
                    if attribute == "required"
                    else ("长度上限为 " if attribute == "max_length" else "最小长度为 ")
                    + str(expected)
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
