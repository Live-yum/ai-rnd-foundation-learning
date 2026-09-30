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
    """Keep each field's predicates and entity scope together in model prose.

    A comma inside name（必填，最长120）doesn't end the subject. Conversely,
    name必填、contact可选 must not apply both predicates to both fields.
    Shared subjects such as 标题、正文搜索 remain one obligation.
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
        # Keep comma-separated predicates with their subject, including the
        # leading 可搜索）before the next field in a parenthesized descriptor.
        previous = []
        start = 0
        seen_subject = False
        for match in re.finditer(pattern, sentence, re.I):
            if seen_subject and re.search(LEGACY_PROPERTY, sentence[start : match.start()], re.I):
                previous.append(sentence[start : match.start()])
                start = match.start()
            seen_subject = True
        previous.append(sentence[start:])
        for clause in previous:
            if clause.strip():
                local_scope = _fact_entity(clause, fields) or scope
                yield f"{local_scope}::{clause}" if local_scope else clause


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


def coverage_gaps(requirement: Requirement, plan: Plan) -> list[str]:
    gaps = []
    fields = [(entity.name, field) for entity in plan.entities for field in entity.fields]
    if plan.data_scope != requirement.data_scope:
        gaps.append("设计改变了已批准的数据归属，必须修改后重新批准")
    for obligation in requirement.field_requirements:
        matches = [
            f
            for e, f in fields
            if f.name == obligation.field and (obligation.entity is None or e == obligation.entity)
        ]
        label = f"{obligation.entity + '.' if obligation.entity else ''}{obligation.field}"
        if len(matches) != 1:
            gaps.append(f"已确认字段 {label} 缺失或映射不唯一")
            continue
        field = matches[0]
        for key, value in obligation.model_dump().items():
            if key in {"field", "entity"} or value is None:
                continue
            actual = getattr(field, key)
            if not _matches_constraint(key, value, actual):
                gaps.append(f"已确认字段 {label}.{key}={value!r}，设计为 {actual!r}")

    # Recognize legacy constraints even when a model has omitted the new typed
    # ledger. Do not inspect assumptions/limitations as if they were requirements.
    texts = [*requirement.features, *requirement.acceptance]
    structured = list(_fact_constraints(requirement.facts))
    for key, attributes in structured:
        candidates = _fact_candidates(key, fields)
        if not candidates and (
            "::" in key or any(_field_mentions(key, aliases) for aliases in ALIASES.values())
        ):
            if any(value is not None for value in attributes.values()):
                gaps.append(f"已确认条件缺少对应字段 {key}")
        for field in candidates:
            for attribute, expected in attributes.items():
                if expected is None:
                    continue
                if (attribute == "choices" and field.kind != "enum") or not _matches_constraint(
                    attribute, expected, getattr(field, attribute)
                ):
                    gaps.append(f"已确认字段 {field.name}.{attribute}={expected!r}，设计不一致")
    texts.extend(_fact_texts(requirement.facts))
    operations = {
        "searchable": r"搜索|检索|search",
        "filterable": r"筛选|过滤|filter",
        "date_range": r"日期区间|日期范围|含边界.*(?:日期|范围)|date.?range",
    }
    texts = [clause for text in texts for clause in _legacy_clauses(text, fields)]
    for text in texts:
        if re.search(
            r"(?:无需|不需要|不要求|取消|禁用|不支持).*(?:搜索|检索|筛选|过滤|日期区间|日期范围)",
            text,
        ):
            continue
        if re.search(r"(?:searchable|filterable|date_range)\s*:\s*(?:false|否)", text, re.I):
            continue
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
                    gaps.append(f"已确认条件缺少对应字段 {canonical}: {text}")
        operation_parts = [text]
        if re.search(operations["searchable"], text, re.I) and re.search(
            operations["filterable"], text, re.I
        ):
            # In a capability list, nouns in the filtering clause are not
            # search targets. Carry noun-only pieces forward so "标题、正文
            # 搜索" still binds both fields to search rather than losing one.
            operation_parts, pending = [], []
            for part in re.split(r"、|并且|并|且|和|与", text):
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
            if not targets and previous_targets:
                targets = previous_targets
            if targets:
                previous_targets = targets
            for flag, pattern in operations.items():
                if not re.search(pattern, part, re.I):
                    continue
                candidates = targets
                if flag == "date_range":
                    candidates = [f for f in targets if f.kind == "date"] or [
                        f for _, f in fields if f.kind == "date"
                    ]
                if not targets:
                    candidates = [f for _, f in fields]
                    if not any(getattr(f, flag) for f in candidates):
                        gaps.append(f"设计未覆盖已确认的 {flag}: {part}")
                elif not candidates or any(not getattr(f, flag) for f in candidates):
                    gaps.append(f"设计未覆盖已确认的 {flag}: {part}")
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
                    gaps.append(f"已确认字段 {field.name} 必填: {text}")
            if (
                re.search(
                    r"可选|非必填|不必填|是否必填.*否|optional|required\s*[:=]\s*(?:false|否)",
                    text,
                    re.I,
                )
                and not validation
            ):
                if field.required:
                    gaps.append(f"已确认字段 {field.name} 可选: {text}")
            if re.search(r"上限|最大|max_length|最多|最长", text, re.I):
                number = re.search(r"(?:上限|最大|max_length|最多|最长)[^\d]*?(\d+)", text, re.I)
                if number and field.max_length != int(number.group(1)):
                    gaps.append(f"已确认字段 {field.name} 长度上限为 {number.group(1)}: {text}")
            if re.search(r"最小|min_length|至少|最短", text, re.I):
                number = re.search(r"(?:最小|min_length|至少|最短)[^\d]*?(\d+)", text, re.I)
                if number and field.min_length != int(number.group(1)):
                    gaps.append(f"已确认字段 {field.name} 最小长度为 {number.group(1)}: {text}")
        # A date field represented as text is not executable date validation.
        if re.search(r"真实日期|YYYY-MM-DD|日期格式", text):
            if not any(f.kind == "date" for f in mentioned):
                gaps.append(f"设计未覆盖真实日期类型: {text}")
    return list(dict.fromkeys(gaps))
