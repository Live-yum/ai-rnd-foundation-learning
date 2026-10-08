# workbench/requirement_coverage.py · 2/4

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](workbench__requirement_coverage_py--001.md) · [下一段](workbench__requirement_coverage_py--003.md)

**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`、`workbench.requirement_canonical`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_fact_entity`（L901–L908）：接收`key`、`fields`。 控制顺序：L902按`"::" in key`分支。 调用`key.split("::")[0].rsplit`、`key.split`、`re.split`、`next`、`part.strip`、`reversed`。 返回路径：L903的`key.split("::")[0].rsplit(".", 1)[-1]`；L908的`next((part.strip() for part in reversed(path[:-1]) if part.strip() in entities), None)`。
- `_fact_candidates`（L911–L924）：接收`key`、`fields`。 调用`_fact_entity`、`_field_mentions`、`any`、`ALIASES.values`。 返回路径：L913的`[ field for entity, field in fields if (explicit_entity is None or entity == explicit_enti…`。
- `_legacy_targets`（L932–L945）：接收`text`、`fields`。 源码说明：Do not turn an ambiguous prose subject into grants on every entity. Exact typed obligations are checked independently. Unscoped repeated names remain semantic-review context unless the prose explicitl。 控制顺序：L939按`_fact_entity(text, fields) is not None or _ALL_ENTITIES.search(text)`分支。 调用`_fact_candidates`、`_fact_entity`、`_ALL_ENTITIES.search`、`len`。 返回路径：L940的`candidates`；L941的`[ field for field in candidates if len({entity for entity, item in fields if item.name == …`。
- `_query_composition_text`（L954–L993）：接收`text`、`fields`。 源码说明：A composite query needs its own local field targets to declare a flag. A subject-free composition statement combines the predicates already declared elsewhere. Explicit 'combined search by title' stil。 控制顺序：L963遍历`text`；L965按`char in "（([【"`分支；L967按`char in "）)]】"`分支；L970遍历`re.finditer(r"[，,；;。\n]\|以及\|并且\|并\|且\|和\|与\|\band\b", text, re.I…`；L971按`depths[match.start()]`分支；L973按`re.fullmatch(r"[，,；;。\n]", match.group()) or re.search( LEGACY_PROPERTY, text[boundar…`分支。 调用`depths.append`、`max`、`re.finditer`、`match.start`、`re.fullmatch`、`match.group`、`re.search`、`boundaries.append`、`match.end`等。 返回路径：L986的`re.sub( r"(?:组合\|联合\|复合\|多条件)\s*(?:查询\|检索\|搜索\|筛选\|过滤)\|" r"\b(?:combined\|composite\|comp…`。
- `_query_composition_text.replace`（L979–L984）：接收`match`。 控制顺序：L982按`_fact_candidates(text[start:end], fields)`分支。 调用`max`、`match.start`、`min`、`match.end`、`_fact_candidates`、`match.group`、`len`。 返回路径：L983的`match.group()`；L984的`" " * len(match.group())`。
- `_query_predicate_text`（L996–L1154）：接收`text`、`fields`。 源码说明：Exclude operation-derived nouns unless an explicit predicate binds fields. Search results and filter conditions describe query output or context; they do not independently enable a field capability. K。 控制顺序：L1048遍历`( rf"\b(?:do\|does\|must\|should)\s+not\s+include\s+(?P<targets>{…`。 调用`_query_composition_text`、`re.compile`、`names.update`、`ALIASES.values`、`"\|".join`、`name.isascii`、`re.escape`、`sorted`、`re.sub`等。 返回路径：L1154的`"; ".join([_DATE_RANGE_QUERY.sub("date_range", text), *shared_predicates])`。
- `_query_predicate_text.negative_membership`（L1044–L1046）：接收`match`。 调用`re.search`。 返回路径：L1046的`match["targets"] + " " + attribute + "=false"`。
- `_query_predicate_text.replace`（L1059–L1116）：接收`match`。 控制顺序：L1093按`binds_before or binds_after or imperative`分支；L1098按`re.search(r"日期区间\|日期范围\|date[-_\s]?range", operation, re.I)`分支；L1102按`negative`分支。 调用`re.split`、`match.start`、`match.end`、`bool`、`re.fullmatch`、`list`、`subjects.finditer`、`mentions[-1].end`、`re.match`等。 返回路径：L1113的`operation + " "`；L1116的`" " * len(match.group())`。
- `_query_predicate_text.shared_predicate`（L1133–L1147）：接收`match`。 控制顺序：L1136按`operation is None or _DATE_NEGATIVE.search(before)`分支；L1138遍历`re.finditer(subject, match["targets"], re.I)`；L1144遍历`fields`；L1145按`field.kind != "date" and any(field is target for target in candidates)`分支。 调用`re.search`、`re.split`、`match.start`、`_DATE_NEGATIVE.search`、`match.group`、`re.finditer`、`_fact_entity`、`reference.group`、`_legacy_targets`等。 返回路径：L1137的`match.group()`；L1147的`match.group()`。
- `_section_entity`（L1157–L1162）：接收`text`、`fields`。 源码说明：Infer only an unambiguous owner of an explicitly named field inventory.。 调用`_field_mentions`、`set.intersection`、`set`、`len`、`next`、`iter`。 返回路径：L1162的`next(iter(common)) if len(common) == 1 else None`。
- `_single_operation_heading`（L1165–L1183）：接收`text`。 源码说明：Only a bare single operation can predicate the list following a colon.。 控制顺序：L1169遍历`( r"日期区间\|日期范围(?:筛选\|查询)?\|date.?range", r"搜索\|检索\|search(?:ing\|…`；L1174按`re.search(pattern, remaining, re.I)`分支。 调用`re.search`、`re.sub`。 返回路径：L1183的`operations == 1 and not remaining`。
- `_explicit_predicate_heading`（L1186–L1201）：接收`text`。 源码说明：Known property/value syntax is a predicate, not a contextual title.。 控制顺序：L1188按`_single_operation_heading(text)`分支。 调用`_single_operation_heading`、`text.strip().rstrip(":：").strip`、`text.strip().rstrip`、`text.strip`、`re.sub(r"\s*(?:字段\|fields?)$", "", heading, flags=re.I).strip`、`re.sub`、`bool`、`re.fullmatch`。 返回路径：L1189的`True`；L1192的`bool( re.fullmatch( r"(?:required\|optional\|必填\|可选填?\|非必填\|不必填\|是否必填\|" r"min_length\|max…`。
- `_explicit_query_sections`（L1204–L1244）：接收`text`、`fields`。 源码说明：Separate a new query subject from an earlier inventory or operation. Commas inside descriptors and bare identifier lists remain untouched. A direct by/using/按/对 clause must name its own fields and ope。 控制顺序：L1211遍历`text`；L1213按`char in "（([【"`分支；L1215按`char in "）)]】"`分支；L1225遍历`boundary.finditer(text)`；L1226按`not depths[match.start()] and ( _fact_candidates(text[start : match.start()], fields)…`分支。 调用`depths.append`、`max`、`re.compile`、`boundary.finditer`、`match.start`、`_fact_candidates`、`text[start : match.start()].strip`、`_single_operation_heading`、`match.end`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_descriptor_inventory_groups`（L1247–L1293）：接收`text`、`subject_pattern`。 源码说明：Project bracketed per-field declarations separately from their wrapper. A bare search(title, detail) target list stays intact. In contrast, a list such as create(title max_length=200, detail max_lengt。 控制顺序：L1256遍历`enumerate(text)`；L1257按`char in "（([【"`分支；L1259按`char in "）)]】" and stack`分支；L1261按`not stack`分支；L1264遍历`spans`；L1267遍历`body`；L1269按`char in "（([【"`分支；L1271按`char in "）)]】"`分支。后续分支沿下方源码相同行号继续阅读。 调用`enumerate`、`stack.append`、`stack.pop`、`spans.append`、`depths.append`、`max`、`re.finditer`、`match.start`、`len`等。 返回路径：L1293的`"".join(parts), declarations`。
- `_entity_subject_heading`（L1296–L1320）：接收`text`、`fields`。 源码说明：Read explicit entity subjects before binding any field predicates. A group is a set of independent owners, not a namespace string. Explicit subjects replace inherited scope; unknown members of a partl。 控制顺序：L1311按`not heading`分支；L1316按`any(owner in field_names and owner not in known for owner in owners)`分支；L1318按`not any(owner in known for owner in owners) and "::" not in heading.group()`分支。 调用`re.match`、`tuple`、`dict.fromkeys`、`re.split`、`any`、`heading.group`、`heading.end`。 返回路径：L1312的`None`；L1317的`None`；L1319的`None`。
- `_explicit_entity_sections`（L1323–L1351）：接收`text`、`fields`。 源码说明：Recognize a new entity subject at top-level punctuation or conjunctions. A coordinated qualified field list still shares its trailing predicate: 'alpha.title and alpha.detail required' is not two inde。 控制顺序：L1332遍历`_top_level_parts(text, r"[、，,；;。\n]\|并且\|并\|且\|和\|与\|\band\b")`；L1335按`not separator or boundary < protected`分支；L1339按`not heading`分支；L1343按`len(owners) > 1 or not syntax.endswith(".") or re.search(LEGACY_PROPERTY, text[start:…`分支。 调用`_entity_subject_heading`、`len`、`_top_level_parts`、`following[: len(following) - len(body)].rstrip`、`syntax.endswith`、`re.search`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_legacy_length_text`（L1354–L1372）：接收`text`、`fields`。 源码说明：Lower explicit length notation, without treating numeric filters as lengths.。 控制顺序：L1356按`not re.search(r"长度\|字符\|\b(?:length\|characters?)\b", text, re.I)`分支。 调用`re.search`、`names.update`、`ALIASES.values`、`name.isascii`、`"\|".join`、`re.escape`、`sorted`、`re.sub`。 返回路径：L1357的`text`；L1361的`re.sub( rf"(?<![a-z0-9_])(?P<field>{pattern})\s*(?P<op>≤\|>=\|<=\|≥)\s*(?P<value>\d+)", la…`。
- `_legacy_subject_projections`（L1375–L1408）：接收`clause`、`pattern`、`scopes`。 源码说明：Project coordinated qualified fields to their owners before predicates. The predicate remains shared, while alpha.title and beta.detail can never become alpha.detail merely because alpha was the previ。 控制顺序：L1387遍历`subjects`；L1392按`not qualified`分支；L1396遍历`owners`；L1398遍历`zip(subjects, bindings)`。 调用`list`、`re.finditer`、`pattern.finditer`、`re.fullmatch`、`match.group`、`any`、`p.start`、`match.start`、`p.end`等。 返回路径：L1393的`[(owner, clause) for owner in scopes or (None,)]`；L1408的`result`。
- `_legacy_clauses`（L1411–L1663）：接收`text`、`fields`。 源码说明：Bind predicates to top-level subjects, preserving bracketed target lists. Both name（必填，最长120）and 搜索（name、contact）are indivisible. A descriptive clause ending at a comma does not lend its subject to th。 控制顺序：L1433遍历`re.split(r"([；;。\n]\|但是\|但\|不过)", text)`；L1434按`sentence in {"但是", "但", "不过"}`分支；L1437按`re.fullmatch(r"[；;。\n]", sentence)`分支；L1442按`contrast and previous_subject and not _fact_candidates(sentence, fields) and re.match…`分支；L1455在`True`成立时循环；L1458按`heading`分支；L1461按`syntax.endswith((":", "："))`分支；L1463按`scopes != persistent_scopes`分支。后续分支沿下方源码相同行号继续阅读。 调用`_legacy_length_text`、`";".join`、`_explicit_entity_sections`、`names.update`、`ALIASES.values`、`"\|".join`、`name.isascii`、`re.escape`、`sorted`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_operation_parts`（L1666–L1680）：接收`text`。 源码说明：Split coordinated operations, never the subjects inside a target list.。 控制顺序：L1669遍历`text`；L1671按`char in "（([【"`分支；L1673按`char in "）)]】"`分支；L1676遍历`re.finditer(r"[、，,]\|并且\|并\|且\|和\|与", text)`；L1677按`not depths[match.start()]`分支。 调用`depths.append`、`max`、`re.finditer`、`match.start`、`match.end`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_query_operation_groups`（L1683–L1735）：接收`text`、`fields`、`operations`。 源码说明：Bind a target list to its local prefix or suffix operator. A prefix operator owns following bare targets until another operator starts; a suffix operator owns preceding bare targets. Completed field d。 控制顺序：L1692遍历`_operation_parts(text)`；L1694按`marker is None`分支；L1695按`prefix`分支；L1697按`list(_legacy_scalar_constraints(part)) or "（）" in part`分支；L1698按`pending`分支；L1724按`prefix`分支；L1727按`is_prefix`分支；L1728按`pending`分支。后续分支沿下方源码相同行号继续阅读。 调用`re.compile`、`"\|".join`、`operations.values`、`_operation_parts`、`operation.search`、`prefix.append`、`list`、`_legacy_scalar_constraints`、`" ".join`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_top_level_parts`（L1764–L1783）：接收`text`、`separators`。 源码说明：Keep operand lists, descriptors and quoted values inside their own group.。 控制顺序：L1767遍历`enumerate(text)`；L1769按`quote`分支；L1770按`char == quote and (not index or text[index - 1] != "\\")`分支；L1772按`char in "\"'"`分支；L1774按`char in "（([【"`分支；L1776按`char in "）)]】"`分支；L1779遍历`re.finditer(separators, text, re.I)`；L1780按`not protected[match.start()]`分支。 调用`enumerate`、`protected.append`、`bool`、`max`、`re.finditer`、`match.start`、`match.group`、`match.end`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_metric_entity`（L1786–L1793）：接收`text`、`fields`。 源码说明：An entity named in a metric clause scopes it, including plain prose names.。 控制顺序：L1791按`explicit`分支。 调用`_METRIC_PREDICATE.sub`、`_field_mentions`、`_fact_entity`、`owners.add`、`len`、`next`、`iter`。 返回路径：L1793的`next(iter(owners)) if len(owners) == 1 else "<ambiguous entity>" if owners else None`。

</details>

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 4 段**。本段覆盖源文件 L901–L1795。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`38870`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 2, "parts": 4, "encoding": "utf-8", "sha256": "849c6815d3cb69b4a391b88efecd9626f084b53a2604d89ce86ea37566e6f169"} -->
````python
# workbench/requirement_coverage.py
def _fact_entity(key, fields):
    if "::" in key:
        return key.split("::")[0].rsplit(".", 1)[-1]
    # Nested objects and descriptor arrays retain their path. Bind constraints
    # to the nearest entity in that path, not every similarly named field.
    entities = {entity for entity, _ in fields}
    path = re.split(r"[.：:]", key)
    return next((part.strip() for part in reversed(path[:-1]) if part.strip() in entities), None)


def _fact_candidates(key, fields):
    explicit_entity = _fact_entity(key, fields)
    return [
        field
        for entity, field in fields
        if (explicit_entity is None or entity == explicit_entity)
        and (
            _field_mentions(key, [field.name])
            or any(
                field.name in aliases and _field_mentions(key, aliases)
                for aliases in ALIASES.values()
            )
        )
    ]


_ALL_ENTITIES = re.compile(
    r"(?:所有|全部|各个?|两个|两种)实体|\b(?:all|both|every)\s+entities\b", re.I
)


def _legacy_targets(text, fields):
    """Do not turn an ambiguous prose subject into grants on every entity.

    Exact typed obligations are checked independently. Unscoped repeated names
    remain semantic-review context unless the prose explicitly says all entities.
    """
    candidates = _fact_candidates(text, fields)
    if _fact_entity(text, fields) is not None or _ALL_ENTITIES.search(text):
        return candidates
    return [
        field
        for field in candidates
        if len({entity for entity, item in fields if item.name == field.name}) == 1
    ]


LEGACY_PROPERTY = (
    r"必填|可选|required|optional|搜索|检索|search|筛选|过滤|filter|"
    r"上限|最大|最多|最长|max_length|最小|至少|最短|min_length|日期区间|日期范围"
)


def _query_composition_text(text, fields):
    """A composite query needs its own local field targets to declare a flag.

    A subject-free composition statement combines the predicates already
    declared elsewhere. Explicit 'combined search by title' still declares
    title's primitive operation; neither an earlier nor a later clause can
    donate targets to a generic composition statement.
    """
    depth, depths = 0, []
    for char in text:
        depths.append(depth)
        if char in "（([【":
            depth += 1
        elif char in "）)]】":
            depth = max(0, depth - 1)
    boundaries = [0]
    for match in re.finditer(r"[，,；;。\n]|以及|并且|并|且|和|与|\band\b", text, re.I):
        if depths[match.start()]:
            continue
        if re.fullmatch(r"[，,；;。\n]", match.group()) or re.search(
            LEGACY_PROPERTY, text[boundaries[-1] : match.start()], re.I
        ):
            boundaries.append(match.end())
    boundaries.append(len(text))

    def replace(match):
        start = max(boundary for boundary in boundaries if boundary <= match.start())
        end = min(boundary for boundary in boundaries if boundary >= match.end())
        if _fact_candidates(text[start:end], fields):
            return match.group()
        return " " * len(match.group())

    return re.sub(
        r"(?:组合|联合|复合|多条件)\s*(?:查询|检索|搜索|筛选|过滤)|"
        r"\b(?:combined|composite|compound|multi[-\s]?condition)\s+"
        r"(?:search(?:ing)?|filter(?:ing)?|quer(?:y|ies))\b",
        replace,
        text,
        flags=re.I,
    )


def _query_predicate_text(text, fields):
    """Exclude operation-derived nouns unless an explicit predicate binds fields.

    Search results and filter conditions describe query output or context; they
    do not independently enable a field capability. Keep declarations such as
    'title is a search criterion' and imperatives such as 'filter results by title'.
    Other verbs in the same clause remain available for ordinary subject binding.
    """
    text = _query_composition_text(text, fields)
    nouns = re.compile(
        r"(?P<operation>"
        r"(?:日期区间|日期范围)(?:筛选|过滤|查询)?|"
        r"(?:关键词|关键字|精确)?(?:搜索|检索|筛选|过滤)|"
        r"\b(?:date[-_\s]?range(?:\s+(?:search|filter(?:ing)?|quer(?:y|ies)))?|"
        r"search(?:ing|ed|es)?|filter(?:ing|ed|s)?)\b)"
        r"\s*(?:的|后(?:的)?|所得(?:的)?|(?:返回|得到|产生)的|['’]s)?[-\s]*"
        r"(?P<noun>结果集?|效果|输出|返回值|条件|"
        r"results?|outcomes?|outputs?|effects?|conditions?|criteria|criterion)"
        r"(?![a-z_])",
        re.I,
    )
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    subjects = re.compile(
        "|".join(
            rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])" if name.isascii() else re.escape(name)
            for name in sorted(names, key=len, reverse=True)
        ),
        re.I,
    )
    # Membership in query controls is a capability predicate, not a schema
    # exclusion. Output/display surfaces (e.g. search results) are not controls.
    subject = rf"(?:[a-z][a-z0-9_]*(?:::|\.))?(?:{subjects.pattern})"
    targets = rf"{subject}(?:\s*(?:[、/]|和|与|\band\b)\s*{subject})*"
    # A keyword query (or a field-bound keyword shorthand) is a search
    # predicate. Lower it before noun/negative/clause handling, so a following
    # exact-filter operator cannot absorb these already-complete targets.
    keyword = r"(?:关键词|关键字|(?<![a-z0-9_])keywords?(?![a-z0-9_]))"
    text = re.sub(keyword + r"\s*(?:查询|\bquer(?:y|ies)\b)", " search ", text, flags=re.I)
    text = re.sub(
        rf"(?P<targets>{targets})\s*(?:的\s*)?{keyword}"
        r"(?=\s*(?:以及|及|并且|并|且|和|与|\band\b|[、，,；;。\n]|$))",
        r"\g<targets> search ",
        text,
        flags=re.I,
    )
    controls = r"(?:filters?|filter\s+(?:criteria|conditions?)|search\s+(?:criteria|conditions?))"

    def negative_membership(match):
        attribute = "searchable" if re.search(r"search", match["control"], re.I) else "filterable"
        return match["targets"] + " " + attribute + "=false"

    for declaration in (
        rf"\b(?:do|does|must|should)\s+not\s+include\s+(?P<targets>{targets})",
        rf"(?P<targets>{targets})\s+(?:must|should)\s+not\s+(?:appear|be\s+included)",
    ):
        text = re.sub(
            declaration + rf"\s+(?:in|as)\s+(?:the\s+)?(?P<control>{controls})\b",
            negative_membership,
            text,
            flags=re.I,
        )

    def replace(match):
        before = re.split(r"[，,；;。\n]", text[: match.start()])[-1]
        after = re.split(r"[，,；;。\n]", text[match.end() :])[0]
        condition = bool(re.fullmatch(r"条件|conditions?|criteria|criterion", match["noun"], re.I))
        mentions = list(subjects.finditer(before))
        tail = before[mentions[-1].end() :] if mentions else ""
        binds_before = (
            condition
            and mentions
            and re.fullmatch(
                r"\s*(?:(?:字段)?\s*(?:可|必须|应|可以|不可|不可以|不得|不能)?\s*"
                r"(?:作为|用作|用于|设置为|设为|是|为)|"
                r"(?:fields?\s+)?(?:is|are|as|(?:must|should)\s+(?:not\s+)?be|"
                r"(?:is|are)\s+not|(?:is|are)\s+(?:not\s+)?used\s+as|"
                r"cannot\s+be\s+used\s+as|serves?\s+as))\s*(?:a|an|the)?\s*",
                tail,
                re.I,
            )
        )
        binds_after = (
            condition
            and re.match(
                r"\s*(?:[：:]|为|是|不?包括|不?包含|使用|采用|"
                r"\b(?:(?:do|does)\s+not\s+include|include|includes|are|is|use|uses)\b)",
                after,
                re.I,
            )
            and subjects.search(after)
        )
        imperative = (
            re.fullmatch(r"search(?:ing)?|filter(?:ing)?", match["operation"], re.I)
            and re.match(r"\s+(?:by|using|on)\s+", after, re.I)
            and subjects.search(after)
        )
        if binds_before or binds_after or imperative:
            operation = match["operation"]
            negative = (
                binds_before and re.search(r"不可|不得|不能|\bnot\b|\bcannot\b", tail, re.I)
            ) or (binds_after and re.match(r"\s*(?:不|(?:do|does)\s+not\b)", after, re.I))
            if re.search(r"日期区间|日期范围|date[-_\s]?range", operation, re.I):
                # Here 日期/date is part of an explicit capability predicate,
                # not a second field named published_on.
                operation = "date_range"
            if negative:
                attribute = (
                    "date_range"
                    if operation == "date_range"
                    else (
                        "searchable"
                        if re.search(r"搜索|检索|search", operation, re.I)
                        else "filterable"
                    )
                )
                operation = attribute + "=false"
            return operation + " "
        # Whitespace preserves token boundaries without manufacturing a new
        # subject, predicate or field alias from the noun phrase.
        return " " * len(match.group())

    text = nouns.sub(replace, text)
    # In "priority and inclusive date range filtering", the trailing verb
    # also predicates the preceding bare fields. Project that shared verb
    # before folding the compound; completed descriptors are not bare targets.
    shared_targets = rf"{subject}(?:\s*(?:[、/,，]|和|与|\band\b)\s*{subject})*"
    shared_range = re.compile(
        rf"(?P<targets>{shared_targets})\s*(?:[、/]|和|与|及|\band\b)\s*"
        rf"(?P<ranged>(?:{subject}\s*)?"
        r"(?:(?:含边界|包含(?:首尾|两端|边界)(?:的)?|起止|inclusive)\s*)?)"
        rf"(?P<range>{_DATE_RANGE_QUERY.pattern})",
        re.I,
    )

    shared_predicates = []

    def shared_predicate(match):
        operation = re.search(r"筛选|过滤|filters?|filtering\b", match["range"], re.I)
        before = re.split(r"[，,；;。\n]", text[: match.start()])[-1]
        if operation is None or _DATE_NEGATIVE.search(before):
            return match.group()
        for reference in re.finditer(subject, match["targets"], re.I):
            scope = _fact_entity(reference.group(), fields) or _fact_entity(
                text[: match.start()], fields
            )
            bound = f"{scope}::{reference.group()}" if scope else reference.group()
            candidates = _legacy_targets(bound, fields)
            for owner, field in fields:
                if field.kind != "date" and any(field is target for target in candidates):
                    shared_predicates.append(f"{owner}.{field.name} {operation.group()}")
        return match.group()

    text = shared_range.sub(shared_predicate, text)
    # A compound range query is one capability. Lower it before the legacy
    # field/operation splitter can treat its search/filter suffix independently.
    # Keep noun handling first: "date range filter results" is still output,
    # while "date range filter and exact filter" keeps both real predicates.
    return "; ".join([_DATE_RANGE_QUERY.sub("date_range", text), *shared_predicates])


def _section_entity(text, fields):
    """Infer only an unambiguous owner of an explicitly named field inventory."""
    declared = {field.name for _, field in fields if _field_mentions(text, [field.name])}
    owners = [{entity for entity, field in fields if field.name == name} for name in declared]
    common = set.intersection(*owners) if owners else set()
    return next(iter(common)) if len(common) == 1 else None


def _single_operation_heading(text):
    """Only a bare single operation can predicate the list following a colon."""
    remaining = text
    operations = 0
    for pattern in (
        r"日期区间|日期范围(?:筛选|查询)?|date.?range",
        r"搜索|检索|search(?:ing|able)?",
        r"筛选|过滤|filter(?:s|ing|able)?",
    ):
        if re.search(pattern, remaining, re.I):
            operations += 1
            remaining = re.sub(pattern, "", remaining, flags=re.I)
    remaining = re.sub(
        r"关键词|关键字|精确|支持|允许|字段|keywords?|exact|fields?|true|false|是|否|and|和|与|并|[\W_]",
        "",
        remaining,
        flags=re.I,
    )
    return operations == 1 and not remaining


def _explicit_predicate_heading(text):
    """Known property/value syntax is a predicate, not a contextual title."""
    if _single_operation_heading(text):
        return True
    heading = text.strip().rstrip(":：").strip()
    heading = re.sub(r"\s*(?:字段|fields?)$", "", heading, flags=re.I).strip()
    return bool(
        re.fullmatch(
            r"(?:required|optional|必填|可选填?|非必填|不必填|是否必填|"
            r"min_length|max_length|(?:长度)?(?:上限|下限)|最小(?:长度)?|最大(?:长度)?|"
            r"至少|最多|最长|最短)"
            r"(?:\s*[:=]?\s*(?:true|false|是|否|\d+))?",
            heading,
            re.I,
        )
    )


def _explicit_query_sections(text, fields):
    """Separate a new query subject from an earlier inventory or operation.

    Commas inside descriptors and bare identifier lists remain untouched.
    A direct by/using/按/对 clause must name its own fields and operation.
    """
    depth, depths = 0, []
    for char in text:
        depths.append(depth)
        if char in "（([【":
            depth += 1
        elif char in "）)]】":
            depth = max(0, depth - 1)
    boundary = re.compile(
        r"(?:[,，]\s*(?:(?:并且|并|且|and)\s*)?|(?:并且|并|且|\band\b)\s*)"
        r"(?=按|对|针对|依据|支持|允许|必须|需要|"
        r"\b(?:by|using|on|supports?|allows?|requires?)\b|"
        r"(?:keyword\s+)?search|filter|关键词搜索|精确筛选)",
        re.I,
    )
    start = 0
    for match in boundary.finditer(text):
        if (
            not depths[match.start()]
            and (
                _fact_candidates(text[start : match.start()], fields)
                or (
                    text[start : match.start()].strip()
                    and not _single_operation_heading(text[start : match.start()])
                )
            )
            and _fact_candidates(text[match.end() :], fields)
            and re.search(
                r"搜索|检索|筛选|过滤|search|filter|日期区间|日期范围|date.?range",
                text[match.end() :],
                re.I,
            )
        ):
            yield text[start : match.start()]
            start = match.end()
    yield text[start:]


def _descriptor_inventory_groups(text, subject_pattern):
    """Project bracketed per-field declarations separately from their wrapper.

    A bare search(title, detail) target list stays intact. In contrast, a list
    such as create(title max_length=200, detail max_length=3000) has independent
    predicates. Keep the wrapper with its bare targets so a genuine outer
    capability still binds them, and check the declarations as separate clauses.
    """
    stack, spans = [], []
    for index, char in enumerate(text):
        if char in "（([【":
            stack.append(index)
        elif char in "）)]】" and stack:
            start = stack.pop()
            if not stack:
                spans.append((start, index))
    parts, declarations, previous = [], [], 0
    for start, end in spans:
        body = text[start + 1 : end]
        depth, depths = 0, []
        for char in body:
            depths.append(depth)
            if char in "（([【":
                depth += 1
            elif char in "）)]】":
                depth = max(0, depth - 1)
        subjects = [
            match for match in re.finditer(subject_pattern, body, re.I) if not depths[match.start()]
        ]
        inventory = len(subjects) > 1 and any(
            re.search(LEGACY_PROPERTY, body[left.end() : right.start()], re.I)
            or (
                re.match(r"\s*[（(\[【]", body[left.end() : right.start()])
                and re.search(r"[）)\]】]", body[left.end() : right.start()])
            )
            for left, right in zip(subjects, subjects[1:])
        )
        if inventory:
            declarations.append(body)
            replacement = "、".join(dict.fromkeys(match.group() for match in subjects))
        else:
            replacement, nested = _descriptor_inventory_groups(body, subject_pattern)
            declarations.extend(nested)
        parts.append(text[previous : start + 1] + replacement + text[end])
        previous = end + 1
    parts.append(text[previous:])
    return "".join(parts), declarations


def _entity_subject_heading(text, fields):
    """Read explicit entity subjects before binding any field predicates.

    A group is a set of independent owners, not a namespace string. Explicit
    subjects replace inherited scope; unknown members of a partly known group
    are retained so another member cannot satisfy their missing fields.
    """
    identifier = r"[a-z][a-z0-9_]*"
    conjunction = r"[/、,&，]|和|与|及|\band\b"
    heading = re.match(
        rf"\s*(?:[-*]\s+|\d+[.)]\s+)?(?P<owners>{identifier}(?:\s*(?:{conjunction})\s*{identifier})*)"
        r"\s*(?:::|[：:.]|的\s*|['’]s\s+|(?=\s+\S))",
        text,
        re.I,
    )
    if not heading:
        return None
    owners = tuple(dict.fromkeys(re.split(rf"\s*(?:{conjunction})\s*", heading["owners"])))
    known = {entity for entity, _ in fields}
    field_names = {field.name for _, field in fields}
    if any(owner in field_names and owner not in known for owner in owners):
        return None
    if not any(owner in known for owner in owners) and "::" not in heading.group():
        return None
    return owners, text[heading.end() :]


def _explicit_entity_sections(text, fields):
    """Recognize a new entity subject at top-level punctuation or conjunctions.

    A coordinated qualified field list still shares its trailing predicate:
    'alpha.title and alpha.detail required' is not two independent sentences.
    """
    leading = _entity_subject_heading(text, fields)
    protected = len(text) - len(leading[1]) if leading else 0
    start, offset = 0, 0
    for part, separator in _top_level_parts(text, r"[、，,；;。\n]|并且|并|且|和|与|\band\b"):
        boundary = offset + len(part)
        offset = boundary + len(separator)
        if not separator or boundary < protected:
            continue
        following = text[offset:]
        heading = _entity_subject_heading(following, fields)
        if not heading:
            continue
        owners, body = heading
        syntax = following[: len(following) - len(body)].rstrip()
        if (
            len(owners) > 1
            or not syntax.endswith(".")
            or re.search(LEGACY_PROPERTY, text[start:boundary], re.I)
        ):
            yield text[start:boundary], text[boundary:offset]
            start = offset
            protected = offset + len(following) - len(body)
    yield text[start:], ""


def _legacy_length_text(text, fields):
    """Lower explicit length notation, without treating numeric filters as lengths."""
    if not re.search(r"长度|字符|\b(?:length|characters?)\b", text, re.I):
        return text
    names = {field.name for _, field in fields}
    names.update(name for names in ALIASES.values() for name in names if name.isascii())
    pattern = "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))
    return re.sub(
        rf"(?<![a-z0-9_])(?P<field>{pattern})\s*(?P<op>≤|>=|<=|≥)\s*(?P<value>\d+)",
        lambda match: (
            match["field"]
            + " "
            + ("max_length" if match["op"] in {"≤", "<="} else "min_length")
            + "="
            + match["value"]
        ),
        text,
        flags=re.I,
    )


def _legacy_subject_projections(clause, pattern, scopes):
    """Project coordinated qualified fields to their owners before predicates.

    The predicate remains shared, while alpha.title and beta.detail can never
    become alpha.detail merely because alpha was the previous namespace.
    """
    subjects = list(re.finditer(pattern, clause, re.I))
    predicates = [
        match for pattern in (_DATE_TYPE, _DATE_FORMAT) for match in pattern.finditer(clause)
    ]
    bindings = []
    qualified = False
    for match in subjects:
        reference = re.fullmatch(r"([a-z][a-z0-9_]*)(?:::|\.)(.+)", match.group(), re.I)
        qualified = qualified or reference is not None
        neutral = any(p.start() <= match.start() and p.end() >= match.end() for p in predicates)
        bindings.append(((reference.group(1),) if reference else scopes, reference, neutral))
    if not qualified:
        return [(owner, clause) for owner in scopes or (None,)]
    owners = dict.fromkeys(owner for targets, _, _ in bindings for owner in targets)
    result = []
    for owner in owners:
        parts, start = [], 0
        for match, (targets, reference, neutral) in zip(subjects, bindings):
            parts.append(clause[start : match.start()])
            parts.append(
                (reference.group(2) if reference else match.group())
                if owner in targets or neutral
                else " " * len(match.group())
            )
            start = match.end()
        parts.append(clause[start:])
        result.append((owner, "".join(parts)))
    return result


def _legacy_clauses(text, fields):
    """Bind predicates to top-level subjects, preserving bracketed target lists.

    Both name（必填，最长120）and 搜索（name、contact）are indivisible.
    A descriptive clause ending at a comma does not lend its subject to the
    next clause. Bare coordinated subjects still share their final predicate.
    """
    text = _legacy_length_text(text, fields)
    text = ";".join(part for part, _ in _explicit_entity_sections(text, fields))
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    pattern = "|".join(
        rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])" if name.isascii() else re.escape(name)
        for name in sorted(names, key=len, reverse=True)
    )
    entity_names = "|".join(re.escape(entity) for entity, _ in fields)
    pattern = rf"(?:(?:{entity_names})(?:::|\.))?(?:{pattern})"
    initial_scope = _fact_entity(text, fields)
    scopes = (initial_scope,) if initial_scope else ()
    persistent_scopes = ()
    previous_subject = ""
    contrast = False
    for sentence in re.split(r"([；;。\n]|但是|但|不过)", text):
        if sentence in {"但是", "但", "不过"}:
            contrast = True
            continue
        if re.fullmatch(r"[；;。\n]", sentence):
            contrast = False
            previous_subject = ""
            scopes = persistent_scopes
            continue
        if (
            contrast
            and previous_subject
            and not _fact_candidates(sentence, fields)
            and re.match(
                r"\s*(?:仍|却|可以|可|必须|需要|要求|支持|允许|不能|禁止|禁用|不)", sentence
            )
            and re.search(LEGACY_PROPERTY, sentence, re.I)
        ):
            sentence = previous_subject + " " + sentence
        contrast = False
        universal_scope = bool(_ALL_ENTITIES.search(sentence))
        explicit_scope = False
        while True:
            original = sentence
            heading = _entity_subject_heading(sentence, fields)
            if heading:
                syntax = sentence[: len(sentence) - len(heading[1])].rstrip()
                scopes, sentence = heading
                if syntax.endswith((":", "：")):
                    persistent_scopes = scopes
                elif scopes != persistent_scopes:
                    persistent_scopes = ()
                explicit_scope = True
            else:
                heading = re.match(r"\s*[^：:\n]*(?:字段|fields)\s*[：:]", sentence, re.I)
                if heading and not _explicit_predicate_heading(heading.group()):
                    if not explicit_scope:
                        scopes = ()
                        persistent_scopes = ()
                    body = sentence[heading.end() :]
                    declared = re.findall(r"(?<![a-z0-9_])([a-z][a-z0-9_]*)\s*[(（]", body, re.I)
                    if not declared:
                        declared = list(
                            {
                                field.name
                                for _, field in fields
                                if _field_mentions(body, [field.name])
                            }
                        )
                    owners = [
                        {entity for entity, field in fields if field.name == name}
                        for name in declared
                    ]
                    common = set.intersection(*owners) if owners and all(owners) else set()
                    # A localized heading is mapped by its executable descriptor
                    # list, never a hard-coded translation or the first entity.
                    if len(common) == 1:
                        if not explicit_scope:
                            scopes = (common.pop(),)
                            persistent_scopes = scopes
                        sentence = body
                else:
                    heading = re.match(r"\s*([^：:\n]+)[：:]", sentence)
                    if heading and not _fact_candidates(heading.group(1), fields):
                        body = sentence[heading.end() :]
                        # A section title is context, not a predicate on its first
                        # field. Keep an operation-only heading when its body is
                        # merely the target list (e.g. 'search: title, detail').
                        if re.search(LEGACY_PROPERTY, body, re.I) or (
                            _fact_candidates(body, fields)
                            and not _explicit_predicate_heading(heading.group(1))
                        ):
                            if not explicit_scope:
                                inferred = _section_entity(body, fields)
                                scopes = (inferred,) if inferred else ()
                                persistent_scopes = ()
                            sentence = body
            if sentence == original:
                break
        wrapper, inventories = _descriptor_inventory_groups(sentence, pattern)
        if inventories:
            for part in [wrapper, *inventories]:
                for owner in scopes or (None,):
                    scoped = f"{owner}::{part}" if owner else part
                    if universal_scope and not owner:
                        scoped = "所有实体：" + scoped
                    yield from _legacy_clauses(scoped, fields)
            subjects = _fact_candidates(sentence, fields)
            if subjects:
                previous_subject = "、".join(dict.fromkeys(field.name for field in subjects))
            continue
        sections = list(_explicit_query_sections(sentence, fields))
        if len(sections) > 1:
            for section in sections:
                for owner in scopes or (None,):
                    scoped = f"{owner}::{section}" if owner else section
                    if universal_scope and not owner:
                        scoped = "所有实体：" + scoped
                    yield from _legacy_clauses(scoped, fields)
                    subjects = _fact_candidates(scoped, fields)
                    if subjects:
                        previous_subject = "、".join(
                            dict.fromkeys(field.name for field in subjects)
                        )
            continue
        depths, depth = [], 0
        for char in sentence:
            depths.append(depth)
            if char in "（([【":
                depth += 1
            elif char in "）)]】":
                depth = max(0, depth - 1)
        previous = []
        start = 0
        seen_subject = False
        previous_match = None
        for match in re.finditer(pattern, sentence, re.I):
            # Field aliases inside a descriptor or operation-first target list
            # are part of that group, not new top-level clauses.
            if depths[match.start()]:
                seen_subject = True
                continue
            if (
                previous_match is not None
                and not sentence[previous_match.end() : match.start()].strip()
            ):
                # Adjacent identifier/translation pairs (category分类) name
                # one subject; a predicate before that subject cannot split it.
                if any(
                    _field_mentions(previous_match.group(), aliases)
                    and _field_mentions(match.group(), aliases)
                    for aliases in ALIASES.values()
                ):
                    previous_match = match
                    continue
            completed_descriptor = False
            prior_end = previous_match.end() if previous_match is not None else start
            if previous_match is not None:
                opening = previous_match.end()
                while opening < match.start() and sentence[opening].isspace():
                    opening += 1
                if opening < match.start() and sentence[opening] in "（([【":
                    completed_descriptor = any(
                        sentence[index] in "）)]】" and depths[index] == 1
                        for index in range(opening + 1, match.start())
                    )
            previous_match = match
            prefix = sentence[start : match.start()]
            if not seen_subject:
                # Entity-level capability summaries before a comma are not
                # predicates on the first field in the following declaration.
                # An explicit operation-first subject list (搜索，按name) stays
                # bound to its subject instead of becoming a generic query.
                boundary = next(
                    (
                        index
                        for index in range(match.start() - 1, start - 1, -1)
                        if sentence[index] in ",，" and not depths[index]
                    ),
                    None,
                )
                if (
                    boundary is not None
                    and re.search(
                        r"搜索|检索|筛选|过滤|search|filter", sentence[start:boundary], re.I
                    )
                    and not re.search(
                        r"按|针对|依据|\bby\b", sentence[boundary + 1 : match.start()], re.I
                    )
                ):
                    previous.append(sentence[start:boundary])
                    start = boundary + 1
                    prefix = sentence[start : match.start()]
            comma = next(
                (
                    index
                    for index in range(match.start() - 1, start - 1, -1)
                    if sentence[index] in ",，" and not depths[index]
                ),
                None,
            )
            descriptive_boundary = False
            if comma is not None:
                first_subject = re.search(pattern, sentence[start:comma], re.I)
                described_from = start + first_subject.end() if first_subject else start
                before_comma = re.sub(pattern, "", sentence[described_from:comma], flags=re.I)
                descriptive_boundary = bool(re.search(r"[a-z0-9\u4e00-\u9fff]", before_comma))
            if seen_subject and (
                re.search(LEGACY_PROPERTY, sentence[prior_end : match.start()], re.I)
                or descriptive_boundary
                or completed_descriptor
            ):
                leading = re.search(
                    r"[,，]\s*((?:可选填|可选|必填|required|optional)\s*)$", prefix, re.I
                )
                cut = start + leading.start(1) if leading else match.start()
                previous.append(sentence[start:cut])
                start = cut
            seen_subject = True
        previous.append(sentence[start:])
        shared = re.search(r"[)）]\s*((?:均|都)\s*.*)$", sentence)
        shared_suffix = (
            shared.group(1)
            if shared
            and re.search(LEGACY_PROPERTY, shared.group(1), re.I)
            and not _fact_candidates(shared.group(1), fields)
            else ""
        )
        list_modifier = ""
        for clause in previous:
            if clause.strip():
                if list_modifier and not re.search(r"必填|可选|required|optional", clause, re.I):
                    clause = list_modifier + " " + clause
                modifier = re.match(r"\s*(可选填|可选|必填|required|optional)\s*", clause, re.I)
                list_modifier = (
                    modifier.group(1) if modifier and re.search(r"[、,，]\s*$", clause) else ""
                )
                # A trailing explicit 'all/both' predicate is shared even when
                # the individual fields have complete, independent descriptors.
                if shared_suffix and re.search(r"[)）]", clause) and shared_suffix not in clause:
                    clause += " " + shared_suffix
                for owner, projection in _legacy_subject_projections(clause, pattern, scopes):
                    scoped = f"{owner}::{projection}" if owner else projection
                    if universal_scope and not owner:
                        scoped = "所有实体 " + scoped
                    subjects = _fact_candidates(scoped, fields)
                    if subjects:
                        previous_subject = "、".join(
                            dict.fromkeys(field.name for field in subjects)
                        )
                    yield scoped


def _operation_parts(text):
    """Split coordinated operations, never the subjects inside a target list."""
    depth, depths = 0, []
    for char in text:
        depths.append(depth)
        if char in "（([【":
            depth += 1
        elif char in "）)]】":
            depth = max(0, depth - 1)
    start = 0
    for match in re.finditer(r"[、，,]|并且|并|且|和|与", text):
        if not depths[match.start()]:
            yield text[start : match.start()]
            start = match.end()
    yield text[start:]


def _query_operation_groups(text, fields, operations):
    """Bind a target list to its local prefix or suffix operator.

    A prefix operator owns following bare targets until another operator starts;
    a suffix operator owns preceding bare targets. Completed field descriptors
    are not a pending target list. This partitions syntax, not typed obligations.
    """
    operation = re.compile("|".join(operations.values()), re.I)
    pending, prefix = [], []
    for part in _operation_parts(text):
        marker = operation.search(part)
        if marker is None:
            if prefix:
                prefix.append(part)
            elif list(_legacy_scalar_constraints(part)) or "（）" in part:
                if pending:
                    yield " ".join(pending)
                    pending = []
                yield part
            else:
                pending.append(part)
            continue
        names = {field.name for field in _fact_candidates(part, fields)}
        names.update(
            alias
            for aliases in ALIASES.values()
            if names.intersection(aliases)
            for alias in aliases
        )
        positions = [
            match.start()
            for name in names
            for match in re.finditer(
                rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])"
                if name.isascii()
                else re.escape(name),
                part,
                re.I,
            )
        ]
        is_prefix = marker.start() < min(positions, default=len(part))
        if prefix:
            yield " ".join(prefix)
            prefix = []
        if is_prefix:
            if pending:
                yield " ".join(pending)
            prefix = [part]
        else:
            yield " ".join([*pending, part])
        pending = []
    if prefix or pending:
        yield " ".join([*prefix, *pending])


_METRIC_CONTEXT = re.compile(
    r"(?<![a-z_])(?:count|group_count|time_count|average_duration|metrics?)(?![a-z_])"
    r"|指标|统计|计数|已解决数|总数|平均.*时长|趋势|分组",
    re.I,
)
_METRIC_KIND = re.compile(
    r"(?<![a-z_])(?:group_count|time_count|average_duration|count)(?![a-z_])"
    r"|已解决数|总数|平均.*?时长|趋势|分组",
    re.I,
)
_QUERY_SURFACE = re.compile(
    r"列表|表格|页面|界面|筛选器|搜索框|查询条件|查询参数|filterable|searchable|date_range"
    r"|(?<![a-z_])(?:list|table|form|ui|search)(?![a-z_])",
    re.I,
)
_METRIC_SCOPE = re.compile(r"权限|可见|角色|本人|负责范围|assigned|read_metrics", re.I)
_METRIC_FILTER = re.compile(r"筛选|过滤|(?<![a-z_])filters?(?![a-z_])", re.I)
_METRIC_PREDICATE = re.compile(
    r"(?<![a-z0-9_])(?:(?P<entity>[a-z][a-z0-9_]*)[.:])?"
    r"(?P<field>[a-z][a-z0-9_]*)\s*(?P<op>!=|>=|<=|==|=)\s*"
    r"(?P<value>\"[^\"]*\"|'[^']*'|[a-zA-Z0-9_.:+-]+|"
    r"[\u4e00-\u9fff]+?(?=\s|[，,；;、（）()]|筛选|过滤|$))",
    re.I,
)


def _top_level_parts(text, separators):
    """Keep operand lists, descriptors and quoted values inside their own group."""
    depth, quote, protected = 0, None, []
    for index, char in enumerate(text):
        protected.append(bool(depth or quote))
        if quote:
            if char == quote and (not index or text[index - 1] != "\\"):
                quote = None
        elif char in "\"'":
            quote = char
        elif char in "（([【":
            depth += 1
        elif char in "）)]】":
            depth = max(0, depth - 1)
    start = 0
    for match in re.finditer(separators, text, re.I):
        if not protected[match.start()]:
            yield text[start : match.start()], match.group()
            start = match.end()
    yield text[start:], ""


def _metric_entity(text, fields):
    """An entity named in a metric clause scopes it, including plain prose names."""
    text = _METRIC_PREDICATE.sub(lambda match: match["entity"] or "", text)
    owners = {entity for entity, _ in fields if _field_mentions(text, [entity])}
    explicit = _fact_entity(text, fields)
    if explicit:
        owners.add(explicit)
    return next(iter(owners)) if len(owners) == 1 else "<ambiguous entity>" if owners else None


````
