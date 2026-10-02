# workbench/requirement_coverage.py · 1/4

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](workbench__requirement_coverage_py--002.md)

**作用：保留用户事实并检查可执行需求覆盖。** 模型格式与类型先由官方LangChain结构化输出和Pydantic负责。reconcile保留已确认事实，替换要有当前真实用户更正原文；coverage_gaps逐项比较结构化字段、数据归属与可识别业务约束，指标与列表查询分区。仅提到英文别名不会建立新字段义务；真实正向声明、明确禁止字段及旧文本兼容检查仍保留，不把部分typed清单当成语义完整证明。来源冲突与设计漏项仍阻塞，不让规划模型自行宣布已覆盖。

**对应关系：** flow.analyse保留事实 → Requirement.field_requirements → flow.design → coverage_gaps；test_requirement_coverage。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.entity_requirements`、`workbench.requirement_canonical`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 例如用户已明确请求标题可搜索，候选Plan却把 searchable 设为 false：coverage_gaps 返回可定位的缺项，流程不能因为JSON合法就批准。reconcile 接收上一版Requirement和新候选；新一轮只是没再提到字段时保留原事实，只有带本轮原话证据的明确更正才能修改。读这一层时用第03阶段的正确计划、缺搜索计划和省略事实三份输入对照，不先背辅助正则。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_mentions`（L31–L37）：接收`text`、`names`。 调用`any`、`n.isascii`、`re.search`、`re.escape`、`text.lower`。 返回路径：L32的`any( re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", text.lower()) if n.isascii() e…`。
- `_authorized`（L40–L204）：接收`change`、`corrections`。 控制顺序：L42按`not any(quote in text for text in corrections)`分支；L44按`not re.search( r"修改\|改为\|改成\|更改\|取消\|删除\|移除\|不再\|不要\|改\|change\|replace\|remove\|drop…`分支；L50按`change.section == "additional_entities"`分支；L63按`change.section == "entity_requirements"`分支；L65按`not _field_mentions(quote, [entity])`分支；L67按`not attribute and change.replacement is None`分支；L69按`attribute == "fields"`分支；L79按`attribute == "additional_fields" and type(change.replacement) is bool`分支。后续分支沿下方源码相同行号继续阅读。 调用`any`、`re.search`、`type`、`bool`、`stated.group(1).lower`、`stated.group`、`change.key.partition`、`_field_mentions`、`isinstance`等。 返回路径：L43的`False`；L49的`False`；L57的`change.key == "additional_entities" and type(change.replacement) is bool and bool(stated) …`。
- `_authorized.stated`（L183–L202）：接收`value`。 控制顺序：L184按`isinstance(value, bool)`分支；L185按`re.search(r"false\|否\|可选\|非必填\|不必填\|关闭\|禁用", quote, re.I)`分支；L188按`isinstance(value, (int, float))`分支；L190按`value == "shared"`分支；L192按`value == "per_user"`分支；L194按`str(value).lower() in quote.lower()`分支；L196按`isinstance(value, str)`分支；L200按`numbers and re.search(r"长度\|字符\|字\|length", quote, re.I)`分支。 调用`isinstance`、`re.search`、`bool`、`re.escape`、`str`、`str(value).lower`、`quote.lower`、`re.findall`、`all`。 返回路径：L186的`not value`；L187的`value and bool(re.search(r"true\|是\|必填\|启用\|开启", quote, re.I))`；L189的`bool(re.search(rf"(?<![\d.]){re.escape(str(value))}(?![\d.])", quote))`。
- `_propagate_fact_correction`（L207–L236）：接收`data`、`key`、`replacement`。 源码说明：Synchronize a source-backed numeric fact across unambiguous legacy text.。 控制顺序：L216按`not attribute or len(numbers) != 1 or len(targets) != 1`分支；L219遍历`("features", "acceptance")`；L220遍历`enumerate(data[section])`；L222按`mentioned == [aliases] and re.search( r"上限\|最大\|最多\|max_length" if attribute == "max_…`分支；L234遍历`data["field_requirements"]`；L235按`field["field"] in aliases`分支。 调用`re.search`、`re.findall`、`str`、`ALIASES.values`、`_mentions`、`len`、`enumerate`、`re.sub`、`list`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `reconcile`（L239–L312）：接收`previous`、`proposed`、`corrections`、`audit`、`canonicalization`。 源码说明：Omission isn't deletion; only source-backed fresh edits replace old intent.。 控制顺序：L241按`not previous`分支；L248遍历`("features", "acceptance", "users")`；L257按`"additional_entities" in previous or not old.additional_entities`分支；L259按`old.data_scope != "unknown"`分支；L261遍历`proposed.changes`；L268按`audit is not None`分支；L270按`not authorized`分支；L274按`section == "facts"`分支。后续分支沿下方源码相同行号继续阅读。 调用`proposed.model_dump`、`canonicalize_requirement`、`Requirement.model_validate`、`list`、`dict.fromkeys`、`getattr`、`f.model_dump`、`fields.update`、`fields.values`等。 返回路径：L245的`Requirement.model_validate(data)`；L312的`Requirement.model_validate(data)`。
- `_presentation_namespace`（L350–L372）：接收`key`。 源码说明：Normalize semantic namespace words, not individual model spellings.。 控制顺序：L352按`not isinstance(key, str)`分支；L354按`key.casefold() in PRESENTATION_FACT_CONTAINERS`分支；L359按`words & {"labels", "display", "presentation", "ui", "i18n", "localization", "translat…`分支。 调用`isinstance`、`key.casefold`、`re.sub`、`set`、`re.findall`、`normalized.casefold`、`any`。 返回路径：L353的`False`；L355的`True`；L360的`True`。
- `_decode_fact`（L420–L429）：接收`value`。 控制顺序：L421按`isinstance(value, str) and value.lstrip().startswith(("{", "["))`分支；L427按`isinstance(decoded, (dict, list))`分支。 调用`isinstance`、`value.lstrip().startswith`、`value.lstrip`、`json.loads`。 返回路径：L428的`decoded`；L429的`value`。
- `_fact_subject`（L432–L452）：接收`key`、`fields`、`entity`、`declared`。 源码说明：Resolve a field position, never a substring of an ancestor's business name.。 控制顺序：L434按`entity is not None and ( not isinstance(entity, str) or not re.fullmatch(r"[a-z][a-z0…`分支；L438按`not isinstance(key, str)`分支；L441按`qualified`分支；L444按`re.fullmatch(r"[a-z][a-z0-9_]*", key) and ( declared or any(field.name == key for _, …`分支；L448遍历`ALIASES.items()`；L449按`key in aliases`分支。 调用`isinstance`、`re.fullmatch`、`qualified.groups`、`any`、`ALIASES.items`、`len`、`next`、`iter`。 返回路径：L439的`(entity, "<invalid field>") if declared else None`；L447的`entity, key`；L451的`entity, next(iter(names)) if len(names) == 1 else canonical`。
- `_field_kind`（L455–L456）：接收`value`。 调用`isinstance`。 返回路径：L456的`isinstance(value, str) and value in FIELD_KINDS`。
- `_scalar_subject`（L459–L466）：接收`key`、`fields`、`entity`。 控制顺序：L464按`len(names) == 1`分支。 调用`_fact_candidates`、`len`、`_fact_entity`、`next`、`iter`。 返回路径：L465的`entity or _fact_entity(key, fields), next(iter(names))`；L466的`None`。
- `_optional_fact`（L469–L474）：接收`value`。 控制顺序：L470按`type(value) is bool`分支；L472按`isinstance(value, str) and value.strip().lower() in {"true", "false", "是", "否"}`分支。 调用`type`、`isinstance`、`value.strip().lower`、`value.strip`。 返回路径：L471的`not value`；L473的`value.strip().lower() in {"false", "否"}`；L474的`value`。
- `_constraint_schema`（L477–L491）：接收`value`。 源码说明：A structural declaration distinguishes a schema from a translated caption.。 控制顺序：L480按`isinstance(value, list)`分支；L482按`not isinstance(value, dict)`分支。 调用`_decode_fact`、`isinstance`、`any`、`value.values`、`value.get`、`bool`、`re.fullmatch`、`type`。 返回路径：L481的`any(isinstance(_decode_fact(item), dict) for item in value)`；L483的`False`；L484的`any(isinstance(_decode_fact(item), (dict, list)) for item in value.values()) or ( isinstan…`。
- `_business_schema`（L494–L500）：接收`value`。 源码说明：An explicit business wrapper needs structured domain declarations.。 调用`_decode_fact`、`isinstance`、`any`、`value.items`。 返回路径：L497的`isinstance(value, dict) and any( key in BUSINESS_FACT_CONTAINERS and isinstance(_decode_fa…`。
- `_fact_records`（L503–L778）：接收`facts`、`fields`。 源码说明：Classify structural facts before projecting field constraints or prose. A name/entity pair alone is not a field declaration. Field definitions have an explicit field position and attributes; business 。 控制顺序：L776遍历`facts.items()`；L777按`key not in FACT_METADATA_KEYS`分支。 调用`facts.items`、`walk`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_fact_records.walk`（L513–L774）：接收`key`、`value`、`path`、`entity`、`subject`、`business`、`container`、`domain`。 控制顺序：L531按`key in FIELD_CONSTRAINT_CONTAINERS and container != "fields" and (domain != "presenta…`分支；L537按`domain == "presentation" and key in BUSINESS_CONSTRAINT_CONTAINERS and _business_sche…`分支；L543按`_presentation_namespace(key) and container != "fields" and not field_position`分支；L545按`domain == "presentation"`分支；L546按`isinstance(value, dict)`分支；L548按`isinstance(value, list)`分支；L552遍历`children`；L555按`key in FIELD_CONSTRAINT_CONTAINERS and container != "fields" and not isinstance(value…`分支。后续分支沿下方源码相同行号继续阅读。 调用`_decode_fact`、`".".join`、`isinstance`、`bool`、`set`、`_fact_subject`、`_constraint_schema`、`_business_schema`、`_presentation_namespace`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_fact_constraints`（L781–L784）：接收`facts`、`fields`。 控制顺序：L782遍历`_fact_records(facts, fields)`；L783按`kind == "constraint"`分支。 调用`_fact_records`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_fact_attribute`（L787–L811）：接收`label`。 控制顺序：L796按`attribute is None and re.search(r"(?:是否必填\|必填)$", label)`分支；L798按`attribute is None and re.search(r"(?:是否可选\|可选)$", label)`分支；L800按`attribute is None`分支；L803遍历`( (r"(?:日期\|date).*(?:区间\|范围\|range)(?:筛选\|过滤)?$", "date_range"),…`；L808按`re.search(pattern, label, re.I)`分支。 调用`next`、`re.search`、`re.escape`。 返回路径：L811的`attribute`。
- `_scalar_fact_attribute`（L814–L830）：接收`label`、`value`。 控制顺序：L816按`attribute in {"required", "optional", "searchable", "filterable", "date_range"}`分支；L817按`isinstance(value, str) and value.strip().lower() not in { "true", "false", "是", "否", …`分支。 调用`_fact_attribute`、`isinstance`、`value.strip().lower`、`value.strip`。 返回路径：L829的`None`；L830的`attribute`。
- `_fact_texts`（L833–L836）：接收`facts`、`fields`。 控制顺序：L834遍历`_fact_records(facts, fields)`；L835按`kind == "text"`分支。 调用`_fact_records`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_field_mentions`（L839–L851）：接收`text`、`names`。 源码说明：Field identifiers are whole identifiers, not arbitrary underscore fragments.。 调用`re.sub`、`"\|".join`、`sorted`、`any`、`name.isascii`、`re.search`、`re.escape`。 返回路径：L846的`any( re.search(rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])", text, re.I) if name.isasc…`。
- `_fact_entity`（L854–L861）：接收`key`、`fields`。 控制顺序：L855按`"::" in key`分支。 调用`key.split("::")[0].rsplit`、`key.split`、`re.split`、`next`、`part.strip`、`reversed`。 返回路径：L856的`key.split("::")[0].rsplit(".", 1)[-1]`；L861的`next((part.strip() for part in reversed(path[:-1]) if part.strip() in entities), None)`。
- `_fact_candidates`（L864–L877）：接收`key`、`fields`。 调用`_fact_entity`、`_field_mentions`、`any`、`ALIASES.values`。 返回路径：L866的`[ field for entity, field in fields if (explicit_entity is None or entity == explicit_enti…`。

</details>

**创建路径：** `workbench/requirement_coverage.py`；**本文件共有 4 段**。本段覆盖源文件 L1–L884。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`35639`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_coverage.py", "part": 1, "parts": 4, "encoding": "utf-8", "sha256": "f831d1776e5d2b81424d99a8d099f55929c23965b73c8019d73aea10b84c5506"} -->
````python
# workbench/requirement_coverage.py
"""Persist approved intent and check executable obligations without a model verdict.

Legacy free text is interpreted conservatively for known field vocabulary; new
requirements can supply exact field_requirements for arbitrary domain fields.
"""

import json
import re
from copy import deepcopy
from types import SimpleNamespace

from workbench.domain import Plan, Requirement
from workbench.entity_requirements import entity_gaps
from workbench.requirement_canonical import canonicalize_requirement

ALIASES = {
    "title": ("title", "标题"),
    "body": ("body", "content", "正文", "内容"),
    "category": ("category", "分类", "类别"),
    "published_on": (
        "published_on",
        "publish_date",
        "publication_date",
        "date",
        "日期",
        "发布日期",
    ),
}


def _mentions(text, names):
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", text.lower())
        if n.isascii()
        else n in text
        for n in names
    )


def _authorized(change, corrections):
    quote = change.source_quote
    if not any(quote in text for text in corrections):
        return False
    if not re.search(
        r"修改|改为|改成|更改|取消|删除|移除|不再|不要|改|change|replace|remove|drop|instead",
        quote,
        re.I,
    ):
        return False
    if change.section == "additional_entities":
        stated = re.search(
            r"(?<![a-z0-9_])additional_entities\s*(?:[:=为]|改为|改成|更改为)?"
            r"\s*(true|false|是|否)(?![a-z])",
            quote,
            re.I,
        )
        return (
            change.key == "additional_entities"
            and type(change.replacement) is bool
            and bool(stated)
            and change.replacement is (stated.group(1).lower() in {"true", "是"})
        )
    if change.section == "entity_requirements":
        entity, _, attribute = change.key.partition(".")
        if not _field_mentions(quote, [entity]):
            return False
        if not attribute and change.replacement is None:
            return bool(re.search(r"取消|删除|移除|不再|不要|remove|drop", quote, re.I))
        if attribute == "fields":
            return (
                bool(re.search(r"字段|\bfields\b", quote, re.I))
                and isinstance(change.replacement, list)
                and bool(change.replacement)
                and all(
                    isinstance(value, str) and _field_mentions(quote, [value])
                    for value in change.replacement
                )
            )
        if attribute == "additional_fields" and type(change.replacement) is bool:
            stated = re.search(
                rf"(?<![a-z0-9_]){re.escape(entity)}(?:\.additional_fields|\s*"
                r"(?:的)?(?:额外字段|其他字段|新增字段))\s*"
                r"(?:[:=为]|改为|改成|更改为)?\s*(true|false|是|否)(?![a-z])",
                quote,
                re.I,
            )
            return bool(stated) and change.replacement is (
                stated.group(1).lower() in {"true", "是"}
            )
        return False
    # Legacy public-registration goals may be explicitly replaced by an
    # administrative-only scope. This recognizes the whole original goal only;
    # compound features and an unrelated cancellation still cannot be erased.
    if change.section in {"features", "acceptance"} and change.replacement is None:
        from workbench.requirement_intent import cancellable_registration_goal

        if cancellable_registration_goal(change.key, quote):
            return True
    aliases = [change.key]
    if change.section == "data_scope":
        aliases.extend(["数据归属", "数据范围", "data scope"])
    for names in ALIASES.values():
        if _mentions(change.key, names):
            aliases.extend(names)
    if not _mentions(quote, aliases):
        # Natural cancellation may name a capability rather than repeat the
        # entire old sentence. Never remove a compound unrelated capability.
        capabilities = (r"搜索|检索|search", r"筛选|过滤|filter", r"CRUD|增删改查", r"日期|date")
        relevant = [pattern for pattern in capabilities if re.search(pattern, change.key, re.I)]
        if (
            change.section not in {"features", "acceptance"}
            or not relevant
            or not all(re.search(pattern, quote, re.I) for pattern in relevant)
        ):
            return False
    attributes = (
        (r"max_length|上限|最大", r"max_length|maximum|上限|最大|最多|长度"),
        (r"min_length|下限|最小", r"min_length|minimum|下限|最小|至少"),
        (r"required|必填", r"required|optional|必填|可选"),
        (r"searchable", r"search|搜索|检索"),
        (r"filterable", r"filter|筛选|过滤"),
        (r"date_range", r"range|区间|范围"),
    )
    if any(
        re.search(key_pattern, change.key, re.I) and not re.search(quote_pattern, quote, re.I)
        for key_pattern, quote_pattern in attributes
    ):
        return False
    if change.replacement is None:
        if change.section in {"features", "acceptance", "users"} and change.key not in quote:
            capabilities = (
                r"搜索|检索|search",
                r"筛选|过滤|filter",
                r"CRUD|增删改查",
                r"必填|required",
                r"可选|optional",
                r"日期|date",
                r"长度|字符|最多|至少|length",
            )
            if any(
                re.search(pattern, change.key, re.I) and not re.search(pattern, quote, re.I)
                for pattern in capabilities
            ):
                return False
            old_targets = [names for names in ALIASES.values() if _mentions(change.key, names)]
            quote_targets = [names for names in ALIASES.values() if _mentions(quote, names)]
            if quote_targets and any(names not in quote_targets for names in old_targets):
                return False
        return bool(re.search(r"取消|删除|移除|不再|不要|remove|drop", quote, re.I))
    if change.section in {"features", "acceptance"} and isinstance(change.replacement, str):
        capabilities = (
            r"搜索|检索|search",
            r"筛选|过滤|filter",
            r"CRUD|增删改查",
            r"必填|required",
            r"可选|optional",
            r"日期|date",
        )
        for pattern in capabilities:
            if re.search(pattern, change.key, re.I) and not re.search(
                pattern, change.replacement, re.I
            ):
                if not (
                    re.search(r"取消|删除|移除|不再|不要|remove|drop", quote, re.I)
                    and re.search(pattern, quote, re.I)
                ):
                    return False
        for aliases in ALIASES.values():
            if _mentions(change.key, aliases) and not _mentions(change.replacement, aliases):
                if not (
                    _mentions(quote, aliases)
                    and re.search(r"取消|删除|移除|不再|不要|remove|drop", quote, re.I)
                ):
                    return False
    # A quoted correction must actually state the new value, not merely be any
    # recent user message. Structured objects require each explicit value.
    values = change.replacement
    if isinstance(values, dict):
        values = list(values.values())
    if not isinstance(values, list):
        values = [values]

    def stated(value):
        if isinstance(value, bool):
            if re.search(r"false|否|可选|非必填|不必填|关闭|禁用", quote, re.I):
                return not value
            return value and bool(re.search(r"true|是|必填|启用|开启", quote, re.I))
        if isinstance(value, (int, float)):
            return bool(re.search(rf"(?<![\d.]){re.escape(str(value))}(?![\d.])", quote))
        if value == "shared":
            return bool(re.search(r"shared|共享", quote, re.I))
        if value == "per_user":
            return bool(re.search(r"per_user|逐用户|个人|隔离", quote, re.I))
        if str(value).lower() in quote.lower():
            return True
        if isinstance(value, str):
            numbers = re.findall(r"\d+", value)
            # Numeric constraint rewording preserves the same field and kind
            # of obligation; the source must state every replacement number.
            if numbers and re.search(r"长度|字符|字|length", quote, re.I):
                return all(re.search(rf"(?<!\d){number}(?!\d)", quote) for number in numbers)
        return False

    return all(stated(value) for value in values)


def _propagate_fact_correction(data, key, replacement):
    """Synchronize a source-backed numeric fact across unambiguous legacy text."""
    attribute = (
        "max_length"
        if re.search(r"max_length|上限|最大", key)
        else ("min_length" if re.search(r"min_length|下限|最小", key) else None)
    )
    numbers = re.findall(r"\d+", str(replacement))
    targets = [aliases for aliases in ALIASES.values() if _mentions(key, aliases)]
    if not attribute or len(numbers) != 1 or len(targets) != 1:
        return
    aliases = targets[0]
    for section in ("features", "acceptance"):
        for index, text in enumerate(data[section]):
            mentioned = [names for names in ALIASES.values() if _mentions(text, names)]
            if (
                mentioned == [aliases]
                and re.search(
                    r"上限|最大|最多|max_length"
                    if attribute == "max_length"
                    else r"最小|至少|min_length",
                    text,
                )
                and len(re.findall(r"\d+", text)) == 1
            ):
                data[section][index] = re.sub(r"\d+", numbers[0], text)
        data[section] = list(dict.fromkeys(data[section]))
    for field in data["field_requirements"]:
        if field["field"] in aliases:
            field[attribute] = int(numbers[0])


def reconcile(previous, proposed, corrections, audit=None, *, canonicalization=None):
    """Omission isn't deletion; only source-backed fresh edits replace old intent."""
    if not previous:
        data = proposed.model_dump()
        data["changes"] = []
        canonicalize_requirement(data, canonicalization)
        return Requirement.model_validate(data)
    old = Requirement.model_validate(previous)
    data = proposed.model_dump()
    for section in ("features", "acceptance", "users"):
        data[section] = list(dict.fromkeys([*getattr(old, section), *data[section]]))
    data["facts"] = {**data["facts"], **old.facts}
    fields = {(f.entity, f.field): f.model_dump() for f in proposed.field_requirements}
    fields.update({(f.entity, f.field): f.model_dump() for f in old.field_requirements})
    data["field_requirements"] = list(fields.values())
    entities = {item.entity: item.model_dump() for item in proposed.entity_requirements}
    entities.update({item.entity: item.model_dump() for item in old.entity_requirements})
    data["entity_requirements"] = list(entities.values())
    if "additional_entities" in previous or not old.additional_entities:
        data["additional_entities"] = old.additional_entities
    if old.data_scope != "unknown":
        data["data_scope"] = old.data_scope
    for change in proposed.changes:
        authorized = _authorized(change, corrections)
        event = {
            **change.model_dump(),
            "authorized": authorized,
            "before": deepcopy(data[change.section]),
        }
        if audit is not None:
            audit.append(event)
        if not authorized:
            event["after"] = deepcopy(data[change.section])
            continue
        section, key, replacement = change.section, change.key, change.replacement
        if section == "facts":
            if replacement is None:
                data[section].pop(key, None)
            else:
                data[section][key] = replacement
                _propagate_fact_correction(data, key, replacement)
        elif section in {"features", "acceptance", "users"}:
            if key in getattr(old, section):
                data[section] = [x for x in data[section] if x != key]
                if isinstance(replacement, str) and replacement not in data[section]:
                    data[section].append(replacement)
        elif section == "entity_requirements":
            entity, _, attribute = key.partition(".")
            for item in list(data[section]):
                if item["entity"] != entity:
                    continue
                if not attribute and replacement is None:
                    data[section].remove(item)
                elif attribute in {"fields", "additional_fields"}:
                    item[attribute] = replacement
        elif section == "additional_entities":
            data[section] = replacement
        elif section == "data_scope" and replacement in {"per_user", "shared"}:
            data[section] = replacement
        elif section == "field_requirements":
            # Dotted keys permit a single source-backed constraint correction
            # without requiring users to restate an entire structured object.
            for field in list(data[section]):
                prefix = (field.get("entity") or "") + "." + field["field"]
                if key == prefix and replacement is None:
                    data[section].remove(field)
                elif key.startswith(prefix + "."):
                    attribute = key[len(prefix) + 1 :]
                    if attribute in field and attribute not in {"field", "entity"}:
                        field[attribute] = replacement
        event["after"] = deepcopy(data[section])
    data["changes"] = []
    canonicalize_requirement(data, canonicalization)
    return Requirement.model_validate(data)


FACT_ATTRIBUTES = {
    "kind",
    "required",
    "min_length",
    "max_length",
    "searchable",
    "filterable",
    "date_range",
    "choices",
}


# Recorded setup/capability catalogs describe the selected environment, not
# requested field behavior. Retain them in Requirement/ledger untouched.
FACT_METADATA_KEYS = {"可用能力", "模板", "前端", "数据库", "数据范围"}
FACT_DESCRIPTOR_KEYS = {"field", "name", "entity", "label", "choice_labels"}


FIELD_FACT_CONTAINERS = {"fields", "field_requirements", "field_constraints", "字段", "字段约束"}
FIELD_CONSTRAINT_CONTAINERS = {"field_requirements", "field_constraints", "字段约束"}
BUSINESS_CONSTRAINT_CONTAINERS = {"business", "business_requirements", "business_constraints"}
PRESENTATION_FACT_CONTAINERS = {
    "labels",
    "display",
    "display_metadata",
    "presentation",
    "ui",
    "i18n",
    "localization",
    "translations",
    "界面标签",
    "显示标签",
}


def _presentation_namespace(key):
    """Normalize semantic namespace words, not individual model spellings."""
    if not isinstance(key, str):
        return False
    if key.casefold() in PRESENTATION_FACT_CONTAINERS:
        return True
    normalized = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    words = set(re.findall(r"[a-z0-9]+", normalized.casefold()))
    if words & {"labels", "display", "presentation", "ui", "i18n", "localization", "translations"}:
        return True
    return any(
        marker in key
        for marker in (
            "界面标签",
            "显示标签",
            "显示名称",
            "字段标签",
            "字段中文名",
            "界面文案",
            "本地化",
        )
    )


RESOURCE_FACT_CONTAINERS = {"resources", "entities", "资源", "实体"}
RELATION_FACT_CONTAINERS = {"relations", "关系"}
BUSINESS_FACT_CONTAINERS = {
    "metrics",
    "relations",
    "permissions",
    "notifications",
    "reminders",
    "roles",
    "resources",
    "workflows",
    "transitions",
    "registration",
    "指标",
    "关系",
    "权限",
    "提醒",
    "角色",
    "流程",
}
BUSINESS_FACT_KEYS = {
    "role_scope",
    "roles",
    "actions",
    "scope",
    "recipient",
    "event",
    "transition",
    "due_field",
    "target_entity",
    "target",
    "op",
    "group_by",
    "start_field",
    "end_field",
    "time_field",
    "from_states",
    "to_state",
    "assignee_field",
    "filters",
}
FACT_DESCRIPTION_KEYS = {"description", "说明", "描述", "requirements", "requirement", "notes"}
FIELD_KINDS = {"text", "integer", "boolean", "date", "datetime", "enum"}


def _decode_fact(value):
    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            decoded = json.loads(value)
        except ValueError:
            pass
        else:
            if isinstance(decoded, (dict, list)):
                return decoded
    return value


def _fact_subject(key, fields, entity=None, *, declared=False):
    """Resolve a field position, never a substring of an ancestor's business name."""
    if entity is not None and (
        not isinstance(entity, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", entity)
    ):
        entity = "<invalid entity>"
    if not isinstance(key, str):
        return (entity, "<invalid field>") if declared else None
    qualified = re.fullmatch(r"([a-z][a-z0-9_]*)(?:::|\.)([a-z][a-z0-9_]*)", key)
    if qualified:
        entity, key = qualified.groups()
        declared = True
    if re.fullmatch(r"[a-z][a-z0-9_]*", key) and (
        declared or any(field.name == key for _, field in fields)
    ):
        return entity, key
    for canonical, aliases in ALIASES.items():
        if key in aliases:
            names = {field.name for _, field in fields if field.name in aliases}
            return entity, next(iter(names)) if len(names) == 1 else canonical
    return None


def _field_kind(value):
    return isinstance(value, str) and value in FIELD_KINDS


def _scalar_subject(key, fields, entity=None):
    # Legacy flat spellings remain supported only when they actually name a
    # field, not because an ancestor happened to share a field identifier.
    matches = _fact_candidates(key, fields)
    names = {field.name for field in matches}
    if len(names) == 1:
        return entity or _fact_entity(key, fields), next(iter(names))
    return None


def _optional_fact(value):
    if type(value) is bool:
        return not value
    if isinstance(value, str) and value.strip().lower() in {"true", "false", "是", "否"}:
        return value.strip().lower() in {"false", "否"}
    return value


def _constraint_schema(value):
    """A structural declaration distinguishes a schema from a translated caption."""
    value = _decode_fact(value)
    if isinstance(value, list):
        return any(isinstance(_decode_fact(item), dict) for item in value)
    if not isinstance(value, dict):
        return False
    return (
        any(isinstance(_decode_fact(item), (dict, list)) for item in value.values())
        or (
            isinstance(value.get("field", value.get("name")), str)
            and bool(re.fullmatch(r"[a-z][a-z0-9_]*", value.get("field", value.get("name"))))
        )
        or any(type(value.get(attribute)) in {bool, int} for attribute in FACT_ATTRIBUTES)
    )


def _business_schema(value):
    """An explicit business wrapper needs structured domain declarations."""
    value = _decode_fact(value)
    return isinstance(value, dict) and any(
        key in BUSINESS_FACT_CONTAINERS and isinstance(_decode_fact(item), (dict, list))
        for key, item in value.items()
    )


def _fact_records(facts, fields):
    """Classify structural facts before projecting field constraints or prose.

    A name/entity pair alone is not a field declaration. Field definitions have
    an explicit field position and attributes; business schemas own their own
    names, kinds, reference fields and scalar lists. We still descend into every
    structural object so nested explicit field definitions cannot disappear.
    """
    entities = {entity for entity, _ in fields}

    def walk(
        key, value, path, entity=None, subject=None, business=False, container=None, domain=None
    ):
        value = _decode_fact(value)
        label = ".".join(path)
        # Domain provenance survives arbitrary maps, lists and JSON encodings.
        # A display schema can legitimately contain fields/name/required/choices
        # captions: those tokens cannot turn its values into field declarations.
        # An explicit constraint namespace is a separate schema, even nested in
        # presentation metadata. Keep traversing to find it and validate it in
        # full; never discard the whole display subtree.
        field_position = (
            domain != "presentation"
            and isinstance(value, dict)
            and bool(set(value) & FACT_ATTRIBUTES)
            and not (set(value) & (FIELD_FACT_CONTAINERS | RESOURCE_FACT_CONTAINERS))
            and _fact_subject(key, fields, entity) is not None
        )
        if (
            key in FIELD_CONSTRAINT_CONTAINERS
            and container != "fields"
            and (domain != "presentation" or _constraint_schema(value))
        ):
            domain = "constraints"
        elif (
            domain == "presentation"
            and key in BUSINESS_CONSTRAINT_CONTAINERS
            and _business_schema(value)
        ):
            domain = "business"
        elif _presentation_namespace(key) and container != "fields" and not field_position:
            domain = "presentation"
        if domain == "presentation":
            if isinstance(value, dict):
                children = value.items()
            elif isinstance(value, list):
                children = ((str(index), item) for index, item in enumerate(value))
            else:
                return
            for name, item in children:
                yield from walk(name, item, [*path, name], entity=entity, domain=domain)
            return
        if (
            key in FIELD_CONSTRAINT_CONTAINERS
            and container != "fields"
            and not isinstance(value, (dict, list))
        ):
            yield "constraint", label, {}, _fact_subject(None, fields, entity, declared=True)
            return
        field_container = key in FIELD_FACT_CONTAINERS and subject is None and container is None
        resource_container = (
            key in RESOURCE_FACT_CONTAINERS and subject is None and container is None
        )
        relation_container = (
            key in RELATION_FACT_CONTAINERS and subject is None and container is None
        )
        collection = (
            "fields"
            if field_container
            else "resources"
            if resource_container
            else "relations"
            if relation_container
            else None
        )
        declared = container == "fields"
        direct = _fact_subject(key, fields, entity, declared=declared and not key.isdigit())
        attributes = (
            {name: _decode_fact(item) for name, item in value.items() if name in FACT_ATTRIBUTES}
            if isinstance(value, dict)
            else {}
        )
        if collection:
            direct = None
        if not business and key in entities and direct is None:
            entity = key
        if (
            not direct
            and not business
            and entity
            and key not in entities
            and attributes
            and subject is None
        ):
            direct = _fact_subject(key, fields, entity, declared=True)
        if isinstance(value, dict):
            descriptor = value.get("field", value.get("name"))
            identifier = isinstance(descriptor, str) and re.fullmatch(
                r"[a-z][a-z0-9_]*", descriptor
            )
            # Collection membership establishes what name/key means. A resource's
            # identity scopes its children, while a relation's from scopes its
            # explicit field. Neither target entities nor business names donate
            # field identities. Leaves can override inherited scope explicitly.
            relation_record = (
                not declared
                and "field" in value
                and (
                    container == "relations" or relation_container or {"from", "to"} <= value.keys()
                )
            )
            entity_record = (container == "resources" and not collection) or (
                bool(set(value) & FIELD_FACT_CONTAINERS)
                and ("entity" in value or ("name" in value and not business))
                and "field" not in value
                and not attributes
            )
            business_record = not declared and (
                business
                or relation_record
                or container in {"resources", "relations"}
                or (
                    key in BUSINESS_FACT_CONTAINERS
                    and not (direct and attributes and not (set(value) & BUSINESS_FACT_KEYS))
                )
                or bool(set(value) & BUSINESS_FACT_KEYS)
                or (
                    isinstance(value.get("kind"), str)
                    and value.get("kind")
                    in {"count", "group_count", "time_count", "average_duration"}
                )
            )
            if entity_record:
                entity = value.get("entity", value.get("name", entity if key.isdigit() else key))
                subject = None
            elif relation_record:
                entity = value.get("entity", value.get("from", entity))
                if "entity" in value and "from" in value and value["entity"] != value["from"]:
                    entity = "<conflicting entity>"
            elif container == "relations" and not key.isdigit():
                # A keyed relation group can declare its source once for all
                # records: relations: {tickets: [{field: owner_id, ...}]}.
                entity = key
            if not entity_record and (
                declared
                and (
                    "field" in value
                    or (key.isdigit() and ("name" in value or domain == "constraints"))
                )
                and not identifier
            ):
                subject = _fact_subject(None, fields, value.get("entity", entity), declared=True)
            elif (
                not entity_record
                and identifier
                and (
                    declared
                    or (
                        attributes
                        and not business_record
                        and (
                            "field" in value
                            or bool(set(attributes) - {"kind"})
                            or _field_kind(attributes.get("kind"))
                        )
                    )
                    or ("field" in value and bool(set(attributes) - {"kind"}))
                )
            ):
                subject = _fact_subject(
                    descriptor,
                    fields,
                    entity if relation_record else value.get("entity", entity),
                    declared=True,
                )
                if business_record and not declared and not _field_kind(attributes.get("kind")):
                    attributes.pop("kind", None)
            elif (
                not entity_record
                and direct
                and not business_record
                and (declared or attributes or subject is None)
            ):
                subject = _fact_subject(
                    direct[1], fields, value.get("entity", direct[0]), declared=True
                )
            elif business_record:
                subject = None
            if subject and (attributes or declared):
                yield "constraint", label, attributes, subject
            for name, item in value.items():
                if subject and (name in FACT_ATTRIBUTES or name in FACT_DESCRIPTOR_KEYS):
                    continue
                if entity_record and name in {"name", "entity", "label"}:
                    continue
                if business_record and name in FACT_DESCRIPTOR_KEYS and not collection:
                    continue
                child_container = (
                    None
                    if (resource_container and entity_record)
                    or (relation_container and relation_record)
                    else collection
                )
                if container == "relations" and not relation_record:
                    child_container = "relations"
                yield from walk(
                    name,
                    item,
                    [*path, name],
                    entity,
                    subject,
                    business_record and not field_container,
                    child_container,
                    domain,
                )
        elif isinstance(value, list):
            if domain == "constraints" and collection == "fields":
                for index, item in enumerate(value):
                    if not isinstance(_decode_fact(item), dict):
                        yield (
                            "constraint",
                            f"{label}.{index}",
                            {},
                            _fact_subject(None, fields, entity, declared=True),
                        )
            if not any(isinstance(_decode_fact(item), (dict, list)) for item in value):
                attribute = _fact_attribute(key)
                target = subject if attribute == "choices" else None
                if not business:
                    target = (
                        target
                        or direct
                        or (
                            _scalar_subject(key, fields, entity) if attribute == "choices" else None
                        )
                    )
                if target and not collection:
                    yield "constraint", label, {"choices": value}, target
            else:
                child_container = collection or container
                if container == "relations" and not key.isdigit():
                    entity = key
                for index, item in enumerate(value):
                    if isinstance(_decode_fact(item), (dict, list)):
                        yield from walk(
                            str(index),
                            item,
                            [*path, str(index)],
                            entity,
                            subject,
                            (business or key in BUSINESS_FACT_CONTAINERS) and not field_container,
                            child_container,
                            domain,
                        )
        else:
            attribute = _scalar_fact_attribute(key, value)
            target = subject or (
                None if business else direct or _scalar_subject(key, fields, entity)
            )
            if attribute is not None and target:
                if attribute == "optional":
                    attribute, value = "required", _optional_fact(value)
                yield "constraint", label, {attribute: value}, target
            elif value is not None and not isinstance(value, bool) and attribute is None:
                if business and key not in FACT_DESCRIPTION_KEYS:
                    return
                prefix = (f"{target[0]}::" if target and target[0] else "") + (
                    target[1] + "." + key if target else label
                )
                if not target and entity:
                    prefix = f"{entity}::{prefix}"
                yield "text", label, f"{prefix}: {value}", target

    for key, value in facts.items():
        if key not in FACT_METADATA_KEYS:
            yield from walk(key, value, [key])


def _fact_constraints(facts, fields=()):
    for kind, path, value, subject in _fact_records(facts, fields):
        if kind == "constraint":
            yield path, value, subject


def _fact_attribute(label):
    attribute = next(
        (
            name
            for name in FACT_ATTRIBUTES
            if re.search(rf"(?:[._]|\s){re.escape(name)}$", label, re.I)
        ),
        None,
    )
    if attribute is None and re.search(r"(?:是否必填|必填)$", label):
        attribute = "required"
    if attribute is None and re.search(r"(?:是否可选|可选)$", label):
        attribute = "optional"
    if attribute is None:
        # Order matters: 日期范围筛选 is a date-range obligation, not
        # merely an exact-filter toggle. Explicit false stays false.
        for pattern, name in (
            (r"(?:日期|date).*(?:区间|范围|range)(?:筛选|过滤)?$", "date_range"),
            (r"(?:搜索|检索)$", "searchable"),
            (r"(?:筛选|过滤)$", "filterable"),
        ):
            if re.search(pattern, label, re.I):
                attribute = name
                break
    return attribute


def _scalar_fact_attribute(label, value):
    attribute = _fact_attribute(label)
    if attribute in {"required", "optional", "searchable", "filterable", "date_range"}:
        if isinstance(value, str) and value.strip().lower() not in {
            "true",
            "false",
            "是",
            "否",
            "必填",
            "可选",
            "非必填",
        }:
            # A legacy label such as 日期区间 can carry descriptive prose,
            # not a boolean. Keep that prose in the existing coverage checks;
            # never stringify actual booleans or relax typed object attributes.
            return None
    return attribute


def _fact_texts(facts, fields=()):
    for kind, path, value, _ in _fact_records(facts, fields):
        if kind == "text":
            yield path, value


def _field_mentions(text, names):
    """Field identifiers are whole identifiers, not arbitrary underscore fragments."""
    # Flat legacy facts use a documented field_attribute spelling. Other keys
    # such as entity_names and bootstrap_role are not fields named name/role.
    text = re.sub(
        r"_(?:" + "|".join(sorted(FACT_ATTRIBUTES)) + r"|format)(?=\s*:|$)", "", text, flags=re.I
    )
    return any(
        re.search(rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])", text, re.I)
        if name.isascii()
        else name in text
        for name in names
    )


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


````
