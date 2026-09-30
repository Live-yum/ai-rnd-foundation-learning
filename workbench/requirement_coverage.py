"""Persist approved intent and check executable obligations without a model verdict.

Legacy free text is interpreted conservatively for known field vocabulary; new
requirements can supply exact field_requirements for arbitrary domain fields.
"""

import json
import re
from copy import deepcopy

from workbench.domain import Plan, Requirement

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


def reconcile(previous, proposed, corrections, audit=None):
    """Omission isn't deletion; only source-backed fresh edits replace old intent."""
    if not previous:
        return proposed.model_copy(update={"changes": []})
    old = Requirement.model_validate(previous)
    data = proposed.model_dump()
    for section in ("features", "acceptance", "users"):
        data[section] = list(dict.fromkeys([*getattr(old, section), *data[section]]))
    data["facts"] = {**data["facts"], **old.facts}
    fields = {(f.entity, f.field): f.model_dump() for f in proposed.field_requirements}
    fields.update({(f.entity, f.field): f.model_dump() for f in old.field_requirements})
    data["field_requirements"] = list(fields.values())
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


def _fact_constraints(facts, prefix=""):
    """Decode JSON facts structurally; their repr is never natural-language input."""
    for key, value in facts.items():
        if not prefix and key in FACT_METADATA_KEYS:
            continue
        label = f"{prefix}.{key}" if prefix else key
        if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
            try:
                decoded = json.loads(value)
            except ValueError:
                pass
            else:
                if isinstance(decoded, (dict, list)):
                    value = decoded
        if isinstance(value, dict):
            descriptor = value.get("field", value.get("name"))
            descriptor = (
                descriptor
                if isinstance(descriptor, str) and re.fullmatch(r"[a-z][a-z0-9_]*", descriptor)
                else None
            )
            if descriptor:
                entity = value.get("entity")
                label += "." + (entity + "::" if isinstance(entity, str) else "") + descriptor
            attributes = {name: item for name, item in value.items() if name in FACT_ATTRIBUTES}
            if attributes:
                yield label, attributes
            metadata = FACT_DESCRIPTOR_KEYS if descriptor or attributes else set()
            nested = {
                name: item
                for name, item in value.items()
                if name not in FACT_ATTRIBUTES and name not in metadata
            }
            yield from _fact_constraints(nested, label)
        elif isinstance(value, list):
            if not any(isinstance(item, (dict, list)) for item in value):
                yield label, {"choices": value}
            else:
                # Lists of field descriptors are structural containers, not
                # enum text. Mixed/null entries cannot turn into regex keywords.
                for index, item in enumerate(value):
                    if isinstance(item, (dict, list)):
                        yield from _fact_constraints({str(index): item}, label)
        else:
            attribute = _scalar_fact_attribute(label, value)
            if attribute == "optional":
                if type(value) is bool:
                    value = not value
                elif isinstance(value, str) and value.strip().lower() in {
                    "true",
                    "false",
                    "是",
                    "否",
                }:
                    value = value.strip().lower() in {"false", "否"}
                yield label, {"required": value}
            elif attribute is not None:
                yield label, {attribute: value}


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


def _fact_texts(facts, prefix=""):
    """Retain legacy scalar descriptions without stringifying typed containers."""
    for key, value in facts.items():
        if not prefix and key in FACT_METADATA_KEYS:
            continue
        label = f"{prefix}.{key}" if prefix else key
        if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
            try:
                decoded = json.loads(value)
            except ValueError:
                pass
            else:
                if isinstance(decoded, (dict, list)):
                    value = decoded
        if isinstance(value, dict):
            descriptor = value.get("field", value.get("name"))
            descriptor = (
                descriptor
                if isinstance(descriptor, str) and re.fullmatch(r"[a-z][a-z0-9_]*", descriptor)
                else None
            )
            if descriptor:
                entity = value.get("entity")
                label += "." + (entity + "::" if isinstance(entity, str) else "") + descriptor
            metadata = (
                FACT_DESCRIPTOR_KEYS
                if descriptor or any(name in FACT_ATTRIBUTES for name in value)
                else set()
            )
            yield from _fact_texts(
                {
                    name: item
                    for name, item in value.items()
                    if name not in FACT_ATTRIBUTES and name not in metadata
                },
                label,
            )
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, (dict, list)):
                    yield from _fact_texts({str(index): item}, label)
        elif (
            value is not None
            and not isinstance(value, bool)
            and _scalar_fact_attribute(label, value) is None
        ):
            yield f"{label}: {value}"


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


LEGACY_PROPERTY = (
    r"必填|可选|required|optional|搜索|检索|search|筛选|过滤|filter|"
    r"上限|最大|最多|最长|max_length|最小|至少|最短|min_length|日期区间|日期范围"
)


def _legacy_clauses(text, fields):
    """Bind predicates to top-level subjects, preserving bracketed target lists.

    Both name（必填，最长120）and 搜索（name、contact）are indivisible.
    A descriptive clause ending at a comma does not lend its subject to the
    next clause. Bare coordinated subjects still share their final predicate.
    """
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    pattern = "|".join(
        rf"(?<![a-z0-9_]){re.escape(name)}(?![a-z0-9_])" if name.isascii() else re.escape(name)
        for name in sorted(names, key=len, reverse=True)
    )
    entity_names = "|".join(re.escape(entity) for entity, _ in fields)
    pattern = rf"(?:(?:{entity_names})(?:::|\.))?(?:{pattern})"
    scope = _fact_entity(text, fields)
    for sentence in re.split(r"[；;。\n]|但是|但|不过", text):
        heading = re.match(r"\s*([a-z][a-z0-9_]*)\s*[：:]", sentence, re.I)
        if heading and heading.group(1) in {entity for entity, _ in fields}:
            scope = heading.group(1)
            sentence = sentence[heading.end() :]
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
                before_comma = re.sub(pattern, "", sentence[start:comma], flags=re.I)
                descriptive_boundary = bool(re.search(r"[a-z0-9\u4e00-\u9fff]", before_comma))
            if seen_subject and (re.search(LEGACY_PROPERTY, prefix, re.I) or descriptive_boundary):
                previous.append(prefix)
                start = match.start()
            seen_subject = True
        previous.append(sentence[start:])
        for clause in previous:
            if clause.strip():
                local_scope = _fact_entity(clause, fields) or scope
                yield f"{local_scope}::{clause}" if local_scope else clause


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
    for match in re.finditer(r"、|并且|并|且|和|与", text):
        if not depths[match.start()]:
            yield text[start : match.start()]
            start = match.end()
    yield text[start:]


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


def _metric_clauses(text, fields):
    """Separate aggregate predicates from field-query declarations.

    Only a recognized metric clause with named filter operands or permission
    scope is consumed. Explicit UI/query flags always remain field obligations.
    The caller checks consumed predicates against executable MetricSpec.filters.
    """
    obligations = []

    def consume(fragment, context="", inherited=False):
        combined = context + fragment
        if (
            not _METRIC_CONTEXT.search(combined)
            or not _METRIC_FILTER.search(_legacy_operation_text(fragment, fields))
            or _QUERY_SURFACE.search(fragment)
        ):
            return fragment
        matches = list(
            re.finditer(
                r"(?<![a-z0-9_])(?:(?P<entity>[a-z][a-z0-9_]*)[.:])?"
                r"(?P<field>[a-z][a-z0-9_]*)\s*(?P<op>!=|>=|<=|==|=)\s*"
                r"(?P<value>\"[^\"]*\"|'[^']*'|[a-zA-Z0-9_.:+-]+|[\u4e00-\u9fff]+?(?=\s|[，,；;、（）()]|筛选|过滤|$))",
                fragment,
                re.I,
            )
        )
        predicates = []
        for match in matches:
            name = match.group("field")
            if name in {"group_by", "start_field", "end_field", "time_field", "kind", "scope"}:
                continue
            value = match.group("value").strip("\"'")
            target = next((field for _, field in fields if field.name == name), None)
            if target is not None and target.kind in {"integer", "boolean"}:
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
        scope_only = not predicates and bool(_METRIC_SCOPE.search(fragment))
        # A metric heading may scope a following predicate, never an unrelated
        # bare field-filter declaration after a comma or conjunction.
        if inherited and not predicates and not scope_only:
            return fragment
        targets = _fact_candidates(fragment, fields)
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
            obligations.append(
                {
                    "kind": kind,
                    "entity": _fact_entity(combined, fields),
                    "predicates": predicates,
                    "targets": targets,
                }
            )
        return ""

    # Parenthesized metric definitions have their own scope, even alongside a
    # list-filter requirement in the same sentence.
    def parenthesis(match):
        prefix = text[: match.start()]
        label = re.split(r"[，,、；;。\n]", prefix)[-1]
        body = match.group(1)
        filtered = consume(body, label)
        return match.group() if filtered == body else ""

    text = re.sub(r"[（(]([^（）()]*)[）)]", parenthesis, text)
    result, context = [], ""
    for part in re.split(r"([，,；;。\n]|并且|并|且|和|与)", text):
        if re.fullmatch(r"[；;。\n]", part):
            context = ""
        if _METRIC_CONTEXT.search(part):
            context = part
            result.append(consume(part))
        else:
            result.append(consume(part, context, inherited=True))
        if _QUERY_SURFACE.search(part):
            context = ""
    return "".join(result), obligations


def _legacy_operation_text(text, fields):
    """Remove only negative operation predicates, not the rest of a mixed clause.

    'name可搜索，category不支持搜索' retains the first requirement. A
    capability explicitly not requested cannot invent a missing date field.
    Structured boolean constraints are independently checked without this step.
    """
    text = re.sub(
        r"(?:searchable|filterable|date_range)\s*[:=]\s*(?:false|否)(?![a-z])",
        "",
        text,
        flags=re.I,
    )
    negative = (
        r"(?:无需|不需要|不要求|取消|禁止|禁用|关闭|不得|不允许|不支持|不添加|不要|没有|无|不)"
    )
    operation = (
        r"(?:(?:关键词|关键字|精确)\s*)?(?:搜索|检索|筛选|过滤)"
        r"|(?:日期区间|日期范围)(?:筛选|过滤)?"
        r"|search(?:able)?|filter(?:able)?|date.?range"
    )
    names = {field.name for _, field in fields}
    names.update(name for aliases in ALIASES.values() for name in aliases)
    name = (
        "(?:" + "|".join(re.escape(value) for value in sorted(names, key=len, reverse=True)) + ")"
    )
    targets = "(?:" + name + r"(?:\s*[、和与]\s*" + name + r")*(?:的)?\s*)?"
    return re.sub(
        negative + r"\s*(?:任何|额外的?|新的?)?\s*" + targets + r"(?:" + operation + r")"
        r"(?:\s*[、或和及]\s*(?:" + negative + r")?\s*(?:" + operation + r"))*",
        "",
        text,
        flags=re.I,
    )


def _matches_constraint(attribute, expected, actual):
    if attribute in {"required", "searchable", "filterable", "date_range"}:
        if isinstance(expected, str):
            word = expected.strip().lower()
            if word in {"true", "是", "必填"}:
                expected = True
            elif word in {"false", "否", "可选", "非必填"}:
                expected = False
        return type(expected) is bool and actual is expected
    if attribute in {"min_length", "max_length"}:
        if isinstance(expected, str):
            legacy = re.fullmatch(r"\s*(\d+)\s*(?:字符|字|characters?)?\s*", expected, re.I)
            if legacy:
                expected = int(legacy.group(1))
        return type(expected) is int and actual == expected
    if attribute == "choices":
        return (
            isinstance(expected, list)
            and all(isinstance(item, str) for item in expected)
            and set(actual) == set(expected)
        )
    return type(expected) is str and actual == expected


def coverage_gaps(requirement: Requirement, plan: Plan, *, diagnostics=None) -> list[str]:
    """Return blocking messages; optionally record the exact deterministic provenance.

    Diagnostic source indices refer to the retained Requirement, never a model
    verdict. Consumers exporting diagnostics must allowlist values separately.
    """
    gaps = []
    fields = [(entity.name, field) for entity in plan.entities for field in entity.fields]
    source = {"section": "data_scope"}
    source_text = ""

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
            if not _matches_constraint(key, value, actual):
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
    structured = list(_fact_constraints(requirement.facts))
    for index, (key, attributes) in enumerate(structured):
        source = {"section": "facts", "index": index, "encoding": "structured"}
        source_text = key
        candidates = _fact_candidates(key, fields)
        if not candidates and (
            "::" in key or any(_field_mentions(key, aliases) for aliases in ALIASES.values())
        ):
            if any(value is not None for value in attributes.values()):
                gap(f"已确认条件缺少对应字段 {key}", "structured_missing_field")
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
        ({"section": "facts", "index": index, "encoding": "legacy"}, text)
        for index, text in enumerate(_fact_texts(requirement.facts))
    )
    operations = {
        "searchable": r"搜索|检索|search",
        "filterable": r"筛选|过滤|filter",
        "date_range": r"日期区间|日期范围|含边界.*(?:日期|范围)|date.?range",
    }
    query_texts = []
    for origin, text in texts:
        query_text, metric_obligations = _metric_clauses(text, fields)
        query_texts.append((origin, query_text))
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
                if (not explicit or metric.entity in explicit)
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
        for index, clause in enumerate(_legacy_clauses(text, fields)):
            source = {**origin, "clause": index}
            source_text = clause
            targets = _fact_candidates(clause, fields)
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
                    if actual is not expected:
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
        mentioned = _fact_candidates(text, fields)
        for canonical, aliases in ALIASES.items():
            if _field_mentions(text, aliases):
                matches = [f for f in mentioned if f.name in aliases]
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
                    and (explicit or re.search(LEGACY_PROPERTY, text, re.I))
                ):
                    gap(f"已确认条件缺少对应字段 {canonical}: {text}", "legacy_missing_field")
        operation_parts = [text]
        if re.search(operations["searchable"], text, re.I) and re.search(
            operations["filterable"], text, re.I
        ):
            # In a capability list, nouns in the filtering clause are not
            # search targets. Carry noun-only pieces forward so "标题、正文
            # 搜索" still binds both fields to search rather than losing one.
            operation_parts, pending = [], []
            for part in _operation_parts(text):
                pending.append(part)
                if any(re.search(pattern, part, re.I) for pattern in operations.values()):
                    operation_parts.append("".join(pending))
                    pending = []
            if pending:
                operation_parts.append("".join(pending))
        previous_targets = []
        for part in operation_parts:
            targets = _fact_candidates(part, fields) if part != text else mentioned
            # An operation-only continuation (标题搜索和精确筛选) inherits
            # the previous named subject; another field cannot satisfy it.
            if (
                not targets
                and previous_targets
                # A named generic keyword search is its own capability, not
                # a search obligation on the preceding exact-filter field.
                and not re.search(r"关键词|关键字|keyword", part, re.I)
            ):
                targets = previous_targets
            if targets:
                previous_targets = targets
            entity_scope = _fact_entity(part, fields) or _fact_entity(text, fields)
            available = [
                f for entity, f in fields if entity_scope is None or entity == entity_scope
            ]
            for flag, pattern in operations.items():
                if not re.search(pattern, part, re.I):
                    continue
                candidates = targets
                if flag == "date_range":
                    candidates = [f for f in targets if f.kind == "date"] or [
                        f for f in available if f.kind == "date"
                    ]
                if not targets:
                    candidates = available
                    if not any(getattr(f, flag) for f in candidates):
                        gap(
                            f"设计未覆盖已确认的 {flag}: {part}",
                            "uncovered_operation",
                            targets=candidates,
                            attribute=flag,
                            expected=True,
                            actual=False,
                        )
                elif not candidates or any(not getattr(f, flag) for f in candidates):
                    gap(
                        f"设计未覆盖已确认的 {flag}: {part}",
                        "uncovered_operation",
                        targets=candidates,
                        attribute=flag,
                        expected=True,
                        actual=False,
                    )
        for field in mentioned:
            # Validation summaries refer to the required/optional flags already
            # declared for each field; they don't make every listed field both.
            validation = bool(
                re.search(
                    r"必填(?:字段|项).*(?:缺失|为空)|(?:缺少|缺失)必填|必填.*可选.*校验", text
                )
            )
            if (
                re.search(r"必填|required", text, re.I)
                and not re.search(
                    r"非必填|不必填|是否必填.*否|optional|required\s*[:=]\s*(?:false|否)",
                    text,
                    re.I,
                )
                and not validation
            ):
                if not field.required:
                    gap(
                        f"已确认字段 {field.name} 必填: {text}",
                        "constraint_mismatch",
                        targets=[field],
                        attribute="required",
                        expected=True,
                        actual=field.required,
                    )
            if (
                re.search(
                    r"可选|非必填|不必填|是否必填.*否|optional|required\s*[:=]\s*(?:false|否)",
                    text,
                    re.I,
                )
                and not validation
            ):
                if field.required:
                    gap(
                        f"已确认字段 {field.name} 可选: {text}",
                        "constraint_mismatch",
                        targets=[field],
                        attribute="required",
                        expected=False,
                        actual=field.required,
                    )
            if re.search(r"上限|最大|max_length|最多|最长", text, re.I):
                number = re.search(r"(?:上限|最大|max_length|最多|最长)[^\d]*?(\d+)", text, re.I)
                if number and field.max_length != int(number.group(1)):
                    gap(
                        f"已确认字段 {field.name} 长度上限为 {number.group(1)}: {text}",
                        "constraint_mismatch",
                        targets=[field],
                        attribute="max_length",
                        expected=int(number.group(1)),
                        actual=field.max_length,
                    )
            if re.search(r"最小|min_length|至少|最短", text, re.I):
                number = re.search(r"(?:最小|min_length|至少|最短)[^\d]*?(\d+)", text, re.I)
                if number and field.min_length != int(number.group(1)):
                    gap(
                        f"已确认字段 {field.name} 最小长度为 {number.group(1)}: {text}",
                        "constraint_mismatch",
                        targets=[field],
                        attribute="min_length",
                        expected=int(number.group(1)),
                        actual=field.min_length,
                    )
        # A date field represented as text is not executable date validation.
        if re.search(r"真实日期|YYYY-MM-DD|日期格式", text):
            if not any(f.kind == "date" for f in mentioned):
                gap(
                    f"设计未覆盖真实日期类型: {text}",
                    "date_kind",
                    targets=mentioned,
                    attribute="kind",
                    expected="date",
                )
    return list(dict.fromkeys(gaps))
